"""Exact original scalarization arithmetic and missing-premise controls."""
from fractions import Fraction as F
from itertools import product
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from support_v28 import scalar, oracle
COVERAGE = {}


class ScalarTests(unittest.TestCase):
    def test_exact_profile_grid_and_premises(self):
        profiles = tuple(product((F(0), F(1)), repeat=2))
        weights = ((F(2), F(1)), (F(1), F(2)))
        checked = pairs = 0
        for x, y in product(profiles, repeat=2):
            pairs += 1
            oracle.certify(scalar.dominates(x, y), all(a <= b for a, b in zip(x, y)))
            oracle.certify(scalar.strict_dominates(x, y),
                           all(a <= b for a, b in zip(x, y)) and x != y)
            for w in weights:
                oracle.certify(scalar.dot(w, x), oracle.weighted(w, x))
                oracle.certify(scalar.dot(w, y), oracle.weighted(w, y))
                self.assertEqual(scalar.dot(w, x) > scalar.dot(w, y),
                                 oracle.weighted(w, x) > oracle.weighted(w, y))
                checked += 1
        x, y = (F(1), F(0)), (F(0), F(1))
        self.assertFalse(scalar.dominates(x, y)); self.assertFalse(scalar.dominates(y, x))
        self.assertGreater(scalar.dot(weights[0], x), scalar.dot(weights[0], y))
        self.assertLess(scalar.dot(weights[1], x), scalar.dot(weights[1], y))
        self.assertEqual(scalar.dot((F(0), F(1)), (F(1), F(0))), F(0))
        self.assertLess(scalar.dot((F(-1), F(1)), (F(1), F(0))),
                        scalar.dot((F(-1), F(1)), (F(0), F(0))))
        self.assertFalse(scalar.strict_dominates(x, x))
        self.assertEqual(checked, 32)
        COVERAGE.update(scalar_profile_pairs=pairs, scalar_weight_comparisons=checked,
                        scalar_named_premise_controls=4)
