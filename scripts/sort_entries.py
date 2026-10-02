#!/usr/bin/env python3
"""Sort the entries of dictionary files in place.

Usage: sort_entries.py [FILE ...]

FILE defaults to all of src/*.xml. Entries with a definition (a d with
text) come first, then the rest; both parts are sorted in North Sámi
alphabetical order by their first lemma. The text of each entry is kept
exactly as it is, only the order changes.
"""

import collections
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from sme_alphabet import sort_key

ROOT = Path(__file__).resolve().parent.parent
ENTRY = re.compile(r"<e[ >].*?</e>", re.S)


def has_definition(e):
    return any("".join(d.itertext()).strip() for d in e.iter("d"))


def order(text):
    e = ET.fromstring(text)
    return (not has_definition(e), sort_key(e.findtext("lg/l") or ""))


def sort_file(path):
    s = path.read_text(encoding="utf-8")
    matches = list(ENTRY.finditer(s))
    if not matches:
        return
    entries = [m.group() for m in matches]
    gaps = [s[a.end() : b.start()] for a, b in zip(matches, matches[1:])]
    # only whitespace may be between the entries (XXE puts blank lines there)
    if any(g.strip() for g in gaps):
        sys.exit(f"{path}: something between the entries, not sorted")
    joiner = collections.Counter(gaps).most_common(1)[0][0] if gaps else ""
    entries.sort(key=order)
    start, end = matches[0].start(), matches[-1].end()
    path.write_text(s[:start] + joiner.join(entries) + s[end:], encoding="utf-8")
    print(f"{len(entries):6d} entries sorted in {path.name}")


def main():
    if sys.argv[1:2] in (["-h"], ["--help"]):
        sys.exit(__doc__)
    files = [Path(f) for f in sys.argv[1:]] or sorted((ROOT / "src").glob("*.xml"))
    for f in files:
        sort_file(f)


main()
