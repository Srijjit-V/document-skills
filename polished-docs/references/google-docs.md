# Google Docs path

Read the google-workspace skill's `references/docs.md` before editing a real Doc. It covers connector names, UTF-16 indexes, tabs, and verification. This file covers what polished-docs adds.

## What was tested (2026-11-03, a live Drive account, private docs)

Same Markdown excerpt, three import routes, each exported to PDF and measured:

| Route | Headings | Code blocks | Table | List | Fonts |
|---|---|---|---|---|---|
| `text/plain` (Markdown pasted as text) | Literal `#` | Literal fences and backticks | Literal pipes | Typed `1.` text | Docs default |
| `text/markdown` (Docs' own import) | Real headings (20pt and 16pt, not bold) | **Each line became its own spaced, proportional-font paragraph** | Real table, bold header row | Real numbered list | Arial; inline code in Roboto Mono |
| `text/html` from `md_to_gdoc_html.py` | Real, bold, sized | Lines kept together, `Courier New` | Real table, bold header | Real list | Georgia; code Courier New |

Facts from a font probe document (HTML import):
- `'Courier New'` is honored. `'Roboto Mono'` and `Consolas` silently fall back to Arial. `FONT_CODE_GDOC` is therefore `Courier New`.
- List items and table cells without their own `font-family` fall back to Arial, which gives mixed fonts. The converter styles every `li`, `td`, and `th`.
- `<th><b>` produces a bold header row. Paragraph margins from inline CSS are honored.
- Not honored or not available through import: repeating table header rows, table cell padding, keep-with-next on headings.

Observed defect after the shipped converter's import: the heading "How a request flows" sat alone at the bottom of page 1 and its list started page 2. Imported headings do not keep with the next paragraph. `gdoc_normalize.py` sets `keepWithNext` on the heading styles and on each heading paragraph.

Academic preset import (a live Drive doc, 2026-11-04): Docs honored Times New Roman 12pt, the centered bold title, the 0.5 in first-line indent, and double spacing (about 2.4 times the font size in the exported PDF, which is how Docs defines double). It **dropped a negative `text-indent`**, so reference lists import with both lines at 0.5 in. `gdoc_normalize.py` sets the hanging indent after a References or Works Cited heading with `indentStart` 36pt and `indentFirstLine` 0pt. It adds no page number. Bullets directly under a text line import as typed dashes unless a blank line precedes them, so `md_to_gdoc_html.py` fixes list starts first.

**Not tested:** the normalizer's batch against a live Doc. The session had Drive but no Docs editor connector, so `gdoc_normalize.py` has only run on synthetic Docs JSON (15 unit tests, every request validated against Google's v1 discovery schema, revision 20261028). Treat the first live run as a trial: read the Doc back and check.

## Workflow

1. Create: `md_to_gdoc_html.py`, then Drive `create_file`, `contentMimeType: text/html`. Prefer this over `text/markdown`, which breaks code blocks.
2. Read: `documents.get` with `includeTabsContent=true`. Save the JSON.
3. Plan: `gdoc_normalize.py doc.json --preset report -o batch.json`. It prints counts and a report.
4. Apply: one `batchUpdate` with the file's `requests` and `writeControl`. A stale revision returns 400; read again and rebuild. Never drop `requiredRevisionId`.
5. Verify: read again, export to PDF, run `layout_lint.py`, look at the pages.

## What the normalizer does

| Action | How |
|---|---|
| Set NORMAL_TEXT, HEADING_1 to 3 | `updateNamedStyle` with font, size, spacing, `keepWithNext` |
| Fix direct overrides that disagree | `updateParagraphStyle`, `updateTextStyle` on those ranges only |
| Remove blank-paragraph spacing | `deleteContentRange` on empty paragraphs (kept: last paragraph, any next to a table) |
| Remove typed indents | `deleteContentRange` on leading spaces and tabs (not in bullets, not in code fonts) |
| Order | Highest index first, ties: style, text style, delete |
| Guard | `writeControl.requiredRevisionId` from the read |

It never touches tables, inline objects, bullet indents, or paragraphs in a code font. It reports, without changing: typed bullets and numbers, bold-only lines that look like headings, ALL CAPS headings, heading levels beyond 3, stacked headings, TITLE and SUBTITLE.

## API facts (verified from the reference pages)

- `UpdateNamedStyleRequest` exists. `namedStyle.namedStyleType` must be set. The field-mask example in the reference lists the parent (`textStyle`) and the child (`textStyle.bold`); the script follows that and the schema test accepts it. If a live call rejects the parent entries, drop them. ([request reference](https://developers.google.com/workspace/docs/api/reference/rest/v1/documents/request))
- No request inserts a page number or AutoText field. Add page numbers by hand: [Use headers, footers, page numbers & footnotes](https://support.google.com/docs/answer/86629). The named-style UI route is Format > Paragraph styles > Normal text or a heading > Update to match ([Docs Help](https://support.google.com/docs/answer/116338)).
- `pinTableHeaderRows` and `updateTableCellStyle` exist, so repeating table headers and cell padding are possible. The normalizer does not use them because it never touches tables.
- Order requests by descending index ([best practices](https://developers.google.com/workspace/docs/api/how-tos/best-practices)). Write quota: 60 per minute per user per project ([limits](https://developers.google.com/workspace/docs/api/limits)). The Drive connector also returned "Resource has been exhausted" errors during testing; wait and retry once.
- Indexes count UTF-16 code units ([structure](https://developers.google.com/workspace/docs/api/concepts/structure)).
- `lineSpacing` is a percentage where 100 is normal ([document reference](https://developers.google.com/workspace/docs/api/reference/rest/v1/documents)). The 135% preset exported at about 123 to 136% of point size, so measure after import.
- Google's native Markdown paste is off by default; import and export are on ([Workspace Updates, July 2024](https://workspaceupdates.googleblog.com/2024/07/import-and-export-markdown-in-google-docs.html)).
