#!/usr/bin/env python3
"""Route B independent oracle for gmi-833-ab-terminology-harness-v1.

Materially independent of ab_harness_v1.py:
  * imports nothing from it;
  * never builds a column dict - it walks each raw table line with its own
    character-level splitter and searches the WHOLE line, so its failure mode
    is cell-boundary permissiveness where route A's is column misalignment;
  * counts crosswalk rows and banned rows by its own line grammar;
  * normalizes with its own translation table rather than route A's regex.
Only the requirements JSON (the specification) is shared.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
PARENT = os.path.join(REPO, "research", "gmi-833-tranche-ab-ac-lit")
CROSSWALK = os.path.join(PARENT, "GMI_TERMINOLOGY_CROSSWALK_V2.md")
BANNED = os.path.join(PARENT, "BANNED_PAPER_TERMS_V1.md")
EXTENSION = os.path.join(HERE, "AB_CROSSWALK_EXTENSION_V1.md")
REQS = os.path.join(HERE, "AB_ROW_REQUIREMENTS_V1.json")

DROP = "*`_"
HYPHEN_TO_SPACE = True
FOLD = {"—": "-", "–": "-", "→": "->"}


def flatten(s):
    out = []
    for ch in s:
        ch = FOLD.get(ch, ch)
        if ch in DROP:
            continue
        if ch == "-" and HYPHEN_TO_SPACE:
            out.append(" ")
            continue
        out.append(ch.lower())
    txt = "".join(out)
    while "  " in txt:
        txt = txt.replace("  ", " ")
    return txt.strip()


def split_pipes(line):
    """Character-level splitter: no regex, no strip("|") shortcut."""
    fields = []
    buf = []
    for ch in line:
        if ch == "|":
            fields.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    fields.append("".join(buf).strip())
    if fields and fields[0] == "":
        fields = fields[1:]
    if fields and fields[-1] == "":
        fields = fields[:-1]
    return fields


def indexed_rows(path):
    """Rows whose first field is all digits. Returns (legacy_name, whole_line)."""
    rows = []
    if not os.path.exists(path):
        return rows
    for raw in open(path).read().split("\n"):
        if not raw.startswith("|"):
            continue
        f = split_pipes(raw)
        if len(f) < 2:
            continue
        head = f[0]
        if not head or not all(c in "0123456789" for c in head):
            continue
        # exclude the legacy cell (f[1]) from the searchable blob for the same
        # reason route A does: a legacy name must not discharge its own audit.
        rows.append((flatten(f[1]), flatten(" | ".join(f[2:]))))
    return rows


def hit(line, req):
    if isinstance(req, dict):
        return any(flatten(a) in line for a in req["any_of"])
    return flatten(req) in line


def banned_rows(path):
    n = 0
    withrep = 0
    for raw in open(path).read().split("\n"):
        if not raw.startswith("|"):
            continue
        f = split_pipes(raw)
        if len(f) != 4:
            continue
        if f[0].startswith("---") or f[0] == "banned term":
            continue
        n += 1
        if f[2]:
            withrep += 1
    return n, withrep


def run():
    spec = json.load(open(REQS))
    prows = indexed_rows(CROSSWALK)
    erows = indexed_rows(EXTENSION)
    bt, bwr = banned_rows(BANNED)
    out_rows = []
    for s in spec["rows"]:
        if not s["evidence_kind"].startswith("CROSSWALK_ROW"):
            continue
        names = s["crosswalk_term"]
        names = names if isinstance(names, list) else [names]
        wanted = set(flatten(n) for n in names)
        pl = " ~ ".join(l for nm, l in prows if nm in wanted)
        el = " ~ ".join(l for nm, l in erows if nm in wanted)
        both = pl + " ~ " + el
        reqs = s["required_terms"]
        out_rows.append({
            "row_id": s["row_id"],
            "parent_rows_found": len([1 for nm, _ in prows if nm in wanted]),
            "extension_rows_found": len([1 for nm, _ in erows if nm in wanted]),
            "parent_covered": sum(1 for r in reqs if hit(pl, r)),
            "total_covered": sum(1 for r in reqs if hit(both, r)),
            "required": len(reqs),
        })
    return {
        "schema": "GMI_AB_HARNESS_RESULT_V1",
        "route": "B",
        "crosswalk_rows": len(prows),
        "extension_rows": len(erows),
        "banned_terms": bt,
        "banned_with_replacement": bwr,
        "required_terms_total": sum(r["required"] for r in out_rows),
        "parent_covered_total": sum(r["parent_covered"] for r in out_rows),
        "total_covered_total": sum(r["total_covered"] for r in out_rows),
        "rows": out_rows,
    }


def main(argv):
    print(json.dumps(run(), indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
