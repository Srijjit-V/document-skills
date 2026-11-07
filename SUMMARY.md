# Three skills: the words, the page, the short version
Source: research/, tests/ · 2026-11-04
> **If you only read one thing:** AI documents fail on the reader, the facts, and the page. Name the reader and a length cap, trace every fact to a source you were given, and lay the page out with measured numbers (11pt, 135% leading, 45 to 90 characters a line).
Legend: ★ biggest effect · ⚠ caveat

## The skills
| Skill | Job |
|---|---|
| ★ clean-docs | Words for any document: reader card, budget, source tracing, lint |
| polished-docs | PDF and Google Doc layout; 7 presets |
| cram-sheet | 1 or 2 readable pages; ranks, cuts, never shrinks type |

## Why AI documents fail
| Cause | Evidence |
|---|---|
| ★ Raters prefer longer answers | [Singhal 23](https://arxiv.org/abs/2310.03716), [Dubois 24](https://arxiv.org/abs/2404.04475) |
| Guessing is rewarded | [Kalai 25](https://arxiv.org/abs/2509.04664) |
| At least 13.5% of 2024 PubMed abstracts show LLM style | [Kobak 25](https://arxiv.org/abs/2406.07016) |
| Recruiters spot generic AI letters | [Harvard FAS](https://careerservices.fas.harvard.edu/blog/2026/08/10/how-to-write-a-cover-letter-that-actually-gets-you-hired-in-2026/) |

## Content results (8 tasks)
| | Plain | Skills |
|---|---|---|
| Avg words | 525 | 441 |
| Avg lint | 89 | 100 |
| Reader Qs | 45/45 | 45/45 |
| Invented facts caught | 0 | 0 |

## Layout results (16 PDFs)
| | Default print | polished-docs |
|---|---|---|
| Layout score | 69 to 74 | 100 |
| Stranded headings | 4 | 0 |
| Pages (plain text) | 17 | 18 |

## Presets
- report, compact, book
- academic: APA/MLA basics, double spaced
- letter, memo, resume (1 page)

## Found by testing
- Bullets under a text line print as typed dashes
- Docs drops a negative `text-indent`, so no hanging indent from HTML
- Plain Claude's cram sheet kept 10pt and half the page empty
- Click gotchas: 2 of 7 wrong from reading; 8 of 8 run on the rerun

## Length by task (words)
| Task | Plain | Skills |
|---|---|---|
| Memo | 499 | 325 |
| Lab report | 1008 | 739 |
| Minutes | 544 | 404 |
| Proposal | 422 | 326 |
| Cover letter | 255 | 210 |
| Essay | 817 | 690 |

## How each works
- clean-docs: reader card, trace facts, draft, lint
- polished-docs: layout card, lint, build PDF or Doc, look at the pages
- cram-sheet: sheet card, rank, build, reader test

## What did not move
- Reader questions: 45 of 45 both ways
- Plain Opus stayed inside the sources when it was given them
- Answer-first tone and padding are where the skills differ

## Fixed after the runs
- Spelled-out numbers undercount tracing
- Header density vs required sections
- Conflicting notes need a decision, not a silent pick
- Tense errors need a re-read

## Gotchas
- ⚠ Normalizer ran on synthetic Docs JSON only
- ⚠ Thin or missing sources untested
- ⚠ Reddit blocked; X and LinkedIn need sign-in; HBR numbers paywalled
- ⚠ Trigger test is a proxy

## Files
- `clean-docs/`, `polished-docs/`, `cram-sheet/`
- `research/general-docs.md`
- `tests/general-results.md`

<!-- Cut to fit: per-task content and layout tables (tests/general-tables.md); keyword and competitor tables (research/market.md, research/layout-market.md); the root-cause table (research/root-causes.md); skill-run fix list (tests/general-results.md). -->
