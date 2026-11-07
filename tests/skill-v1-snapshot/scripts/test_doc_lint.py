import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from doc_lint import lint  # noqa: E402

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

    def test_em_dash(self):
        r = lint("Fast — and cheap — and done.")
        self.assertEqual(r["issues"]["em_dash"][0]["count"], 2)


if __name__ == "__main__":
    unittest.main()
