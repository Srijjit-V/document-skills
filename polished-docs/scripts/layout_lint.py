#!/usr/bin/env python3
"""layout_lint: score a doc's layout out of 100. Works on Markdown and PDF.

Usage:
  python3 layout_lint.py FILE.md|FILE.pdf [--mode doc|cram] [--preset NAME] [--json]

Markdown checks: stacked blank lines, space/tab indents, typed bullets,
skipped or too many heading levels, ALL CAPS headings, bold-only fake
headings, several h1, double spaces, paragraphs over 150 words, stacked headings.
PDF checks (needs `pip install pdfplumber`): body size, characters per line,
leading, headings stranded at a page bottom, sparse pages, text near the edge.

--mode cram allows body text under 10pt and tighter margins (cram sheets are
the one doc type allowed to do that). Exit 0 = pass (score >= 80, no hard fail).
"""
import argparse
import json
import logging
import os
import re
import statistics
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import presets as P  # noqa: E402
logging.getLogger("pdfminer").setLevel(logging.ERROR)  # silences harmless FontBBox warnings

PER_ISSUE = {  # (points per hit, cap)
    "stacked_blank_lines": (3, 15), "typed_indent": (3, 15), "typed_marker": (3, 15),
    "skipped_heading_level": (5, 10), "too_many_heading_levels": (10, 10),
    "all_caps_heading": (3, 9), "bold_fake_heading": (4, 16), "multiple_h1": (5, 5),
    "double_space": (1, 5), "long_paragraph": (2, 10), "stacked_headings": (3, 9),
    "list_without_blank_line": (3, 9),
    # PDF checks
    "body_size": (40, 40), "small_text": (10, 10), "chars_per_line": (15, 15), "leading": (10, 10),
    "stranded_heading": (10, 30), "sparse_page": (5, 15), "text_near_edge": (10, 10), "empty_pdf": (100, 100),
}
LIST_RE = re.compile(r"^\s*([-*+]|\d+[.)])\s+")
HEAD_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
TYPED_RE = re.compile(r"^\s*([•◦▪▫●○■□‣–—]|\(\d+\)|\([a-zA-Z]\))\s+\S")
BOLD_ONLY_RE = re.compile(r"^\s*(\*\*|__)[^*_].*?(\*\*|__)\s*:?\s*$")


def lint_md(text):
    issues = {}

    def add(cat, line, detail=""):
        issues.setdefault(cat, []).append(f"line {line}" + (f": {detail}" if detail else ""))

    lines = text.splitlines()
    in_code, blank_run, in_list = False, 0, False
    prev_kind = "blank"
    prev_heading_line = None
    levels, last_level, h1s = [], None, 0
    para, para_start = [], 0

    def flush(i):
        nonlocal para
        n = len(" ".join(para).split())
        if n > 150:
            add("long_paragraph", para_start, f"{n} words")
        para = []

    for i, raw in enumerate(lines, 1):
        if FENCE_RE.match(raw):
            flush(i)
            in_code = not in_code
            blank_run = 0
            prev_kind = "blank"
            continue
        if in_code:
            continue
        line = raw.rstrip("\n")
        if not line.strip() or re.fullmatch(r"\s*(&nbsp;|<br\s*/?>)\s*", line):
            if re.fullmatch(r"\s*(&nbsp;|<br\s*/?>)\s*", line):
                add("stacked_blank_lines", i, "spacing with &nbsp; or <br>")
            blank_run += 1
            if blank_run == 2:
                add("stacked_blank_lines", i, "2+ blank lines in a row")
            flush(i)
            prev_kind = "blank"
            continue
        blank_run = 0
        m = HEAD_RE.match(line)
        if m:
            flush(i)
            lvl, title = len(m.group(1)), m.group(2)
            levels.append(lvl)
            if lvl == 1:
                h1s += 1
            if last_level is not None and lvl > last_level + 1:
                add("skipped_heading_level", i, f"h{last_level} to h{lvl}")
            letters = re.sub(r"[^A-Za-z]", "", title)
            if len(letters) >= 4 and letters.isupper():
                add("all_caps_heading", i, title[:40])
            if prev_heading_line is not None:
                add("stacked_headings", i, "heading directly after a heading")
            last_level, prev_heading_line, in_list = lvl, i, False
            prev_kind = "blank"
            continue
        prev_heading_line = None
        is_list = bool(LIST_RE.match(line))
        if is_list and prev_kind == "text" and re.match(r"^([-*+]|1[.)])\s", line):
            add("list_without_blank_line", i, "bullets right under a text line print as typed dashes in many converters")
        if is_list:
            in_list = True
            prev_kind = "item"
        elif not line.startswith((" ", "\t")):
            in_list = False
            prev_kind = "text"
        else:
            prev_kind = "item" if prev_kind == "item" else "text"
        if TYPED_RE.match(line):
            add("typed_marker", i, line.strip()[:30])
        if not is_list and not in_list and not line.lstrip().startswith(("|", ">")):
            if line.startswith("\t") or re.match(r"^ {1,3}\S", line):
                add("typed_indent", i, "paragraph indented with spaces or a tab")
        if BOLD_ONLY_RE.match(line) and not is_list:
            add("bold_fake_heading", i, line.strip()[:40])
        body = re.sub(r"`[^`]*`", "x", line)  # keep a placeholder so removed code does not leave a double space
        if not body.lstrip().startswith("|") and re.search(r"\S  +\S", body):
            add("double_space", i)
        if not (is_list or line.lstrip().startswith(("|", ">"))):
            if not para:
                para_start = i
            para.append(line)
    flush(len(lines))
    if len(set(levels)) > 3:
        add("too_many_heading_levels", 1, f"levels used: {sorted(set(levels))}")
    if h1s > 1:
        add("multiple_h1", 1, f"{h1s} h1 headings")
    return _score(issues, {"headings": len(levels)})


def _score(issues, extra, hard_fail=False):
    score = 100
    for cat, hits in issues.items():
        per, cap = PER_ISSUE.get(cat, (5, 15))
        score -= min(cap, per * len(hits))
    score = max(0, score)
    out = {"score": score, "pass": score >= 80 and not hard_fail,
           "issues": {k: v[:6] + ([f"... +{len(v) - 6} more"] if len(v) > 6 else []) for k, v in issues.items()}}
    out.update(extra)
    return out


MONO = re.compile(r"mono|courier|menlo|consolas|code", re.I)


def lint_pdf(path, mode="doc", preset=None):
    try:
        import pdfplumber
    except ImportError:
        print("setup: `pip install pdfplumber` first", file=sys.stderr)
        raise SystemExit(3)
    issues, hard = {}, False

    def add(cat, detail):
        issues.setdefault(cat, []).append(detail)

    pages = []
    with pdfplumber.open(path) as pdf:
        for pn, page in enumerate(pdf.pages, 1):
            lines = []
            for ln in page.extract_text_lines(return_chars=True, strip=True):
                ch = [c for c in ln["chars"] if c["text"].strip()]
                if not ch:
                    continue
                size = Counter(round(c["size"], 1) for c in ch).most_common(1)[0][0]
                lines.append(dict(
                    text=ln["text"], top=ln["top"], bottom=ln["bottom"], x0=ln["x0"], x1=ln["x1"],
                    size=size, mono=bool(MONO.search(ch[0]["fontname"])),
                    bold=all("bold" in c["fontname"].lower() or "black" in c["fontname"].lower() for c in ch),
                    n=len(ch), chars=ch))
            pages.append(dict(w=float(page.width), h=float(page.height), lines=lines))
    if not pages or not any(p["lines"] for p in pages):
        add("empty_pdf", "no text found")
        return _score(issues, dict(pages=len(pages), body_pt=None, avg_chars_per_line=None, leading=None), True)

    def is_footer(p, l):
        return l["top"] > p["h"] * 0.92

    body_lines_all = [(p, l) for p in pages for l in p["lines"] if not is_footer(p, l)]
    size_chars = Counter()
    for _, l in body_lines_all:
        if not l["mono"]:
            size_chars[l["size"]] += l["n"]
    body = size_chars.most_common(1)[0][0] if size_chars else 0.0

    min_pt = P.MIN_BODY_PT if mode == "doc" else 7.0
    if body < min_pt:
        add("body_size", f"body text is {body}pt, minimum {min_pt}pt")
        hard = True
    small = sum(l["n"] for _, l in body_lines_all if l["size"] < min_pt - 0.05)
    total = sum(l["n"] for _, l in body_lines_all)
    if mode == "doc" and total and small / total > 0.02 and not hard:
        add("small_text", f"{small / total:.0%} of text is under {min_pt}pt")

    plain = [l for _, l in body_lines_all if not l["mono"] and abs(l["size"] - body) < 0.3 and l["n"] >= 30]
    avg = round(statistics.mean(l["n"] for l in plain), 1) if plain else None
    lo, hi = (preset or {}).get("chars_range", P.CHARS_PER_LINE)
    if avg is not None and mode == "doc" and not (lo <= avg <= hi):
        add("chars_per_line", f"average {avg} characters per line, want {lo} to {hi}")

    # Only the gap after a line that runs to the right margin is certain to sit inside one paragraph;
    # bullet-to-bullet and paragraph gaps are larger and would read as loose spacing.
    pitches = []
    for p in pages:
        ls = [l for l in p["lines"] if not l["mono"] and abs(l["size"] - body) < 0.3 and not is_footer(p, l)]
        if not ls:
            continue
        left, right = min(l["x0"] for l in ls), max(l["x1"] for l in ls)
        for a, b in zip(ls, ls[1:]):
            d = b["top"] - a["top"]
            if a["x1"] >= right - 0.1 * (right - left) and 0.9 * body < d < 2.6 * body:
                pitches.append(d)
    leading = round(statistics.median(pitches) / body, 2) if len(pitches) >= 4 and body else None
    lo_l, hi_l = (preset or {}).get("leading_range", P.LEADING_RANGE)
    if leading is not None and mode == "doc" and not (lo_l <= leading <= hi_l):
        add("leading", f"line spacing {leading * 100:.0f}% of point size, want {lo_l * 100:.0f}% to {hi_l * 100:.0f}%")

    for pn, p in enumerate(pages[:-1], 1):
        content = [l for l in p["lines"] if not is_footer(p, l)]
        if not content:
            continue
        last = max(content, key=lambda l: l["bottom"])
        head = (last["size"] > body + 0.4 or (last["bold"] and len(last["text"]) < 90 and last["size"] >= body)) \
            and not last["mono"] and "|" not in last["text"]
        if head:
            add("stranded_heading", f"page {pn} ends with \"{last['text'][:50]}\"")

    counts = [sum(l["n"] for l in p["lines"]) for p in pages]
    if len(pages) >= 3:
        med = statistics.median(counts)
        for pn, c in enumerate(counts[:-1], 1):
            if c < 0.35 * med:
                add("sparse_page", f"page {pn} has {c} characters, median {int(med)}")

    edge = 36.0 if mode == "doc" else 21.0
    worst = min(min(l["x0"] for l in p["lines"]) for p in pages if p["lines"])
    worst_r = min(p["w"] - max(l["x1"] for l in p["lines"]) for p in pages if p["lines"])
    if min(worst, worst_r) < edge:
        add("text_near_edge", f"text comes within {min(worst, worst_r) / 72:.2f} in of the page edge, want {edge / 72:.2f} in")

    return _score(issues, dict(pages=len(pages), body_pt=body, avg_chars_per_line=avg, leading=leading), hard)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--mode", choices=["doc", "cram"], default="doc")
    ap.add_argument("--preset", choices=list(P.PRESETS), help="use this preset's line-length and leading ranges")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.file.lower().endswith(".pdf"):
        r = lint_pdf(a.file, a.mode, P.get(a.preset) if a.preset else None)
    else:
        r = lint_md(open(a.file, encoding="utf-8").read())
    if a.json:
        print(json.dumps(r, indent=2))
    else:
        keys = [k for k in ("pages", "body_pt", "avg_chars_per_line", "leading", "headings") if r.get(k) is not None]
        print(("PASS" if r["pass"] else "FAIL"), f"score {r['score']}/100", "  ".join(f"{k} {r[k]}" for k in keys))
        for cat, hits in r["issues"].items():
            print(f"  {cat}: " + "; ".join(hits))
    sys.exit(0 if r["pass"] else 1)


if __name__ == "__main__":
    main()
