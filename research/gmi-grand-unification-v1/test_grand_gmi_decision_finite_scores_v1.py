import importlib.util
import math
import pathlib
import unittest
from fractions import Fraction

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "grand_gmi_decision_finite_scores_checks_v1",
    HERE / "grand_gmi_decision_finite_scores_checks_v1.py",
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestGrandGMIDecisionFiniteScoresV1(unittest.TestCase):
    def test_all_infinite_scores_never_produce_regret_certificate(self):
        with self.assertRaisesRegex(ValueError, "finite regret is undefined"):
            mod.decision_report((math.inf, math.inf), (math.inf, math.inf), 0)

    def test_infinite_unusable_actions_preserve_finite_regret_guarantee(self):
        result = mod.decision_report((0, 2, math.inf), (1, 1, math.inf), 1)
        self.assertEqual(result["infinite_action_indices"], (2,))
        self.assertEqual(result["estimated_minimizers"], (0, 1))
        self.assertEqual(result["regrets"], (0, 2))

    def test_infinite_status_cannot_change_under_finite_uniform_error(self):
        for true, estimated in (((0, math.inf), (0, 1)), ((0, 1), (0, math.inf))):
            with self.assertRaisesRegex(ValueError, "cannot change"):
                mod.decision_report(true, estimated, 100)

    def test_equality_tie_is_allowed_but_unique_selection_is_not_certified(self):
        result = mod.decision_report((0, 2), (1, 1), 1)
        self.assertEqual(result["true_minimizers"], (0,))
        self.assertEqual(result["estimated_minimizers"], (0, 1))
        self.assertEqual(max(result["regrets"]), result["regret_bound"])

    def test_any_exact_positive_margin_above_boundary_excludes_the_competitor(self):
        slack = Fraction(1, 10**100)
        result = mod.decision_report((0, 2 + slack), (1, 1 + slack), 1)
        self.assertEqual(result["estimated_minimizers"], (0,))
        self.assertGreater(result["margin"], 2)

    def test_singleton_and_only_finite_action_have_vacuous_stability(self):
        for true, estimated, chosen in (((7,), (8,), 0), ((math.inf, 7), (math.inf, 8), 1)):
            result = mod.decision_report(true, estimated, 1)
            self.assertEqual(result["margin"], math.inf)
            self.assertEqual(result["allowed_choices"], (chosen,))
            self.assertEqual(result["regrets"], (0,))

    def test_selection_slack_is_needed_even_when_representation_bound_is_valid(self):
        exact_choice = mod.decision_report((0, 3), (1, 2), 1)
        approximate_choice = mod.decision_report((0, 3), (1, 2), 1, alpha=1)
        self.assertEqual(exact_choice["allowed_choices"], (0,))
        self.assertEqual(approximate_choice["allowed_choices"], (0, 1))
        self.assertGreater(max(approximate_choice["regrets"]), exact_choice["regret_bound"])
        self.assertEqual(max(approximate_choice["regrets"]), approximate_choice["regret_bound"])

    def test_zero_precision_selects_only_true_minimizers(self):
        result = mod.decision_report((0, 2), (0, 2), 0)
        self.assertEqual(result["allowed_choices"], (0,))
        self.assertEqual(result["regrets"], (0,))

    def test_invalid_precision_scores_and_empty_actions_are_rejected(self):
        for value in (math.inf, -math.inf, math.nan, -1, True):
            with self.assertRaises(ValueError):
                mod.decision_report((0,), (0,), value)
        with self.assertRaises(ValueError):
            mod.decision_report((), (), 0)

    def test_additive_receipt(self):
        result = mod.run()
        self.assertTrue(result["all_checks_green"], result["checks"])
        self.assertEqual(result["observed"], {"finite_perturbation_cases": 225, "invalid_domains_rejected": 12})

    def test_empty_ecology_is_rejected_before_supremum(self):
        with self.assertRaisesRegex(ValueError, "nonempty finite ecology"):
            mod.finite_field_report(((),), ((),), 0)

    def test_equal_robust_scores_do_not_certify_loss_field_accuracy(self):
        self.assertEqual(mod.decision_report((100,), (100,), 1)["regrets"], (0,))
        with self.assertRaisesRegex(ValueError, "Loss-field error"):
            mod.finite_field_report(((0, 100),), ((50, 100),), 1)


if __name__ == "__main__":
    unittest.main()
