import filecmp
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cram_to_html as C  # noqa: E402

SHEET = """# Water cycle: exam review
Source: Ch. 7 notes, 2026-11-04
> **If you only read one thing:** water moves in a loop.
Legend: ★ likely · ⚠ mistake

## Key terms ★
| Term | Meaning |
|---|---|
| Evaporation | liquid to vapor |

## Steps
1. Sun heats water
2. Vapor rises

## Common mistakes
- ⚠ Evaporation needs heat, not boiling: `**` stays literal in code.

<!-- Cut to fit: groundwater zones -->
"""


class Convert(unittest.TestCase):
    def setUp(self):
        self.h = C.convert(SHEET)

    def test_banner_legend_and_title(self):
        self.assertIn("If you only read one thing:", self.h)
        self.assertIn("Legend:", self.h)
        self.assertIn("<title>Water cycle: exam review</title>", self.h)

    def test_boxes_and_table(self):
        self.assertEqual(self.h.count("<section"), 3)
        self.assertIn("<th>Term</th>", self.h)
        self.assertIn("<ol>", self.h)

    def test_mistakes_box_is_the_red_box(self):
        self.assertIn('class="gotchas"', self.h)

    def test_cut_comment_is_not_rendered(self):
        self.assertNotIn("groundwater", self.h)

    def test_code_span_keeps_asterisks(self):
        self.assertIn("<code>**</code>", self.h)

    def test_body_type_is_not_below_the_floor(self):
        self.assertIn("font: 8.5pt/", self.h)


class Render(unittest.TestCase):
    def test_small_sheet_is_one_page(self):
        if C.find_chrome() is None:
            self.skipTest("needs Chrome")
        d = tempfile.mkdtemp()
        out = os.path.join(d, "s.html")
        with open(out, "w") as f:
            f.write(C.convert(SHEET))
        self.assertEqual(C.render_pdf(out, os.path.join(d, "s.pdf")), 1)


class Copies(unittest.TestCase):
    def test_shared_scripts_match_clean_docs(self):
        other = os.path.join(HERE, "..", "..", "clean-docs", "scripts")
        if not os.path.isdir(other):
            self.skipTest("clean-docs not beside cram-sheet")
        for f in ("doc_lint.py", "source_check.py"):
            self.assertTrue(filecmp.cmp(os.path.join(HERE, f), os.path.join(other, f), shallow=False),
                            f"{f} differs from clean-docs; copy the newer one")


if __name__ == "__main__":
    unittest.main()
