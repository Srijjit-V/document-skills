#!/usr/bin/env python3
"""Score every tests/<repo>/<variant>/ folder: words, lint, PDF pages, reader test.

Reader test proxy: for each question, the number of words a reader passes before
the first text that answers it (regex in questions.json). Lower = found faster.
"-" = the doc never answers it. This is a position proxy, not human timing.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "clean-docs", "scripts"))
sys.path.insert(0, os.path.join(HERE, "..", "cram-sheet", "scripts"))
from doc_lint import lint  # noqa: E402
from cram_to_html import render_pdf  # noqa: E402

Q = json.load(open(os.path.join(HERE, "questions.json")))


def words_before(text, pattern):
    m = re.search(pattern, text, flags=re.I | re.M)
    if not m:
        return None
    return len(re.findall(r"\S+", text[:m.start()]))


def score(path, kind, questions):
    if not os.path.exists(path):
        return None
    text = open(path, encoding="utf-8").read()
    mode = "cram" if kind == "cheatsheet" else "standard"
    r = lint(text, budget=550 if kind == "cheatsheet" else None, mode=mode)
    pos = [words_before(text, q["answer_regex"]) for q in questions]
    found = [p for p in pos if p is not None]
    row = {"words": r["words"], "lint": r["score"], "headers": r["headers"],
           "bullets": r["bullets"], "bold": r["bold"], "answered": f"{len(found)}/{len(pos)}",
           "median_words_to_answer": sorted(found)[len(found) // 2] if found else None,
           "positions": pos, "issues": sorted(r["issues"])}
    if kind == "cheatsheet":
        html = path[:-3] + ".html"
        row["pdf_pages"] = render_pdf(html, html[:-5] + ".pdf") if os.path.exists(html) else None
    return row


def main():
    out = {}
    for repo, questions in Q.items():
        for variant in sorted(os.listdir(os.path.join(HERE, repo))):
            d = os.path.join(HERE, repo, variant)
            if not os.path.isdir(d):
                continue
            for kind in ("docs", "cheatsheet"):
                out[f"{repo}/{variant}/{kind}"] = score(os.path.join(d, kind + ".md"), kind, questions)
    json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1)
    print("| Run | Words | Lint | Hdr | Bul | Bold | Answered | Median words to answer | PDF pages | Lint flags |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for k, r in out.items():
        if r:
            print(f"| {k} | {r['words']} | {r['lint']} | {r['headers']} | {r['bullets']} | {r['bold']} | "
                  f"{r['answered']} | {r['median_words_to_answer']} | {r.get('pdf_pages', '')} | "
                  f"{', '.join(r['issues'])} |")


if __name__ == "__main__":
    main()
