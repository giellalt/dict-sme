#!/usr/bin/env python3
"""Export the entries of a batch to a PDF for proofreading.

Collects the entries of each batch from src/*.xml, sorts them
alphabetically and writes pdf/batch-BATCH.pdf. Its state (the last step
in its history), its editor and who has the step it is in are taken from
batches.xml. The text of the PDF (headings,
labels, notes) is in North Sámi, unless --en is given.

Needs WeasyPrint for PDF output, either as a Python module or as a
program:
  Windows  the executable from https://github.com/Kozea/WeasyPrint/releases,
           saved as tools/weasyprint.exe in this repository (or anywhere on
           the PATH)
  Mac      brew install weasyprint
  Linux    pip install weasyprint (or the distribution's package)
With --open, the file is opened in the program the computer uses for it;
then, if WeasyPrint is missing, the HTML is written and opened in the
browser instead, to be printed from there.
"""

import argparse
import datetime
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from html import escape
from pathlib import Path
from textwrap import dedent

from sme_alphabet import sort_key

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
BATCHES = ROOT / "batches" / "batches.xml"
EXPORTS = ROOT / "pdf"  # not in git, see .gitignore
# Where the weasyprint program may be when it is not on the PATH: the
# Windows executable in tools/ (not in git), and Homebrew's folders on a
# Mac, which programs started from the Dock do not have on their PATH.
WEASYPRINT_PLACES = [
    ROOT / "tools" / "weasyprint.exe",
    ROOT / "tools" / "weasyprint",
    Path("/opt/homebrew/bin/weasyprint"),
    Path("/usr/local/bin/weasyprint"),
]
MISSING = (
    "WeasyPrint is missing (Windows: tools/weasyprint.exe, Mac: brew install "
    "weasyprint, Linux: pip install weasyprint); or use --html and print from a browser"
)

# the text in the PDF; --en picks the English one
TEXTS = {
    "en": {
        "title": "dict-sme · batch {batch}",
        "editor": "Editor: {name}",
        "proofreader": "Proofreader: {name}",
        "state": "State: {state}",
        "states": {},
        "entries": lambda n: f"{n} {'entry' if n == 1 else 'entries'}",
        "printed": "printed {date}",
        "missing": "{what} missing",
        "definition": "definition",
        "example": "example",
        "idiom": "idiom",
        "syn.": "syn.",
        "ant.": "ant.",
    },
    "sme": {
        "title": "dict-sme · sátnečoakkáldat {batch}",
        "editor": "Redaktevra: {name}",
        "proofreader": "Korrekturlohkki: {name}",
        "state": "Stáhtus: {state}",
        "states": {
            "edit": "redigeren",
            "proofread-1": "1. korrekturlohkan",
            "correcting-1": "1. divvun",
            "proofread-2": "2. korrekturlohkan",
            "correcting-2": "2. divvun",
            "publish": "almmuheapmái",
        },
        "entries": lambda n: f"{n} {'sátni' if n == 1 else 'sáni'}",
        "printed": "čálihuvvon {date}",
        "missing": "{what} váilu",
        "definition": "definišuvdna",
        "example": "ovdamearka",
        "idiom": "idioma",
        "syn.": "syn.",
        "ant.": "ant.",
    },
}
T = TEXTS["sme"]


def norm(t):
    return re.sub(r"\s+", " ", t or "").strip()


def inline(el):
    """Text of el with its d_ref children, as HTML."""
    out = [escape(el.text or "")]
    for child in el:
        if child.tag == "d_ref":
            out.append(f'<span class="ref">{escape(child.text or "")}</span>')
        else:
            out.append(escape("".join(child.itertext())))
        out.append(escape(child.tail or ""))
    return norm("".join(out)) if out else ""


def missing(what):
    text = T["missing"].format(what=T[what])
    return f'<span class="missing">[{text}]</span>'


def lemma(l):
    """a lemma, with its homonym number as a superscript"""
    hid = f"<sup>{escape(l.get('hid'))}</sup>" if l.get("hid") else ""
    return f'<span class="lemma">{escape(norm(l.text))}{hid}</span>'


def entry_html(e):
    lg = e.find("lg")
    ls = lg.findall("l")
    # pos is on lg (on l in older files), type on each l
    pos = lg.get("pos") or ls[0].get("pos") or ""
    types = [l.get("type") or "" for l in ls]
    if len(set(types)) == 1:
        # all variants have the same type: write it once, after the pos
        lemmas = ", ".join(lemma(l) for l in ls)
        tail = f"{escape(pos)}{' ' + escape(types[0]) if types[0] else ''}"
        head = f'{lemmas} <span class="pos">{tail}</span>'
    else:
        # the types differ: pos and type after each variant
        head = ", ".join(
            f"{lemma(l)}"
            f' <span class="pos">{escape(pos)}{" " + escape(t) if t else ""}</span>'
            for l, t in zip(ls, types)
        )
    out = [
        '<div class="entry">',
        f'<p class="head">{head}</p>',
    ]
    dgs = e.findall("dg")
    for n, dg in enumerate(dgs, 1):
        num = f'<span class="num">{n}</span> ' if len(dgs) > 1 else ""
        ds = [inline(d) or missing("definition") for d in dg.findall("d")]
        out.append(f'<p class="sense">{num}{"; ".join(ds)}</p>')
        for tag, item, label in (("syng", "syn", "syn."), ("antg", "ant", "ant.")):
            for g in dg.findall(tag):
                # each is a d_ref, shown as a link like those in definitions
                words = ", ".join(
                    inline(w) if norm("".join(w.itertext())) else missing(label)
                    for w in g.findall(item)
                )
                out.append(
                    f'<p class="rel"><span class="label">{T[label]}</span> {words}</p>'
                )
        for x in dg.iter("x"):
            out.append(
                f'<p class="ex">{escape(norm(x.text)) or missing("example")}</p>'
            )
    for ig in e.findall("ig"):
        i = escape(norm(ig.findtext("i"))) or missing("idiom")
        out.append(f'<p class="idiom">◊ <span class="i">{i}</span></p>')
        idgs = ig.findall("idg")
        for n, idg in enumerate(idgs, 1):
            num = f'<span class="num">{n}</span> ' if len(idgs) > 1 else ""
            d = escape(norm(idg.findtext("id"))) or missing("definition")
            out.append(f'<p class="idiom-def">{num}{d}</p>')
            for x in idg.findall("ix"):
                out.append(
                    f'<p class="ex idiom-ex">{escape(norm(x.text)) or missing("example")}</p>'
                )
    out.append("</div>")
    return "\n".join(out)


CSS = dedent("""
    @page {
        size: A4;
        /* wide right margin for handwritten notes */
        margin: 2cm 7cm 2.2cm 1.8cm;
        @top-left { content: string(batch); font-size: 8pt; color: #666; }
        /* in the corner, over the notes margin, so it reaches as far right as
           the left header reaches left */
        @top-right-corner { content: string(lemma, first) " – " string(lemma, last);
                            font-size: 8pt; color: #666; text-align: right;
                            padding-right: 1.8cm; }
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
    .ref { color: #1a4fd6; text-decoration: underline; }
    .missing { color: #b00000; font-style: normal; font-family: sans-serif;
               font-size: 8.5pt; }
    """)


def read_batches():
    if not BATCHES.exists():
        return {}
    return {b.get("id"): b for b in ET.parse(BATCHES).getroot().iter("batch")}


def collect(batch):
    entries = []
    for f in sorted(SRC.glob("*.xml")):
        for e in ET.parse(f).getroot().iter("e"):
            if e.get("batch") == batch:
                entries.append(e)
    return sorted(entries, key=lambda e: sort_key(norm(e.findtext("lg/l"))))


def page(batch, info, entries):
    title = T["title"].format(batch=batch)
    lines = []
    if info is not None:
        steps = info.findall("step")
        last = steps[-1] if steps else None
        state = last.get("state") if last is not None else ""
        lines.append(T["state"].format(state=escape(T["states"].get(state, state))))
        lines.append(T["editor"].format(name=escape(info.get("editor") or "")))
        # who proofreads this round
        if state.startswith("proofread") and last.get("by"):
            lines.append(T["proofreader"].format(name=escape(last.get("by"))))
    lines.append(
        f"{T['entries'](len(entries))}"
        f" · {T['printed'].format(date=datetime.date.today())}"
    )
    body = "\n".join(entry_html(e) for e in entries)
    return dedent(f"""
    <!DOCTYPE html>
        <html lang="se"><head><meta charset="utf-8"><title>{escape(title)}</title>
        <style>{CSS}</style></head><body>
        <header><h1>{escape(title)}</h1></header>
        <p class="info">{"<br>".join(lines)}</p>
        {body}
        </body></html>
    """)


def open_file(path):
    """open path in the program the computer uses for it, without waiting"""
    if sys.platform == "win32":
        os.startfile(path)
    else:
        subprocess.Popen(
            ["open" if sys.platform == "darwin" else "xdg-open", str(path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def pdf_maker():
    """a function (html, file) that writes html as a PDF, using WeasyPrint as
    a Python module, or else the weasyprint program; None if neither is
    there"""
    try:
        from weasyprint import HTML

        return lambda html, dst: HTML(string=html).write_pdf(dst)
    except (ImportError, OSError):
        # OSError: the module is there, but not the libraries it needs
        pass
    exe = shutil.which("weasyprint") or next(
        (str(p) for p in WEASYPRINT_PLACES if p.is_file()), None
    )
    if not exe:
        return None

    def make(html, dst):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "batch.html"
            src.write_text(html, encoding="utf-8")
            done = subprocess.run(
                [exe, str(src), str(dst)], capture_output=True, text=True
            )
        if done.returncode:
            sys.exit(f"weasyprint failed: {done.stderr.strip()}")

    return make


def main():
    global T
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "batches", nargs="+", metavar="BATCH", help="a batch id like 2601"
    )
    parser.add_argument(
        "-o", "--output", help="write here instead of pdf/ (only with one batch)"
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="write the HTML the PDF is made from instead, which "
        "is useful for working on the layout, or for printing "
        "from a browser",
    )
    parser.add_argument(
        "--en", action="store_true", help="write the text of the PDF in English"
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="open the file when it is written; without WeasyPrint, "
        "write the HTML and open it in the browser",
    )
    args = parser.parse_args()
    if args.output and len(args.batches) > 1:
        parser.error("-o can only be used with one batch")
    if args.en:
        T = TEXTS["en"]
    if not args.html:
        make_pdf = pdf_maker()
        if make_pdf is None:
            if not args.open:
                sys.exit(MISSING)
            print(
                "WeasyPrint is missing, so the HTML is opened in the browser; print it from there"
            )
            args.html = True
    batches = read_batches()
    for batch in args.batches:
        if batch not in batches:
            print(f"{batch}: not in {BATCHES.name}", file=sys.stderr)
        entries = collect(batch)
        if not entries:
            print(f"{batch}: no entries, skipped", file=sys.stderr)
            continue
        html = page(batch, batches.get(batch), entries)
        if args.output:
            dst = args.output
        else:
            EXPORTS.mkdir(exist_ok=True)
            dst = EXPORTS / f"batch-{batch}.{'html' if args.html else 'pdf'}"
        if args.html:
            Path(dst).write_text(html, encoding="utf-8")
        else:
            make_pdf(html, dst)
        print(f"{batch}: {len(entries)} entries -> {dst}")
        if args.open:
            open_file(dst)


main()
