# Test results: plain Claude vs clean-docs

**Bottom line:** With the skill, docs were 55% shorter (2,166 → 983 words on average), lint scores rose from 71 to 100, and the reader-test answers sat 2–4× closer to the top of the doc. Cheat sheets went from 12 of 15 questions answered to 15 of 15, all on one page. Plain Claude's cheat sheets were already decent; most of the gain is in the long docs.

## Setup
- Repos (shallow clones, 2026-11-02): [pallets/itsdangerous](https://github.com/pallets/itsdangerous) @672971d (1.2k lines), [httpie/cli](https://github.com/httpie/cli) @5b604c3 (9.8k), [scrapy/scrapy](https://github.com/scrapy/scrapy) @e397746 (37.9k).
- Same prompt for every run ("docs.md a new developer would use, plus a one-page cheatsheet.md/.html"). Baseline = Opus 5.5 subagent, no skill. Skill runs read `clean-docs/SKILL.md` first.
- `skill-v1` = first draft (snapshot in `skill-v1-snapshot/`). `skill-v2` = after fixes from the v1 runs.
- Everything is scored with the final linter (`evaluate.py`), so the columns compare like with like.
- Reader test: 5 new-developer questions per repo (`questions.json`). "Words to answer" counts the words a reader passes before the first text that answers the question. **This measures position, not timed human reading**, and the regex answer keys can miss a valid answer phrased differently. I checked every miss by hand and fixed 3 keys that were too strict; the fixes apply to all runs.

## Averages
| | Baseline | Skill v1 | Skill v2 |
|---|---|---|---|
| docs.md words | 2,166 | 847 | 983 |
| docs.md lint | 71 | 100 | 100 |
| docs.md questions answered | 13/15 | 13/15 | 14/15 |
| docs.md median words to answer (itsd. / httpie / scrapy) | 194 / 998 / 313 | 92 / 411 / 243 | 76 / 224 / 149 |
| Cheat sheet questions answered | 12/15 | 12/15 | 15/15 |
| Cheat sheet pages | 1, 1, 1 | 1, 1, 1 | 1, 1, 1 |

Per-run detail: `results-table.md`, raw numbers in `results.json`.

## What failed in v1 and what changed
| v1 failure (seen in) | Fix in v2/v3 |
|---|---|
| The user install line was dropped because the reader card said "knows Python" (itsdangerous, httpie) | Rule 1: install + smallest example within the first ~150 words |
| Cheat sheets skipped `startproject` | The first box must cover getting started |
| The linter punished plain words ("you can", "may") and forced awkward rewrites (all 3) | Removed them from filler/hedges; the budget now counts prose only, not code |
| Bold labels on every bullet passed the lint (httpie) | New `bold_labels` check in standard mode |
| Cheat sheet passed the page count but overflowed cells, and banner code was unreadable (all 3) | Wrapping CSS, readable banner code, `--screenshot`, and a skill step to look at it |
| `Content-*` rendered as italics | Removed single-asterisk italics |
| No guidance when nothing can run | Three verification levels; one top-line note when nothing runs |
| "Docs for a new developer" fit no template | Onboarding = "Use it" + "Change it" halves |
| Build artifacts overwrote each other, and a stray PDF was left in the output | PDF and PNG go to a temp dir (`--tmpdir`) |

v2 runs still reported: tables are too narrow for long keys (now: keys over ~18 characters go in lists), the screenshot didn't show full page height (now drawn at 11in), and the lint output showed total words next to a prose budget (now prints both). These v3 fixes were checked by rebuilding sheets, not by a third round of runs.

## Ground-truth findings
Skill runs installed and ran the code. These findings came from running it, and I grep-checked that the baseline docs don't contain them:
- itsdangerous: `max_age` passed to a non-timed serializer is silently ignored (`serializer.py:328`). The repo's own `docs/serializer.rst` shows `dumps` returning bytes, but it returns `str`.
- scrapy: in a generated project, `-o` onto an existing file logs an error and the items are lost.
- httpie: piped stdin plus `key=value` items fails with "cannot be mixed". The baseline mentions `--ignore-stdin` only as a fix for cron jobs hanging.

The baseline docs already covered some gotchas well: project-template settings that differ from library defaults (scrapy), and the `BadPayload` exception hierarchy (itsdangerous). The skill's gain is mostly length, structure, and findability. The new facts are a smaller, real bonus.

## Not measured
Factual accuracy of the baseline docs (no line-by-line audit), timed human reading, and v3 as a full rerun.

## Click rerun with the run-or-tag rule (2026-11-03)

The first Click sheet (`tests/click/skill-v3/`) listed seven gotchas after reading source only. Running them on released Click 8.5.0 showed: three correct, one misleading (`-dbg` works as one option when declared), one wrong (`multiple=True, default="ab"` fails with "Value must be an iterable"), two only in the docs. The sheet was corrected.

A fresh run with the updated skill (`tests/click/skill-v4/`) produced ten gotchas. The agent reported running every one; I re-ran eight of them independently on 8.5.0 and all matched. One line was tagged `[docs only]`, and three claims were dropped rather than guessed. Caveats: Click 8.5.0 is the only version that could be run, while the checkout is 8.6.0.dev, so the sheet says "behavior run on 8.5.0". Installing the checkout was blocked, so the released package from PyPI was used.

Skill changes from this run: a `[docs only]` tag, a rule for version gaps, and a note on `--tmpdir`.
