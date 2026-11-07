# Document types: budget, opener, structure

Each entry sets a maximum, not a checklist. Drop any section that would be empty or obvious. Budgets are starting points that `doc_lint.py --type` enforces; raise one only for real complexity and say so. If the person gave a length ("one page", "500 words", "five paragraphs"), that limit wins.

Sourced rules are marked with a link. Everything else is a convention of this skill, not an external standard, and has not been checked against one (see `research/general-docs.md`).

| Type | Reader's job | Budget (words) | Opener and shape |
|---|---|---|---|
| email | Act on one ask | 150 | Sentence 1 is the ask or the news. Boomerang's data peaks near 75 to 100 words ([secondhand](https://blog.boomerangapp.com/?p=3933)). No headings, one thank-you at most. |
| memo | Decide | 600 | BLUF: purpose and recommendation in the first paragraph ([BLUF](https://en.wikipedia.org/wiki/BLUF_(communication))). Header lines TO, FROM, DATE, SUBJECT; a page or two ([Purdue](https://owl.purdue.edu/owl/subject_specific_writing/professional_technical_writing/memos/format.html)). |
| report | Understand findings and act | 1500 | Answer first: what you found and what to do. Then findings, method, appendix. |
| essay | Follow an argument | 1200 | Thesis in the first paragraph, not "In this essay". One claim and its evidence per paragraph. The last paragraph adds a consequence, not a recap. Cite only provided sources. The person's word limit wins over 1200: pass it as `--budget`. |
| cover-letter | Decide to interview | 400 | Role plus one specific reason in the first sentence; 3 to 4 short paragraphs; 250 to 400 words ([Harvard FAS](https://careerservices.fas.harvard.edu/blog/2026/08/10/how-to-write-a-cover-letter-that-actually-gets-you-hired-in-2026/)). Skip "I am writing to express my interest". Use only facts the person gave. |
| resume | Screen quickly | 550 | One page; bullets start with an action verb, no first-person pronouns, no full sentences ([MIT CAPD](https://capd.mit.edu/resources/career-toolkit-crafting-an-effective-resume/)). Numbers only if given. |
| proposal | Approve funding or a plan | 1200 | Problem and ask (amount, date) in the first paragraph. Then need, plan, timeline, budget table (totals must add up), risks, how success is measured. |
| minutes | Know what was decided and who owns what | 500 | Date, attendees, then Decisions (with votes), Actions (owner and due date), short Discussion, Next meeting. Facts from the transcript only. Mark garbled or unresolved items in plain words ("proposed, not voted on", "[unclear]"). Leave out "prepared by" and approval status unless given. Bold labels are fine here, as in resumes and study guides. |
| lab-report | Reproduce and judge the result | 1200 | Title, Purpose, Method, Data (table with units), Analysis (show the calculation), Results, Sources of error, Conclusion. Every computed value shows its formula. |
| study-guide | Learn and self-test | 900 | A scope line (what it covers, the exam date if given), Key terms, Concepts with one example each, Practice questions with answers from the notes, Common mistakes. Label any made-up practice numbers as made up. |
| policy | Know what they must do | 800 | Purpose, Scope, Rules (use "must", "can", "must not" consistently, as [GOV.UK](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/) does), Responsibilities, Exceptions, Owner and effective date. |
| newsletter | Skim for what matters to them | 500 | Most important item first; 3 to 5 items, each: what, why it matters, what to do, date. |
| readme | Decide if this is for me, then run it | 600 | What it does and for whom, install, smallest working example, gotchas. Add a line for where output goes (stdout or stderr) and the exit codes when the tool sets them. |
| api-reference | Look up exact behavior | 1200 per file (80 to 200 per item) | One entry per item: what it does, parameters that surprise, returns and raises. |
| runbook | Fix the incident now, under stress | 500 | Symptom, impact, diagnose, mitigate, fix, escalate. Copy-pasteable commands. |
| adr | Understand why we chose X | 600 | Decision in one sentence, context, options with for and against, consequences. |

Also supported: how-to guide (200 to 600), bug report or ticket (60 to 200), onboarding (400 to 1000). Their templates are at the end of this file.

## Plain-language rules that apply to every type
- Paragraphs of 150 words or fewer; one idea per sentence; active voice ([digital.gov](https://digital.gov/guides/plain-language/writing/clear-short)).
- Split sentences over 25 words; no more than 5 sentences per paragraph ([GOV.UK](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/)).
- Use "buy", "help", "about" instead of "purchase", "assist", "approximately" (GOV.UK, same page).

## Markdown shapes that polished-docs expects
Write plain Markdown. Layout is polished-docs' job. For documents with a fixed form, use these shapes so the layout step can recognize them. A single newline inside a block is kept as a line break.

Letter (cover letter or business letter), blocks separated by blank lines. Put the writer's phone and email in the sender block once; don't repeat them in the closing unless the ask needs them:
```markdown
Jordan Lee
12 Elm Street
Riverbend, WA 98000

November 4, 2026

Ms. Dana Whitfield
Riverbend Public Library

Dear Ms. Whitfield,

First paragraph.

Second paragraph.

Sincerely,
Jordan Lee
```

Memo: a title, four header lines, a rule, then the body.
```markdown
# Memo

**TO:** Dana Whitfield, VP Operations
**FROM:** Sam Okafor
**DATE:** November 4, 2026
**SUBJECT:** Pilot a new shipping carrier

---

Recommendation first.
```

Resume: name as the title, one contact line, `##` for sections, bullets for entries.
```markdown
# Jordan Lee
Riverbend, WA · jordan@example.com · 555-0100

## Experience
**Program Assistant**, Riverbend Library, 2022 to 2024
- Ran weekly story hour for 40 children
```

Academic essay (APA or MLA style): `# Title`, body paragraphs, then `## References` or `## Works Cited` with one reference per paragraph.

## Templates for technical documents
Each template sets a maximum, not a checklist.

## README
```markdown
# name

One sentence: what it does and for whom. One sentence: why use it over the obvious alternative (only if true).

```bash
install command
smallest real usage that shows the point
```
Expected output, if it helps.

## Usage            <- only if there's more than the quickstart
Common tasks as short examples; a table for flags/options/env vars.

## Gotchas          <- only from evidence: tests, issues, error handling
- The non-obvious thing that bites people, and what to do.

## Develop          <- only if outside contributors are expected
test/build commands.

License: X. Links: docs, changelog.
```
Leave out: badges walls, "Features" lists that repeat the intro, Table of contents for <600 words, "Contributing" boilerplate, closing summary.

## API reference (one entry)
```markdown
### `name(arg1, arg2=default) -> ReturnType`
One line: what it does, in terms of the caller's goal.

| Param | Type | Default | Notes |
|---|---|---|---|
| arg2 | int | 3 | Only the non-obvious: units, ranges, what 0 means |

Returns / raises: only what the signature doesn't say (when it raises, what None means).
```python
smallest realistic call
```
```
Leave out: restating the param name as its description ("url: the URL").

## How-to guide
```markdown
# Verb the goal  (e.g. "Rotate the API key")
When to use this, prerequisites in one line.

1. Imperative step. `command`
2. If <condition>, do X; otherwise Y.
3. ...

Check it worked: `command` → expected output.
If it fails: the 1–3 known failure modes and fixes.
```

## Runbook
```markdown
# Alert/symptom name
**Impact:** who is affected. **Severity:** guide. **Owner:** team/channel.

## Diagnose
1. `command` → what healthy vs broken looks like.
## Mitigate (stop the bleeding)
1. Safe, reversible step first.
## Fix
1. ...
## Escalate if
- condition → who.
```
Copy-pasteable commands with no placeholders left unfilled. Most likely cause first.

## ADR
```markdown
# ADR-NNN: Decision as a sentence  (Status: accepted, YYYY-MM-DD)
**Decision:** one sentence.
**Context:** the forces: constraints, numbers, deadlines.
**Options considered:**
| Option | For | Against |
**Consequences:** what gets easier, what gets harder, what we must now watch.
```

## Bug report / ticket
```markdown
**Summary:** one line: component, what breaks, when.
**Steps to reproduce:**
1. ...
**Expected:** ...   **Actual:** ... (exact error text)
**Environment:** version, OS, config that matters.
**Notes:** suspected cause with file:line, if known. Workaround, if any.
```
A few sentences, not an investigation log. Attach logs, don't paste 1,500 lines.

## Onboarding
```markdown
# Start here: <project>
What the system does in two sentences, and a 5–8 line map: directory → what lives there.

## Use it
User install line, the 2–4 calls/commands people need most, and the gotchas that bite users.
## Day 1: change it
1. Clone, dev install, run, test (exact commands, verified).
## How a request flows
Short prose or one diagram, with file:line entry points.
## Conventions that aren't obvious
Table: rule | why.
## Where to ask / who owns what   <- only if you found it (CODEOWNERS, CONTRIBUTING, chat link)
```
