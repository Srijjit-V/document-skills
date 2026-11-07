import unittest
from csvtrim import trim


class TrimTest(unittest.TestCase):
    def test_strips_cells(self):
        rows, dropped = trim([[" a ", " b"]])
        self.assertEqual(rows, [["a", "b"]])
        self.assertEqual(dropped, 0)

    def test_drops_empty_rows(self):
        rows, dropped = trim([["a"], ["", " "], []])
        self.assertEqual(rows, [["a"]])
        self.assertEqual(dropped, 2)

    def test_keep_empty(self):
        rows, dropped = trim([["a"], [" ", ""]], keep_empty=True)
        self.assertEqual(len(rows), 2)
        self.assertEqual(dropped, 0)


if __name__ == "__main__":
    unittest.main()
