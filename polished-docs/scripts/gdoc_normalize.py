#!/usr/bin/env python3
"""gdoc_normalize: turn a Google Docs JSON (documents.get) into ONE batchUpdate body
that fixes layout, plus a report of what it cannot fix safely.

Usage:
  python3 gdoc_normalize.py doc.json [--preset report|compact|book] [-o batch.json]

Input is the JSON from documents.get (pass includeTabsContent=true if the doc has
tabs; legacy body.content also works). Output {"requests": [...], "writeControl":
{"requiredRevisionId": ...}} is ready for documents.batchUpdate.

What it changes
  - Named styles NORMAL_TEXT and HEADING_1..3 (font, size, spacing, keepWithNext)
  - Direct paragraph and text formatting that disagrees with the preset
  - Deletes empty paragraphs used as spacing and typed (space/tab) indents
What it never touches: tables, inline objects, bulleted paragraphs' indents.
Report only: typed bullets/numbers, bold-as-heading, ALL CAPS headings,
heading levels beyond 3, stacked headings, TITLE/SUBTITLE paragraphs.

Requests are ordered from the highest index to the lowest (Google's advice), the
named-style requests come first, and writeControl guards against stale edits.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import presets as P  # noqa: E402
from mdutil import REF_HEADING  # noqa: E402

MONO = re.compile(r"mono|courier|consolas|menlo|code", re.I)
TYPED_MARK = re.compile(r"^\s*([•◦▪▫●○■□‣–—*-]|\d+[.)]|\(\d+\)|\([a-zA-Z]\))\s+\S")
HEADINGS = {"HEADING_1": 1, "HEADING_2": 2, "HEADING_3": 3}


def pt(x):
    return {"magnitude": round(float(x), 2), "unit": "PT"}


def targets(preset):
    """Target paragraph and text style per named style."""
    p = P.get(preset)
    body = p["body_pt"]
    normal_para = {"lineSpacing": round(p["leading"] * 100, 1), "spaceAbove": pt(0),
                   "spaceBelow": pt(p["para_space_pt"]), "avoidWidowAndOrphan": True,
                   "indentFirstLine": pt(p["first_line_indent_em"] * body)}
    font = p["font_gdoc"]
    out = {"NORMAL_TEXT": dict(
        para=normal_para,
        text={"fontSize": pt(body), "weightedFontFamily": {"fontFamily": font}})}
    for name, level in HEADINGS.items():
        size = p[f"h{level}_pt"]
        para = {"lineSpacing": round(p["heading_leading"] * 100, 1),
                "spaceAbove": pt(0 if level == 1 else size * p["heading_above_em"]),
                "spaceBelow": pt(size * p["heading_below_em"]), "keepWithNext": True,
                "keepLinesTogether": True, "avoidWidowAndOrphan": True, "indentFirstLine": pt(0)}
        if level == 1 and p["h1_align"] == "center":
            para["alignment"] = "CENTER"
        text = {"fontSize": pt(size), "weightedFontFamily": {"fontFamily": font}, "bold": True}
        if p["kind"] == "academic" and level == 3:   # APA level 3: bold italic
            text["italic"] = True
        out[name] = dict(para=para, text=text)
    return out


def _mask(prefix, d):
    return [f"{prefix}.{k}" for k in d]


def named_style_requests(tg, tab_id):
    reqs = []
    for name, t in tg.items():
        fields = ["paragraphStyle"] + _mask("paragraphStyle", t["para"]) + \
                 ["textStyle"] + _mask("textStyle", t["text"])
        r = {"updateNamedStyle": {"namedStyle": {"namedStyleType": name, "paragraphStyle": t["para"],
                                                 "textStyle": t["text"]}, "fields": ",".join(fields)}}
        if tab_id:
            r["updateNamedStyle"]["tabId"] = tab_id
        reqs.append((None, r))
    return reqs


def _tabs(doc):
    """Yield (tab_id or None, body content list)."""
    def walk(tabs):
        for t in tabs:
            yield t["tabProperties"]["tabId"], t.get("documentTab", {}).get("body", {}).get("content", [])
            yield from walk(t.get("childTabs", []))
    if doc.get("tabs"):
        yield from walk(doc["tabs"])
    else:
        yield None, doc.get("body", {}).get("content", [])


def _para_info(el):
    p = el["paragraph"]
    runs, text, has_obj = [], "", False
    for e in p.get("elements", []):
        if "textRun" in e:
            c = e["textRun"]["content"]
            runs.append((e["startIndex"], e["endIndex"], c, e["textRun"].get("textStyle", {})))
            text += c
        else:
            has_obj = True  # inline object, page break, footnote ref, person, etc.
    fonts = [r[3].get("weightedFontFamily", {}).get("fontFamily", "") for r in runs if r[2].strip()]
    return dict(start=el["startIndex"], end=el["endIndex"], text=text, runs=runs, has_obj=has_obj,
                style=p.get("paragraphStyle", {}), named=p.get("paragraphStyle", {}).get("namedStyleType", "NORMAL_TEXT"),
                bullet="bullet" in p, mono=bool(fonts) and all(MONO.search(f) for f in fonts))


def _differs(have, want):
    for k, v in want.items():
        if k in have and have[k] != v:
            return True
    return False


def plan(doc, preset):
    tg = targets(preset)
    reqs, report = [], []   # reqs: (sortkey or None, request)
    counts = dict(named_styles=0, para_styles=0, text_styles=0, deleted_empty=0, deleted_indent=0)
    for tab_id, content in _tabs(doc):
        reqs += named_style_requests(tg, tab_id)
        counts["named_styles"] += len(tg)
        rng = lambda s, e: {"startIndex": s, "endIndex": e, **({"tabId": tab_id} if tab_id else {})}
        last_end = max((el.get("endIndex", 0) for el in content), default=0)
        prev_heading = False
        in_refs = False
        for i, el in enumerate(content):
            if "paragraph" not in el:
                prev_heading = False
                continue
            pi = _para_info(el)
            prev_el = content[i - 1] if i else None
            next_el = content[i + 1] if i + 1 < len(content) else None
            is_empty = (not pi["has_obj"]) and pi["text"].strip() == "" and not pi["bullet"]
            near_table = any(x is not None and "table" in x for x in (prev_el, next_el))
            if is_empty:
                if pi["end"] == last_end or near_table:
                    report.append(f"kept empty paragraph at {pi['start']} (last paragraph or next to a table)")
                else:
                    reqs.append(((pi["start"], 2), {"deleteContentRange": {"range": rng(pi["start"], pi["end"])}}))
                    counts["deleted_empty"] += 1
                continue
            if pi["has_obj"]:
                report.append(f"skipped paragraph at {pi['start']} (inline object)")
                continue
            named, stripped = pi["named"], pi["text"].strip()
            if named in ("TITLE", "SUBTITLE") or (named.startswith("HEADING_") and named not in HEADINGS):
                report.append(f"{named} at {pi['start']}: not normalized (use HEADING_1 to HEADING_3, max 3 levels)")
                continue
            letters = re.sub(r"[^A-Za-z]", "", stripped)
            if named in HEADINGS:
                if len(letters) >= 4 and letters.isupper():
                    report.append(f"ALL CAPS heading at {pi['start']}: \"{stripped[:40]}\"")
                if prev_heading:
                    report.append(f"stacked headings at {pi['start']}")
            prev_heading = named in HEADINGS
            if named in HEADINGS:
                in_refs = bool(REF_HEADING.match(stripped))
            if named not in tg:
                continue
            if named == "NORMAL_TEXT" and not pi["bullet"]:
                if TYPED_MARK.match(pi["text"]):
                    report.append(f"typed bullet or number at {pi['start']}: \"{stripped[:30]}\" (convert to a real list)")
                if (pi["runs"] and all(r[3].get("bold") for r in pi["runs"] if r[2].strip())
                        and len(stripped) < 80 and next_el is not None and "paragraph" in next_el):
                    report.append(f"bold-only paragraph at {pi['start']} looks like a heading: \"{stripped[:40]}\"")
            want_para = dict(tg[named]["para"])
            if pi["bullet"]:
                for k in ("indentFirstLine", "indentStart"):
                    want_para.pop(k, None)
                want_para["spaceBelow"] = pt(2)
            hanging = False
            if in_refs and named == "NORMAL_TEXT" and not pi["bullet"] and P.get(preset)["hanging_refs"]:
                # References / Works Cited: 0.5 in hanging indent (first line at the margin, the rest 0.5 in in).
                # Docs ignores a negative text-indent on import, so this is set here, and always.
                want_para = dict(want_para, indentStart=pt(36), indentFirstLine=pt(0))
                hanging = True
            if (hanging or _differs(pi["style"], want_para)) and not pi["mono"]:
                keys = list(want_para)
                reqs.append(((pi["start"], 0), {"updateParagraphStyle": {
                    "paragraphStyle": want_para, "fields": ",".join(keys), "range": rng(pi["start"], pi["end"])}}))
                counts["para_styles"] += 1
            if not pi["mono"]:
                want_text = tg[named]["text"]
                for s, e, c, ts in pi["runs"]:
                    if not c.strip() or MONO.search(ts.get("weightedFontFamily", {}).get("fontFamily", "")):
                        continue
                    if _differs(ts, want_text):
                        reqs.append(((s, 1), {"updateTextStyle": {
                            "textStyle": want_text, "fields": ",".join(want_text), "range": rng(s, e)}}))
                        counts["text_styles"] += 1
            m = re.match(r"^[ \t ]+(?=\S)", pi["text"])
            if m and not pi["bullet"] and not pi["mono"]:
                reqs.append(((pi["start"], 2), {"deleteContentRange": {
                    "range": rng(pi["start"], pi["start"] + len(m.group(0)))}}))
                counts["deleted_indent"] += 1
    named_first = [r for k, r in reqs if k is None]
    indexed = sorted((x for x in reqs if x[0] is not None), key=lambda x: (-x[0][0], x[0][1]))
    return named_first + [r for _, r in indexed], report, counts


def build(doc, preset="report"):
    if not doc.get("revisionId"):
        raise SystemExit("no revisionId in the JSON: read the doc with documents.get first")
    requests, report, counts = plan(doc, preset)
    return {"requests": requests, "writeControl": {"requiredRevisionId": doc["revisionId"]}}, report, counts


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("doc_json")
    ap.add_argument("--preset", default="report", choices=list(P.PRESETS))
    ap.add_argument("-o", "--out", help="write the batchUpdate body here")
    a = ap.parse_args()
    body, report, counts = build(json.load(open(a.doc_json, encoding="utf-8")), a.preset)
    out = a.out or os.path.splitext(a.doc_json)[0] + ".batch.json"
    json.dump(body, open(out, "w"), indent=1)
    print(f"wrote {out}: {len(body['requests'])} requests "
          + ", ".join(f"{k} {v}" for k, v in counts.items()))
    for line in report:
        print("  report:", line)
    print("  not possible via the API: page numbers (Docs Help: 'Use headers, footers, page numbers & footnotes').")
    print("  UI route for named styles: Format > Paragraph styles > Normal text or Heading > Update to match.")


if __name__ == "__main__":
    main()
