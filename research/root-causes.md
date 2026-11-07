# Why AI-generated docs read badly: root causes
<!-- doc_lint: allow ai_word,filler,recap -->

**Bottom line:** AI docs are long because training rewarded length. They are shapeless because the model has no reader in mind. They are wrong at the edges because the model never ran the code. Prompting fixes part of this; the rest needs a written process and a lint check. Each cause below maps to a rule in `clean-docs/SKILL.md` (listed as **Rule**).

Research date: 2026-11-02. "Unverified" means I could not open the source myself.

## A. Causes inside the model

### 1. Length bias from preference tuning
- What: Models learn from ratings, and both human and AI raters prefer longer answers. The model learns that "longer" scores as "better", whatever the content.
- Evidence:
  - Singhal et al., *A Long Way to Go* (COLM 2024): a reward based only on length reproduces most of RLHF's measured gains, and reward models correlate strongly with length. [arXiv:2310.03716](https://arxiv.org/abs/2310.03716)
  - Saito et al., *Verbosity Bias in Preference Labeling by LLMs* (NeurIPS 2023 workshop): GPT-4 as a judge prefers longer answers more than humans do. [arXiv:2310.10076](https://arxiv.org/abs/2310.10076)
  - Park et al., *Disentangling Length from Quality in DPO* (2024): unregularized DPO drives output far past the length of the training data. Controlling for length raised win rates by up to 20%. [arXiv:2403.19159](https://arxiv.org/abs/2403.19159)
  - Dubois et al., *Length-Controlled AlpacaEval* (2024): the leading automatic benchmark favored verbose models. Removing the length effect raised its correlation with Chatbot Arena from 0.94 to 0.98. [arXiv:2404.04475](https://arxiv.org/abs/2404.04475)
- In plain words: A rater sees two answers. The longer one looks more thorough, so it wins. Repeat that millions of times and the model learns to pad. It adds an intro, restates the question, covers every case at equal depth, and closes with a recap. Benchmarks graded by other LLMs reward the same thing, so the habit is never punished.
- In a doc: A 1,500-word README for a 200-line tool. Three intro paragraphs before the install command.
- Rule: Set a word budget before writing (Step 1). Run `doc_lint.py` to check the budget.

### 2. Chat-tuning format habits leak into docs
- What: Chat models are tuned to look organized on screen, with headers, bullets, bold, and a summary at the end. In a doc, that structure is noise.
- Evidence:
  - Anthropic's own prompting guide says markdown in the prompt raises markdown in the output. Its suggested fix is to ask for "smoothly flowing prose paragraphs" and avoid bold and bullets unless a list is needed. [platform.claude.com best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
  - Wikipedia's *Signs of AI writing* page lists these as tells: leftover Markdown (its top item), overused bold, bolded inline labels in lists, title-case headings, section-ending summaries, and em-dash overuse. [Wikipedia](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
- In a doc: A `##` header over every two sentences. `**Note:**` on every bullet. Bullets nested three levels deep. An "In summary" section.
- Rule: Formatting rules F1–F6. The linter checks header density, bullet ratio, bold count, and recap phrases.

### 3. Stock "AI voice": vocabulary, hedges, and significance claims
- What: Some words and patterns are statistically overused by tuned models.
- Evidence: The Wikipedia page lists "delve", "pivotal", "tapestry", "underscore", copula avoidance ("serves as", "boasts"), negative parallelism ("not just X, it's Y"), the rule of three, inflated significance ("stands as a testament"), and pleasantries ("I hope this helps"). [Wikipedia](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing). The page itself warns these are weak signals, not proof.
- In a doc: "This robust library seamlessly leverages a multifaceted approach…"
- Rule: The banned word list in `references/ai-tells.md`. The linter flags them.

### 4. Confident guessing instead of "I don't know"
- What: Training and evaluation reward guessing over admitting uncertainty, so the model fills gaps with plausible inventions.
- Evidence:
  - Kalai et al. (OpenAI), *Why Language Models Hallucinate* (2025): accuracy-only grading gives zero points for abstaining, so models learn to guess. [arXiv:2509.04664](https://arxiv.org/abs/2509.04664)
  - Spracklen et al. (USENIX Security 2025): code models invent package names in at least 5.2% of samples for commercial models and 21.7% for open-source models. [arXiv:2406.10279](https://arxiv.org/abs/2406.10279)
- In a doc: A flag that does not exist. A README pointing to a `docs/` folder that is not in the repo ([HN example](https://news.ycombinator.com/item?id=46286298)).
- Rule: Verify every claim against the code (Step 3). Mark anything unchecked `[unverified]`.

### 5. Context limits and context rot
- What: On a large codebase the model reads less reliably. Facts in the middle of a long context get lost, so it fills gaps from priors.
- Evidence:
  - Liu et al., *Lost in the Middle* (TACL 2023): accuracy is highest when the relevant information is at the start or end of the context and drops when it is in the middle. [arXiv:2307.03172](https://arxiv.org/abs/2307.03172)
  - Chroma, *Context Rot* (2025): across 18 models, output grows less reliable as input length grows, even on simple tasks. [trychroma.com](https://www.trychroma.com/research/context-rot)
- In a doc: Generic docs that fit any project. APIs that sound right but don't match the code.
- Rule: Read the entry points and tests first, then cite `file:line` for each claim (Step 3).

## B. Causes in how people use it

### 6. No model of the reader
- What: Nobody tells the model who will read the doc, what they already know, or what they are trying to do. So it covers everything at equal weight.
- Evidence:
  - Ferri-Benedetti, *What's wrong with AI-generated docs* (2025-04-01): LLMs lack the strategy, context, and judgment that information architecture needs. They miss caveats and "what not to do". The page shows no byline; [I'd Rather Be Writing](https://idratherbewriting.com/blog/whats-wrong-ai-webinar-recording) attributes it to him. [passo.uno](https://passo.uno/whats-wrong-ai-generated-docs/)
  - HackerNoon, *The Problem With Autogenerated Docs* (2026): names three failure modes, the Over-Explainer, the Repeater, and False Completeness. Its cause is that the model has no picture of the reader. [hackernoon](https://hackernoon.com/the-problem-with-autogenerated-docs)
  - Anthropic's `doc-coauthoring` skill starts by asking "Who's the primary audience?" [GitHub](https://github.com/anthropics/skills/blob/main/skills/doc-coauthoring/SKILL.md)
- In a doc: It explains what `npm install` does, then skips the one environment variable that breaks prod.
- Rule: Step 1, the reader card: who reads it, their task, what they already know, and the budget. Each paragraph must serve that task.

### 7. No ground truth
- What: The model documents what the code *looks* like it does. It has not run it, hit the errors, or seen the bug reports.
- Evidence: Ferri-Benedetti (above) says LLM docs miss "product truth". Codegen argues naive docstrings are vague filler and need call-graph context ([codegen.com](https://codegen.com/your-ai-is-writing-bad-docs-because-it-lacks-context/), vendor blog). On HN: fact-checking AI docs takes hours while generating them took minutes ([item 48842468](https://news.ycombinator.com/item?id=48842468)).
- In a doc: It describes the happy path in detail and leaves out timeouts, retries, and limits.
- Rule: Run the examples where possible. Mine tests, error handling, and issues for gotchas. Add a "Gotchas" section only from evidence.

### 8. One-line prompts
- What: A prompt like "document this codebase" gives the model no audience, length, outline, or style target.
- Evidence:
  - Tix (2024): one-page docs drafted after the AI asked follow-up questions were preferred over docs from the request alone. [arXiv:2407.12017](https://arxiv.org/abs/2407.12017)
  - Requirements-engineering case study: quality of LLM output depends heavily on the input given. [arXiv:2507.19113](https://arxiv.org/abs/2507.19113)
- In a doc: Generic structure (Overview / Features / Installation / Usage / Contributing / License) whatever the project.
- Rule: The skill writes its own brief (Step 1) and picks a template by doc type.

### 9. No one reads before shipping
- What: Writing is now cheap, so review cost moves to the reader.
- Evidence: On HN, people refuse to review large unreviewed AI docs ([49018235](https://news.ycombinator.com/item?id=49018235)) and stop reading at the first sign of AI text ([50251392](https://news.ycombinator.com/item?id=50251392)).
- Rule: Self-check: run the linter and answer 5 reader questions from the doc before handing it over.

## Your starting evidence, checked

| # | Claim | Status |
|---|---|---|
| 1 | r/softwareengineer "AI is terrible for making documentation" and its quotes | **Unverified.** Reddit is blocked to my search and browser. Not quoted in the skill. The same complaints appear on HN (see market.md). |
| 2 | r/ExperiencedDevs threads (Oct 2026) | **Unverified**, same reason. |
| 3 | passo.uno, Apr 2025 | **Verified.** Dated 2025-04-01. Author attributed by a second source. |
| 4 | Codegen blog | **Verified.** Vendor post, updated 2025-07-17. |
| 5 | Zeroheight, "Why AI shouldn't write your design system docs" | **Not found.** A similar title, "Why you shouldn't rely on AI to write your documentation" (Feb/Mar 2025), appears in listings, but I could not open it. |
| 6 | Medium, "82% of AI docs confuse users" | **No source.** The post cites "15,000+ pages" with no study, author, or method behind it. **Do not use.** [medium](https://medium.com/ai-tomorrow/stop-using-ai-for-documentation-heres-why-82-confuses-users-more-and-the-user-first-method-d496bd8f0194) |
| 7 | LinkedIn, Shumin Chen | **Unverified.** Not found. |
| 8 | Han Wang (Mintlify), Fortune | **Partly verified.** No Fortune piece found. Agents-as-readers is Mintlify's public thesis ([a16z podcast](https://a16z.com/podcast/how-mintlify-is-rebuilding-documentation-for-coding-agents/)). |
| 9 | Scott Abel quote | **Unverified.** Closest match is a paywalled Content Wrangler post ([link](https://www.thecontentwrangler.com/p/how-technical-writers-can-make-ai)). |
| 10 | DEV, "Will AI kill documentation and blogs?" | **Verified.** Posted 2025-05-17. Argues AI complements docs and needs human review. [dev.to](https://dev.to/nooxs/does-ai-kill-documentation-and-articles-4deh) |
| 11 | "30% rule of AI" | **No standard meaning.** Vendor blogs use it as a loose automate-30%/keep-70% heuristic, and none name an origin ([example](https://gravity.fast/blog/what-is-the-30-percent-rule-in-ai/)). Not used. |
