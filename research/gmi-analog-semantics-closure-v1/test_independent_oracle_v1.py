#!/usr/bin/env python3
"""Tests for REV-L46 route 2 (gmi-analog-semantics-closure-v1).

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

    def test_case_count_arithmetic(self):
        self.assertEqual(oracle.case_count_arithmetic(), 162)

    def test_vertex_identity_and_extension(self):
        c = oracle.multiaffine_vertex_identity()
        self.assertTrue(c["vertex_grid_agrees"])
        self.assertTrue(c["non_vertex_axis_affine"])

    def test_interval_validity(self):
        self.assertTrue(oracle.interval_validity_algebraic())

    def test_euler_steps_exact(self):
        self.assertEqual(oracle.euler_steps_exact(F(1), F(1), F(1), F(1, 100)), 172)
        # L=0 boundary: amplification T; N = ceil(T*C*T/eps) = ceil(1/eps)
        # (route-2 general form uses the series for e^{LT}-1; at L=0 the
        # amplification is horizon*T which the series reproduces as 0->0;
        # guard: this control uses the explicit T factor)
        # sanity: a larger epsilon needs fewer steps
        self.assertLessEqual(
            oracle.euler_steps_exact(F(1), F(1), F(1), F(1, 10)),
            oracle.euler_steps_exact(F(1), F(1), F(1), F(1, 100)))

    def test_series_bounds(self):
        s = oracle.exp_minus_one_series(10)
        t = oracle.series_tail_bound(10)
        # 1.71828... < e-1 < 1.71828... + tiny tail
        self.assertTrue(F(1718281, 1000000) < s)
        self.assertTrue(s + t < F(1718282, 1000000))

    def test_structural(self):
        s = oracle.structural_checks()
        self.assertEqual(s["ledger_rows"], 2)
        self.assertTrue(s["ledger_all_green"])
        self.assertEqual(s["schema_required_count"], 8)
        self.assertTrue(s["accounting_covers_required_12"])

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
