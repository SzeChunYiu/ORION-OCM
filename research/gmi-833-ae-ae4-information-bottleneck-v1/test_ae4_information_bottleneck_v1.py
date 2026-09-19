#!/usr/bin/env python3
"""Tests for GMI #833 AE4.  stdlib only; runs under -I -B and -I -O -B."""

import ast
import json
import os
import subprocess
import sys
import unittest
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROUTE_A = os.path.join(HERE, "ae4_information_bottleneck_v1.py")
ROUTE_B = os.path.join(HERE, "independent_ib_oracle_v1.py")
sys.path.insert(0, HERE)

import ae4_information_bottleneck_v1 as A  # noqa: E402

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
            self.assertNotIn("ae4_information", n)
        self.assertEqual(sorted(set(names)),
                         ["fractions", "itertools", "json", "sys"])

    def test_the_two_routes_do_not_share_an_arithmetic(self):
        # Checked on the AST, not on the prose: route B's docstring says it
        # never factorises, and a substring test would be satisfied by that
        # sentence alone.
        tree = ast.parse(open(ROUTE_B).read())
        defined = set()
        called = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                defined.add(node.name)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                called.add(node.func.id)
            if isinstance(node, ast.Attribute):
                called.add(node.attr)
        for forbidden in ("factorise", "fact", "Ent", "key_fixed", "order_keys",
                          "common_D", "entropy_signature"):
            self.assertNotIn(forbidden, defined, forbidden)
            self.assertNotIn(forbidden, called, forbidden)
        self.assertIn("pow_entropy", defined)

    def test_route_b_engine_self_checks_pass(self):
        e = route_b()["engine_self_check"]
        for k, v in e.items():
            self.assertTrue(v, k)

    def test_route_b_refuses_a_scale_that_would_round(self):
        self.assertTrue(route_b()["engine_self_check"][
            "non_integral_exponent_raises"])


class TestExactArithmetic(unittest.TestCase):
    def test_no_float_literal_and_no_logarithm_anywhere(self):
        for path in (ROUTE_A, ROUTE_B):
            tree = ast.parse(open(path).read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value,
                                                                float):
                    self.fail("float literal in %s line %d" % (path,
                                                               node.lineno))
                if isinstance(node, ast.Attribute) and node.attr == "log":
                    self.fail("logarithm evaluated in %s" % path)
            self.assertNotIn("import math", open(path).read())

    def test_known_entropies_are_exact(self):
        self.assertEqual(A.entropy([F(1, 4)] * 4).as_str(), "2")
        self.assertEqual(A.entropy([F(1, 2)] * 2).as_str(), "1")
        self.assertEqual(A.entropy([F(1, 2), F(1, 4), F(1, 8), F(1, 8)]
                                   ).as_str(), "7/4")

    def test_a_non_dyadic_entropy_is_not_printed_as_a_rational(self):
        s = A.entropy([F(1, 3)] * 3).as_str()
        self.assertIn("log2(3)", s)

    def test_the_sign_test_orders_correctly(self):
        thirds = A.entropy([F(1, 3)] * 3)
        half = A.entropy([F(1, 2)] * 2)
        quarters = A.entropy([F(1, 4)] * 4)
        self.assertEqual(thirds.cmp(half), 1)
        self.assertEqual(thirds.cmp(quarters), -1)
        self.assertEqual(half.cmp(half), 0)

    def test_a_fixed_denominator_that_does_not_clear_raises(self):
        # H(3/8,3/8,1/8,1/8) carries the coefficient -3/4 on log2(3), so D = 1
        # cannot clear it and the engine must REFUSE rather than round.
        e = A.entropy([F(3, 8), F(3, 8), F(1, 8), F(1, 8)])
        self.assertEqual(e.c[3], F(-3, 4))
        self.assertRaises(ValueError, lambda: e.key_fixed(1))
        self.assertIsNotNone(e.key_fixed(4))


class TestScope(unittest.TestCase):
    def test_all_4140_deterministic_encoders(self):
        self.assertEqual(len(A.all_partitions(8)), 4140)
        self.assertEqual(route_a()["scope"]["encoders"], 4140)
        self.assertEqual(route_b()["encoders_enumerated"], 4140)

    def test_stochastic_encoders_are_declared_not_optimised(self):
        f = route_a()["results"]["IB_1_formalisation"]
        self.assertFalse(f["stochastic_encoders_optimised"])
        self.assertIn("IB_OPTIMUM_OVER_STOCHASTIC_ENCODERS_PROVED",
                      route_a()["forbidden_promotions"])


class TestIB1(unittest.TestCase):
    def test_every_symbol_has_a_parent_with_a_citation(self):
        cw = route_a()["results"]["IB_1_formalisation"]["crosswalk"]
        self.assertGreaterEqual(len(cw), 6)
        for e in cw:
            self.assertTrue(e["citation"].strip())
            self.assertTrue(e["parent"].strip())
            self.assertTrue(e["status"].strip())


class TestIB2(unittest.TestCase):
    def test_relation_totals_match_route_b(self):
        self.assertEqual(
            route_a()["results"]["IB_2_relation_over_the_beta_ladder"][
                "relation_totals"],
            route_b()["relation_totals"])

    def test_two_relations_occur_and_two_are_reported_zero(self):
        t = route_a()["results"]["IB_2_relation_over_the_beta_ladder"][
            "relation_totals"]
        self.assertEqual(sorted(t), ["EQUAL", "GMI_STRICTLY_REFINES",
                                     "IB_STRICTLY_REFINES", "INCOMPARABLE"])
        self.assertGreater(t["EQUAL"], 0)
        self.assertGreater(t["GMI_STRICTLY_REFINES"], 0)
        self.assertEqual(t["IB_STRICTLY_REFINES"], 0)
        self.assertEqual(t["INCOMPARABLE"], 0)

    def test_every_world_has_a_threshold_and_it_matches_route_b(self):
        a = route_a()["results"]["IB_2_relation_over_the_beta_ladder"][
            "per_world"]
        b = route_b()["per_world"]
        for w in a:
            self.assertIsNotNone(
                a[w]["smallest_beta_at_which_T_GMI_is_IB_optimal"], w)
            self.assertEqual(
                a[w]["smallest_beta_at_which_T_GMI_is_IB_optimal"],
                b[w]["smallest_beta_at_which_T_GMI_is_IB_optimal"], w)
            self.assertEqual(a[w]["T_GMI"], b[w]["T_GMI"], w)

    def test_the_noisy_channel_needs_a_much_larger_tradeoff(self):
        a = route_a()["results"]["IB_2_relation_over_the_beta_ladder"][
            "per_world"]
        self.assertEqual(
            a["W_noisy"]["smallest_beta_at_which_T_GMI_is_IB_optimal"], "6")
        for w in ("W_dictator", "W_pair", "W_triple"):
            self.assertEqual(
                a[w]["smallest_beta_at_which_T_GMI_is_IB_optimal"], "1")

    def test_a_non_dyadic_entropy_reaches_the_receipt(self):
        a = route_a()["results"]["IB_2_relation_over_the_beta_ladder"][
            "per_world"]
        self.assertIn("log2(3)", a["W_and"]["H_Y"])


class TestIB3(unittest.TestCase):
    def test_minimality_is_proved_not_asserted(self):
        r = route_a()["results"]["IB_3_smallest_counterexample"]
        self.assertTrue(r["minimality_proved"])
        self.assertEqual(r["smaller_sizes_with_a_counterexample"], 0)

    def test_the_stronger_counterexample_is_absent_and_reported(self):
        p = route_a()["results"]["IB_3_smallest_counterexample"][
            "proved_absence_of_the_stronger_counterexample"]
        self.assertEqual(p["instances_found"], 0)
        self.assertIsNone(p["smallest_support_size_found"])
        self.assertEqual(p["exhausted_support_sizes"], [2, 3, 4, 5, 6])
        self.assertIn("EARNED_BY_EXHAUSTION", p["status"])

    def test_the_general_statement_is_labelled_a_conjecture(self):
        p = route_a()["results"]["IB_3_smallest_counterexample"][
            "proved_absence_of_the_stronger_counterexample"]
        self.assertIn("CONJECTURE", p["conjecture_not_claimed"].upper())

    def test_the_counterexample_survives_a_nondegenerate_tradeoff(self):
        c = route_a()["results"]["IB_3_smallest_counterexample"][
            "channel_search"]
        self.assertIsNotNone(c["smallest_support_size"])
        self.assertTrue(c["minimality_proved"])
        self.assertGreaterEqual(F(c["per_size"][0]["first"]["beta"]), 1)

    def test_the_revival_chain_is_recorded(self):
        c = route_a()["results"]["IB_3_smallest_counterexample"][
            "channel_search"]
        self.assertIn("revival_record", c)
        self.assertIn("attributed", c["revival_record"])


class TestIB4toIB7(unittest.TestCase):
    def test_both_orderings_are_exhibited(self):
        r = route_a()["results"]["IB_4_relevance_versus_control"]
        self.assertGreater(r["relevance_beats_control_pairs"], 0)
        self.assertGreater(r["control_beats_relevance_pairs"], 0)

    def test_forgetting_criterion_is_exact_and_two_sided(self):
        r = route_a()["results"]["IB_5_when_forgetting_is_optimal"]
        self.assertEqual(r["criterion_mismatches"], 0)
        self.assertGreater(r["free_merges"], 0)
        self.assertGreater(r["costly_merges"], 0)

    def test_every_retention_mechanism_is_resolved(self):
        r = route_a()["results"][
            "IB_6_when_apparent_irrelevance_must_be_retained"]
        self.assertEqual(len(r["mechanisms"]), 5)
        for m in r["mechanisms"]:
            self.assertIn(m["verdict"], ("WITNESSED", "NOT_WITNESSED"),
                          m["mechanism"])
        self.assertEqual(r["witnessed"] + r["not_witnessed"], 5)

    def test_the_causal_retention_witness_really_separates(self):
        m = [x for x in route_a()["results"][
            "IB_6_when_apparent_irrelevance_must_be_retained"]["mechanisms"]
            if x["mechanism"] == "causal intervention"][0]
        self.assertEqual(m["verdict"], "WITNESSED")
        self.assertNotEqual(m["observational_contrast"],
                            m["interventional_contrast"])

    def test_two_frontiers_are_reported_separately(self):
        f = route_a()["results"]["IB_7_capacity_distortion_frontiers"]
        self.assertIn("predictive_frontier_size", f)
        self.assertIn("control_frontier_size", f)
        self.assertTrue(f["sweep_verified_against_quadratic_test_on_slice"])
        self.assertIsInstance(f["shared_encoders"], int)


class TestIB8(unittest.TestCase):
    def test_all_five_predictions_recorded_with_a_verdict(self):
        p = route_a()["results"]["IB_8_priced_crossover_predictions"][
            "predictions"]
        self.assertEqual(len(p), 5)
        for k, v in p.items():
            self.assertIn(v["verdict"], ("HELD", "FAILED"), k)

    def test_the_predictions_were_frozen_before_the_executor(self):
        r = route_a()["results"]["IB_8_priced_crossover_predictions"]
        self.assertTrue(r["frozen_before_executor"])
        self.assertEqual(r["freeze_commit"], route_a()["freeze_commit"])

    def test_the_predictions_are_evaluated_on_every_registered_world(self):
        r = route_a()["results"]["IB_8_priced_crossover_predictions"]
        self.assertEqual(r["worlds_evaluated"], len(A.WORLDS))
        self.assertEqual(len(r["per_world"]), len(A.WORLDS))

    def test_the_ladder_is_not_vacuous(self):
        r = route_a()["results"]["IB_8_priced_crossover_predictions"]
        self.assertGreaterEqual(
            max(v["distinct_selected_encoders"]
                for v in r["per_world"].values()), 3)


class TestHostilesAndNull(unittest.TestCase):
    def test_every_hostile_is_potent_before_it_is_detected(self):
        for h in route_a()["hostiles"]:
            self.assertTrue(h["moves_target_quantity"], h["id"])
            self.assertTrue(h["detected"], h["id"])

    def test_the_dyadic_only_hostile_really_inverts_the_order(self):
        h = [x for x in route_a()["hostiles"]
             if x["id"] == "H1_dyadic_only_entropy"][0]
        self.assertNotEqual(h["exact_sign"], h["hostile_sign"])
        self.assertEqual(h["exact_sign"], 1)
        self.assertEqual(h["hostile_sign"], -1)

    def test_null_is_silent_on_clean_and_recalls_every_planted(self):
        n = route_a()["null"]
        self.assertEqual(n["clean_controls_firing"], 0)
        self.assertEqual(n["planted_controls_firing"],
                         n["planted_controls_enumerated"])


class TestReceiptIntegrity(unittest.TestCase):
    def test_manifest_agrees_with_receipt(self):
        m = json.loads(open(os.path.join(HERE, "MANIFEST_V1.json")).read())
        r = route_a()
        self.assertEqual(m["claim_ceiling"], r["claim_ceiling"])
        self.assertEqual(m["source_main"], r["source_main"])
        self.assertEqual(m["freeze_commit"], r["freeze_commit"])
        self.assertEqual(m["issue_comment_id"], r["issue_comment_id"])

    def test_verdict_is_green_and_every_check_true(self):
        r = route_a()
        self.assertEqual(r["verdict"], "GREEN")
        for k, v in r["checks"].items():
            self.assertTrue(v, k)

    def test_the_map_correction_is_recorded_in_the_manifest(self):
        m = json.loads(open(os.path.join(HERE, "MANIFEST_V1.json")).read())
        self.assertEqual(len(m["map_corrections"]), 1)
        self.assertEqual(m["map_corrections"][0]["verdict"], "NOT_LOAD_BEARING")

    def test_reconciliation_rows_are_the_frozen_rows(self):
        rec = json.loads(open(os.path.join(
            HERE,
            "ISSUE_833_RECONCILIATION_AE4_INFORMATION_BOTTLENECK_V1.json"
        )).read())
        self.assertEqual(rec["schema"], "GMI_ISSUE_RECONCILIATION_V2")
        self.assertEqual(len(rec["replacements"]), 8)
        freeze = open(os.path.join(HERE, "FREEZE_V1.md")).read()
        for rep in rec["replacements"]:
            self.assertEqual(
                rep["anchor"],
                "### AE4 — Information Bottleneck / relevant-information "
                "boundary")
            self.assertTrue(rep["new"].startswith("- [x] "))
            core = rep["old"][len("- [ ] "):]
            # the freeze escapes backticks inside its heredoc-written list
            self.assertIn(core.replace("`", "\\`"), freeze)


if __name__ == "__main__":
    unittest.main(verbosity=2)
