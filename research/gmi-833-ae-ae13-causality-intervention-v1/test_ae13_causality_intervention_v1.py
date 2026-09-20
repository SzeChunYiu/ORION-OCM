#!/usr/bin/env python3
"""Tests for GMI #833 AE13.  stdlib only; runs under -I -B and -I -O -B."""

import ast
import json
import os
import subprocess
import sys
import unittest
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROUTE_A = os.path.join(HERE, "ae13_causality_intervention_v1.py")
ROUTE_B = os.path.join(HERE, "independent_causal_oracle_v1.py")
sys.path.insert(0, HERE)

import ae13_causality_intervention_v1 as A  # noqa: E402

_CACHE = {}


def route_a():
    if "a" not in _CACHE:
        _CACHE["a"] = json.loads(
            open(os.path.join(HERE, "RESULT_V1.json")).read())
    return _CACHE["a"]


def route_b():
    if "b" not in _CACHE:
        out = subprocess.check_output([sys.executable, "-I", "-B", ROUTE_B])
        _CACHE["b"] = json.loads(out.decode("utf-8"))
    return _CACHE["b"]


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
            self.assertNotIn("ae13_causality", n)
        self.assertEqual(sorted(set(names)), ["fractions", "itertools", "json",
                                              "sys"])

    def test_route_b_uses_adjustment_not_truncation(self):
        src = open(ROUTE_B).read()
        self.assertIn("do_by_adjustment", src)
        self.assertNotIn("truncated_numerators", src)
        self.assertNotIn("trunc_fast", src)

    def test_route_b_decides_equivalence_by_d_separation(self):
        src = open(ROUTE_B).read()
        self.assertIn("d_separated", src)
        self.assertNotIn("v_structures", src)


class TestExactArithmetic(unittest.TestCase):
    def test_no_float_literals_anywhere(self):
        for path in (ROUTE_A, ROUTE_B):
            tree = ast.parse(open(path).read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value,
                                                                float):
                    self.fail("float literal in %s line %d" % (path,
                                                               node.lineno))

    def test_no_math_import(self):
        for path in (ROUTE_A, ROUTE_B):
            self.assertNotIn("import math", open(path).read())

    def test_truncated_joints_are_probability_distributions(self):
        for dag in A.DAGS:
            sl = A.cpt_slots(dag)
            plan = A.compile_dag(dag, sl)
            theta = tuple((i % 5) for i in range(len(sl)))
            for var in range(A.NV):
                for val in (0, 1):
                    t = A.trunc_fast(plan, theta, var, val)
                    self.assertEqual(sum(t), A.TRUNC_DEN,
                                     "do(%d=%d) does not sum to 1" % (var, val))

    def test_observational_joints_are_probability_distributions(self):
        for dag in A.DAGS:
            sl = A.cpt_slots(dag)
            plan = A.compile_dag(dag, sl)
            for theta in ((1,) * len(sl), (3,) * len(sl), (2,) * len(sl)):
                self.assertEqual(sum(A.joint_fast(plan, theta)), A.JOINT_DEN)


class TestScope(unittest.TestCase):
    def test_twenty_five_labelled_dags(self):
        self.assertEqual(len(A.DAGS), 25)
        self.assertEqual(route_b()["labelled_dags"], 25)

    def test_eleven_markov_classes_by_two_independent_characterisations(self):
        self.assertEqual(len(A.MCLASSES), 11)
        self.assertEqual(route_b()["equivalence_classes"], 11)
        self.assertEqual(sorted(len(c) for c in A.MCLASSES),
                         route_b()["class_size_multiset"])

    def test_route_a_and_b_agree_on_class_composition(self):
        self.assertEqual(
            route_a()["results"]["CI_1_observational_non_identification"][
                "classes_with_more_than_one_dag"],
            route_b()["classes_with_more_than_one_dag"])
        self.assertEqual(
            route_a()["results"]["CI_1_observational_non_identification"][
                "singleton_classes_which_ARE_identified"],
            route_b()["singleton_classes"])


class TestCI1(unittest.TestCase):
    def test_every_multi_dag_class_has_a_witness(self):
        c = route_a()["results"]["CI_1_observational_non_identification"]
        self.assertEqual(c["classes_with_a_non_identification_witness"],
                         c["classes_with_more_than_one_dag"])

    def test_singleton_classes_are_reported_as_identified(self):
        c = route_a()["results"]["CI_1_observational_non_identification"]
        self.assertGreater(c["singleton_classes_which_ARE_identified"], 0)
        for e in c["per_class"]:
            if e["dags_in_class"] == 1:
                self.assertEqual(
                    e["cross_dag_pairs_with_identical_joint_and_different_"
                      "intervention"], 0)

    def test_the_claim_carries_its_quantifier(self):
        c = route_a()["results"]["CI_1_observational_non_identification"]
        self.assertIn("not 'never'", c["claim"])

    def test_every_witness_really_has_an_identical_joint(self):
        c = route_a()["results"]["CI_1_observational_non_identification"]
        n = 0
        for e in c["per_class"]:
            w = e["witness"]
            if w is None:
                continue
            n += 1
            self.assertNotEqual(w["dag_1"], w["dag_2"])
            self.assertNotEqual(w["query_vector_1"], w["query_vector_2"])
            self.assertEqual(
                sum(F(x) for x in w["identical_observational_joint"]), 1)
        self.assertGreaterEqual(n, 7)


class TestCI2(unittest.TestCase):
    def test_named_class_matches_route_b(self):
        a = route_a()["results"]["CI_2_equivalence_class"]
        b = route_b()["CI_2"]
        self.assertEqual(a["fixed_observational_joint"],
                         b["fixed_observational_joint"])
        self.assertEqual(a["members_of_the_other_dag_reproducing_it"],
                         b["members_of_the_other_dag_reproducing_it"])
        self.assertEqual(a["identification_interval_low"],
                         b["identification_interval_low"])
        self.assertEqual(a["identification_interval_high"],
                         b["identification_interval_high"])

    def test_the_two_dags_are_markov_equivalent_and_disagree(self):
        a = route_a()["results"]["CI_2_equivalence_class"]
        self.assertTrue(a["markov_equivalent"])
        self.assertTrue(a["joint_sums_to_one"])
        self.assertTrue(a["interventional_answers_differ"])


class TestCI3CI4(unittest.TestCase):
    def test_requirement_verdict_flips_exactly_at_the_threshold(self):
        r = route_a()["results"]["CI_3_CI_4_requirement_and_price"]
        self.assertTrue(r["required_below_tolerance"])
        self.assertFalse(r["required_at_tolerance"])
        self.assertFalse(r["required_above_tolerance"])
        self.assertTrue(r["flip_verified"])

    def test_intervention_is_not_always_worth_its_cost(self):
        r = route_a()["results"]["CI_3_CI_4_requirement_and_price"]
        self.assertGreater(r["groups_with_zero_value_of_intervention"], 0)
        w = r["named_zero_value_specification"]
        self.assertIsNotNone(w)
        self.assertEqual(w["value_of_intervention"], "0")
        self.assertGreaterEqual(len(w["dags_realising_the_joint"]), 2)

    def test_every_query_reports_both_group_counts(self):
        r = route_a()["results"]["CI_3_CI_4_requirement_and_price"]
        for name, d in r["per_query"].items():
            self.assertEqual(
                d["groups_with_a_non_degenerate_interval"]
                + d["groups_identified_observationally"],
                d["joint_groups_examined"], name)


class TestCI5(unittest.TestCase):
    def test_relation_counts_match_route_b(self):
        a = route_a()["results"]["CI_5_predictive_versus_causal_state"]
        b = route_b()["CI_5"]
        self.assertEqual(a["relation_counts"], b["relation_counts"])
        self.assertEqual(a["excluded_non_positive"], b["excluded_non_positive"])

    def test_all_four_relations_are_reported_including_the_zero(self):
        a = route_a()["results"]["CI_5_predictive_versus_causal_state"]
        self.assertEqual(sorted(a["relation_counts"]),
                         ["CAUSAL_STRICTLY_REFINES", "EQUAL", "INCOMPARABLE",
                          "PREDICTIVE_STRICTLY_REFINES"])
        self.assertIn("proof_of_the_zero", a)

    def test_the_two_states_genuinely_differ(self):
        a = route_a()["results"]["CI_5_predictive_versus_causal_state"]
        self.assertGreater(a["relation_counts"]["INCOMPARABLE"], 0)
        self.assertGreater(a["relation_counts"]["PREDICTIVE_STRICTLY_REFINES"],
                           0)


class TestCI6(unittest.TestCase):
    def test_every_entry_carries_a_citation(self):
        e = route_a()["results"]["CI_6_parent_crosswalk"]["entries"]
        self.assertGreaterEqual(len(e), 6)
        for x in e:
            self.assertTrue(x["citation"].strip())
            self.assertTrue(x["status"].strip())
            self.assertIn("residual", x)

    def test_the_two_senses_of_causal_state_are_kept_apart(self):
        c = route_a()["results"]["CI_6_parent_crosswalk"]
        self.assertTrue(c["separates_computational_mechanics_from_pearl"])
        self.assertGreaterEqual(c["parent_sufficient_terminals"], 3)

    def test_conflation_is_a_registered_forbidden_promotion(self):
        self.assertIn(
            "COMPUTATIONAL_MECHANICS_CAUSAL_STATE_IS_PEARLIAN_CAUSAL_STATE",
            route_a()["forbidden_promotions"])


class TestHostiles(unittest.TestCase):
    def test_every_hostile_is_potent_before_it_is_detected(self):
        for h in route_a()["hostiles"]:
            self.assertTrue(h["moves_target_quantity"], h["id"])
            self.assertTrue(h["detected"], h["id"])

    def test_the_section_s_own_error_is_a_hostile(self):
        h = [x for x in route_a()["hostiles"]
             if x["id"] == "H1_read_intervention_off_observation"][0]
        self.assertEqual(h["true_ACE_C_on_A"], "0")
        self.assertNotEqual(h["hostile_ACE_C_on_A"], "0")
        self.assertEqual(h["hostile_ACE_C_on_A"],
                         route_b()["H1_check"]["observational_contrast"])
        self.assertEqual(h["true_ACE_C_on_A"],
                         route_b()["H1_check"]["true_ACE_C_on_A"])

    def test_conditioning_instead_of_truncating_really_moves_the_answer(self):
        h = [x for x in route_a()["hostiles"]
             if x["id"] == "H3_condition_instead_of_truncate"][0]
        self.assertNotEqual(h["true_p_do"], h["hostile_p_cond"])


class TestNull(unittest.TestCase):
    def test_no_alarm_on_the_identified_controls(self):
        n = route_a()["null"]
        self.assertEqual(n["clean_controls_firing"], 0)
        self.assertEqual(n["alarms_on_clean_controls"], 0)
        self.assertGreaterEqual(n["clean_controls_enumerated"], 200)

    def test_full_recall_on_the_planted_positives(self):
        n = route_a()["null"]
        self.assertEqual(n["planted_controls_firing"],
                         n["planted_controls_enumerated"])

    def test_the_planted_premise_is_verified_not_asserted(self):
        n = route_a()["null"]
        self.assertEqual(n["planted_controls_whose_twin_was_verified_to_exist"],
                         n["planted_controls_enumerated"])


class TestReceiptIntegrity(unittest.TestCase):
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
            "ISSUE_833_RECONCILIATION_AE13_CAUSALITY_INTERVENTION_V1.json"
        )).read())
        self.assertEqual(rec["schema"], "GMI_ISSUE_RECONCILIATION_V2")
        self.assertEqual(len(rec["replacements"]), 6)
        self.assertEqual(len(rec["not_closed"]), 1)
        freeze = open(os.path.join(HERE, "FREEZE_V1.md")).read()
        for rep in rec["replacements"]:
            self.assertEqual(rep["anchor"], "### AE13 — Causality and intervention")
            self.assertTrue(rep["new"].startswith("- [x] "))
            self.assertIn(rep["old"][len("- [ ] "):], freeze)

    def test_the_tier2_morphology_row_is_declared_not_closed(self):
        rec = json.loads(open(os.path.join(
            HERE,
            "ISSUE_833_RECONCILIATION_AE13_CAUSALITY_INTERVENTION_V1.json"
        )).read())
        self.assertIn("morphology", rec["not_closed"][0]["row"].lower())
        self.assertIn("gmi-833-ae-morphology-sweep-v1",
                      rec["not_closed"][0]["reason"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
