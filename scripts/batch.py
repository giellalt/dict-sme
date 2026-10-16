#!/usr/bin/env python3
"""Work with batches of entries.

Run "batch.py -h" for the commands, "batch.py COMMAND -h" for one of them.

Names of people must be in the list in schema/batches.rnc.

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

When batch.py runs in a terminal, it asks instead which of the entries
is meant, and writes the answer back into WORDLIST (with tags and
homograph number), so it is not asked again, e.g. by remove.

Only the <e> start tags in src/*.xml and the <batch> tags in batches.xml
are changed; the rest of the files stays as it is. Check the result with git diff.
"""

import argparse
import collections
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
BATCHES = ROOT / "batches.xml"
BATCHES_SCHEMA = ROOT / "schema" / "batches.rnc"
# the states of a batch, in order; as in schema/batches.rnc
STATES = [
    "edit",
    "proofread-1",
    "correcting-1",
    "proofread-2",
    "correcting-2",
    "publish",
]
ENTRY = re.compile(r"<e[ >].*?</e>", re.S)
BATCH_ID = re.compile(r"[0-9]{4}$")


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
                if (
                    norm(l.text) == word
                    and (typ is None or (l.get("type") or "") == typ)
                    and (hid is None or l.get("hid") == hid)
                ):
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


def people():
    """the names in the person list in schema/batches.rnc"""
    m = re.search(
        r"^person\s*=(.*?)(?=^\S|\Z)",
        BATCHES_SCHEMA.read_text(encoding="utf-8"),
        re.M | re.S,
    )
    return re.findall(r'"([^"]*)"', m.group(1)) if m else []


def need_batch(batch, batches):
    if batch not in batches:
        sys.exit(
            f"batch {batch} is not in batches.xml; add it with: batch.py new {batch} EDITOR"
        )


def set_batch_attribute(batch, name, value):
    """set an attribute of the batch in batches.xml, changing only its tag"""
    s = BATCHES.read_text(encoding="utf-8")
    m = re.search(rf'<batch\b[^>]*\bid="{batch}"[^>]*>', s)
    tag = re.sub(rf'\s{name}="[^"]*"', "", m.group())
    tag = tag[:-1].rstrip() + f' {name}="{value}">'
    BATCHES.write_text(s[: m.start()] + tag + s[m.end() :], encoding="utf-8")


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


def first_definition(e):
    for d in e.iter("d"):
        t = norm("".join(d.itertext()))
        if t:
            return t
    return ""


def exact_line(e, word):
    """the wordlist line that finds e: word with the pos and type of the
    lemma it matched, and its homograph number"""
    lg = e.find("lg")
    l = next((l for l in lg.findall("l") if norm(l.text) == word), lg.find("l"))
    line = f"{norm(l.text)}+{lg.get('pos')}" + (
        f"+{l.get('type')}" if l.get("type") else ""
    )
    return line + (f"\t{l.get('hid')}" if l.get("hid") else "")


def choose(d, n, label, found):
    """ask which of the entries found is meant; returns the chosen ones"""
    print(f"\nline {n}: {label} matches more than one entry:")
    for i, k in enumerate(found, 1):
        f, _, _, e = d.entries[k]
        x = norm(e.findtext(".//x"))
        about = first_definition(e) or (
            f"(no definition; example: {x})" if x else "(no definition)"
        )
        extra = f" [in batch {e.get('batch')}]" if e.get("batch") else ""
        print(f"  {i}) {describe(e)} ({f.name}){extra}: {about}")
    while True:
        try:
            answer = input(
                f"which one? 1-{len(found)}, several as 1,2, a = all, Enter = leave out: "
            )
        except EOFError:
            print()
            return []
        answer = answer.strip().lower()
        if not answer:
            return []
        if answer == "a":
            return found
        numbers = answer.replace(",", " ").split()
        if all(x.isdigit() and 1 <= int(x) <= len(found) for x in numbers):
            return list(dict.fromkeys(found[int(x) - 1] for x in numbers))
        print("  answer with the numbers in the list")


def match_words(d, path):
    """entry indexes for the words in the list; problems are reported.
    In a terminal, the user is asked about words with more than one entry,
    and the answers are written back into the list."""
    ask = sys.stdin.isatty()
    ks, problems, answers = [], [], {}
    for n, word, pos, typ, hid in read_wordlist(path):
        found = d.find(word, pos, typ, hid)
        label = "+".join(x for x in (word, pos, typ) if x) + (f" {hid}" if hid else "")
        if len(found) > 1 and ask:
            found = choose(d, n, label, found)
            if not found:
                problems.append(f"line {n}: {label}: more than one entry, none chosen")
                continue
            answers[n] = [exact_line(d.entries[k][3], word) for k in found]
            ks += found
        elif not found:
            problems.append(f"line {n}: {label}: not found")
        elif len(found) > 1:
            which = "; ".join(describe(d.entries[k][3]) for k in found)
            problems.append(
                f"line {n}: {label}: more than one entry ({which}), add tags and/or homograph number"
            )
        else:
            ks.append(found[0])
    if answers:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
        for n, new in answers.items():
            lines[n - 1] = "\n".join(new)
        Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"{len(answers)} answers written to {path}")
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
            count[b]["entries"] += 1
            count[b]["definition"] += has_definition(e)
    print(
        f"{'batch':6} {'state':13} {'editor':14} {'proofreader':14} {'entries':>7} {'with def':>8}"
    )
    for b in sorted(set(batches) | set(count)):
        info = batches.get(b)
        if info is None:
            state, editor, proofreader = "?", "(not in batches.xml)", ""
        else:
            state, editor, proofreader = (
                info.get("state"),
                info.get("editor"),
                info.get("proofreader") or "-",
            )
        c = count[b]
        print(
            f"{b:6} {state:13} {editor:14} {proofreader:14} {c['entries']:7} {c['definition']:8}"
        )


def cmd_new(batch, editor, note=""):
    if not BATCH_ID.match(batch):
        sys.exit(
            f"{batch}: a batch id is the year (two digits) and a number, e.g. 2604"
        )
    if batch in read_batches():
        sys.exit(f"batch {batch} is already in batches.xml")
    s = BATCHES.read_text(encoding="utf-8")
    esc = lambda t: t.replace("&", "&amp;").replace("<", "&lt;")
    line = (
        f'    <batch id="{batch}" editor="{editor}" state="edit">{esc(note)}</batch>\n'
    )
    i = s.rindex("</batches>")
    BATCHES.write_text(s[:i] + line + s[i:], encoding="utf-8")
    print(f"batch {batch} ({editor}) added to batches.xml")


def cmd_set(batch, role, name):
    need_batch(batch, read_batches())
    set_batch_attribute(batch, role, name)
    print(f"batch {batch}: {role} is now {name}")


def cmd_add(batch, path, move=False, force=False):
    batches = read_batches()
    need_batch(batch, batches)
    if batches[batch].get("state") == "publish" and not force:
        sys.exit(
            f"batch {batch} is published: what is added goes on the website unchecked; use --force to add anyway"
        )
    d = Dictionary()
    ks, problems = match_words(d, path)
    added = 0
    for k in ks:
        e = d.entries[k][3]
        other = e.get("batch")
        if other == batch:
            continue
        if other and not move:
            problems.append(
                f"{describe(e)}: already in batch {other} (use --move to move it)"
            )
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


def cmd_state(batch, state, force=False):
    batches = read_batches()
    need_batch(batch, batches)
    if STATES.index(state) >= STATES.index("proofread-1") and not batches[batch].get(
        "proofreader"
    ):
        sys.exit(
            f"batch {batch} has no proofreader; set one with: batch.py set {batch} proofreader NAME"
        )
    if state == "publish":
        d = Dictionary()
        missing = [
            describe(e)
            for _, _, _, e in d.entries
            if e.get("batch") == batch and not has_definition(e)
        ]
        if missing and not force:
            print(f"{len(missing)} entries in batch {batch} have no definition:")
            for m in missing:
                print("  " + m)
            sys.exit("nothing changed; write the definitions, or use --force")
    set_batch_attribute(batch, "state", state)
    print(f"batch {batch} is now in state {state}")


def cmd_check():
    problems = []
    root = ET.parse(BATCHES).getroot()
    ids = collections.Counter(b.get("id") for b in root.iter("batch"))
    names = people()
    for b, n in ids.items():
        if n > 1:
            problems.append(f"batch {b} is {n} times in batches.xml")
    for info in root.iter("batch"):
        b, state = info.get("id"), info.get("state")
        if not BATCH_ID.match(b or ""):
            problems.append(
                f"batch {b}: the id is not the year and a number, e.g. 2604"
            )
        if state not in STATES:
            problems.append(f"batch {b}: unknown state {state!r}")
        elif STATES.index(state) >= STATES.index("proofread-1") and not info.get(
            "proofreader"
        ):
            problems.append(f"batch {b}: in state {state}, but has no proofreader")
        for role in ("editor", "proofreader"):
            if info.get(role) and info.get(role) not in names:
                problems.append(
                    f"batch {b}: {role} {info.get(role)} is not in the list of people in schema/batches.rnc"
                )
    d = Dictionary()
    count = collections.Counter()
    unknown = collections.defaultdict(list)
    for f, _, _, e in d.entries:
        b = e.get("batch")
        if b:
            count[b] += 1
            if b not in ids:
                unknown[b].append(f"{describe(e)} (src/{f.name})")
    for b, es in sorted(unknown.items()):
        problems.append(
            f"batch {b} is not in batches.xml, but {len(es)} entries are in it: "
            + "; ".join(es[:5])
            + (" ..." if len(es) > 5 else "")
        )
    for b in sorted(ids):
        if not count[b]:
            problems.append(f"batch {b} has no entries")
    for p in problems:
        print(p)
    print(f"{len(problems)} problems" if problems else "no problems")
    if problems:
        sys.exit(1)


def main():
    doc = __doc__.split("\n\n", 2)
    parser = argparse.ArgumentParser(
        description=doc[0],
        epilog=doc[2],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="cmd", required=True, metavar="COMMAND")

    def command(name, help, func):
        p = sub.add_parser(name, help=help, description=help)
        p.set_defaults(func=func)
        return p

    command(
        "list",
        "show each batch with its state, editor, proofreader, how many "
        "entries it has and how many of them have a definition",
        lambda a: cmd_list(),
    )

    p = command(
        "new",
        'add a batch to batches.xml in state edit, e.g. "batch.py new 2624 Helena"',
        lambda a: cmd_new(a.batch, a.editor, a.note),
    )
    p.add_argument("batch", metavar="BATCH")
    p.add_argument("editor", choices=people())
    p.add_argument("note", metavar="NOTE", nargs="?", default="")

    p = command(
        "add",
        "put the words in WORDLIST into the batch",
        lambda a: cmd_add(a.batch, a.wordlist, move=a.move, force=a.force),
    )
    p.add_argument("batch", metavar="BATCH")
    p.add_argument("wordlist", metavar="WORDLIST")
    p.add_argument(
        "--move",
        action="store_true",
        help="move words that are already in another batch; "
        "without it they are left there and reported",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="add to a batch in state publish, which puts the "
        "words on the website unchecked",
    )

    p = command(
        "remove",
        "take the words in WORDLIST out of the batch",
        lambda a: cmd_remove(a.batch, a.wordlist),
    )
    p.add_argument("batch", metavar="BATCH")
    p.add_argument("wordlist", metavar="WORDLIST")

    p = command(
        "state",
        "set the state of the batch; from proofread-1 on, "
        "the batch needs a proofreader",
        lambda a: cmd_state(a.batch, a.state, force=a.force),
    )
    p.add_argument("batch", metavar="BATCH")
    p.add_argument("state", choices=STATES)
    p.add_argument(
        "--force",
        action="store_true",
        help="set publish even when entries in the batch have no "
        "definition (they are listed otherwise, and nothing is changed)",
    )

    p = command(
        "set",
        "set the editor or proofreader of the batch",
        lambda a: cmd_set(a.batch, a.role, a.name),
    )
    p.add_argument("batch", metavar="BATCH")
    p.add_argument("role", choices=["editor", "proofreader"])
    p.add_argument("name", choices=people())

    command(
        "check",
        "report problems that the schemas cannot find: entries in "
        "a batch that is not in batches.xml, batches without entries, "
        "batches that need a proofreader, and so on",
        lambda a: cmd_check(),
    )

    args = parser.parse_args()
    try:
        args.func(args)
    except FileNotFoundError as err:
        sys.exit(str(err))


main()
