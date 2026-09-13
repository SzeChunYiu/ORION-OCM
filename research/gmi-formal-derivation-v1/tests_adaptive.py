"""Exact finite controls for ADAPTIVE.md; not a mechanized general proof."""

from fractions import Fraction as F
from itertools import product
from math import factorial
import unittest


def paths(n):
    return tuple((bits, F(1, 2**n)) for bits in product((0, 1), repeat=n))


def probability(tree, predicate):
    return sum((weight for bits, weight in tree if predicate(bits)), F(0))


def expectation(tree, value):
    return sum((weight * value(bits) for bits, weight in tree), F(0))


def child_protocol(bits):
    """Parent uses two visits; child is created after first failure, if ≤2."""
    parent = 1
    born = None
    allocation = F(0)
    for t in (0, 1):
        parent *= 2 * bits[t]
        if not bits[t]:
            born = t + 1  # Birth after this observation, indexed from one.
            allocation = F(1, 4) if born == 1 else F(1, 8)
            break
    child = 1
    crossed = False
    if born is not None:
        for outcome in bits[born:]:
            child *= 2 * outcome
            if child >= 1 / allocation:
                crossed = True
                break
    return parent >= 4, born, allocation, crossed


class TestAdaptiveDerivation(unittest.TestCase):
    def test_exact_finite_tree_and_fresh_conditional_means(self):
        tree = paths(5)
        self.assertEqual(sum((w for _, w in tree), F(0)), 1)
        # Every complete global prefix, including information other rows see.
        for t in range(5):
            for prefix in product((0, 1), repeat=t):
                mass = probability(tree, lambda b: b[:t] == prefix)
                first_moment = expectation(
                    tree, lambda b: b[t] if b[:t] == prefix else 0
                )
                self.assertEqual(first_moment / mass, F(1, 2))

    def test_predictable_revisit_without_conditioning_on_existence(self):
        tree = paths(3)
        exists = probability(tree, lambda b: b[0] == 1)
        crosses = probability(tree, lambda b: b[0] == b[2] == 1)
        attained_wealth = expectation(tree, lambda b: 4 * b[0] * b[2])
        self.assertEqual(exists, F(1, 2))
        self.assertEqual(crosses, F(1, 4))
        self.assertEqual(attained_wealth, 1)
        self.assertEqual(crosses / exists, F(1, 2))
        self.assertEqual(attained_wealth / exists, 2)

    def test_birth_allocations_and_conditional_tower_are_exact(self):
        tree = paths(5)
        for bits, _ in tree:
            _, _, allocation, _ = child_protocol(bits)
            self.assertLessEqual(F(1, 4) + allocation, F(1, 2))
        for birth, level in ((1, F(1, 4)), (2, F(1, 8))):
            mass = probability(tree, lambda b: child_protocol(b)[1] == birth)
            bad = probability(
                tree, lambda b: child_protocol(b)[1] == birth
                and child_protocol(b)[3]
            )
            self.assertEqual(bad / mass, level)
        union = probability(
            tree, lambda b: child_protocol(b)[0] or child_protocol(b)[3]
        )
        allocated = expectation(tree, lambda b: F(1, 4) + child_protocol(b)[2])
        self.assertEqual(union, F(13, 32))
        self.assertEqual(union, allocated)
        self.assertLessEqual(union, F(1, 2))

    def test_dependent_rows_union_valid_but_product_invalid(self):
        tree = paths(2)
        wealth = lambda b: 4 * b[0] * b[1]
        self.assertEqual(expectation(tree, wealth), 1)
        union = probability(tree, lambda b: wealth(b) >= 4)
        self.assertEqual(union, F(1, 4))
        self.assertLessEqual(union, F(1, 4) + F(1, 4))
        self.assertEqual(expectation(tree, lambda b: wealth(b) ** 2), 4)
        self.assertGreater(
            probability(tree, lambda b: wealth(b) ** 2 >= 8), F(1, 8)
        )

    def test_replay_breaks_global_conditional_law_and_calibration(self):
        tree = paths(1)
        self.assertEqual(expectation(tree, lambda b: b[0]), F(1, 2))
        for revealed in (0, 1):
            mass = probability(tree, lambda b: b[0] == revealed)
            conditional = expectation(
                tree, lambda b: b[0] if b[0] == revealed else 0
            ) / mass
            self.assertEqual(conditional, revealed)
            self.assertNotEqual(conditional, F(1, 2))
        self.assertEqual(
            probability(tree, lambda b: (2 * b[0]) ** 3 >= 4), F(1, 2)
        )
        # exp(16) > its seventh positive series term > 42240.
        self.assertGreater(F(16**7, factorial(7)), 42240)
        self.assertEqual(probability(tree, lambda b: abs(F(b[0]) - F(1, 2))
                                     == F(1, 2)), 1)

    def test_postselected_historical_value_and_fresh_repair(self):
        tree = paths(2)
        for choice in (0, 1):
            self.assertEqual(expectation(tree, lambda b: 2 * (b[0] == choice)), 1)
        self.assertEqual(expectation(tree, lambda b: 2 * (b[0] == b[0])), 2)
        for observed in (0, 1):
            mass = probability(tree, lambda b: b[0] == observed)
            calibrated = expectation(
                tree, lambda b: 2 * (b[1] == observed) if b[0] == observed else 0
            ) / mass
            self.assertEqual(calibrated, 1)

    def test_fixed_time_e_values_do_not_imply_optional_validity(self):
        tree = paths(2)
        for t in (0, 1):
            self.assertEqual(expectation(tree, lambda b: 2 * b[t]), 1)
        stopped = lambda b: 2 if b[0] == 1 else 2 * b[1]
        self.assertEqual(expectation(tree, stopped), F(3, 2))
        self.assertEqual(probability(tree, lambda b: stopped(b) >= 2), F(3, 4))

    def test_target_drift_is_not_a_current_mean_guarantee(self):
        observations = (0,) * 32 + (1,) * 32
        pooled = F(sum(observations), len(observations))
        self.assertEqual(pooled, F(1, 2))
        self.assertEqual(observations[31], 0)
        self.assertEqual(observations[32], 1)  # Old conditional-law premise fails.
        # exp(32) > its fifth positive series term > 166400.
        self.assertGreater(F(32**5, factorial(5)), 166400)
        self.assertEqual(abs(pooled - observations[-1]), F(1, 2))
        self.assertEqual(pooled, F(sum(observations), 64))  # Past conditional mean.

    def test_unadapted_process_invalidates_crossing_stopping_argument(self):
        outcomes = (1, 2, 3)
        wealth = lambda u, t: 1 if t == 0 else 3 * (u == t)
        # Under the trivial filtration every stopping time is constant.
        for deterministic_time in range(5):
            fixed_expectation = sum(
                (F(1, 3) * wealth(u, deterministic_time) for u in outcomes), F(0)
            )
            self.assertLessEqual(fixed_expectation, 1)
        crossing_probability = sum(
            (F(1, 3) for u in outcomes if max(wealth(u, t) for t in outcomes) >= 2),
            F(0),
        )
        self.assertEqual(crossing_probability, 1)
        self.assertGreater(crossing_probability, F(1, 2))
        # {first crossing <= 1}={U=1}, absent from the trivial sigma algebra.
        self.assertNotIn(frozenset({1}), (frozenset(), frozenset(outcomes)))


if __name__ == "__main__":
    unittest.main()
