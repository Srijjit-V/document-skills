#!/usr/bin/env python3
"""Build each docs.md two ways and measure both PDFs.

  default  : Markdown -> plain HTML (no CSS) -> Chrome print with its default settings
  polished : polished-docs/scripts/md_to_pdf.py, preset 'report'

Run with a Python that has markdown, pdfplumber, pymupdf installed:
  python3 tests/layout_compare.py
Writes tests/layout/<repo>/<variant>/{default,polished}.pdf and tests/layout-table.md.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SK = os.path.join(HERE, "..", "polished-docs", "scripts")
sys.path.insert(0, SK)
import layout_lint as L  # noqa: E402
import md_to_pdf as M  # noqa: E402
import presets as P  # noqa: E402

RUNS = [(r, v) for r in ("itsdangerous", "httpie", "scrapy") for v in ("baseline", "skill-v2")]


def default_print(md_path, pdf_path):
    import markdown
    body = markdown.markdown(open(md_path, encoding="utf-8").read(), extensions=["tables", "fenced_code"])
    html = f'<!doctype html><html><head><meta charset="utf-8"><title>{os.path.basename(md_path)}</title></head><body>{body}</body></html>'
    d = tempfile.mkdtemp(prefix="default-")
    hp = os.path.join(d, "doc.html")
    open(hp, "w", encoding="utf-8").write(html)
    chrome = M.find_chrome()
    with tempfile.TemporaryDirectory() as prof:   # NO --no-pdf-header-footer: this is the browser default
        subprocess.run([chrome, "--headless=new", "--disable-gpu", f"--user-data-dir={prof}",
                        f"--print-to-pdf={pdf_path}", "file://" + hp],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)


def polished(md_path, pdf_path):
    build = M.build_pdf(open(md_path, encoding="utf-8").read(), P.get("report"), pdf_path)
    return build[1]


def min_pt_and_small(pdf_path):
    import pdfplumber
    sizes = []
    with pdfplumber.open(pdf_path) as pdf:
        for pg in pdf.pages:
            sizes += [round(c["size"], 1) for c in pg.chars if c["text"].strip()]
    under10 = sum(1 for s in sizes if s < 10) / max(len(sizes), 1)
    return min(sizes), under10


def main():
    rows, data = [], {}
    for repo, var in RUNS:
        md = os.path.join(HERE, repo, var, "docs.md")
        out = os.path.join(HERE, "layout", repo, var)
        os.makedirs(out, exist_ok=True)
        ml = L.lint_md(open(md, encoding="utf-8").read())
        for kind, fn in (("default", default_print), ("polished", polished)):
            pdf = os.path.join(out, f"{kind}.pdf")
            note = fn(md, pdf)
            r = L.lint_pdf(pdf, "doc")
            mn, under = min_pt_and_small(pdf)
            strand = len(r["issues"].get("stranded_heading", []))
            blank = len(ml["issues"].get("stacked_blank_lines", []))
            data[f"{repo}/{var}/{kind}"] = dict(pages=r["pages"], body_pt=r["body_pt"], min_pt=mn,
                                               pct_under_10pt=round(under * 100, 1),
                                               chars_per_line=r["avg_chars_per_line"], leading=r["leading"],
                                               pdf_score=r["score"], stranded=strand, md_score=ml["score"],
                                               blank_line_spacing=blank, pdf_issues=sorted(r["issues"]),
                                               retried=bool(note))
            d = data[f"{repo}/{var}/{kind}"]
            rows.append(f"| {repo}/{var} | {kind} | {d['pages']} | {d['body_pt']} | {d['min_pt']} | "
                        f"{d['chars_per_line']} | {d['leading']} | {d['pdf_score']} | {d['stranded']} | "
                        f"{d['blank_line_spacing']} | {'yes' if d['retried'] else ''} | {', '.join(d['pdf_issues'])} |")
    hdr = ("| Doc | Build | Pages | Body pt | Min pt | Chars/line | Leading | PDF score | Stranded | "
           "Blank-line spacing | Safe retry | PDF flags |\n" + "|---" * 12 + "|\n")
    open(os.path.join(HERE, "layout-table.md"), "w").write(hdr + "\n".join(rows) + "\n")
    json.dump(data, open(os.path.join(HERE, "layout-results.json"), "w"), indent=1)
    print(hdr + "\n".join(rows))


if __name__ == "__main__":
    main()
