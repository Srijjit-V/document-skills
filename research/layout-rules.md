# Layout rules for docs that look right

**Bottom line:** Body text 10 to 12pt, leading 120 to 145%, 45 to 90 characters per line, space between paragraphs OR a first-line indent (never both), real heading styles with keep-with-next, and no blank lines, tabs, or typed bullets used as layout. Every number below was read from the source page on 2026-11-02. Nothing here is a testable rule until a script can measure it; the last column says which.

## Print typography (Butterick, Practical Typography)

| Rule | Number | Source | Measured by |
|---|---|---|---|
| Body size, print | 10 to 12pt | [point size](https://practicaltypography.com/point-size.html) | `layout_lint` PDF body pt |
| Line spacing | 120 to 145% of point size | [line spacing](https://practicaltypography.com/line-spacing.html) | PDF line pitch / font size |
| Line length | 45 to 90 characters, spaces included | [line length](https://practicaltypography.com/line-length.html) | PDF average chars per line |
| Side margins at 12pt | 1.5 to 2.0 in; the 1 in default is too small | [page margins](https://practicaltypography.com/page-margins.html) | via chars per line |
| First-line indent | 1 to 4 times the point size | [first-line indents](https://practicaltypography.com/first-line-indents.html) | preset |
| Space between paragraphs | 4 to 10pt, or 50 to 100% of body size | [space between paragraphs](https://practicaltypography.com/space-between-paragraphs.html) | preset |
| Indent and space together | Never both ("Using both is a mistake.") | [first-line indents](https://practicaltypography.com/first-line-indents.html) | preset |
| Heading levels | At most 3; two is better | [headings](https://practicaltypography.com/headings.html) | Markdown lint |
| Heading size | Bigger "just a little"; no all caps, no underline | [headings](https://practicaltypography.com/headings.html) | Markdown lint (caps) |
| Indent with spaces or tabs | Never; use the indent setting | [first-line indents](https://practicaltypography.com/first-line-indents.html), [tabs](https://practicaltypography.com/tabs-and-tab-stops.html) | Markdown lint |
| Extra carriage returns for space | Never; use space between paragraphs | [carriage returns](https://practicaltypography.com/carriage-returns.html) | Markdown lint |
| Keep headings with the next paragraph | "Always use this option with headings." | [keep with next](https://practicaltypography.com/keep-with-next-paragraph.html) | PDF stranded-heading check |
| Bold or italic, not both; no underline in print | As little as possible | [bold or italic](https://practicaltypography.com/bold-or-italic.html), [underlining](https://practicaltypography.com/underlining.html) | Markdown lint (bold count) |
| Justified text | Only with hyphenation; left-align by default | [justified text](https://practicaltypography.com/justified-text.html) | preset (left) |

**Why margins are not a rule on their own:** Butterick's 1.5 to 2.0 in applies at 12pt. What matters is the line length it produces. At 11pt on Letter, 1.25 in side margins leave a 6 in column, which tests in the 45 to 90 range (see `tests/layout-results.md`). The linter measures characters per line, not the margin.

## Accessibility and style guides

| Rule | Detail | Source |
|---|---|---|
| Text spacing tolerance | Content must survive line height 1.5, paragraph spacing 2x, letter spacing 0.12, word spacing 0.16, with no loss of content. This is a tolerance test for HTML, not a default. The page says it does not apply to PDF. | [WCAG 1.4.12](https://www.w3.org/WAI/WCAG21/Understanding/text-spacing.html) |
| Width and spacing, AAA | Width no more than 80 characters, not justified, line spacing at least 1.5, paragraph spacing at least 1.5 times line spacing | [WCAG 1.4.8](https://www.w3.org/WAI/WCAG21/Understanding/visual-presentation.html) |
| Headings | Sentence case, no skipped levels, no empty headings, no links in headings | [Google style](https://developers.google.com/style/headings) |
| Stacked headings | "Avoid having two headings in a row without text in between" | [Microsoft style](https://learn.microsoft.com/en-us/style-guide/scannable-content/headings) |
| Lists | Numbered only for sequence; no one-item lists; parallel items | [Google style](https://developers.google.com/style/lists) |
| List length | At least 2 items, ideally at most 7 | [Microsoft style](https://learn.microsoft.com/en-us/style-guide/scannable-content/lists) |
| Docs structure | Use the built-in heading styles; use left-aligned text | [Google Docs accessibility](https://support.google.com/docs/answer/6199477) |

Two honest notes. The WCAG AAA spacing (1.5) sits above Butterick's 145% cap, so an accessibility-first preset would use 150%. Google's accessibility page has no rule about blank lines, so that rule rests on Butterick alone.

## Google Docs API (read from the reference pages)

| Fact | Source |
|---|---|
| `ParagraphStyle` has `namedStyleType`, `spaceAbove`, `spaceBelow`, `lineSpacing` (percent of normal, 100.0 is normal), `indentFirstLine`, `indentStart`, `keepWithNext`, `keepLinesTogether`, `avoidWidowAndOrphan` | [Document reference](https://developers.google.com/workspace/docs/api/reference/rest/v1/documents) |
| `UpdateNamedStyleRequest` exists and changes a named style; `fields` must include `namedStyleType`. **This corrects the brief, which said the API cannot change a named style.** | [Request reference](https://developers.google.com/workspace/docs/api/reference/rest/v1/documents/request) |
| No request inserts a page number or AutoText field (0 mentions on the request page). Footers can be created, but a page-number field cannot be added. | [Request reference](https://developers.google.com/workspace/docs/api/reference/rest/v1/documents/request) |
| Order requests in a batch by descending index | [Best practices](https://developers.google.com/workspace/docs/api/how-tos/best-practices) |
| `writeControl.requiredRevisionId` guards against stale writes; a batch is atomic | [batchUpdate](https://developers.google.com/workspace/docs/api/reference/rest/v1/documents/batchUpdate) |
| Indexes count UTF-16 code units | [Structure](https://developers.google.com/workspace/docs/api/concepts/structure) |
| Write limit: 60 per minute per user per project | [Limits](https://developers.google.com/workspace/docs/api/limits) |
| `CreateParagraphBulletsRequest` removes leading tabs, which can shift indexes | [Request reference](https://developers.google.com/workspace/docs/api/reference/rest/v1/documents/request) |

## Markdown into Google Docs

- Docs can import Markdown, and paste it when Tools > Preferences > Enable Markdown is on. Import and export are on by default; copy and paste are off ([Workspace Updates, July 2024](https://workspaceupdates.googleblog.com/2024/07/import-and-export-markdown-in-google-docs.html)).
- Google's help page documents headings, bold, italic, strikethrough, and links. It does not mention lists, tables, or code blocks ([Docs Help](https://support.google.com/docs/answer/12014036)).
- A vendor blog (Unmarkdown, so partly marketing) reports that plain paste leaves literal `#`, `**`, and pipe characters, and tables become pipes ([unmarkdown](https://unmarkdown.com/blog/5-things-that-break-when-you-paste-ai-output)). This is the symptom list the skill targets; treat the "20%" detection figure on that site as unverified.

## Print CSS (to test, not assume)

| Feature | What the source says | Status |
|---|---|---|
| `@page` size and margin | Baseline 2024 ([MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/@page)) | Source read |
| `break-after`, `break-inside` | Widely available ([MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/break-after)) | Source read |
| `orphans` | Initial value 2; "Limited availability" ([MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/orphans)) | Test in Chrome |
| Margin boxes such as `@bottom-center` with `counter(page)` | Chrome 131 added them ([Chrome blog](https://developer.chrome.com/blog/print-margins)) | Test in Chrome |
| Repeating `thead` on each page | Not confirmed from a source | Test in Chrome |
| Playwright `page.pdf` | Defaults to Letter, zero margins, no header or footer ([docs](https://playwright.dev/docs/api/class-page#page-pdf)) | Summary only |

## Not verified

- Reddit threads (r/googledocs and the others): blocked in the browser pane again on 2026-11-02.
- "AI Overview" text and the LinkedIn, X posts: Google search and LinkedIn are not fetchable here. Quotes from your brief stay labeled as supplied by you.
- Chrome print flags (`--print-to-pdf`, `--no-pdf-header-footer`): the Chrome headless page does not document them. The build script's behavior is tested instead.

## Fixed-form documents (added 2026-11-04)

Sourced rules for APA and MLA papers, memos, business letters, cover letters, and resumes are in [general-docs.md](general-docs.md#2-what-good-looks-like-by-document-type). The layout numbers they produce, and where each preset departs from Butterick:

| Preset | Numbers | Source | Departs from Butterick because |
|---|---|---|---|
| academic | 12pt Times New Roman, double spaced, 1 in margins, 0.5 in first-line indent, 0.5 in hanging indent for references, page number top right | [Purdue OWL APA](https://owl.purdue.edu/owl/research_and_citation/apa_style/apa_formatting_and_style_guide/general_format.html), [MLA](https://owl.purdue.edu/owl/research_and_citation/mla_style/mla_formatting_and_style_guide/mla_general_format.html) | The style guides require double spacing and 1 in margins; the resulting line is about 73 characters, inside 45 to 90 |
| letter | Block format, single spaced, blank line between paragraphs | [Purdue OWL](https://owl.purdue.edu/owl/subject_specific_writing/professional_technical_writing/basic_business_letters/index.html) | Paragraph space is 12pt (a blank line), above Butterick's 4 to 10pt, because block format specifies the blank line |
| memo | TO, FROM, DATE, SUBJECT block; single spaced; a page or two | [Purdue OWL](https://owl.purdue.edu/owl/subject_specific_writing/professional_technical_writing/memos/format.html) | none |
| resume | One page, margins at least 0.5 in, type at least 10pt | [MIT CAPD](https://capd.mit.edu/resources/career-toolkit-crafting-an-effective-resume/) | Short bullet lines, so characters per line runs lower |

**Google Docs import, tested 2026-11-04 (academic essay, live Drive):** Docs honored Times New Roman 12pt, a centered bold title, the 0.5 in first-line indent, and double spacing. Its "double" measures about 2.4 times the font size in the exported PDF, because Docs scales from the font's natural line height; that is what APA's double spacing means in Docs, so the academic preset accepts 1.9 to 2.5. Docs **dropped a negative `text-indent`**, so a hanging indent cannot come from the HTML. The normalizer sets it with `indentStart` 36pt and `indentFirstLine` 0pt, which has only been tested on synthetic JSON. Docs added no page number; that is manual.

**List starts:** Python-Markdown prints bullets as typed dashes when no blank line precedes them. AI output often writes an entry line and its bullets with no blank line, so `mdutil.fix_list_starts` inserts the line and `layout_lint` flags it.

**Measuring leading:** in list-heavy documents the gaps between bullets and paragraphs are larger than line gaps, so a median read 150 to 157%. The linter now measures only the gap after a line that runs to the right margin, which always sits inside one paragraph, and the result matches the CSS (136%, 130%, 200%).
