# PDF path

`scripts/md_to_pdf.py` converts Markdown with the `markdown` package, wraps it in print CSS from `presets.py`, and prints it with headless Chrome (`--print-to-pdf --no-pdf-header-footer`). Then `layout_lint.py` measures the PDF.

## What was tested (Chrome 156.0.8078.80, macOS, 2026-11-02)

| Feature | Result | How checked |
|---|---|---|
| `thead { display: table-header-group }` repeats the header on each page | Works | Header row seen again on page 2 of a rendered doc |
| `@page { @bottom-center { content: counter(page) " / " counter(pages) } }` | Works | Footer "1 / 4" on every page ([Chrome 131 margin boxes](https://developer.chrome.com/blog/print-margins)) |
| `orphans: 3; widows: 3` | Works | With 1, a paragraph split 1 line then 2; with 3, it moved whole (`tests/css_print_features.py`, one page break) |
| `break-after: avoid` on h1 to h4 | Works for real headings | 0 stranded headings across the six test docs |
| Bold-only paragraph (`**Title**`) kept with the next block | Needs the `p.lead` rule the script adds | One stranded fake heading before the rule, none after |
| `break-inside: avoid` on rows and short code blocks | Works | Rows were not split across pages in the renders |

Chrome's headless page does not document these flags ([Chrome headless](https://developer.chrome.com/docs/chromium/headless)), so the behavior above comes from running them. `orphans` is listed as limited availability on [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/orphans), and it worked in this Chrome.

## The shrink-to-fit trap

When any element is wider than the column, Chrome scales the whole page down. Two plain-AI docs printed at 7.7pt and 8.9pt this way, with no warning. `md_to_pdf.py` measures the result, and if body text is under the preset size it reprints with fixed table columns and break-anywhere wrapping. The cost is honest page count: the plain-AI httpie doc went from 8 shrunk pages to 15 at 11pt. If it is still shrunk, the script says so and exits 2. Fix the source: shorten the long token, or split the table.

## Defaults a browser print uses (for comparison)

Plain HTML printed by Chrome with no CSS (measured on the itsdangerous doc): Times 12pt body, text about 0.33 in from the page edge, line height about 112%, monospace in Menlo 9.75pt, and a default header and footer in 8pt that print the date, the title, and the local file path. In the six test docs, 43 to 54% of characters were under 10pt in five of them, and 99.6% in the scrapy baseline, which Chrome had shrunk to 8.4pt body. None were under 10pt in the polished print (`tests/layout-results.md`).

## Limits of the checks

- Characters per line is the mean of body lines with at least 30 characters. Tables and code blocks skew it a little.
- Leading is the median gap after a line that runs to the right margin, over body size. Such a gap is certain to sit inside one paragraph. A plain median read 150% on bullet-heavy documents and a mode read paragraph gaps, because gaps between bullets and paragraphs are larger than line gaps. With fewer than 4 such gaps (a letter, a resume) leading is not measured.
- A stranded heading is detected as a large or fully bold short line that ends a page. A bold table header row could trigger it.
- The script cannot see taste: awkward column widths, a wrapped command, a table that needs splitting. Look at the pages.

## Alternatives

Pandoc ([pandoc.org](https://pandoc.org/)) delegates PDF output to other engines. Typst ([typst.app](https://typst.app/docs/)) is a typesetting system that is not Markdown-native. A competitor's post claims HTML-to-PDF tools break pagination and tables ([HN 46307205](https://news.ycombinator.com/item?id=46307205)). In these tests, print CSS handled table-header repeat, row splitting, and orphans correctly, but it did need the shrink guard above. Neither Pandoc nor Typst was tested here.
