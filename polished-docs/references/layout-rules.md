# Layout rules and where the numbers come from

Every number was read from the linked page on 2026-11-02 and 2026-11-04. `scripts/presets.py` turns them into seven presets.

## Presets

| Preset | Body | Leading | Paragraph | Side margins | Headings | Code size or page number |
|---|---|---|---|---|---|---|
| report | 11pt | 135% | 7pt space, no indent | 1.25 in | 22 / 15 / 12pt | 10pt |
| compact | 10.5pt | 135% | 6pt space, no indent | 1.15 in | 20 / 14 / 11.5pt | 10pt |
| book | 11pt | 135% | 1.5em first-line indent, no space | 1.5 in | 22 / 15 / 12pt | 10pt |
| academic | 12pt Times New Roman | 200% (double) | 0.5 in first-line indent, no space | 1 in all sides | 12 / 12 / 12pt, level 1 centered bold, level 3 bold italic | page number top right |
| letter | 11pt | 130% | 12pt (a blank line), no indent | 1 in | none | no page number |
| memo | 11pt | 130% | 10pt space | 1 in | 18 / 12 / 11pt | page number at bottom |
| resume | 10.5pt | 125% | none; tight bullets | 0.75 in | name 20pt, section 11pt | one page |

The last four are sourced differently. academic follows APA 7 and MLA 9 as read from [Purdue OWL APA](https://owl.purdue.edu/owl/research_and_citation/apa_style/apa_formatting_and_style_guide/general_format.html) and [MLA](https://owl.purdue.edu/owl/research_and_citation/mla_style/mla_formatting_and_style_guide/mla_general_format.html): 1 in margins, double spaced, 12pt Times New Roman, 0.5 in indent, 0.5 in hanging indent for references, headings per [Purdue OWL](https://owl.purdue.edu/owl/research_and_citation/apa_style/apa_formatting_and_style_guide/apa_headings_and_seriation.html). The official APA site returned empty pages, so APA's own wording is unverified. letter is block format ([Purdue OWL](https://owl.purdue.edu/owl/subject_specific_writing/professional_technical_writing/basic_business_letters/index.html)); margins and font are this skill's choice. memo follows the [Purdue memo format](https://owl.purdue.edu/owl/subject_specific_writing/professional_technical_writing/memos/format.html) for structure. resume uses [MIT CAPD](https://capd.mit.edu/resources/career-toolkit-crafting-an-effective-resume/): one page, margins at least 0.5 in, type at least 10pt.

Margins are a design choice. The rule they serve is 45 to 90 characters per line, which the linter measures (about 58 to 63 in tests). Heading sizes are also a choice: Butterick says make headings "just a little" bigger, so 22pt on 11pt text is larger than his advice. Keep or lower them to taste.

## Rules

| Rule | Number | Source |
|---|---|---|
| Body size, print | 10 to 12pt | [point size](https://practicaltypography.com/point-size.html) |
| Line spacing | 120 to 145% of point size | [line spacing](https://practicaltypography.com/line-spacing.html) |
| Line length | 45 to 90 characters | [line length](https://practicaltypography.com/line-length.html) |
| Margins at 12pt | 1.5 to 2.0 in; 1 in is too small | [page margins](https://practicaltypography.com/page-margins.html) |
| First-line indent | 1 to 4 times the point size | [first-line indents](https://practicaltypography.com/first-line-indents.html) |
| Paragraph space | 4 to 10pt, or 50 to 100% of body size | [space between paragraphs](https://practicaltypography.com/space-between-paragraphs.html) |
| Indent plus space | Never both | [first-line indents](https://practicaltypography.com/first-line-indents.html) |
| Heading levels | At most 3 | [headings](https://practicaltypography.com/headings.html) |
| Spaces or tabs to indent | Never | [first-line indents](https://practicaltypography.com/first-line-indents.html), [tabs](https://practicaltypography.com/tabs-and-tab-stops.html) |
| Extra returns for space | Never | [carriage returns](https://practicaltypography.com/carriage-returns.html) |
| Headings keep with next | Always | [keep with next](https://practicaltypography.com/keep-with-next-paragraph.html) |
| No skipped heading levels, sentence case | | [Google style](https://developers.google.com/style/headings) |
| No two headings in a row | | [Microsoft style](https://learn.microsoft.com/en-us/style-guide/scannable-content/headings) |
| Lists: 2 to 7 items, numbered only for sequence | | [Microsoft](https://learn.microsoft.com/en-us/style-guide/scannable-content/lists), [Google](https://developers.google.com/style/lists) |
| Text spacing tolerance (HTML, not PDF) | Line height 1.5, paragraph spacing 2x | [WCAG 1.4.12](https://www.w3.org/WAI/WCAG21/Understanding/text-spacing.html) |
| Width, AAA | At most 80 characters, not justified | [WCAG 1.4.8](https://www.w3.org/WAI/WCAG21/Understanding/visual-presentation.html) |

For an accessibility-first doc, raise leading to 150% (WCAG 1.4.8 asks for 1.5). That is above Butterick's 145% cap; pick one and say which.
