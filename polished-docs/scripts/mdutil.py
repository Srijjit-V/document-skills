"""Small Markdown fixes shared by the PDF and Google Docs converters."""
import re

ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+\S")
FENCE = re.compile(r"^\s*(```|~~~)")


def fix_list_starts(md):
    """Insert the blank line a list needs after a plain text line.

    CommonMark lets a bullet list interrupt a paragraph; Python-Markdown (and some
    importers) do not, so the bullets print as typed dashes. AI output often writes
    an entry line and its bullets with no blank line between them. A numbered list
    may interrupt a paragraph only when it starts at 1, as in CommonMark.
    """
    out, in_code, prev_kind = [], False, "blank"   # blank | text | item
    for line in md.split("\n"):
        if FENCE.match(line):
            in_code = not in_code
            out.append(line)
            prev_kind = "text"
            continue
        if in_code:
            out.append(line)
            continue
        m = ITEM.match(line)
        if not line.strip():
            kind = "blank"
        elif m:
            kind = "item"
            starts_list = bool(re.match(r"^\s*([-*+]|1[.)])\s", line))
            if prev_kind == "text" and starts_list and not m.group(1):
                out.append("")
        elif prev_kind == "item" and line.startswith((" ", "\t")):
            kind = "item"       # indented continuation of a list item
        else:
            kind = "text"
        out.append(line)
        prev_kind = kind
    return "\n".join(out)


REF_HEADING = re.compile(r"^(references|works cited|bibliography)$", re.I)


def mark_references(body):
    """Give every paragraph after a References / Works Cited heading the class 'ref' (hanging indent)."""
    out, in_refs = [], False
    for chunk in re.split(r"(<h[1-6][^>]*>.*?</h[1-6]>)", body, flags=re.S):
        if re.match(r"<h[1-6]", chunk):
            in_refs = bool(REF_HEADING.match(re.sub(r"<[^>]+>", "", chunk).strip()))
        elif in_refs:
            chunk = chunk.replace("<p>", '<p class="ref">')
        out.append(chunk)
    return "".join(out)
