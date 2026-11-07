import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import markdown  # noqa: F401
    import md_to_gdoc_html as G
    READY = True
except ImportError:
    READY = False

MD = "# T\n\nText with `code`.\n\n```\nline one\nline two\n```\n\n| A | B |\n|---|---|\n| x | y |\n\n1. one\n2. two\n\n#### deep\n"


@unittest.skipUnless(READY, "needs markdown")
class Gdoc(unittest.TestCase):
    def setUp(self):
        self.h = G.convert(MD, "report")

    def test_code_font_is_one_docs_honors(self):
        self.assertIn("'Courier New'", self.h)
        self.assertNotIn("Roboto Mono", self.h)
        self.assertNotIn("Consolas", self.h)

    def test_cells_and_list_items_carry_a_font(self):
        self.assertIn('<td style="font-family:Georgia', self.h)
        self.assertIn('<li style="font-family:Georgia', self.h)

    def test_header_cells_bold(self):
        self.assertIn("<b>A</b>", self.h)

    def test_no_style_block_or_classes(self):
        self.assertNotIn("<style", self.h)
        self.assertNotIn("class=", self.h)

    def test_max_three_heading_levels(self):
        self.assertNotIn("<h4", self.h)

    def test_book_preset_indent_not_space(self):
        b = G.convert(MD, "book")
        self.assertIn("text-indent:16.5pt", b)
        self.assertIn("margin:0 0 0.0pt 0", b)


    def test_academic_centers_h1_and_italicizes_h3(self):
        h = G.convert("# Title\n\n### Level three\n\nBody.\n", "academic")
        self.assertIn("text-align:center", h)
        self.assertIn("font-style:italic", h)
        self.assertIn("Times New Roman", h)
        self.assertIn("text-indent:36.0pt", h)

    def test_references_get_a_hanging_indent(self):
        h = G.convert("# T\n\nBody text.\n\n## References\n\nRivera, M. (2021). A title.\n", "academic")
        self.assertIn("margin:0 0 0.0pt 36pt;text-indent:-36pt", h)
        body_p = h.split("References")[0]
        self.assertNotIn("-36pt", body_p)

    def test_resume_bullets_become_a_real_list(self):
        h = G.convert("**Role**, Org\n- did a thing\n- did more\n", "resume")
        self.assertIn("<ul>", h)
        self.assertEqual(h.count("<li"), 2)


if __name__ == "__main__":
    unittest.main()
