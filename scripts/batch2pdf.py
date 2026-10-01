#!/usr/bin/env python3
"""Export the entries of a batch to a PDF for proofreading.

Usage: batch2pdf.py [--html] [-o OUTPUT] BATCH [BATCH ...]

BATCH is a batch id like 2601. Collects the entries with <e batch="2601">
from src/*.xml, sorts them alphabetically and writes batch-2601.pdf (or
OUTPUT when one batch is given).
Who has the batch and when it is due is taken from batches.xml.

--html writes the HTML the PDF is made from instead, which is useful for
working on the layout, or for printing from a browser.

Needs WeasyPrint for PDF output: pip install weasyprint
"""
import sys, re, datetime
from pathlib import Path
import xml.etree.ElementTree as ET
from html import escape
from sme_alphabet import sort_key

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'src'
BATCHES = ROOT / 'batches.xml'


def norm(t):
    return re.sub(r'\s+', ' ', t or '').strip()

def inline(el):
    """Text of el with its d_ref children, as HTML."""
    out = [escape(el.text or '')]
    for child in el:
        if child.tag == 'd_ref':
            target = ' '.join(filter(None, (child.get('lemma'),
                                            child.get('pos'), child.get('type'))))
            out.append(f'<span class="ref">{escape(child.text or "")}</span>'
                       f'<span class="target"> (→ {escape(target)}'
                       f' {escape(child.get("dg_id") or "")})</span>')
        else:
            out.append(escape(''.join(child.itertext())))
        out.append(escape(child.tail or ''))
    return norm(''.join(out)) if out else ''

def missing(what):
    return f'<span class="missing">[{what} missing]</span>'

def entry_html(e):
    lg = e.find('lg')
    ls = lg.findall('l')
    # pos and type are on lg; older files have them on the first l
    pos = lg.get('pos') or ls[0].get('pos') or ''
    typ = lg.get('type') or ls[0].get('type') or ''
    lemmas = ', '.join(f'<span class="lemma">{escape(norm(l.text))}</span>'
                       for l in ls)
    out = ['<div class="entry">',
           f'<p class="head">{lemmas} <span class="pos">{escape(pos)}'
           f'{" " + escape(typ) if typ else ""}</span></p>']
    dgs = e.findall('dg')
    for n, dg in enumerate(dgs, 1):
        num = f'<span class="num">{n}</span> ' if len(dgs) > 1 else ''
        ds = [inline(d) or missing('definition') for d in dg.findall('d')]
        out.append(f'<p class="sense">{num}{"; ".join(ds)}</p>')
        for tag, item, label in (('syng', 'syn', 'syn.'), ('antg', 'ant', 'ant.')):
            for g in dg.findall(tag):
                words = ', '.join(escape(norm(w.text)) or missing(label)
                                  for w in g.findall(item))
                out.append(f'<p class="rel"><span class="label">{label}</span> {words}</p>')
        for x in dg.iter('x'):
            out.append(f'<p class="ex">{escape(norm(x.text)) or missing("example")}</p>')
    for ig in e.findall('ig'):
        i = escape(norm(ig.findtext('i'))) or missing('idiom')
        out.append(f'<p class="idiom">◊ <span class="i">{i}</span></p>')
        for d in ig.findall('id'):
            out.append(f'<p class="idiom-def">{escape(norm(d.text)) or missing("definition")}</p>')
        for x in ig.findall('ix'):
            out.append(f'<p class="ex idiom-ex">{escape(norm(x.text)) or missing("example")}</p>')
    out.append('</div>')
    return '\n'.join(out)

CSS = '''
@page {
    size: A4;
    margin: 2cm 2cm 2.2cm 2cm;
    @top-left { content: string(batch); font-size: 8pt; color: #666; }
    @top-right { content: string(lemma, first) " – " string(lemma, last);
                 font-size: 8pt; color: #666; }
    @bottom-center { content: counter(page) " / " counter(pages);
                     font-size: 8pt; color: #666; }
}
body { font-family: "Noto Serif", "DejaVu Serif", serif; font-size: 10.5pt;
       line-height: 1.35; }
header { string-set: batch content(); }
h1 { font-size: 16pt; margin: 0 0 0.3em 0; }
.info { color: #444; margin: 0 0 1.5em 0; border-bottom: 1px solid #999;
        padding-bottom: 0.8em; }
.entry { margin: 0 0 1em 0; break-inside: avoid; }
.entry p { margin-top: 0; margin-bottom: 0; }
.head { margin-bottom: 0.15em; }
.lemma { font-weight: bold; font-size: 12pt; string-set: lemma content(); }
.pos { font-style: italic; color: #333; }
.sense { margin-left: 2.2em; text-indent: -1em; }
.num { font-weight: bold; }
.rel, .ex, .idiom-def { margin-left: 2.4em; }
.label { font-variant: small-caps; color: #555; }
.ex { font-style: italic; }
.idiom { margin-left: 1.2em; padding-top: 0.2em; }
.idiom .i { font-weight: bold; }
.idiom-ex { margin-left: 3.6em; }
.ref { text-decoration: underline; }
.target { font-size: 8.5pt; color: #555; }
.missing { color: #b00000; font-style: normal; font-family: sans-serif;
           font-size: 8.5pt; }
'''

def read_batches():
    if not BATCHES.exists():
        return {}
    return {b.get('id'): b for b in ET.parse(BATCHES).getroot().iter('batch')}

def collect(batch):
    entries = []
    for f in sorted(SRC.glob('*.xml')):
        for e in ET.parse(f).getroot().iter('e'):
            if e.get('batch') == batch:
                entries.append(e)
    return sorted(entries, key=lambda e: sort_key(norm(e.findtext('lg/l'))))

def page(batch, info, entries):
    title = f'dict-sme · batch {batch}'
    lines = []
    if info is not None:
        lines.append(f'Assigned to: {escape(info.get("assignee"))}')
        if info.get('due'):
            lines.append(f'Due: {escape(info.get("due"))}')
        if norm(info.text):
            lines.append(escape(norm(info.text)))
    lines.append(f'{len(entries)} {"entry" if len(entries) == 1 else "entries"}'
                 f' · printed {datetime.date.today()}')
    body = '\n'.join(entry_html(e) for e in entries)
    return f'''<!DOCTYPE html>
<html lang="se"><head><meta charset="utf-8"><title>{escape(title)}</title>
<style>{CSS}</style></head><body>
<header><h1>{escape(title)}</h1></header>
<p class="info">{"<br>".join(lines)}</p>
{body}
</body></html>
'''

def main():
    args = sys.argv[1:]
    as_html = '--html' in args
    args = [a for a in args if a != '--html']
    output = None
    if '-o' in args:
        i = args.index('-o')
        output = args[i + 1]
        del args[i:i + 2]
    if not args or (output and len(args) > 1):
        sys.exit(__doc__)
    if not as_html:
        try:
            from weasyprint import HTML
        except ImportError:
            sys.exit('WeasyPrint is missing: pip install weasyprint '
                     '(or use --html and print from a browser)')
    batches = read_batches()
    for batch in args:
        if batch not in batches:
            print(f'{batch}: not in {BATCHES.name}', file=sys.stderr)
        entries = collect(batch)
        if not entries:
            print(f'{batch}: no entries, skipped', file=sys.stderr)
            continue
        html = page(batch, batches.get(batch), entries)
        dst = output or f'batch-{batch}.{"html" if as_html else "pdf"}'
        if as_html:
            Path(dst).write_text(html, encoding='utf-8')
        else:
            HTML(string=html).write_pdf(dst)
        print(f'{batch}: {len(entries)} entries -> {dst}')

main()
