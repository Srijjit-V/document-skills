import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from doc_lint import PROFILES, lint  # noqa: E402

SLOP = """# Overview

## Introduction

This robust library seamlessly leverages a multifaceted approach. It is important to note that it might work.

## Features

- **Fast**: very fast
- **Robust**: crucial
- **Seamless**: delve

## Conclusion

In summary, this robust library seamlessly leverages a multifaceted approach and it is important to note that it might work.
"""

CLEAN = """# fetchy

Download a URL with retries. Use it when a flaky endpoint must not fail your build.

```bash
fetchy https://example.com/file.tgz --retries 5
```

Retries back off exponentially from 1s and stop at 30s. A 4xx response is not retried because repeating a bad request cannot fix it.
"""


class LintTest(unittest.TestCase):
    def test_slop_fails(self):
        r = lint(SLOP)
        self.assertFalse(r["pass"])
        for cat in ("ai_word", "filler", "recap", "restate"):
            self.assertIn(cat, r["issues"])

    def test_clean_passes(self):
        r = lint(CLEAN, budget=200)
        self.assertTrue(r["pass"], r["issues"])

    def test_budget(self):
        r = lint(CLEAN, budget=10)
        self.assertIn("budget", r["issues"])
        self.assertFalse(r["pass"])

    def test_code_ignored(self):
        r = lint("Run it.\n\n```\n# leverage robust delve\n```\n")
        self.assertNotIn("ai_word", r["issues"])

    def test_bold_labels(self):
        r = lint("Text.\n\n- **A:** x\n- **B:** y\n- **C:** z\n")
        self.assertIn("bold_labels", r["issues"])

    def test_plain_words_ok(self):
        r = lint("You can pass a list. There is one default. It may raise ValueError.")
        self.assertEqual(r["issues"], {})

    def test_em_dash(self):
        r = lint("Fast — and cheap — and done.")
        self.assertEqual(r["issues"]["em_dash"][0]["count"], 2)


RESUME = """# Jordan Lee

## Experience

**Program Assistant**, Riverbend Library, 2022 to 2024
- Ran weekly story hour for 40 children
- Cut checkout wait times by 3 minutes
- Trained 6 volunteers on the catalog
- Organized 12 community events
- Managed a $2,000 supply budget
- Wrote the volunteer handbook

## Education

- B.A. English, State University, 2022
- Dean's list, four terms
"""

EMAIL = """Hi Priya,

I hope this email finds you well. The budget file is attached and the Friday review is moved to 2pm.

Thank you for your time and consideration.
"""


class Profiles(unittest.TestCase):
    def test_resume_bullets_ok_under_resume_profile(self):
        strict = lint(RESUME)
        ok = lint(RESUME, doc_type="resume")
        self.assertIn("bullet_ratio", strict["issues"])
        self.assertNotIn("bullet_ratio", ok["issues"])

    def test_type_sets_default_budget(self):
        r = lint("word " * 200, doc_type="email")
        self.assertEqual(r["budget"], 150)
        self.assertIn("budget", r["issues"])

    def test_email_opener_and_closer_flagged(self):
        r = lint(EMAIL, doc_type="email")
        self.assertIn("opener", r["issues"])
        self.assertIn("closer", r["issues"])

    def test_headings_flagged_in_email(self):
        r = lint("# Update\n\n## Status\n\nShort note here about the plan for Friday.\n", doc_type="email")
        self.assertIn("headers_in_short_form", r["issues"])

    def test_summary_at_top_is_not_a_recap(self):
        top = "## Summary\n\nThe pilot saves $1.45 per parcel.\n\n" + ("Detail sentence here. " * 30 + "\n\n") * 3
        self.assertNotIn("recap", lint(top)["issues"])

    def test_closing_summary_heading_is_a_recap(self):
        end = ("Detail sentence here. " * 30 + "\n\n") * 3 + "## Summary\n\nThat was it.\n"
        self.assertIn("recap", lint(end)["issues"])

    def test_conclusion_heading_allowed_in_lab_report(self):
        end = ("Detail sentence here. " * 30 + "\n\n") * 3 + "## Conclusion\n\ng is 9.7.\n"
        self.assertIn("recap", lint(end)["issues"])
        self.assertNotIn("recap", lint(end, doc_type="lab-report")["issues"])

    def test_rule_of_three_and_negative_parallelism(self):
        t = ("Our fast, simple, and reliable tool is not just a plugin, but a platform. "
             "It is bold, clear, and warm. We are calm, kind, and sharp. Fresh, quick, and neat.\n")
        r = lint(t)
        self.assertIn("rule_of_three", r["issues"])
        self.assertIn("negative_parallelism", r["issues"])

    def test_long_sentences_flagged(self):
        long = " ".join(["word"] * 30) + "."
        r = lint("\n\n".join([long] * 10) + "\n")
        self.assertIn("long_sentences", r["issues"])

    def test_unknown_type_raises(self):
        with self.assertRaises(ValueError):
            lint("x", doc_type="poem")

    def test_every_profile_has_required_keys(self):
        for name, p in PROFILES.items():
            self.assertIn("budget", p, name)
            self.assertGreater(p["budget"], 0)


class DocTypesTable(unittest.TestCase):
    """references/doc-types.md and the PROFILES budgets must agree."""

    def test_table_matches_profiles(self):
        path = os.path.join(os.path.dirname(__file__), "..", "references", "doc-types.md")
        if not os.path.exists(path):
            self.skipTest("doc-types.md not found")
        rows = {}
        for line in open(path, encoding="utf-8"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 4 and cells[0] in PROFILES:
                rows[cells[0]] = cells[2]
        self.assertEqual(sorted(rows), sorted(PROFILES), "every profile needs a row in doc-types.md")
        for name, budget in rows.items():
            self.assertTrue(budget.startswith(str(PROFILES[name]["budget"])), f"{name}: {budget} vs {PROFILES[name]['budget']}")


class FixedForms(unittest.TestCase):
    def test_memo_header_labels_and_table_totals_are_not_bold_overuse(self):
        memo = ("# Memo\n\n**TO:** Dana\n**FROM:** Sam\n**DATE:** Nov 4\n**SUBJECT:** Pilot\n\n---\n\n"
                + ("A plain sentence about the pilot here. " * 8 + "\n\n") * 3
                + "| Item | Cost |\n|---|---|\n| Van | 9,800 |\n| **Total** | **18,500** |\n")
        self.assertNotIn("bold", lint(memo, doc_type="memo")["issues"])

    def test_required_sections_do_not_trip_header_density_in_a_readme(self):
        para = "This sentence explains one useful point in plain words for the reader. " * 4
        text = f"# tool\n\n{para}\n\n## Install\n\n{para}\n\n## Usage\n\n{para}\n\n## Gotchas\n\n{para}\n"
        self.assertIn("header_density", lint(text)["issues"])
        self.assertNotIn("header_density", lint(text, doc_type="readme")["issues"])


if __name__ == "__main__":
    unittest.main()
