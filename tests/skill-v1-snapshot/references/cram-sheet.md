# Cram sheet method

A cram sheet is a reference card: condensed notes in columns, split into labeled boxes, one fact per line ([Wikipedia: Reference card](https://en.wikipedia.org/wiki/Reference_card)). It works when it covers common cases for a narrow task. It fails when it shrinks a full reference into tiny type.

## Capacity (US Letter, 3 columns, 8.5pt, 0.4in margins)
| Budget | Words (prose + code) | Boxes | Lines per box |
|---|---|---|---|
| 1 page | ~450–550 | 5–9 | 3–7 |
| 2 pages | ~900–1100 | 10–16 | 3–7 |

Tables and code use more height per word than prose. Trust the PDF page count from `cram_to_html.py --pdf`, not the word estimate.

## Ranking: what earns a line
Score each candidate fact: **frequency** (1–3: rare, weekly, daily) × **cost of getting it wrong** (1–3). Fill boxes from the top of the ranking down. Ties go to the fact the code or docs make hardest to find. Anything that didn't fit goes in the **Cut to fit** list.

## Rules
1. Top line: `> **If you only read one thing:** …`. This is the single fact that prevents the most pain or unlocks the most use.
2. Boxes are labeled by task ("Install", "Daily commands", "Config", "Debug"), not by abstraction ("Overview"). Put the most used box first.
3. One line per fact. Commands as `code` plus a description of 3–8 words. Use 2–3 column tables for options, flags, and mappings.
4. Examples over prose. A real command beats a sentence about the command.
5. Gotchas box is required. Fill it from tests, issues, and error handling, each with its fix. If there's no evidence, write fewer gotchas, not invented ones.
6. Symbols: use at most 3, defined in a `Legend:` line. Suggested: ★ most used, ⚠ gotcha/danger, → leads to/returns.
7. Chunking: 3–7 lines per box. If a box runs longer, split it or cut it.
8. No font shrinking. Body text stays at 8.5pt (8pt floor). Over budget → cut the lowest-ranked lines.
9. One "why" per trap. A sheet without reasons teaches cargo-culting. Give gotchas a short "because".
10. Footer-free. Put the source and version in the `Source:` line so the reader knows when the sheet goes stale.

## Markdown format (input to cram_to_html.py)
```markdown
# tool-name cram sheet
Source: repo@v1.2.3 · 2026-11-02
> **If you only read one thing:** run `x --dry-run` before `x apply`; apply is not reversible.
Legend: ★ most used · ⚠ gotcha

## Daily commands
| Command | Does |
|---|---|
| `x init` ★ | create config in ./x.toml |

## Gotchas
- ⚠ `--force` skips the lock: two runs corrupt state. Never in CI.

<!-- Cut to fit: (list for the user, not rendered) -->
```

## Build
```bash
python3 scripts/cram_to_html.py sheet.md --pages 1 --pdf   # writes sheet.html + sheet.pdf, exit 1 if over
python3 scripts/doc_lint.py sheet.md --mode cram --budget 550
```

## Cut report (give this to the user)
```
Cut to fit (1 page):
- <fact>: rare (used at setup only); in README §Config
- <fact>: duplicate of the X box
```
