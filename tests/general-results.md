# General documents: plain Claude vs the skills

**Bottom line:** Across 8 non-code tasks, the skills cut length by 16% on average (memo 35%, lab report 27%, minutes 26%), lifted lint from 89 to 100, and the layout step took every PDF from a 69 to 74 average to 100 with no stranded headings. They did **not** change reader-question results (45 of 45 both ways) or source tracing: neither arm invented a fact that my checks or my reading caught. Plain Opus already stayed inside the sources when the sources were in the prompt. Whether that holds when the sources are thin is untested.

## What was tested

| Test | Real or synthetic | Result |
|---|---|---|
| 8 tasks, each written by plain Claude (no skills) and with the skills; 9 outputs per arm (the study task yields a guide and a cram sheet) | Fictional inputs written for this test, in `tests/inputs/` | Tables below |
| Layout of all 16 Markdown outputs, printed two ways | Real Chrome 156 renders | Tables below |
| Cram sheets: the HTML each arm produced, printed by Chrome | Real | Tables below |
| Google Doc import of the academic preset (one doc in a live Drive) | Real, private | Section below |
| `gdoc_normalize.py` | **Synthetic Docs JSON only** (no Docs editor tool in this session) | 18 unit tests, every request checked against Google's v1 schema |
| Skill descriptions on 28 everyday requests | **Proxy**: a model shown only the descriptions, not the real trigger mechanism | 28 of 28 correct, no false triggers on the 6 non-document requests |
| Resume preset | One synthetic sample and unit tests; no resume was among the 8 tasks | Renders to one page |
| Not tested | A human reader study; thin or missing sources; documents over 3 pages; APA title page and MLA name block (not built); the skills' real triggering | |

Inputs are fictional (people, a library, a company, three invented journal articles). Answer keys for 5 reader questions per task are in `general-questions.json`, outside the folders the writing agents could read. Agents were told to use only the folder for their task.

## Content and layout tables

Source-check columns count numbers, names, quotes, and citations not found in the sources. Most "untraced" numbers are computed (the lab reports), spelled out in words in the source (the minutes transcript says "twenty-four hundred"), or labeled as made-up practice numbers (the study guides). `source_check` cannot tell those from inventions; I reviewed the lists by hand.

| Task | Arm | Words | Lint | Qs answered | Median words to answer | Untraced nums / names / quotes / cites | Lint flags |
|---|---|---|---|---|---|---|---|
| minutes | plain | 544 | 80 | 5/5 | 61 | 17 / 0 / 0 / 0 | budget |
| minutes | skill | 404 | 100 | 5/5 | 79 | 15 / 0 / 0 / 0 |  |
| memo | plain | 499 | 78 | 5/5 | 48 | 3 / 1 / 0 / 0 | bold, bold_labels, filler |
| memo | skill | 325 | 100 | 5/5 | 49 | 0 / 0 / 0 / 0 |  |
| cover-letter | plain | 255 | 100 | 5/5 | 98 | 1 / 0 / 0 / 0 |  |
| cover-letter | skill | 210 | 100 | 5/5 | 54 | 1 / 0 / 0 / 0 |  |
| lab-report | plain | 1008 | 88 | 5/5 | 206 | 34 / 0 / 0 / 0 | bold_labels, filler |
| lab-report | skill | 739 | 100 | 5/5 | 107 | 18 / 0 / 0 / 0 |  |
| study-guide | plain | 743 | 100 | 5/5 | 191 | 7 / 0 / 1 / 0 |  |
| study-guide | skill | 691 | 98 | 5/5 | 197 | 6 / 0 / 0 / 0 | rule_of_three |
| cram-sheet | plain | 221 | 90 | 5/5 | 66 | 0 / 0 / 0 / 0 | bold |
| cram-sheet | skill | 336 | 100 | 5/5 | 45 | 3 / 0 / 0 / 0 |  |
| essay | plain | 817 | 86 | 5/5 | 277 | 0 / 6 / 0 / 0 | recap, restate |
| essay | skill | 690 | 100 | 5/5 | 204 | 0 / 0 / 0 / 0 |  |
| proposal | plain | 422 | 82 | 5/5 | 83 | 0 / 0 / 0 / 0 | bold, bold_labels |
| proposal | skill | 326 | 100 | 5/5 | 76 | 1 / 0 / 0 / 0 |  |
| readme | plain | 216 | 100 | 5/5 | 54 | 1 / 1 / 0 / 0 |  |
| readme | skill | 245 | 100 | 5/5 | 89 | 0 / 0 / 0 / 0 |  |

| Task | Arm | Build | Pages | Body pt | Min pt | % chars under 10pt | Chars/line | Leading | Layout score | Stranded |
|---|---|---|---|---|---|---|---|---|---|---|
| minutes | plain | default | 2 | 12.0 | 8.0 | 8.1 | 75.6 | 1.12 | 70 | 1 |
| minutes | plain | polished | 2 | 10.5 | 10.0 | 0.0 | 64.6 | 1.36 | 100 | 0 |
| minutes | skill | default | 1 | 12.0 | 8.0 | 5.5 | 73.4 | 1.12 | 80 | 0 |
| minutes | skill | polished | 2 | 10.5 | 10.0 | 0.0 | 63.3 | 1.36 | 100 | 0 |
| memo | plain | default | 2 | 12.0 | 8.0 | 8.1 | 79.9 | 1.12 | 70 | 1 |
| memo | plain | polished | 2 | 11.0 | 10.0 | 0.0 | 67.7 | 1.3 | 100 | 0 |
| memo | skill | default | 1 | 12.0 | 8.0 | 6.4 | 81.6 | 1.12 | 80 | 0 |
| memo | skill | polished | 1 | 11.0 | 10.0 | 0.0 | 65.9 | 1.3 | 100 | 0 |
| cover-letter | plain | default | 1 | 12.0 | 8.0 | 8.3 | 75 | 1.12 | 70 | 0 |
| cover-letter | plain | polished | 1 | 11.0 | 11.0 | 0.0 | 69.7 | 1.3 | 100 | 0 |
| cover-letter | skill | default | 1 | 12.0 | 8.0 | 10.3 | 82.4 | 1.12 | 70 | 0 |
| cover-letter | skill | polished | 1 | 11.0 | 11.0 | 0.0 | 67.3 | 1.3 | 100 | 0 |
| lab-report | plain | default | 3 | 12.0 | 8.0 | 7.8 | 70.5 | 1.12 | 60 | 1 |
| lab-report | plain | polished | 3 | 11.0 | 10.0 | 0.0 | 62.2 | 1.36 | 100 | 0 |
| lab-report | skill | default | 2 | 12.0 | 8.0 | 7.7 | 74.4 | 1.12 | 70 | 0 |
| lab-report | skill | polished | 3 | 11.0 | 10.0 | 0.0 | 62 | 1.36 | 100 | 0 |
| study-guide | plain | default | 3 | 12.0 | 8.0 | 8.6 | 66.0 | 1.12 | 70 | 0 |
| study-guide | plain | polished | 3 | 11.0 | 10.0 | 0.0 | 56.8 | 1.36 | 100 | 0 |
| study-guide | skill | default | 3 | 12.0 | 8.0 | 9.0 | 69.6 | 1.12 | 70 | 0 |
| study-guide | skill | polished | 3 | 11.0 | 10.0 | 0.0 | 60.8 | 1.36 | 100 | 0 |
| cram-sheet | plain | html | 1 | 10.0 | 9.5 | 11.1 | 58.1 |  | 100 |  |
| cram-sheet | skill | html | 1 | 8.5 | 8.0 | 97.6 | 43.6 |  | 100 |  |
| essay | plain | default | 2 | 12.0 | 8.0 | 5.1 | 88.2 | 1.12 | 80 | 0 |
| essay | plain | polished | 3 | 12.0 | 12.0 | 0.0 | 75.7 | 2.0 | 100 | 0 |
| essay | skill | default | 2 | 12.0 | 8.0 | 6.2 | 89.2 | 1.12 | 80 | 0 |
| essay | skill | polished | 2 | 12.0 | 12.0 | 0.0 | 75.0 | 2.0 | 100 | 0 |
| proposal | plain | default | 2 | 12.0 | 8.0 | 9.4 | 71.5 | 1.12 | 70 | 0 |
| proposal | plain | polished | 2 | 11.0 | 10.0 | 0.0 | 58.8 | 1.36 | 100 | 0 |
| proposal | skill | default | 2 | 12.0 | 8.0 | 11.9 | 76.4 | 1.12 | 70 | 0 |
| proposal | skill | polished | 2 | 11.0 | 10.0 | 0.0 | 63.6 | 1.36 | 100 | 0 |
| readme | plain | default | 2 | 12.0 | 8.0 | 36.2 | 83.6 | 1.12 | 60 | 1 |
| readme | plain | polished | 2 | 11.0 | 10.0 | 0.0 | 60.8 | 1.36 | 100 | 0 |
| readme | skill | default | 1 | 12.0 | 8.0 | 28.7 | 71.7 | 1.12 | 70 | 0 |
| readme | skill | polished | 2 | 11.0 | 10.0 | 0.0 | 62.3 | 1.36 | 100 | 0 |

## What the numbers say

| Measure | Plain | Skills |
|---|---|---|
| Average words (9 outputs) | 525 | 441 (-16%) |
| Average lint score | 89 | 100 |
| Reader questions answered | 45 / 45 | 45 / 45 |
| Layout score, browser-default print | 69 | 74 |
| Layout score, polished-docs | 100 | 100 |
| Headings stranded at a page bottom, default print | 4 | 0 |
| Text under 10pt, default print (average share) | 11.5% | 10.7% |
| Pages, 8 documents, default / polished | 17 / 18 | 13 / 16 |

- Length: Cuts by task: memo 499 to 325, lab report 1008 to 739, minutes 544 to 404, proposal 422 to 326, cover letter 255 to 210, essay 817 to 690, study guide 743 to 691. Two outputs got longer: the README (216 to 245) and the cram sheet (221 to 336, which is fuller, not padded).
- **What plain Claude's lint flags were:** bold labels and filler (memo, lab report), a closing recap and repeated paragraphs (essay), bold labels (proposal), and a 544-word minutes against a 500 budget.
- Cover letters, read side by side: Both are accurate. The plain one closes with "Thank you for considering my application" and pads ("supports the written side of the job"). The skill one opens with the point, says plainly that the writer has not supervised paid staff, and ends on the ask.
- Cram sheets: On this non-code topic plain Claude did **not** shrink its type: it used 10pt, left about half the page empty, and had no priority line. The skill's sheet is 8.5pt, holds 52% more, and adds a starred ranking, a priority line, a "what the teacher said to know" box, and a mistakes box that gives a reason for each item. It also left about a quarter of the page empty, because the notes ran out. The gain here is selection and structure, not rescuing tiny type.
- Layout: In the default print the address blocks of the plain cover letter run together on one line, the lab-report table loses its padding, and Chrome prints a date and the local file path in the margins. Polished output keeps address lines apart (the `letter` preset), pads tables, repeats header rows, and prints at the preset size. Readable layout costs pages: about 1 more page per 8 documents when the same text is printed with room to breathe.
- The chain: Plain Claude printed by default: 17 pages. Skills plus polished-docs: 16 pages at readable size, every score 100.

## What the runs exposed, and the fixes

Every skill run reported what got in its way. These changed the tools or the instructions afterwards; the 16 outputs were not regenerated, so they reflect the earlier versions.

| Run found | Fix |
|---|---|
| `source_check` said 46% traced on a transcript that spells out numbers | Warns when the source spells numbers out; SKILL.md says to check those by hand |
| `source_check` flagged "Rivera's (2021)" and text in an HTML comment | Possessives and comments are ignored |
| Memo header labels (**TO:**) and a bold Total row counted as bold overuse | Excluded from the bold count |
| Header-density rule nagged short READMEs and proposals that need their sections | Per-type words-per-header thresholds |
| No rule for notes that conflict, gaps the reader cares about, or inference beyond the sources | Added to clean-docs Step 2 |
| Tense error ("I do this work" for a job that ended) caught only by re-reading | Reader test now includes a tense and attribution pass |
| Word limit enforced as a maximum only | SKILL.md says to pass `--budget` and count a minimum by hand |
| Minutes, study guide, README, letter shapes were incomplete | doc-types updated (unclear-item markers, scope line, exit codes, contact details once) |
| No fallback when a cram sheet runs out of material | cram-sheet says to leave the page short and say so |

Found while testing the layout, separate from the runs:
- Bullets directly under an entry line printed as typed dashes (a resume). Fixed in both converters, and `layout_lint` flags it.
- Leading read 150 to 157% on bullet-heavy documents. The linter now measures only the gap after a line that runs to the right margin, and matches the CSS (136%, 130%, 200%).
- Docs' import dropped the hanging indent on references. The normalizer now sets it with `indentStart` and `indentFirstLine`.

## Google Doc: academic preset (live Drive, 2026-11-04)

One essay excerpt imported through the HTML route and exported to PDF (`tests/gdoc/F-academic-import.pdf`):

| Check | Result |
|---|---|
| Times New Roman 12pt, bold centered title | Honored |
| 0.5 in first-line indent | Honored (36pt) |
| Double spacing | Honored; measures 2.38 times the font size, which is how Docs defines double |
| Hanging indent on references | **Dropped**: both lines of each reference sit at 0.5 in. The normalizer would set it; not run live. |
| Page number | None; add by hand |

The normalizer was not run on this document: this session has Drive but no Docs editing tool. So there is no before and after for the normalizer on a real Doc. Account note: Drive reports the owner of the test docs (now six, "[polished-docs test] A" to "F") as another account; I did not share or delete them.

## Click cram sheet, rerun under the cram-sheet skill (2026-11-04)

The first Click sheet had 2 of 7 gotchas wrong from reading source. The second (run-or-tag rule) ran all 10. This third run (`tests/click/skill-v5/`, written by the new cram-sheet skill) ran all 8 of its gotchas, with one `[docs-only]` tag, 350 prose words, lint 97, one page, about 15% empty. I re-ran six of its claims myself (group option placement, a leading-dash argument, an empty environment variable, `multiple` defaults, case-insensitive `Choice`, value precedence) and all matched. Caveat: only released Click 8.5.0 could be run, while the checkout is 8.6.0.dev, so the sheet's Source line names 8.5.0 and nothing 8.6-only is on it.

The run's friction led to three fixes: the Source line names the version actually run; the builder reuses one `--tmpdir` folder instead of creating one per build; and the skill says a low `source_check` share is expected when software is verified by running.

Test suites after all changes: clean-docs 31, cram-sheet 8, polished-docs 58, all passing (without the PDF libraries, 18 render tests skip).

## Files

`tests/inputs/` inputs; `tests/general/<task>/{plain,skill}/` outputs and their PDFs (`*.default.pdf`, `*.polished.pdf`); `general-results.json`, `general-tables.md`, `general-questions.json`; `general_eval.py` to rerun; `trigger-*.json`; page images in `tests/general/`.
