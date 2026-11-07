import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mdutil import fix_list_starts  # noqa: E402


class ListStarts(unittest.TestCase):
    def test_inserts_blank_line_before_bullets(self):
        self.assertEqual(fix_list_starts("Entry\n- a\n- b"), "Entry\n\n- a\n- b")

    def test_leaves_existing_blank_line(self):
        self.assertEqual(fix_list_starts("Entry\n\n- a"), "Entry\n\n- a")

    def test_numbered_list_only_when_it_starts_at_one(self):
        self.assertEqual(fix_list_starts("Text\n1. a\n2. b"), "Text\n\n1. a\n2. b")
        self.assertEqual(fix_list_starts("Text\n2. continues a sentence"), "Text\n2. continues a sentence")

    def test_does_not_split_list_items_or_nesting(self):
        s = "- a\n  - b\n- c"
        self.assertEqual(fix_list_starts(s), s)

    def test_code_fences_are_untouched(self):
        s = "```\nText\n- not a list\n```"
        self.assertEqual(fix_list_starts(s), s)

    def test_bold_line_is_not_a_bullet(self):
        s = "**Role**\n- a"
        self.assertEqual(fix_list_starts(s), "**Role**\n\n- a")
        self.assertEqual(fix_list_starts("**bold** text"), "**bold** text")

    def test_continuation_line_after_item_is_not_text(self):
        s = "- a\n  more of a\n- b"
        self.assertEqual(fix_list_starts(s), s)


if __name__ == "__main__":
    unittest.main()
