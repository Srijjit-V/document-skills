import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from layout_lint import lint_md  # noqa: E402

BAD = """# TITLE OF THE DOC

# Second h1

#### skipped to h4


**Not a heading:**
Text with  a double space.

•  typed bullet
 One space indent paragraph.

&nbsp;

Next.
"""

GOOD = """# Guide

Install with `pip install x` and run `x --help`.

## Steps

1. First
2. Second

```
code  with  spaces
    and indent
```

| a   | b |
|-----|---|
| 1   | 2 |
"""


class MdLint(unittest.TestCase):
    def test_bad_hits_every_check(self):
        r = lint_md(BAD)
        for cat in ("stacked_blank_lines", "all_caps_heading", "multiple_h1", "skipped_heading_level",
                    "bold_fake_heading", "double_space", "typed_marker", "typed_indent", "stacked_headings"):
            self.assertIn(cat, r["issues"], cat)
        self.assertFalse(r["pass"])

    def test_good_is_clean(self):
        r = lint_md(GOOD)
        self.assertEqual(r["issues"], {})
        self.assertTrue(r["pass"])

    def test_inline_code_does_not_cause_double_space(self):
        self.assertNotIn("double_space", lint_md("Run `a` (now) and `b`.\n")["issues"])

    def test_long_paragraph(self):
        self.assertIn("long_paragraph", lint_md("word " * 160 + "\n")["issues"])

    def test_list_continuation_indent_ok(self):
        self.assertNotIn("typed_indent", lint_md("- item\n  continued text\n")["issues"])


class ListStarts(unittest.TestCase):
    def test_bullets_under_text_are_flagged(self):
        r = lint_md("**Role**, Org, 2022\n- did a thing\n- did another\n")
        self.assertIn("list_without_blank_line", r["issues"])

    def test_blank_line_before_list_is_fine(self):
        r = lint_md("**Role**, Org, 2022\n\n- did a thing\n- did another\n")
        self.assertNotIn("list_without_blank_line", r["issues"])

    def test_list_after_heading_is_fine(self):
        self.assertNotIn("list_without_blank_line", lint_md("## Skills\n- one\n- two\n")["issues"])

    def test_nested_items_are_fine(self):
        self.assertNotIn("list_without_blank_line", lint_md("- a\n  - b\n- c\n")["issues"])


if __name__ == "__main__":
    unittest.main()
