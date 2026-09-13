"""Exact finite countercontrols for GAC-1--5.

These checks do not prove the analytic theorem.  They freeze the small rational
counterexamples used to reject weaker composition rules.
"""

from fractions import Fraction
from itertools import product
import unittest


class GlobalAdaptiveCompositionControls(unittest.TestCase):
    def test_private_history_validity_can_fail_after_global_selection(self) -> None:
        rows = []
        for z in (0, 1):
            p = Fraction(1, 2)
            l1 = Fraction(2 if z == 1 else 0)
            l2 = Fraction(2 if z == 0 else 0)
            selected = l1 if z == 1 else l2
            rows.append((p, l1, l2, selected))

        self.assertEqual(sum(p * l1 for p, l1, _, _ in rows), 1)
        self.assertEqual(sum(p * l2 for p, _, l2, _ in rows), 1)
        self.assertEqual(sum(p * selected for p, _, _, selected in rows), 2)

    def test_retroactive_max_breaks_e_value_validity(self) -> None:
        rows = []
        for h1, h2 in product((0, 1), repeat=2):
            p = Fraction(1, 4)
            e1 = Fraction(2 * h1)
            e2 = Fraction(2 * h2)
            rows.append((p, e1, e2))

        self.assertEqual(sum(p * e1 for p, e1, _ in rows), 1)
        self.assertEqual(sum(p * e2 for p, _, e2 in rows), 1)
        self.assertEqual(sum(p * max(e1, e2) for p, e1, e2 in rows), Fraction(3, 2))

    def test_predictable_half_half_mix_is_safe_in_same_control(self) -> None:
        rows = []
        for h1, h2 in product((0, 1), repeat=2):
            p = Fraction(1, 4)
            e1 = Fraction(2 * h1)
            e2 = Fraction(2 * h2)
            mixed = (e1 + e2) / 2
            rows.append((p, mixed))

        self.assertEqual(sum(p * mixed for p, mixed in rows), 1)

    def test_fresh_full_alpha_per_birth_accumulates_error(self) -> None:
        alpha = Fraction(1, 20)
        fwer_10 = 1 - (1 - alpha) ** 10
        self.assertGreater(fwer_10, alpha)
        self.assertEqual(fwer_10, Fraction(4108933742199, 10240000000000))

    def test_geometric_dynamic_birth_budget_is_summable(self) -> None:
        alpha = Fraction(1, 20)
        partial = sum((alpha / (2**j) for j in range(1, 40)), Fraction(0))
        self.assertLess(partial, alpha)


if __name__ == "__main__":
    unittest.main()
