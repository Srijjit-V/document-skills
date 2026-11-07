# Document skills for Claude Code

Three independent Claude Code skills that make AI-written documents clean, readable and properly formatted.

| Skill | Job |
|---|---|
| [clean-docs](clean-docs/) | The words: one reader, a length budget, facts traced to your sources, no AI filler. Includes `doc_lint.py` and `source_check.py`. |
| [polished-docs](polished-docs/) | The layout, as a PDF and as a Google Doc. Seven presets: report, compact, book, academic, letter, memo, resume. |
| [cram-sheet](cram-sheet/) | One or two readable pages. Ranks facts, cuts instead of shrinking type (8pt floor). |

## Install

Copy the folders you want into `~/.claude/skills/`:

```bash
cp -R clean-docs polished-docs cram-sheet ~/.claude/skills/
```

Scripts need Python 3. PDF building and layout checks also need Chrome or Chromium, and the `markdown` and `pdfplumber` packages.

## Results

See [SUMMARY.md](SUMMARY.md) for the one-page overview and [tests/general-results.md](tests/general-results.md) for the eight-task comparison against plain Claude. Research with sources is in [research/](research/).

## Known limits

- `gdoc_normalize.py` was only run on synthetic Google Docs JSON, not on a live Doc.
- Thin or missing sources were not tested.
- The trigger test is a proxy, not real usage.
- Some sites (Reddit, X, LinkedIn, HBR) could not be read; claims from them are labeled unverified.

## License

MIT, see [LICENSE](LICENSE).
