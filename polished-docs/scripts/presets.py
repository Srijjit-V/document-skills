"""One table of layout presets. Every script in this skill reads it.

Numbers for report, compact, and book come from research/layout-rules.md
(Butterick, Practical Typography): body 10-12pt, leading 120-145%, 45-90 characters
per line, paragraph space 4-10pt OR a first-line indent of 1-4x the point size
(never both). Heading sizes and margins are design choices, checked by measurement
(characters per line) rather than by margin width.

academic follows APA 7 and MLA 9 student-paper basics as read from Purdue OWL
(research/general-docs.md): 1 in margins, double spacing, 12pt Times New Roman,
0.5 in first-line indent, 0.5 in hanging indent for the reference list, page number
at the top right. Standards override Butterick here, so academic has its own ranges.
letter, memo, and resume are conventions of this skill: see doc-types in clean-docs.
"""

MIN_BODY_PT = 10.0          # nothing in a regular doc goes below this
CHARS_PER_LINE = (45, 90)   # Butterick
LEADING_RANGE = (1.20, 1.45)

FONT_BODY_CSS = 'Georgia, "Times New Roman", Times, serif'
FONT_HEAD_CSS = FONT_BODY_CSS
FONT_TIMES_CSS = '"Times New Roman", Times, serif'
FONT_CODE_CSS = 'Menlo, Consolas, "Courier New", monospace'
# Fonts as Google Docs names them (weightedFontFamily.fontFamily)
FONT_BODY_GDOC = "Georgia"
FONT_CODE_GDOC = "Courier New"   # the HTML import honors this name; Roboto Mono and Consolas fall back to Arial (tested)
HEADING_SPACE = dict(above_em=1.4, below_em=0.4)   # heading spacing, in heading-size multiples (default)

DEFAULTS = dict(
    kind="doc", font_css=FONT_BODY_CSS, font_gdoc=FONT_BODY_GDOC,
    page_number="bottom",            # "bottom" | "top-right" | None
    leading_range=LEADING_RANGE, chars_range=CHARS_PER_LINE,
    heading_above_em=HEADING_SPACE["above_em"], heading_below_em=HEADING_SPACE["below_em"],
    heading_leading=1.15, h1_align="left", nl2br=False, hanging_refs=False, max_pages=None,
)

PRESETS = {
    "report": dict(
        body_pt=11.0, leading=1.35, para_space_pt=7.0, first_line_indent_em=0.0,
        margin_x_in=1.25, margin_y_in=1.0, h1_pt=22.0, h2_pt=15.0, h3_pt=12.0,
        code_pt=10.0, note="Default: reports, proposals, READMEs, guides."),
    "compact": dict(
        body_pt=10.5, leading=1.35, para_space_pt=6.0, first_line_indent_em=0.0,
        margin_x_in=1.15, margin_y_in=0.9, h1_pt=20.0, h2_pt=14.0, h3_pt=11.5,
        code_pt=10.0, note="Denser: reference docs, runbooks, minutes."),
    "book": dict(
        body_pt=11.0, leading=1.35, para_space_pt=0.0, first_line_indent_em=1.5,
        margin_x_in=1.5, margin_y_in=1.0, h1_pt=22.0, h2_pt=15.0, h3_pt=12.0,
        code_pt=10.0, note="Long prose: first-line indent, no paragraph space."),
    "academic": dict(
        kind="academic", font_css=FONT_TIMES_CSS, font_gdoc="Times New Roman",
        body_pt=12.0, leading=2.0, para_space_pt=0.0, first_line_indent_em=3.0,   # 3em x 12pt = 0.5 in
        margin_x_in=1.0, margin_y_in=1.0, h1_pt=12.0, h2_pt=12.0, h3_pt=12.0, code_pt=10.0,
        page_number="top-right", leading_range=(1.9, 2.5), chars_range=(45, 100),   # Docs "double" measures about 2.4x the font size
        heading_above_em=0.0, heading_below_em=0.0, heading_leading=2.0, h1_align="center",
        hanging_refs=True, note="APA 7 / MLA 9 essentials: double spaced, 0.5 in indent, hanging references."),
    "letter": dict(
        kind="letter", body_pt=11.0, leading=1.3, para_space_pt=12.0, first_line_indent_em=0.0,   # block format: blank line between paragraphs
        margin_x_in=1.0, margin_y_in=1.0, h1_pt=14.0, h2_pt=12.0, h3_pt=11.0, code_pt=10.0,
        page_number=None, chars_range=(45, 100), nl2br=True,
        note="Block-format business or cover letter, single spaced."),
    "memo": dict(
        kind="memo", body_pt=11.0, leading=1.3, para_space_pt=10.0, first_line_indent_em=0.0,
        margin_x_in=1.0, margin_y_in=1.0, h1_pt=18.0, h2_pt=12.0, h3_pt=11.0, code_pt=10.0,
        chars_range=(45, 100), nl2br=True,
        note="Memo: TO/FROM/DATE/SUBJECT block, rule, single-spaced body."),
    "resume": dict(
        kind="resume", body_pt=10.5, leading=1.25, para_space_pt=0.0, first_line_indent_em=0.0,
        margin_x_in=0.75, margin_y_in=0.6, h1_pt=20.0, h2_pt=11.0, h3_pt=10.5, code_pt=10.0,
        page_number=None, chars_range=(25, 120), nl2br=True, max_pages=1,
        note="One page, margins 0.75 in (MIT CAPD: at least 0.5 in), type at least 10pt."),
}


def get(name):
    if name not in PRESETS:
        raise SystemExit(f"unknown preset {name!r}; choose from {', '.join(PRESETS)}")
    p = {**DEFAULTS, **PRESETS[name]}
    # Fail loudly if a preset would break a rule (e.g. both indent and space).
    assert p["body_pt"] >= MIN_BODY_PT, f"{name}: body under {MIN_BODY_PT}pt"
    assert p["code_pt"] >= MIN_BODY_PT, f"{name}: code under {MIN_BODY_PT}pt"
    lo, hi = p["leading_range"]
    assert lo <= p["leading"] <= hi, f"{name}: leading {p['leading']} outside {p['leading_range']}"
    assert not (p["first_line_indent_em"] and p["para_space_pt"]), f"{name}: indent and space together"
    assert p["margin_x_in"] >= 0.5 and p["margin_y_in"] >= 0.5, f"{name}: margin under 0.5 in"
    p["name"] = name
    return p


if __name__ == "__main__":
    import json, sys
    print(json.dumps({n: get(n) for n in PRESETS}, indent=1) if len(sys.argv) < 2
          else json.dumps(get(sys.argv[1]), indent=1))
