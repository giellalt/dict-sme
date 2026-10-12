#!/usr/bin/env python3
"""Make the lists that the Dictionary menu in XXE (xxe/dict-sme.xxe) uses.

Every entry in src/ is listed, and each definition group (dg) of entries
that have more than one. Variant lemmas are listed too, pointing to the
entry under its first lemma. A dg without an id cannot be linked to and is
left out. Three files are written in xxe/:

refs.txt     for "Insert reference" and the synonym and antonym buttons.
             Read by XXE's pick command: each target is two lines, the
             label shown in the list, then the <d_ref> inserted when it is
             chosen.
goto.txt     for "Go to entry": the entries and variant lemmas (not the
             definition groups), with the same labels, each followed by
             where the entry is: "FILE E 0", the file in src/ and the
             number of the <e> among the elements in <r>. (The 0 is the
             definition group, as in what find_target.py prints.)
targets.xml  for "Follow link": where each lemma (and each dg of it) is,
             looked up by find_target.py.

The Dictionary menu runs this with --if-stale before it uses the lists, so
it is normally not needed by hand.
"""

import argparse
import re
import xml.etree.ElementTree as ET
from html import escape
from pathlib import Path

from sme_alphabet import sort_key

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT = ROOT / "xxe"
FILES = ("refs.txt", "goto.txt", "targets.xml")
LABEL_DEFINITION = 60  # characters of the definition shown in the label


def norm(t):
    return re.sub(r"\s+", " ", t or "").strip()


def short(t):
    return t if len(t) <= LABEL_DEFINITION else t[: LABEL_DEFINITION - 1].rstrip() + "…"


def d_ref(l, pos, dg_id=None):
    """the <d_ref> to insert, as XML that XXE's paste command accepts.
    escape() also escapes ' so that the XXE macros can put it in XPath."""
    attrs = {
        "lemma": norm(l.text),
        "pos": pos,
        "type": l.get("type"),
        "hid": l.get("hid"),
        "dg_id": dg_id,
    }
    a = "".join(f' {k}="{escape(v)}"' for k, v in attrs.items() if v)
    return f'<?xml version="1.0" encoding="UTF-8"?><d_ref{a}>{escape(norm(l.text))}</d_ref>'


def name(l, pos):
    """how the label shows a lemma: dihtor N, giella N 2, vuovdi N NomAg"""
    return " ".join(filter(None, (norm(l.text), pos, l.get("type"), l.get("hid"))))


def targets(e):
    """(label, d_ref, dg or None) for the entry, its dgs and its variant
    lemmas"""
    lg = e.find("lg")
    pos = lg.get("pos")
    first, *variants = lg.findall("l")
    dgs = e.findall("dg")
    definition = lambda dg: short(
        norm(" ".join("".join(d.itertext()) for d in dg.findall("d")))
    )
    whole = name(first, pos) + (f" — {definition(dgs[0])}" if len(dgs) == 1 else "")
    yield whole, d_ref(first, pos), None
    if len(dgs) > 1:
        for n, dg in enumerate(dgs, 1):
            if dg in linkable(dgs):
                yield (
                    f"{name(first, pos)} {n}: {definition(dg)}",
                    d_ref(first, pos, dg.get("id")),
                    dg,
                )
    for v in variants:
        yield f"{name(v, pos)} → {name(first, pos)}", d_ref(first, pos), None


def linkable(dgs):
    return [dg for dg in dgs if dg.get("id") and dg.get("id") != "???"]


def stale(out):
    """a list is missing, or older than a file in src/ or this script"""
    made = [out / name for name in FILES]
    if not all(f.exists() for f in made):
        return True
    oldest = min(f.stat().st_mtime for f in made)
    return any(f.stat().st_mtime > oldest for f in [*SRC.glob("*.xml"), Path(__file__)])


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=OUT,
        help="write the lists in this folder instead of xxe/",
    )
    parser.add_argument(
        "--if-stale",
        action="store_true",
        help="only make the lists when a file in src/ has changed since",
    )
    args = parser.parse_args()
    out = args.output
    if args.if_stale and not stale(out):
        print(f"the lists in {out} are up to date")
        return
    refs, goto, rows = [], [], []
    for f in sorted(SRC.glob("*.xml")):
        # positions as in XPointer element(): among element children
        for n, e in enumerate(ET.parse(f).getroot(), 1):
            if e.tag != "e":
                continue
            where = f"{f.name} {n}"
            in_e = list(e)
            for label, ref, dg in targets(e):
                refs.append((label, ref))
                if dg is None:
                    goto.append((label, f"{where} 0"))
            lg = e.find("lg")
            for l in lg.findall("l"):
                key = {
                    "l": norm(l.text),
                    "pos": lg.get("pos"),
                    "type": l.get("type") or "",
                    "hid": l.get("hid") or "",
                }
                rows.append({**key, "dg": "", "f": f.name, "e": n, "g": ""})
                for dg in linkable(e.findall("dg")):
                    rows.append(
                        {
                            **key,
                            "dg": dg.get("id"),
                            "f": f.name,
                            "e": n,
                            "g": in_e.index(dg) + 1,
                        }
                    )
    out.mkdir(exist_ok=True)
    for lines, name in ((refs, "refs.txt"), (goto, "goto.txt")):
        lines.sort(key=lambda t: sort_key(t[0]))
        # the label and what goes with it must each be on one line
        (out / name).write_text(
            "".join(f"{norm(a)}\n{b}\n" for a, b in lines), encoding="utf-8"
        )
    (out / "targets.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<targets>\n'
        + "".join(
            "<t" + "".join(f' {k}="{escape(str(v))}"' for k, v in r.items()) + "/>\n"
            for r in rows
        )
        + "</targets>\n",
        encoding="utf-8",
    )
    print(f"{len(refs)} link targets -> {out}")


main()
