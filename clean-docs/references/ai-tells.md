# AI tells and what to write instead
<!-- doc_lint: allow ai_word,filler,hedge,recap -->

Based on [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) plus doc-specific padding. `doc_lint.py` flags most of these. Fix the sentence, not just the word: usually the whole clause can go.

| Pattern | Example | Write instead |
|---|---|---|
| Inflated vocabulary | delve, tapestry, multifaceted, landscape, pivotal, realm, intricate | the plain word, or cut it |
| Promo adjectives | robust, seamless, powerful, comprehensive, cutting-edge, effortless | a measurable fact: "retries 3× with backoff" |
| Corporate verbs | leverage, utilize, empower, streamline, harness, elevate | use, let, speed up |
| Copula avoidance | "serves as", "stands as", "boasts", "features" | "is", "has" |
| Significance claims | "plays a crucial role", "a testament to", "pivotal moment" | say what it does |
| Negative parallelism | "It's not just X, it's Y" | "It does X and Y" |
| Rule of three | "fast, reliable, and scalable" | only the adjectives you can back up |
| Throat-clearing | "It is important to note that", "Note that", "In order to" | delete; start with the fact |
| Meta-narration | "This guide will walk you through", "Let's dive in" | delete; start with step 1 |
| Hedges on verified facts | might, may, typically, generally, should work | state it, or mark `[unverified]` |
| Recap ending | "In summary", "In conclusion", "Overall," | delete the section |
| Chat leftovers | "I hope this helps", "Feel free to", "Let me know" | delete |
| Em-dash chains | "fast — and cheap — and done" | commas, colons, or two sentences |
| Bold labels on every bullet | `- **Speed:** very fast` | a table, or plain bullets |
| Title Case Headings | "## Getting Started With The API" | "## Call the API" |
| Emoji headers | "## 🚀 Features" | "## Features" |
| Generic section set | Overview / Features / Installation / Usage / Contributing / License, every time | only sections this reader needs |
| Placeholder text | `[Describe X here]`, `example.com/source1`, `2025-XX-XX` | real value or cut |
| Email pleasantry opener | "I hope this email finds you well" | start with the ask or the news |
| Cover-letter opener | "I am writing to express my interest in..." | the role and one specific reason ([Harvard FAS](https://careerservices.fas.harvard.edu/blog/2026/08/10/how-to-write-a-cover-letter-that-actually-gets-you-hired-in-2026/)) |
| Generic closer | "Thank you for your time and consideration", "Please do not hesitate to contact me" | the next step and a date |
| Essay opener | "In this essay, I will discuss..." | the thesis itself |
| Essay filler transition | "Furthermore", "Moreover", "In today's world" | cut, or a real connective ("because", "so") |
| Section-ending summary | "Despite these challenges...", "In conclusion" | end on a fact or the next step |
| Invented specifics | an achievement, quote, or statistic the sources never gave | leave it out, or `[needs: ...]` |
| Stock corporate phrasing | "leverage synergies", "moving forward", "circle back" | the plain action |

The email and letter openers and closers are listed on the Wikipedia page, but I read that part from a summary and not the page text. Treat them as patterns to check, not proof. Wikipedia itself warns the signs are weak evidence.
