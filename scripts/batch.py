#!/usr/bin/env python3
"""Work with batches of entries.

Usage:
  batch.py list
  batch.py new BATCH ASSIGNEE [NOTE]
  batch.py add BATCH WORDLIST [--move]
  batch.py remove BATCH WORDLIST
  batch.py status BATCH edit|publish [--force]
  batch.py close BATCH
  batch.py open BATCH

list     shows each batch with its person, state and how many of its entries
         are edit/publish and have a definition.
new      adds a batch to batches.xml, e.g. "batch.py new 2604 Helena".
add      puts the words in WORDLIST into the batch. Words that are already in
         another batch are left there and reported, unless --move is given.
remove   takes the words in WORDLIST out of the batch.
status   sets the status of all entries in the batch. Setting publish is
         refused while entries in the batch have no definition, and these
         are listed; --force sets it anyway.
close    marks the batch as finished, so XXE no longer offers it.
open     opens a closed batch again.

WORDLIST is a text file with one word per line, written as in the
analysers: the lemma, then the pos and type as tags. A homograph number,
when needed, comes after a tab:
    vuovdi+N            vuovdi without a type
    vuovdi+N+NomAg      vuovdi with type NomAg
    giella+N<TAB>2      homograph 2 of giella
    rievtti mielde+Adv
    uhcán               no tags: any pos and type
When the pos is given, the type must match exactly, so vuovdi+N does not
match vuovdi+N+NomAg. A word matches an entry when it is one of the
entry's lemmas, so any variant spelling can be used. When a word matches
more than one entry, it is reported and left out; add the tags and/or the
homograph number. Empty lines and lines starting with # are skipped.

Only the <e> start tags in src/*.xml and batches.xml are changed; the rest
of the files stays as it is. Check the result with git diff.
"""
import re
import sys
import collections
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
BATCHES = ROOT / "batches.xml"
ENTRY = re.compile(r"<e[ >].*?</e>", re.S)
BATCH_ID = re.compile(r"[0-9]{2}[0-9]{2,}$")


def norm(t):
    return re.sub(r"\s+", " ", t or "").strip()


def has_definition(e):
    return any("".join(d.itertext()).strip() for d in e.iter("d"))


def describe(e):
    lg = e.find("lg")
    return ", ".join(
        f"{norm(l.text)}+{lg.get('pos')}"
        + (f"+{l.get('type')}" if l.get("type") else "")
        + (f" {l.get('hid')}" if l.get("hid") else "")
        for l in lg.findall("l")
    )


class Dictionary:
    """All entries in src/, with a way to change the attributes of their
    start tags and write back only what changed."""

    def __init__(self):
        self.files = sorted(SRC.glob("*.xml"))
        self.text = {f: f.read_text(encoding="utf-8") for f in self.files}
        self.entries = []  # (file, start, end, element)
        for f in self.files:
            for m in ENTRY.finditer(self.text[f]):
                self.entries.append((f, m.start(), m.end(), ET.fromstring(m.group())))
        self.changes = {}  # entry index -> {attribute: value or None}

    def set(self, k, name, value):
        self.changes.setdefault(k, {})[name] = value
        e = self.entries[k][3]
        if value is None:
            e.attrib.pop(name, None)
        else:
            e.set(name, value)

    def find(self, word, pos=None, typ=None, hid=None):
        """typ None: any type; "": no type"""
        found = []
        for k, (_, _, _, e) in enumerate(self.entries):
            lg = e.find("lg")
            if pos and lg.get("pos") != pos:
                continue
            for l in lg.findall("l"):
                if (norm(l.text) == word
                        and (typ is None or (l.get("type") or "") == typ)
                        and (hid is None or l.get("hid") == hid)):
                    found.append(k)
                    break
        return found

    def save(self):
        changed = collections.Counter()
        for f in self.files:
            s = self.text[f]
            ks = sorted(k for k in self.changes if self.entries[k][0] == f)
            for k in reversed(ks):
                _, a, b, _ = self.entries[k]
                tag_end = s.index(">", a) + 1
                tag = s[a:tag_end]
                for name, value in self.changes[k].items():
                    tag = re.sub(rf'\s{name}="[^"]*"', "", tag)
                    if value is not None:
                        tag = tag[:-1].rstrip("/").rstrip() + f' {name}="{value}">'
                s = s[:a] + tag + s[tag_end:]
                changed[f.name] += 1
            if ks:
                f.write_text(s, encoding="utf-8")
        for name, n in sorted(changed.items()):
            print(f"{n:6d} entries changed in src/{name}")


def read_batches():
    if not BATCHES.exists():
        return {}
    return {b.get("id"): b for b in ET.parse(BATCHES).getroot().iter("batch")}


def need_batch(batch, batches):
    if batch not in batches:
        sys.exit(f"batch {batch} is not in batches.xml; add it with: batch.py new {batch} NAME")


def read_wordlist(path):
    words = []
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        cols = [norm(c) for c in line.split("\t")]
        tags = cols[0].split("+")
        word = tags[0]
        pos = tags[1] if len(tags) > 1 else None
        # with a pos, a missing type means "no type"
        typ = (tags[2] if len(tags) > 2 else "") if pos else None
        hid = cols[1] if len(cols) > 1 and cols[1] else None
        words.append((n, word, pos, typ, hid))
    return words


def match_words(d, path):
    """entry indexes for the words in the list; problems are reported"""
    ks, problems = [], []
    for n, word, pos, typ, hid in read_wordlist(path):
        found = d.find(word, pos, typ, hid)
        label = "+".join(x for x in (word, pos, typ) if x) + (f" {hid}" if hid else "")
        if not found:
            problems.append(f"line {n}: {label}: not found")
        elif len(found) > 1:
            which = "; ".join(describe(d.entries[k][3]) for k in found)
            problems.append(f"line {n}: {label}: more than one entry ({which}), add tags and/or homograph number")
        else:
            ks.append(found[0])
    return list(dict.fromkeys(ks)), problems


def report(problems):
    if problems:
        print(f"{len(problems)} words left out:")
        for p in problems:
            print("  " + p)


def cmd_list():
    batches = read_batches()
    d = Dictionary()
    count = collections.defaultdict(collections.Counter)
    for _, _, _, e in d.entries:
        b = e.get("batch")
        if b:
            c = count[b]
            c["entries"] += 1
            c[e.get("status")] += 1
            c["definition"] += has_definition(e)
            c["own assignee"] += bool(e.get("assignee"))
    print(f"{'batch':6} {'state':6} {'assignee':16} {'entries':>7} {'edit':>6} {'publish':>7} {'with def':>8}")
    for b in sorted(set(batches) | set(count)):
        info = batches.get(b)
        state = info.get("state", "open") if info is not None else "?"
        who = info.get("assignee") if info is not None else "(not in batches.xml)"
        c = count[b]
        extra = f"  ({c['own assignee']} with their own assignee)" if c["own assignee"] else ""
        print(f"{b:6} {state:6} {who:16} {c['entries']:7} {c['edit']:6} {c['publish']:7} {c['definition']:8}{extra}")


def cmd_new(batch, assignee, note=""):
    if not BATCH_ID.match(batch):
        sys.exit(f"{batch}: a batch id is the year (two digits) and a number, e.g. 2604")
    if batch in read_batches():
        sys.exit(f"batch {batch} is already in batches.xml")
    s = BATCHES.read_text(encoding="utf-8")
    esc = lambda t: t.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")
    line = f'    <batch id="{batch}" assignee="{esc(assignee)}">{esc(note)}</batch>\n'
    i = s.rindex("</batches>")
    s = s[:i] + line + s[i:]
    BATCHES.write_text(s, encoding="utf-8")
    print(f"batch {batch} ({assignee}) added to batches.xml")


def set_state(batch, state):
    need_batch(batch, read_batches())
    s = BATCHES.read_text(encoding="utf-8")
    m = re.search(rf'<batch\b[^>]*\bid="{batch}"[^>]*>', s)
    tag = re.sub(r'\sstate="[^"]*"', "", m.group())
    if state == "closed":
        tag = tag[:-1].rstrip() + ' state="closed">'
    s = s[: m.start()] + tag + s[m.end():]
    BATCHES.write_text(s, encoding="utf-8")
    print(f"batch {batch} is now {state}")


def cmd_add(batch, path, move=False):
    need_batch(batch, read_batches())
    d = Dictionary()
    ks, problems = match_words(d, path)
    added = 0
    for k in ks:
        e = d.entries[k][3]
        other = e.get("batch")
        if other == batch:
            continue
        if other and not move:
            problems.append(f"{describe(e)}: already in batch {other} (use --move to move it)")
            continue
        d.set(k, "batch", batch)
        added += 1
    d.save()
    print(f"{added} entries put in batch {batch}")
    report(problems)


def cmd_remove(batch, path):
    d = Dictionary()
    ks, problems = match_words(d, path)
    removed = 0
    for k in ks:
        e = d.entries[k][3]
        if e.get("batch") != batch:
            problems.append(f"{describe(e)}: not in batch {batch}")
            continue
        d.set(k, "batch", None)
        removed += 1
    d.save()
    print(f"{removed} entries taken out of batch {batch}")
    report(problems)


def cmd_status(batch, status, force=False):
    if status not in ("edit", "publish"):
        sys.exit("status is edit or publish")
    d = Dictionary()
    ks = [k for k, (_, _, _, e) in enumerate(d.entries) if e.get("batch") == batch]
    if not ks:
        sys.exit(f"no entries in batch {batch}")
    if status == "publish":
        missing = [describe(d.entries[k][3]) for k in ks if not has_definition(d.entries[k][3])]
        if missing and not force:
            print(f"{len(missing)} entries in batch {batch} have no definition:")
            for m in missing:
                print("  " + m)
            sys.exit("nothing changed; write the definitions, or use --force")
    n = 0
    for k in ks:
        if d.entries[k][3].get("status") != status:
            d.set(k, "status", status)
            n += 1
    d.save()
    print(f"{n} entries in batch {batch} set to {status}")


def main():
    args = sys.argv[1:]
    flags = {a for a in args if a.startswith("--")}
    args = [a for a in args if not a.startswith("--")]
    if not args or args[0] in ("-h", "help"):
        sys.exit(__doc__)
    cmd, rest = args[0], args[1:]
    try:
        if cmd == "list" and not rest:
            cmd_list()
        elif cmd == "new" and len(rest) in (2, 3):
            cmd_new(*rest)
        elif cmd == "add" and len(rest) == 2:
            cmd_add(*rest, move="--move" in flags)
        elif cmd == "remove" and len(rest) == 2:
            cmd_remove(*rest)
        elif cmd == "status" and len(rest) == 2:
            cmd_status(*rest, force="--force" in flags)
        elif cmd == "close" and len(rest) == 1:
            set_state(rest[0], "closed")
        elif cmd == "open" and len(rest) == 1:
            set_state(rest[0], "open")
        else:
            sys.exit(__doc__)
    except FileNotFoundError as err:
        sys.exit(str(err))


main()
