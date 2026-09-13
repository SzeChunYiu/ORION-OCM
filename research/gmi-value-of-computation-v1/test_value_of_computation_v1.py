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


from pathlib import Path
import types

_model = types.ModuleType("voc_source")
_path = Path(__file__).with_name("value_of_computation_model_v1.py")
exec(compile(_path.read_bytes(), str(_path), "exec"), _model.__dict__)
ranked_value = _model.ranked_value


class ValueOfComputationControls(unittest.TestCase):
    def test_bare_recurrence_has_a_continuum_of_fixed_points(self) -> None:
        # VOC-1 / T1: J = min(1, J) is solved by every J in [0, 1].
        for j in (Fraction(0), Fraction(1, 3), Fraction(1, 2), Fraction(1)):
            self.assertEqual(bare_recurrence(j), j)
        # Values are nonnegative by contract; signed fixed points below0 are outside it.
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

    def test_actual_pinned_memo_collision_and_corrected_result(self):
        # Execute preserved source without running its suite.
        path = Path(__file__).parent / "raw/pr571-743b9ded/test_value_of_computation_v1.py"
        old = {"__name__": "historical_voc_control"}
        exec(compile(path.read_bytes(), str(path), "exec"), old)
        c = Fraction
        args = ([c(10)], [(c(0), [c(10)]), (c(0), [c(0)])], 1)
        self.assertEqual(old["ranked_value"](*args), c(10))
        self.assertEqual(ranked_value(*args), c(0))
        self.assertEqual(old["ranked_value"]([c(10)], [(c(1), [c(10)])], 3), c(10))
        self.assertEqual(ranked_value([c(10)], [(c(1), [c(10)])], 3), c(10))

    def test_ranked_dead_end_is_infeasible(self):
        self.assertIsNone(ranked_value([], [], 0))
        self.assertIsNone(ranked_value([], [(Fraction(0), [])], 3))

    def test_rank_cache_cannot_import_another_register(self):
        poisoned = {0: Fraction(999), ((Fraction(0),), 0): Fraction(999)}
        self.assertEqual(ranked_value([Fraction(0)], [], 0, poisoned), Fraction(0))
        self.assertEqual(poisoned[0], Fraction(999))

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
