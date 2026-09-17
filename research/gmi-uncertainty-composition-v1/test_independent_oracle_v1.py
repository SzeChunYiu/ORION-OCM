#!/usr/bin/env python3
"""Tests for REV-L46 route 2 (gmi-uncertainty-composition-v1).

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

    def test_matrix_image(self):
        d0 = (0, 1, 2)
        d1 = ("a", "b")
        r0 = ((0, "a"), (1, "a"), (2, "b"))
        self.assertEqual(oracle.image_by_matrix(r0, d0, d1, (0, 2)), ("a", "b"))
        self.assertEqual(oracle.image_by_matrix(r0, d0, d1, (1,)), ("a",))
        self.assertEqual(oracle.image_by_matrix(r0, d0, d1, ()), ())

    def test_matrix_associativity_certificate(self):
        c = oracle.exhaustive_uc1_bitmask()
        self.assertEqual(c["cases"], 1024)
        self.assertEqual(c["failures"], 0)
        self.assertTrue(c["all_hold"])

    def test_coverage_bound(self):
        self.assertEqual(oracle.coverage_bound_lcm(), F(187, 200))
        self.assertTrue(oracle.nested_witness_attains(F(187, 200)))

    def test_query_identification(self):
        vals = (10, 20, 30, 40)
        self.assertEqual(oracle.identify_query(vals, lambda x: x % 2 == 0),
                         "IDENTIFIED_TRUE")
        self.assertEqual(oracle.identify_query(vals, lambda x: x > 25),
                         "CANNOT_IDENTIFY")
        self.assertEqual(oracle.identify_query(vals, lambda x: x <= 40),
                         "IDENTIFIED_TRUE")
        self.assertEqual(oracle.identify_query((), lambda x: True),
                         "INCONSISTENT_EMPTY_IMAGE")

    def test_hostile_spaces(self):
        h = oracle.hostile_spaces()
        d = h["disjoint_failures"]
        self.assertEqual(d["true_joint_good"], "1/2")
        self.assertEqual(d["union_bound_lower"], "1/2")
        self.assertTrue(d["union_bound_is_attained"])
        self.assertEqual(d["independence_product"], "9/16")
        self.assertTrue(d["product_is_unsound_lower_bound"])
        ov = h["overlapping_failures"]
        self.assertEqual(ov["true_joint_good"], "3/4")
        self.assertTrue(ov["union_bound_is_conservative"])

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
