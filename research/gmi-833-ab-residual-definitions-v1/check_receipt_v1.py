#!/usr/bin/env python3
"""Build (`--write`) or verify the AB08/AB25 receipt against a live run."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import residual_definitions_v1 as A            # noqa: E402
import independent_definitions_oracle_v1 as B  # noqa: E402

RECEIPT = HERE / "RESULT_V1.json"


def build():
    a = A.main()
    b = B.derive()
    out = dict(a)
    out["schema"] = "GMI_833_AB_RESIDUAL_DEFINITIONS_RESULT_V1"
    out["package"] = "gmi-833-ab-residual-definitions-v1"
    out["issue"] = 833
    out["rows"] = ["AB08", "AB25"]
    out["route_b"] = b
    out["route_agreement"] = {
        "compared_by": "count equality plus list equality on the row-named item lists",
        "component_lists_identical":
            a["AB08_rice_subtraction"]["row_components"] == b["ab08_row_components"],
        "level_lists_identical":
            a["AB25_novelty_ladder"]["row_levels"] == b["ab25_row_levels"],
        "verdicts_identical":
            a["AB08_rice_subtraction"]["verdict_counts"] == b["ab08_verdicts"],
    }
    out["named_results"] = {
        "RD-1": "all five Rice components are subtracted with a verdict in the "
                "declared vocabulary and a named residual; 2 ABSORBED, 3 PARTIAL, "
                "0 DIVERGENT",
        "RD-2": "all six novelty-ladder levels carry an operational criterion "
                "naming a witness, a falsifier, a parent and a demotion rule; the "
                "demotion chain is strictly downward and terminates at level 0",
        "RD-3": "every required item is read off the row that demands it, with "
                "AB25's antecedent declared in the freeze in advance; 0/200 random "
                "bindings reproduce the true one",
    }
    out["forbidden_promotions"] = [
        "GMI_IS_NOVEL_WRT_RICE", "RICE_SUBSUMED", "PARENT_EXHAUSTED",
        "LADDER_APPLIED", "CLAIM_IS_AT_LEVEL_N", "ALL_PARENTS_EXHAUSTED",
        "CITATIONS_VERIFIED", "NOVELTY_ESTABLISHED", "CORPUS_TERMINOLOGY_CLEAN",
        "MIGRATION_COMPLETE", "ANALYTIC_PROOF",
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
    diffs = [k for k in ("AB08_rice_subtraction", "AB25_novelty_ladder", "guard",
                         "null", "hostiles", "route_b", "route_agreement")
             if stored.get(k) != live.get(k)]
    if diffs:
        print("RECEIPT DRIFT in: %s" % ", ".join(diffs))
        return 1
    print("receipt matches the live two-route run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
