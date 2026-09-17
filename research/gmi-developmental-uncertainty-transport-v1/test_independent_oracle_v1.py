#!/usr/bin/env python3
"""Tests for REV-L46 route 2 (gmi-developmental-uncertainty-transport-v1).

Run: python3 -I -B test_independent_oracle_v1.py -v
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import independent_oracle_v1 as oracle  # noqa: E402


class TestIndependentOracle(unittest.TestCase):

    def test_backward_image_matches_known_maps(self):
        # INFO: y = x+1
        img = oracle.image_backward((F(-1), F(0), F(1)),
                                    oracle.FIVE_KIND_RELATIONS["INFO"],
                                    tuple(F(v) for v in range(-4, 6)))
        self.assertEqual([str(x) for x in img], ["0", "1", "2"])
        # MORPH: y = x^2 (non-monotone source)
        img = oracle.image_backward((F(-1), F(0), F(1), F(2), F(3), F(4)),
                                    oracle.FIVE_KIND_RELATIONS["MORPH"],
                                    tuple(F(v) for v in range(-6, 18)))
        self.assertEqual([str(x) for x in img], ["0", "1", "4", "9", "16"])

    def test_chain_five_kinds(self):
        rows = oracle.chain_five_kinds()
        self.assertEqual(len(rows), 6)
        expected_values = [["-1", "0", "1"], ["0", "1", "2"], ["0", "1", "2"],
                           ["0", "1", "2", "3"], ["-1", "0", "1", "2", "3", "4"],
                           ["0", "1", "4", "9", "16"]]
        for row, exp in zip(rows, expected_values):
            self.assertEqual([str(v) for v in row["values"]], exp)
            self.assertEqual(str(row["failure_budget"]), "1/20")

    def test_allocation_partials(self):
        p = oracle.allocation_partials((1, 2, 5, 1000))
        self.assertEqual(p["1"]["closed_form"], "1/40")
        self.assertEqual(p["2"]["closed_form"], "1/30")
        self.assertEqual(p["5"]["closed_form"], "1/24")
        self.assertEqual(p["1000"]["closed_form"], "50/1001")
        self.assertEqual(p["1"]["partial"], p["1"]["closed_form"])

    def test_budget_witness(self):
        b = oracle.budget_union_bound_with_witness()
        self.assertEqual(b["failure_budget"], "13/200")
        self.assertEqual(b["coverage_lower_bound"], "187/200")
        self.assertTrue(b["attained_equals_bound"])
        self.assertTrue(b["product_differs_from_union_bound"])
        self.assertNotEqual(b["independence_product_value"], "187/200")

    def test_affine_hull_sign_directed(self):
        lo, hi = oracle.affine_hull_sign_directed(F(1, 4), F(3, 4), F(-2), F(3), F(1, 10))
        self.assertEqual((str(lo), str(hi)), ("7/5", "13/5"))
        # positive slope control
        lo2, hi2 = oracle.affine_hull_sign_directed(F(1, 4), F(3, 4), F(2), F(0), F(0))
        self.assertEqual((str(lo2), str(hi2)), ("1/2", "3/2"))
        # zero slope control
        lo3, hi3 = oracle.affine_hull_sign_directed(F(1, 4), F(3, 4), F(0), F(5), F(1, 4))
        self.assertEqual((str(lo3), str(hi3)), ("19/4", "21/4"))

    def test_nonlinear_minkowski(self):
        r = oracle.nonlinear_image_minkowski()
        self.assertEqual(r["result"], ["-1", "0", "1", "2"])
        self.assertEqual(r["squares"], ["0", "1"])

    def test_unknown_and_identifiability(self):
        u = oracle.unknown_relation_cardinality()
        self.assertEqual(u["mixed_query"], "CANNOT_IDENTIFY")
        self.assertEqual(u["constant_query"], "IDENTIFIED_TRUE")
        self.assertEqual(u["terminal"], "CANNOT_IDENTIFY_NO_RELATION")

    def test_copy_counterexample(self):
        c = oracle.copy_counterexample_measure()
        self.assertTrue(c["source_covers_surely"])
        self.assertFalse(c["copy_covers"])
        self.assertTrue(c["full_domain_covers"])

    def test_evidence_purity(self):
        self.assertTrue(oracle.chain_evidence_purity())

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
