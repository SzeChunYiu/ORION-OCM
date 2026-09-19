#!/usr/bin/env python3
"""Tests for AE12 (issue #833).

Every check uses a `unittest` assertion METHOD.  The bare `assert` statement is
deliberately absent from this file: the package is run under `python3 -I -O -B`
in CI, which strips `assert`, and a test built on it would become a vacuous pass
in the optimised mode.  The final test in this file proves that absence by
parsing this very file.

Run:
  python3 -I -B  research/gmi-833-ae-ae12-fep-audit-v1/test_ae12_fep_audit_v1.py -v
  python3 -I -O -B research/gmi-833-ae-ae12-fep-audit-v1/test_ae12_fep_audit_v1.py -v
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
ROUTE_A = os.path.join(HERE, "ae12_fep_audit_v1.py")
ROUTE_B = os.path.join(HERE, "independent_fep_oracle_v1.py")
TEST_SELF = os.path.abspath(__file__)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


A = _load("ae12_route_a", ROUTE_A)
B = _load("ae12_route_b", ROUTE_B)


def _run(path, extra=()):
    cmd = [sys.executable, "-I", "-B", path] + list(extra)
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.returncode, proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8")


class RegisterCustody(unittest.TestCase):
    def test_digest_matches(self):
        reg = A.load_register()
        self.assertEqual(reg["package"], "gmi-833-ae-ae12-fep-audit-v1")
        self.assertEqual(reg["issue_comment_id"], 5692689542)

    def test_digest_mismatch_is_refused(self):
        reg = A.load_register()
        tampered = dict(reg)
        tampered["registered_constants"] = dict(reg["registered_constants"])
        tampered["registered_constants"]["DMAX"] = 5
        path = os.path.join(HERE, "_tampered_register.json")
        with open(path, "w") as fh:
            fh.write(json.dumps(tampered))
        try:
            with self.assertRaises(RuntimeError):
                A.load_register(path)
        finally:
            os.remove(path)


class ExactArithmetic(unittest.TestCase):
    def test_dyadic_predicate(self):
        self.assertTrue(A.is_dyadic(Fraction(0)))
        self.assertTrue(A.is_dyadic(Fraction(1)))
        self.assertTrue(A.is_dyadic(Fraction(1, 16)))
        self.assertFalse(A.is_dyadic(Fraction(1, 3)))
        self.assertFalse(A.is_dyadic(Fraction(3, 4)))

    def test_two_log2_implementations_agree(self):
        for k in range(0, 9):
            p = Fraction(1, 2 ** k)
            self.assertEqual(A.dlog2(p), B.log2_dyadic(p))

    def test_non_dyadic_is_rejected_by_both(self):
        with self.assertRaises(ValueError):
            A.dlog2(Fraction(1, 3))
        with self.assertRaises(ValueError):
            B.log2_dyadic(Fraction(1, 3))

    def test_no_float_in_the_receipt(self):
        with open(os.path.join(HERE, "RESULT_V1.json"), "r") as fh:
            raw = fh.read()
        loaded = json.loads(raw)

        def walk(node, path="$"):
            if isinstance(node, float):
                self.fail("float found at %s" % path)
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
        offenders = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if "ae12_fep_audit" in alias.name:
                        offenders.append(alias.name)
            if isinstance(node, ast.ImportFrom):
                if node.module and "ae12_fep_audit" in node.module:
                    offenders.append(node.module)
        self.assertEqual(offenders, [])

    def test_route_b_does_not_read_route_a_by_path(self):
        with open(ROUTE_B, "r") as fh:
            src = fh.read()
        self.assertNotIn("ae12_fep_audit_v1.py", src.replace(
            "`ae12_fep_audit_v1`", ""))


class RoutesAgree(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rc, out, err = _run(ROUTE_A)
        if rc != 0:
            raise RuntimeError("route A failed: %s" % err)
        cls.a = json.loads(out)
        rc, out, err = _run(ROUTE_B)
        if rc != 0:
            raise RuntimeError("route B failed: %s" % err)
        cls.b = json.loads(out)

    def test_perception_agrees(self):
        for w in ("W_SPLIT", "W_TRI", "W_CORR"):
            pa = self.a["results"]["perception_audit"][w]["per_observation"]
            pb = self.b["perception"][w]
            self.assertEqual(sorted(pa), sorted(pb))
            for o in sorted(pa):
                self.assertEqual(pa[o]["exact_posterior"], pb[o]["exact_posterior"])
                self.assertEqual(pa[o]["argmin_q"], pb[o]["argmin_q"])
                self.assertEqual(pa[o]["min_free_energy_bits"],
                                 pb[o]["min_free_energy_bits"])
                self.assertTrue(pa[o]["argmin_equals_posterior"])
                self.assertTrue(pb[o]["argmin_equals_posterior"])
                self.assertTrue(pa[o]["min_equals_surprisal"])

    def test_mean_field_agrees(self):
        a = self.a["results"]["mean_field_restriction"]
        b = self.b["mean_field"]
        self.assertEqual(a["min_free_energy_full_bits"], b["min_full_bits"])
        self.assertEqual(a["min_free_energy_mean_field_bits"], b["min_mean_field_bits"])
        self.assertEqual(a["mean_field_excess_bits"], b["excess_bits"])
        self.assertEqual(a["mean_field_excess_bits"], "1")
        self.assertFalse(a["posterior_is_a_product"])
        self.assertFalse(b["posterior_is_a_product"])

    def test_misspecification_agrees(self):
        a = self.a["results"]["misspecification"]["per_observation"]
        b = self.b["misspecification"]
        for o in sorted(a):
            self.assertEqual(a[o]["true_posterior"], b[o]["true_posterior"])
            self.assertEqual(a[o]["model_posterior"], b[o]["model_posterior"])
            self.assertEqual(a[o]["posteriors_differ"], b[o]["posteriors_differ"])
        self.assertEqual(a["o0"]["true_posterior"], ["1/2", "1/2", "0"])
        self.assertEqual(a["o0"]["model_posterior"], ["1/2", "0", "1/2"])

    def test_preference_prior_agrees(self):
        a = self.a["results"]["preference_prior_nonexistence"]
        b = self.b["preference_prior"]
        self.assertEqual(a["efe_difference_a0_minus_a1_over_all_C"],
                         b["efe_difference_over_all_C"])
        self.assertEqual(a["efe_difference_a0_minus_a1_over_all_C"], ["1"])
        self.assertEqual(a["ambiguity_gap_a0_minus_a1_bits"], b["ambiguity_gap_bits"])
        self.assertEqual(a["registered_utility_difference"],
                         b["registered_utility_difference"])
        self.assertEqual(a["strict_contradiction_witnesses"],
                         b["strict_contradiction_witnesses"])
        self.assertTrue(a["predicted_outcomes_identical"])
        self.assertTrue(a["no_preference_prior_reproduces_utility_order"])

    def test_selectors_agree(self):
        for nm, key in (("W_DISC1", "discriminating_task_W_DISC1"),
                        ("W_AGREE1", "agreement_task_W_AGREE1")):
            a = self.a["results"][key]
            b = self.b["selectors"][nm]
            self.assertEqual(a["expected_free_energy_bits"],
                             b["expected_free_energy_bits"])
            self.assertEqual(a["expected_free_energy_choice"], b["efe_choice"])
            self.assertEqual(a["rate_distortion_cardinality_1_choice"], b["rd_choice"])
            self.assertEqual(a["cpc_choices_over_grid"], b["cpc_choices"])
            self.assertEqual(a["control_regret"], b["control_regret"])
            self.assertEqual(a["predictive_loss"], b["predictive_loss"])

    def test_blanket_agrees(self):
        a = self.a["results"]["markov_blanket"]
        b = self.b["blanket"]
        self.assertEqual(a["SYS_MB_OK"]["exists"], b["SYS_MB_OK"])
        self.assertEqual(a["SYS_MB_FAIL"]["exists"], b["SYS_MB_FAIL"])
        self.assertTrue(a["SYS_MB_OK"]["exists"])
        self.assertFalse(a["SYS_MB_FAIL"]["exists"])


class NamedNumbers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(HERE, "RESULT_V1.json"), "r") as fh:
            cls.r = json.load(fh)

    def test_verdict_and_checks(self):
        self.assertEqual(self.r["verdict"], "GREEN")
        for name, value in sorted(self.r["checks"].items()):
            self.assertTrue(value, "check failed: %s" % name)

    def test_grid_size(self):
        self.assertEqual(self.r["results"]["discriminating_task_W_DISC1"]["grid_size"],
                         45)

    def test_discrimination_numbers(self):
        d = self.r["results"]["discriminating_task_W_DISC1"]
        self.assertEqual(d["expected_free_energy_bits"], ["1", "0", "1"])
        self.assertEqual(d["expected_free_energy_choice"], "a1")
        self.assertEqual(d["rate_distortion_cardinality_1_choice"], "a0")
        self.assertEqual(d["cpc_choices_over_grid"], ["a0", "a1"])
        self.assertEqual(d["term_vector_dominations"], ["a2 dominated by a1"])
        self.assertTrue(d["no_lambda_agrees_with_both_efe_and_rd"])

    def test_agreement_numbers(self):
        a = self.r["results"]["agreement_task_W_AGREE1"]
        self.assertEqual(a["expected_free_energy_bits"], ["1", "3/2", "3"])
        self.assertEqual(a["cpc_choices_over_grid"], ["b0"])
        self.assertTrue(a["all_three_agree"])

    def test_null_numbers(self):
        n = self.r["null"]
        self.assertEqual(n["trials"], 200)
        self.assertEqual(n["exhaustive_space_size"], 27)
        self.assertEqual(n["exhaustive_controls_firing"], 2)
        self.assertEqual(n["exhaustive_firing_rate"], "2/27")
        self.assertTrue(n["planted_positive_fires"])
        self.assertEqual(n["planted_positive_gap_bits"], "1")
        self.assertEqual(n["known_clean_worlds_flagged"], [])
        self.assertTrue(n["no_alarm_on_clean"])

    def test_refutations_are_disclosed(self):
        refuted = [p for p in self.r["prospective_predictions"]
                   if p["verdict"] == "REFUTED"]
        self.assertEqual(sorted(p["id"] for p in refuted), ["AE12-P4", "AE12-P5"])
        for p in refuted:
            self.assertIn("diagnosis", p)
            self.assertTrue(p["diagnosis"]["exact_values"])
            self.assertTrue(p["diagnosis"]["earned_instead"])
            self.assertTrue(p["diagnosis"]["stage_attributed"])
        self.assertEqual(self.r["predictions_refuted"], 2)
        self.assertEqual(self.r["predictions_confirmed"], 6)

    def test_parent_sufficiency_is_marked(self):
        ps = self.r["results"]["parent_sufficiency"]
        self.assertTrue(ps)
        for entry in ps:
            self.assertEqual(entry["terminal"], "PARENT_SUFFICIENT")
            self.assertFalse(entry["novelty_claimed"])

    def test_criticisms_carry_dois_and_are_evaluated(self):
        crits = self.r["results"]["criticism_table"]
        self.assertGreaterEqual(len(crits), 4)
        for c in crits:
            self.assertTrue(c["doi"])
            self.assertIn("evaluated", c)
            self.assertTrue(c["registered_predicate"])
        self.assertTrue(any(c["evaluated"] is False for c in crits))


class Bounds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(HERE, "RESULT_V1.json"), "r") as fh:
            cls.r = json.load(fh)

    def test_every_bound_is_classified_and_falsifiable(self):
        self.assertTrue(self.r["bounds"])
        for b in self.r["bounds"]:
            self.assertIn(b["kind"], ("upper", "lower"))
            self.assertFalse(b["vacuous"], "vacuous bound: %s" % b["name"])
            self.assertTrue(b["range_derivation"])
            self.assertTrue(b["attained_by"])
            self.assertTrue(b["violated_by"])
            self.assertEqual(b["status"], "FALSIFIABLE")

    def test_the_vacuity_rule_actually_fires(self):
        """A checker that never fires is not a checker.  A lower bound sitting on
        the definitional floor must be classified vacuous even when attained."""
        rec = A.bound_record("planted", "lower", Fraction(0), Fraction(0),
                             Fraction(16), "planted range", "an attaining witness",
                             None, "none")
        self.assertTrue(rec["vacuous"])
        self.assertEqual(rec["status"], "UNFALSIFIED_BOUND")
        rec2 = A.bound_record("planted_upper", "upper", Fraction(16), Fraction(0),
                              Fraction(16), "planted range", "an attaining witness",
                              "a relaxed object", "relaxed")
        self.assertTrue(rec2["vacuous"])


class Hostiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(HERE, "RESULT_V1.json"), "r") as fh:
            cls.r = json.load(fh)

    def test_potency_then_detection(self):
        names = sorted(h["name"] for h in self.r["hostiles"])
        reg = A.load_register()
        self.assertEqual(names, sorted(h["name"] for h in reg["hostiles"]))
        for h in self.r["hostiles"]:
            self.assertTrue(h["potent"], "hostile not potent: %s" % h["name"])
            self.assertNotEqual(h["true_value"], h["perturbed_value"])
            self.assertTrue(h["detected"], "hostile not detected: %s" % h["name"])


class Determinism(unittest.TestCase):
    def test_receipt_matches_the_live_run_in_both_modes(self):
        with open(os.path.join(HERE, "RESULT_V1.json"), "rb") as fh:
            stored = fh.read()
        for extra_flags in ([], ["-O"]):
            cmd = [sys.executable, "-I", "-B"] + extra_flags + [ROUTE_A]
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual(proc.returncode, 0, proc.stderr.decode("utf-8"))
            self.assertEqual(proc.stdout, stored)

    def test_two_runs_are_byte_identical(self):
        _rc1, o1, _e1 = _run(ROUTE_A)
        _rc2, o2, _e2 = _run(ROUTE_A)
        self.assertEqual(o1, o2)


class NoBareAssert(unittest.TestCase):
    def test_no_assert_statement_in_the_test_or_the_executor(self):
        for path in (TEST_SELF, ROUTE_A, ROUTE_B):
            with open(path, "r") as fh:
                tree = ast.parse(fh.read())
            found = [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Assert)]
            self.assertEqual(found, [], "bare assert in %s at %s" % (path, found))


if __name__ == "__main__":
    unittest.main(verbosity=2)
