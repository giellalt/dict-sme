#!/usr/bin/env python3
"""Find where a link points to, for "Follow link" in XXE.

Usage: find_target.py DOCUMENT_URL N

Prints "FILE E G" for the target of the N-th <d_ref> in the document (in
document order, counting from 1): the file in src/, the number of the <e>
among the elements in <r>, and the number of the <dg> among the elements
in <e>, or 0 for a link to the whole entry. This is what the go-to command
in xxe/dict-sme.xxe takes. Prints a line starting with "!" when the target
is not found.

Uses xxe/targets.xml, made by make_refs.py. XXE could look this up itself,
but its XPath takes many seconds on a list this long.
"""

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import url2pathname

ROOT = Path(__file__).resolve().parent.parent
TARGETS = ROOT / "xxe" / "targets.xml"


def norm(t):
    return re.sub(r"\s+", " ", t or "").strip()


def main():
    if len(sys.argv) != 3 or not sys.argv[2].isdigit():
        sys.exit(__doc__)
    url, n = sys.argv[1], int(sys.argv[2])
    path = (
        Path(url2pathname(unquote(urlparse(url).path)))
        if url.startswith("file:")
        else Path(url)
    )
    links = list(ET.parse(path).getroot().iter("d_ref"))
    if not 1 <= n <= len(links):
        print(f"! there is no link number {n} in {path.name}")
        return
    r = links[n - 1]
    want = (
        norm(r.get("lemma")),
        r.get("pos"),
        r.get("type") or "",
        r.get("dg_id") or "",
    )
    for t in ET.parse(TARGETS).getroot():
        if (t.get("l"), t.get("pos"), t.get("type"), t.get("dg")) == want and (
            r.get("hid") is None or t.get("hid") == r.get("hid")
        ):
            print(f"{t.get('f')} {t.get('e')} {t.get('g') or 0}")
            return
    print(
        f"! no entry found for {want[0]} {want[1]}"
        + (f" (dg {want[3]})" if want[3] else "")
        + "; scripts/check_links.py shows what is wrong with the link"
    )


main()
