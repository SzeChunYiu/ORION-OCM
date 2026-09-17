#!/usr/bin/env python3
"""Tests for REV-L46 route 2 (gmi-structural-threshold-repair-v1).

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

    def test_parity_by_gf2(self):
        p = oracle.parity_by_gf2()
        self.assertEqual(p["all8_outputs"], [0, 1, 1, 0, 1, 0, 0, 1])
        self.assertTrue(p["equals_gf2_parity"])
        self.assertTrue(p["indicator_identity_proven"])
        self.assertEqual(p["witness_opcode_count"], 39)

    def test_configuration_search(self):
        cfg = oracle.configuration_search()
        self.assertEqual(cfg["shape_A_minimum"], 39)
        self.assertEqual(cfg["shape_B_minimum"], 39)
        self.assertEqual(cfg["r_floor_from_search"], 3)
        self.assertEqual(cfg["s_floor_from_search"], 6)

    def test_two_input_certificate(self):
        t = oracle.two_input_certificate()
        self.assertEqual(t["realized_output_functions"], 14)
        self.assertEqual(t["categories"],
                         {"constant": 2, "literal": 4, "one_corner": 4,
                          "three_corners": 4})
        self.assertTrue(t["two_opposite_corner_patterns_excluded_by_midpoint"])

    def test_four_input_omission(self):
        o = oracle.four_input_omission()
        self.assertEqual(o["bounded_output_functions"], 986)
        self.assertEqual(o["omitted_weights"], [3, 2, 2, 1])
        self.assertEqual(o["omitted_threshold"], 4)
        self.assertTrue(o["omitted_not_in_grid"])

    def test_finite_degree_cases(self):
        self.assertEqual(oracle.finite_degree_cases_arithmetic(), 3251)

    def test_syntax_stress(self):
        s = oracle.syntax_stress_arithmetic()
        self.assertEqual(s["signed_zero_large_support_patterns"], 124)
        self.assertTrue(s["spot_price_floors_hold"])

    def test_rendering(self):
        r = oracle.rendering_counterexample()
        self.assertEqual(r["fixed_order_opcodes"], 18)
        self.assertEqual(r["reordered_opcodes"], 17)
        self.assertTrue(r["all8_outputs_equal"])

    def test_delegation(self):
        d = oracle.delegation_counterexample()
        self.assertEqual(d["wrapper_opcodes"], 4)
        self.assertEqual(d["neural_wrapper_per_sweep"], 32)
        self.assertFalse(d["universal_exclusion_of_delegating_class"])

    def test_crosscheck_receipt(self):
        rc = subprocess.run([sys.executable, "-I", "-B",
                             str(HERE / "l46_crosscheck_v1.py")],
                            capture_output=True, text=True)
        receipt = json.loads((HERE / "ORACLE_RESULT_L46_V1.json").read_text())
        disagrees = [r["claim_id"] for r in receipt["agreement"]["rows"]
                     if not r["agree"]]
        self.assertTrue(receipt["independence_audit"]["stdlib_only"])
        self.assertTrue(receipt["negative_control"]["passed"])
        # The single possible disagreement is the recorded L46-F1 finding,
        # which is interpreter-dependent: on CPython >= 3.11 the registered
        # BASE6 reproduces (no disagreement, CONVERTED); on 3.8 the raw
        # count is 7 and the finding fires exactly once.
        if any("base6" in d for d in disagrees):
            self.assertEqual(len(disagrees), 1)
            self.assertIn("interpreter-version-sensitive", disagrees[0])
            self.assertEqual(rc.returncode, 2)
            self.assertEqual(receipt["verdict"], "TWO_ROUTE_WITH_FINDINGS")
        else:
            self.assertEqual(disagrees, [])
            self.assertEqual(rc.returncode, 0)
            self.assertEqual(receipt["verdict"], "TWO_ROUTE_CONVERTED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
