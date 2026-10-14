#!/usr/bin/env python3
"""List the entries of a batch, for "Go to entry in batch" in XXE.

Usage: batch_goto.py BATCH

Writes xxe/batch.txt, read by XXE's pick command: for each entry of the
batch, in alphabetical order, the label shown in the list, then where the
entry is, "FILE E 0", as in goto.txt (see make_refs.py). Prints the number
of entries, or a line starting with "!" when the batch has none.
"""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from sme_alphabet import sort_key

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT = ROOT / "xxe" / "batch.txt"
LABEL_DEFINITION = 60  # characters of the definition shown in the label


def norm(t):
    return re.sub(r"\s+", " ", t or "").strip()


def label(e):
    """dihtor N — computer"""
    lg = e.find("lg")
    l = lg.find("l")
    name = " ".join(filter(None, (norm(l.text), lg.get("pos"), l.get("type"), l.get("hid"))))
    d = norm("".join(e.find("dg/d").itertext())) if e.find("dg/d") is not None else ""
    if len(d) > LABEL_DEFINITION:
        d = d[: LABEL_DEFINITION - 1].rstrip() + "…"
    return name + (f" — {d}" if d else "")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    batch = sys.argv[1]
    found = []
    for f in sorted(SRC.glob("*.xml")):
        # positions as in XPointer element(): among element children
        for n, e in enumerate(ET.parse(f).getroot(), 1):
            if e.tag == "e" and e.get("batch") == batch:
                found.append((label(e), f"{f.name} {n} 0"))
    if not found:
        print(f"! batch {batch} has no entries")
        return
    found.sort(key=lambda t: sort_key(t[0]))
    OUT.write_text("".join(f"{a}\n{b}\n" for a, b in found), encoding="utf-8")
    print(f"{len(found)} entries in batch {batch}")


main()
