#!/usr/bin/env python3
"""Tests for the REV-L46 independent route 2 (gmi-formal-proof-audit-v1).

Run: python3 -I -B test_independent_oracle_v1.py -v
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import independent_oracle_v1 as oracle  # noqa: E402


class TestIndependentOracle(unittest.TestCase):

    def test_corpus_arithmetic(self):
        ids = oracle.corpus_identifiers()
        self.assertEqual(len(ids), 39)
        self.assertIn("T602-17b", ids)
        self.assertIn("T602-17", ids)  # 01..38 includes 17; 17b is the 39th
        self.assertNotIn("T602-39", ids)

    def test_crossover_boundary_algebra(self):
        self.assertTrue(oracle.schema_crossover_algebraic())

    def test_signs_witness_and_bound(self):
        self.assertTrue(oracle.schema_signs_witness_and_bound())

    def test_factorization_partition_both_directions(self):
        # constant-on-fibers: canonical factor consistent (iff holds, True)
        self.assertTrue(oracle.schema_factorization_partition((0, 0, 1, 1), (1, 1, 0, 0)))
        # NOT constant on the fiber {0,1}: no factor exists (iff holds, True)
        self.assertTrue(oracle.schema_factorization_partition((0, 0, 1, 1), (1, 0, 0, 0)))
        # exhaustive: the iff statement itself holds for every pair
        for observation in oracle._all_functions(4, 2):
            for target in oracle._all_functions(4, 2):
                self.assertTrue(
                    oracle.schema_factorization_partition(observation, target))

    def test_extrapolation_product_form(self):
        self.assertTrue(oracle.schema_extrapolation_product_form())

    def test_conjunction_symmetry(self):
        self.assertTrue(oracle.schema_conjunction_symmetry_reduced())

    def test_periodicity_floyd(self):
        self.assertTrue(oracle.schema_periodicity_floyd())

    def test_floyd_known_cycle(self):
        # f = (1,2,0,0): orbit of 0 is 0->1->2->0, mu=0, lam=3
        self.assertEqual(oracle._floyd_cycle((1, 2, 0, 0), 0), (0, 3))
        # f = (1,3,2,0): orbit 0->1->3->0 after pre-period 0; but 2 fixed:
        # orbit of 0: mu=0, lam=3
        self.assertEqual(oracle._floyd_cycle((1, 3, 2, 0), 0), (0, 3))

    def test_oracle_quantities_shape(self):
        q = oracle.oracle_quantities()
        self.assertEqual(q["theorems"], 39)
        self.assertTrue(q["inventory_is_closed_corpus"])
        self.assertTrue(q["ledger_all_green"])
        self.assertTrue(all(q["schemas"].values()))

    def test_crosscheck_receipt(self):
        rc = subprocess_run([sys.executable, "-I", "-B",
                             str(HERE / "l46_crosscheck_v1.py")])
        self.assertEqual(rc.returncode, 0, rc.stdout + rc.stderr)
        receipt = json.loads((HERE / "ORACLE_RESULT_L46_V1.json").read_text())
        self.assertEqual(receipt["verdict"], "TWO_ROUTE_CONVERTED")
        self.assertTrue(receipt["agreement"]["exact_agreement_everywhere"])
        self.assertTrue(receipt["independence_audit"]["stdlib_only"])
        self.assertTrue(receipt["negative_control"]["passed"])


def subprocess_run(argv):
    import subprocess
    return subprocess.run(argv, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
