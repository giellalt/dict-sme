#!/usr/bin/env python3
"""Work with batches of entries.

Run "batch.py -h" for the commands, "batch.py COMMAND -h" for one of them.

Names of people must be in the list of people at the top of batches.xml.

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
import datetime
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
BATCHES = ROOT / "batches" / "batches.xml"
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
    """the names in the list of people in batches.xml"""
    if not BATCHES.exists():
        return []
    root = ET.parse(BATCHES).getroot()
    return [norm(p.text) for p in root.iter("person") if norm(p.text)]


def need_batch(batch, batches):
    if batch not in batches:
        sys.exit(
            f"batch {batch} is not in batches.xml; add it with: batch.py new {batch} EDITOR"
        )


def retag(tag, name, value):
    """a start tag with the attribute NAME set to VALUE (None: removed).
    The attributes are written in alphabetical order, as XXE saves them,
    so that saving in XXE does not change the line again."""
    m = re.match(r"<(\w+)(.*?)\s*(/?)>$", tag, re.S)
    attrs = dict(re.findall(r'(\w+)="([^"]*)"', m.group(2)))
    if value is None:
        attrs.pop(name, None)
    else:
        attrs[name] = esc(value)
    text = "".join(f' {k}="{v}"' for k, v in sorted(attrs.items()))
    return f"<{m.group(1)}{text}{m.group(3)}>"


def set_batch_attribute(batch, name, value):
    """set an attribute of the batch in batches.xml, changing only its tag"""
    s = BATCHES.read_text(encoding="utf-8")
    m = re.search(rf'<batch\b[^>]*\bid="{batch}"[^>]*>', s)
    tag = retag(m.group(), name, value)
    BATCHES.write_text(s[: m.start()] + tag + s[m.end() :], encoding="utf-8")


def steps(info):
    return info.findall("step")


def state_of(info):
    """the state the batch is in now: that of its last step"""
    s = steps(info)
    return s[-1].get("state") if s else None


def who_has(info):
    """who does the step the batch is in now ("" when nobody has it yet)"""
    s = steps(info)
    return (s[-1].get("by") or "") if s else ""


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")


def batch_block(s, batch):
    """start and end of <batch id="BATCH">...</batch> in the text of batches.xml"""
    m = re.search(rf'<batch\b[^>]*\bid="{batch}"[^>]*>.*?</batch>', s, re.S)
    return m.start(), m.end()


def add_step(batch, state, by=""):
    """add a step at the end of the batch's history, dated today"""
    s = BATCHES.read_text(encoding="utf-8")
    a, b = batch_block(s, batch)
    block = s[a:b]
    # indent the new step like the steps that are there
    indent = re.search(r"\n([ \t]*)<step\b", block)
    indent = indent.group(1) if indent else "        "
    close = block.rindex("</batch>")
    before = block[:close].rstrip()
    by_attr = f' by="{esc(by)}"' if by else ""
    date = datetime.date.today().isoformat()
    # attributes in alphabetical order, as XXE saves them
    step = f'<step{by_attr} date="{date}" state="{state}"'
    step += "/>"
    end_indent = re.search(r"([ \t]*)$", s[:a]).group(1)
    block = before + "\n" + indent + step + "\n" + end_indent + block[close:]
    BATCHES.write_text(s[:a] + block + s[b:], encoding="utf-8")


def set_last_step_by(batch, by):
    """set who does the step the batch is in now"""
    s = BATCHES.read_text(encoding="utf-8")
    a, b = batch_block(s, batch)
    block = s[a:b]
    m = list(re.finditer(r"<step\b[^>]*?(/?)>", block))[-1]
    tag = retag(m.group(), "by", by)
    block = block[: m.start()] + tag + block[m.end() :]
    BATCHES.write_text(s[:a] + block + s[b:], encoding="utf-8")


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
        f"{'batch':6} {'state':13} {'who':14} {'since':10} {'editor':14} {'entries':>7} {'with def':>8}"
    )
    for b in sorted(set(batches) | set(count)):
        info = batches.get(b)
        if info is None:
            state, who, since, editor = "?", "", "", "(not in batches.xml)"
        else:
            last = steps(info)[-1] if steps(info) else None
            state = state_of(info) or "?"
            who = who_has(info) or "-"
            since = last.get("date") if last is not None else ""
            editor = info.get("editor")
        c = count[b]
        print(
            f"{b:6} {state:13} {who:14} {since:10} {editor:14} {c['entries']:7} {c['definition']:8}"
        )


def cmd_history(batch):
    batches = read_batches()
    need_batch(batch, batches)
    info = batches[batch]
    print(f"batch {batch}, editor {info.get('editor')}")
    for st in steps(info):
        print(f"  {st.get('date')}  {st.get('state'):13} {st.get('by') or '-'}")


def cmd_new(batch, editor):
    if not BATCH_ID.match(batch):
        sys.exit(
            f"{batch}: a batch id is the year (two digits) and a number, e.g. 2604"
        )
    if batch in read_batches():
        sys.exit(f"batch {batch} is already in batches.xml")
    s = BATCHES.read_text(encoding="utf-8")
    date = datetime.date.today().isoformat()
    # indented like the rest of the file (XXE saves it with the indent in
    # xxe/batches.xxe): one step for a batch, two for its steps
    unit = re.search(r"\n([ \t]*)<people\b", s)
    unit = unit.group(1) if unit else "   "
    lines = [f'{unit}<batch editor="{esc(editor)}" id="{batch}">']
    lines.append(f'{unit * 2}<step by="{esc(editor)}" date="{date}" state="edit"/>')
    lines.append(f"{unit}</batch>")
    i = s.rindex("</batches>")
    BATCHES.write_text(s[:i] + "\n".join(lines) + "\n" + s[i:], encoding="utf-8")
    print(f"batch {batch} ({editor}) added to batches.xml")


def cmd_editor(batch, name):
    need_batch(batch, read_batches())
    set_batch_attribute(batch, "editor", name)
    print(f"batch {batch}: editor is now {name}")


def cmd_assign(batch, name):
    batches = read_batches()
    need_batch(batch, batches)
    set_last_step_by(batch, name)
    print(f"batch {batch}: {name} has step {state_of(batches[batch])}")


def cmd_add(batch, path, move=False, force=False):
    batches = read_batches()
    need_batch(batch, batches)
    if state_of(batches[batch]) == "publish" and not force:
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


def cmd_next(batch, by=None, force=False):
    batches = read_batches()
    need_batch(batch, batches)
    now = state_of(batches[batch])
    if now == STATES[-1]:
        sys.exit(f"batch {batch} is published already")
    cmd_step(batch, STATES[STATES.index(now) + 1], by, force)


def cmd_step(batch, state, by=None, force=False):
    batches = read_batches()
    need_batch(batch, batches)
    info = batches[batch]
    # the editor makes the corrections, unless someone else is named
    if by is None and (state == "edit" or state.startswith("correcting")):
        by = info.get("editor")
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
    add_step(batch, state, by or "")
    who = f", {by} has it" if by else ", nobody has it yet"
    print(f"batch {batch} is now in state {state}{who}")


def cmd_missing(batch):
    """for XXE: the number of entries in the batch without a definition on
    the first line, then the entries"""
    d = Dictionary()
    missing = [
        describe(e)
        for _, _, _, e in d.entries
        if e.get("batch") == batch and not has_definition(e)
    ]
    print(len(missing))
    for m in missing:
        print(m)


def cmd_check():
    problems = []
    root = ET.parse(BATCHES).getroot()
    ids = collections.Counter(b.get("id") for b in root.iter("batch"))
    names = people()
    for b, n in ids.items():
        if n > 1:
            problems.append(f"batch {b} is {n} times in batches.xml")
    for info in root.iter("batch"):
        b = info.get("id")
        if not BATCH_ID.match(b or ""):
            problems.append(
                f"batch {b}: the id is not the year and a number, e.g. 2604"
            )
        if not steps(info):
            problems.append(f"batch {b}: has no steps")
        dates = [st.get("date") or "" for st in steps(info)]
        if dates != sorted(dates):
            problems.append(f"batch {b}: the steps are not in the order of their dates")
        for st in steps(info):
            if st.get("state") not in STATES:
                problems.append(f"batch {b}: unknown state {st.get('state')!r}")
        if steps(info) and not who_has(info) and state_of(info) != "publish":
            problems.append(
                f"batch {b}: nobody has step {state_of(info)}; "
                f"set someone with: batch.py assign {b} NAME"
            )
        names_used = [("editor", info.get("editor"))] + [
            (f"step {st.get('state')}", st.get("by")) for st in steps(info)
        ]
        for role, name in names_used:
            if name and name not in names:
                problems.append(
                    f"batch {b}: {role}: {name} is not in the list of people in batches.xml"
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
        "show each batch with its state, who has it and since when, "
        "its editor, how many entries it has and how many of them have "
        "a definition",
        lambda a: cmd_list(),
    )

    p = command(
        "history",
        "show the steps of the batch: when it moved on, and who did what",
        lambda a: cmd_history(a.batch),
    )
    p.add_argument("batch", metavar="BATCH")

    p = command(
        "new",
        'add a batch to batches.xml in state edit, e.g. "batch.py new 2624 Helena"',
        lambda a: cmd_new(a.batch, a.editor),
    )
    p.add_argument("batch", metavar="BATCH")
    p.add_argument("editor", choices=people())

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

    force_help = (
        "move to publish even when entries in the batch have no "
        "definition (they are listed otherwise, and nothing is changed)"
    )
    p = command(
        "next",
        "move the batch on to its next step, e.g. from proofread-1 to "
        'correcting-1: "batch.py next 2601 Helena". NAME is who does the '
        "step; for correcting it is the editor if left out",
        lambda a: cmd_next(a.batch, a.name, force=a.force),
    )
    p.add_argument("batch", metavar="BATCH")
    p.add_argument("name", metavar="NAME", nargs="?", choices=people() + [None])
    p.add_argument("--force", action="store_true", help=force_help)

    p = command(
        "step",
        "move the batch to any state, also back, e.g. to correcting-1 "
        "again after proofread-2",
        lambda a: cmd_step(a.batch, a.state, a.name, force=a.force),
    )
    p.add_argument("batch", metavar="BATCH")
    p.add_argument("state", choices=STATES)
    p.add_argument("name", metavar="NAME", nargs="?", choices=people() + [None])
    p.add_argument("--force", action="store_true", help=force_help)

    p = command(
        "assign",
        "set who does the step the batch is in now, e.g. the proofreader "
        "when it was not known when the batch moved on",
        lambda a: cmd_assign(a.batch, a.name),
    )
    p.add_argument("batch", metavar="BATCH")
    p.add_argument("name", choices=people())

    p = command(
        "editor",
        "change the editor of the batch",
        lambda a: cmd_editor(a.batch, a.name),
    )
    p.add_argument("batch", metavar="BATCH")
    p.add_argument("name", choices=people())

    p = command(
        "missing",
        "list the entries in the batch that have no definition; the "
        "first line is how many there are",
        lambda a: cmd_missing(a.batch),
    )
    p.add_argument("batch", metavar="BATCH")

    command(
        "check",
        "report problems that the schemas cannot find: entries in "
        "a batch that is not in batches.xml, batches without entries, "
        "batches whose current step nobody has, and so on",
        lambda a: cmd_check(),
    )

    args = parser.parse_args()
    try:
        args.func(args)
    except FileNotFoundError as err:
        sys.exit(str(err))


main()
