# Templates by doc type

Each template sets a maximum, not a checklist. Drop a section if it would be empty, obvious, or a restatement. Budgets are starting points; raise them only for real complexity and say so.

| Type | Reader's task | Budget (words) | Diátaxis |
|---|---|---|---|
| README | Decide if this is for me, then run it | 250–600 | mix: tutorial + pointers |
| API reference (per module/endpoint) | Look up exact behavior | 80–200 per item | reference |
| How-to guide | Get one goal done | 200–600 | how-to |
| Runbook | Fix the incident now, under stress | 150–500 | how-to |
| ADR | Understand why we chose X | 250–600 | explanation |
| Bug report / ticket | Reproduce and fix | 60–200 | n/a |
| Onboarding | Be productive in week one | 400–1000 | tutorial + map |

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

## Day 1: run it
1. Clone, install, run, test (exact commands, verified).
## How a request flows
Short prose or one diagram, with file:line entry points.
## Conventions that aren't obvious
Table: rule | why.
## Where to ask / who owns what
```
