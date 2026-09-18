# -*- coding: utf-8 -*-
"""RA-1 route B -- materially independent citation oracle.

Route A resolves each cited field by walking a dot path through the parsed
receipt and checks the forbidden set by reading specific known keys.

Route B instead:

  * recomputes every blob sha from the raw bytes with its own framing;
  * flattens each receipt into a complete {dot-path -> canonical-json} map by
    exhaustive recursive descent, then does plain dictionary lookup -- no path
    walking, so a path that route A mis-walks cannot agree by accident;
  * builds each parent's forbidden set by collecting EVERY string value
    anywhere in the receipt whose key name begins with "forbidden", rather
    than reading a fixed key list;
  * re-indexes the pinned rows by (comment_id, anchor) and compares row text by
    exact membership in that group.

It imports nothing from citation_audit_v1.py.  Stdlib only.

    python3 -I -B independent_oracle_v1.py
"""

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))


def sha(path):
    raw = open(path, "rb").read()
    header = ("blob %d" % len(raw)).encode("ascii") + b"\x00"
    return hashlib.sha1(header + raw).hexdigest()


def flatten(obj, prefix=""):
    out = {prefix: json.dumps(obj, sort_keys=True)} if prefix else {}
    if isinstance(obj, dict):
        for k in obj:
            out.update(flatten(obj[k], (prefix + "." + k) if prefix else k))
    elif isinstance(obj, list):
        for i, x in enumerate(obj):
            out.update(flatten(x, (prefix + "." + str(i)) if prefix else str(i)))
    return out


def forbidden_strings(obj, key_is_forbidden=False, acc=None):
    if acc is None:
        acc = set()
    if isinstance(obj, dict):
        for k, val in obj.items():
            forbidden_strings(val, key_is_forbidden or str(k).startswith("forbidden"), acc)
    elif isinstance(obj, list):
        for x in obj:
            forbidden_strings(x, key_is_forbidden, acc)
    elif isinstance(obj, str) and key_is_forbidden:
        acc.add(obj)
    return acc


def main():
    table = json.load(open(os.path.join(HERE, "CITATION_TABLE_V1.json")))
    smap = json.load(open(os.path.join(HERE, "AGAH_STRUCTURAL_MAP_V1.json")))
    rows = json.load(open(os.path.join(HERE, "AGAH_ROWS_V1.json")))

    by_anchor = {}
    for r in rows:
        by_anchor.setdefault((r["cid"], r["anchor"]), set()).add(r["row"])

    pin_bad = field_bad = value_bad = forb_bad = row_bad = status_bad = 0
    fields_checked = 0
    pkgs = set()
    flat_cache = {}
    forb_cache = {}

    for rep in table["replacements"]:
        grp = by_anchor.get((rep["comment_id"], rep["anchor"]))
        if grp is None or rep["old"] not in grp:
            row_bad += 1
        for c in rep["citations"]:
            pkgs.add(c["package"])
            full = os.path.join(REPO, c["receipt_path"])
            if not os.path.exists(full) or sha(full) != c["blob_sha"]:
                pin_bad += 1
                continue
            if full not in flat_cache:
                doc = json.load(open(full))
                flat_cache[full] = flatten(doc)
                forb_cache[full] = forbidden_strings(doc)
                st = doc.get("status", doc.get("verdict"))
                if isinstance(st, str) and st != "GREEN":
                    status_bad += 1
            flat = flat_cache[full]
            for path, pinned in sorted(c["fields"].items()):
                fields_checked += 1
                if path not in flat:
                    field_bad += 1
                elif flat[path] != pinned:
                    value_bad += 1
            if rep["row_meaning_token"] in forb_cache[full]:
                forb_bad += 1

    closed = [r for r in smap["rows"] if r["disposition"] != "OPEN"]
    out = {
        "schema": "AGAH_ORACLE_RESULT_V1",
        "route": "EXHAUSTIVE_FLATTEN_PLUS_KEY_PREFIX_FORBIDDEN_HARVEST",
        "replacements": len(table["replacements"]),
        "distinct_packages": len(pkgs),
        "fields_checked": fields_checked,
        "pin_failures": pin_bad,
        "field_failures": field_bad,
        "value_failures": value_bad,
        "forbidden_conflicts": forb_bad,
        "row_text_failures": row_bad,
        "status_failures": status_bad,
        "rows_total": len(smap["rows"]),
        "rows_closed": len(closed),
        "rows_open": len(smap["rows"]) - len(closed),
    }
    with open(os.path.join(HERE, "ORACLE_RESULT_V1.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps(out, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
