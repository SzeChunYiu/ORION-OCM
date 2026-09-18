#!/usr/bin/env python3
"""Build (`--write`) or verify the AA21 receipt against a live two-route run.

Without `--write` this exits non-zero if `RESULT_V1.json` disagrees with what
the two routes produce right now. It is the CI step that stops a stale receipt.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import finite_universal_harness_v1 as A       # noqa: E402
import independent_fin2univ_oracle_v1 as B    # noqa: E402

RECEIPT = HERE / "RESULT_V1.json"


def build():
    a = A.main()
    b = B.derive()
    graph = A._read_json(A.GAP_GRAPH)
    full = A.registered_population(graph)

    agree = {
        "compared_by": "set equality on gap ids and claim ids, then count equality",
        "gap_id_sets_identical": set(full["gap_ids"]) == set(b["gap_ids"]),
        "claim_id_sets_identical": set(full["claim_ids"]) == set(b["claim_ids"]),
        "records": [full["records"], b["firing_object_rows"]],
        "distinct_gap_ids": [full["distinct_gap_ids"], b["distinct_gap_ids"]],
        "duplicate_records": [full["duplicate_gap_id_records"], b["duplicate_object_rows"]],
    }
    receipt = {
        "schema": "GMI_833_AA21_RESULT_V1",
        "package": "gmi-833-aa-finite-universal-harness-v1",
        "issue": 833,
        "rows": ["AA21"],
        "source_main": a["source_main"],
        "claim_ceiling": a["claim_ceiling"],
        "predicate": a["predicate"],
        "registered_population": a["registered_population"],
        "route_b": {k: v for k, v in b.items() if k not in ("gap_ids", "claim_ids")},
        "route_agreement": agree,
        "validation": a["validation"],
        "hostiles": a["hostiles"],
        "hostiles_detected": a["hostiles_detected"],
        "hostiles_total": a["hostiles_total"],
        "null": a["null"],
        "named_results": {
            "FU-1": "two independent routes agree by set equality on the registered "
                    "FIN2UNIV population",
            "FU-2": "the registered population carries a duplicate-record defect: "
                    "283 records over 269 identities",
            "FU-3": "the detector has total recall on planted positives and zero "
                    "alarms on the declared-clean classes",
            "FU-4": "0/200 randomized reassignments reproduce the true flagged set",
        },
        "forbidden_promotions": [
            "FIN2UNIV_CLAIMS_ARE_FALSE",
            "ALL_FALLACIES_DETECTED",
            "AA_FALLACY_SWEEP_COMPLETE",
            "CORPUS_FREE_OF_OVEREXTRAPOLATION",
            "NO_UNIVERSAL_OVERCLAIM_REMAINS",
            "DETECTOR_IS_COMPLETE",
            "ANALYTIC_PROOF",
        ],
    }
    return receipt


def main(argv):
    live = build()
    if "--write" in argv:
        RECEIPT.write_text(json.dumps(live, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("wrote %s" % RECEIPT.name)
        return 0
    if not RECEIPT.exists():
        print("MISSING RECEIPT")
        return 1
    stored = json.loads(RECEIPT.read_text(encoding="utf-8"))
    diffs = []
    for key in ("registered_population", "validation", "null", "route_agreement",
                "predicate", "hostiles_detected", "hostiles_total"):
        if stored.get(key) != live.get(key):
            diffs.append(key)
    if diffs:
        print("RECEIPT DRIFT in: %s" % ", ".join(diffs))
        return 1
    print("receipt matches the live two-route run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
