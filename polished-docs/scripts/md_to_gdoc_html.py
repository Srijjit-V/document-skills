#!/usr/bin/env python3
"""md_to_gdoc_html: Markdown to minimal semantic HTML for a Google Docs import.

Usage:
  python3 md_to_gdoc_html.py doc.md -o doc.html [--preset report|compact|book]

Upload the result with Drive create_file (contentMimeType text/html). Docs turns
h1 to h3, p, ul, ol, table, b, i, a into real styles and lists. The script adds
INLINE font, size, line-height, and spacing hints (no <style> block, no classes),
because Docs ignores classes and honors inline styles. Tested on a live import: Docs honors
Georgia, sizes, bold, margins, and 'Courier New'; it drops 'Roboto Mono' and Consolas, and
list items and table cells need their own font or they fall back to Arial. Treat the
hints as best effort: read the doc back and run gdoc_normalize.py for the rest.
Needs: pip install markdown
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import presets as P  # noqa: E402
from mdutil import fix_list_starts, mark_references  # noqa: E402


def convert(md_text, preset="report"):
    try:
        import markdown
    except ImportError:
        raise SystemExit("setup: `pip install markdown` first")
    p = P.get(preset)
    body = markdown.markdown(fix_list_starts(md_text), extensions=["tables", "fenced_code", "sane_lists"] + (["nl2br"] if p["nl2br"] else []))
    body = re.sub(r"<t([dh])>(.*?)</t\1>", lambda m: f"<t{m.group(1)}>{m.group(2).replace(chr(92) + '|', '|')}</t{m.group(1)}>",
                  body, flags=re.S)
    font = p["font_gdoc"]
    base = f"font-family:{font};font-size:{p['body_pt']}pt;line-height:{p['leading'] * 100:.0f}%"
    indent = f";text-indent:{p['first_line_indent_em'] * p['body_pt']}pt" if p["first_line_indent_em"] else ""
    para = f'<p style="{base};margin:0 0 {p["para_space_pt"]}pt 0{indent}">'
    mono = f"font-family:'{P.FONT_CODE_GDOC}';font-size:{p['code_pt']}pt"
    if p["hanging_refs"]:   # References / Works Cited: 0.5 in hanging indent
        body = mark_references(body)
        hang = f'<p style="{base};margin:0 0 {p["para_space_pt"]}pt 36pt;text-indent:-36pt">'
        body = body.replace('<p class="ref">', hang)
    body = body.replace("<p>", para)
    for lvl, key in ((1, "h1_pt"), (2, "h2_pt"), (3, "h3_pt")):
        size = p[key]
        above = 0 if lvl == 1 else size * p["heading_above_em"]
        style = (f"font-family:{font};font-size:{size}pt;font-weight:bold;line-height:{p['heading_leading'] * 100:.0f}%;"
                 f"margin:{above:.1f}pt 0 {size * p['heading_below_em']:.1f}pt 0")
        if lvl == 1 and p["h1_align"] == "center":
            style += ";text-align:center"
        if lvl == 3 and p["kind"] == "academic":
            style += ";font-style:italic"
        body = re.sub(rf"<h{lvl}>", f'<h{lvl} style="{style}">', body)
    body = re.sub(r"<h[456]>(.*?)</h[456]>", r"<h3>\1</h3>", body, flags=re.S)  # max 3 levels
    # Docs falls back to Arial for list items and table cells unless each carries its own font.
    plain = f"font-family:{font};font-size:{p['body_pt']}pt"
    body = body.replace("<li>", f'<li style="{plain}">')
    body = re.sub(r"<td>", f'<td style="{plain}">', body)
    body = re.sub(r"<th>(.*?)</th>", lambda m: f'<th style="{plain}"><b>{m.group(1)}</b></th>', body, flags=re.S)
    body = re.sub(r"<pre><code[^>]*>", f'<pre style="{mono}">', body)
    body = body.replace("</code></pre>", "</pre>")
    inline_mono = f"font-family:'{P.FONT_CODE_GDOC}'"   # quoted; inline code: font only, size follows the paragraph
    body = re.sub(r"<code>", f'<span style="{inline_mono}">', body).replace("</code>", "</span>")
    return f'<!doctype html><html><head><meta charset="utf-8"></head><body>{body}</body></html>'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("md")
    ap.add_argument("-o", "--out")
    ap.add_argument("--preset", default="report", choices=list(P.PRESETS))
    a = ap.parse_args()
    out = a.out or os.path.splitext(a.md)[0] + ".gdoc.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(convert(open(a.md, encoding="utf-8").read(), a.preset))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
