"""Independent controls for fixed-model learning and uncertainty timing."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
import json
import math
import subprocess
import unittest
from unknown_model_frontier_v1 import Action, Model, frontier, successful_costs, rectangular, posterior
from unknown_model_mixtures_v1 import minimax_mixture, charged_minimax
from unknown_model_oracle_v1 import fixed_points, independent_frontier, switching, execute, policies
from grand_gmi_unknown_model_checks_v1 import apparatus, check, census


class UnknownModelTests(unittest.TestCase):
    def test_complete_stochastic_policy_and_nature_census(self):
        result = census()
        self.assertEqual(result["rational_two_model_kernels"], 81)
        self.assertEqual(result["common_policy_trees"], 578)
        self.assertEqual(result["fixed_model_terminal_path_executions"], 2260)
        self.assertEqual(result["changing_model_nature_tables"], 4452)

    def test_fixed_model_policy_frontier_and_declared_random_seed_timing(self):
        model = apparatus()
        result, count = check(model, 4)
        costs = successful_costs(result["points"], 2)
        self.assertEqual(costs, ((2, 4), (4, 2)))
        self.assertEqual(count["common_trees"], 13)
        self.assertEqual(min(map(max, costs)), 4)
        mix = minimax_mixture(costs)
        self.assertEqual(mix["value"], 3)
        self.assertEqual(tuple(sum(w*costs[i][j] for i, w in mix["mixture"]) for j in range(2)), (3, 3))
        # Nature that sees the seed first instead obtains E_seed[max_theta J]=4.
        self.assertEqual(sum(w*max(costs[i]) for i, w in mix["mixture"]), 4)

    def test_no_reset_comparison_includes_full_randomized_policy_class(self):
        result, _ = check(apparatus(reset=False), 4)
        costs = successful_costs(result["points"], 2)
        self.assertEqual(costs, ((2, 7), (6, 6), (7, 2)))
        self.assertEqual(min(map(max, costs)), 6)
        self.assertEqual(minimax_mixture(costs)["value"], F(9, 2))
        self.assertEqual(charged_minimax(costs, F(1, 4)), F(19, 4))

    def test_sampler_cost_can_remove_the_randomization_advantage(self):
        costs = ((F(2), F(4)), (F(4), F(2)))
        self.assertEqual(charged_minimax(costs, F(1, 4)), F(13, 4))
        self.assertEqual(charged_minimax(costs, 2), 4)

    def test_reset_cost_is_not_erased_when_testing_revival(self):
        result, _ = check(apparatus(reset_cost=4), 4)
        costs = successful_costs(result["points"], 2)
        self.assertEqual(min(map(max, costs)), 6)
        self.assertEqual(minimax_mixture(costs)["value"], F(9, 2))

    def test_finish_consumes_a_charged_control(self):
        short, _ = check(apparatus(), 3)
        self.assertEqual(min(map(max, successful_costs(short["points"], 2))), 6)
        self.assertIn((0, 1, 2, 4), short["points"])
        # Failure under theta1 is a deadline at ready R, not a successful output.
        _, paths = fixed_points(apparatus(), 0, state=2)
        self.assertEqual(paths["fixed_model_path_executions"], 2)
        self.assertEqual(set(frontier(apparatus(), 0, 2)["points"]), {(1, 1, 1, 1)})

    def test_switching_adversary_is_checked_by_complete_nature_tables(self):
        model = apparatus()
        expected = switching(model, 4)
        actual = rectangular(model, 4)
        self.assertEqual(actual["successful_minimax_work"], 6)
        self.assertEqual(expected["successful_minimax_work"], 6)
        self.assertEqual(expected["nature_table_assignments"], 612)
        missing = apparatus(fallback=False)
        self.assertTrue(successful_costs(frontier(missing, 4)["points"], 2))
        self.assertEqual(rectangular(missing, 4)["minimum_worst_failure"], 1)
        self.assertIsNone(switching(missing, 4)["successful_minimax_work"])

    def test_per_model_oracles_do_not_supply_one_common_policy(self):
        points, _ = fixed_points(apparatus(), 4)
        costs = successful_costs(points, 2)
        self.assertEqual(tuple(min(v[j] for v in costs) for j in range(2)), (2, 2))
        self.assertNotIn((2, 2), costs)
        self.assertTrue(all(sum(v) >= 6 for v in costs))

    def test_posterior_persists_and_overlapping_likelihoods_do_not_identify(self):
        self.assertEqual(posterior((F(1, 2),)*2, (0, 1)), (0, 1))
        self.assertEqual(posterior((0, 1), (1, 1)), (0, 1))
        uncertain = posterior((F(1, 2),)*2, (F(1, 4), F(3, 4)))
        self.assertEqual(uncertain, (F(1, 4), F(3, 4)))
        self.assertIsNone(posterior((0, 1), (1, 0)))

    def test_noisy_model_frontier_keeps_all_model_coordinates(self):
        model = apparatus()
        a = replace(model.actions[0][0], rows=((0, F(1, 4), F(3, 4), 0), (0, F(3, 4), F(1, 4), 0)))
        model = replace(model, actions=((a,)+model.actions[0][1:],)+model.actions[1:])
        actual, _ = check(model, 4)
        raw, _ = fixed_points(model, 4)
        self.assertEqual(set(actual["points"]), independent_frontier(raw))
        self.assertTrue(any(v[0] != v[1] for v in raw))

    def test_supplied_hypotheses_are_not_a_coverage_certificate(self):
        base = apparatus(fallback=False)
        point, tree = next((v, t) for v, t in frontier(base, 4)["points"].items() if v[:2] == (0, 0))
        actions = []
        for state, row in enumerate(base.actions):
            more = []
            for action in row:
                extra = (0, 1, 0, 0) if state == 0 else action.rows[0]
                more.append(replace(action, rows=action.rows+(extra,)))
            actions.append(tuple(more))
        extended = replace(base, actions=tuple(actions), models=3)
        self.assertEqual(execute(extended, tree, theta=2)[0][0], 1)
        self.assertFalse(successful_costs(frontier(extended, 4)["points"], 3))

    def test_mixture_vertex_enumeration_needs_three_models_and_supports(self):
        costs = ((0, 3, 3), (3, 0, 3), (3, 3, 0))
        result = minimax_mixture(costs)
        self.assertEqual(result["value"], 2)
        self.assertEqual(len(result["mixture"]), 3)
        grid = []
        for i, j in product(range(13), repeat=2):
            if i+j <= 12:
                weights = (F(i, 12), F(j, 12), F(12-i-j, 12))
                grid.append(max(sum(w*v[t] for w, v in zip(weights, costs)) for t in range(3)))
        self.assertEqual(min(grid), result["value"])
        self.assertTrue(all(sum(v) == 6 for v in costs))  # Uniform-model dual lower bound 2.

    def test_deadlines_dead_ends_and_actual_abort_charges(self):
        model = replace(apparatus(), abort=(7, 2, 3, 0))
        self.assertEqual(set(frontier(model, 0)["points"]), {(1, 1, 7, 7)})
        self.assertEqual(set(frontier(model, 0, 3)["points"]), {(0, 0, 0, 0)})
        dead = apparatus(reset=False, fallback=False)
        self.assertEqual(set(frontier(dead, 5, 1)["points"]), {(1, 1, 1, 1)})
        self.assertIsNone(minimax_mixture(())["value"])

    def test_invalid_resource_and_kernel_registers(self):
        for horizon in (True, -1, math.inf, math.nan):
            with self.assertRaises(ValueError):
                frontier(apparatus(), horizon)
        for charge in (True, -1, math.inf, math.nan, 0.5):
            with self.assertRaises(ValueError):
                frontier(replace(apparatus(), abort=(charge, 1, 1, 0)), 4)
            with self.assertRaises(ValueError):
                charged_minimax(((1, 2),), charge)
        bad = Action("invalid", F(1), ((1, 1), (0, 1)))
        with self.assertRaises(ValueError):
            frontier(Model(((bad,), ()), 2, 1, (1, 0)), 2)

    def test_isolated_standalone_checker(self):
        path = Path(__file__).with_name("grand_gmi_unknown_model_checks_v1.py")
        result = subprocess.run([sys.executable, "-I", "-B", str(path)], check=True, capture_output=True, text=True)
        receipt = json.loads(result.stdout)
        self.assertTrue(receipt["all_checks_green"])
        self.assertEqual(receipt["fixed_model_including_sampler_minimax"], "13/4")


if __name__ == "__main__":
    unittest.main()
