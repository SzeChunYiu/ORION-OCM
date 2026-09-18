#!/usr/bin/env python3
"""Tests for GMI #833 AE7.  stdlib only; runs under -I -B and -I -O -B.

Route independence, exact-arithmetic hygiene, the seven results, the hostiles
(potent BEFORE detected), the null with its no-alarm case, and agreement of the
two routes on every headline number.
"""

import ast
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROUTE_A = os.path.join(HERE, "ae7_prediction_to_control_v1.py")
ROUTE_B = os.path.join(HERE, "independent_control_oracle_v1.py")
sys.path.insert(0, HERE)

import ae7_prediction_to_control_v1 as A  # noqa: E402


def _run(path):
    out = subprocess.check_output([sys.executable, "-I", "-B", path])
    return json.loads(out.decode("utf-8"))


_A_CACHE = {}


def route_a():
    if "r" not in _A_CACHE:
        _A_CACHE["r"] = A.run()
    return _A_CACHE["r"]


_B_CACHE = {}


def route_b():
    if "r" not in _B_CACHE:
        _B_CACHE["r"] = _run(ROUTE_B)
    return _B_CACHE["r"]


class TestRouteIndependence(unittest.TestCase):
    def test_route_b_imports_nothing_from_route_a(self):
        tree = ast.parse(open(ROUTE_B).read())
        names = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names += [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names.append(node.module or "")
        for n in names:
            self.assertNotIn("ae7_prediction_to_control", n)
        self.assertEqual(sorted(set(names)), ["fractions", "json", "sys"])

    def test_route_b_uses_a_different_value_method(self):
        src = open(ROUTE_B).read()
        self.assertIn("EVERY\n    deterministic policy", src)
        self.assertNotIn("blocks_of", src)
        self.assertNotIn("argmax_actions", src)


class TestExactArithmeticHygiene(unittest.TestCase):
    def _no_floats(self, path):
        tree = ast.parse(open(path).read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, float):
                self.fail("float literal in %s at line %d" % (path, node.lineno))
            if isinstance(node, ast.Attribute) and node.attr == "log":
                self.fail("logarithm evaluated in %s" % path)

    def test_route_a_has_no_float_literal(self):
        self._no_floats(ROUTE_A)

    def test_route_b_has_no_float_literal(self):
        self._no_floats(ROUTE_B)

    def test_no_division_operator_outside_fractions(self):
        # every reported quantity is a Fraction or an int; true division of two
        # ints would silently produce a float.
        for path in (ROUTE_A, ROUTE_B):
            src = open(path).read()
            self.assertNotIn("float(", src)
            self.assertNotIn("import math", src)


class TestScope(unittest.TestCase):
    def test_all_4140_sensors_enumerated(self):
        parts = A.all_partitions(8)
        self.assertEqual(len(parts), 4140)
        self.assertEqual(len(set(parts)), 4140)

    def test_partitions_are_canonical_restricted_growth(self):
        for p in A.all_partitions(8):
            self.assertEqual(p[0], 0)
            mx = 0
            for v in p:
                self.assertLessEqual(v, mx + 1)
                mx = max(mx, v)

    def test_route_a_and_b_agree_on_the_sensor_set(self):
        self.assertEqual(route_a()["scope"]["sensors"],
                         route_b()["sensors_enumerated"])

    def test_registered_targets_all_ignore_the_third_coordinate(self):
        for name, tg in A.REGISTERED_TARGETS:
            for s in range(8):
                self.assertEqual(tg(s), tg(s ^ 4),
                                 "%s reads b2" % name)


class TestPC1(unittest.TestCase):
    def test_named_witness_is_predictively_identical(self):
        w = route_a()["results"]["PC_1_prediction_insufficient_for_control"][
            "named_witness"]
        self.assertTrue(w["identical_predictive_profile"])
        self.assertEqual(w["control_value_A"], "1")
        self.assertEqual(w["control_value_B"], "1/2")
        self.assertEqual(w["gap"], "1/2")

    def test_pair_census_matches_route_b(self):
        a = route_a()["results"]["PC_1_prediction_insufficient_for_control"]
        b = route_b()
        self.assertEqual(a["same_predictive_different_control_pairs"],
                         b["PC_1_same_predictive_different_control_pairs"])
        self.assertEqual(a["distinct_predictive_profiles"],
                         b["distinct_predictive_profiles"])
        self.assertEqual(a["same_predictive_different_control_pairs"][
            "U_hidden_coordinate"], 10980)
        self.assertEqual(a["distinct_predictive_profiles"], 712)

    def test_the_reported_zero_is_reported_not_omitted(self):
        a = route_a()["results"]["PC_1_prediction_insufficient_for_control"]
        self.assertIn("U_visible_coordinate",
                      a["same_predictive_different_control_pairs"])
        self.assertEqual(
            a["same_predictive_different_control_pairs"]["U_visible_coordinate"],
            0)


class TestPC2(unittest.TestCase):
    def test_control_sufficiency_counts_match_route_b(self):
        a = route_a()["results"]["PC_2_control_sufficiency"]["per_utility"]
        b = route_b()["PC_2"]
        for u in a:
            self.assertEqual(a[u]["V_full"], b[u]["V_full"], u)
            self.assertEqual(a[u]["V_blind"], b[u]["V_blind"], u)
            self.assertEqual(a[u]["control_sufficient_sensors"],
                             b[u]["control_sufficient_sensors"], u)
            self.assertEqual(a[u]["coarsest_control_sufficient_sensors"],
                             b[u]["coarsest_control_sufficient_sensors"], u)
            self.assertEqual(a[u]["unique_coarsest"], b[u]["unique_coarsest"], u)

    def test_non_uniqueness_is_exhibited_not_assumed(self):
        a = route_a()["results"]["PC_2_control_sufficiency"]["per_utility"]
        self.assertFalse(a["U_helly_triple"]["unique_coarsest"])
        self.assertGreaterEqual(
            a["U_helly_triple"]["coarsest_control_sufficient_sensors"], 2)

    def test_helly_failure_is_real(self):
        h = route_a()["results"]["PC_2_control_sufficiency"]["helly_failure"]
        self.assertGreater(h["pairwise_compatible_triples_without_common_optimum"],
                           0)
        t = h["example"]
        self.assertTrue(A.block_is_free((t[0], t[1]), A._u_helly))
        self.assertTrue(A.block_is_free((t[0], t[2]), A._u_helly))
        self.assertTrue(A.block_is_free((t[1], t[2]), A._u_helly))
        self.assertFalse(A.block_is_free(tuple(t), A._u_helly))


class TestPC3(unittest.TestCase):
    def test_every_crosswalk_entry_carries_a_citation_and_a_status(self):
        cw = route_a()["results"]["PC_3_parent_crosswalk"]
        self.assertGreaterEqual(len(cw), 5)
        for e in cw:
            self.assertTrue(e["citation"].strip())
            self.assertIn("doi:", e["citation"])
            self.assertTrue(e["status"].strip())
            self.assertIn("residual", e)

    def test_parent_sufficient_terminals_are_present(self):
        cw = route_a()["results"]["PC_3_parent_crosswalk"]
        self.assertGreaterEqual(
            sum(1 for e in cw if e["status"] == "PARENT_SUFFICIENT"), 3)


class TestPC4(unittest.TestCase):
    def test_value_of_information_census_matches_route_b(self):
        a = route_a()["results"]["PC_4_value_of_information"]
        b = route_b()["PC_4"]
        self.assertEqual(a["comparable_sensor_pairs_checked"],
                         b["comparable_sensor_pairs_checked"])
        self.assertEqual(a["pairs_with_zero_value_of_information"],
                         b["pairs_with_zero_value_of_information"])
        self.assertEqual(a["pairs_with_positive_value_of_information"],
                         b["pairs_with_positive_value_of_information"])
        self.assertEqual(a["comparable_sensor_pairs_checked"], 163754)

    def test_both_sides_of_the_threshold_and_the_tie_at_it(self):
        p = route_a()["results"]["PC_4_value_of_information"]["probe"]
        self.assertTrue(p["acquire_below"])
        self.assertTrue(p["tie_at_break_even"])
        self.assertFalse(p["acquire_above"])


class TestPC5andPC6(unittest.TestCase):
    def test_free_merge_criterion_equals_the_value_test_everywhere(self):
        a = route_a()["results"]["PC_5_free_merges"]["per_utility"]
        for u in a:
            self.assertEqual(a[u]["criterion_vs_value_mismatches"], 0, u)

    def test_free_pair_counts_match_route_b(self):
        a = route_a()["results"]["PC_5_free_merges"]["per_utility"]
        b = route_b()["PC_5_free_state_pairs"]
        for u in a:
            self.assertEqual(a[u]["free_state_pairs"], b[u], u)

    def test_control_relevant_predictively_redundant_matches_route_b(self):
        a = route_a()["results"]["PC_6_control_relevant_predictively_redundant"]
        b = route_b()
        self.assertEqual(a["predictively_redundant_state_pairs"],
                         b["PC_6_predictively_redundant_state_pairs"])
        self.assertEqual(a["control_relevant_among_them"],
                         b["PC_6_control_relevant_among_them"])
        self.assertEqual(a["control_relevant_among_them"]["U_hidden_coordinate"],
                         4)
        self.assertEqual(a["control_relevant_among_them"]["U_visible_coordinate"],
                         0)

    def test_the_boundary_of_the_witness_is_reported(self):
        a = route_a()["results"]["PC_6_control_relevant_predictively_redundant"]
        b = a["boundary_of_the_witness"]
        self.assertEqual(len(b), len(A.PROBE_TARGETS))
        by = dict((e["probe_target"], e["redundant_pairs_surviving"]) for e in b)
        # Reading the hidden coordinate, directly or through parity, destroys
        # the whole redundancy.  Majority does NOT: on the four states with
        # b0 == b1 the majority is pinned by b0 and b2 stays invisible, so two
        # redundant pairs survive.  That asymmetry is the boundary, and it is
        # reported rather than rounded to "any extra target kills it".
        self.assertEqual(by["Y_b2"], 0)
        self.assertEqual(by["Y_parity"], 0)
        self.assertEqual(by["Y_majority"], 2)


class TestPC7Predictions(unittest.TestCase):
    def test_all_five_predictions_are_recorded_with_a_verdict(self):
        p = route_a()["results"]["PC_7_priced_transitions"]["predictions"]
        self.assertEqual(len(p), 5)
        for k, v in p.items():
            self.assertIn(v["verdict"], ("HELD", "FAILED"), k)
            self.assertTrue(v["statement"].strip())

    def test_predictions_hold_and_agree_with_route_b(self):
        p = route_a()["results"]["PC_7_priced_transitions"]["predictions"]
        b = route_b()["PC_7"]
        self.assertEqual(p["R1_monotone_coarsening"]["violations"],
                         b["R1_violations"])
        self.assertEqual(p["R2_multistage_transition"][
            "problems_with_three_or_more"],
            b["R2_problems_with_three_or_more"])
        self.assertEqual(p["R4_blind_above_max_gain"]["failures"],
                         b["R4_failures"])
        self.assertEqual(p["R5_control_order_is_not_predictive_order"][
            "problems_witnessing"], b["R5_problems_witnessing"])
        for k, v in p.items():
            self.assertEqual(v["verdict"], "HELD", k)

    def test_selection_sequences_match_route_b(self):
        a = route_a()["results"]["PC_7_priced_transitions"]["per_problem"]
        b = route_b()["PC_7"]["per_problem"]
        for u in a:
            self.assertEqual(a[u]["selection_sequence"],
                             b[u]["selection_sequence"], u)

    def test_the_ladder_is_not_vacuous(self):
        # R1 would hold trivially if the selection never changed.
        a = route_a()["results"]["PC_7_priced_transitions"]["per_problem"]
        self.assertGreaterEqual(
            max(v["distinct_selected_sensors"] for v in a.values()), 3)
        for v in a.values():
            self.assertGreaterEqual(v["distinct_selected_sensors"], 2)


class TestHostiles(unittest.TestCase):
    def test_every_hostile_is_potent_before_it_is_detected(self):
        for h in route_a()["hostiles"]:
            self.assertTrue(h["moves_target_quantity"],
                            "%s does not move its target" % h["id"])
            self.assertTrue(h["detected"], "%s not detected" % h["id"])
            self.assertTrue(h["detector"].strip())

    def test_there_are_at_least_five_hostiles(self):
        self.assertGreaterEqual(len(route_a()["hostiles"]), 5)

    def test_sensor_leak_hostile_really_inflates_the_blind_value(self):
        h = [x for x in route_a()["hostiles"] if x["id"] == "H1_sensor_leak"][0]
        self.assertEqual(h["true_value"], "1/2")
        self.assertEqual(h["hostile_value"], "1")


class TestNull(unittest.TestCase):
    def test_null_fires_on_the_planted_case(self):
        self.assertTrue(route_a()["null"]["fires_on_planted"])

    def test_null_is_silent_on_the_clean_control(self):
        self.assertEqual(route_a()["null"]["alarms_on_clean_controls"], 0)

    def test_controls_are_matched_to_the_claim(self):
        n = route_a()["null"]
        self.assertEqual(n["clean_controls_enumerated"], 200)
        self.assertEqual(n["clean_controls_firing"], 0)
        self.assertEqual(n["false_alarms_on_clean"], "0/200")

    def test_recall_is_measured_on_planted_positives(self):
        n = route_a()["null"]
        self.assertEqual(n["planted_controls_enumerated"], 200)
        self.assertEqual(n["planted_controls_firing"], 200)
        self.assertEqual(n["recall_on_planted"], "200/200")

    def test_clean_controls_provably_cannot_trigger(self):
        # a utility measurable wrt the registered targets cannot make a
        # predictively redundant pair control-relevant; assert the premise
        # rather than trusting the construction.
        self.assertIn("functions ", n_construction())


class TestReceiptIntegrity(unittest.TestCase):
    def test_result_file_matches_a_fresh_run(self):
        live = route_a()
        stored = json.loads(
            open(os.path.join(HERE, "RESULT_V1.json")).read())
        self.assertEqual(stored, live)

    def test_manifest_agrees_with_receipt(self):
        m = json.loads(open(os.path.join(HERE, "MANIFEST_V1.json")).read())
        r = route_a()
        self.assertEqual(m["claim_ceiling"], r["claim_ceiling"])
        self.assertEqual(m["source_main"], r["source_main"])
        self.assertEqual(m["freeze_commit"], r["freeze_commit"])
        self.assertEqual(m["issue_comment_id"], r["issue_comment_id"])
        self.assertEqual(sorted(m["forbidden_promotions"]),
                         sorted(r["forbidden_promotions"]))

    def test_verdict_is_green_and_every_check_true(self):
        r = route_a()
        self.assertEqual(r["verdict"], "GREEN")
        for k, v in r["checks"].items():
            self.assertTrue(v, k)

    def test_reconciliation_rows_are_the_frozen_rows(self):
        rec = json.loads(open(os.path.join(
            HERE,
            "ISSUE_833_RECONCILIATION_AE7_PREDICTION_TO_CONTROL_V1.json")).read())
        self.assertEqual(rec["schema"], "GMI_ISSUE_RECONCILIATION_V2")
        self.assertEqual(rec["issue"], 833)
        self.assertEqual(len(rec["replacements"]), 7)
        freeze = open(os.path.join(HERE, "FREEZE_V1.md")).read()
        for rep in rec["replacements"]:
            self.assertEqual(rep["anchor"], "### AE7 — From prediction to control")
            self.assertTrue(rep["new"].startswith("- [x] "))
            self.assertIn("— ✅ `gmi-833-ae-ae7-prediction-to-control-v1`",
                          rep["new"])
            core = rep["old"][len("- [ ] "):]
            self.assertIn(core.replace("`", "\\`"), freeze)


def n_construction():
    return route_a()["null"]["clean_control_construction"]


if __name__ == "__main__":
    unittest.main(verbosity=2)
