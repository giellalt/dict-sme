#!/usr/bin/env python3

from pathlib import Path
import subprocess
import sys

def main():
    # files are passed in as positional args to the script, however many..
    files = sys.argv[1:]

    schema = Path(__file__).parent.parent / "schema" / "dict-sme.rnc"

    ret = 0
    for f in files:
        if Path(f).name == "meta.xml":
            continue

        args = ["jing", "-c", str(schema), f]
        try:
            proc = subprocess.run(args, capture_output=True)
        except FileNotFoundError:
            print("Install the 'jing' program.")
            print("error: jing: command not found")
            return 1
        if proc.returncode != 0:
            print(proc.stderr.decode("utf-8"))
            ret = 1

    return ret


if __name__ == "__main__":
    raise SystemExit(main())
