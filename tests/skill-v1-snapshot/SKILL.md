---
name: clean-docs
description: Write documentation people can read: READMEs, API references, how-to guides, runbooks, ADRs, bug reports/tickets, onboarding docs, and one-page cram sheets / cheat sheets. Plans the reader and a word budget first, verifies claims against the code, and lints the result for padding, AI vocabulary, and over-formatting. Use this whenever the user asks to write, document, explain, summarize into, or clean up any technical doc, README, docstring page, wiki page, ticket, postmortem, or cheat sheet, or says docs are "too long", "AI-sounding", "slop", or "unreadable", even if they don't name the skill. Also use for "cram sheet", "cheat sheet", "one-pager", "quick reference", or "fit this on one page".
---

# clean-docs

AI-written docs fail in predictable ways. They are long because training rewarded length. They are shapeless because no reader was specified. They are wrong at the edges because nobody ran the code. They are over-formatted because chat habits leak into the doc. This skill counters each one with a step you can check. Background and sources: `references/rules.md`.

Pick a mode:
- Mode A, standard doc: any doc a person reads to do a task.
- Mode B, cram sheet: "cheat sheet", "cram sheet", "one-pager", "quick reference", "fit on one page". Default budget is 1 page; 2 pages if asked.

## Step 1: Write the reader card (both modes)

Before drafting, write these five lines into your working notes. They don't go in the doc.

```
Reader:   who opens this (role + experience), e.g. "backend dev new to this repo, knows Python"
Task:     the one thing they're trying to get done when they open it
Knows:    what you may skip explaining (their language, git, HTTP…)
Doesn't:  what they lack and you must supply (project-specific setup, the non-obvious traps)
Budget:   word cap from the table in references/templates.md (cram: pages)
```

Every paragraph has to help that reader with that task. If the user gave no audience, choose the most likely one from context, state it in one line when you deliver, and keep going. Without a named reader, the model weights everything equally and the doc grows padding. Without a budget, nothing pushes back on length.

## Step 2: Gather ground truth

Read in this order, and stop once you can answer the reader's task: entry points and CLI/API surface → config and env vars → tests (they show real usage and edge cases) → error handling and raised exceptions → existing docs, changelog, issues. On large repos, read selectively and record `file:line` for each fact. Models lose facts buried in long contexts, so a pointer beats memory.

Run the install and the example commands when it's safe and cheap (no network side effects, no secrets). A command you ran is verified. One you didn't run gets `[unverified]` next to it. Never invent flags, defaults, file paths, or version numbers. If a fact is unknown, write that it's unknown or leave it out.

## Step 3: Draft

### Mode A rules (each traces to a source in references/rules.md)
1. **Lead with the answer.** The first one or two sentences say what this is and why the reader should care, or the fix and when to apply it. Not `This document describes…`.
2. **Write the non-obvious; skip what the code already says.** Cover why it exists, limits, defaults that surprise, ordering constraints, and failure modes. Don't restate signatures or explain what `npm install` does.
3. **One doc, one job.** Tutorial, how-to, reference, or explanation (Diátaxis). Link out for the rest.
4. **Formatting has to earn its place:**
   - Headers only when the doc runs past about a screen (~300 words), and no more than one per ~80–150 words. Sentence case, key word first.
   - Bullets only for 3+ parallel items. Numbered lists only for ordered steps. Nest at most one level.
   - Tables to compare things on 2+ attributes (options, flags, env vars, error codes).
   - Bold sparingly, for a scan keyword. Never `**Label:**` on every bullet.
   - Plain prose for reasoning. A paragraph of three sentences is fine.
5. **Real examples.** Copy-pasteable, complete enough to run, with realistic values, and the expected output when it helps. One good example beats three partial ones.
6. **Conditions before instructions:** "If you use Docker, run X", not "Run X if you use Docker". Use second person, active voice, imperative for steps.
7. **Plain words.** No AI vocabulary or filler (list in `references/ai-tells.md`). No hedging on facts you verified. No em dashes; use a comma, colon, or new sentence.
8. **No recap at the end.** End on the last useful fact, a "Next" link, or the gotchas. Never `In summary`.

Use the matching template in `references/templates.md` (README, API reference, how-to, runbook, ADR, bug report/ticket, onboarding). Templates are maximums: drop any section that would be empty or obvious.

### Mode B: cram sheet
Read `references/cram-sheet.md` for the format, then:
1. List every candidate fact as one line. Rank by how often the reader needs it × how bad it is to get wrong.
2. Fill boxes in rank order until the budget is reached (about 450–550 words per page in 3 columns at 8.5pt). Use 3–7 lines per box and 4–9 boxes per page.
3. Always include: a top line "If you only read one thing: …", a Gotchas box, and a legend if you use symbols.
4. If it doesn't fit, cut content, never font size. Body text stays at 8.5pt (minimum 8pt). Record each cut in a "Cut to fit" list for the user.
5. Build and check:
   ```bash
   python3 <skill>/scripts/cram_to_html.py sheet.md --pages 1 --pdf
   ```
   Exit 1 means over budget. Cut the lowest-ranked lines and rebuild.

## Step 4: Self-check before handing over

1. Lint, and fix until it passes:
   ```bash
   python3 <skill>/scripts/doc_lint.py doc.md --budget N            # Mode A
   python3 <skill>/scripts/doc_lint.py sheet.md --budget N --mode cram
   ```
   It checks the word budget, AI vocabulary, filler, hedges, em dashes, header density, bullet ratio, bold overuse, deep nesting, recap endings, and paragraphs that restate earlier ones. A score under 80 or a blown budget fails. Read each flag and fix the sentence; don't swap in a synonym to dodge the list. If a flag is a false positive (a style guide that has to quote `leverage`), add `<!-- doc_lint: allow ai_word -->` and say why.
2. Reader test. Write the 5 questions the reader from Step 1 would ask first. For each, confirm the doc answers it and that the answer can be found in seconds (in the first lines of a section, or a table row). Fix what fails.
3. Truth pass. Every command, flag, path, and default either matches the code you read or is marked `[unverified]`.

## Step 5: Deliver

Give the user the file(s) and a short note, at most 5 lines:
- the reader and budget you assumed, and the final word count and lint score
- anything marked `[unverified]`
- for cram sheets: the page count and the "Cut to fit" list (what was dropped and why), so they can ask for any of it back

Don't paste the whole doc into chat when it's saved to a file.
