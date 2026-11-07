# Cram sheet method

A cram sheet is a reference card: condensed notes in columns, split into labeled boxes, one fact per line ([Wikipedia: Reference card](https://en.wikipedia.org/wiki/Reference_card)). It works when it covers the common cases of a narrow subject. It fails when it shrinks a full reference into tiny type.

## Capacity (US Letter, 3 columns, 8.5pt body, 0.4 in margins)
| Budget | Words | Boxes | Lines per box |
|---|---|---|---|
| 1 page | about 350 to 550 (tables and code run low) | 5 to 9 | 3 to 7 |
| 2 pages | about 900 to 1100 | 10 to 16 | 3 to 7 |

Trust the PDF page count from `cram_to_html.py --pdf`, not the word estimate. Three to five items per box matches working memory, which holds about four chunks ([Cowan 2001](https://www.cambridge.org/core/journals/behavioral-and-brain-sciences/article/magical-number-4-in-shortterm-memory-a-reconsideration-of-mental-storage-capacity/44023F1147D4A1D44BDC0AD226838496)).

## Ranking: what earns a line
Score each candidate fact: need (1 to 3: rare, weekly, daily; or for study material, unlikely, likely, certain to be tested) times cost of a miss (1 to 3: minor, annoying, serious; or for study material, easy to recall, harder, easy to confuse). Fill from the top. Ties go to the fact that is hardest to find in the source. Anything that did not fit goes in the Cut to fit list.

## Rules
1. Top line: `> **If you only read one thing:** ...`. The one fact that prevents the most pain or unlocks the most.
2. Boxes are labeled by task or concept ("Key terms", "Steps", "Compare", "Formulas"), not "Overview". The most used box goes first.
3. One line per fact. Terms as `term | meaning` tables; steps as a numbered list; comparisons as a table with 2 or 3 columns.
4. Examples over prose. A worked number beats a sentence about it.
5. A box of common mistakes, exceptions, or gotchas is required, each with a short "because". A sheet with answers but no reasons teaches memorizing the wrong thing; people who only copy a cheat sheet's commands without understanding them get stuck ([HN 9913617](https://news.ycombinator.com/item?id=9913617)). Every item must be checked against the material (or run, for software); otherwise tag it `⚠?` or drop it.
6. Cover common cases, not the full reference, and keep the scope narrow ([HN 9829104](https://news.ycombinator.com/item?id=9829104), [HN 9953968](https://news.ycombinator.com/item?id=9953968)).
7. Symbols: at most 3, defined in a `Legend:` line. Suggested: ★ most important, ⚠ mistake or danger, → leads to.
8. No font shrinking: body 8.5pt, floor 8pt. Over budget means cut lines.
9. Put the source and date in the `Source:` line so the reader knows when the sheet goes stale.

## Form by content
| Content | Form |
|---|---|
| Vocabulary, definitions | Two-column table, term first |
| A process | Numbered list, one action per line, the check after the step |
| Two or three things compared | Table with the same attributes per row |
| Formulas | Code font, one per line, with units; a worked example below |
| Dates and sequences | Short list, earliest first |
| Rules with exceptions | Rule line, then "Except:" line |
| Code or commands | `code` plus 3 to 8 words, under about 30 characters per column |

## Markdown format (input to cram_to_html.py)
A non-code example. The same format works for commands and settings.

```markdown
# Water cycle: exam review
Source: Ch. 7 notes, 2026-11-04
> **If you only read one thing:** water moves in a loop, and the sun drives every step.
Legend: ★ likely on the exam · ⚠ common mistake

## Key terms ★
| Term | Meaning |
|---|---|
| Evaporation | liquid water to vapor, driven by solar heat |
| Condensation | vapor to droplets, on cooling |
| Watershed | land that drains to one outlet |

## Steps
1. Sun heats surface water
2. Vapor rises and cools
3. Droplets form clouds
4. Precipitation falls; runoff or infiltration

## Common mistakes
- ⚠ Evaporation needs heat, not boiling: it happens at any temperature, because surface molecules escape.

<!-- Cut to fit: groundwater zones (rare; in notes p. 4); history of the term (not testable) -->
```

`## ` headings become boxes; titles with "mistake", "gotcha", "trap", or "exception" render in the red box.

## Build and check
```bash
python3 scripts/cram_to_html.py sheet.md --pages 1 --pdf --screenshot   # sheet.html here; PDF + PNG in a temp dir; exit 1 if over
python3 scripts/doc_lint.py sheet.md --mode cram --budget 550
python3 scripts/source_check.py sheet.md notes.md
```

## Cut report (give this to the user)
```
Cut to fit (1 page):
- <fact>: rare (appears once in the notes); in notes p. 4
- <fact>: duplicate of the Steps box
```
