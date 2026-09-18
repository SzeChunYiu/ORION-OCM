#!/usr/bin/env python3
"""Tests for `gmi-833-ac-lanes-harness-v1` (issue #833, AC01/AC03/AC04/AC06).

Runnable as `python3 -I -B  test_ac_lanes_harness_v1.py`
       and  `python3 -I -O -B test_ac_lanes_harness_v1.py`.
Nothing load-bearing is expressed with `assert`.
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import ac_lanes_harness_v1 as A       # noqa: E402
import independent_ac_oracle_v1 as B  # noqa: E402

FAILURES = []
RUN = []


def check(name, cond, detail=""):
    RUN.append(name)
    if not cond:
        FAILURES.append("%s :: %s" % (name, detail))


def test_rows_are_byte_identical_to_the_freeze():
    freeze = (HERE / "FREEZE_V1.md").read_text(encoding="utf-8")
    for rid, row in sorted(A.ROWS.items()):
        check("freeze_quotes_%s" % rid, row in freeze,
              "%s is not quoted verbatim in the freeze" % rid)
    # Route B recovers the rows from the freeze independently; they must match.
    recovered = B.rows_from_freeze()
    check("routes_share_no_row_constant", recovered == A.ROWS,
          "route B recovered different row text: %s"
          % [k for k in A.ROWS if A.ROWS[k] != recovered.get(k)])
    check("freeze_no_neighbour", "No neighboring row is earned here." in freeze, "")
    check("freeze_pins_source_main",
          "5e57d4292266bccf435136e1f7d72caa32e920a0" in freeze, "")
    for forbidden in ("CITATIONS_VERIFIED", "LITERATURE_SATURATED",
                      "PARENT_IS_EARLIEST", "WHAT_IS_ACTUALLY_NEW_COMPLETE"):
        check("freeze_forbids_%s" % forbidden, forbidden in freeze, "")
    check("freeze_declares_ac05_firewall", "AC05 firewall" in freeze
          or "The AC05 firewall" in freeze, "")


def test_anti_invention_guard():
    guard = A.anti_invention_guard()
    check("guard_passed", guard["passed"],
          json.dumps([c for c in guard["detail"] if not c["occurs"]]))
    check("guard_covers_eleven_lanes_and_six_kinds",
          guard["checked"] == 11 + 6 + 5, str(guard["checked"]))
    # The guard must be able to fail.
    check("guard_is_falsifiable",
          "quantum astrology" not in A.ROWS["AC01"], "")


def test_route_b_is_independent():
    src = (HERE / "independent_ac_oracle_v1.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    check("oracle_does_not_import_route_a",
          not any("ac_lanes_harness" in m for m in imported), str(imported))
    check("oracle_uses_no_regex", "re" not in imported,
          "route B imports re; a shared regex bug could make both routes agree")


def test_routes_agree():
    a = A.main()
    b = B.derive()
    pairs = [
        ("lane items", a["AC01_lane_coverage"]["row_items"], b["lane_items"]),
        ("lane headings", a["AC01_lane_coverage"]["lane_headings"], b["lane_headings"]),
        ("bound", a["AC01_lane_coverage"]["bound_one_to_one"], b["bound_one_to_one"]),
        ("lane entries", a["AC01_lane_coverage"]["total_entries"], b["total_entries"]),
        ("exact rows", a["AC03_canonical_preference"]["antecedent_rows_exact_match"],
         b["exact_rows"]),
        ("ac03 ok", a["AC03_canonical_preference"]["satisfying_either"],
         b["ac03_satisfying_either"]),
        ("ac04 antecedent",
         a["AC04_synonyms_and_primary_term"]["antecedent_rows_multi_synonym"],
         b["ac04_antecedent_rows"]),
        ("ac04 parent",
         a["AC04_synonyms_and_primary_term"]["resolved_by_frozen_parent"],
         b["ac04_resolved_by_frozen_parent"]),
        ("ac06 anchored",
         a["AC06_parent_record"]["with_dated_or_authored_parent_in_parent_artifact"],
         b["ac06_with_parent_in_parent_artifact"]),
        ("ac06 supplied", a["AC06_parent_record"]["supplied_by_addendum"],
         b["ac06_supplied_by_addendum"]),
        ("ac06 total", a["AC06_parent_record"]["total_with_parent_record"],
         b["ac06_total_with_parent_record"]),
    ]
    for label, x, y in pairs:
        check("agree_%s" % label.replace(" ", "_"), x == y, "A=%s B=%s" % (x, y))
    # Set equality, not count equality, on the row-id sets.
    check("ac06_missing_sets_identical",
          set(a["AC06_parent_record"]["without_parent_in_parent_artifact"])
          == set(b["ac06_missing_in_parent_artifact"]), "")
    check("ac04_addendum_sets_identical",
          set(a["AC04_synonyms_and_primary_term"]["addendum_rows"])
          == set(A.supplied_ac04_rows()), "")
    check("entries_per_lane_identical",
          a["AC01_lane_coverage"]["entries_per_lane"] == b["entries_per_lane"], "")
    check("ac06_status_identical",
          a["AC06_parent_record"]["verification_status_in_parent_artifact"]
          == b["ac06_verification_status"], "")
    return a, b


def test_ac01(a):
    c = a["AC01_lane_coverage"]
    check("ac01_eleven_items", c["row_items"] == 11, str(c["row_items"]))
    check("ac01_eleven_lanes", c["lane_headings"] == 11, str(c["lane_headings"]))
    check("ac01_injective", c["binding_is_injective_both_ways"], json.dumps(c))
    check("ac01_no_unbound", not c["unbound_row_items"], str(c["unbound_row_items"]))
    check("ac01_lanes_non_empty", c["min_entries_in_a_lane"] >= 5,
          str(c["min_entries_in_a_lane"]))


def test_ac03_ac04_ac06(a):
    c3 = a["AC03_canonical_preference"]
    check("ac03_no_violations", not c3["violations"], json.dumps(c3["violations"]))
    check("ac03_antecedent_non_vacuous", c3["antecedent_rows_exact_match"] > 0, "")
    check("ac03_outside_antecedent_counted_not_judged",
          c3["rows_outside_antecedent"] > 0, "")

    c4 = a["AC04_synonyms_and_primary_term"]
    check("ac04_no_unresolved", not c4["unresolved"], json.dumps(c4["unresolved"]))
    check("ac04_addendum_is_minimal", c4["resolved_by_addendum"] == 2,
          "the addendum must supply exactly the two rows the parent leaves open")
    check("ac04_parent_owns_the_rest", c4["resolved_by_frozen_parent"] == 38,
          str(c4["resolved_by_frozen_parent"]))

    c6 = a["AC06_parent_record"]
    check("ac06_all_rows_have_a_parent", c6["total_with_parent_record"] == c6["rows"],
          "%s of %s" % (c6["total_with_parent_record"], c6["rows"]))
    check("ac06_ac05_not_in_scope", c6["ac05_in_scope"] is False, "")
    check("ac06_verification_split_disclosed",
          c6["verification_status_in_parent_artifact"].get("CITE-TF", 0) > 0
          and c6["verification_status_in_parent_artifact"].get("VERIFIED", 0) > 0,
          json.dumps(c6["verification_status_in_parent_artifact"]))
    # The AC05 firewall: nothing in this package may claim verification.
    for path in sorted(HERE.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        check("no_verified_claim_in_%s" % path.name,
              "CITATIONS_VERIFIED" not in text or "Forbidden" in text
              or "forbidden" in text or "NOT" in text,
              "%s appears to claim citation verification" % path.name)
    add = (HERE / "AC_CROSSWALK_ADDENDUM_V1.md").read_text(encoding="utf-8")
    check("addendum_marks_everything_cite_tf",
          add.count("CITE-TF") >= 8 and "AC05 stays open" in add, "")


def test_ac07_stays_open(a):
    f = a["AC07_feasibility"]
    check("ac07_six_kinds", f["kind_count"] == 6, str(f["kind_count"]))
    check("ac07_not_earned", f["rule_types_the_declared_set"] is False, "")
    check("ac07_reason_recorded", f["undetermined_count"] == 4,
          str(f["undetermined_count"]))
    check("ac07_verdict_says_open", "NOT EARNED" in f["verdict"], "")


def test_hostiles_and_null(a):
    for h in a["hostiles"]:
        check("hostile_detected_%s" % h["name"], bool(h["detected"]), json.dumps(h))
        check("hostile_moved_%s" % h["name"], h["before"] != h["after"], json.dumps(h))
    check("hostile_count", a["hostiles_total"] >= 6, str(a["hostiles_total"]))
    n = a["null"]
    check("null_trials", n["trials"] == 200, str(n["trials"]))
    check("null_never_fully_matches", n["random_permutations_fully_matching"] == 0,
          json.dumps(n))
    check("null_non_vacuous", n["max_random_matches"] > 0, json.dumps(n))
    check("null_true_binding_total", n["true_binding_matches"] == n["items"], "")


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
    for key in ("AC01_lane_coverage", "AC03_canonical_preference",
                "AC04_synonyms_and_primary_term", "AC06_parent_record",
                "AC07_feasibility", "null"):
        check("receipt_%s" % key, stored[key] == a[key], "%s drifted" % key)


def main():
    test_rows_are_byte_identical_to_the_freeze()
    test_anti_invention_guard()
    test_route_b_is_independent()
    a, b = test_routes_agree()
    test_ac01(a)
    test_ac03_ac04_ac06(a)
    test_ac07_stays_open(a)
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
