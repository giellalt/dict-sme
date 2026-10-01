#!/usr/bin/env python3
"""Import the dict-sme-nob dictionary into src/ of this repository.

Usage: smenob2sme.py [SMENOB_SRC_DIR]

SMENOB_SRC_DIR defaults to ../dict-sme-nob/src next to this repository.
Every NAME_smenob.xml there becomes src/NAME_sme.xml here, overwriting
what is in src/. Proper nouns (type="Prop") are left out, and so are the
N_Prop* files, which only contain proper nouns.

What is kept:
  - lemma, pos and type; lsub becomes an extra l (a variant)
  - each meaning (mg) that has a definition, examples, synonyms or
    antonyms becomes a dg; a meaning without a definition gets an empty
    <d/>, to be written later
  - definitions (dg/d, with dg/re put in front in parentheses), examples
    (x), synonyms (sg/s), antonyms (antg/ant), idioms (i and id)
  - l_ref and the c attribute of mg, as comments
Entries without any of this are imported with only the lemma.

Everything Norwegian (t, xt, dt, it, re in tg and mg) and metadata (freq,
src, context, dial, sem_type, paradigms, ...) is dropped.

Entries with the same lemma+pos+type are merged into the first of them,
and get a comment saying so.

In each file, entries with a definition come first, then the rest; both
parts are sorted in North Sámi alphabetical order.
The dgs of an entry get the ids a, b, c, ... in the order they come in.
"""
import sys, re, collections
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
from sme_alphabet import sort_key

ROOT = Path(__file__).resolve().parent.parent
DST = ROOT / 'src'
DEFAULT_SRC = ROOT.parent / 'dict-sme-nob' / 'src'

HEADER = '''<?xml version="1.0" encoding="UTF-8"?>
<?xml-model href="../schema/dict-sme.rnc" type="application/relax-ng-compact-syntax"?>
<?xml-stylesheet type="text/css" href="../schema/dict-sme_XXE.css"?>
<r id="dict-sme" xml:lang="sme">
    <lics xml:lang="en" xml:space="preserve">
        <lic>
            This code is made available under a Creative Commons Attribution license
            <a>https://creativecommons.org/licenses/by/4.0/</a>.

            You are free to copy, distribute and adapt the work, as long as you always give
            proper attribution using the attribution text below.

            For the full license text, see the link above.
        </lic>
        <ref>
            Work by The Centre for Sámi Lexicography, Giellatekno and Divvun at UiT,
            and members of the language communities. Source code
            available at <a>https://github.com/giellalt/dict-sme</a>.

            Based on dict-sme-nob, work by Nils Jernsletten, Giellatekno and
            Divvun at UiT, and members of the language communities, licensed
            under CC BY 3.0 NO <a>http://creativecommons.org/licenses/by/3.0/no/deed.en</a>.
            Source code available at <a>https://github.com/giellalt/dict-sme-nob</a>.
        </ref>
        <sourcenote>
            THIS TEXT IS THE ORIGINAL SOURCE CODE. This is NOT a fully styled and
            published dictionary. As such it can and
            will contain unfinished entries, unpublished entries, entries with
            objectionable translations, etc. If you find any errors or want to add more
            words, download the file, edit it, and send it back to
            <a>mailto:feedback@divvun.no</a> and <a>mailto:giellatekno@uit.no</a>.
            Please also note that the entries are not necessarily sorted,
            or could be wrongly sorted.
        </sourcenote>
    </lics>
'''

I = '    '
stats = collections.Counter()

def norm(t):
    return re.sub(r'\s+', ' ', t or '').strip()

def unique(items):
    return list(dict.fromkeys(i for i in items if i))

class Entry:
    def __init__(self, pos, typ):
        self.pos, self.typ = pos, typ
        self.lemmas = []    # strings
        self.dgs = []       # (ds, syns, ants, xs)
        self.igs = []       # (i, ids)
        self.comments = []
        self.merged = 1

def read_entry(e):
    lg = e.find('lg')
    l = lg.find('l')
    entry = Entry(l.get('pos'), l.get('type'))
    entry.lemmas = unique([norm(l.text)] + [norm(s.text) for s in lg.findall('lsub')])
    stats['lsub -> extra l'] += len(entry.lemmas) - 1
    for mg in e.findall('mg'):
        ds = []
        for dg in mg.findall('dg'):
            re_ = norm(dg.findtext('re'))
            for d in dg.findall('d'):
                txt = norm(d.text)
                if txt:
                    ds.append(f'({re_}) {txt}' if re_ else txt)
        syns = unique(norm(s.text) for s in mg.findall('sg/s'))
        ants = unique(norm(a.text) for a in mg.findall('antg/ant'))
        xs = unique(norm(x.text) for x in mg.iter('x'))
        if ds or syns or ants or xs:
            if not ds:
                stats['dg with empty d'] += 1
            entry.dgs.append((ds, syns, ants, xs))
        for lr in mg.findall('l_ref'):
            entry.comments.append(f'l_ref: {norm(lr.text)}')
        if mg.get('c'):
            entry.comments.append(norm(mg.get('c')))
    for ig in e.findall('ig'):
        i = norm(ig.findtext('i'))
        if i:
            entry.igs.append((i, unique(norm(d.text) for d in ig.findall('id'))))
    return entry

def dg_id(n):
    """a, b, ..., z, aa, ab, ... for n = 1, 2, ..."""
    s = ''
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(ord('a') + r) + s
    return s

def merge(a, b):
    a.lemmas = unique(a.lemmas + b.lemmas)
    a.dgs += b.dgs
    a.igs += b.igs
    a.comments += b.comments
    a.merged += 1

def write_entry(entry, out):
    out.append(f'{I}<e status="edit">')
    attrs = f' pos="{entry.pos}"' + (f' type="{entry.typ}"' if entry.typ else '')
    out.append(f'{I*2}<lg{attrs}>')
    out += [f'{I*3}<l>{escape(l)}</l>' for l in entry.lemmas]
    out.append(f'{I*2}</lg>')
    for n, (ds, syns, ants, xs) in enumerate(entry.dgs, 1):
        out.append(f'{I*2}<dg id="{dg_id(n)}">')
        out += [f'{I*3}<d>{escape(d)}</d>' for d in ds] or [f'{I*3}<d/>']
        for tag, item, vals in (('syng', 'syn', syns), ('antg', 'ant', ants), ('xg', 'x', xs)):
            if vals:
                out.append(f'{I*3}<{tag}>')
                out += [f'{I*4}<{item}>{escape(v)}</{item}>' for v in vals]
                out.append(f'{I*3}</{tag}>')
        out.append(f'{I*2}</dg>')
    for i, ids in entry.igs:
        out.append(f'{I*2}<ig>')
        out.append(f'{I*3}<i>{escape(i)}</i>')
        out += [f'{I*3}<id>{escape(d)}</id>' for d in ids]
        out.append(f'{I*2}</ig>')
    comments = list(entry.comments)
    if entry.merged > 1:
        comments.insert(0, f'merged from {entry.merged} entries with the same '
                           'lemma+pos+type in dict-sme-nob')
    if comments:
        out.append(f'{I*2}<cg>')
        out += [f'{I*3}<c>{escape(c)}</c>' for c in comments]
        out.append(f'{I*2}</cg>')
    out.append(f'{I}</e>')

def has_definition(entry):
    return any(ds for ds, *_ in entry.dgs)

def entry_order(entry):
    return (not has_definition(entry), sort_key(entry.lemmas[0]))

def write_file(name, file_entries):
    out = []
    for entry in file_entries:
        write_entry(entry, out)
    (DST / f'{name}_sme.xml').write_text(HEADER + '\n'.join(out) + '\n</r>\n',
                                       encoding='utf-8')
    print(f'{len(file_entries):6d} entries -> src/{name}_sme.xml')

def main():
    if len(sys.argv) > 2 or sys.argv[1:2] in (['-h'], ['--help']):
        sys.exit(__doc__)
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SRC
    files = sorted(f for f in src.glob('*_smenob.xml')
                   if not f.name.startswith('N_Prop'))
    if not files:
        sys.exit(f'no *_smenob.xml files in {src}')
    # key -> Entry; entries are written to the file where the key is first seen
    entries = {}
    per_file = {f: [] for f in files}
    for f in files:
        for e in ET.parse(f).getroot().iter('e'):
            entry = read_entry(e)
            if entry.typ == 'Prop':
                stats['proper nouns left out'] += 1
                continue
            key = (entry.lemmas[0], entry.pos, entry.typ)
            if key in entries:
                merge(entries[key], entry)
                stats['merged into an earlier entry'] += 1
            else:
                entries[key] = entry
                per_file[f].append(entry)
    for f, file_entries in per_file.items():
        file_entries.sort(key=entry_order)
        write_file(f.name.replace('_smenob.xml', ''), file_entries)
    with_d = sum(1 for e in entries.values() if has_definition(e))
    print(f'{len(entries):6d} entries in all, {with_d} with a definition')
    for k, v in sorted(stats.items()):
        print(f'{v:6d}  {k}')

main()
