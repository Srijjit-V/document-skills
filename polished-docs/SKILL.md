---
name: polished-docs
description: Lay out any document so it looks right as a PDF and as a Google Doc: real heading styles, one readable font, correct spacing and indents, sane line length, page numbers, nothing stranded at a page bottom, and the right form for the type (business letter, memo, resume, APA or MLA paper, report). Use whenever someone asks to format, lay out, polish, or "make this look professional", "format my paper", "turn this into a PDF", "put this in a Google Doc", or "clean up this Google Doc", or says pasted text shows literal # or **, has stray spacing or typed bullets, or looks different in Docs. Run after clean-docs when the words themselves are padded or generic; use cram-sheet for a one-page condensed version.
---

# polished-docs

AI Markdown assumes a renderer that hides its habits: blank lines as spacing, typed bullets, bold lines as headings, tiny type squeezed to fit. A PDF or Google Doc shows every one of them. This skill fixes layout only. It never rewrites the words. Numbers and sources: `references/layout-rules.md`.

`<skill>` means the folder this SKILL.md is in. Scripts need Python 3. The PDF path needs `pip install markdown pdfplumber pymupdf` and Chrome or Chromium.

## Step 0: Check the text first

If the draft is padded or sounds like AI, run clean-docs first. Layout cannot rescue 2,000 words of filler, and a longer document costs more pages at a readable size.

## Step 1: Write the layout card

```
Target:     pdf | google-doc | both
Document:   report | proposal | lab report | essay or paper | cover letter | letter | memo | resume | minutes | README | other
Page:       Letter (A4 only if asked)
Preset:     from the table below
Font/size:  from the preset; change only if the user, or their style guide, says so
Paragraphs: space between OR first-line indent (the preset decides). Never both.
Margins:    from the preset; judge by characters per line, not inches
Headings:   levels used, at most 3
Page cap:   resume 1; otherwise the user's limit
```

| Document | Preset | What it does |
|---|---|---|
| report, proposal, lab report, README, guide | `report` | Georgia 11pt, 135% leading, 7pt paragraph space, 1.25 in side margins |
| minutes, runbook, reference | `compact` | 10.5pt, tighter margins |
| long prose, essay without a style guide | `book` | first-line indent, no paragraph space |
| essay or paper in APA or MLA | `academic` | Times New Roman 12pt, double spaced, 0.5 in indent, 1 in margins, hanging indent for References or Works Cited, page number top right, APA heading levels 1 to 3 |
| cover letter, business letter | `letter` | block format: single spaced, blank line between paragraphs, no page number |
| memo | `memo` | TO/FROM/DATE/SUBJECT block, rule, single-spaced body |
| resume | `resume` | one page, 10.5pt, 0.75 in margins, section rules |

`academic` covers the essentials of APA 7 and MLA 9 student papers as read from Purdue OWL. It does not build a title page, the MLA name block, the MLA last-name header, an abstract, or block quotes. Say so, and tell the user to check their instructor's guide. Type goes below 10pt only on a cram sheet (the cram-sheet skill). Never shrink a document to hit a page count; cut content instead.

The document must be in the shape the preset expects. Shapes for letters, memos, and resumes are in clean-docs `references/doc-types.md`.

## Step 2: Fix the Markdown source

```bash
python3 <skill>/scripts/layout_lint.py doc.md
```

It flags stacked blank lines, space or tab indents, typed bullets, bullets with no blank line above them (many converters print those as typed dashes), skipped or more than 3 heading levels, ALL CAPS headings, bold-only fake headings, several h1s, double spaces, paragraphs over 150 words, and stacked headings. Fix each hit in the source. A PDF build hides some of these, because HTML collapses blank lines, but Google Docs and plain-text pastes show them. Bold-only lines also get no keep-with-next, so they end up alone at a page bottom.

## Step 3a: PDF

```bash
python3 <skill>/scripts/md_to_pdf.py doc.md -o doc.pdf --preset report --png-dir pages/
```

It prints through headless Chrome with print CSS: headings keep with the next block, orphans and widows set to 3, table headers repeat, table rows and short code blocks stay whole, page numbers where the preset puts them. If Chrome shrinks the page to fit a wide table, it retries with fixed columns and break-anywhere wrapping. It never ships smaller type. Exit codes: 0 ok, 1 over the page cap (cut content), 2 the layout check failed, 3 setup problem.

Look at the PNG pages yourself. The script cannot judge taste: awkward table columns, a code line wrapped mid-name, an address block that ran together. Details: `references/pdf.md`.

## Step 3b: Google Doc

Read `references/google-docs.md` and the google-workspace skill's `references/docs.md` first. In short:

1. `python3 <skill>/scripts/md_to_gdoc_html.py doc.md -o doc.html --preset report`, then Drive `create_file` with `contentMimeType: text/html`. The Docs import honors the inline fonts and spacing this script writes. Do not upload raw Markdown as plain text: it keeps every `#` and `**`.
2. With the Docs editor connector, read the doc (`documents.get`, `includeTabsContent=true`), run `python3 <skill>/scripts/gdoc_normalize.py doc.json --preset report`, and send its `batchUpdate` body as one call. It sets the named styles, adds `keepWithNext` to headings, removes blank-paragraph spacing and typed indents, and never touches tables or images.
3. Read the doc again. Report what the script lists but cannot fix: typed bullets, bold-as-heading, ALL CAPS headings.
4. Tell the user to add page numbers in the Docs menu (the API has no request for them; see the Docs Help page in the reference).

With no Docs editor connector, stop after step 1 and say plainly which fixes remain and that they are not applied.

## Step 4: Verify

- PDF: `python3 <skill>/scripts/layout_lint.py doc.pdf --preset report` (score out of 100; body size, characters per line, leading, stranded headings, sparse pages, edge margins).
- Google Doc: export with Drive `download_file_content` (`application/pdf`). The result is large and is saved to a file. Decode the base64 `content`, then lint and look at the pages.

## Step 5: Deliver

Five lines at most: path or link, preset, page count, lint score, and anything left undone (for example "page numbers not added" or "normalizer not run"). State what you ran and what you did not.
