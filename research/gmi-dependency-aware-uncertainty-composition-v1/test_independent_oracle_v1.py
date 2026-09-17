#!/usr/bin/env python3
"""Tests for REV-L46 route 2 (gmi-dependency-aware-uncertainty-composition-v1).

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

    def test_xor_control(self):
        c = oracle.joint_root_xor_control()
        self.assertEqual(c["global_y"], [0])
        self.assertEqual(c["local_y"], [0, 1])
        self.assertTrue(c["strict"])

    def test_shared_ancestor_control(self):
        c = oracle.shared_ancestor_control()
        self.assertEqual(c["global_y"], [0])
        self.assertEqual(c["local_y"], [-2, 0, 2])
        self.assertTrue(c["strict"])

    def test_nonlinear_control(self):
        c = oracle.nonlinear_setvalued_control()
        self.assertEqual(c["global_s"], [0, 1])
        self.assertEqual(c["global_q"], [-1, 0, 1, 2])
        self.assertEqual(c["local_s"], [0, 1])
        self.assertEqual(c["local_q"], [-1, 0, 1, 2])
        self.assertEqual(c["coverage_lower_bound"], "19/20")

    def test_missing_relation_control(self):
        c = oracle.missing_relation_control()
        self.assertEqual(c["global_m"], ["a", "b", "c"])
        self.assertEqual(c["local_m"], ["a", "b", "c"])
        self.assertEqual(c["empty_image"], [])
        self.assertTrue(c["empty_distinct_from_missing"])

    def test_exhaustive_soundness(self):
        e = oracle.exhaustive_local_soundness_bitmask()
        self.assertEqual(e["cases"], 1024)
        self.assertEqual(e["failures"], 0)
        self.assertTrue(e["all_sound"])
        self.assertEqual(e["strict_inclusion_cases"], 24)

    def test_budgets(self):
        b = oracle.budget_controls()
        self.assertEqual(b["joint_source"]["lower"], "373/400")
        self.assertEqual(b["marginal_source"]["union_alpha"], "1/20")
        self.assertEqual(b["marginal_source"]["lower"], "373/400")

    def test_hostiles(self):
        h = oracle.marginal_dependence_hostile()
        d = h["disjoint"]
        self.assertEqual(d["true_joint_coverage"], "1/2")
        self.assertTrue(d["union_attained"])
        self.assertTrue(d["product_unsound"])
        self.assertEqual(h["overlap"]["true_joint_coverage"], "3/4")
        self.assertTrue(h["overlap"]["union_conservative"])

    def test_governance(self):
        g = oracle.governance_checks()
        self.assertTrue(g["cycle_rejected"])
        self.assertTrue(g["topological_order_ok"])

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
