# Layout test results: browser default vs polished-docs

**Bottom line:** Printed at readable size, every test doc scores 100/100 on the layout check, up from 60. Readable size costs pages: the plain-AI docs double from 18 to 36 pages. The two skills together beat plain AI printed by default: 14 pages at 11pt, against 18 pages with tiny type. The Google Docs normalizer was not run on a live Doc (no Docs editor connector), so its effect on a real document is unproven.

## What was tested

| Test | Real or synthetic | Result |
|---|---|---|
| 6 docs (itsdangerous, httpie, scrapy; plain-AI and clean-docs versions) printed two ways | Real, Chrome 156 on macOS | Table below |
| Google Doc import routes, 5 docs created in a live Drive and exported to PDF | Real, one account, private | Table further down |
| `gdoc_normalize.py` | **Synthetic Docs JSON only** | 15 unit tests; every request checked against Google's v1 discovery schema |
| `layout_lint.py` Markdown checks | Synthetic fixtures + the 6 docs | 5 unit tests |
| `md_to_pdf.py` shrink guard, `md_to_gdoc_html.py` | Real renders and unit tests | 5 + 6 tests |
| Pandoc, Typst, WeasyPrint, Playwright | Not tested | |
| Docs → PDF export of a doc after the normalizer | **Not done** | no Docs editor connector in this session |

Unit tests: `python3 -m unittest discover -p "test_*.py"` in `polished-docs/scripts`. 32 tests pass with the pip packages installed. Without them, 11 skip (the ones that need `markdown`, `pdfplumber`, or Chrome) and 21 still run.

## PDF: browser default print vs polished-docs

"Default" is Markdown to plain HTML with no CSS, printed by Chrome with its default settings. "Polished" is `md_to_pdf.py --preset report`. Files: `tests/layout/<repo>/<variant>/{default,polished}.pdf`. Full per-doc table: `layout-table.md`.

| | Default print | polished-docs |
|---|---|---|
| Pages, total over 6 docs | 28 | 50 |
| Body size | 8.4 to 12pt (scrapy plain-AI shrunk to 8.4) | 11pt in all six |
| Characters under 10pt | 43 to 54% of text in five docs; 99.6% in one | 0% in all six |
| Characters per line, average | 74 | 60 |
| Leading, average | 112% of point size | 136% |
| Layout score, average (out of 100) | 60 | 100 |
| Headings stranded at a page bottom | 3 | 0 |
| Browser header/footer in 8pt with the local file path | Yes | No (page number only) |
| Blank-line spacing hits in the Markdown | 0 | 0 |

Per source doc:

| Source | Default pages | Polished pages |
|---|---|---|
| plain-AI docs (3) | 18 | 36 |
| clean-docs docs (3) | 10 | 14 |

- **The chain:** plain AI printed by default was 18 pages of small, crowded type. clean-docs plus polished-docs is 14 pages at 11pt with 100/100 scores.
- **Chrome shrinks silently.** Two plain-AI docs (httpie, scrapy) printed at 7.7pt and 8.9pt even with the polished CSS, because a wide table overflowed the column. The guard reprinted them with fixed columns. The httpie doc went from 8 shrunk pages to 15 full-size pages.
- **Blank-line spacing is 0 everywhere.** All six docs came from Claude, which does not use blank lines as spacing in these outputs. The Markdown check is covered by synthetic fixtures only.
- **Stranded headings were real.** The default print had 3 (all in the plain-AI httpie doc). The polished first pass also had 1, caused by a bold line used as a heading; the build now keeps bold-only lines with the next block.
- **Where I fixed what I saw in the images:** table first columns broke mid-name (`httpie/client.p` then `y`), fixed by switching `overflow-wrap` from `anywhere` to `break-word`; `\|` printed with the backslash in tables, fixed; a bold lead-in line sat apart from its table, fixed.
- **Still imperfect:** in safe mode a long command in a table cell can wrap mid-token, and a wrapped code comment returns to the left margin. See `tests/layout/compare-*.png` for the page images I checked.

## Google Docs: import routes (live Drive, 2026-11-03)

Docs created from the same httpie excerpt, exported with Drive to PDF, then measured (`tests/gdoc/*.pdf`). Doc C is a shorter version of the excerpt, so compare formatting, not page counts. Docs are private to the connected Drive account; I did not share them.

| Doc | Route | Body | Fonts in the PDF | Lint | Main finding |
|---|---|---|---|---|---|
| A | `text/plain`, Markdown text | n/a | not exported | n/a | Read back: literal `#`, backticks, `\|---\|` rows |
| B | `text/markdown` (Docs' import) | 11pt | Arial; inline code Roboto Mono | 100, 3 pages | Headings, table, list are real. **Each code line became its own spaced Arial paragraph.** Headings not bold. |
| C | `text/html`, first converter draft | 11pt | Georgia plus Arial in lists and cells, code in Arial | 100, 2 pages | Fonts mixed; `Roboto Mono` dropped; header row not bold |
| D | font and tag probe | | | | `Courier New` honored; `Roboto Mono`, `Consolas` fall back to Arial; list items and cells need their own font; `<th><b>` is bold |
| E | `text/html`, final converter | 11pt | Georgia everywhere, Courier New code, 4 Arial characters (list numbers) | 90, 2 pages | **A heading was stranded at the bottom of page 1**, its list on page 2 |

What the normalizer would address, and what it would not:
- Addressed by design: the stranded heading (`keepWithNext`), leftover Arial from imports (named styles), blank-paragraph spacing, typed indents.
- Not addressed: table cell padding and repeating header rows (the API has `updateTableCellStyle` and `pinTableHeaderRows`; the script avoids tables), page numbers (no API request).
- Unverified: whether Docs accepts the field masks the script builds, whether the named-style change overrides the direct formatting the import writes, and how many direct overrides it must fix. Only a live run answers these.

**Account note:** Drive reports the owner of the five test docs as another account. If that is not an account you expect, check the Drive connector. The docs are titled "[polished-docs test] A" through "E". I did not delete them; trash them when you are done.

## Files

- `tests/layout/` PDFs (default and polished) and page-image comparisons
- `tests/gdoc/` Docs exports (`B`, `C`, `D`, `E` PDFs), the Markdown excerpts, and generated HTML
- `tests/layout-table.md`, `tests/layout-results.json`, `tests/layout_compare.py`, `tests/css_print_features.py`
