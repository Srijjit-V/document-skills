# AI-written documents beyond code: failures and standards
<!-- doc_lint: allow ai_word,filler -->

**Bottom line:** The evidence that AI text is padded, generic, and over-formatted holds outside software, but most of it is secondhand or vendor-adjacent. Hard format standards exist for APA, MLA, memos, letters, and resumes, and I verified the numbers below from the pages themselves. Rules for minutes, lab reports, study guides, policies, proposals, and newsletters come from no standard I could find; the skill treats them as design choices. Research date 2026-11-04. "Unverified" means I could not open the source.

## 1. How AI fails on non-technical documents

| Finding | Source | Status |
|---|---|---|
| "Workslop": AI work that looks good but lacks substance, passed to colleagues who redo it. The authors are at BetterUp and Stanford. | [HBR, 2025-09-22](https://hbr.org/2025/09/ai-generated-workslop-is-destroying-productivity) | Title, authors, date verified. The body is paywalled, so its survey numbers are **unverified**. |
| 40% of employees at 1,150 companies said they received workslop in the past month; memos padded with stock corporate phrasing | [Fortune, 2025-10-13](https://fortune.com/2025/10/13/workslop-wasting-workers-time-ai-resentment) | Secondhand report of the research; figures not checked against the HBR text |
| At least 13.5% of 2024 PubMed abstracts were processed with LLMs, found by excess style words such as "delves", "underscores", "showcasing" | [Kobak et al., Science Advances 2025](https://arxiv.org/abs/2406.07016) (arXiv title: "Delving into LLM-assisted writing in biomedical publications through excess vocabulary") | Verified. Note the arXiv title differs from the one in the brief. |
| LLM modification up to 17.5% in computer science papers and up to 6.3% in math and Nature portfolio papers, across 950,965 papers | [Liang et al. 2024](https://arxiv.org/abs/2404.01268) | Verified |
| Patterns listed: "stands/serves as", "is a testament/reminder", "setting the stage for", "evolving landscape". The page also warns these signs are weak evidence. | [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) | First 39k characters verbatim. Email and letter patterns ("I hope this helps", "I hope this message finds you well") are **summary-only**. |
| Recruiters spot generic, overly formal AI cover letters; use AI as a starting point only | [Harvard FAS career blog, 2026-08-10](https://careerservices.fas.harvard.edu/blog/2026/08/10/how-to-write-a-cover-letter-that-actually-gets-you-hired-in-2026/) | Fetched |
| Hiring manager asks people to stop sending AI cover letters; commenters call them lengthy, ornate, and easy to spot | [HN 37761045](https://news.ycombinator.com/item?id=37761045) | Thread fetched via API; the "70+ emails" detail is from a secondary page, unverified |
| A parent says a teen's formal writing took on ChatGPT's polite assistant tone | [HN 38800470](https://news.ycombinator.com/item?id=38800470) | Anecdote about tone, not padding |

Earlier causes still apply to every document type: length bias in preference training ([root-causes.md](root-causes.md)), guessing instead of abstaining, and no named reader.

**Not found in any source:** a measured rate of "wrong format for the document type" (a letter that reads like a blog post). That failure is in your brief; I treat it as an observation to test, not a statistic. The "82%" Medium claim has no source (see root-causes.md).

## 2. What good looks like, by document type

| Type | Verified rules | Source |
|---|---|---|
| Any | Put the main point first. BLUF comes from US Army Regulation 25-50, which requires the main point at the beginning and active voice. | [Wikipedia: BLUF](https://en.wikipedia.org/wiki/BLUF_(communication)) |
| Any | Paragraphs of 150 words or fewer, three to eight sentences, never over 250; one idea per sentence; active voice | [digital.gov plain language](https://digital.gov/guides/plain-language/writing/clear-short) |
| Any | Split sentences over 25 words; paragraphs of at most 5 sentences; avoid negative contractions; avoid "leverage", "robust", "in order to" (the word list is from a summary of the page) | [GOV.UK clear language](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/) |
| Narrative memo | Amazon writes "narratively structured six-page memos", no slides, read silently at the start of a meeting | [Amazon 2017 shareholder letter](https://www.aboutamazon.com/news/company-news/2017-letter-to-shareholders) |
| Email | Boomerang's analysis of 40 million emails found response rates above 50% for 50 to 125 words, peaking near 75 to 100 words | [Boomerang via search summary](https://blog.boomerangapp.com/?p=3933), secondhand; the original page would not load. Your "3 to 5 sentences" is **unverified**. |
| Memo | Usually a page or two, single spaced, left justified; skip a line between paragraphs. Header lines TO, FROM, DATE, SUBJECT. Opening is about a short paragraph. A summary only if longer than a page. | [Purdue OWL memo format](https://owl.purdue.edu/owl/subject_specific_writing/professional_technical_writing/memos/format.html), [parts](https://owl.purdue.edu/owl/subject_specific_writing/professional_technical_writing/memos/parts_of_a_memo.html) |
| Business letter | Block format: everything left justified and single spaced, with a blank line between paragraphs. The page gives no margin or font numbers. | [Purdue OWL basic business letters](https://owl.purdue.edu/owl/subject_specific_writing/professional_technical_writing/basic_business_letters/index.html) |
| Cover letter | One page, 250 to 400 words, three to four short paragraphs; skip "I am writing to express my interest in" | [Harvard FAS 2026](https://careerservices.fas.harvard.edu/blog/2026/08/10/how-to-write-a-cover-letter-that-actually-gets-you-hired-in-2026/) |
| Cover letter | One intro paragraph, one to three skills paragraphs, one closing paragraph; margins about 1 in (0.7 in at the least), single spaced, left aligned | [Purdue OWL](https://owl.purdue.edu/owl/job_search_writing/job_search_letters/cover_letters_1_quick_tips/quick_formatting_tips.html) |
| Resume | One page unless extensive experience; margins at least 0.5 in (0.75 in ideal); font no smaller than 10pt and do not shrink to fit; action verbs, no first-person pronouns, round bullets | [MIT CAPD](https://capd.mit.edu/resources/career-toolkit-crafting-an-effective-resume/), [MIT resumes](https://capd.mit.edu/resources/resumes/) |
| APA 7 student paper | 8.5 x 11 in, 1 in margins, double spaced throughout; fonts 12pt Times New Roman, 11pt Calibri or Arial, 11pt Georgia, 10pt Lucida Sans Unicode; page number flush right; reference list alphabetized with a 0.5 in hanging indent, double spaced | [Purdue OWL APA general format](https://owl.purdue.edu/owl/research_and_citation/apa_style/apa_formatting_and_style_guide/general_format.html), [reference list](https://owl.purdue.edu/owl/research_and_citation/apa_style/apa_formatting_and_style_guide/reference_list_basic_rules.html) |
| APA 7 headings | Level 1 centered, bold, title case; level 2 flush left, bold; level 3 flush left, bold italic; levels 4 and 5 run in | [Purdue OWL headings](https://owl.purdue.edu/owl/research_and_citation/apa_style/apa_formatting_and_style_guide/apa_headings_and_seriation.html) |
| APA paragraph indent | A new paragraph begins 1/2 inch in (inferred from a Purdue page about block quotes: "the same place you would begin a new paragraph") | [Purdue OWL](https://owl.purdue.edu/owl/research_and_citation/apa_style/apa_formatting_and_style_guide/in_text_citations_the_basics.html). The official apastyle.apa.org pages returned empty bodies, so APA's own wording is **unverified**. |
| MLA 9 | 12pt, double spaced, 1 in margins, 1/2 in paragraph indent; header with last name and page number 1/2 in from the top, flush right; name, instructor, course, and date block on page one; Works Cited with a 0.5 in hanging indent and no extra space between entries | [Purdue OWL MLA general](https://owl.purdue.edu/owl/research_and_citation/mla_style/mla_formatting_and_style_guide/mla_general_format.html), [Works Cited](https://owl.purdue.edu/owl/research_and_citation/mla_style/mla_formatting_and_style_guide/mla_works_cited_page_basic_format.html). The official style.mla.org pages gave no numbers. |

**No standard found:** meeting minutes, lab reports, study guides, policies and SOPs, proposals, newsletters. The structures in `clean-docs/references/doc-types.md` for these are my conventions, built from the rules above (answer first, one reader, short), and are untested against any external standard.

## 3. Access: what I could not open

| Source | Result on 2026-11-03 and 11-04 |
|---|---|
| Reddit (r/softwareengineer, r/ExperiencedDevs, r/googledocs) | Blocked in search and in the browser pane |
| X, LinkedIn | Both open in the browser pane but redirect to a sign-in page. I did not sign in. |
| Google "AI Overview" | Not fetchable; its text is as you supplied it |
| apastyle.apa.org, style.mla.org | APA pages empty, MLA pages teaser or 404; Purdue used instead |
| HBR article body, Nature | Paywall and login redirect |

## 4. Tools for general writing

| Tool | What it does | Source |
|---|---|---|
| Grammarly AI Detector | Estimates how much pasted text looks AI-written; the "99% accuracy" figure is a vendor claim | [grammarly.com](https://www.grammarly.com/ai-detector) |
| Hemingway Editor | "Make your writing correct and clear"; what it highlights is unverified | [hemingwayapp.com](https://hemingwayapp.com/) |
| Vale | Prose linter with YAML rules; runs offline and in CI; supports Markdown and Typst | [vale.sh](https://vale.sh/) |
| Pandoc, Typst | Conversion and typesetting; PDF from Markdown needs an engine | [pandoc.org](https://pandoc.org/), [typst.app](https://typst.app/) |
| Microsoft Editor | Grammar and clarity suggestions; sources unopened, **unverified** | |

**Gap (my assessment):** none of these enforce a length budget, source tracing, and numeric layout together. Detectors estimate whether text sounds like AI; they do not check that each fact traces to a source.
