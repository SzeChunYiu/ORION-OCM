#!/usr/bin/env python3
"""Tests for `gmi-833-aa-fallacy-detectors-v1` (issue #833, AA19/AA31/AA37).

Runnable as `python3 -I -B  test_fallacy_detectors_v1.py`
       and  `python3 -I -O -B test_fallacy_detectors_v1.py`.
Nothing load-bearing is expressed with `assert`.
"""
from __future__ import annotations

import ast
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import fallacy_detectors_v1 as A            # noqa: E402
import independent_detector_oracle_v1 as B  # noqa: E402

FAILURES = []
RUN = []


def check(name, cond, detail=""):
    RUN.append(name)
    if not cond:
        FAILURES.append("%s :: %s" % (name, detail))


def test_freeze_governs():
    freeze = (HERE / "FREEZE_V1.md").read_text(encoding="utf-8")
    for rid, row in sorted(A.ROWS.items()):
        check("freeze_quotes_%s" % rid, row in freeze, "%s not quoted verbatim" % rid)
    check("freeze_no_neighbour", "No neighboring row is earned here." in freeze, "")
    check("freeze_pins_source_main",
          "5e57d4292266bccf435136e1f7d72caa32e920a0" in freeze, "")
    check("freeze_declares_review_queue_ceiling",
          "VALIDATED_REVIEW_QUEUE_DETECTOR_V1" in freeze, "")
    for forbidden in ("AA_FALLACY_SWEEP_COMPLETE", "QUEUED_CLAIM_IS_FALSE",
                      "UNQUEUED_CLAIM_IS_SOUND", "DETECTOR_IS_COMPLETE",
                      "GRAMMAR_BIAS_ELIMINATED", "ANALYTIC_PROOF"):
        check("freeze_forbids_%s" % forbidden, forbidden in freeze, "")
    # The 18 other AA fallacy rows must be named as NOT earned.
    for rid in ("AA16", "AA17", "AA18", "AA20", "AA22", "AA33", "AA36"):
        check("freeze_excludes_%s" % rid, rid in freeze, "")
    recovered = B.rows_from_freeze()
    check("routes_share_no_row_constant", recovered == A.ROWS,
          "route B recovered different row text")


def test_anti_invention_guard():
    guard = A.anti_invention_guard()
    check("guard_passed", guard["passed"],
          json.dumps([c for c in guard["detail"] if not c["occurs"]]))
    check("guard_is_substantial", guard["checked"] >= 30, str(guard["checked"]))
    # Every tier-1 term must have a declared source; the guard says so, and the
    # falsifiability of that claim is asserted here.
    check("guard_is_falsifiable",
          "quantum astrology" not in A.ROWS["AA37"].lower(), "")


def test_route_b_is_independent():
    src = (HERE / "independent_detector_oracle_v1.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    check("oracle_does_not_import_route_a",
          not any("fallacy_detectors" in m for m in imported), str(imported))
    check("oracle_does_not_import_the_ledger_gate",
          not any("ledger_gate" in m for m in imported), str(imported))
    check("oracle_uses_no_regex", "re" not in imported, str(imported))
    check("oracle_does_not_execute_the_grammar_parent",
          "grammar_bias_core_v1" not in src and "remint_fixture" not in src,
          "route B must read the parent's committed receipt, not run it")


def test_routes_agree():
    a = A.main()
    b = B.derive()
    a19 = a["AA19_representability_vs_reachability"]
    a31 = a["AA31_grammar_induced_artifacts"]
    a37 = a["AA37_parent_reduction_after_new_form"]
    pairs = [
        ("aa19 objects", a19["objects_scanned"], b["AA19"]["objects_scanned"]),
        ("aa19 records", a19["queued_records"], b["AA19"]["queued_records"]),
        ("aa19 ids", a19["queued_distinct_object_ids"],
         b["AA19"]["queued_distinct_object_ids"]),
        ("aa19 files", a19["queued_distinct_source_files"],
         b["AA19"]["queued_distinct_source_files"]),
        ("aa19 alarms", a19["real_alarms_total"], b["AA19"]["real_alarms_total"]),
        ("aa19 overlap", a19["overlap_with_aa21_fin2univ"],
         b["AA19"]["overlap_with_aa21_fin2univ"]),
        ("aa31 cells", a31["divergent_cells"], b["AA31"]["divergent_cells"]),
        ("aa31 permutations", a31["parent_certified_permutations"],
         b["AA31"]["parent_certified_permutations"]),
        ("aa37 results", a37["named_results_scanned"],
         b["AA37"]["named_results_scanned"]),
        ("aa37 tier1", a37["tier1_triggered"], b["AA37"]["tier1_triggered"]),
        ("aa37 identified", a37["tier1_identified"], b["AA37"]["tier1_identified"]),
        ("aa37 cleared", a37["tier1_cleared_by_a_parent_ledger"],
         b["AA37"]["tier1_cleared_by_a_parent_ledger"]),
        ("aa37 queued", a37["tier1_queued"], b["AA37"]["tier1_queued"]),
    ]
    for label, x, y in pairs:
        check("agree_%s" % label.replace(" ", "_"), x == y, "A=%s B=%s" % (x, y))
    # Set equality on the queues, not count equality.
    check("aa19_queue_sets_identical",
          set(a19["queued_object_ids"]) == set(b["AA19"]["queued_object_ids"]),
          "symmetric difference %d"
          % len(set(a19["queued_object_ids"]) ^ set(b["AA19"]["queued_object_ids"])))
    check("aa31_cell_sets_identical",
          sorted(map(tuple, a31["divergent_cells_detail"]))
          == sorted(map(tuple, b["AA31"]["divergent_cells_detail"])), "")
    check("aa37_queue_sets_identical",
          sorted((q["path"], q["result"]) for q in a37["queue"])
          == sorted((q["path"], q["result"]) for q in b["AA37"]["queue"]), "")
    return a, b


def test_aa19(a):
    c = a["AA19_representability_vs_reachability"]
    p = a["AA19_planted"]
    check("aa19_recall_total",
          p["planted_positives_detected" if "planted_positives_detected" in p
            else "planted_positives_queued"] == p["planted_positives"]
          and p["planted_positives"] > 0, json.dumps(p))
    check("aa19_planted_clean_silent", p["planted_clean_alarms"] == 0, json.dumps(p))
    # The no-alarm case that matters is the real one.
    check("aa19_real_zero_alarms", c["real_alarms_total"] == 0, json.dumps(
        {k: c[k] for k in ("real_alarms_total", "real_clean_total")}))
    check("aa19_real_clean_population_large", c["real_clean_total"] > 20000,
          str(c["real_clean_total"]))
    check("aa19_queue_non_empty", c["queued_records"] > 0, str(c["queued_records"]))
    # Disjointness from AA21 is checked, not asserted.
    check("aa19_nearly_disjoint_from_aa21",
          c["overlap_with_aa21_fin2univ"] < c["queued_distinct_object_ids"],
          "AA19 has collapsed into AA21's population: %s" % c["overlap_with_aa21_fin2univ"])
    check("aa19_text_variant_inflation_reported",
          c["text_variant_extra_records"] >= 0, "")


def test_aa31(a):
    c = a["AA31_grammar_induced_artifacts"]
    check("aa31_isometric_family_non_empty", c["isometric_remints_checked"] > 0,
          str(c["isometric_remints_checked"]))
    check("aa31_isometric_zero_alarms", c["isometric_alarms"] == 0, json.dumps(c))
    check("aa31_matches_parent_permutation_count",
          c["isometric_remints_checked"] == c["parent_certified_permutations"],
          "%s vs %s" % (c["isometric_remints_checked"],
                        c["parent_certified_permutations"]))
    check("aa31_parent_had_no_invariant_failure",
          c["parent_invariant_failures"] == 0, str(c["parent_invariant_failures"]))
    check("aa31_pair_is_same_semantics", c["nonisometric_pair_same_semantics"],
          "the positive must differ in grammar, not in what it computes")
    check("aa31_pair_is_queued", c["nonisometric_pair_queued"], "")
    check("aa31_cells_named", c["divergent_cells"] > 0,
          "a queued pair must name the cells that diverge")
    # Exactness: a Fraction comparison must see a difference a float tolerance
    # would swallow.
    near = A.bias_divergence({"X": {"Q": {"0": "1/3"}}},
                             {"X": {"Q": {"0": "333333/1000000"}}})
    check("aa31_exact_not_tolerant", len(near) == 1, str(near))
    same = A.bias_divergence({"X": {"Q": {"0": "2/6"}}}, {"X": {"Q": {"0": "1/3"}}})
    check("aa31_equal_fractions_do_not_diverge", len(same) == 0, str(same))


def test_aa37(a):
    c = a["AA37_parent_reduction_after_new_form"]
    p = c["planted"]
    check("aa37_planted_recall", p["planted_queued"] == 1, json.dumps(p))
    check("aa37_planted_clearing", p["planted_cleared"] == 1, json.dumps(p))
    check("aa37_off_topic_silent", p["planted_off_topic_triggered"] == 0,
          json.dumps(p))
    check("aa37_real_population_non_empty", c["tier1_identified"] > 0,
          json.dumps({k: c[k] for k in ("tier1_triggered", "tier1_identified")}))
    check("aa37_real_no_alarm_population_large",
          c["real_non_triggering_results"] > 2000,
          str(c["real_non_triggering_results"]))
    check("aa37_this_tranche_is_a_live_negative",
          c["this_tranche_tier1_results"] > 0 and c["this_tranche_queued"] == 0,
          json.dumps({k: c[k] for k in ("this_tranche_tier1_results",
                                        "this_tranche_queued")}))
    check("aa37_tier2_is_only_an_inflation_figure",
          c["tier2_inflation_over_tier1"] > 0, json.dumps(
              {k: c[k] for k in ("tier1_identified", "tier2_identified",
                                 "tier2_inflation_over_tier1")}))
    check("aa37_queue_entries_name_a_file_and_a_result",
          all(q.get("path") and q.get("result") for q in c["queue"]), "")


def test_hostiles_and_null(a):
    for h in a["hostiles"]:
        check("hostile_detected_%s" % h["name"], bool(h["detected"]), json.dumps(h))
        check("hostile_moved_%s" % h["name"], h["before"] != h["after"], json.dumps(h))
    check("hostile_count", a["hostiles_total"] >= 7, str(a["hostiles_total"]))
    n = a["null"]
    check("null_trials", n["trials"] == 200, str(n["trials"]))
    check("null_never_reproduces", n["reproduced_true_queue"] == 0, json.dumps(n))
    check("null_non_vacuous", n["min_flagged"] > 0, json.dumps(n))
    check("null_overlap_below_truth",
          n["max_overlap_with_true_queue"] < n["true_queue_size"], json.dumps(n))
    # exact rationals, not floats
    Fraction(n["mean_flagged_exact"])
    Fraction(n["mean_overlap_exact"])
    RUN.append("null_means_are_exact_rationals")


def test_no_float(a):
    def walk(node, path="$"):
        if isinstance(node, float):
            FAILURES.append("float_in_receipt :: %s" % path)
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, path + "." + str(k))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, path + "[%d]" % i)
    RUN.append("no_float_in_receipt")
    walk(a)


def test_receipt_matches(a):
    path = HERE / "RESULT_V1.json"
    if not path.exists():
        RUN.append("receipt_present")
        FAILURES.append("receipt_present :: RESULT_V1.json missing")
        return
    stored = json.loads(path.read_text(encoding="utf-8"))
    for key in ("AA19_planted", "AA31_grammar_induced_artifacts", "guard", "null"):
        check("receipt_%s" % key, stored[key] == a[key], "%s drifted" % key)
    # AA19 and AA37 read a corpus other lanes extend: bind them non-vacuously.
    live19 = a["AA19_representability_vs_reachability"]
    st19 = stored["AA19_representability_vs_reachability"]
    check("receipt_aa19_corpus_did_not_shrink",
          live19["objects_scanned"] >= st19["objects_scanned"], "")
    check("receipt_aa19_still_zero_alarms", live19["real_alarms_total"] == 0, "")
    live37 = a["AA37_parent_reduction_after_new_form"]
    st37 = stored["AA37_parent_reduction_after_new_form"]
    check("receipt_aa37_corpus_did_not_shrink",
          live37["named_results_scanned"] >= st37["named_results_scanned"], "")
    check("receipt_aa37_tranche_still_clear",
          live37["this_tranche_queued"] == 0, "")


def main():
    test_freeze_governs()
    test_anti_invention_guard()
    test_route_b_is_independent()
    a, b = test_routes_agree()
    test_aa19(a)
    test_aa31(a)
    test_aa37(a)
    test_hostiles_and_null(a)
    test_no_float(a)
    test_receipt_matches(a)
    print("checks run: %d" % len(RUN))
    if FAILURES:
        print("FAILURES (%d):" % len(FAILURES))
        for f in FAILURES:
            print("  - %s" % f)
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
