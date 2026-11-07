#!/usr/bin/env python3
"""doc_lint: flag padded, AI-flavored, over-formatted Markdown documents.

Usage:
  python3 doc_lint.py FILE.md [--type TYPE] [--budget WORDS] [--mode standard|cram] [--json]

--type picks a profile (budget, and which density rules apply) from the table in
PROFILES: email, memo, report, essay, cover-letter, resume, proposal, minutes,
lab-report, study-guide, policy, newsletter, readme, api-reference, runbook, adr.
Without --type the strict general rules apply, as before.
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
    "evolving landscape", "stands as", "serves as",
]
FILLER = [
    "it is important to note", "it's important to note", "it is worth noting",
    "it's worth noting", "note that", "please note", "in order to",
    "simply", "just ", "basically", "essentially", "very ", "really ",
    "at the end of the day", "needless to say", "as mentioned",
    "as previously mentioned", "as we can see", "let's dive", "let's explore",
    "i hope this helps", "feel free to", "whether you're", "this guide will",
    "in this guide", "in this document", "this document describes",
    "plays a key role", "plays a crucial role", "it should be noted",
    "in this essay", "this essay will", "in this paper, we will",
]
HEDGES = [
    "might", "could potentially", "possibly", "perhaps", "arguably", "somewhat",
    "to some extent", "it seems", "should work",
]
RECAP_PHRASES = [r"\bin (summary|conclusion)\b", r"\bto (sum up|summarize|recap)\b",
                 r"\boverall, ", r"\bin short, "]
RECAP_HEADING = r"^#+\s*(summary|conclusion|in summary|wrapping up|final thoughts|recap|key takeaways)\b"
# Generic first and last lines. Wikipedia's AI-writing page lists chatbot pleasantries;
# Harvard's career blog says to skip "I am writing to express my interest in".
OPENERS = [
    r"i hope (this|you)\b.{0,40}\b(well|finds you)", r"i hope this (email|message|note)",
    r"i am writing to (express|apply|inquire|request|submit|follow|share)",
    r"i('m| am) (excited|thrilled|delighted|pleased) to (apply|submit|share|announce)",
    r"in today's (fast-paced|digital|modern|ever)", r"in the (ever-evolving|fast-paced)",
    r"^(certainly|absolutely)[!,.]", r"here is (a|the|your) (draft|template|summary)",
]
CLOSERS = [
    r"thank you for (your )?(time|consideration)", r"i look forward to (hearing|the opportunity)",
    r"(please )?(do not|don't) hesitate to", r"let me know if you (have|need)",
    r"i hope this helps", r"feel free to (reach|contact)", r"best of luck",
]
SALUTATION = re.compile(r"^(dear|hi|hello|to whom|to:|from:|date:|subject:|re:)\b", re.I)

# type: budget (prose words), density (header-density rule on?), bullets (max bullet ratio),
# bold (bold spans per 100 words), labels (bold-label check on?), no_headers, conclusion_ok
PROFILES = {
    "email":         dict(budget=150,  density=False, bullets=0.5,  bold=1, labels=True,  no_headers=True),
    "memo":          dict(budget=600,  density=True,  words_per_header=40, bullets=0.5,  bold=1, labels=True),
    "report":        dict(budget=1500, density=True,  words_per_header=40, bullets=0.5,  bold=1, labels=True,  conclusion_ok=True),
    "essay":         dict(budget=1200, density=False, bullets=0.2,  bold=0.5, labels=True),
    "cover-letter":  dict(budget=400,  density=False, bullets=0.2,  bold=0.5, labels=True, no_headers=True),
    "resume":        dict(budget=550,  density=False, bullets=0.95, bold=4, labels=False),
    "proposal":      dict(budget=1200, density=True,  words_per_header=40, bullets=0.5,  bold=1, labels=True,  conclusion_ok=True),
    "minutes":       dict(budget=500,  density=False, bullets=0.7,  bold=3, labels=False),
    "lab-report":    dict(budget=1200, density=False, bullets=0.4,  bold=1, labels=True,  conclusion_ok=True),
    "study-guide":   dict(budget=900,  density=False, bullets=0.7,  bold=3, labels=False),
    "policy":        dict(budget=800,  density=False, bullets=0.6,  bold=2, labels=False),
    "newsletter":    dict(budget=500,  density=False, bullets=0.5,  bold=2, labels=True),
    "readme":        dict(budget=600,  density=True,  words_per_header=40, bullets=0.5,  bold=1, labels=True),
    "api-reference": dict(budget=1200, density=False, bullets=0.6,  bold=1, labels=True),
    "runbook":       dict(budget=500,  density=True,  words_per_header=30, bullets=0.7,  bold=2, labels=True),
    "adr":           dict(budget=600,  density=True,  words_per_header=40, bullets=0.5,  bold=1, labels=True),
}

WEIGHTS = {  # points lost per hit, capped per category
    "ai_word": (3, 25), "filler": (2, 15), "hedge": (1, 10), "em_dash": (2, 15),
    "recap": (8, 16), "header_density": (10, 10), "bullet_ratio": (10, 10),
    "bold": (2, 10), "bold_labels": (10, 10), "nesting": (3, 9), "restate": (6, 18),
    "budget": (20, 20), "opener": (4, 8), "closer": (3, 6), "rule_of_three": (1, 6),
    "negative_parallelism": (2, 6), "long_sentences": (6, 6), "headers_in_short_form": (8, 8),
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


def find_phrases(low, phrases):
    hits = []
    for ph in phrases:
        n = len(re.findall(r"\b" + re.escape(ph.strip()) + r"\b", low))
        if n:
            hits.append((ph.strip(), n))
    return hits


def sentences(paras):
    out = []
    for p in paras:
        out += [s for s in re.split(r"(?<=[.!?])\s+", p) if s.strip()]
    return out


def lint(text, budget=None, mode="standard", doc_type=None):
    prof = PROFILES.get(doc_type or "", {})
    if doc_type and doc_type not in PROFILES:
        raise ValueError(f"unknown type {doc_type!r}; choose from {', '.join(PROFILES)}")
    if budget is None and prof:
        budget = prof["budget"]
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
    for pat in RECAP_PHRASES:
        n = len(re.findall(pat, low))
        if n:
            add("recap", pat, n)
    # A summary at the top is the answer first; only a closing "Summary" heading is a recap.
    seen, late = 0, []
    for l in lines:
        if re.match(RECAP_HEADING, l.lower()) and seen >= 0.7 * wc:
            late.append(l)
        seen += len(words(l))
    if late and not prof.get("conclusion_ok"):
        add("recap", "closing summary or conclusion heading", len(late))

    headers = [l for l in lines if re.match(r"\s*#{1,6}\s", l)]
    bullets = [l for l in lines if re.match(r"\s*([-*+]|\d+\.)\s", l)]
    body_lines = [l for l in lines if not re.match(r"\s*#{1,6}\s", l)]
    # Cram sheets are built from boxes and one-line facts; density rules differ.
    if mode == "standard":
        if prof.get("density", True):
            wph = prof.get("words_per_header", 60)   # fixed forms (memo, report, README) carry required sections
            if len(headers) > 1 and wc / max(len(headers), 1) < wph:
                add("header_density", f"{len(headers)} headers for {wc} words "
                    f"(1 per {wc // max(len(headers), 1)} words; want >= {wph})")
            if wph == 60 and wc < 300 and len(headers) > 3:
                add("header_density", f"short doc ({wc} words) with {len(headers)} headers")
        max_ratio = prof.get("bullets", 0.5)
        ratio = len(bullets) / max(len(body_lines), 1)
        if len(bullets) >= 6 and ratio > max_ratio:
            add("bullet_ratio", f"{ratio:.0%} of body lines are bullets (want <= {max_ratio:.0%})")
    if prof.get("no_headers") and len(headers) > 1:
        add("headers_in_short_form", f"{len(headers)} headings in a {doc_type}")
    nested = [l for l in bullets if len(l.expandtabs(4)) - len(l.expandtabs(4).lstrip()) >= 6]
    if nested:
        add("nesting", "bullets nested 2+ levels", len(nested))

    # Bold in table rows (a Total row) and in header-block labels (**TO:**) is by design.
    bold_text = "\n".join(l for l in prose.splitlines()
                          if not l.lstrip().startswith("|")
                          and not re.match(r"\s*\*\*(TO|FROM|DATE|SUBJECT|CC|RE):\*\*", l))
    bold = len(re.findall(r"\*\*[^*\n]+\*\*|__[^_\n]+__", bold_text))
    per100 = prof.get("bold", 1)
    allowed = (max(2, int(wc * per100 / 100)) if mode == "standard" else max(4, wc // 40))
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

    labels = [l for l in bullets if re.match(r"\s*([-*+]|\d+\.)\s+\*\*[^*]+\*\*", l)]
    # Cram sheets may bold a scan keyword per line; some types (minutes, resumes) label by design.
    if mode == "standard" and prof.get("labels", True) and len(labels) >= 3 and len(labels) >= len(bullets) / 2:
        add("bold_labels", f"{len(labels)} of {len(bullets)} list items start with a bold label")

    if mode == "standard" and paras:
        first = next((p for p in paras if not SALUTATION.match(p)), paras[0]).lower()
        first = re.split(r"(?<=[.!?])\s", first)[0][:200]
        for pat in OPENERS:
            if re.search(pat, first):
                add("opener", f"generic opener: \"{first[:60]}\"")
                break
        blocks = [b for b in re.split(r"\n\s*\n", prose) if b.strip()]
        last = " ".join(blocks[-2:]).lower()[-300:]
        for pat in CLOSERS:
            if re.search(pat, last):
                add("closer", "generic closing line")
                break
        triads = len(re.findall(r"\b[a-z]+, [a-z]+, (?:and|or) [a-z]+\b", low))
        if triads > max(2, wc // 250):
            add("rule_of_three", f"{triads} lists of three single words", triads - max(2, wc // 250))
        neg = len(re.findall(r"\bnot (?:just|only|merely) [^.;]{3,80}?,? (?:but|it's|it is)\b", low))
        if neg:
            add("negative_parallelism", "\"not just X, but Y\" framing", neg)
        sents = sentences(paras)
        if len(sents) >= 8:
            long_ = sum(1 for s in sents if len(words(s)) > 25)
            if long_ / len(sents) > 0.2:
                add("long_sentences", f"{long_} of {len(sents)} sentences run over 25 words (GOV.UK: split them)")

    # Budget counts prose only: runnable examples are the good part of a doc.
    if budget and wc > budget:
        add("budget", f"{wc} prose words > budget {budget} (code excluded)")

    issues = {k: v for k, v in issues.items() if k not in allow}
    score = 100
    for cat, hits in issues.items():
        per, cap = WEIGHTS[cat]
        score -= min(cap, per * sum(c for _, c in hits))
    score = max(score, 0)
    return {
        "words": total_wc, "prose_words": wc, "budget": budget, "type": doc_type,
        "headers": len(headers), "bullets": len(bullets), "bold": bold,
        "score": score, "pass": score >= 80 and "budget" not in issues,
        "issues": {k: [{"what": d, "count": c} for d, c in v] for k, v in issues.items()},
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--budget", type=int, help="max prose words (code blocks excluded)")
    ap.add_argument("--type", dest="doc_type", choices=sorted(PROFILES), help="document type profile")
    ap.add_argument("--mode", choices=["standard", "cram"], default="standard")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    with open(a.file, encoding="utf-8") as f:
        r = lint(f.read(), a.budget, a.mode, a.doc_type)
    if a.json:
        print(json.dumps(r, indent=2))
    else:
        status = "PASS" if r["pass"] else "FAIL"
        b = f"/{r['budget']}" if r["budget"] else ""
        print(f"{status}  score {r['score']}/100  prose words {r['prose_words']}{b} "
              f"(total {r['words']} incl. code)  "
              f"headers {r['headers']}  bullets {r['bullets']}  bold {r['bold']}")
        for cat, hits in r["issues"].items():
            print(f"  {cat}: " + "; ".join(
                f"{h['what']}" + (f" x{h['count']}" if h["count"] > 1 else "") for h in hits))
    sys.exit(0 if r["pass"] else 1)


if __name__ == "__main__":
    main()
