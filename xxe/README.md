# XXE configuration for dict-sme

`dict-sme.xxe` changes XMLmind XML Editor (XXE) for the files in `src/`.
It also brings the style sheet, `dict-sme.css`: without this folder
installed, XXE shows the files unstyled. Shortcuts are written for Windows
and Linux; on a Mac, Ctrl is Cmd, Alt is Option.

**New elements**

- A new entry ("+ entry") comes with one lemma and one definition group.
- A new definition group ("+ definition group") gets the next free id by
  itself: the letter after the highest one in the entry (a, b → c). Links
  to definition groups need the id, so it should never be missing or
  chosen by hand.

**Links** (Dictionary menu and buttons)

- **Insert reference…** (Ctrl+Alt+R): pick an entry, or one definition
  group of an entry with several, and a `<d_ref>` to it is inserted at the
  caret. The caret must be in a `<d>`. The text of the `d_ref` is the
  lemma; change it to the form used in the sentence.
- **+ synonym**, **+ antonym**, **+ synonyms**, **+ antonyms** (the buttons
  in the entry): open the same list, and add a `<syn>` or `<ant>` with a
  `<d_ref>` to the chosen entry or definition group. Synonyms and
  antonyms are always links; there is no way to type one as plain text.
- **Follow link** (Ctrl+Alt+L): with the caret in a link, go to the
  entry or definition group it points to, in this file or another one.
- **Go to entry…** (Ctrl+Alt+G): pick any entry (or variant lemma), in
  any file, and go to it.

**PDF and lists** (Dictionary menu)

- **PDF of a batch…**: asks for a batch number (the batch of the entry at
  the caret, if any, is filled in), makes the PDF and opens it. Without
  WeasyPrint, it opens the HTML in the browser instead, to be printed
  from there.
- **Refresh lists**: makes the lists below again in any case.

The checks are run in a terminal: `scripts/check_links.py` (links) and
`scripts/batch.py check` (batches).

**How it keeps up to date.** Every command first saves the document and
then runs `scripts/make_refs.py --if-stale`, which makes the lists again
only if a file in `src/` has changed since (after a save, a pull, a
branch switch). The lists are `xxe/refs.txt`, `xxe/goto.txt` and
`xxe/targets.xml`; they are not in git. Python 3 is needed on every
computer where XXE is used.

## Setup

XXE looks for add-ons in the `addon` folder of its preferences folder:

| | XXE preferences folder |
|---|---|
| Windows | `%APPDATA%\XMLmind\XMLEditor11\` |
| Mac | `~/Library/Application Support/XMLmind/XMLEditor11/` |
| Linux | `~/.xxe11/` |

The `11` is the XXE version.

**IMPORTANT:** Turn off XXE's quick start cache: Options → Preferences → Advanced →
Cached data, untick "Quick Start cache". With it on, XXE does not see
this configuration, or changes to it, until the cache is cleared. With it
off, restarting XXE is enough.

### Windows

1. Install Python 3 from <https://www.python.org/downloads/>. Keep
   "Use admin privileges when installing py.exe" and "Add python.exe to
   PATH" ticked. Check in a new Command Prompt that `py -3 --version`
   works.
2. Let XXE load this folder straight from the repository, so that
   `git pull` also updates the configuration. In a Command Prompt
   (change the path to where the repository is):

    ```sh
    setx XXE_ADDON_PATH "C:\Users\NAME\PATH-TO-FOLDER\dict-sme\xxe;+"
    ```

   The `;+` at the end is needed, or XXE no longer loads its own add-ons.
3. For PDFs: download the WeasyPrint executable for Windows from
   <https://github.com/Kozea/WeasyPrint/releases> (under "Assets" of the
   latest release), unpack it if it is a zip, and put `weasyprint.exe` in
   a folder `tools` in the repository (`C:\Users\NAME\dict-sme\tools\`).
   The folder is not in git. Without it, "PDF of a batch" opens the batch
   in the browser instead, to be printed to PDF from there.
4. Restart XXE.

### Mac

1. Install Python 3 from <https://www.python.org/downloads/> (or with
   Homebrew). Check in Terminal that `python3 --version` works.
2. Link this folder into XXE's add-on folder, so that `git pull` also
   updates the configuration (change the path to where the repository is):

    ```sh
    mkdir -p ~/Library/Application\ Support/XMLmind/XMLEditor11/addon
    ln -s ~/PATH-TO-FOLDER/dict-sme/xxe ~/Library/Application\ Support/XMLmind/XMLEditor11/addon/dict-sme
    ```

3. For PDFs: `brew install weasyprint` (Homebrew, <https://brew.sh>).
   Without it, "PDF of a batch" opens the batch in the browser instead,
   to be printed to PDF from there.
4. Restart XXE.

### Linux

1. Link this folder into XXE's add-on folder:

    ```sh
    ln -s "$PWD/xxe" ~/.xxe11/addon/dict-sme
    ```

2. Restart XXE. 

For PDFs: `pip install weasyprint`, or the distribution's package (e.g.
`apt install weasyprint`).

### Check

Open a file in `src/`. There should be a Dictionary menu. If there is
not, look in XXE's log (e.g. the terminal XXE was started from) for a line
about `dict-sme.xxe`.
