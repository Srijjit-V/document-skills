#!/usr/bin/env python3
"""Score the plain-vs-skill outputs in tests/general/ on content and layout.

Content per output: words, doc_lint score (with the document-type profile), reader
questions answered (regex answer keys in general-questions.json) and how far into the
text the answer first appears, and claims not found in the sources (source_check).
Layout per output: PDF built two ways, browser default print and polished-docs, then
measured (pages, body size, characters per line, leading, layout score, stranded headings).
Cram sheets: the HTML each arm produced, printed to PDF by Chrome.

Run with a Python that has markdown, pdfplumber, pymupdf (and Chrome installed):
  python3 tests/general_eval.py
Writes tests/general-results.json and tests/general-tables.md.
"""
import json
import logging
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for d in ("clean-docs", "cram-sheet", "polished-docs"):
    sys.path.insert(0, os.path.join(HERE, "..", d, "scripts"))
sys.path.insert(0, HERE)
import doc_lint  # noqa: E402
import layout_lint as L  # noqa: E402
import md_to_pdf as M  # noqa: E402
import presets as P  # noqa: E402
import source_check as SC  # noqa: E402
import cram_to_html as C  # noqa: E402
from layout_compare import default_print  # noqa: E402

logging.getLogger("pdfminer").setLevel(logging.ERROR)
Q = json.load(open(os.path.join(HERE, "general-questions.json")))
FILES = {  # task key -> (folder, file)
    "minutes": ("minutes", "minutes.md"), "memo": ("memo", "memo.md"),
    "cover-letter": ("cover-letter", "cover-letter.md"), "lab-report": ("lab-report", "lab-report.md"),
    "study-guide": ("study", "study-guide.md"), "cram-sheet": ("study", "cram-sheet.md"),
    "essay": ("essay", "essay.md"), "proposal": ("proposal", "proposal.md"), "readme": ("readme", "README.md"),
}
ARMS = ("plain", "skill")


def read(path):
    return open(path, encoding="utf-8", errors="ignore").read() if os.path.exists(path) else None


def words_before(text, pattern):
    m = re.search(pattern, text, flags=re.I | re.M | re.S)
    return None if not m else len(re.findall(r"\S+", text[:m.start()]))


def pdf_facts(pdf):
    import pdfplumber
    sizes = []
    with pdfplumber.open(pdf) as d:
        for pg in d.pages:
            sizes += [round(c["size"], 1) for c in pg.chars if c["text"].strip()]
    return (min(sizes) if sizes else None), (round(100 * sum(s < 10 for s in sizes) / len(sizes), 1) if sizes else None)


def content(task, arm):
    folder, fname = FILES[task]
    path = os.path.join(HERE, "general", folder, arm, fname)
    text = read(path)
    if text is None:
        return None
    spec = Q[task]
    mode = "cram" if task == "cram-sheet" else "standard"
    lint = doc_lint.lint(text, None, mode, None if task == "cram-sheet" else spec["type"])
    srcs = [read(os.path.join(HERE, s)) or "" for s in spec["sources"]]
    tr = SC.check(text, srcs)
    pos = [words_before(text, q["answer_regex"]) for q in spec["questions"]]
    found = [p for p in pos if p is not None]
    return dict(words=lint["prose_words"], total_words=lint["words"], lint=lint["score"], lint_pass=lint["pass"],
                lint_flags=sorted(lint["issues"]), answered=len(found), of=len(pos),
                median_pos=sorted(found)[len(found) // 2] if found else None, positions=pos,
                untraced={k: tr[k]["untraced"] for k in ("numbers", "names", "quotes", "citations")},
                traced_share=tr["traced_share"], hard_fail=tr["hard_fail"])


def layout(task, arm):
    folder, fname = FILES[task]
    base = os.path.join(HERE, "general", folder, arm)
    md = os.path.join(base, fname)
    if not os.path.exists(md):
        return None
    stem = os.path.splitext(fname)[0]
    out = {}
    if task == "cram-sheet":
        html = os.path.join(base, stem + ".html")
        if os.path.exists(html):
            pdf = os.path.join(base, stem + ".print.pdf")
            pages = C.render_pdf(html, pdf)
            mn, under = pdf_facts(pdf)
            r = L.lint_pdf(pdf, "cram")
            out["html"] = dict(pages=pages, body_pt=r["body_pt"], min_pt=mn, pct_under_10=under,
                               chars_per_line=r["avg_chars_per_line"], score=r["score"], issues=sorted(r["issues"]))
        return out
    preset = P.get(Q[task]["preset"])
    d_pdf, p_pdf = os.path.join(base, stem + ".default.pdf"), os.path.join(base, stem + ".polished.pdf")
    default_print(md, d_pdf)
    r, log = M.build_pdf(open(md, encoding="utf-8").read(), preset, p_pdf)
    for kind, pdf, res in (("default", d_pdf, L.lint_pdf(d_pdf, "doc")), ("polished", p_pdf, r)):
        mn, under = pdf_facts(pdf)
        out[kind] = dict(pages=res["pages"], body_pt=res["body_pt"], min_pt=mn, pct_under_10=under,
                         chars_per_line=res["avg_chars_per_line"], leading=res["leading"], score=res["score"],
                         stranded=len(res["issues"].get("stranded_heading", [])), issues=sorted(res["issues"]),
                         retried=bool(log) if kind == "polished" else False)
    md_lint = L.lint_md(open(md, encoding="utf-8").read())
    out["markdown"] = dict(score=md_lint["score"], issues=sorted(md_lint["issues"]))
    return out


def main():
    res = {}
    for task in FILES:
        for arm in ARMS:
            c, l = content(task, arm), layout(task, arm)
            res[f"{task}/{arm}"] = dict(content=c, layout=l)
    json.dump(res, open(os.path.join(HERE, "general-results.json"), "w"), indent=1)
    rows = ["| Task | Arm | Words | Lint | Qs answered | Median words to answer | Untraced nums / names / quotes / cites | Lint flags |",
            "|---|---|---|---|---|---|---|---|"]
    for k, v in res.items():
        c = v["content"]
        if not c:
            rows.append(f"| {k.split('/')[0]} | {k.split('/')[1]} | (missing) | | | | | |")
            continue
        u = c["untraced"]
        rows.append(f"| {k.split('/')[0]} | {k.split('/')[1]} | {c['words']} | {c['lint']} | {c['answered']}/{c['of']} | "
                    f"{c['median_pos']} | {len(u['numbers'])} / {len(u['names'])} / {len(u['quotes'])} / {len(u['citations'])} | "
                    f"{', '.join(c['lint_flags'])} |")
    rows += ["", "| Task | Arm | Build | Pages | Body pt | Min pt | % chars under 10pt | Chars/line | Leading | Layout score | Stranded |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, v in res.items():
        l = v["layout"]
        if not l:
            continue
        for kind, d in l.items():
            if kind == "markdown":
                continue
            rows.append(f"| {k.split('/')[0]} | {k.split('/')[1]} | {kind} | {d['pages']} | {d['body_pt']} | {d['min_pt']} | "
                        f"{d['pct_under_10']} | {d['chars_per_line']} | {d.get('leading', '')} | {d['score']} | {d.get('stranded', '')} |")
    open(os.path.join(HERE, "general-tables.md"), "w").write("\n".join(rows) + "\n")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
