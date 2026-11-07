"""Tests for md_to_pdf. The rendering tests need Chrome and pip packages
(markdown, pdfplumber); they skip when those are missing."""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import md_to_pdf as M  # noqa: E402
import presets as P  # noqa: E402

try:
    import markdown, pdfplumber  # noqa: E401,F401
    READY = M.find_chrome() is not None
except ImportError:
    READY = False

WIDE = "# Wide\n\n| Key | Value |\n|---|---|\n| " + "A" * 160 + " | x |\n\n" + "Body text. " * 40 + "\n"


class Html(unittest.TestCase):
    def test_bold_only_paragraph_is_kept_with_next(self):
        if not READY:
            self.skipTest("needs markdown")
        html = M.md_to_html("**Formatting:**\n\nBody.\n", P.get("report"))
        self.assertIn('class="lead"', html)

    def test_escaped_pipe_in_table_cell(self):
        if not READY:
            self.skipTest("needs markdown")
        html = M.md_to_html("| a | b |\n|---|---|\n| x \\| y | z |\n", P.get("report"))
        self.assertIn("x | y", html)

    def test_book_preset_has_indent_and_no_paragraph_space(self):
        css = M.css_for(P.get("book"), "")
        self.assertIn("text-indent: 1.5em", css)
        self.assertNotIn("margin: 0 0 0.0pt", css)


@unittest.skipUnless(READY, "needs Chrome, markdown, pdfplumber")
class Render(unittest.TestCase):
    def test_wide_table_never_shrinks_type(self):
        out = os.path.join(tempfile.mkdtemp(), "w.pdf")
        r, log = M.build_pdf(WIDE, P.get("report"), out)
        self.assertGreaterEqual(r["body_pt"], P.MIN_BODY_PT)
        self.assertAlmostEqual(r["body_pt"], 11.0, delta=0.2)

    def test_tiny_doc_has_no_false_leading_alarm(self):
        out = os.path.join(tempfile.mkdtemp(), "tiny.pdf")
        r, _ = M.build_pdf("# Smoke test\n\nA short document.\n\n## Section\n\nOne more line.\n", P.get("report"), out)
        self.assertNotIn("leading", r["issues"])
        self.assertTrue(r["pass"])

    def test_normal_doc_scores_clean(self):
        out = os.path.join(tempfile.mkdtemp(), "n.pdf")
        r, _ = M.build_pdf("# T\n\n" + ("A sentence of ordinary prose. " * 30 + "\n\n") * 6, P.get("report"), out)
        self.assertTrue(r["pass"], r["issues"])
        self.assertTrue(45 <= r["avg_chars_per_line"] <= 90)


if __name__ == "__main__":
    unittest.main()
