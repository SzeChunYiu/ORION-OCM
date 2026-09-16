#!/usr/bin/env python3
"""GMI #833 claim-discipline v1 — mechanical S1 scan (FREEZE_V1.md section 3).

Deterministic, stdlib-only. Reads THEOREM_SCORES_V1/V2 and classifies each of the
six discipline fields per object per the frozen scan rule. Emits GAP_REGISTER_V1.json.
Run: python3 -I -B scan_registers_v1.py  (byte-identical under -O)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(HERE)
FIELDS = [
    "scope_quantifiers",
    "assumptions",
    "falsifiers",
    "strongest_parents",
    "forbidden_extrapolations",
]
TOKENS = {
    "REGISTERED_IN_PACKAGE_DOCS",
    "REGISTERED_IN_PROSE_AT_CITED_PATH",
    "UNREGISTERED_IN_LEGACY_SOURCE",
}


def field_status(value):
    """S1 rule: STATED iff the score record carries field-specific content."""
    if isinstance(value, list):
        vals = [v.strip() for v in value if isinstance(v, str) and v.strip()]
        if not vals:
            return "UNSTATED_EMPTY"
        if all(v in TOKENS or v.startswith("REGISTERED_IN") for v in vals):
            if any(v == "UNREGISTERED_IN_LEGACY_SOURCE" for v in vals):
                return "UNSTATED_IN_SOURCE"
            return "POINTER_UNRESOLVED"
        return "STATED"
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return "UNSTATED_EMPTY"
        if s in TOKENS or s.startswith("REGISTERED_IN"):
            return "UNSTATED_IN_SOURCE" if s == "UNREGISTERED_IN_LEGACY_SOURCE" else "POINTER_UNRESOLVED"
        return "STATED"
    return "UNSTATED_EMPTY"


def main():
    v1 = json.load(open(os.path.join(RESEARCH, "gmi-833-maturity-rescore-v1", "THEOREM_SCORES_V1.json")))["records"]
    v2 = json.load(open(os.path.join(RESEARCH, "gmi-833-maturity-rescore-v2-v1", "THEOREM_SCORES_V2.json")))
    rows = []
    for e in v1:
        row = {
            "result_id": e["result_id"],
            "package": e["package"],
            "tranche": "U-V1",
            "source": "THEOREM_SCORES_V1.json",
        }
        for f in FIELDS:
            row[f] = field_status(e.get("scope_quantifier_class" if f == "scope_quantifiers" else f))
        rows.append(row)
    for e in v2:
        row = {
            "result_id": e["result_id"],
            "package": e["package"],
            "tranche": "U-LEGACY" if e["tranche"] == "LEGACY_173" else "U-ARRIVALS",
            "source": "THEOREM_SCORES_V2.json",
        }
        for f in FIELDS:
            row[f] = field_status(e.get("scope_quantifier_class" if f == "scope_quantifiers" else f))
        rows.append(row)
    rows.sort(key=lambda r: r["result_id"])
    counts = {f: {} for f in FIELDS}
    for r in rows:
        for f in FIELDS:
            counts[f][r[f]] = counts[f].get(r[f], 0) + 1
    out = {
        "schema": "GMI833_CLAIM_DISCIPLINE_GAP_REGISTER_V1",
        "scan_rule": "FREEZE_V1.md section 3 (S1 score-record status; S2 extraction resolves POINTER_UNRESOLVED during registration)",
        "objects": rows,
        "counts": counts,
        "object_count": len(rows),
    }
    path = os.path.join(HERE, "GAP_REGISTER_V1.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=False)
        fh.write("\n")
    print("objects scanned:", len(rows), "(U-V1 %d, U-LEGACY %d, U-ARRIVALS %d)" % (
        sum(1 for r in rows if r["tranche"] == "U-V1"),
        sum(1 for r in rows if r["tranche"] == "U-LEGACY"),
        sum(1 for r in rows if r["tranche"] == "U-ARRIVALS")))
    for f in FIELDS:
        print(f, json.dumps(counts[f], sort_keys=True))
    # U-NEW objects are S2-scanned at assembly (no score record exists for them).
    return 0


if __name__ == "__main__":
    sys.exit(main())
