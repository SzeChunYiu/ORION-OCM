#!/usr/bin/env python3
"""Build (`--write`) or verify the AA19/AA31/AA37 receipt against a live run."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import fallacy_detectors_v1 as A            # noqa: E402
import independent_detector_oracle_v1 as B  # noqa: E402

RECEIPT = HERE / "RESULT_V1.json"


def build():
    a = A.main()
    b = B.derive()
    a19 = a["AA19_representability_vs_reachability"]
    out = dict(a)
    out["schema"] = "GMI_833_AA_FALLACY_DETECTORS_RESULT_V1"
    out["package"] = "gmi-833-aa-fallacy-detectors-v1"
    out["issue"] = 833
    out["rows"] = ["AA19", "AA31", "AA37"]
    out["route_b"] = {
        "AA19": {k: v for k, v in b["AA19"].items() if k != "queued_object_ids"},
        "AA31": b["AA31"],
        "AA37": {k: v for k, v in b["AA37"].items() if k != "queue"},
    }
    out["route_agreement"] = {
        "compared_by": "set equality on every queue, then count equality",
        "aa19_queue_sets_identical":
            set(a19["queued_object_ids"]) == set(b["AA19"]["queued_object_ids"]),
        "aa31_cell_sets_identical":
            sorted(map(tuple, a["AA31_grammar_induced_artifacts"]["divergent_cells_detail"]))
            == sorted(map(tuple, b["AA31"]["divergent_cells_detail"])),
        "aa37_queue_sets_identical":
            sorted((q["path"], q["result"])
                   for q in a["AA37_parent_reduction_after_new_form"]["queue"])
            == sorted((q["path"], q["result"]) for q in b["AA37"]["queue"]),
        "route_b_sources": ("AA19 recount of the object corpus; AA31 the parent's "
                            "COMMITTED receipt rather than a live run; AA37 an "
                            "independent markdown scan with no regex"),
    }
    out["named_results"] = {
        "FD-1": "AA19 queues universal claims warranted by a search that was run; "
                "zero alarms on the real declared-clean population",
        "FD-2": "AA31 queues a same-semantics grammar pair by exact rational "
                "divergence; the parent's whole isometric family raises none",
        "FD-3": "AA37 queues new-form claims carrying no parent-reduction ledger, "
                "with this tranche's own notes as a live cleared negative",
        "FD-4": "each detector's text-trigger variant is measured and published as "
                "an inflation figure, never used to queue",
    }
    out["forbidden_promotions"] = [
        "AA_FALLACY_SWEEP_COMPLETE", "ALL_FALLACIES_DETECTED",
        "CORPUS_FREE_OF_FALLACY", "NO_CONFUSION_REMAINS",
        "QUEUED_CLAIM_IS_FALSE", "UNQUEUED_CLAIM_IS_SOUND",
        "DETECTOR_IS_COMPLETE", "DETECTOR_IS_SOUND",
        "GRAMMAR_BIAS_ELIMINATED", "ALL_GRAMMARS_EQUIVALENT",
        "SEARCH_REACHABILITY_INVARIANT_UNIVERSALLY",
        "ALL_PARENTS_EXHAUSTED", "PARENT_REDUCTION_COMPLETE",
        "NOVELTY_ESTABLISHED", "RECURSION_EXHAUSTED", "ANALYTIC_PROOF",
    ]
    out["AA19_representability_vs_reachability"] = {
        k: v for k, v in a19.items() if k != "queued_object_ids"}
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
    diffs = [k for k in ("AA19_planted", "AA31_grammar_induced_artifacts",
                         "guard", "null", "route_agreement")
             if stored.get(k) != live.get(k)]
    # AA37's planted fixtures are constructed and corpus-independent, so they
    # are pinned by EQUALITY even though the tier-1 corpus figures beside them
    # are not. A reconciliation line may quote these without a scope clause.
    if stored["AA37_parent_reduction_after_new_form"]["planted"] != \
            live["AA37_parent_reduction_after_new_form"]["planted"]:
        diffs.append("AA37_parent_reduction_after_new_form.planted")
    a19 = live["AA19_representability_vs_reachability"]
    a37 = live["AA37_parent_reduction_after_new_form"]
    s19 = stored["AA19_representability_vs_reachability"]
    s37 = stored["AA37_parent_reduction_after_new_form"]
    live_checks = [
        ("object corpus did not shrink",
         a19["objects_scanned"] >= s19["objects_scanned"]),
        ("AA19 still raises zero alarms on the real clean population",
         a19["real_alarms_total"] == 0),
        ("theorem corpus did not shrink",
         a37["named_results_scanned"] >= s37["named_results_scanned"]),
        ("this tranche's own new-form results are still cleared",
         a37["this_tranche_queued"] == 0),
    ]
    print("live: %d objects, AA19 queue %d, %d alarms; %d named results, "
          "AA37 queue %d" % (a19["objects_scanned"], a19["queued_records"],
                             a19["real_alarms_total"], a37["named_results_scanned"],
                             a37["tier1_queued"]))
    failed = [lbl for lbl, ok in live_checks if not ok]
    if diffs or failed:
        for d in diffs:
            print("RECEIPT DRIFT in pinned section: %s" % d)
        for f in failed:
            print("LIVE ASSERTION FAILED: %s" % f)
        return 1
    print("receipt matches: pinned quantities exact, live corpus assertions hold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
