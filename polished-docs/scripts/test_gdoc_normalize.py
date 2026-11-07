"""Unit tests for gdoc_normalize on SYNTHETIC Docs JSON.

These tests never touch a real Google Doc. They check the planner's logic and
validate every emitted request against Google's own Docs API v1 discovery
schema (fixtures/docs_v1_discovery.json, revision 20261028), so wrong field
names, enum values, or field-mask paths fail here.
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gdoc_normalize as G  # noqa: E402

SCHEMAS = json.load(open(os.path.join(HERE, "fixtures", "docs_v1_discovery.json")))["schemas"]


# ---- schema validation -------------------------------------------------
def _resolve(s):
    while "$ref" in s:
        s = SCHEMAS[s["$ref"]]
    return s


def validate(obj, schema, path="$"):
    s = _resolve(schema)
    errs, t = [], s.get("type")
    if "enum" in s and obj not in s["enum"]:
        errs.append(f"{path}: {obj!r} not in enum")
    if t == "object" or "properties" in s:
        if not isinstance(obj, dict):
            return [f"{path}: expected object"]
        props = s.get("properties", {})
        for k, v in obj.items():
            if k not in props:
                if "additionalProperties" not in s:
                    errs.append(f"{path}.{k}: unknown property")
            else:
                errs += validate(v, props[k], f"{path}.{k}")
    elif t == "array":
        if not isinstance(obj, list):
            return [f"{path}: expected array"]
        for i, v in enumerate(obj):
            errs += validate(v, s["items"], f"{path}[{i}]")
    elif t == "string" and not isinstance(obj, str):
        errs.append(f"{path}: expected string")
    elif t in ("number", "integer") and (isinstance(obj, bool) or not isinstance(obj, (int, float))):
        errs.append(f"{path}: expected number")
    elif t == "boolean" and not isinstance(obj, bool):
        errs.append(f"{path}: expected boolean")
    return errs


def mask_errors(fields, schema_name):
    errs = []
    for f in fields.split(","):
        if f == "*":
            continue
        s = SCHEMAS[schema_name]
        for part in f.split("."):
            s = _resolve(s)
            if part not in s.get("properties", {}):
                errs.append(f"mask path {f!r}: {part!r} not in schema")
                break
            s = s["properties"][part]
    return errs


MASK_TARGET = {"updateParagraphStyle": ("paragraphStyle", "ParagraphStyle"),
               "updateTextStyle": ("textStyle", "TextStyle"),
               "updateNamedStyle": ("namedStyle", "NamedStyle")}


def check_body(body):
    errs = validate(body, {"$ref": "BatchUpdateDocumentRequest"})
    for r in body["requests"]:
        (name, args), = r.items()
        if name in MASK_TARGET:
            errs += mask_errors(args["fields"], MASK_TARGET[name][1])
    return errs


# ---- synthetic doc builder --------------------------------------------
class B:
    def __init__(self, tabs=False):
        self.i, self.content, self.tabs = 1, [{"startIndex": 0, "endIndex": 1, "sectionBreak": {}}], tabs
        self.table_range = None
        self.obj_range = None

    def para(self, text, named="NORMAL_TEXT", bullet=False, bold=False, font=None, size=None, pstyle=None, obj=False):
        ts = {}
        if bold:
            ts["bold"] = True
        if font:
            ts["weightedFontFamily"] = {"fontFamily": font}
        if size:
            ts["fontSize"] = {"magnitude": size, "unit": "PT"}
        s, e = self.i, self.i + len(text) + (1 if obj else 0)
        els = [{"startIndex": s, "endIndex": s + len(text), "textRun": {"content": text, "textStyle": ts}}]
        if obj:
            els.append({"startIndex": s + len(text), "endIndex": e, "inlineObjectElement": {"inlineObjectId": "x"}})
        ps = {"namedStyleType": named, **(pstyle or {})}
        el = {"startIndex": s, "endIndex": e, "paragraph": {"elements": els, "paragraphStyle": ps}}
        if bullet:
            el["paragraph"]["bullet"] = {"listId": "l"}
        if obj:
            self.obj_range = (s, e)
        self.content.append(el)
        self.i = e
        return (s, e)

    def table(self):
        s = self.i
        inner = {"startIndex": s + 3, "endIndex": s + 7, "paragraph": {
            "elements": [{"startIndex": s + 3, "endIndex": s + 7, "textRun": {"content": "cel\n", "textStyle": {
                "weightedFontFamily": {"fontFamily": "Arial"}}}}], "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"}}}
        e = s + 8
        self.content.append({"startIndex": s, "endIndex": e, "table": {"tableRows": [
            {"tableCells": [{"content": [inner]}]}]}})
        self.table_range, self.i = (s, e), e

    def doc(self, rev="rev123"):
        body = {"content": self.content}
        if self.tabs:
            return {"revisionId": rev, "tabs": [{"tabProperties": {"tabId": "t.0", "index": 0},
                                                   "documentTab": {"body": body}}]}
        return {"revisionId": rev, "body": body}


def sample():
    b = B()
    b.para("Title\n", "HEADING_1", size=20)
    b.para("\n")                                        # blank spacing after a heading
    b.para("    Typed indent paragraph.\n", pstyle={"spaceBelow": {"magnitude": 0, "unit": "PT"}})
    b.para("\n"), b.para("\n")                          # stacked blanks
    b.para("Run with Arial.\n", font="Arial", size=12)
    b.para("item\n", bullet=True, pstyle={"spaceBelow": {"magnitude": 10, "unit": "PT"}})
    b.para("• typed bullet\n")
    b.para("Fake heading\n", bold=True)
    b.para("Body after fake heading.\n")
    b.para("\n")                                        # empty before a table: kept
    b.table()
    b.para("See image\n", obj=True)
    b.para("ALL CAPS HEADING\n", "HEADING_2", pstyle={"lineSpacing": 100})
    b.para("Next heading\n", "HEADING_2")
    b.para("Deep\n", "HEADING_4")
    b.para("code = 1\n", font="Courier New")
    b.para("\n")                                        # last paragraph: kept
    return b


class Normalize(unittest.TestCase):
    def setUp(self):
        self.b = sample()
        self.body, self.report, self.counts = G.build(self.b.doc(), "report")
        self.reqs = self.body["requests"]

    def test_schema_valid(self):
        self.assertEqual(check_body(self.body), [])

    def test_write_control_guard(self):
        self.assertEqual(self.body["writeControl"], {"requiredRevisionId": "rev123"})

    def test_named_styles_come_first(self):
        names = [list(r)[0] for r in self.reqs[:4]]
        self.assertEqual(names, ["updateNamedStyle"] * 4)
        kinds = [r["updateNamedStyle"]["namedStyle"]["namedStyleType"] for r in self.reqs[:4]]
        self.assertEqual(kinds, ["NORMAL_TEXT", "HEADING_1", "HEADING_2", "HEADING_3"])

    def test_headings_keep_with_next(self):
        h = [r["updateNamedStyle"]["namedStyle"]["paragraphStyle"] for r in self.reqs[1:4]]
        self.assertTrue(all(p["keepWithNext"] for p in h))

    def test_highest_index_first(self):
        starts = []
        for r in self.reqs[4:]:
            (name, args), = r.items()
            starts.append(args["range"]["startIndex"])
        self.assertEqual(starts, sorted(starts, reverse=True))

    def test_never_touches_table_or_inline_object(self):
        ts, te = self.b.table_range
        os_, oe = self.b.obj_range
        for r in self.reqs[4:]:
            (name, args), = r.items()
            s, e = args["range"]["startIndex"], args["range"]["endIndex"]
            self.assertFalse(s < te and e > ts, f"{name} overlaps the table")
            self.assertFalse(s < oe and e > os_, f"{name} overlaps the inline object paragraph")

    def test_deletes(self):
        dels = [r["deleteContentRange"]["range"] for r in self.reqs if "deleteContentRange" in r]
        self.assertEqual(len(dels), 4)          # 3 empty paragraphs + 1 typed indent
        last_end = self.b.content[-1]["endIndex"]
        self.assertTrue(all(d["endIndex"] < last_end for d in dels))   # never the final newline
        self.assertEqual(sorted(d["endIndex"] - d["startIndex"] for d in dels), [1, 1, 1, 4])
        self.assertEqual(self.counts["deleted_empty"], 3)
        self.assertEqual(self.counts["deleted_indent"], 1)

    def test_direct_formatting_overrides_fixed(self):
        kinds = [list(r)[0] for r in self.reqs[4:]]
        self.assertIn("updateParagraphStyle", kinds)
        self.assertIn("updateTextStyle", kinds)
        texts = [r["updateTextStyle"]["textStyle"] for r in self.reqs if "updateTextStyle" in r]
        self.assertTrue(any(t.get("fontSize", {}).get("magnitude") == 11.0 for t in texts))

    def test_report_only_items(self):
        r = "\n".join(self.report)
        for needle in ("typed bullet", "bold-only paragraph", "ALL CAPS heading", "stacked headings",
                       "HEADING_4", "inline object", "kept empty paragraph"):
            self.assertIn(needle, r)

    def test_code_font_left_alone(self):
        for r in self.reqs[4:]:
            (name, args), = r.items()
            if name == "updateTextStyle":
                self.assertNotIn("Courier", json.dumps(args))

    def test_conforming_doc_only_needs_named_styles(self):
        tg = G.targets("report")
        b = B()
        b.para("Heading\n", "HEADING_1", pstyle=dict(tg["HEADING_1"]["para"]))
        b.para("Body text here.\n", pstyle=dict(tg["NORMAL_TEXT"]["para"]))
        body, _, c = G.build(b.doc(), "report")
        self.assertEqual(len(body["requests"]), 4)
        self.assertEqual((c["para_styles"], c["text_styles"], c["deleted_empty"]), (0, 0, 0))

    def test_tabs_add_tab_id(self):
        b = sample()
        b.tabs = True
        body, _, _ = G.build(b.doc(), "report")
        for r in body["requests"]:
            (name, args), = r.items()
            if name == "updateNamedStyle":
                self.assertEqual(args["tabId"], "t.0")
            else:
                self.assertEqual(args["range"]["tabId"], "t.0")
        self.assertEqual(check_body(body), [])

    def test_missing_revision_id_refuses(self):
        d = self.b.doc()
        del d["revisionId"]
        with self.assertRaises(SystemExit):
            G.build(d, "report")

    def test_book_preset_sets_indent_not_space(self):
        body, _, _ = G.build(self.b.doc(), "book")
        normal = body["requests"][0]["updateNamedStyle"]["namedStyle"]["paragraphStyle"]
        self.assertEqual(normal["spaceBelow"]["magnitude"], 0.0)
        self.assertEqual(normal["indentFirstLine"]["magnitude"], 16.5)
        self.assertEqual(check_body(body), [])

    def test_schema_validator_catches_bad_names(self):
        bad = {"requests": [{"updateParagraphStyle": {"paragraphStyle": {"lineSpace": 135},
                                                      "fields": "lineSpace", "range": {"startIndex": 1, "endIndex": 2}}}]}
        errs = check_body(bad)
        self.assertTrue(any("lineSpace" in e for e in errs))


    def test_every_preset_yields_schema_valid_requests(self):
        import presets as P
        for name in P.PRESETS:
            body, _, _ = G.build(sample().doc(), name)
            self.assertEqual(check_body(body), [], name)

    def test_references_get_a_hanging_indent_only_in_academic(self):
        b = B()
        b.para("Body paragraph.\n")
        b.para("References\n", "HEADING_2")
        b.para("Rivera, M. (2021). A title.\n")
        b.para("Chen, L. (2022). Another title.\n")
        body, _, _ = G.build(b.doc(), "academic")
        hang = [r["updateParagraphStyle"] for r in body["requests"]
                if "updateParagraphStyle" in r and r["updateParagraphStyle"]["paragraphStyle"].get("indentStart")]
        self.assertEqual(len(hang), 2)
        for h in hang:
            self.assertEqual(h["paragraphStyle"]["indentStart"]["magnitude"], 36.0)
            self.assertEqual(h["paragraphStyle"]["indentFirstLine"]["magnitude"], 0.0)
        self.assertEqual(check_body(body), [])
        plain, _, _ = G.build(b.doc(), "report")
        self.assertFalse(any(r.get("updateParagraphStyle", {}).get("paragraphStyle", {}).get("indentStart")
                             for r in plain["requests"]))

    def test_academic_targets_follow_apa(self):
        t = G.targets("academic")
        normal = t["NORMAL_TEXT"]
        self.assertEqual(normal["para"]["lineSpacing"], 200.0)
        self.assertEqual(normal["para"]["indentFirstLine"]["magnitude"], 36.0)
        self.assertEqual(normal["para"]["spaceBelow"]["magnitude"], 0.0)
        self.assertEqual(normal["text"]["weightedFontFamily"]["fontFamily"], "Times New Roman")
        self.assertEqual(t["HEADING_1"]["para"]["alignment"], "CENTER")
        self.assertTrue(t["HEADING_3"]["text"]["italic"])
        self.assertNotIn("italic", t["HEADING_2"]["text"])


if __name__ == "__main__":
    unittest.main()
