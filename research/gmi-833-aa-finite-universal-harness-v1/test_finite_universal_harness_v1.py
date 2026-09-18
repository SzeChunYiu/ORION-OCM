#!/usr/bin/env python3
"""Tests for `gmi-833-aa-finite-universal-harness-v1` (issue #833, AA21).

Runnable as `python3 -I -B  test_finite_universal_harness_v1.py`
       and  `python3 -I -O -B test_finite_universal_harness_v1.py`.

No `assert` statement carries load-bearing logic: every check raises
explicitly, so `-O` does not hollow the suite out.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import finite_universal_harness_v1 as A          # noqa: E402
import independent_fin2univ_oracle_v1 as B       # noqa: E402

REPO = HERE.parent.parent
FAILURES = []
RUN = []


def check(name, cond, detail=""):
    RUN.append(name)
    if not cond:
        FAILURES.append("%s :: %s" % (name, detail))


# --------------------------------------------------------------------------
# Anti-invention guard: every string this package treats as required must
# occur literally in the AA21 row text it claims to discharge.
# --------------------------------------------------------------------------
AA21_ROW = "- [ ] Search for finite-scope-to-universal extrapolation."


def test_row_text_governs_the_package():
    low = AA21_ROW.lower()
    for token in ("finite", "universal", "extrapolation", "search"):
        check("row_names_%s" % token, token in low,
              "AA21 row text does not contain %r" % token)
    # The package must not silently widen to a neighbouring fallacy row.
    for foreign in ("converse", "identifiability", "stationarity", "leakage",
                    "quantifier-order", "grammar-induced"):
        check("row_excludes_%s" % foreign.replace("-", "_"), foreign not in low,
              "AA21 row text unexpectedly contains %r" % foreign)


def test_freeze_declares_this_row_and_precedes_implementation():
    freeze = (HERE / "FREEZE_V1.md").read_text(encoding="utf-8")
    check("freeze_quotes_row", AA21_ROW in freeze, "freeze does not quote the row verbatim")
    check("freeze_no_neighbour", "No neighboring row is earned here." in freeze, "")
    check("freeze_pins_source_main",
          "5e57d4292266bccf435136e1f7d72caa32e920a0" in freeze, "")
    check("freeze_declares_ceiling", "REGISTERED_DETECTOR_VALIDATED_V1" in freeze, "")
    for forbidden in ("FIN2UNIV_CLAIMS_ARE_FALSE", "ALL_FALLACIES_DETECTED",
                      "DETECTOR_IS_COMPLETE", "ANALYTIC_PROOF"):
        check("freeze_forbids_%s" % forbidden, forbidden in freeze, "")
    # The declared-clean classes must have been fixed in the freeze, not here.
    # The freeze states them in prose ("UNIVERSAL with an analytic or mechanized
    # evidence mode"); the freeze is committed and is never edited to match a
    # later test, so the test resolves against the freeze's own wording.
    low = freeze.lower()
    for word in ("analytic", "mechanized", "no-alarm", "recall", "null"):
        check("freeze_declares_%s" % word.replace("-", "_"), word in low,
              "freeze does not declare %r before implementation" % word)
    check("freeze_declares_clean_classes",
          "declared-clean" in low and "zero" in low, "")


# --------------------------------------------------------------------------
# Two materially independent routes.
# --------------------------------------------------------------------------
def test_routes_agree_by_set_equality():
    a = A.main()
    b = B.derive()
    pop = a["registered_population"]

    graph = A._read_json(A.GAP_GRAPH)
    full = A.registered_population(graph)

    check("route_b_recovers_quantifier",
          b["recovered_predicate"]["quantifier_class"] == A.FIN2UNIV_QUANTIFIER,
          str(b["recovered_predicate"]))
    check("route_b_recovers_modes",
          tuple(sorted(b["recovered_predicate"]["proof_evidence_modes"]))
          == tuple(sorted(A.FIN2UNIV_EVIDENCE_MODES)),
          str(b["recovered_predicate"]))
    check("route_b_recovers_id_rule",
          b["recovered_gap_id_rule"] == {"prefix": A.GAP_ID_PREFIX, "hex_truncation": 12},
          str(b["recovered_gap_id_rule"]))

    check("records_agree", pop["records"] == b["firing_object_rows"],
          "%s vs %s" % (pop["records"], b["firing_object_rows"]))
    check("distinct_ids_agree", pop["distinct_gap_ids"] == b["distinct_gap_ids"],
          "%s vs %s" % (pop["distinct_gap_ids"], b["distinct_gap_ids"]))
    check("duplicates_agree",
          pop["duplicate_gap_id_records"] == b["duplicate_object_rows"],
          "%s vs %s" % (pop["duplicate_gap_id_records"], b["duplicate_object_rows"]))
    # THE load-bearing comparison: set equality, not count equality.
    check("gap_id_sets_identical", set(full["gap_ids"]) == set(b["gap_ids"]),
          "symmetric difference %d" % len(set(full["gap_ids"]) ^ set(b["gap_ids"])))
    check("claim_id_sets_identical", set(full["claim_ids"]) == set(b["claim_ids"]),
          "symmetric difference %d" % len(set(full["claim_ids"]) ^ set(b["claim_ids"])))
    return a, b, full


def _non_docstring_strings(path):
    """Every string constant in a module except module/class/function docstrings."""
    import ast
    tree = ast.parse(path.read_text(encoding="utf-8"))
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr):
                val = body[0].value
                if isinstance(val, ast.Constant) and isinstance(val.value, str):
                    docstrings.add(id(val))
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) not in docstrings:
                out.append(node.value)
    return tree, out


def test_route_b_does_not_import_route_a():
    path = HERE / "independent_fin2univ_oracle_v1.py"
    import ast
    tree, strings = _non_docstring_strings(path)
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    check("oracle_independent",
          not any("finite_universal_harness" in m for m in imported),
          "route B imports route A: %s" % imported)
    check("oracle_imports_stdlib_only",
          set(m.split(".")[0] for m in imported) <= {
              "hashlib", "json", "re", "collections", "pathlib", "typing",
              "__future__"},
          "route B imports a non-stdlib module: %s" % imported)
    check("oracle_never_opens_gap_graph",
          not any("GMI_GAP_GRAPH" in s for s in strings),
          "route B reads the registered population it is supposed to re-derive")
    # And route A must never read the object corpus to BUILD the population.
    a_tree, a_strings = _non_docstring_strings(HERE / "finite_universal_harness_v1.py")
    check("route_a_population_comes_from_the_gap_graph",
          any("GMI_GAP_GRAPH" in s for s in a_strings),
          "route A no longer reads the registered gap graph")


# --------------------------------------------------------------------------
# Detector validation.
# --------------------------------------------------------------------------
def test_recall_and_no_alarm(a):
    v = a["validation"]
    check("recall_total",
          v["planted_positives_detected"] == v["planted_positives"] and v["planted_positives"] > 0,
          str(v))
    check("no_alarm_on_declared_clean",
          v["declared_clean_alarms"] == 0 and v["declared_clean"] > 0,
          str(v))
    # A detector that cannot fail the no-alarm test is not a test.
    widened = A.FIN2UNIV_EVIDENCE_MODES + A.CLEAN_UNIVERSAL_MODES
    alarms = sum(1 for o in A.declared_clean()
                 if o["quantifier_class"] == A.FIN2UNIV_QUANTIFIER
                 and o["proof_evidence_mode"] in widened)
    check("no_alarm_case_is_falsifiable", alarms > 0,
          "widening the mode set raised no alarm - the clean set is vacuous")


def test_hostiles_all_detected_and_moved(a):
    host = a["hostiles"]
    check("hostile_count", len(host) >= 6, str(len(host)))
    for h in host:
        check("hostile_detected_%s" % h["name"], bool(h["detected"]), json.dumps(h))
        check("hostile_moved_%s" % h["name"], h["before"] != h["after"],
              "%s did not move %s" % (h["name"], h["moved_quantity"]))


def test_null_is_beaten(a):
    n = a["null"]
    check("null_trials", n["trials"] == 200, str(n["trials"]))
    check("null_never_reproduces", n["reproduced_true_set"] == 0, str(n))
    # The null must be non-vacuous: randomized sets of comparable size.
    check("null_non_vacuous", n["min_flagged"] > 0 and n["max_flagged"] > 0, str(n))
    check("null_overlap_strictly_below_truth",
          n["max_overlap_with_true_set"] < n["true_set_size"], str(n))


# --------------------------------------------------------------------------
# Integrity of the registered population (disclosure, not repair).
# --------------------------------------------------------------------------
def test_population_integrity(full):
    check("required_text_cells_non_empty", full["empty_required_text_cells"] == 0,
          str(full["empty_required_text_cells"]))
    check("duplicate_defect_is_disclosed", full["duplicate_gap_id_records"] > 0,
          "the 283/269 duplicate finding no longer reproduces - update the theorem note")
    check("claim_ids_equal_gap_ids",
          full["distinct_claim_ids"] == full["distinct_gap_ids"],
          "%s vs %s" % (full["distinct_claim_ids"], full["distinct_gap_ids"]))
    for col, vals in full["column_profile"].items():
        check("column_%s_is_constant" % col, len(vals) == 1,
              "%s carries %d values" % (col, len(vals)))


def test_no_float_in_receipt(a):
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


def test_receipt_matches_live_run(a):
    path = HERE / "RESULT_V1.json"
    if not path.exists():
        RUN.append("receipt_present")
        FAILURES.append("receipt_present :: RESULT_V1.json missing")
        return
    stored = json.loads(path.read_text(encoding="utf-8"))
    live = a["registered_population"]
    for key in ("records", "distinct_gap_ids", "distinct_claim_ids",
                "duplicate_gap_id_records", "total_gaps_in_graph"):
        check("receipt_%s" % key,
              stored["registered_population"][key] == live[key],
              "%s: receipt %s live %s" % (key, stored["registered_population"][key], live[key]))


def main():
    test_row_text_governs_the_package()
    test_freeze_declares_this_row_and_precedes_implementation()
    test_route_b_does_not_import_route_a()
    a, b, full = test_routes_agree_by_set_equality()
    test_recall_and_no_alarm(a)
    test_hostiles_all_detected_and_moved(a)
    test_null_is_beaten(a)
    test_population_integrity(full)
    test_no_float_in_receipt(a)
    test_receipt_matches_live_run(a)

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
