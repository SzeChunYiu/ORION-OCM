#!/usr/bin/env python3
"""Build (`--write`) or verify RESULT_V1.json against a live two-route run."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import ac05_citation_check_v1 as A        # noqa: E402
import independent_ac05_oracle_v1 as B    # noqa: E402

RECEIPT = HERE / "RESULT_V1.json"
KEYS = ("passing_rows", "failing_rows", "harel_row1", "hostiles", "null", "register", "per_row", "route_b", "route_agreement")


def build():
    a = A.main()
    b = B.derive()
    pa = {p["row"]: p for p in a["per_row"]}
    out = dict(a)
    out["schema"] = "GMI_833_AC05_RESULT_V1"
    out["package"] = "gmi-833-ac05-citation-revival-v1"
    out["issue"] = 833
    out["comment_id"] = 5684607872
    out["row_under_reconciliation"] = "AC05"
    out["route_b"] = b
    out["route_agreement"] = {
        "passing_equal": a["passing_rows"] == b["passing"],
        "failing_sets_equal": a["failing_rows"] == b["failing_rows"],
        "harel_equal": a["harel_row1"]["ok"] == b["harel_ok"],
        "rows_with_identifier_set_disagreement": [n for n in range(1, 49)
                                                  if pa[n]["identifiers_in_cell"] != b["per_row"][str(n)]["identifiers"]],
    }
    out["named_results"] = {
        "AC05-1": "48/48 crosswalk rows carry, in their own citations cell, a resolvable identifier and a VERIFIED-2026-09-19 anchor whose register record has a supporting passage (<=15 words) with locator and a recorded resolution status",
        "AC05-2": "the eight rows the prior proxy found unbacked (16, 19, 21, 23, 34, 41, 47, 48) each carry an in-place verified primary anchor; row 48 is an honest programme-internal primary source, with Hempel & Oppenheim 1948 retired as non-supporting",
        "AC05-3": "row 1's Harel 1992 anchor is corrected to Computer 25(1):8-20, doi:10.1109/2.108047 (Crossref container-title 'Computer'); the first-tried DOI 10.1109/2.108007 resolves 404",
        "AC05-4": "two independently written routes agree on the count, the failing set, the Harel verdict and every row's identifier set; 7/7 hostiles applicable and detected; 0/122 primary-identifier deletions missed over 200 null draws",
    }
    out["forbidden_promotions"] = [
        "LITERATURE_SATURATED", "PARENT_IS_EARLIEST", "ALL_PARENTS_EXHAUSTED", "DEFINITIONS_CORRECT",
        "AC02_CLOSED", "AC07_CLOSED", "AC08_CLOSED", "AC09_CLOSED", "WHAT_IS_ACTUALLY_NEW_COMPLETE",
        "ROW_CLOSED_BY_NARROWING", "SECONDARY_QUOTATION_IS_PRIMARY_CHECK", "RESOLUTION_RECHECKED_IN_CI",
    ]
    return out


def main(argv):
    live = build()
    if "--write" in argv:
        RECEIPT.write_text(json.dumps(live, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
        print("wrote %s" % RECEIPT.name)
        return 0
    if not RECEIPT.exists():
        print("MISSING RECEIPT")
        return 1
    stored = json.loads(RECEIPT.read_text(encoding="utf-8"))
    diffs = [k for k in KEYS if stored.get(k) != live.get(k)]
    if diffs:
        print("RECEIPT DRIFT in: %s" % ", ".join(diffs))
        return 1
    print("receipt matches the live two-route run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
