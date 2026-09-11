#!/usr/bin/env python3

import unittest
from fractions import Fraction

from analytic_phase_microscope import LinearLifecycle, crossover_horizon, run


class AnalyticPhaseMicroscopeTest(unittest.TestCase):
    def test_registered_boundary(self) -> None:
        a = LinearLifecycle(Fraction(100), Fraction(1), Fraction(20))
        b = LinearLifecycle(Fraction(10), Fraction(5), Fraction(2))
        self.assertEqual(crossover_horizon(a, b, 0), Fraction(45, 2))
        self.assertEqual(crossover_horizon(a, b, 10), Fraction(135, 2))

    def test_revision_moves_boundary_outward(self) -> None:
        receipt = run()
        boundaries = [Fraction(row["crossover_horizon"]) for row in receipt["rows"]]
        self.assertEqual(boundaries, sorted(boundaries))
        self.assertGreater(boundaries[-1], boundaries[0])

    def test_frontier_reversal(self) -> None:
        receipt = run()
        for row in receipt["rows"]:
            self.assertFalse(row["parametric_wins_below"])
            self.assertTrue(row["parametric_wins_above"])


if __name__ == "__main__":
    unittest.main()
