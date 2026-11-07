# Layout market: what people search, what breaks, what exists

**Bottom line:** People keep building Markdown-to-Docs and Markdown-to-PDF converters, which shows demand. Direct complaints about AI documents looking wrong are thin outside vendor blogs. No tool found checks layout against numeric rules, and none chains a content cleaner with a layout step. Evidence is Hacker News, vendor blogs, and official docs; Reddit, X, and LinkedIn were unreachable.

## Phrases and intent
| Phrase | Intent | Evidence |
|---|---|---|
| markdown to google docs | Convert | 108 HN story hits, many in the reverse direction (Docs to Markdown); a Markdown-to-Docs tool in [48601134](https://news.ycombinator.com/item?id=48601134) |
| paste chatgpt into google docs | Fix breakage | [unmarkdown posts](https://unmarkdown.com/blog/why-chatgpt-output-looks-terrible-when-you-paste-it) |
| chatgpt to pdf | Export | [HN 46970531](https://news.ycombinator.com/item?id=46970531) |
| markdown to pdf pandoc typst | Build | [HN 49576203](https://news.ycombinator.com/item?id=49576203), [47083014](https://news.ycombinator.com/item?id=47083014) |
| does google docs support markdown | Permission | [Docs Help](https://support.google.com/docs/answer/12014036) |
| why does ai make documentation so bad reddit | Complaint | Unverified: Reddit blocked |

## Recurring problems (ranked by distinct sources seen)
| # | Problem | Sources |
|---|---|---|
| 1 | Literal `#`, `**`, and pipes after paste | [unmarkdown 1](https://unmarkdown.com/blog/5-things-that-break-when-you-paste-ai-output), [2](https://unmarkdown.com/blog/why-chatgpt-output-looks-terrible-when-you-paste-it), [3](https://unmarkdown.com/blog/markdown-to-google-docs) (one vendor, three posts) |
| 2 | Tables collapse to pipe characters | [unmarkdown](https://unmarkdown.com/blog/how-to-paste-chatgpt-tables-into-google-docs), [Docs Help gap](https://support.google.com/docs/answer/12014036) |
| 3 | Agents write Markdown, coworkers need Google Docs | [HN 48601134](https://news.ycombinator.com/item?id=48601134), [HN 47393964](https://news.ycombinator.com/item?id=47393964) |
| 4 | HTML-to-PDF breaks pagination and tables (claim by a competitor) | [HN 46307205](https://news.ycombinator.com/item?id=46307205) |
| 5 | LLM Markdown has broken nested lists and overflowing tables | [HN 46307205](https://news.ycombinator.com/item?id=46307205) |
| 6 | Default Pandoc/LaTeX output looks dated, with wide margins and code running off the page | [neilzone.co.uk](https://neilzone.co.uk/2025/01/using-pandoc-and-typst-to-convert-markdown-into-custom-formatted-pdfs-with-a-sample-template/) |

Not found in any source I could read: blank-line spacing, tab indents, typed bullets, bold-as-heading, headings stranded at page bottom. Those are in your brief and in Butterick's rules, so they stay in the skill as checks, but I have no outside complaint count for them.

## Existing tools
| Tool | What it does | Layout rules checked? | Chains content cleaning? |
|---|---|---|---|
| Docs native Markdown | Import, export, optional paste conversion ([Docs Help](https://support.google.com/docs/answer/12014036)) | No | No |
| Unmarkdown | Copy as formatted rich text for Docs ([blog](https://unmarkdown.com/blog)) | No | No |
| markdown-to-google-docs MCP | Creates Docs from Markdown ([HN](https://news.ycombinator.com/item?id=48601134)) | No | No |
| Pandoc | Universal converter; PDF via other engines ([pandoc.org](https://pandoc.org/)) | Template-dependent | No |
| Typst | Typesetting system, not Markdown-native ([typst.app](https://typst.app/docs/)) | Template-dependent | No |
| MDXport | Markdown to PDF via Typst; heuristics for LLM Markdown ([HN](https://news.ycombinator.com/item?id=46307205)) | Heuristics, no numeric score | No |

**Gap:** A numeric layout lint (body size, leading, characters per line, stranded headings) for Markdown, PDF, and Docs, plus a hand-off from a content skill. In this search the converters I found create documents; none repaired styles in a Doc that already exists. I did not search exhaustively, so treat that as "not found", not "does not exist".

## Addendum for non-code documents (2026-11-04)

Tools for general writing (Grammarly, Hemingway, Vale, Microsoft Editor) and the evidence on AI cover letters, memos, and essays are in [general-docs.md](general-docs.md). The gap is the same: none of them enforces a length budget, source tracing, and numeric layout together, and none produces the right form for the document type (a block letter whose address lines stay on separate lines, a double-spaced paper with a hanging reference list). In testing, the browser-default print of a plain Markdown letter ran its address blocks together on one line, which is the failure that preset prevents.
