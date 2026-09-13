"""Finite adversarial witnesses; these do not mechanically prove infinite laws."""
from fractions import Fraction as F
from itertools import product
import unittest


def dynamic_value(kernel, rewards, initial, horizon):
    values = [F(0), F(0)]
    for _ in range(horizon):
        values = [max(rewards[s][a] + sum(
            kernel[s][a][n] * values[n] for n in range(2)
        ) for a in range(2)) for s in range(2)]
    return values[initial]


def trace_value(kernel, rewards, initial, policy):
    """Independent full two-action history tree: (root,left,right)."""
    root, left, right = policy
    total = F(0)
    for mid, end in product(range(2), repeat=2):
        second = (left, right)[mid]
        probability = kernel[initial][root][mid] * kernel[mid][second][end]
        total += probability * (rewards[initial][root] + rewards[mid][second])
    return total


class CompositionWitnesses(unittest.TestCase):
    def test_bellman_against_all_history_trees(self):
        count = 0
        for ps in product((F(0), F(1, 2), F(1)), repeat=4):
            kernel = [[(1-ps[2*s+a], ps[2*s+a]) for a in range(2)] for s in range(2)]
            for rs in product((F(0), F(1)), repeat=4):
                rewards = [rs[:2], rs[2:]]
                for initial in range(2):
                    exact = max(trace_value(kernel, rewards, initial, policy)
                                for policy in product(range(2), repeat=3))
                    self.assertEqual(dynamic_value(kernel, rewards, initial, 2), exact)
                    count += 1
        self.assertEqual(count, 2592)

    def test_conditional_first_failure_and_dependence(self):
        # All 16 hidden seeds; second output repeats the first, never a fresh bit.
        outcomes = list(product(range(2), repeat=4))
        repeated = [(bits[0], bits[0]) for bits in outcomes]
        independent = [(bits[0], bits[1]) for bits in outcomes]
        first = sum(F(1, 16) for a, b in repeated if a)
        second = sum(F(1, 16) for a, b in repeated if b)
        repeated_pair = sum(F(1, 16) for a, b in repeated if a == b)
        independent_pair = sum(F(1, 16) for a, b in independent if a == b)
        self.assertEqual(first, F(1, 2))
        self.assertEqual(second, F(1, 2))
        self.assertEqual(repeated_pair, F(1))
        self.assertEqual(independent_pair, F(1, 2))
        # Risk spending: fail if first two bits 11; after survival, fail iff
        # next two bits 11. First-failure decomposition uses the actual past.
        first_failure = sum(F(1, 16) for x in outcomes if x[:2] == (1, 1))
        second_failure = sum(F(1, 16) for x in outcomes
                             if x[:2] != (1, 1) and x[2:] == (1, 1))
        self.assertEqual(first_failure + second_failure, F(7, 16))
        self.assertLessEqual(first_failure + second_failure, F(1, 2))

    def test_small_one_step_error_does_not_certify_long_safety(self):
        epsilon = F(1, 10)
        for horizon in range(1, 21):
            actual = 1 - (1-epsilon)**horizon
            self.assertLessEqual(actual, min(F(1), horizon*epsilon))
        self.assertGreater(1-(1-epsilon)**20, F(4, 5))

    def test_two_step_computation_revives_myopic_rejection(self):
        prior = F(1, 2)
        cost = F(1, 10)
        one_step = max(sum(F(1, 4)*int(rule[key] == hidden)
                           for hidden, key in product(range(2), repeat=2)) - cost
                       for rule in product(range(2), repeat=2))
        two_step = F(0)
        for hidden, key in product(range(2), repeat=2):
            second_signal = hidden ^ key
            guess = key ^ second_signal
            two_step += F(1, 4) * (int(guess == hidden) - 2*cost)
        self.assertLess(one_step, prior)
        self.assertEqual(two_step, F(4, 5))
        self.assertGreater(two_step, prior)

    def test_observationally_identical_causal_models(self):
        def causal_model(u, intervention=None):
            x = u if intervention is None else intervention
            return x, x  # Y's structural parent is X.
        def confounded_model(u, intervention=None):
            x = u if intervention is None else intervention
            return x, u  # Y's structural parent is hidden U.
        obs_a = [causal_model(u) for u in range(2)]
        obs_b = [confounded_model(u) for u in range(2)]
        self.assertEqual(obs_a, obs_b)
        intervention_a = sum(F(1, 2)*causal_model(u, 1)[1] for u in range(2))
        intervention_b = sum(F(1, 2)*confounded_model(u, 1)[1] for u in range(2))
        self.assertEqual(intervention_a, F(1))
        self.assertEqual(intervention_b, F(1, 2))

    def test_compatible_pieces_need_global_resource_feasibility(self):
        alternatives = [(1, 3), (3, 1)]
        coordinate_minimum = tuple(min(v[i] for v in alternatives) for i in range(2))
        self.assertEqual(coordinate_minimum, (1, 1))
        self.assertNotIn(coordinate_minimum, alternatives)
        self.assertFalse(any(all(x <= 2 for x in v) for v in alternatives))


if __name__ == "__main__":
    unittest.main()
