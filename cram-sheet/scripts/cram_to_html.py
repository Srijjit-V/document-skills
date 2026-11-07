#!/usr/bin/env python3
"""cram_to_html: turn a Cram Sheet Markdown file into print-ready HTML (US Letter),
optionally render a PDF with headless Chrome and check the page count.

Usage:
  python3 cram_to_html.py SHEET.md [-o SHEET.html] [--pages 1|2] [--cols 3] [--pdf]

Input format (see references/cram-method.md):
  # Title                         -> page header
  > If you only read one thing: … -> full-width banner
  Legend: ★ most used · ⚠ gotcha  -> small legend line under the banner
  ## Box title                    -> one labeled box; boxes flow across columns
  tables, lists, code fences, short paragraphs inside boxes

Font size is fixed (8.5pt body, never below 8pt). If the PDF runs over --pages,
the script exits 1 so the caller cuts content instead of shrinking type.
"""
import argparse
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile

CSS = """
@page { size: letter; margin: 0.4in; }
:root { --ink:#111; --muted:#555; --rule:#bbb; --accent:#0b5cad; --warn:#a33; --box:#f6f7f9; }
* { box-sizing: border-box; }
body { font: 8.5pt/1.3 -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; color: var(--ink);
       background:#fff; margin: 0; }
.sheet { max-width: 7.7in; margin: 0 auto; }
header { display:flex; align-items: baseline; justify-content: space-between;
         border-bottom: 2px solid var(--ink); margin-bottom: 4pt; }
h1 { font-size: 15pt; margin: 0 0 2pt; }
.meta { color: var(--muted); font-size: 8pt; }
.one { background: var(--ink); color:#fff; padding: 4pt 6pt; margin: 0 0 3pt; font-size: 9.5pt; border-radius: 3pt; }
.one strong { color: #ffd84d; }
.one code { background: #333; color: #ffd84d; }
.legend { color: var(--muted); font-size: 8pt; margin: 0 0 5pt; }
.cols { column-count: var(--cols); column-gap: 8pt; }
section { break-inside: avoid; background: var(--box); border: 1px solid var(--rule);
          border-radius: 3pt; padding: 3pt 5pt 4pt; margin: 0 0 6pt; }
section.gotchas { border-color: var(--warn); background: #fff6f5; }
h2 { font-size: 9.5pt; margin: 0 0 2pt; color: var(--accent); text-transform: uppercase; letter-spacing: .03em; }
section.gotchas h2 { color: var(--warn); }
h3 { font-size: 8.5pt; margin: 3pt 0 1pt; }
p { margin: 1pt 0 2pt; }
ul, ol { margin: 1pt 0 2pt; padding-left: 11pt; }
li { margin: 0 0 1pt; }
table { border-collapse: collapse; width: 100%; margin: 1pt 0 2pt; }
th, td { text-align: left; vertical-align: top; padding: 1pt 3pt; border-bottom: 1px solid #ddd; }
th { font-size: 8pt; color: var(--muted); font-weight: 600; }
code { font: 8pt/1.25 ui-monospace, Menlo, Consolas, monospace; background:#e9ecf0; padding: 0 2pt; border-radius: 2pt;
       overflow-wrap: anywhere; }
td { overflow-wrap: break-word; }
pre { background:#e9ecf0; padding: 2pt 4pt; margin: 1pt 0 2pt; white-space: pre-wrap; border-radius: 2pt; }
pre code { background: none; padding: 0; }
a { color: var(--accent); text-decoration: none; }
footer { color: var(--muted); font-size: 7.5pt; border-top: 1px solid var(--rule); margin-top: 2pt; padding-top: 2pt; }
/* On screen, draw the sheet at full Letter height so empty space shows in screenshots. */
@media screen { body { background:#e5e5e5; } .sheet { background:#fff; padding: .4in; margin: 0 auto;
  min-height: 11in; } }
@media screen and (max-width: 700px) { .cols { column-count: 1; } .sheet { padding: 16px; } }
"""


def inline(s):
    s = html.escape(s, quote=False)
    codes = []  # protect code spans so ** inside them stays literal

    def keep(m):
        codes.append(m.group(1))
        return f"\x00{len(codes) - 1}\x00"
    s = re.sub(r"`([^`]+)`", keep, s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', s)
    return re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{codes[int(m.group(1))]}</code>", s)


def block_html(lines):
    out, i = [], 0
    while i < len(lines):
        l = lines[i]
        if l.strip().startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith("```"):
                j += 1
            out.append("<pre><code>" + html.escape("\n".join(lines[i + 1:j])) + "</code></pre>")
            i = j + 1
        elif l.strip().startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            head, body = rows[0], [r for r in rows[1:] if not all(re.match(r"^:?-+:?$", c) for c in r)]
            t = "<table><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr>"
            t += "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
            out.append(t + "</table>")
        elif re.match(r"\s*([-*+]|\d+\.)\s", l):
            tag = "ol" if re.match(r"\s*\d+\.", l) else "ul"
            items = []
            while i < len(lines) and re.match(r"\s*([-*+]|\d+\.)\s", lines[i]):
                items.append(re.sub(r"^\s*([-*+]|\d+\.)\s+", "", lines[i]))
                i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
        elif l.startswith("### "):
            out.append(f"<h3>{inline(l[4:])}</h3>")
            i += 1
        elif l.strip():
            para = []
            while i < len(lines) and lines[i].strip() and not re.match(r"\s*([-*+|]|\d+\.|```|#)", lines[i]):
                para.append(lines[i].strip())
                i += 1
            if not para:  # unmatched marker line; emit as text so we never loop
                para, i = [l.strip()], i + 1
            out.append(f"<p>{inline(' '.join(para))}</p>")
        else:
            i += 1
    return "\n".join(out)


def convert(md, cols=3):
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    lines = md.splitlines()
    title, one, legend, meta = "Cram sheet", "", "", ""
    sections, cur = [], None
    for l in lines:
        if l.startswith("# ") and not sections and title == "Cram sheet":
            title = l[2:].strip()
        elif l.startswith(">") and cur is None:
            one += " " + l.lstrip("> ").strip()
        elif l.lower().startswith("legend:") and cur is None:
            legend = l.split(":", 1)[1].strip()
        elif l.lower().startswith("source:") and cur is None:
            meta = l.split(":", 1)[1].strip()
        elif l.startswith("## "):
            cur = {"title": l[3:].strip(), "lines": []}
            sections.append(cur)
        elif cur is not None:
            cur["lines"].append(l)
    body = []
    for s in sections:
        cls = ' class="gotchas"' if re.search(r"gotcha|trap|pitfall|watch out|mistake|common error|exception|careful", s["title"], re.I) else ""
        body.append(f'<section{cls}><h2>{inline(s["title"])}</h2>\n{block_html(s["lines"])}</section>')
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{CSS}</style></head>
<body><div class="sheet" style="--cols:{cols}">
<header><h1>{inline(title)}</h1><span class="meta">{inline(meta)}</span></header>
{f'<p class="one">{inline(one.strip())}</p>' if one else ''}
{f'<p class="legend">Legend: {inline(legend)}</p>' if legend else ''}
<div class="cols">
{chr(10).join(body)}
</div></div></body></html>
"""


def find_chrome():
    for c in ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              "/Applications/Chromium.app/Contents/MacOS/Chromium",
              shutil.which("google-chrome") or "", shutil.which("chromium") or "",
              shutil.which("chromium-browser") or ""]:
        if c and os.path.exists(c):
            return c
    return None


def _chrome(args):
    chrome = find_chrome()
    if not chrome:
        return False
    with tempfile.TemporaryDirectory() as prof:
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        f"--user-data-dir={prof}"] + args,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    return True


def render_pdf(html_path, pdf_path):
    """Print to PDF; return page count, or None without Chrome."""
    if not _chrome(["--no-pdf-header-footer", f"--print-to-pdf={pdf_path}",
                    "file://" + os.path.abspath(html_path)]):
        return None
    with open(pdf_path, "rb") as f:
        return len(re.findall(rb"/Type\s*/Page[^s]", f.read()))


def render_png(html_path, png_path):
    """Screenshot at Letter width (816px = 8.5in) so you can eyeball overflow."""
    return _chrome([f"--screenshot={png_path}", "--window-size=816,1060",
                    "file://" + os.path.abspath(html_path)])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("md")
    ap.add_argument("-o", "--out")
    ap.add_argument("--pages", type=int, default=1)
    ap.add_argument("--cols", type=int, default=3)
    ap.add_argument("--pdf", action="store_true", help="render PDF with headless Chrome and check page count")
    ap.add_argument("--keep-pdf", action="store_true", help="keep the PDF next to the HTML (default: temp dir)")
    ap.add_argument("--screenshot", action="store_true", help="also write a PNG of page 1 to a temp dir")
    ap.add_argument("--tmpdir", help="where PDF/PNG checks go (default: a new system temp dir)")
    a = ap.parse_args()
    out = a.out or os.path.splitext(a.md)[0] + ".html"
    with open(a.md, encoding="utf-8") as f:
        doc = convert(f.read(), a.cols)
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"wrote {out}")
    if a.tmpdir:
        os.makedirs(a.tmpdir, exist_ok=True)
    if a.tmpdir:
        tmp = a.tmpdir          # reused and overwritten on each build; no new subfolder
    else:
        tmp = tempfile.mkdtemp(prefix="cram-")
    stem = os.path.splitext(os.path.basename(out))[0]
    if a.screenshot:
        png = os.path.join(tmp, stem + ".png")
        if render_png(out, png):
            print(f"screenshot {png}: open it and check for text spilling out of boxes or cells (exit code 1 means over the page budget, nothing else)")
    if a.pdf:
        pdf = (os.path.splitext(out)[0] if a.keep_pdf else os.path.join(tmp, stem)) + ".pdf"
        n = render_pdf(out, pdf)
        if n is None:
            print("no Chrome/Chromium found: open the HTML in a browser, print to PDF (Letter), count pages")
            return
        verdict = "OK" if n <= a.pages else "OVER BUDGET: cut content, do not shrink the font"
        print(f"pdf {pdf}: {n} page(s), budget {a.pages} -> {verdict}")
        sys.exit(0 if n <= a.pages else 1)


if __name__ == "__main__":
    main()
