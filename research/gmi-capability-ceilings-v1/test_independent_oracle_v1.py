#!/usr/bin/env python3
"""Tests for REV-L46 route 2 (gmi-capability-ceilings-v1).

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

    def test_injectivity_counting(self):
        self.assertTrue(oracle.injective_assignments(4, 4))
        self.assertFalse(oracle.injective_assignments(5, 4))
        self.assertFalse(oracle.injective_assignments(2, 1))

    def test_state_capacity(self):
        self.assertFalse(oracle.delayed_label_witness(3, 2))
        self.assertTrue(oracle.delayed_label_witness(3, 3))

    def test_partition_refinement(self):
        self.assertFalse(oracle.observation_factors(
            {"x0": "z0", "x1": "z0", "x2": "z1"},
            {"x0": "a0", "x1": "a1", "x2": "a0"}))
        self.assertTrue(oracle.observation_factors(
            {"x0": "z0", "x1": "z0", "x2": "z1"},
            {"x0": "a0", "x1": "a0", "x2": "a1"}))

    def test_min_bits_doubling(self):
        self.assertEqual(oracle.min_bits_by_doubling(5), 3)
        self.assertEqual(oracle.min_bits_by_doubling(4), 2)
        self.assertEqual(oracle.min_bits_by_doubling(1), 0)

    def test_rank_by_minors(self):
        self.assertEqual(oracle.rank_by_minors([[1, 0, 0], [0, 1, 0]]), 2)
        self.assertEqual(oracle.rank_by_minors([[1, 0, 0], [2, 0, 0]]), 1)
        self.assertEqual(oracle.rank_by_minors([[1, 1, 0], [2, 2, 0], [0, 0, 1]]), 2)

    def test_tree_recurrence(self):
        self.assertEqual(oracle.tree_nodes_recurrence(2, 0), 1)
        self.assertEqual(oracle.tree_nodes_recurrence(2, 2), 7)
        self.assertEqual(oracle.tree_nodes_recurrence(2, 3), 15)
        self.assertEqual(oracle.tree_nodes_recurrence(1, 4), 5)
        # recurrence agrees with the geometric closed form on a grid
        for b in range(1, 5):
            for h in range(0, 7):
                closed = h + 1 if b == 1 else (b ** (h + 1) - 1) // (b - 1)
                self.assertEqual(oracle.tree_nodes_recurrence(b, h), closed)

    def test_horizon_walk(self):
        self.assertEqual(oracle.max_horizon_walk(2, 14), 2)
        self.assertEqual(oracle.max_horizon_walk(2, 15), 3)
        self.assertEqual(oracle.max_horizon_walk(1, 5), 4)

    def test_hypergeom(self):
        self.assertEqual(oracle.hypergeom_false_adoption(10, 1, 8), F(1, 5))
        self.assertEqual(oracle.hypergeom_false_adoption(10, 1, 10), F(0))
        self.assertEqual(oracle.hypergeom_false_adoption(6, 2, 2), F(2, 5))
        self.assertEqual(oracle.min_checks_scan(10, 1, F(1, 5)), 8)
        self.assertEqual(oracle.min_checks_scan(10, 1, F(0)), 10)

    def test_adversary(self):
        self.assertEqual(oracle.adversary_first_missing(5, [0, 1, 2, 3]), 4)
        self.assertIsNone(oracle.adversary_first_missing(5, [0, 1, 2, 3, 4]))
        self.assertEqual(oracle.adversary_first_missing(5, [4, 2, 0, 1]), 3)

    def test_social(self):
        s = oracle.social_checks()
        self.assertFalse(s["base_response_identifiable"])
        self.assertTrue(s["diagnostic_response_identifiable"])
        self.assertTrue(s["diagnostic_model_identifiable"])
        self.assertFalse(s["base_model_identifiable"])
        self.assertEqual(s["base_class_count"], 2)
        self.assertEqual(s["diagnostic_class_count"], 3)
        self.assertTrue(s["same_response_identifiable"])

    def test_transcript_word_count(self):
        self.assertEqual(oracle.transcript_word_count(2, 2), 4)
        self.assertEqual(oracle.transcript_word_count(3, 0), 1)

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
