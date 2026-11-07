"""Preset tests. The render tests need Chrome plus markdown and pdfplumber and skip without them."""
import logging
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import md_to_pdf as M  # noqa: E402
import presets as P  # noqa: E402

logging.getLogger("pdfminer").setLevel(logging.ERROR)
try:
    import markdown, pdfplumber  # noqa: E401,F401
    READY = M.find_chrome() is not None
except ImportError:
    READY = False

ESSAY = """# Later Starts and Attendance

Many districts have debated whether first bells should move later. A fictional study found that attendance rose after a shift (Rivera, 2021). The effect was larger for older students, which fits a simple account of teenage sleep timing, though the sample came from one district.

## Evidence

A second fictional report found no change in scores (Chen, 2022). The two results suggest that the benefit is behavioral before it is academic, so districts should measure attendance first and scores later, over several years.

## References

Chen, L., & Okoye, A. (2022). Start times and test scores in one district. Journal of Fictional Education, 14(1), 12-30.
"""

LETTER = """Jordan Lee
12 Elm Street
Riverbend, WA 98000

November 4, 2026

Dear Ms. Whitfield,

I am applying for the Program Coordinator role.

Sincerely,
Jordan Lee
"""

RESUME = """# Jordan Lee
Riverbend, WA

## Experience

**Program Assistant**, Riverbend Library, 2022 to 2024
- Ran weekly story hour for 40 children
- Organized 12 community events
"""


def lines_of(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        pg = pdf.pages[0]
        return pg, pg.extract_text_lines()


def render(md, preset):
    out = os.path.join(tempfile.mkdtemp(), "t.pdf")
    r, _ = M.build_pdf(md, P.get(preset), out)
    return out, r


class Table(unittest.TestCase):
    def test_every_preset_is_valid(self):
        for name in P.PRESETS:
            p = P.get(name)
            self.assertGreaterEqual(p["body_pt"], P.MIN_BODY_PT, name)

    def test_academic_numbers(self):
        p = P.get("academic")
        self.assertEqual(p["leading"], 2.0)
        self.assertEqual(p["first_line_indent_em"] * p["body_pt"], 36.0)   # 0.5 in
        self.assertEqual((p["margin_x_in"], p["margin_y_in"]), (1.0, 1.0))
        self.assertEqual(p["para_space_pt"], 0)
        self.assertEqual(p["page_number"], "top-right")

    def test_resume_follows_mit_floor(self):
        p = P.get("resume")
        self.assertGreaterEqual(p["margin_x_in"], 0.5)
        self.assertGreaterEqual(p["body_pt"], 10.0)
        self.assertEqual(p["max_pages"], 1)

    def test_academic_css(self):
        css = M.css_for(P.get("academic"), "")
        self.assertIn("@top-right", css)
        self.assertIn("p.ref", css)

    def test_references_get_hanging_class(self):
        html = M.mark_references("<h2>Body</h2><p>x</p><h2>References</h2><p>a</p><p>b</p><h2>Appendix</h2><p>c</p>")
        self.assertEqual(html.count('class="ref"'), 2)


@unittest.skipUnless(READY, "needs Chrome, markdown, pdfplumber")
class Render(unittest.TestCase):
    def test_academic_indent_hanging_indent_and_page_number(self):
        out, r = render(ESSAY, "academic")
        pg, ls = lines_of(out)
        self.assertAlmostEqual(r["leading"], 2.0, delta=0.05)
        first = next(l for l in ls if l["text"].startswith("Many districts"))
        second = next(l for l in ls if l["top"] > first["top"] and not l["text"].startswith("Many"))
        self.assertAlmostEqual(first["x0"] - second["x0"], 36.0, delta=1.5)          # first-line indent 0.5 in
        ref = next(l for l in ls if l["text"].startswith("Chen, L."))
        ref2 = next(l for l in ls if l["top"] > ref["top"] and l["text"].startswith(("Education", "Journal", "14", "30")) or (l["top"] > ref["top"] and l is not ref))
        self.assertAlmostEqual(ref2["x0"] - ref["x0"], 36.0, delta=1.5)              # hanging indent 0.5 in
        num = next(l for l in ls if l["text"].strip() == "1")
        self.assertGreater(num["x1"], pg.width - 1.2 * 72)                            # flush right
        self.assertLess(num["top"], 72)                                               # in the top margin

    def test_letter_keeps_address_lines_apart(self):
        out, r = render(LETTER, "letter")
        _, ls = lines_of(out)
        texts = [l["text"] for l in ls]
        self.assertIn("12 Elm Street", texts)
        self.assertIn("Riverbend, WA 98000", texts)
        self.assertEqual(r["pages"], 1)
        self.assertNotIn("1 / 1", " ".join(texts))      # letters carry no page number

    def test_resume_has_real_bullets_and_one_page(self):
        out, r = render(RESUME, "resume")
        _, ls = lines_of(out)
        self.assertFalse(any(l["text"].lstrip().startswith("- ") for l in ls))   # no typed dashes
        entry = next(l for l in ls if l["text"].startswith("Program Assistant"))
        item = next(l for l in ls if l["text"].startswith("Ran weekly"))
        self.assertGreater(item["x0"] - entry["x0"], 8)      # a real list: bullet lines are indented under the entry
        self.assertEqual(r["pages"], 1)

    def test_resume_over_one_page_exits_nonzero(self):
        d = tempfile.mkdtemp()
        md = os.path.join(d, "r.md")
        with open(md, "w") as f:
            f.write("# Long Resume\n\n## Experience\n\n" + "".join(
                f"**Role {i}**, Org, 2020\n- Did a distinct thing number {i} for the team this year\n- Another distinct thing {i}\n\n"
                for i in range(30)))
        rc = subprocess.run([sys.executable, os.path.join(HERE, "md_to_pdf.py"), md, "-o", os.path.join(d, "r.pdf"),
                             "--preset", "resume"], capture_output=True, text=True).returncode
        self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
