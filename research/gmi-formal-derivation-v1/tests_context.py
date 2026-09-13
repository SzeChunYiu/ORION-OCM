"""Exact context, shared-state and joint-resource counterexamples."""

import itertools
import unittest
from fractions import Fraction


class ContextTests(unittest.TestCase):
    def test_local_projection_success_does_not_imply_joint_relation(self):
        relation = {(0, 1), (1, 0)}
        first_allowed = {x for x, _ in relation}
        second_allowed = {y for _, y in relation}
        combined = (0, 0)
        self.assertIn(combined[0], first_allowed)
        self.assertIn(combined[1], second_allowed)
        self.assertNotIn(combined, relation)
        self.assertIn((0, 1), relation)  # compatible coordinated repair

    def test_shared_seed_preserves_marginals_but_changes_joint_law(self):
        shared = {(0, 0): Fraction(1, 2), (1, 1): Fraction(1, 2)}
        independent = {pair: Fraction(1, 4)
                       for pair in itertools.product(range(2), repeat=2)}
        for coordinate in (0, 1):
            for value in (0, 1):
                self.assertEqual(
                    sum(p for pair, p in shared.items() if pair[coordinate] == value),
                    sum(p for pair, p in independent.items()
                        if pair[coordinate] == value),
                )
        self.assertEqual(sum(p for (x, y), p in shared.items() if x == y), 1)
        self.assertEqual(
            sum(p for (x, y), p in independent.items() if x == y), Fraction(1, 2)
        )

    def test_joint_resource_minima_need_not_be_attainable(self):
        candidates = {(1, 3), (3, 1)}
        coordinate_minima = tuple(min(c[k] for c in candidates) for k in (0, 1))
        self.assertEqual(coordinate_minima, (1, 1))
        self.assertNotIn(coordinate_minima, candidates)

    def test_component_local_kernel_fails_in_observed_context(self):
        # Actual context observes Z and chooses A=Z; the component emits Y=Z.
        actual = [(z, z, z, Fraction(1, 2)) for z in (0, 1)]
        # A local fair-output kernel has forgotten the shared observed Z.
        reduced = [(z, z, y, Fraction(1, 4))
                   for z, y in itertools.product((0, 1), repeat=2)]
        actual_success = sum(p for z, action, y, p in actual if action == y)
        reduced_success = sum(p for z, action, y, p in reduced if action == y)
        self.assertEqual(actual_success, 1)
        self.assertEqual(reduced_success, Fraction(1, 2))
        # On complete observed histories the kernel is delta_Z, not fair.
        for z in (0, 1):
            conditional_actual = sum(p for zz, action, y, p in actual
                                     if zz == z and y == z) / Fraction(1, 2)
            conditional_reduced = sum(p for zz, action, y, p in reduced
                                      if zz == z and y == z) / Fraction(1, 2)
            self.assertEqual(conditional_actual, 1)
            self.assertEqual(conditional_reduced, Fraction(1, 2))

    def test_same_state_marginal_does_not_preserve_initial_context_coupling(self):
        # Both executions use the identical exact output kernel Y=S.
        coupled = {(0, 0): Fraction(1, 2), (1, 1): Fraction(1, 2)}
        decoupled = {pair: Fraction(1, 4)
                     for pair in itertools.product((0, 1), repeat=2)}
        for state in (0, 1):
            self.assertEqual(
                sum(p for (s, z), p in coupled.items() if s == state),
                sum(p for (s, z), p in decoupled.items() if s == state),
            )
        success = lambda law: sum(p for (s, z), p in law.items() if s == z)
        self.assertEqual(success(coupled), 1)
        self.assertEqual(success(decoupled), Fraction(1, 2))
        # Restoring the entire initial joint law repairs the prediction.
        self.assertEqual(success(dict(coupled)), success(coupled))

    def test_charged_architecture_preference_crossing(self):
        cost_i = lambda horizon: 10 + horizon
        cost_j = lambda horizon: 2 + 3 * horizon
        self.assertGreater(cost_i(3), cost_j(3))
        self.assertEqual(cost_i(4), cost_j(4))
        self.assertLess(cost_i(5), cost_j(5))


if __name__ == "__main__":
    unittest.main()
