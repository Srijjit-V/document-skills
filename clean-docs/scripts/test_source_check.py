import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from source_check import check  # noqa: E402

SRC = ["""Notes: Maria Santos will order lumber by Nov 15. Budget approved: $2,400 for raised beds.
The vote was 5-2. The city permit fee is $85. "We should wait until spring for the shed," said Tom Ibarra.
Rivera, M. (2021). Later start times and attendance. Journal of Fictional Education, 12(3), 44-58."""]


class SourceCheck(unittest.TestCase):
    def test_traced_claims_pass(self):
        out = ('Maria Santos will order lumber by Nov 15. The group approved $2,400 and voted 5-2. '
               'Tom Ibarra said "We should wait until spring for the shed" (Rivera, 2021).')
        r = check(out, SRC)
        self.assertEqual(r["numbers"]["untraced"], [])
        self.assertEqual(r["names"]["untraced"], [])
        self.assertEqual(r["quotes"]["untraced"], [])
        self.assertEqual(r["citations"]["untraced"], [])
        self.assertFalse(r["hard_fail"])

    def test_invented_number_and_name_are_flagged(self):
        r = check("Maria Santos ordered $3,100 of lumber from Hollis Supply.", SRC)
        self.assertIn("3100", r["numbers"]["untraced"])
        self.assertIn("Hollis", r["names"]["untraced"])

    def test_invented_quote_and_citation_are_hard_failures(self):
        out = 'As Kim said, "schools should start much later in the day" (Kim, 2019).'
        r = check(out, SRC)
        self.assertTrue(r["hard_fail"])
        self.assertTrue(r["quotes"]["untraced"])
        self.assertIn("Kim (2019)", r["citations"]["untraced"])

    def test_curly_quotes_and_comma_numbers_match(self):
        r = check("The “We should wait until spring for the shed” line stands; budget 2400 was approved.", SRC)
        self.assertEqual(r["quotes"]["untraced"], [])
        self.assertEqual(r["numbers"]["untraced"], [])

    def test_list_numbering_is_not_a_claim(self):
        r = check("1. First step\n2. Second step\n", SRC)
        self.assertEqual(r["numbers"]["total"], 0)

    def test_narrative_citation_form(self):
        r = check("Rivera (2021) found an effect.", SRC)
        self.assertEqual(r["citations"]["untraced"], [])


class Cleanup(unittest.TestCase):
    def test_possessive_citation_is_not_untraced(self):
        self.assertEqual(check("Rivera's (2021) study found it.", SRC)["citations"]["untraced"], [])

    def test_html_comments_are_ignored(self):
        r = check('Fine.\n<!-- Cut to fit: "an invented quote of many words here" -->', SRC)
        self.assertEqual(r["quotes"]["untraced"], [])


class SpelledNumbers(unittest.TestCase):
    def test_warns_when_sources_spell_numbers_out(self):
        src = ["The quote is twenty-three ten for lumber and ninety for screws, so twenty-four hundred; five or six people, one hundred."]
        r = check("Lumber was $2,310 and screws $90.", src)
        self.assertGreaterEqual(r["spelled_numbers_in_sources"], 5)
        self.assertIn("manual", r["warning"])

    def test_no_warning_for_digit_sources(self):
        self.assertEqual(check("It cost $90.", ["It cost $90."])["warning"], "")


if __name__ == "__main__":
    unittest.main()
