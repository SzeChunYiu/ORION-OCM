"""Tests for gmi-833-mtg-naturality-tiers-v1.

Calls the route-A executor's functions directly (imported by path, so the
tests run under ``python3 -I``), runs the hostiles, the null and the
no-alarm case, cross-checks ``RESULT_V1.json`` against
``ORACLE_RESULT_V1.json`` on every shared quantity, and writes
``TEST_RESULT_V1.json`` (identical under ``-O``; no bare ``assert``).
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
import unittest
from fractions import Fraction

ROOT = os.path.dirname(os.path.abspath(__file__))
TEST_SCHEMA = "GMI_833_MTG_NATURALITY_TIERS_TEST_RESULT_V1"
FREEZE_CEILING = "GMI_833_MTG_APPROXIMATE_AND_STOCHASTIC_NATURALITY_TIERS_AT_REGISTERED_FINITE_SCOPE"
FREEZE_FORBIDDEN = ["OPTIMIZER_EQUIVALENCE_PROVED", "REAL_LEARNING_DYNAMICS_VALIDATED", "BAYESIAN_OR_LATENT_UNCERTAINTY_CLAIMED", "UNIVERSAL_HYSTERESIS", "CONTINUOUS_STATE_NATURALITY_PROVED", "COMPLETE_GMI"]


def load_executor():
    spec = importlib.util.spec_from_file_location("naturality_tiers_v1", os.path.join(ROOT, "naturality_tiers_v1.py"))
    if spec is None or spec.loader is None:
        raise RuntimeError("EXECUTOR_NOT_FOUND")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


X = load_executor()
_CACHE = {}


def result():
    if "result" not in _CACHE:
        _CACHE["result"] = X.build_result()
    return _CACHE["result"]


def hostiles():
    if "hostiles" not in _CACHE:
        _CACHE["hostiles"] = X.run_hostiles()
    return _CACHE["hostiles"]


def null():
    if "null" not in _CACHE:
        _CACHE["null"] = X.run_null()
    return _CACHE["null"]


def read_json(name):
    with open(os.path.join(ROOT, name)) as fh:
        return json.load(fh)


class NaturalityTiersTests(unittest.TestCase):
    def test_hostiles_all_applicable_and_detected(self):
        h = hostiles()
        self.assertEqual(len(h), 8)
        for name, rec in h.items():
            self.assertTrue(rec["applicable"], name)
            self.assertTrue(rec["detected"], name)

    def test_hostile_names(self):
        self.assertEqual(sorted(hostiles()), sorted(["float_input_rejected", "non_row_stochastic_kernel_rejected", "non_total_map_rejected", "experience_alphabet_mismatch_rejected", "static_not_exact", "final_output_only_hostile", "deterministic_overclaim", "tampered_receipt_eps_zeroed"]))

    def test_null_zero_of_200(self):
        n = null()
        self.assertEqual(n["draws"], 200)
        self.assertEqual(n["passing"], 0)
        self.assertTrue(n["truth_rows_in_pool_family"])
        self.assertGreater(n["tv_min"], Fraction(0))

    def test_no_alarm_clean_fixture(self):
        m, n, p = X.fixture_three_state()
        c = X.classify(m, n, X.ISO_MN, X.registered_metric(n), X.REGISTERED_LEVEL)
        self.assertEqual(X.tier_name(c), "FULL")
        self.assertEqual(c["eps"], Fraction(0))
        sm, sn, _ = X.fixture_stochastic()
        self.assertEqual(X.stochastic_defect(sm, sn, X.ISO_SMSN), Fraction(0))
        rows = X.track(m, n, X.ISO_MN, X.NAT3_WORD_LENGTH)
        self.assertEqual(sum(sum(r["mismatch_vector"]) for r in rows), 0)
        self.assertTrue(all(r["final_output_agree"] for r in rows))
        self.assertEqual(X.final_output_only_check(m, n, X.ISO_MN, X.NAT3_WORD_LENGTH), 0)

    def test_eps_definition_values(self):
        m, n, p = X.fixture_three_state()
        self.assertEqual(X.naturality_defect(m, p, X.LC_MP, X.registered_metric(p)), Fraction(1, 2))
        self.assertEqual(X.naturality_defect(m, p, X.STATIC_MP, X.registered_metric(p)), Fraction(1))
        self.assertEqual(X.naturality_defect(m, p, X.LC_MP, X.discrete_metric(p.states)), Fraction(1))
        self.assertEqual(X.naturality_defect(m, n, X.COLLAPSE_MN, X.registered_metric(n)), Fraction(0))

    def test_float_rejected_everywhere(self):
        sm, sn, _ = X.fixture_stochastic()
        kern = dict(sm.kernel)
        kern[("x2", "a")] = {"x2": 1.0}
        with self.assertRaisesRegex(X.NaturalityTiersError, "PROBABILITY_NOT_FRACTION"):
            X.StochSystem("F", sm.states, sm.experiences, sm.outputs, kern)
        kern_int = dict(sm.kernel)
        kern_int[("x2", "a")] = {"x2": 1}
        with self.assertRaisesRegex(X.NaturalityTiersError, "PROBABILITY_NOT_FRACTION"):
            X.StochSystem("I", sm.states, sm.experiences, sm.outputs, kern_int)
        with self.assertRaisesRegex(X.NaturalityTiersError, "METRIC_NOT_FRACTION"):
            X.Metric("bad", ("u", "v"), {("u", "v"): 0.5})
        with self.assertRaisesRegex(X.NaturalityTiersError, "FLOAT_IN_RECEIPT"):
            X.ser({"x": 0.5})

    def test_metric_axioms_enforced(self):
        with self.assertRaisesRegex(X.NaturalityTiersError, "METRIC_TRIANGLE_VIOLATED"):
            X.Metric("bad", ("u", "v", "w"), {("u", "v"): Fraction(1, 4), ("v", "w"): Fraction(1, 4), ("u", "w"): Fraction(1)})
        with self.assertRaisesRegex(X.NaturalityTiersError, "METRIC_NOT_SYMMETRIC"):
            X.Metric("bad", ("u", "v"), {("u", "v"): Fraction(1), ("v", "u"): Fraction(1, 2)})

    def test_named_results_checks(self):
        r = result()
        self.assertEqual(r["results"], ["NAT-1", "NAT-2", "NAT-3", "NAT-4"])
        for name, val in r["checks"].items():
            self.assertTrue(val, name)
        self.assertEqual(r["verdict"], "GREEN")
        self.assertEqual(r["status"], "GREEN")

    def test_tier_strictness_registered(self):
        c = result()["counts"]
        self.assertGreater(c["nat2_registered_three_state_full"], 0)
        self.assertGreater(c["nat2_registered_three_state_exact_minus_full"], 0)
        self.assertGreater(c["nat2_registered_three_state_lc_minus_exact"], 0)
        self.assertGreater(c["nat2_registered_three_state_static_minus_lc"], 0)
        self.assertEqual(c["nat2_discrete_three_state_static_minus_lc"], 0)
        self.assertEqual(c["nat2_registered_three_state_total"], 243)
        self.assertEqual(c["nat2_registered_two_state_total"], 8)

    def test_freeze_constants(self):
        r = result()
        self.assertEqual(r["claim_ceiling"], FREEZE_CEILING)
        self.assertEqual(r["forbidden_promotions"], FREEZE_FORBIDDEN)
        self.assertEqual(r["schema"], "GMI_833_MTG_NATURALITY_TIERS_RESULT_V1")

    def test_all_counts_are_int(self):
        for k, v in result()["counts"].items():
            self.assertIs(type(v), int, k)

    def test_receipt_matches_recomputation(self):
        with open(os.path.join(ROOT, "RESULT_V1.json")) as fh:
            self.assertEqual(fh.read(), X.canonical_json(result()))

    def test_cross_route_shared_quantities(self):
        a = read_json("RESULT_V1.json")["shared_quantities"]
        b = read_json("ORACLE_RESULT_V1.json")
        self.assertEqual(b["route"], "TRAJECTORY_ENUMERATION_AND_INTEGER_MATRIX_KERNELS")
        self.assertEqual(b["status"], "GREEN")
        ob = b["shared_quantities"]
        self.assertEqual(sorted(a), sorted(ob))
        compared = 0
        for k in sorted(a):
            self.assertEqual(a[k], ob[k], k)
            compared += 1
        self.assertGreaterEqual(compared, 60)
        _CACHE["shared_quantities_compared"] = compared

    def test_no_bare_assert_in_sources(self):
        pat = re.compile(r"^\s*assert\b")
        for name in ("naturality_tiers_v1.py", "independent_oracle_v1.py", "test_naturality_tiers_v1.py"):
            with open(os.path.join(ROOT, name)) as fh:
                for line in fh:
                    self.assertIsNone(pat.match(line), name + ": " + line.strip())


def write_test_receipt() -> None:
    h = hostiles()
    n = null()
    a = read_json("RESULT_V1.json")["shared_quantities"]
    b = read_json("ORACLE_RESULT_V1.json")["shared_quantities"]
    compared = sum(1 for k in a if k in b and a[k] == b[k])
    receipt = {
        "schema": TEST_SCHEMA,
        "hostiles_total": len(h),
        "hostiles_detected": sum(1 for v in h.values() if v["detected"]),
        "hostiles_applicable": sum(1 for v in h.values() if v["applicable"]),
        "null_draws": n["draws"],
        "null_passing": n["passing"],
        "shared_quantities_compared": compared,
        "shared_quantities_total": len(a),
        "status": "GREEN",
    }
    with open(os.path.join(ROOT, "TEST_RESULT_V1.json"), "w") as fh:
        fh.write(json.dumps(receipt, indent=1, sort_keys=True) + "\n")


if __name__ == "__main__":
    outcome = unittest.main(exit=False, argv=[sys.argv[0]] + sys.argv[1:]).result
    if outcome.wasSuccessful():
        write_test_receipt()
        print("TEST_RECEIPT_WRITTEN")
    else:
        print("TEST_RECEIPT_NOT_WRITTEN")
        sys.exit(1)
