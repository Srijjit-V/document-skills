#!/usr/bin/env python3
"""doc_lint: flag padded, AI-flavored, over-formatted Markdown docs.

Usage:
  python3 doc_lint.py FILE.md [--budget WORDS] [--mode standard|cram] [--json]

Exit code 0 = pass (score >= 80 and within budget), 1 = fail.
Code blocks and inline code are ignored for prose checks.
"""
import argparse
import json
import re
import sys

AI_WORDS = [
    "delve", "delves", "delving", "multifaceted", "landscape", "tapestry",
    "crucial", "robust", "seamless", "seamlessly", "leverage", "leverages",
    "leveraging", "pivotal", "underscore", "underscores", "showcase",
    "showcases", "testament", "realm", "intricate", "embark", "elevate",
    "unleash", "empower", "empowers", "holistic", "synergy", "paramount",
    "vibrant", "comprehensive", "cutting-edge", "game-changer", "streamline",
    "streamlines", "effortless", "effortlessly", "harness", "navigate the",
    "in today's", "ever-evolving", "boasts", "furthermore", "moreover",
]
FILLER = [
    "it is important to note", "it's important to note", "it is worth noting",
    "it's worth noting", "note that", "please note", "in order to",
    "simply", "just ", "basically", "essentially", "very ", "really ",
    "at the end of the day", "needless to say", "as mentioned",
    "as previously mentioned", "as we can see", "let's dive", "let's explore",
    "i hope this helps", "feel free to", "whether you're", "this guide will",
    "in this guide", "in this document", "this document describes",
    "serves as", "stands as", "plays a key role", "plays a crucial role",
    "it should be noted", "you can ", "there are ", "there is ",
]
HEDGES = [
    "might", "may ", "could potentially", "possibly", "perhaps", "generally",
    "typically", "usually", "arguably", "somewhat", "relatively", "in some cases",
    "to some extent", "it seems", "should work",
]
RECAP = [
    r"^#+\s*(summary|conclusion|in summary|wrapping up|final thoughts|recap|key takeaways)\b",
    r"\bin (summary|conclusion)\b", r"\bto (sum up|summarize|recap)\b",
    r"\boverall, ", r"\bin short, ",
]

WEIGHTS = {  # points lost per hit, capped per category
    "ai_word": (3, 25), "filler": (2, 15), "hedge": (1, 10), "em_dash": (2, 15),
    "recap": (8, 16), "header_density": (10, 10), "bullet_ratio": (10, 10),
    "bold": (2, 10), "nesting": (3, 9), "restate": (6, 18), "budget": (20, 20),
}


def strip_code(text):
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"~~~.*?~~~", "", text, flags=re.S)
    return re.sub(r"`[^`\n]*`", "CODE", text)


def words(s):
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9'_-]*", s)


def paragraphs(prose):
    out = []
    for block in re.split(r"\n\s*\n", prose):
        lines = [l for l in block.splitlines()
                 if l.strip() and not l.lstrip().startswith(("#", "|", ">"))]
        lines = [l for l in lines if not re.match(r"\s*([-*+]|\d+\.)\s", l)]
        p = " ".join(lines).strip()
        if len(words(p)) >= 12:
            out.append(p)
    return out


def shingles(p, n=3):
    w = [x.lower() for x in words(p)]
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


def find_phrases(low, phrases, boundary=True):
    hits = []
    for ph in phrases:
        pat = re.escape(ph.strip()) if not boundary else r"\b" + re.escape(ph.strip()) + r"\b"
        n = len(re.findall(pat, low))
        if n:
            hits.append((ph.strip(), n))
    return hits


def lint(text, budget=None, mode="standard"):
    # <!-- doc_lint: allow ai_word,filler --> skips categories for docs that
    # discuss the words themselves (style guides, this skill's references).
    allow = set()
    for m in re.findall(r"<!--\s*doc_lint:\s*allow\s+([\w,\s]+?)\s*-->", text):
        allow |= {x.strip() for x in m.split(",")}
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    prose = strip_code(text)
    low = prose.lower()
    lines = [l for l in prose.splitlines() if l.strip()]
    wc = len(words(strip_code(text)))
    total_wc = len(words(text))
    issues = {}

    def add(cat, detail, count=1):
        issues.setdefault(cat, []).append((detail, count))

    for w, n in find_phrases(low, AI_WORDS):
        add("ai_word", w, n)
    for w, n in find_phrases(low, FILLER):
        add("filler", w, n)
    for w, n in find_phrases(low, HEDGES):
        add("hedge", w, n)
    n = prose.count("—") + len(re.findall(r"\s--\s", prose))
    if n:
        add("em_dash", "em dashes", n)
    for pat in RECAP:
        n = len(re.findall(pat, low, flags=re.M))
        if n:
            add("recap", pat, n)

    headers = [l for l in lines if re.match(r"\s*#{1,6}\s", l)]
    bullets = [l for l in lines if re.match(r"\s*([-*+]|\d+\.)\s", l)]
    body_lines = [l for l in lines if not re.match(r"\s*#{1,6}\s", l)]
    # Cram sheets are built from boxes and one-line facts; density rules differ.
    if mode == "standard":
        if len(headers) > 1 and wc / max(len(headers), 1) < 80:
            add("header_density", f"{len(headers)} headers for {wc} words "
                f"(1 per {wc // max(len(headers), 1)} words; want >= 80)")
        if wc < 300 and len(headers) > 3:
            add("header_density", f"short doc ({wc} words) with {len(headers)} headers")
        ratio = len(bullets) / max(len(body_lines), 1)
        if len(bullets) >= 6 and ratio > 0.5:
            add("bullet_ratio", f"{ratio:.0%} of body lines are bullets (want <= 50%)")
    nested = [l for l in bullets if len(l.expandtabs(4)) - len(l.expandtabs(4).lstrip()) >= 6]
    if nested:
        add("nesting", "bullets nested 2+ levels", len(nested))

    bold = len(re.findall(r"\*\*[^*\n]+\*\*|__[^_\n]+__", prose))
    allowed = max(2, wc // 100) if mode == "standard" else max(4, wc // 40)
    if bold > allowed:
        add("bold", f"{bold} bold spans (allow {allowed} for {wc} words)", bold - allowed)

    paras = paragraphs(prose)
    sh = [shingles(p) for p in paras]
    for i in range(len(paras)):
        for j in range(i):
            if not sh[i] or not sh[j]:
                continue
            sim = len(sh[i] & sh[j]) / len(sh[i] | sh[j])
            if sim >= 0.25:
                add("restate", f"para {i + 1} repeats para {j + 1} ({sim:.0%} overlap): "
                    f"\"{paras[i][:60]}...\"")

    if budget and total_wc > budget:
        add("budget", f"{total_wc} words > budget {budget}")

    issues = {k: v for k, v in issues.items() if k not in allow}
    score = 100
    for cat, hits in issues.items():
        per, cap = WEIGHTS[cat]
        score -= min(cap, per * sum(c for _, c in hits))
    score = max(score, 0)
    return {
        "words": total_wc, "prose_words": wc, "budget": budget,
        "headers": len(headers), "bullets": len(bullets), "bold": bold,
        "score": score, "pass": score >= 80 and "budget" not in issues,
        "issues": {k: [{"what": d, "count": c} for d, c in v] for k, v in issues.items()},
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--budget", type=int, help="max words (whole file, code included)")
    ap.add_argument("--mode", choices=["standard", "cram"], default="standard")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    with open(a.file, encoding="utf-8") as f:
        r = lint(f.read(), a.budget, a.mode)
    if a.json:
        print(json.dumps(r, indent=2))
    else:
        status = "PASS" if r["pass"] else "FAIL"
        b = f"/{r['budget']}" if r["budget"] else ""
        print(f"{status}  score {r['score']}/100  words {r['words']}{b}  "
              f"headers {r['headers']}  bullets {r['bullets']}  bold {r['bold']}")
        for cat, hits in r["issues"].items():
            print(f"  {cat}: " + "; ".join(
                f"{h['what']}" + (f" x{h['count']}" if h["count"] > 1 else "") for h in hits))
    sys.exit(0 if r["pass"] else 1)


if __name__ == "__main__":
    main()
