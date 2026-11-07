---
name: clean-docs
description: Write or rewrite any document so a real reader can use it: emails, memos, reports, essays, cover letters, resumes, proposals, meeting minutes, lab reports, study guides, policies, newsletters, READMEs, and technical docs. Fixes the words: one reader and one purpose, a length budget, every fact traced to the sources you gave, no AI filler or padding. Use whenever someone asks to write, draft, rewrite, tighten, summarize, shorten, proofread, or "clean up" a document, says text sounds like AI or is too long, wordy, generic, or padded, or asks for help with their report, paper, essay, email, letter, resume, notes, or README, even if they never name the skill. For layout as a PDF or Google Doc use polished-docs; for a one-page condensed version use cram-sheet.
---

# clean-docs
<!-- doc_lint: allow filler,rule_of_three -->

AI-written documents fail in predictable ways. They are long because training rewarded length. They are generic because no reader was named. They state things the sources never said because guessing is rewarded. They are over-formatted because chat habits leak into the page. This skill counters each with a step you can check. Background and sources: `references/rules.md` and `research/general-docs.md`.

`<skill>` means the folder this SKILL.md is in. The scripts need Python 3.

## Step 1: Write the reader and purpose card

Write these lines into your working notes. They don't go in the document.

```
Type:     one row from references/doc-types.md
Reader:   who opens this, what they already know
Purpose:  what they should know, decide, or do after reading
Lacks:    what they don't have that you must supply
Sources:  every file, note, link, transcript, or data the person gave you
Budget:   the word cap in doc-types.md, or the person's own limit (theirs wins)
```

Every paragraph must help that reader reach that purpose. If the person named no reader, choose the likeliest, say so in one line when you deliver, and keep going. Without a named reader the model weights everything equally and the document grows padding. Without a budget nothing pushes back on length.

## Step 2: Ground every fact in the sources

The sources are what the person gave you: notes, data, a job posting, a transcript, a repo. Read them fully before drafting. Then:

- Every fact, number, date, name, quote, and citation traces to a source, or is tagged `[unverified]`.
- Never invent a citation, a quote, a statistic, an achievement, or a date. If the person gave no sources for a claim, leave the claim out or write it as their own statement without a citation.
- If a needed fact is missing, leave a visible placeholder such as `[needs: due date]` and list the placeholders when you deliver. A placeholder is honest; a guess is not.
- Computed values (totals, averages, a calculated result) are fine. Show the calculation or say "computed from the table".
- Say what you do not know. "The transcript does not say who approves this" beats a confident invention.
- When two notes conflict (cancel the contract, but keep one region on it), state the conflict and who must decide. Don't resolve it silently.
- Don't claim what the sources contradict or leave out. If a gap matters to the reader (a posting asks for staff management and the person has none), state it in one sentence or leave the claim out. Never imply the opposite.
- Reasoning beyond the sources is fine in an argument when it reads as the author's reasoning ("this suggests"), not as a finding from a source.
- The writer's own name and contact details, and today's date, may come from the request. Everything else traces to the sources.
- Computed values are fine: show the inputs next to the number ("38% of 212 households, about 81"). `source_check` lists them as untraced; that is expected.

For code, a repo, or any process you can run: run it. Each fact gets one of four levels:
- Ran it: no tag needed.
- Read in source or config: no tag; add a `file:line` only where it points the reader somewhere useful, and re-check it, since line numbers drift.
- Stated in the project's docs but not run: tag `[docs only]` and name the file.
- Neither: tag `[unverified]` or leave it out.

Behavior claims ("X is parsed as Y", "this fails silently") need a run or a test. Reading control-flow code is easy to get wrong: one Click sheet claimed `-dbg` splits into `-d -b -g`, and a run showed otherwise. If you can only run a different version than the one you read, say so. A missing claim costs less than a wrong one.

## Step 3: Draft

1. Answer first. The opening sentence or two gives the answer, the ask, the decision, or the thesis, in the form listed for the type in `references/doc-types.md`. No "This document describes...", no "I hope this finds you well", no "I am writing to express my interest".
2. One idea per paragraph, one idea per sentence. Split sentences over 25 words. Use the active voice and the reader's words. Paragraphs of 150 words or fewer.
3. Say the specific thing. Prefer the number, name, or example from the sources to the adjective. Cut what the reader already knows. Keep what they would otherwise have to ask: the reason, the limit, the exception, the deadline.
4. Formatting earns its place. Headings only when the document is long enough to navigate (about 300 words or more) and fixed forms (memo, report, lab report) need them. Bullets for 3 or more parallel items; numbers only for ordered steps; a table to compare on 2 or more attributes. Bold sparingly. Plain prose for reasoning.
5. Plain words. No AI vocabulary or filler (`references/ai-tells.md`). No hedging on facts you verified. No em dashes. Avoid reflexive lists of three (three adjectives, three abstractions) and "not just X, but Y". A list of three real things from the sources is fine.
6. End on the last useful thing: the next step, the deadline, the ask. No recap.
7. Write plain Markdown. Layout is polished-docs' job. For letters, memos, and resumes, use the shapes in `references/doc-types.md` so the layout step can recognize them.

## Step 4: Check before handing over

```bash
python3 <skill>/scripts/doc_lint.py doc.md --type email                  # type: see doc-types.md; sets the budget
python3 <skill>/scripts/doc_lint.py doc.md --type essay --budget 800    # when the person gave a limit, pass it
python3 <skill>/scripts/source_check.py doc.md notes.md data.csv         # every source file you were given
```

Call the scripts by their full path from any folder, and quote paths that contain spaces. The linter enforces a maximum; if the person gave a minimum ("600 to 800 words"), count that yourself.

1. Lint passes (score 80 or more, within the budget). The linter flags padding, AI vocabulary, filler openers and closers, hedges, em dashes, lists of three, "not just X, but Y", long sentences, header density, bullet ratio, bold overuse, recap endings, and repeated paragraphs. Fix the sentence, not just the word. A false positive (a style guide that has to quote "leverage") can be allowed with `<!-- doc_lint: allow ai_word -->`.
2. Trace. `source_check.py` lists every number, name, quote, and citation not found in the sources. Computed numbers are fine. Anything else is removed or tagged. If the sources spell numbers out in words (a transcript), it warns that the traced share undercounts; check those numbers by hand. An untraced quote or citation is always removed. It is a text match: it cannot tell that a matched number is attached to the right claim, so re-read the facts yourself.
3. Reader test. Write the 5 questions the reader will ask first. Each must be answered in the document, and findable in seconds. Then re-read for tense and attribution (who did what, and when): neither tool can catch "I do this work" for a job that ended.
4. For software: every command and flag matches what you ran or read, and every behavior claim was run or is tagged.

## Hand-offs

- Layout (PDF, Google Doc, "make this look professional", "format my paper", stray `#` after a paste): polished-docs, after the text passes lint.
- A one-page or two-page condensed version ("study sheet", "cheat sheet", "the short version"): cram-sheet.

## Step 5: Deliver

Five short lines at most (the file path does not count): the reader, purpose, and budget you assumed; the final word count and lint score; placeholders and `[unverified]` items; anything you could not check. Don't paste the whole document into chat when it is saved to a file.
