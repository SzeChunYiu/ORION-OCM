#!/usr/bin/env python3
"""Build (`--write`) or verify the AA02-AA06 receipt against a live run."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import ledger_gate_v1 as A                # noqa: E402
import independent_ledger_oracle_v1 as B  # noqa: E402
import test_ledger_gate_v1 as T           # noqa: E402

RECEIPT = HERE / "RESULT_V1.json"
KEYS = ("theorem_files", "named_results", "complete_named_results",
        "non_compliant_named_results", "identified_named_results",
        "identified_complete", "unparsed_theorem_artifacts",
        "vendored_theorem_artifacts", "vendored_named_results",
        "emission_by_ledger", "experiment_files", "experiment_complete",
        "experiment_emission_by_ledger")


def build():
    a = A.census()
    b = B.derive()
    base = json.loads((HERE / "LEDGER_BASELINE_V1.json").read_text(encoding="utf-8"))
    code, gate_report = A.gate(None, None, None)
    demo = T.gate_demo()

    a_map = {}
    for f in a["per_file"]:
        for r in f["named_results"]:
            a_map[f["path"] + "::" + r["result"]] = bool(r["complete"])

    planted_total = 0
    planted_complete = 0
    for f in a["per_file"]:
        if f["path"].startswith("research/gmi-833-aa-finite-universal-harness-v1/") \
           or f["path"].startswith("research/gmi-833-aa-ledger-gate-v1/"):
            planted_total += f["count"]
            planted_complete += f["complete"]

    return {
        "schema": "GMI_833_AA_LEDGER_GATE_RESULT_V1",
        "package": "gmi-833-aa-ledger-gate-v1",
        "issue": 833,
        "rows": ["AA02", "AA03", "AA04", "AA05", "AA06"],
        "source_main": "5e57d4292266bccf435136e1f7d72caa32e920a0",
        "claim_ceiling": "RATCHETED_LEDGER_EMISSION_GATE_V1",
        "baseline": {k: base[k] for k in (
            "theorem_files", "named_results", "complete_named_results",
            "non_compliant_named_results", "identified_named_results",
            "emission_by_ledger", "experiment_files",
            "unparsed_theorem_artifacts", "excluded_prefixes")},
        "live_census": {k: a[k] for k in KEYS},
        "route_b": {k: b[k] for k in (
            "theorem_files", "named_results", "complete_named_results",
            "non_compliant_named_results", "emission_by_ledger",
            "unparsed_theorem_artifacts", "experiment_files",
            "experiment_complete", "experiment_emission_by_ledger")},
        "route_agreement": {
            "compared_by": "set equality over (path::result) -> complete",
            "per_result_maps_identical": a_map == b["per_result"],
            "keys": len(a_map),
            "duplicate_result_keys": a["named_results"] - len(a_map),
            "duplicate_note": (
                "headings that repeat verbatim inside one theorem artifact "
                "collapse to one key; disclosed, not de-duplicated in the counts"
            ),
        },
        "guard": A.anti_invention_guard(),
        "row_binding_null": A.row_binding_null(),
        "vocabulary_null_diagnostic": A.null_study(a),
        "planted_positives": {
            "theorem_named_results": planted_total,
            "theorem_named_results_complete": planted_complete,
            "experiment_ledger_artifacts": a["experiment_files"],
            "experiment_ledger_artifacts_complete": a["experiment_complete"],
        },
        "gate_on_the_real_repo": {
            "exit": code,
            "new_named_results": gate_report["new_named_results"],
            "regressions": gate_report["regressions"],
            "violations": len(gate_report["violations"]),
            "corpus_debt_grew": gate_report["corpus_debt_grew"],
        },
        "gate_failure_demonstration": demo,
        "named_results": {
            "LG-1": "at source_main, 0 of 2345 named results in 329 theorem "
                    "artifacts emit all four theorem ledgers",
            "LG-2": "the emission predicate rejects the prose-mention decoy, "
                    "and both routes agree per named result by set equality",
            "LG-3": "the ratchet is blocking and demonstrably fails on a new "
                    "non-compliant result, on a regression and on the decoy",
            "LG-4": "AA06's experiment-ledger artifact class had no instance on "
                    "main; the planted positives are detected",
            "LG-5": "every canonical ledger label occurs in its own AA row text; "
                    "0/200 random row bindings satisfy the guard",
        },
        "forbidden_promotions": [
            "CORPUS_LEDGERS_COMPLETE",
            "ALL_THEOREMS_COMPLIANT",
            "LEDGER_DEBT_CLEARED",
            "LEDGER_CONTENTS_VERIFIED",
            "ASSUMPTIONS_EXHAUSTED",
            "ALL_FALSIFIERS_KNOWN",
            "ALL_PARENTS_EXHAUSTED",
            "RECURSION_EXHAUSTED",
            "NO_MATERIAL_GAP_REMAINS",
            "ANALYTIC_PROOF",
        ],
    }


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

    # PINNED quantities: equality. The baseline is a frozen picture of
    # source_main and the validation apparatus is self-contained, so any drift
    # in these is a defect.
    diffs = []
    for key in ("baseline", "guard", "row_binding_null", "planted_positives",
                "gate_failure_demonstration"):
        if stored.get(key) != live.get(key):
            diffs.append(key)

    # LIVE quantities: the theorem corpus is a shared surface that other lanes
    # extend, so demanding equality here would make this check fail on main for
    # a reason that has nothing to do with this package. Assert it
    # NON-VACUOUSLY instead, and print the live number.
    a = live["live_census"]
    b = live["route_b"]
    stored_live = stored["live_census"]
    live_checks = [
        ("theorem corpus did not shrink below the receipt",
         a["theorem_files"] >= stored_live["theorem_files"]),
        ("named results did not shrink below the receipt",
         a["named_results"] >= stored_live["named_results"]),
        ("ledger debt never grew past the frozen baseline",
         a["non_compliant_named_results"] <= stored["baseline"]["non_compliant_named_results"]),
        ("every planted positive is still complete",
         a["complete_named_results"] >= stored_live["complete_named_results"]),
        ("the experiment-ledger class is still populated",
         a["experiment_files"] >= 2 and a["experiment_complete"] == a["experiment_files"]),
        ("routes still agree on the live corpus",
         all(a[k] == b[k] for k in ("theorem_files", "named_results",
                                    "complete_named_results",
                                    "non_compliant_named_results"))
         and live["route_agreement"]["per_result_maps_identical"]),
    ]
    print("live corpus now: %d theorem artifacts, %d named results, "
          "%d complete, %d non-compliant (frozen baseline %d)"
          % (a["theorem_files"], a["named_results"], a["complete_named_results"],
             a["non_compliant_named_results"],
             stored["baseline"]["non_compliant_named_results"]))
    failed_live = [label for label, ok in live_checks if not ok]

    if diffs or failed_live:
        if diffs:
            print("RECEIPT DRIFT in pinned section(s): %s" % ", ".join(diffs))
        for label in failed_live:
            print("LIVE ASSERTION FAILED: %s" % label)
        return 1
    print("receipt matches: pinned quantities exact, live corpus assertions hold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
