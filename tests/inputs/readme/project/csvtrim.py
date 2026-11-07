#!/usr/bin/env python3
"""csvtrim: strip whitespace from every cell and drop rows that are completely empty."""
import argparse
import csv
import sys


def trim(rows, keep_empty=False):
    """Return (trimmed rows, number of dropped rows)."""
    dropped = 0
    out = []
    for row in rows:
        cells = [c.strip() for c in row]
        if not keep_empty and not any(cells):
            dropped += 1
            continue
        out.append(cells)
    return out, dropped


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", help="CSV file to read")
    ap.add_argument("-o", "--output", help="write here instead of standard output (overwrites an existing file)")
    ap.add_argument("--delimiter", default=",", help="field delimiter for input and output (default ,)")
    ap.add_argument("--keep-empty", action="store_true", help="keep rows that are completely empty")
    a = ap.parse_args(argv)
    try:
        with open(a.input, newline="", encoding="utf-8") as f:
            rows, dropped = trim(csv.reader(f, delimiter=a.delimiter), a.keep_empty)
    except FileNotFoundError:
        print(f"csvtrim: no such file: {a.input}", file=sys.stderr)
        return 2
    out = open(a.output, "w", newline="", encoding="utf-8") if a.output else sys.stdout
    csv.writer(out, delimiter=a.delimiter, lineterminator="\n").writerows(rows)
    if a.output:
        out.close()
    print(f"csvtrim: dropped {dropped} empty rows", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
