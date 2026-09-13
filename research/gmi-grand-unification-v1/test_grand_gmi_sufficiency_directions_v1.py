import importlib.util
import math
import pathlib
import unittest
from fractions import Fraction

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "grand_gmi_sufficiency_directions_checks_v1",
    HERE / "grand_gmi_sufficiency_directions_checks_v1.py",
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestGrandGMISufficiencyDirectionsV1(unittest.TestCase):
    def test_affordable_probe_with_one_state_cannot_solve_delayed_task(self):
        checked, exact, best = mod.active_policy_counts(True, 1)
        self.assertEqual((checked, exact, best), (2, 0, Fraction(1, 2)))

    def test_two_state_memory_plus_probe_has_complete_exact_policy(self):
        checked, exact, best = mod.active_policy_counts(True, 2)
        self.assertEqual((checked, exact, best), (16, 2, 1))

    def test_memory_without_information_does_not_supply_missing_bit(self):
        self.assertEqual(mod.active_policy_counts(False, 2)[1:], (0, Fraction(1, 2)))

    def test_raw_bound_above_one_does_not_block_certain_range_certificate(self):
        raw_upper = math.sqrt(math.log(40) / 2)
        self.assertGreater(raw_upper, 1)
        self.assertEqual(min(1, raw_upper), 1)

    def test_same_sample_valid_rule_can_certify_when_hoeffding_does_not(self):
        self.assertGreater(math.sqrt(math.log(40) / 4), Fraction(4, 5))
        self.assertEqual(mod.registered_two_sample_upper((0, 0)), Fraction(4, 5))
        self.assertEqual(mod.registered_two_sample_upper((0, Fraction(1, 100))), 1)

    def test_coverage_at_and_arbitrarily_close_above_threshold(self):
        for risk in (Fraction(4, 5), Fraction(4, 5) + Fraction(1, 10**100), Fraction(1)):
            failure = mod.exact_miscoverage((0, 1), (1 - risk, risk))
            self.assertLessEqual(failure, Fraction(1, 25))
            self.assertLess(failure, Fraction(1, 20))

    def test_nonreactive_hidden_self_state_is_still_unpredictable(self):
        self.assertEqual(mod.exact_predictor_count((0, 0), (0, 1)), 0)

    def test_identified_self_state_or_constant_target_allows_exact_prediction(self):
        self.assertEqual(mod.exact_predictor_count((0, 1), (0, 1)), 1)
        self.assertEqual(mod.exact_predictor_count((0, 0), (1, 1)), 1)

    def test_nested_nonbox_envelopes_move_only_in_correct_directions(self):
        outer = ((0, 4), (2, 1), (3, 3))
        inner = ((2, 1), (3, 3))
        self.assertEqual(mod.envelope(outer), ((0, 1), (3, 4)))
        self.assertEqual(mod.envelope(inner), ((2, 1), (3, 3)))

    def test_universal_strict_domination_survives_nonempty_subsets(self):
        winner = ((0, 0), (1, 1))
        loser = ((2, 2), (3, 2))
        for refined_winner in mod.nonempty_subsets(winner):
            for refined_loser in mod.nonempty_subsets(loser):
                for actual in refined_winner:
                    for alternative in refined_loser:
                        self.assertTrue(all(a <= b for a, b in zip(actual, alternative)))
                        self.assertTrue(any(a < b for a, b in zip(actual, alternative)))

    def test_receipt_covers_every_separate_direction(self):
        result = mod.run()
        self.assertTrue(result["all_checks_green"], result["checks"])
        self.assertEqual(result["self_prediction_witness"]["nonidentifiable_nonreactive_problems"], 4)
        self.assertEqual(result["generalization_witness"]["finite_probability_laws_checked"], 66)
        self.assertEqual(result["nested_resource_set_cases"], 65)


if __name__ == "__main__":
    unittest.main()
