"""Exact adverse and positive controls for the four PR568 premise repairs."""
from fractions import Fraction as F
from itertools import product
from math import comb
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from learning_memory_models_v1 import (
    deterministic_decoders, empirical_risks, external_regret, law,
    memorizer_losses, output_law, population_risks, private_action_view,
    proper_erm, pushforward, success,
)


class LearningMemoryScopeControls(unittest.TestCase):
    def test_negative_linear_regret_is_valid_one_sided(self):
        for horizon in range(1, 101):
            losses = [(t % 2, 1 - t % 2) for t in range(horizon)]
            chosen = [t % 2 for t in range(horizon)]
            regret = external_regret(losses, chosen)
            self.assertEqual(regret, -(horizon // 2))
            self.assertEqual(max(regret, 0), 0)
        self.assertEqual(external_regret(losses, chosen) / 100, F(-1, 2))

    def test_zero_regret_and_positive_linear_failure_controls(self):
        rows = [(0, 1)] * 12
        self.assertEqual(external_regret(rows, [0] * 12), 0)
        self.assertEqual(external_regret(rows, [1] * 12) / 12, 1)

    def test_expected_signed_regret_is_not_expected_positive_part(self):
        values = {-12: F(1, 2), 12: F(1, 2)}
        self.assertEqual(sum(v * p for v, p in values.items()), 0)
        self.assertEqual(sum(max(v, 0) * p for v, p in values.items()) / 12, F(1, 2))

    def test_private_action_joint_view_identifies_despite_equal_marginals(self):
        laws = [private_action_view(w) for w in (0, 1)]
        self.assertEqual(pushforward(laws[0], lambda v: v[1]),
                         pushforward(laws[1], lambda v: v[1]))
        self.assertNotEqual(laws[0], laws[1])
        decoder = {(a, z): {a ^ z: F(1)} for a, z in product((0, 1), repeat=2)}
        self.assertEqual([success(laws[w], decoder, w) for w in (0, 1)], [1, 1])
        # Independent execution of the actual action/observation protocol.
        for world, seed in product((0, 1), repeat=2):
            action = seed
            observation = action ^ world
            self.assertEqual(action ^ observation, world)

    def test_equal_complete_views_cannot_be_decoded_even_with_abstention(self):
        same = {0: F(1, 4), 1: F(3, 4)}
        for decoder in deterministic_decoders(same):
            q0, q1 = success(same, decoder, 0), success(same, decoder, 1)
            self.assertLessEqual(q0 + q1, 1)
            self.assertLessEqual(min(q0, q1), F(1, 2))
        # All denominator-four randomized output laws, including wrong outputs.
        for a, b, c in product(range(5), repeat=3):
            if a + b + c > 4:
                continue
            kernel = {0: F(a, 4), 1: F(b, 4), "abstain": F(c, 4),
                      "other": F(4-a-b-c, 4)}
            decoder = {v: kernel for v in same}
            self.assertLessEqual(min(success(same, decoder, w) for w in (0, 1)), F(1, 2))

    def test_policy_specific_obstruction_does_not_quantify_all_learners(self):
        for action in (0, 1):
            views = [{(action, world if action else 0): F(1)} for world in (0, 1)]
            if action == 0:
                self.assertEqual(*views)
            else:
                decoder = {(1, y): {y: F(1)} for y in (0, 1)}
                self.assertEqual([success(views[w], decoder, w) for w in (0, 1)], [1, 1])

    def test_forgetting_no_side_information_vs_fresh_revealing_repair(self):
        forgotten = {0: "same", 1: "same"}
        hidden = [{(forgotten[w], 0): F(1)} for w in (0, 1)]
        self.assertEqual(*hidden)
        for decoder in deterministic_decoders(hidden[0]):
            self.assertLessEqual(min(success(hidden[w], decoder, w) for w in (0, 1)), F(1, 2))
        revealed = [{(forgotten[w], w): F(1)} for w in (0, 1)]
        decoder = {("same", z): {z: F(1)} for z in (0, 1)}
        self.assertEqual([success(revealed[w], decoder, w) for w in (0, 1)], [1, 1])

    def test_fresh_uninformative_observation_does_not_revive_forgetting(self):
        same = {("same", z): F(1, 2) for z in (0, 1)}
        for decoder in deterministic_decoders(same):
            self.assertLessEqual(min(success(same, decoder, w) for w in (0, 1)), F(1, 2))

    def test_sample_dependent_size_two_class_breaks_the_original_bound(self):
        # n=24 exceeds 8 log 8 because e**3 > 1+3+9/2 > 8.
        self.assertGreater(1 + 3 + F(9, 2), 8)
        for sample in ([0] * 24, list(range(24)), [i % 7 for i in range(24)]):
            h = {"memorize": memorizer_losses(96, sample), "good": (0,) * 96}
            chosen = proper_erm(h, sample)
            empirical = empirical_risks(h, sample)
            risks = population_risks(h, [F(1, 96)] * 96)
            self.assertEqual(empirical, {"memorize": 0, "good": 0})
            self.assertEqual(chosen, "memorize")
            self.assertGreaterEqual(risks[chosen] - min(risks.values()), F(3, 4))
        # Exact exhaustive smaller-domain check of the all-sample cardinality mechanism.
        for sample in product(range(4), repeat=2):
            losses = memorizer_losses(4, sample)
            self.assertEqual(sum(losses), 4 - len(set(sample)))
            self.assertGreaterEqual(F(sum(losses), 4), F(1, 2))

    def test_improper_output_escapes_uniform_class_bound(self):
        sample = list(range(24))
        fixed = {"good": (0,) * 96}
        outsider = memorizer_losses(96, sample)
        self.assertNotIn(outsider, fixed.values())
        self.assertEqual(sum(outsider[x] for x in sample), 0)
        self.assertGreaterEqual(F(sum(outsider), 96), F(3, 4))
        self.assertEqual(proper_erm(fixed, sample), "good")

    def test_fixed_class_pac_no_alarm_exact_binomial_laws(self):
        n = 24
        for numerator in range(17):
            p = F(numerator, 16)
            failure = F(0)
            for ones in range(n + 1):
                chance = comb(n, ones) * p ** ones * (1-p) ** (n-ones)
                chosen = int(2 * ones > n)
                risk = (1-p) if chosen else p
                if risk - min(p, 1-p) > F(1, 2):
                    failure += chance
            self.assertLessEqual(failure, F(1, 2))

    def test_fresh_scoring_revives_a_pilot_selected_class(self):
        for pilot in ([0] * 24, list(range(24)), [i % 7 for i in range(24)]):
            # Condition on this pilot before drawing the independent scoring sample.
            h = {"memorize": memorizer_losses(96, pilot), "good": (0,) * 96}
            observed = set(pilot)
            outside = next(x for x in range(96) if x not in observed)
            self.assertEqual(proper_erm(h, [pilot[0]] * 24), "memorize")
            self.assertEqual(proper_erm(h, [outside] * 24), "good")
            # Under fresh iid scoring, the bad tie occurs iff every draw is observed.
            failure = F(len(observed), 96) ** 24
            self.assertLessEqual(failure, F(1, 4) ** 24)
            self.assertLess(failure, F(1, 2))

    def test_approximate_erm_uniform_bound_exhaustive_three_members(self):
        values = (F(0), F(1, 2), F(1))
        for true in product(values, repeat=3):
            for empirical in product(values, repeat=3):
                deviation = max(abs(a-b) for a, b in zip(true, empirical))
                for chosen in range(3):
                    eta = empirical[chosen] - min(empirical)
                    self.assertLessEqual(true[chosen]-min(true), 2*deviation+eta)

    def test_invalid_probability_kernel_is_not_silently_normalized(self):
        for weights in ({0: F(1, 2)}, {0: F(-1), 1: F(2)}, {}):
            with self.assertRaises(ValueError):
                law(weights)


if __name__ == "__main__":
    unittest.main()
