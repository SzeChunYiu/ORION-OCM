import json
from fractions import Fraction as F
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from grand_gmi_finite_data_checks_v1 import run
from finite_data_model_v1 import (Problem, certificate, cheapest_mixture, intervals,
                                 model_distance, synthesize, transfer_bounds)
from finite_data_oracle_v1 import (all_profiles, dual_mixture_cost, mixed_evaluate,
                                  ordered_count_law, path_evaluate, policy_syntax)
from finite_data_sampling_v1 import (confidence_upper, count_law, empirical_register,
                                    row_confidence_upper, simultaneous_failure)
from finite_data_witnesses_v1 import (chain, choice, falsifying_controls, positive_certificate,
                                    register_controls, sharp_controls)


class FiniteDataTests(unittest.TestCase):
    def test_full_payload_matches_independent_finite_census(self):
        receipt = json.loads((HERE / "GRAND_GMI_FINITE_DATA_MODEL_TRANSFER_RECEIPT_V1.json").read_text())
        actual = run()
        self.assertEqual(actual, receipt)
        self.assertEqual(actual["policy_census"]["common_policy_comparisons"], 104976)
        self.assertEqual(actual["policy_census"]["syntax_trees"], 1680)
        self.assertEqual(actual["sampling_census"]["exact_tail_bounds"], 720)

    def test_sharp_success_and_stage_terminal_costs(self):
        result = sharp_controls()
        self.assertEqual(result["sharp_cases"], 20)
        self.assertEqual(result["H4_epsilon_quarter"], [F(175, 256), F(1581, 256)])

    def test_zero_horizon_has_no_model_error(self):
        p = choice(horizon=0)
        self.assertEqual(transfer_bounds(p, 1), (0, 0))
        self.assertEqual(set(all_profiles(p)[0]), {(0, 0)})

    def test_early_settlement_is_charged_once(self):
        p = choice(F(1), horizon=3)
        p = Problem(p.rows, p.stage, (0, 2, 4), p.goals)
        self.assertEqual(set(all_profiles(p)[0]), {(F(1), F(3)), (F(1), F(5))})

    def test_ready_is_not_finished_and_finish_consumes_slot(self):
        rows = (((0, 1, 0),), ((0, 0, 1),), ())
        stage = ((1,), (3,), ())
        for h, expected in ((1, (0, 3)), (2, (1, 6))):
            p = Problem(rows, (stage,)*h, (0, 2, 2), frozenset({2}))
            self.assertEqual(set(all_profiles(p)[0]), {expected})

    def test_probe_reset_finish_charges_complete_path(self):
        rows = (((0, 1, 0), (0, 0, 1)), ((1, 0, 0),), ())
        p = Problem(rows, (((1, 3), (2,), ()),)*3, (0, 4, 2), frozenset({2}))
        paths = policy_syntax((2, 1, 0), 3, 0)
        tree = next(t for t in paths if t[0] == 0 and t[1][1][0] == 0 and t[1][1][1][0][0] == 1)
        self.assertEqual(path_evaluate(p, tree)[0], (1, 8))
        self.assertEqual(dual_mixture_cost(all_profiles(p)[0], F(1)), 5)

    def test_probability_and_cost_intervals_are_clipped(self):
        p = choice()
        self.assertEqual(intervals(p, (F(1), F(3)), 1)[0], (F(0), F(1)))
        self.assertEqual(intervals(p, (F(0), F(1)), 1)[0], (F(0), F(1)))
        self.assertEqual(intervals(p, (F(1), F(3)), 1)[1], (F(0), F(7)))

    def test_missing_terminal_charge_and_wrong_horizon_are_refuted(self):
        record = falsifying_controls()["rare_hazard"]
        self.assertEqual(record["bound"], (F(1, 8), F(1, 2)))
        self.assertGreater(record["empirical_success"]-record["true_success"], 0)
        self.assertGreater(record["cost_gap"], 0)

    def test_post_transition_cost_requires_next_index(self):
        p = Problem((((F(7, 8), F(1, 8)),), ()), (((0,), ()),), (0, 0), frozenset({1}))
        wrong_cost_bound = transfer_bounds(p, F(1, 8))[1]
        actual_post_transition_work = sum(w*c for w, c in zip(p.rows[0][0], (0, 1)))
        self.assertGreater(actual_post_transition_work, wrong_cost_bound)

    def test_half_l1_not_quarter_l1(self):
        p, q = choice(F(1)), choice(F(7, 8))
        self.assertEqual(model_distance(p, q), F(1, 8))
        self.assertEqual(sum(abs(a-b) for a, b in zip(p.rows[0][0], q.rows[0][0])), F(1, 4))

    def test_changing_policy_is_not_model_transfer(self):
        p = choice(F(1, 2), penalty=0)
        self.assertEqual(model_distance(p, p), 0)
        self.assertEqual(set(all_profiles(p)[0]), {(F(1, 2), F(1)), (F(1), F(3))})

    def test_fixed_seed_fee_uses_augmented_objective(self):
        points = {(F(0), F(0)): ("a",), (F(1), F(2)): ("b",)}
        for fee, expected in ((0, F(1)), (F(1, 4), F(5, 4)), (10, F(2))):
            self.assertEqual(cheapest_mixture(points, F(1, 2), fee)["cost"], expected)
            self.assertEqual(dual_mixture_cost(points, F(1, 2), fee), expected)

    def test_missing_sufficient_certificate_does_not_prove_infeasible(self):
        p = choice(F(1))
        self.assertIsNone(certificate(p, 1, 1)[0])
        self.assertTrue(any(success == 1 for success, _ in all_profiles(p)[0]))

    def test_fixed_N_positive_certificate_and_full_sampling_charge(self):
        result = positive_certificate()
        self.assertLess(result["confidence_failure_upper"], result["alpha"])
        self.assertEqual(result["acquisition_setup"], 3084)
        self.assertEqual(result["custody"]["recorded_draws"], 768)

    def test_single_symbol_row_and_known_only_register(self):
        rows, counts = empirical_register((1, 0), {(0, 0): (1,)}, {},
                                         tuple((0, 0, i, 1) for i in range(4)), 4)
        self.assertEqual(rows, (((F(0), F(1)),), ()))
        self.assertEqual(row_confidence_upper((1,), 4, 0), 0)
        known, empty = empirical_register((1, 0), {}, {(0, 0): (0, 1)}, (), 4)
        self.assertEqual(known, rows)
        self.assertEqual(empty["recorded_draws"], 0)
        self.assertEqual(row_confidence_upper((), 4, 0), 0)

    def test_unreachable_row_and_custody_mutations_rejected(self):
        self.assertEqual(register_controls()["rejected"], ["omitted_unreachable_row", "missing_draw",
                         "duplicate_draw", "outside_supplied_alphabet", "changed_known_costs"])

    def test_observed_support_is_not_known_support(self):
        result = register_controls()
        self.assertEqual(result["false_support_radius"], 0)
        self.assertGreater(result["true_omitted_hazard"], 0)
        self.assertEqual(result["drift_success_gap"], 1)

    def test_correlated_draws_break_the_iid_confidence_claim(self):
        result = falsifying_controls()
        self.assertGreater(result["copied_draw_failure"], result["falsely_applied_iid_upper"])

    def test_row_union_needed_after_data_selection(self):
        result = falsifying_controls()
        self.assertEqual(result["single_row_tail"], F(1, 8))
        self.assertEqual(result["two_row_tail"], F(15, 64))
        self.assertEqual(result["selected"]["expected_selection_optimism"], F(35, 256))

    def test_exact_multinomial_against_ordered_draws(self):
        row = (F(1, 4), F(1, 2), F(1, 4))
        self.assertEqual(count_law(row, 4), ordered_count_law(row, 4))

    def test_rare_unseen_hazard_stays_inside_confidence_region(self):
        r = falsifying_controls()["rare_hazard"]
        self.assertGreater(r["all_safe_probability"], 0)
        self.assertLess(r["true_success"], 1)
        self.assertEqual(r["eta"], r["bound"][0])

    def test_nonfinite_or_inconsistent_registers_are_rejected(self):
        with self.assertRaises(ValueError):
            transfer_bounds(choice(), float("inf"))
        with self.assertRaises(ValueError):
            confidence_upper(1, 2, 0, F(1, 8))
        with self.assertRaises(ValueError):
            Problem((((1, 1),), ()), (((0,), ()),), (0, 0), frozenset({1}))
        p = choice()
        with self.assertRaises(ValueError):
            model_distance(p, Problem(p.rows, p.stage, p.settlement, frozenset({2})))


if __name__ == "__main__":
    unittest.main()
