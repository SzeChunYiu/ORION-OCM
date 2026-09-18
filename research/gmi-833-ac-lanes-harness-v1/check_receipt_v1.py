#!/usr/bin/env python3
"""Build (`--write`) or verify the AC receipt against a live two-route run."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import ac_lanes_harness_v1 as A       # noqa: E402
import independent_ac_oracle_v1 as B  # noqa: E402

RECEIPT = HERE / "RESULT_V1.json"


def build():
    a = A.main()
    b = B.derive()
    out = dict(a)
    out["schema"] = "GMI_833_AC_LANES_RESULT_V1"
    out["package"] = "gmi-833-ac-lanes-harness-v1"
    out["issue"] = 833
    out["rows_closed"] = ["AC01", "AC03", "AC04", "AC06"]
    out["rows_left_open"] = ["AC02", "AC05", "AC07", "AC08", "AC09"]
    out["route_b"] = b
    out["route_agreement"] = {
        "compared_by": "count equality plus set equality on every row-id set",
        "ac06_missing_sets_identical":
            set(a["AC06_parent_record"]["without_parent_in_parent_artifact"])
            == set(b["ac06_missing_in_parent_artifact"]),
        "entries_per_lane_identical":
            a["AC01_lane_coverage"]["entries_per_lane"] == b["entries_per_lane"],
        "status_identical":
            a["AC06_parent_record"]["verification_status_in_parent_artifact"]
            == b["ac06_verification_status"],
    }
    out["named_results"] = {
        "ACL-1": "the eleven lanes the AC01 row names bind one-to-one to the "
                 "eleven registered lanes, in both directions",
        "ACL-2": "every EXACT crosswalk row adopts a canonical term",
        "ACL-3": "every multi-synonym row resolves to one primary paper term",
        "ACL-4": "every crosswalk row carries an earliest-or-strongest parent "
                 "record, with the verification split disclosed and AC05 out of scope",
        "ACL-5": "AC07 is not earned: four of its six kinds have no discriminator "
                 "among the fields registered on main",
    }
    out["forbidden_promotions"] = [
        "CITATIONS_VERIFIED", "CITATION_BACKED", "AC05_CLOSED",
        "LITERATURE_SATURATED", "ALL_PARENTS_EXHAUSTED", "NO_PARENT_MISSED",
        "WHAT_IS_ACTUALLY_NEW_COMPLETE", "PARENT_IS_EARLIEST", "ANALYTIC_PROOF",
    ]
    return out


def main(argv):
    live = build()
    if "--write" in argv:
        RECEIPT.write_text(json.dumps(live, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
        print("wrote %s" % RECEIPT.name)
        return 0
    if not RECEIPT.exists():
        print("MISSING RECEIPT")
        return 1
    stored = json.loads(RECEIPT.read_text(encoding="utf-8"))
    diffs = [k for k in ("AC01_lane_coverage", "AC03_canonical_preference",
                         "AC04_synonyms_and_primary_term", "AC06_parent_record",
                         "AC07_feasibility", "guard", "null", "route_b",
                         "route_agreement", "hostiles")
             if stored.get(k) != live.get(k)]
    if diffs:
        print("RECEIPT DRIFT in: %s" % ", ".join(diffs))
        return 1
    print("receipt matches the live two-route run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
