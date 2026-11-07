#!/usr/bin/env python3
"""Does this Chrome honor orphans/widows? Prints how many lines of a split paragraph
land on each side of a page break, with orphans/widows 1 vs 3.
Each paragraph is made of one repeated token per paragraph (p01, p02, ...), so a
line can be assigned to its paragraph by its first word."""
import os, re, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "polished-docs", "scripts"))
import md_to_pdf as M
import pdfplumber, logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)

def make(n_lines_cycle):
    paras = []
    for i in range(1, 16):
        k = n_lines_cycle[i % len(n_lines_cycle)]
        paras.append(" ".join(f"p{i:02d}" for _ in range(k * 12)))   # ~12 tokens per 6in line at 11pt
    return "\n\n".join(paras) + "\n"

def splits(pdf):
    out = []
    with pdfplumber.open(pdf) as d:
        pages = []
        for pg in d.pages:
            lines = [l["text"].split()[0] for l in pg.extract_text_lines() if l["top"] < pg.height * 0.92 and l["text"].split()]
            pages.append(lines)
    for a, b in zip(pages, pages[1:]):
        if a and b and a[-1] == b[0]:
            tok = a[-1]
            out.append((tok, a.count(tok), b[:6].count(tok) if b[0] == tok else 0))
    return out

for o in (1, 3):
    p = M.P.get("report")
    html = M.md_to_html(make([5, 7, 4, 9, 6]), p)
    html = html.replace("orphans: 3; widows: 3;", f"orphans: {o}; widows: {o};")
    d = tempfile.mkdtemp(); hp = os.path.join(d, "t.html"); open(hp, "w").write(html)
    pdf = os.path.join(d, "t.pdf"); M.print_pdf(hp, pdf)
    s = splits(pdf)
    # count lines of the continuing paragraph on page 2 properly: tokens at top of next page
    with pdfplumber.open(pdf) as dd:
        res = []
        for a, b in zip(dd.pages, dd.pages[1:]):
            la = [l["text"].split()[0] for l in a.extract_text_lines() if l["top"] < a.height*0.92]
            lb = [l["text"].split()[0] for l in b.extract_text_lines() if l["top"] < b.height*0.92]
            if la and lb and la[-1] == lb[0]:
                res.append((la[-1], la.count(la[-1]), lb.count(lb[0])))
    print(f"orphans/widows={o}: paragraph splits (token, lines before break, lines after break) = {res}")
