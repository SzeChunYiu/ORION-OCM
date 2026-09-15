from __future__ import annotations

import unittest
from fractions import Fraction

from analog_semantics_closure_v1 import (
    analog_affine_interval,
    d1_d6_interval_compiler,
    euler_step_bound,
    euler_step_count,
    exhaustive_sampled_certificate,
    validate_closure,
)


class AnalogSemanticsClosureTests(unittest.TestCase):
    def test_exact_sampled_interval(self) -> None:
        args = (Fraction(1), Fraction(-1), Fraction(2), Fraction(1), Fraction(1, 4))
        self.assertEqual(analog_affine_interval(*args), (Fraction(3, 4), Fraction(5, 4)))
        self.assertEqual(analog_affine_interval(*args), d1_d6_interval_compiler(*args))

    def test_exhaustive_sampled_compiler(self) -> None:
        result = exhaustive_sampled_certificate()
        self.assertEqual(result["cases"], 162)
        self.assertEqual(result["mismatches"], 0)
        self.assertEqual(result["invalid_intervals"], 0)

    def test_euler_bound_is_explicit(self) -> None:
        self.assertGreater(euler_step_bound(1, 1, 1, 0.01), 0)
        self.assertEqual(euler_step_count(1, 1, 1, 0.01), 172)

    def test_only_two_earned_tasks_close(self) -> None:
        result = validate_closure()
        self.assertEqual(result["ledger_rows"], 2)
        self.assertEqual(result["accounting_coordinates"], 23)


if __name__ == "__main__":
    unittest.main()
