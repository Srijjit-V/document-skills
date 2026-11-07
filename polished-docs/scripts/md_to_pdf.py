#!/usr/bin/env python3
"""md_to_pdf: render Markdown to a Letter PDF through print CSS in headless Chrome.

Usage:
  python3 md_to_pdf.py doc.md -o doc.pdf [--preset report|compact|book|academic|letter|memo|resume]
                       [--max-pages N] [--html doc.html] [--png-dir DIR]

Needs: python3, `pip install markdown`, Chrome or Chromium. For the self-check
(and --png-dir) also `pip install pdfplumber pymupdf`.

Exit codes: 0 ok; 1 over --max-pages (cut content; type is never shrunk);
2 the PDF failed the layout check (see report); 3 setup problem.
"""
import argparse
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import presets as P  # noqa: E402
from mdutil import fix_list_starts, mark_references  # noqa: E402,F401


# Second attempt when the first print was shrunk to fit: fixed columns, break anywhere.
SAFE_CSS = """
table { table-layout: fixed; }
td, th, code, pre, li, p { overflow-wrap: anywhere; word-break: break-word; }
"""


def page_rule(p, title_footer):
    font = p["font_css"]
    if p["page_number"] == "top-right":
        return f"@top-right {{ content: counter(page); font: {p['body_pt']}pt {font}; color: #111; }}"
    if p["page_number"] == "bottom":
        return (f'@bottom-center {{ content: {title_footer}counter(page) " / " counter(pages); '
                f"font: 10pt {font}; color: #555; }}")
    return ""


def kind_css(p):
    """Extra CSS for the document kinds that have a fixed form."""
    k, body = p["kind"], p["body_pt"]
    if k == "academic":   # APA 7 heading levels: 1 centered bold, 2 left bold, 3 left bold italic
        return ("h1 { text-align: center; } h3, h4 { font-style: italic; }"
                " p.ref { padding-left: 0.5in; text-indent: -0.5in; }")
    if k == "resume":
        return (f"h1 {{ text-align: center; margin-bottom: 2pt; }} h1 + p {{ text-align: center; margin: 0 0 6pt; }}"
                f" h2 {{ text-transform: uppercase; letter-spacing: .06em; border-bottom: .6pt solid #333;"
                f" padding-bottom: 1pt; margin: 8pt 0 3pt; }}"
                f" p {{ margin: 0 0 2pt; }} ul {{ margin: 0 0 3pt; padding-left: 1.1em; }} li {{ margin: 0 0 1pt; }}")
    if k == "memo":
        return "hr { border-top: 1pt solid #111; margin: 4pt 0 12pt; }"
    if k == "letter":
        return "h1 { margin-bottom: 12pt; }"
    return ""


def css_for(p, title_footer, safe=False):
    body, lead = p["body_pt"], p["leading"]
    indent = p["first_line_indent_em"]
    font = p["font_css"]
    h_above, h_below = p["heading_above_em"], p["heading_below_em"]
    para = (f"p {{ margin: 0; text-indent: {indent}em; }} p + p {{ text-indent: {indent}em; }}"
            if indent else f"p {{ margin: 0 0 {p['para_space_pt']}pt; }}")
    if indent and p["kind"] != "academic":  # book style: no indent right after a heading
        para += " h1 + p, h2 + p, h3 + p, pre + p, table + p, blockquote + p { text-indent: 0; }"
    hl = p["heading_leading"]
    return f"""
@page {{
  size: Letter;
  margin: {p['margin_y_in']}in {p['margin_x_in']}in;
  {page_rule(p, title_footer)}
}}
html {{ -webkit-print-color-adjust: exact; }}
body {{ font: {body}pt/{lead} {font}; color: #111; margin: 0;
        orphans: 3; widows: 3; hyphens: manual; text-align: left; }}
{para}
h1, h2, h3, h4 {{ font-family: {font}; line-height: {hl}; font-weight: 700;
                  break-after: avoid; break-inside: avoid; page-break-after: avoid; }}
h1 {{ font-size: {p['h1_pt']}pt; margin: 0 0 {p['h1_pt'] * h_below}pt; }}
h2 {{ font-size: {p['h2_pt']}pt; margin: {p['h2_pt'] * h_above}pt 0 {p['h2_pt'] * h_below}pt; }}
h3, h4 {{ font-size: {p['h3_pt']}pt; margin: {p['h3_pt'] * h_above}pt 0 {p['h3_pt'] * h_below}pt; }}
h1:first-child {{ margin-top: 0; }}
ul, ol {{ margin: 0 0 {p['para_space_pt'] or 7}pt; padding-left: 1.4em; }}
li {{ margin: 0 0 2pt; break-inside: avoid; }}
li > p {{ margin: 0 0 2pt; text-indent: 0; }}
code {{ font-family: {P.FONT_CODE_CSS}; font-size: {p['code_pt']}pt; background: #eef0f2; padding: 0 2pt;
        border-radius: 2pt; overflow-wrap: break-word; }}
pre {{ background: #eef0f2; padding: 5pt 7pt; margin: 0 0 {p['para_space_pt'] or 7}pt; border-radius: 3pt;
       white-space: pre-wrap; overflow-wrap: break-word; font-size: {p['code_pt']}pt; line-height: 1.3; }}
pre code {{ background: none; padding: 0; font-size: inherit; }}
pre.keep {{ break-inside: avoid; }}
table {{ border-collapse: collapse; width: 100%; margin: 0 0 {p['para_space_pt'] or 7}pt; table-layout: auto; }}
thead {{ display: table-header-group; }}
tr {{ break-inside: avoid; }}
th, td {{ text-align: left; vertical-align: top; padding: 3pt 5pt; border-bottom: 0.5pt solid #bbb;
          overflow-wrap: break-word; font-size: {body}pt; line-height: {min(lead, 1.4)}; text-indent: 0; }}
th {{ border-bottom: 1pt solid #555; font-weight: 700; }}
blockquote {{ margin: 0 0 {p['para_space_pt'] or 7}pt; padding-left: 10pt; border-left: 2pt solid #bbb; color: #333; }}
a {{ color: #0b5cad; text-decoration: none; }}
img {{ max-width: 100%; }}
hr {{ border: 0; border-top: 0.5pt solid #bbb; margin: 8pt 0; }}
p.lead {{ break-after: avoid; page-break-after: avoid; }}
{kind_css(p)}
""" + (SAFE_CSS if safe else "")


def md_to_html(md_text, p, footer_title=None, safe=False):
    try:
        import markdown
    except ImportError:
        print("setup: `pip install markdown` first", file=sys.stderr)
        raise SystemExit(3)
    exts = ["tables", "fenced_code", "sane_lists"] + (["nl2br"] if p["nl2br"] else [])
    body = markdown.markdown(fix_list_starts(md_text), extensions=exts)

    def keep_short(m):  # keep short code blocks whole; long ones may break
        return '<pre class="keep">' if m.group(1).count("\n") <= 25 else "<pre>"
    body = re.sub(r"<pre>(.*?)</pre>", lambda m: keep_short(m) + m.group(1) + "</pre>", body, flags=re.S)
    # GitHub-style Markdown writes a literal pipe inside a table cell as \|
    body = re.sub(r"<t([dh])>(.*?)</t\1>", lambda m: f"<t{m.group(1)}>{m.group(2).replace(chr(92) + '|', '|')}</t{m.group(1)}>",
                  body, flags=re.S)
    # A paragraph that is only bold text acts like a heading: keep it with what follows.
    body = re.sub(r"<p>(<strong>[^<]*</strong>:?)</p>", r'<p class="lead">\1</p>', body)
    if p["hanging_refs"]:
        body = mark_references(body)
    footer = f'"{footer_title}  \\00B7  " ' if footer_title else ""
    m = re.search(r"<h1[^>]*>(.*?)</h1>", body, flags=re.S)
    title = re.sub(r"<[^>]+>", "", m.group(1)) if m else "Document"
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f"<title>{html.escape(title)}</title><style>{css_for(p, footer, safe)}</style></head>"
            f"<body>{body}</body></html>")


def find_chrome():
    for c in ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              "/Applications/Chromium.app/Contents/MacOS/Chromium",
              shutil.which("google-chrome") or "", shutil.which("chromium") or "",
              shutil.which("chromium-browser") or ""]:
        if c and os.path.exists(c):
            return c
    return None


def print_pdf(html_path, pdf_path):
    chrome = find_chrome()
    if not chrome:
        print("setup: Chrome or Chromium not found", file=sys.stderr)
        raise SystemExit(3)
    with tempfile.TemporaryDirectory() as prof:
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--user-data-dir={prof}", f"--print-to-pdf={pdf_path}",
                        "file://" + os.path.abspath(html_path)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    if not os.path.exists(pdf_path):
        print("setup: Chrome produced no PDF", file=sys.stderr)
        raise SystemExit(3)


def build_pdf(md_text, p, out, html_path=None, footer_title=None):
    """Render with print CSS; if Chrome shrank the page to fit, retry with safe wrapping.
    Returns (lint result, list of log lines)."""
    import layout_lint as L
    hp = html_path or os.path.join(tempfile.mkdtemp(prefix="polished-"), "doc.html")
    log = []
    for safe in (False, True):
        with open(hp, "w", encoding="utf-8") as f:
            f.write(md_to_html(md_text, p, footer_title, safe))
        print_pdf(hp, out)
        r = L.lint_pdf(out, mode="doc", preset=p)
        shrunk = r["body_pt"] is not None and r["body_pt"] < p["body_pt"] - 0.3
        if not shrunk:
            return r, log
        if not safe:
            log.append(f"first print was shrunk to fit (body {r['body_pt']}pt, wanted {p['body_pt']}pt): "
                       "retrying with fixed table columns and break-anywhere wrapping")
        else:
            log.append("STILL SHRUNK: something is wider than the page. Shorten the long line or table "
                       "cell, or split the table. Type is not shrunk below the preset.")
    return r, log


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("md")
    ap.add_argument("-o", "--out")
    ap.add_argument("--preset", default="report", choices=list(P.PRESETS))
    ap.add_argument("--max-pages", type=int)
    ap.add_argument("--html", help="also keep the intermediate HTML here")
    ap.add_argument("--footer-title", help="text shown before the page number in the footer")
    ap.add_argument("--png-dir", help="write one PNG per page here to look at")
    a = ap.parse_args()
    p = P.get(a.preset)
    out = a.out or os.path.splitext(a.md)[0] + ".pdf"
    md_text = open(a.md, encoding="utf-8").read()
    r, log = build_pdf(md_text, p, out, a.html, a.footer_title)
    for line in log:
        print(line)
    print(f"wrote {out}: {r['pages']} page(s), body {r['body_pt']}pt, "
          f"{r['avg_chars_per_line']} chars/line, leading {r['leading']}, layout score {r['score']}/100")
    for k, v in r["issues"].items():
        print(f"  {k}: {v}")
    if a.png_dir:
        import pymupdf
        os.makedirs(a.png_dir, exist_ok=True)
        stem = os.path.splitext(os.path.basename(out))[0]
        with pymupdf.open(out) as d:
            for i, pg in enumerate(d, 1):
                pg.get_pixmap(dpi=80).save(os.path.join(a.png_dir, f"{stem}-p{i}.png"))
    max_pages = a.max_pages or p["max_pages"]
    if max_pages and r["pages"] > max_pages:
        print(f"OVER BUDGET: {r['pages']} pages > {max_pages}. Cut content; type stays at {p['body_pt']}pt.")
        sys.exit(1)
    sys.exit(0 if r["pass"] else 2)


if __name__ == "__main__":
    main()
