#!/usr/bin/env python3
"""Tests for REV-L46 route 2 (gmi-learning-law-selection-v1).

Run: python3 -I -B test_independent_oracle_v1.py -v
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import independent_oracle_v1 as oracle  # noqa: E402


class TestIndependentOracle(unittest.TestCase):

    def test_infeasible_by_two_independent_counts(self):
        feasible = oracle.count_admissible_ie()
        self.assertEqual(128 - feasible, 36)
        self.assertEqual(oracle.count_infeasible_predicate_ie(), 36)

    def test_generic_census_binary_family(self):
        g = oracle.census_binary_family()
        self.assertEqual(g["census"],
                         {"infeasible": 36, "selected": 92, "undetermined": 0})
        self.assertTrue(g["binary_uniqueness_argument"])

    def test_uniform_census(self):
        u = oracle.census_uniform()
        self.assertEqual(u,
                         {"infeasible": 36, "selected": 50, "undetermined": 42})

    def test_lls3_flips(self):
        f = oracle.lls3_flips()
        self.assertEqual(f["K1_admits"], ["BAYES_UPDATE", "MIRROR_DESCENT"])
        self.assertEqual(f["K1_cheap_gradient_selects"], "MIRROR_DESCENT")
        self.assertEqual(f["K1_cheap_likelihood_selects"], "BAYES_UPDATE")
        self.assertEqual(f["K2_cheap_enum_selects"], "EXACT_SEARCH")
        self.assertEqual(f["K2_cheap_cmp_selects"], "ORDINAL_HILL_CLIMB")
        self.assertEqual(f["K3_cheap_proj_selects"], "GRADIENT_STEP")
        self.assertEqual(f["K3_cheap_norm_selects"], "MIRROR_DESCENT")

    def test_lls4_projection_hiding(self):
        p = oracle.lls4_projection_hiding()
        self.assertTrue(p["same_projection"])
        self.assertTrue(p["different_admissible_sets"])

    def test_lls5_refusals(self):
        r = oracle.lls5_refusals()
        self.assertTrue(r["empty_contract_infeasible"])
        self.assertTrue(r["missing_price_raises"])
        self.assertTrue(r["float_prices_refused"])

    def test_deferred_receipt(self):
        d = oracle.deferred_predictions_receipt()
        self.assertEqual((d["held"], d["total"]), (3, 3))
        self.assertTrue(d["receipt_digest_matches_frozen_predictions"])

    def test_crosscheck_receipt(self):
        rc = subprocess.run([sys.executable, "-I", "-B",
                             str(HERE / "l46_crosscheck_v1.py")],
                            capture_output=True, text=True)
        self.assertEqual(rc.returncode, 0, rc.stdout + rc.stderr)
        receipt = json.loads((HERE / "ORACLE_RESULT_L46_V1.json").read_text())
        self.assertEqual(receipt["verdict"], "TWO_ROUTE_CONVERTED")
        self.assertTrue(receipt["agreement"]["exact_agreement_everywhere"])
        self.assertTrue(receipt["independence_audit"]["stdlib_only"])
        self.assertTrue(receipt["negative_control"]["passed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
