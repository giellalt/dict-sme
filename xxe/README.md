# XXE configuration for dict-sme

`dict-sme.xxe` changes XMLmind XML Editor (XXE) for the files in `src/`.
It brings a style sheet that gives a simple UI when editing the xml 
files, as well as an array of custom features and keyboard shortcuts.

## Features

- **Dictionary menu** and toolbar group with the commands below.
- **Links:** insert a link to an entry or definition group, and follow
  it (also by right-clicking the link).
- **Synonyms and antonyms** are added as links, picked from a list.
- **Go to** any entry, or to an entry in a batch.
- **New entry** gets the pos of the file; **new definition group** gets
  the next free id.
- **Ctrl+Enter** adds a new element of the kind the caret is in, right
  after it.
- **Move up/down** the definition, definition group, synonym, example,
  … at the caret, among others of its kind.
- **Batch info** (state, editor) shown on each entry.
- **PDF of a batch** for proofreading.

## Keyboard shortcuts

| Command | Windows / Linux | Mac |
|---|---|---|
| Insert reference | Ctrl+Alt+R | Cmd+Option+R |
| Follow link | Ctrl+Alt+L | Cmd+Option+L |
| Go to entry | Ctrl+Alt+G | Cmd+Option+G |
| Go to entry in batch | Ctrl+Alt+B | Cmd+Option+B |
| New one of the same kind after (definition, synonym, example, …) | Ctrl+Enter | Cmd+Enter |
| New entry | Ctrl+Alt+N | Cmd+Option+N |
| New definition group | Ctrl+Alt+Enter | Cmd+Option+Enter |
| New synonym | Ctrl+Alt+S | Cmd+Option+S |
| New antonym | Ctrl+Alt+A | Cmd+Option+A |
| New example | Ctrl+Alt+E | Cmd+Option+E |
| New idiom | Ctrl+Alt+I | Cmd+Option+I |
| New comment | Ctrl+Alt+C | Cmd+Option+C |
| Move up | Alt+Up | Option+Up |
| Move down | Alt+Down | Option+Down |


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

1. Install the [Python install manager](https://apps.microsoft.com/detail/9nq7512cxl7t) 

2. In a Command Prompt (change `"PATH-TO-FOLDER` to the actual path):

    ```sh
    setx XXE_ADDON_PATH "C:\Users\NAME\PATH-TO-FOLDER\dict-sme\xxe;+"
    ```

3. For PDFs: download the WeasyPrint executable for Windows from
   <https://github.com/Kozea/WeasyPrint/releases> (`weasyprint-windows-onefile.zip`
   under "Assets" of the latest release), unpack it, and put `weasyprint.exe` in
   a folder `tools` in the repository (`dict-sme\tools\`).

4. Restart XXE.

### Mac

1. Make sure [Python3](https://www.python.org/downloads/) and [homebrew](https://brew.sh/)
   both are installed. 

2. Link this folder into XXE's add-on folder as such. Change `"PATH-TO-FOLDER"`
   to the actual path.

    ```sh
    mkdir -p ~/Library/Application\ Support/XMLmind/XMLEditor11/addon
    ln -s ~/PATH-TO-FOLDER/dict-sme/xxe ~/Library/Application\ Support/XMLmind/XMLEditor11/addon/dict-sme
    ```

3. For PDFs: `brew install weasyprint`.

4. Restart XXE.

### Linux

1. Link this folder into XXE's add-on folder:

    ```sh
    ln -s "$PWD/xxe" ~/.xxe11/addon/dict-sme
    ```

2. For PDFs: `sudo apt install weasyprint`

3. Restart XXE. 


### Check

Open a file in `src/`. There should be a Dictionary menu. If there is
not, look in XXE's log (arrow in the bottom right) for a line
about `dict-sme.xxe`.
