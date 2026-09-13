"""Exact finite countercontrols for VOC-1--6.

These checks do not prove the analytic theorems.  They freeze the rational
witnesses that reject the bare recurrence, the myopic stopping rule, the
common-safe-action stopping rule, and tolerance-based tie detection.
"""

from fractions import Fraction
import math
import unittest


def bare_recurrence(j, certified_cost=Fraction(1), cognitive_charge=Fraction(0)):
    """One state, one certified action, one zero-charge cognitive self-loop."""
    return min(certified_cost, cognitive_charge + j)


def ranked_value(certified, cognitive, k, memo=None):
    """VOC-2: cognition strictly decreases k and is unavailable at k = 0."""
    if memo is None:
        memo = {}
    if k in memo:
        return memo[k]
    best = min(certified) if certified else None
    if k > 0:
        for charge, successor_certified in cognitive:
            value = charge + ranked_value(successor_certified, cognitive, k - 1, memo)
            best = value if best is None else min(best, value)
    memo[k] = best
    return best


class ValueOfComputationControls(unittest.TestCase):
    def test_bare_recurrence_has_a_continuum_of_fixed_points(self) -> None:
        # VOC-1 / T1: J = min(1, J) is solved by every J in [0, 1].
        for j in (Fraction(0), Fraction(1, 3), Fraction(1, 2), Fraction(1)):
            self.assertEqual(bare_recurrence(j), j)
        # Outside the interval it is not a fixed point, so the set is exactly [0,1].
        self.assertNotEqual(bare_recurrence(Fraction(2)), Fraction(2))

    def test_rank_certificate_makes_the_value_unique_and_terminating(self) -> None:
        # VOC-2: at k = 0 no cognition is admitted.
        certified = [Fraction(10)]
        cognitive = [(Fraction(1), [Fraction(10)])]
        self.assertEqual(ranked_value(certified, cognitive, 0), Fraction(10))
        # With allowance, deliberation is only taken when it pays; here it does not.
        self.assertEqual(ranked_value(certified, cognitive, 3), Fraction(10))

    def test_positive_charge_bounds_the_number_of_cognitive_steps(self) -> None:
        # VOC-3: m steps cost at least m*epsilon; beyond C/epsilon it is suboptimal.
        epsilon, c = Fraction(1), Fraction(10)
        bound = c // epsilon
        self.assertEqual(bound, 10)
        self.assertGreater((bound + 1) * epsilon, c)

    def test_myopic_value_of_computation_stops_too_early(self) -> None:
        # VOC-4 / W2: each single probe has VOC = 0 < charge 1, so myopia stops.
        best_now = Fraction(10)
        charge = Fraction(1)
        best_after_one_probe = Fraction(10)
        single_step_voc = best_now - best_after_one_probe
        self.assertEqual(single_step_voc, Fraction(0))
        self.assertLess(single_step_voc, charge)
        myopic_cost = best_now
        optimal_cost = charge + charge + Fraction(1)
        self.assertEqual(myopic_cost, Fraction(10))
        self.assertEqual(optimal_cost, Fraction(3))
        self.assertLess(optimal_cost, myopic_cost)

    def test_common_safe_action_does_not_license_economic_stopping(self) -> None:
        # VOC-5 / W3 / T3.
        common_safe = Fraction(10)
        probe = Fraction(1)
        model_specific = Fraction(1)
        self.assertEqual(probe + model_specific, Fraction(2))
        self.assertLess(probe + model_specific, common_safe)

    def test_tolerance_ties_are_not_exact_argmin_sets(self) -> None:
        # VOC-6 / W4 / T2.
        delta = Fraction(1, 2 ** 42)
        pair_a = (Fraction(1), Fraction(1) + delta)
        pair_b = (Fraction(1) + delta, Fraction(1))

        def exact_argmin(pair):
            best = min(pair)
            return frozenset(i for i, v in enumerate(pair) if v == best)

        self.assertEqual(exact_argmin(pair_a), frozenset({0}))
        self.assertEqual(exact_argmin(pair_b), frozenset({1}))
        # Opposite singletons: the exact sets are disjoint, so this is a collision.
        self.assertTrue(exact_argmin(pair_a).isdisjoint(exact_argmin(pair_b)))
        exact_collisions = 1

        # The tolerance classifier calls both "tie" and records none.
        def is_tie(pair):
            return math.isclose(float(pair[0]), float(pair[1]),
                                rel_tol=1e-12, abs_tol=0.0)

        self.assertTrue(is_tie(pair_a))
        self.assertTrue(is_tie(pair_b))
        tolerance_collisions = 0
        self.assertNotEqual(exact_collisions, tolerance_collisions)

        # The witness is exactly representable in binary floating point.
        self.assertEqual(Fraction(float(Fraction(1) + delta)), Fraction(1) + delta)


if __name__ == "__main__":
    unittest.main()
