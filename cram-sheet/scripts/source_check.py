#!/usr/bin/env python3
"""source_check: list what a document claims that its sources do not contain.

Usage:
  python3 source_check.py OUTPUT.md SOURCE [SOURCE ...] [--json]

Checks four kinds of claim against the text of the source files:
  numbers     every figure, date part, percent, and amount
  names       capitalized words in the middle of sentences (people, places, products)
  quotes      anything in double quotes of 3+ words
  citations   (Author, 2021) style in-text citations and Author (2021) forms

A number can be legitimately computed (a total, an average), so untraced numbers
are warnings to review. An untraced quote or citation is never fine: exit code 1.
This is a text match, not a fact checker: it cannot tell that a matched number
is attached to the right claim.
"""
import argparse
import json
import re
import sys

COMMON_CAPS = {
    "the", "this", "that", "these", "those", "and", "but", "for", "with", "from", "dear",
    "sincerely", "regards", "best", "thanks", "thank", "monday", "tuesday", "wednesday",
    "thursday", "friday", "saturday", "sunday", "january", "february", "march", "april",
    "may", "june", "july", "august", "september", "october", "november", "december",
    "abstract", "introduction", "methods", "method", "results", "discussion", "conclusion",
    "references", "summary", "date", "subject", "memo", "table", "figure", "attendees",
    "action", "actions", "decision", "decisions", "next", "yes", "note", "see", "please",
    "hi", "hello", "regarding", "attached", "background", "recommendation", "purpose",
    "objective", "data", "analysis", "procedure", "materials", "key", "terms", "overview",
    "agenda", "minutes", "meeting", "budget", "timeline", "risks", "cost", "costs", "total",
    "works", "cited", "tags", "contact", "education", "experience", "skills", "projects",
}


def norm(text):
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", text.lower())


def num_tokens(text):
    text = re.sub(r"(?m)^\s*(\d+)[.)]\s", " ", text)          # list numbering
    out = []
    for m in re.finditer(r"\d[\d,]*(?:\.\d+)?", text):
        out.append(m.group(0).replace(",", "").rstrip("."))
    return out


def names(text):
    found = []
    for line in text.splitlines():
        if re.match(r"\s*#", line) or line.strip().startswith("|"):
            continue
        line = re.sub(r"`[^`]*`|\*\*|__|\[|\]\([^)]*\)", " ", line)
        for sent in re.split(r"(?<=[.!?:])\s+|^\s*[-*]\s+|^\s*\d+[.)]\s+", line):
            toks = re.findall(r"[A-Za-z][A-Za-z'\-]*", sent)
            for i, t in enumerate(toks):
                if i == 0 or not t[0].isupper() or len(t) < 3 or t.lower() in COMMON_CAPS:
                    continue
                found.append(t)
    return found


def quotes(text):
    t = text.replace("“", '"').replace("”", '"')
    return [q.strip() for q in re.findall(r'"([^"\n]{12,300})"', t) if len(q.split()) >= 3]


CITE = re.compile(r"\(([A-Z][A-Za-z'\-]+(?:,? (?:&|and) [A-Z][A-Za-z'\-]+)?(?: et al\.)?),? (\d{4}[a-z]?)[,)]")
CITE_NARR = re.compile(r"\b([A-Z][A-Za-z'\-]+(?: et al\.)?) \((\d{4}[a-z]?)\)")


def citations(text):
    out = {(m.group(1), m.group(2)) for m in CITE.finditer(text)}
    out |= {(m.group(1), m.group(2)) for m in CITE_NARR.finditer(text)}
    return sorted(out)


NUMBER_WORDS = re.compile(r"\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fifteen|"
                          r"twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million)\b", re.I)


def check(output_text, source_texts):
    output_text = re.sub(r"<!--.*?-->", "", output_text, flags=re.S)         # cut-to-fit notes and such
    output_text = re.sub(r"([A-Z][A-Za-z\-]+)['\u2019]s\b", r"\1", output_text)   # Rivera's (2021) -> Rivera (2021)
    src = norm("\n".join(source_texts))
    src_nums = set(num_tokens("\n".join(source_texts)))
    res = {}
    nums = sorted(set(num_tokens(output_text)), key=lambda x: float(x) if x.replace(".", "").isdigit() else 0)
    res["numbers"] = dict(total=len(nums), untraced=[n for n in nums if n not in src_nums])
    nm = sorted(set(names(output_text)))
    res["names"] = dict(total=len(nm), untraced=[n for n in nm if n.lower() not in src])
    qs = quotes(output_text)
    res["quotes"] = dict(total=len(qs), untraced=[q for q in qs if norm(q) not in src])
    cs = citations(output_text)
    miss = []
    for author, year in cs:
        first = author.split(",")[0].split(" ")[0]
        if first.lower() not in src or year[:4] not in src:
            miss.append(f"{author} ({year})")
    res["citations"] = dict(total=len(cs), untraced=miss)
    tot = sum(v["total"] for v in res.values())
    bad = sum(len(v["untraced"]) for v in res.values())
    res["traced_share"] = round(1 - bad / tot, 3) if tot else 1.0
    res["hard_fail"] = bool(res["quotes"]["untraced"] or res["citations"]["untraced"])
    spelled = len(NUMBER_WORDS.findall("\n".join(source_texts)))
    res["spelled_numbers_in_sources"] = spelled
    res["warning"] = ("the sources spell out numbers in words (%d found): untraced numbers need a manual "
                      "check against them, so the traced share undercounts" % spelled) if spelled >= 5 else ""
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("output")
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    out = open(a.output, encoding="utf-8").read()
    srcs = [open(p, encoding="utf-8", errors="ignore").read() for p in a.sources]
    r = check(out, srcs)
    if a.json:
        print(json.dumps(r, indent=2))
    else:
        if r["warning"]:
            print("note:", r["warning"])
        print(f"traced {r['traced_share']:.0%} of claims  " + "  ".join(
            f"{k} {len(r[k]['untraced'])}/{r[k]['total']} untraced" for k in ("numbers", "names", "quotes", "citations")))
        for k in ("numbers", "names", "quotes", "citations"):
            if r[k]["untraced"]:
                print(f"  {k}: " + "; ".join(str(x) for x in r[k]["untraced"][:25]))
    sys.exit(1 if r["hard_fail"] else 0)


if __name__ == "__main__":
    main()
