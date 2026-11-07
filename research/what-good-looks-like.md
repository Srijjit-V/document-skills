# What good docs do: testable rules

**Bottom line:** Readers scan, so put the answer first, front-load every line, cut words, and match the doc to one reader task. Every rule below can be checked, either by a linter or by a yes/no question.

## Evidence on how people read

| Finding | Source |
|---|---|
| 79% of test users scanned; 16% read word by word (1997) | [NN/g, How Users Read on the Web](https://www.nngroup.com/articles/how-users-read-on-the-web/) |
| Measured usability rose 58% with concise text, 47% with scannable text, 27% with objective text, and 124% with all three | [NN/g, Concise, Scannable, Objective](https://www.nngroup.com/articles/concise-scannable-and-objective-how-to-write-for-the-web/) |
| Eyes follow an F shape: they read the first lines, then only the left edge, so the first words of headings carry the page | [NN/g, F-shaped pattern](https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/) |
| Inverted pyramid: put the most important point first in the doc, in each paragraph, and in each sentence | [NN/g, Inverted pyramid](https://www.nngroup.com/articles/inverted-pyramid/) |
| BLUF ("bottom line up front") comes from US Army Regulation 25-50: put the main point at the start | [Wikipedia, BLUF](https://en.wikipedia.org/wiki/BLUF_(communication)) |
| Working memory holds about 4 chunks (range 3–5) | [Cowan 2001, BBS](https://www.cambridge.org/core/journals/behavioral-and-brain-sciences/article/magical-number-4-in-shortterm-memory-a-reconsideration-of-mental-storage-capacity/44023F1147D4A1D44BDC0AD226838496) |

## Rules

### Structure
| # | Rule | Test | Source |
|---|---|---|---|
| S1 | Each doc is one type: tutorial, how-to, reference, or explanation. Don't mix them. | Can you name the type in one word? | [Diátaxis](https://diataxis.fr/start-here/) |
| S2 | A how-to guide assumes a competent reader with a real goal. Steps only; link out for theory. | Does any step teach theory? | Diátaxis |
| S3 | Reference mirrors the structure of the code and stays neutral. | Does the order match the code's own grouping? | Diátaxis |
| S4 | The first sentence or two answer "what is this, and should I care". | Read only line 1: does it answer that? | NN/g inverted pyramid; [HN wish](https://news.ycombinator.com/item?id=48079874) |
| S5 | Headers exist for navigation. Use them only when a doc is longer than about one screen (~300 words). | Fewer than 1 header per ~150 words | NN/g (meaningful subheadings); Wikipedia AI tells |
| S6 | Headers are descriptive, in sentence case, with key words first. | No title case, no "Overview" or "Introduction" | [Google style](https://developers.google.com/style/highlights), [Microsoft style](https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice), NN/g F-pattern |

### Sentences
| # | Rule | Test | Source |
|---|---|---|---|
| W1 | Front-load: the key word comes in the first few words of each paragraph and list item. | First 5 words carry the topic | Microsoft top-10; [Write the Docs](https://www.writethedocs.org/guide/writing/docs-principles/) |
| W2 | Second person, active voice, imperative for steps. | No "the user should" | Google style |
| W3 | Put conditions before instructions ("If X, run Y"). | No "Run Y if X" | Google style |
| W4 | Cut `you can` and `there is/are`. | grep | Microsoft top-10 |
| W5 | Objective, not promotional: no `powerful`, `seamless`, `robust`. | Linter word list | NN/g objective (+27%) |
| W6 | Aim for half the words of a normal draft. | Word count ≤ budget | NN/g concise (+58%) |

### Content
| # | Rule | Test | Source |
|---|---|---|---|
| C1 | Explain why and what is not obvious. Skip what the code or its name already says. | Does any sentence just restate a signature? | [HN](https://news.ycombinator.com/item?id=49708862); passo.uno |
| C2 | Give real, runnable, copy-pasteable examples for common use cases, not every case. | Does each example run? | Write the Docs ("Exemplary"); [Stripe teardown](https://www.moesif.com/blog/best-practices/api-product-management/the-stripe-developer-experience-and-docs-teardown/); [Go by Example](https://gobyexample.com/) |
| C3 | Wrong docs are worse than no docs. Verify each claim, or mark it. | Does every claim have a `file:line` or `[unverified]`? | Write the Docs |
| C4 | Some repetition is fine when it saves a jump ("ARID"), but don't restate a paragraph. | Linter: near-duplicate paragraphs | Write the Docs |
| C5 | Include caveats, limits, and "don't do this". | Is there a gotchas section, backed by evidence? | passo.uno |
| C6 | Link text says where the link goes. | No "click here" or "this page" | Google, Write the Docs, NN/g |

### Formatting
| # | Rule | Test | Source |
|---|---|---|---|
| F1 | Use bullets only for parallel items (3+ of the same kind). Use numbers only for steps in order. | Bullet lines under 40% of prose docs | NN/g; Anthropic prompting guide |
| F2 | Use tables to compare items on 2+ attributes. | Is there a comparison written as prose or bullets? | Diátaxis reference; devhints |
| F3 | Bold is for scanning keywords, not decoration. At most ~1 bold per 100 words. | Linter | NN/g ("highlighted keywords"); Wikipedia AI tells (overused bold) |
| F4 | No closing recap (`In summary`, `In conclusion`). | Linter | Wikipedia AI tells |
| F5 | No emoji headers, no em-dash chains. | Linter | Wikipedia AI tells |
| F6 | Nest bullets at most one level. | Linter | Readability; Wikipedia AI tells |

## Docs people praise: the patterns

| Doc | What it does | Rule it shows |
|---|---|---|
| Stripe API | Three columns: navigation, prose, and runnable code in your language with your test key | C2 |
| Go by Example | One topic per page, full runnable program, short notes beside the code | C2, S1 |
| devhints.io / quickref | Section headings, two-column Expression/Description tables, one-line entries | F2, cram sheet |
| Diátaxis sites (Canonical, Django) | Pages split by type | S1 |

## Docs that agents read (llms.txt)
- `/llms.txt` was proposed by Jeremy Howard (Answer.AI) in Sept 2024. It is a markdown file with an H1 name, a blockquote summary, then H2 lists of `- [name](url): note`, with an "Optional" section for secondary links. [llmstxt.org](https://llmstxt.org/)
- What helps agents is the same as what helps humans: a one-line summary first, a flat structure, explicit names and links. Mintlify says agents are now a large share of doc traffic ([a16z](https://a16z.com/podcast/how-mintlify-is-rebuilding-documentation-for-coding-agents/)). The rules above serve both readers.

## Cheat sheets (for Cram Sheet mode)
| Rule | Source |
|---|---|
| A reference card is condensed notes in one or more columns, split by topic, with term → description → usage entries | [Wikipedia, Reference card](https://en.wikipedia.org/wiki/Reference_card) |
| Cover common use cases, not the full reference | [HN 9829104](https://news.ycombinator.com/item?id=9829104) |
| Narrow scope (one task or tool) beats broad scope | [HN 9953968](https://news.ycombinator.com/item?id=9953968) |
| A sheet without the reasoning gets people through tasks without understanding, so add one "why" line for traps | [HN 9913617](https://news.ycombinator.com/item?id=9913617) |
| Use Expression/Description tables and one-line comments | [devhints.io/bash](https://devhints.io/bash) |
| 3–5 items per group fits working memory; ~7 is the upper limit | Cowan 2001 |
| A one-page limit forces you to prioritize; multi-page "cheat sheets" turn into notes | [chatslide guide](https://www.chatslide.ai/guides/cheat-sheet-maker-create-study-guides) (secondary) |
