---
name: cram-sheet
description: Fit a topic onto one or two readable pages: study sheet, cram sheet, cheat sheet, exam review, one-pager, quick reference, meeting prep sheet, process or policy summary, "the short version", "fit this on one page". Works for any subject (a chapter, a policy, a process, a role, a library). Ranks facts by how often they are needed, cuts instead of shrinking type (8pt floor), reports what was cut, and checks every claim against the material you gave. Use whenever someone wants to review, memorize, or hand off a condensed version of notes, a textbook chapter, a report, a procedure, or code docs, even if they never say "cram sheet".
---

# cram-sheet

A page packed with tiny type is not condensed, it is unread. When AI fits too much on a page it shrinks the font and drops the structure. This skill picks what earns a place, cuts the rest, and tells you what it cut. Method and sources: `references/cram-method.md`.

`<skill>` means the folder this SKILL.md is in. Scripts need Python 3; the PDF and screenshot checks also need Chrome or Chromium.

Related skills: clean-docs writes full documents (reader, budget, source tracing). polished-docs lays out regular documents as PDF or Google Doc. This skill condenses.

## Step 1: Write the sheet card

Write these lines into your working notes. They don't go in the sheet.

```
Subject:   what the sheet covers, and what it does not
Reader:    who uses it (a student before Friday's exam, a new hire, you at your desk)
Moment:    how they use it (5-second glance, or 20-minute review)
Material:  the notes, chapter, policy, or files you were given
Budget:    1 page by default; 2 only if asked
```

The moment decides the shape. A glance sheet needs one-line facts and a top line. A review sheet can hold worked examples. If the person gave no reader, pick the likeliest and say so in one line when you deliver.

## Step 2: Ground every line in the material

Every fact, number, date, formula, name, and quote comes from the material you were given, or is tagged `[unverified]`. Never fill a gap from memory and present it as theirs. Never invent a formula, a citation, or an exam date. If the material is silent, leave the line out.

For behavior claims about software or a process ("this flag does X", "step 3 fails if Y"), run it or find a test that shows it; otherwise tag `⚠?`. Reading is not checking. If the version you can run differs from the source you read (8.5.0 installed, 8.6.0.dev checked out), put the version you ran on the Source line and keep to behavior you observed.

## Step 3: Rank, fill, cut

1. List every candidate fact as one line.
2. Score each: how often the reader needs it, times how costly a miss is. For study material, use how likely it is to be tested times how hard it is to recall. Without usage data, estimate from the material's own emphasis (headings, repetition, "remember", worked examples).
3. Fill boxes from the top of the ranking until the page is full: about 350 to 550 words per page (fewer when it has code or tables). 5 to 9 boxes per page, 3 to 7 lines per box. Label boxes by task or concept, not "Overview". The first box is what the reader needs first.
4. Match the form to the content: terms as a two-column table, steps as a numbered list, comparisons as a table, formulas in code font, dates as a short list. One line per fact; a real example beats a sentence about it.
5. Always include a top line ("If you only read one thing: ..."), and a box of common mistakes, exceptions, or gotchas, each with a short "because". A wrong gotcha is worse than none: check it or drop it.
6. If it doesn't fit, cut the lowest-ranked lines. Never shrink type: body 8.5pt, floor 8pt. Record each cut in a "Cut to fit" list. If the material runs out before the page is full, leave the page short and say so. Don't pad.

## Step 4: Build and look

```bash
python3 <skill>/scripts/cram_to_html.py sheet.md --pages 1 --pdf --screenshot
```

Exit 1 means over budget: cut and rebuild. Then open the screenshot, because a page count cannot see text spilling out of a cell, a command wrapped mid-word, or a third of the page left empty. If more than a fifth is empty and cut lines remain, add back the best of them. If the material is exhausted, a shorter page is fine. The word range is a cap, not a target. Keep code lines under about 30 characters and keep long identifiers out of narrow table cells. The PDF and PNG go to a temp folder (pass `--tmpdir DIR` to choose it). Deliver the .md and .html unless a PDF was asked for.

The input format is in `references/cram-method.md`.

## Step 5: Check before handing over

```bash
python3 <skill>/scripts/doc_lint.py sheet.md --mode cram --budget 550
python3 <skill>/scripts/source_check.py sheet.md notes.md      # numbers, names, quotes not in the material
```

1. Lint passes (score 80 or more).
2. Reader test: write the 5 questions the reader will ask first. Each must be answerable from the sheet in seconds.
3. Trace: every untraced number or name from `source_check.py` is either computed (say so) or removed. An untraced quote is always removed. For a software sheet verified by running, there is no notes file: pass the docs you read. A low traced share is expected there, because the evidence is your run log, not a source text.

## Step 6: Deliver

At most 5 lines: the reader and budget you assumed; the page count; anything tagged `[unverified]`; the "Cut to fit" list, so they can ask for any of it back. Keep that list in an HTML comment at the end of the .md as well.
