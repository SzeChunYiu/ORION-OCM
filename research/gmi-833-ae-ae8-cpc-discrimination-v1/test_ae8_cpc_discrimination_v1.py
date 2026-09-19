#!/usr/bin/env python3
"""Tests for AE8 (issue #833).

Every check uses a `unittest` assertion METHOD.  The bare `assert` statement is
deliberately absent: CI runs this file under `python3 -I -O -B`, which strips
`assert`, and a test built on it would become a vacuous pass.  The last test
proves that absence by parsing this file and both routes.

Run:
  python3 -I -B  research/gmi-833-ae-ae8-cpc-discrimination-v1/test_ae8_cpc_discrimination_v1.py -v
  python3 -I -O -B research/gmi-833-ae-ae8-cpc-discrimination-v1/test_ae8_cpc_discrimination_v1.py -v
"""
from __future__ import annotations

import ast
import importlib.util
import json
import os
import subprocess
import sys
import unittest
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROUTE_A = os.path.join(HERE, "ae8_cpc_discrimination_v1.py")
ROUTE_B = os.path.join(HERE, "independent_cpc_oracle_v1.py")
SELF = os.path.abspath(__file__)
RESULT = os.path.join(HERE, "RESULT_V1.json")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


A = _load("ae8_route_a", ROUTE_A)


def _run(path, flags=()):
    cmd = [sys.executable, "-I", "-B"] + list(flags) + [path]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout, p.stderr


class RegisterCustody(unittest.TestCase):
    def test_digest(self):
        reg = A.load_register()
        self.assertEqual(reg["package"], "gmi-833-ae-ae8-cpc-discrimination-v1")
        self.assertEqual(reg["issue_comment_id"], 5692689542)
        self.assertEqual(len(reg["registered_constants"]["LGRID"]), 45)

    def test_tampered_register_is_refused(self):
        reg = A.load_register()
        bad = dict(reg)
        bad["registered_constants"] = dict(reg["registered_constants"])
        bad["registered_constants"]["null_trials"] = 7
        path = os.path.join(HERE, "_tampered.json")
        with open(path, "w") as fh:
            fh.write(json.dumps(bad))
        try:
            with self.assertRaises(RuntimeError):
                A.load_register(path)
        finally:
            os.remove(path)


class ExactLogarithms(unittest.TestCase):
    def test_sign_of_a_known_combination(self):
        # log2(3) - log2(2) > 0 and log2(2) - log2(3) < 0
        a = A.LogComb.log2_of(Fraction(3))
        b = A.LogComb.log2_of(Fraction(2))
        self.assertEqual((a - b).sign(), 1)
        self.assertEqual((b - a).sign(), -1)
        self.assertEqual((a - a).sign(), 0)

    def test_entropy_of_a_uniform_binary_source_is_one_bit(self):
        h = A.entropy_lc([1, 1], 2)
        one = A.LogComb.log2_of(Fraction(2))
        self.assertEqual((h - one).sign(), 0)

    def test_entropy_of_a_three_way_uniform_source_is_log2_three(self):
        h = A.entropy_lc([1, 1, 1], 3)
        three = A.LogComb.log2_of(Fraction(3))
        self.assertEqual((h - three).sign(), 0)
        self.assertEqual((h - A.LogComb.log2_of(Fraction(2))).sign(), 1)
        self.assertEqual((h - A.LogComb.log2_of(Fraction(4))).sign(), -1)

    def test_no_float_in_the_receipt(self):
        with open(RESULT, "r") as fh:
            loaded = json.load(fh)

        def walk(node, path="$"):
            if isinstance(node, float):
                self.fail("float at %s" % path)
            if isinstance(node, dict):
                for k, v in node.items():
                    walk(v, path + "." + str(k))
            if isinstance(node, list):
                for i, v in enumerate(node):
                    walk(v, path + "[%d]" % i)

        walk(loaded)


class RouteIndependence(unittest.TestCase):
    def test_route_b_does_not_import_route_a(self):
        with open(ROUTE_B, "r") as fh:
            tree = ast.parse(fh.read())
        bad = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                bad += [a.name for a in node.names if "ae8_cpc" in a.name]
            if isinstance(node, ast.ImportFrom):
                if node.module and "ae8_cpc" in node.module:
                    bad.append(node.module)
        self.assertEqual(bad, [])

    def test_route_b_only_uses_the_standard_library(self):
        with open(ROUTE_B, "r") as fh:
            tree = ast.parse(fh.read())
        mods = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                mods |= set(a.name.split(".")[0] for a in node.names)
            if isinstance(node, ast.ImportFrom) and node.module:
                mods.add(node.module.split(".")[0])
        self.assertTrue(mods <= {"hashlib", "itertools", "json", "os", "sys",
                                 "fractions", "__future__"}, sorted(mods))


class RoutesAgree(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rc, out, err = _run(ROUTE_B)
        if rc != 0:
            raise RuntimeError(err.decode("utf-8"))
        cls.b = json.loads(out.decode("utf-8"))
        with open(RESULT, "r") as fh:
            cls.a = json.load(fh)

    def test_model_space_and_grid(self):
        self.assertEqual(self.a["results"]["model_space_size"],
                         self.b["model_space_size"])
        self.assertEqual(self.a["results"]["grid_size"], self.b["grid_size"])
        self.assertEqual(self.a["results"]["grid_size"], 45)

    def test_preferences_agree(self):
        self.assertEqual(self.a["results"]["gmi_preference"],
                         self.b["gmi_preference"])
        self.assertEqual(self.a["results"]["gmi_preference_term_only"],
                         self.b["gmi_preference_term_only"])

    def test_agreement_vectors_agree(self):
        self.assertEqual(self.a["results"]["cpc_agreement_by_lambda_index"],
                         self.b["cpc_agreement_by_lambda_index"])
        self.assertEqual(self.a["results"]["cpc_best_agreement"],
                         self.b["cpc_best_agreement"])
        self.assertEqual(
            self.a["results"]
                  ["cpc_agreement_against_term_only_preference_by_lambda_index"],
            self.b["cpc_agreement_against_term_only_by_lambda_index"])

    def test_matrix_agrees(self):
        self.assertEqual(self.a["results"]["pairwise_agreement_matrix"],
                         self.b["pairwise_agreement_matrix"])

    def test_collisions_agree(self):
        ca = self.a["results"]["term_vector_collisions"]
        cb = self.b["term_vector_collisions"]
        self.assertEqual(sorted(ca), sorted(cb))
        for k in sorted(ca):
            self.assertEqual(ca[k]["world"], cb[k]["world"])
            self.assertEqual(ca[k]["preferred_model"], cb[k]["preferred_model"])
            self.assertEqual(ca[k]["other_model"], cb[k]["other_model"])
            self.assertEqual([ca[k]["term_vector_cost_bits"],
                              ca[k]["term_vector_predictive_loss"],
                              ca[k]["term_vector_control_regret"]],
                             cb[k]["term_vector"])

    def test_per_world_term_vectors_agree(self):
        for wn in sorted(self.b["per_world"]):
            ta = self.a["results"]["per_world"][wn]["term_vectors"]
            tb = self.b["per_world"][wn]["term_vectors"]
            self.assertEqual(sorted(ta), sorted(tb))
            for mn in sorted(ta):
                self.assertEqual([ta[mn]["cost_bits"], ta[mn]["predictive_loss"],
                                  ta[mn]["control_regret"]], tb[mn])


class Collisions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(RESULT, "r") as fh:
            cls.r = json.load(fh)

    def test_collisions_are_computed_not_stipulated(self):
        colls = self.r["results"]["term_vector_collisions"]
        self.assertTrue(colls)
        for name, c in sorted(colls.items()):
            self.assertTrue(c["equality_was_computed"])
            self.assertTrue(c["objects_differ"],
                            "colliding models are the same object: %s" % name)
            self.assertNotEqual(c["preferred_model"], c["other_model"])
            self.assertNotEqual(c["attributes_preferred"], c["attributes_other"])
            diff = [k for k in c["attributes_preferred"]
                    if c["attributes_preferred"][k] != c["attributes_other"][k]]
            self.assertEqual(diff, [name],
                             "the pair differs on more than its own attribute")

    def test_the_two_colliding_models_have_equal_term_vectors(self):
        for name, c in sorted(self.r["results"]["term_vector_collisions"].items()):
            wn = c["world"]
            tv = self.r["results"]["per_world"][wn]["term_vectors"]
            a = tv[c["preferred_model"]]
            b = tv[c["other_model"]]
            self.assertEqual(a["cost_bits"], b["cost_bits"])
            self.assertEqual(a["predictive_loss"], b["predictive_loss"])
            self.assertEqual(a["control_regret"], b["control_regret"])

    def test_irreducibility_is_reported_both_ways(self):
        irr = self.r["results"]["irreducibility"]
        self.assertEqual(sorted(irr), sorted(A.ATTR_NAMES))
        proved = [k for k, v in irr.items()
                  if v["status"] == "IRREDUCIBLE_AT_REGISTERED_SCOPE"]
        self.assertTrue(proved)
        for k, v in sorted(irr.items()):
            self.assertIn(v["status"], ("IRREDUCIBLE_AT_REGISTERED_SCOPE",
                                        "NOT_PROVED_IRREDUCIBLE"))


class NamedNumbers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(RESULT, "r") as fh:
            cls.r = json.load(fh)

    def test_verdict_and_checks(self):
        self.assertEqual(self.r["verdict"], "GREEN")
        for name, value in sorted(self.r["checks"].items()):
            self.assertTrue(value, "check failed: %s" % name)

    def test_the_baseline_is_falsifiable(self):
        res = self.r["results"]
        self.assertLess(res["bag_of_laws_worlds_covered"], res["world_count"])
        self.assertLessEqual(res["bag_of_laws_agreement"],
                             res["bag_of_laws_worlds_covered"])
        refuted = [k for k, v in res["law_coverage"].items()
                   if v["status"] == "REFUTED_ON_ROSTER"]
        valid = [k for k, v in res["law_coverage"].items() if v["valid"]]
        self.assertTrue(valid)
        self.assertEqual(sorted(set(refuted) & set(valid)), [])

    def test_classifier_ladder_is_ordered_and_consistent(self):
        res = self.r["results"]
        ladder = res["classifier_ladder"]
        self.assertEqual([x["criterion"] for x in ladder],
                         ["THEOREM", "VARIATIONAL_PRINCIPLE", "DECOMPOSITION",
                          "HEURISTIC", "SLOGAN"])
        first = next(x["criterion"] for x in ladder if x["holds"])
        self.assertEqual(res["classifier_verdict"], first)
        self.assertNotEqual(res["classifier_verdict"], "THEOREM")

    def test_master_law_claim_is_withheld_with_both_legs_reported(self):
        t = self.r["results"]["master_law_test"]
        self.assertEqual(t["master_law_claim"], "WITHHELD")
        self.assertEqual(t["terminal"], "CPC_MASTER_LAW_CLAIM_WITHHELD")
        self.assertIn("cpc_pareto_dominates_bag_of_laws", t)
        self.assertIn("worlds_where_cpc_differs_from_every_parent_principle", t)
        self.assertIn("CPC_IS_THE_GMI_MASTER_LAW", self.r["forbidden_promotions"])

    def test_rate_distortion_constraint_is_feasible(self):
        self.assertTrue(
            self.r["checks"]
                  ["rate_distortion_cardinality_constraint_feasible_everywhere"])
        for wn, pw in sorted(self.r["results"]["per_world"].items()):
            self.assertIsNotNone(pw["principle_choices"]["RATE_DISTORTION"], wn)
            self.assertTrue(any(v["codebook_cardinality"] == 1
                                for v in pw["term_vectors"].values()), wn)

    def test_observational_equivalence_is_scoped(self):
        res = self.r["results"]
        self.assertIn("OBSERVATIONALLY_EQUIVALENT_AT_REGISTERED_SCOPE",
                      res["observational_equivalence_terminal"])
        for pair in res["observationally_equivalent_pairs"]:
            a, b = pair.split("|")
            self.assertEqual(res["pairwise_agreement_matrix"][pair],
                             res["world_count"])
        self.assertIn("OBSERVATIONAL_EQUIVALENCE_IMPLIES_IDENTITY",
                      self.r["forbidden_promotions"])

    def test_disclosed_gaps_are_present(self):
        self.assertTrue(self.r["disclosed_register_gaps"])
        self.assertGreaterEqual(len(self.r["disclosed_register_gaps"]), 2)


class NullAndBounds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(RESULT, "r") as fh:
            cls.r = json.load(fh)

    def test_null_is_not_degenerate(self):
        n = self.r["null"]
        self.assertEqual(n["trials"], 200)
        hist = n["agreement_histogram"]
        self.assertGreater(len(hist), 1,
                           "the null has zero variance; the sampler is degenerate")
        self.assertEqual(sum(hist.values()), 200)

    def test_bounds_are_classified_and_falsifiable(self):
        self.assertTrue(self.r["bounds"])
        for b in self.r["bounds"]:
            self.assertIn(b["kind"], ("upper", "lower"))
            self.assertFalse(b["vacuous"], "vacuous bound: %s" % b["name"])
            self.assertTrue(b["range_derivation"])
            self.assertTrue(b["violated_by"])
            self.assertEqual(b["status"], "FALSIFIABLE")

    def test_the_vacuity_rule_fires_on_a_planted_bound(self):
        rec = A.bound_record("planted_upper", "upper", 12, 0, 12, "planted",
                             "an attaining witness", None, "none")
        self.assertTrue(rec["vacuous"])
        self.assertEqual(rec["status"], "UNFALSIFIED_BOUND")
        rec2 = A.bound_record("planted_lower", "lower", 0, 0, 12, "planted",
                              "an attaining witness", "a relaxed object", "relaxed")
        self.assertTrue(rec2["vacuous"])


class Hostiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(RESULT, "r") as fh:
            cls.r = json.load(fh)

    def test_registered_hostiles_are_potent_then_detected(self):
        reg = A.load_register()
        self.assertEqual(sorted(h["name"] for h in self.r["hostiles"]),
                         sorted(h["name"] for h in reg["hostiles"]))
        for h in self.r["hostiles"]:
            self.assertNotEqual(h["true_value"], h["perturbed_value"],
                                "hostile is inert: %s" % h["name"])
            self.assertTrue(h["potent"], "hostile not potent: %s" % h["name"])
            self.assertTrue(h["detected"], "hostile not detected: %s" % h["name"])


class Determinism(unittest.TestCase):
    def test_receipt_matches_the_live_run_in_both_modes(self):
        with open(RESULT, "rb") as fh:
            stored = fh.read()
        for flags in ([], ["-O"]):
            rc, out, err = _run(ROUTE_A, flags)
            self.assertEqual(rc, 0, err.decode("utf-8"))
            self.assertEqual(out, stored)


class NoBareAssert(unittest.TestCase):
    def test_no_assert_statement(self):
        for path in (SELF, ROUTE_A, ROUTE_B):
            with open(path, "r") as fh:
                tree = ast.parse(fh.read())
            found = [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Assert)]
            self.assertEqual(found, [], "bare assert in %s at %s" % (path, found))


if __name__ == "__main__":
    unittest.main(verbosity=2)
