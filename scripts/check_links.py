#!/usr/bin/env python3
"""Check the links between entries: <d_ref> in definitions, synonyms and
antonyms.

A link points to the entry with that lemma (any of its variants), pos and
type, and with that homograph number when it is given; and to one of its
definition groups when dg_id is given. Reported:

  broken       no entry matches
  ambiguous    more than one entry matches: add the homograph number
  no such dg   the entry has no definition group with that id
  empty        the link has no text
  itself       a synonym or antonym of its own entry
  one-way      A has B as synonym (antonym), but B does not have A
  unpublished  an entry in a published batch links to an entry that is not
               published, so the link would not work on the website

The type must match exactly: a link without type does not match vuovdi
NomAg. One-way is checked for whole entries, not definition groups.
"""

import argparse
import collections
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
BATCHES = ROOT / "batches" / "batches.xml"
KINDS = [
    "broken",
    "ambiguous",
    "no such dg",
    "empty",
    "itself",
    "one-way",
    "unpublished",
]


def norm(t):
    return re.sub(r"\s+", " ", t or "").strip()


class Entry:
    def __init__(self, f, e):
        self.file, self.e = f, e
        lg = e.find("lg")
        self.pos = lg.get("pos")
        self.lemmas = lg.findall("l")
        self.dg_ids = {dg.get("id") for dg in e.findall("dg") if dg.get("id")}
        self.batch = e.get("batch")

    def __str__(self):
        l = self.lemmas[0]
        return " ".join(
            filter(None, (norm(l.text), self.pos, l.get("type"), l.get("hid")))
        )


def target(r):
    """how a link is written in the report"""
    return " ".join(
        filter(None, (r.get("lemma"), r.get("pos"), r.get("type"), r.get("hid")))
    ) + (f" (dg {r.get('dg_id')})" if r.get("dg_id") else "")


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--only",
        choices=KINDS,
        action="append",
        help="report only this kind of problem (can be given more than once)",
    )
    args = parser.parse_args()

    entries = [
        Entry(f, e)
        for f in sorted(SRC.glob("*.xml"))
        for e in ET.parse(f).getroot().iter("e")
    ]
    index = collections.defaultdict(list)  # (lemma, pos) -> [(entry, l)]
    for en in entries:
        for l in en.lemmas:
            index[(norm(l.text), en.pos)].append((en, l))

    def resolve(r):
        found = [
            en
            for en, l in index.get((norm(r.get("lemma")), r.get("pos")), [])
            if (l.get("type") or "") == (r.get("type") or "")
            and (r.get("hid") is None or l.get("hid") == r.get("hid"))
        ]
        return list(dict.fromkeys(found))

    published = set()
    if BATCHES.exists():
        published = {
            b.get("id")
            for b in ET.parse(BATCHES).getroot().iter("batch")
            # the state of a batch is that of its last step
            if b.findall("step") and b.findall("step")[-1].get("state") == "publish"
        }

    problems = collections.defaultdict(list)  # kind -> [message]
    related = collections.defaultdict(set)  # (entry, "syn"|"ant") -> target entries
    links = []  # (entry, where, d_ref, target entry)
    for en in entries:
        for where, parent in [("d", d) for d in en.e.iter("d")] + [
            (tag[:3], g) for tag in ("syng", "antg") for g in en.e.iter(tag)
        ]:
            for r in parent.iter("d_ref"):
                here = f"src/{en.file.name}: {en}: {where} → {target(r)}"
                if not norm("".join(r.itertext())):
                    problems["empty"].append(here)
                found = resolve(r)
                if not found:
                    problems["broken"].append(here)
                    continue
                if len(found) > 1:
                    problems["ambiguous"].append(
                        f"{here}: {', '.join(str(t) for t in found)}"
                    )
                    continue
                t = found[0]
                if r.get("dg_id") and r.get("dg_id") not in t.dg_ids:
                    has = ", ".join(sorted(t.dg_ids)) or "none"
                    problems["no such dg"].append(f"{here}: {t} has dg {has}")
                if where in ("syn", "ant"):
                    if t is en:
                        problems["itself"].append(here)
                    related[(en, where)].add(t)
                links.append((en, where, r, t))

    for (en, kind), targets in related.items():
        for t in targets:
            if t is not en and en not in related.get((t, kind), ()):
                name = "synonym" if kind == "syn" else "antonym"
                problems["one-way"].append(
                    f"src/{en.file.name}: {en} has {t} as {name}, but {t} (src/{t.file.name}) does not have {en}"
                )

    for en, where, r, t in links:
        if en.batch in published and t.batch not in published:
            problems["unpublished"].append(
                f"src/{en.file.name}: {en}: {where} → {target(r)}: {t} is not published"
            )

    lines, counts = [], []
    for kind in args.only or KINDS:
        if problems[kind]:
            lines.append(f"{kind} ({len(problems[kind])}):")
            lines += ["  " + p for p in sorted(set(problems[kind]))]
            counts.append(f"{len(problems[kind])} {kind}")
    total = sum(len(problems[k]) for k in args.only or KINDS)
    summary = f"{len(links)} links checked, " + (
        f"{total} problems: {', '.join(counts)}" if total else "no problems"
    )
    for line in lines:
        print(line)
    print(summary)
    sys.exit(1 if total else 0)


main()
