import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from row_confidence_v1 import radius, tail_upper, registered_radii
from visit_oracle_v1 import prefix_failure, full_bitstrings, optional_peek, adaptive_failure


class AdaptiveRowsTests(unittest.TestCase):
    def test_exact_optional_peek_failure_and_revival(self):
        out = optional_peek()
        self.assertEqual(out["optional_failure"], F(47, 125))
        self.assertGreater(out["optional_failure"], out["fixed_look_nominal_error"])
        self.assertEqual(out["repair_uniform_union_upper"], F(17, 72))
        self.assertEqual(out["repair_failure_at_p"], 0)

    def test_visit_completion_selection_bias(self):
        # Continue to the second visit iff the first bit is zero.
        paths = {(0, 0): F(1, 4), (0, 1): F(1, 4)}
        mass = sum(paths.values())
        self.assertEqual(mass, F(1, 2))
        self.assertEqual(sum(w for bits, w in paths.items() if bits[0] == 1)/mass, 0)
        self.assertNotEqual(0, F(1, 2))

    def test_known_singleton_needs_no_data(self):
        self.assertEqual(radius(1, 0, F(1, 4), F(1)), 0)

    def test_unobserved_unknown_row_has_radius_one(self):
        self.assertEqual(radius(2, 0, F(1, 4), F(1)), 1)

    def test_independently_known_empty_unknown_register(self):
        self.assertEqual(registered_radii((), (), F(1, 4), ()), ())

    def test_nonvacuous_rational_radius_certified(self):
        r = radius(2, 64, F(1, 4), F(1))
        self.assertLess(r, 1)
        self.assertLessEqual(tail_upper(2, 64, r), F(1, 4)/(64*65))
        self.assertGreater(tail_upper(2, 64, r-F(1, 64)), F(1, 4)/(64*65))

    def test_error_spending_telescopes(self):
        for n in (1, 3, 9, 100):
            self.assertEqual(sum(F(1, j*(j+1)) for j in range(1, n+1)), F(n, n+1))

    def test_prefix_oracle_matches_actual_paths(self):
        eps = {n: F(1, 3) for n in range(1, 8)}
        self.assertEqual(prefix_failure(F(1, 4), 7, eps), full_bitstrings(F(1, 4), 7, eps))

    def test_deterministic_sampler_law_no_alarm(self):
        eps = [{n: F(0) for n in range(1, 9)}] * 2
        self.assertEqual(adaptive_failure((F(0), F(1)), 8, eps, "higher_mean")[0], 0)

    def test_reused_draw_breaks_fresh_law_assumption(self):
        # Repeated copies of one fair bit have TV 1/2 from Bernoulli(1/2).
        r = radius(2, 128, F(1, 4), F(1))
        self.assertLess(r, F(1, 2))
        self.assertEqual(sum(F(1, 2) for x in (0, 1) if abs(F(x)-F(1, 2)) > r), 1)

    def test_weights_are_one_global_allocation(self):
        with self.assertRaises(ValueError):
            registered_radii((2, 2), (1, 1), F(1, 4), (F(3, 4), F(3, 4)))

    def test_prevalidation_not_bypassed_by_numeric_cache_equality(self):
        radius(2, 64, F(1, 4), F(1))
        with self.assertRaises(ValueError):
            radius(2, 64, 0.25, 1.0)

    def test_invalid_scalar_contracts(self):
        for args in ((0, 1, F(1, 4), F(1)), (2, -1, F(1, 4), F(1)),
                     (2, 1, F(0), F(1)), (2, 1, F(1), F(1)),
                     (2, 1, F(1, 4), F(0)), (True, 1, F(1, 4), F(1))):
            with self.subTest(args=args), self.assertRaises(ValueError):
                radius(*args)

    def test_mismatched_row_register(self):
        with self.assertRaises(ValueError):
            registered_radii((2,), (1, 2), F(1, 4), (F(1),))


if __name__ == "__main__":
    unittest.main()
