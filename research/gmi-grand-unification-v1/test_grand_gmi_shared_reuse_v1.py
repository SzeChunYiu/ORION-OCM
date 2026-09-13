import json
import math
from pathlib import Path
import subprocess
import sys
import unittest
from dataclasses import replace
from fractions import Fraction as F
from grand_gmi_shared_reuse_checks_v1 import adaptive_census, configuration_census, hazards, shared_register
from grand_gmi_shared_reuse_model_v1 import Register, distances, graph, invalidated, mass, solve
from grand_gmi_shared_reuse_oracle_v1 import event_image, execute_stage, execute_synthesized, policy_oracle


class SharedReuseTests(unittest.TestCase):
    def test_complete_adaptive_policy_trees(self):
        result = adaptive_census()
        self.assertEqual(result["instances"], 24)
        self.assertEqual(result["complete_policy_trees"], 43968)
        self.assertEqual(result["direct_history_executions"], 84400)
        self.assertEqual((result["feasible_instances"], result["infeasible_instances"]), (18, 6))

    def test_all_three_node_dags_against_explicit_simple_traces(self):
        result = configuration_census()
        self.assertEqual(result["configuration_pair_comparisons"], 1032)
        self.assertGreater(result["simple_action_traces"], 1032)

    def test_knapsack_fit_is_not_constructive_reachability(self):
        model = shared_register()
        states, edges = graph(model, 2)
        dist, _, _ = distances(states, edges)
        self.assertEqual(mass(model, 6), 2)
        self.assertIn(6, states)
        self.assertNotIn(6, dist[0])
        states, edges = graph(model, 3)
        dist, _, _ = distances(states, edges)
        self.assertEqual(dist[0][6], 6)
        self.assertEqual(dist[0][2]+dist[0][4], 10)

    def test_memory_revival_and_joint_lifetime_work(self):
        for memory, expected in ((1, None), (2, F(12)), (3, F(10))):
            model, requests, events = shared_register(), (1, 2, 1, 2), hazards(3)
            result = solve(model, memory, requests, events)
            self.assertEqual(result["value"], expected)
            if expected is not None:
                actual = execute_synthesized(model, memory, requests, events, result)
                self.assertEqual(actual["expected"], expected)
                self.assertLessEqual(actual["peak"], memory)

    def test_stochastic_mean_and_support_worstcase_are_separate(self):
        model, requests, events = shared_register(), (1, 2, 1, 2), hazards(3, 1, F(1, 2))
        for memory, expected in ((2, F(18)), (3, F(35, 2))):
            result = solve(model, memory, requests, events)
            self.assertEqual(result["value"], expected)
            self.assertEqual(execute_synthesized(model, memory, requests, events, result)["expected"], expected)
            self.assertEqual(solve(model, memory, requests, events, objective="worstcase")["value"], 24)

    def test_general_root_hazard_work_law_on_extra_rationals(self):
        model, requests = shared_register(), (1, 2, 1, 2)
        for q in (F(1, 4), F(3, 4)):
            for memory, expected in ((2, 12+12*q), (3, 10+16*q-2*q*q)):
                events = hazards(3, 1, q)
                result = solve(model, memory, requests, events)
                self.assertEqual(result["value"], expected)
                self.assertEqual(execute_synthesized(model, memory, requests, events, result)["expected"], expected)

    def test_invalidation_crosses_evicted_ancestor(self):
        model = shared_register()
        self.assertEqual(invalidated(model, 1), 7)
        self.assertEqual(event_image(model, frozenset({1, 2}), 1), frozenset())
        self.assertEqual(solve(model, 2, (1, 1), hazards(1, 2, F(1)))["value"], 8)
        self.assertEqual(solve(model, 2, (1, 1), hazards(1, 1, F(1)))["value"], 12)
        with self.assertRaises(ValueError):
            execute_stage(model, 2, 1, event_image(model, frozenset({0, 1}), 1), (("serve", 1),))

    def test_shared_scaffold_matches_cri_on_admitted_instance(self):
        from grand_gmi_reuse_invalidation_checks_v1 import bellman
        model = Register((0, 1), (1, 1), (4, 1), (0, 1), (0, 0), (0, 0))
        events = hazards(1, 2, F(1, 2))
        result = solve(model, 2, (1, 1), events)
        self.assertEqual(result["value"], F(15, 2))
        self.assertEqual(result["value"], bellman(2, (5, 1, 6, 1, 0, F(1, 2)), True)["cold"])
        self.assertEqual(result["value"], policy_oracle(model, 2, (1, 1), events)["expected"])

    def test_post_service_prefetch_is_a_real_policy_choice(self):
        model = replace(shared_register(), sizes=(2, 1, 1), holding=F(1))
        result = solve(model, 3, (1, 2), hazards(1))
        self.assertEqual(result["value"], 9)
        self.assertIn(("build", 2), result["policy"][0, 0][2])
        self.assertEqual(execute_synthesized(model, 3, (1, 2), hazards(1), result)["expected"], 9)
        # Valid release-only schedule: retain p after a, then build b; two holding units.
        _, first, _ = execute_stage(model, 3, 1, set(),
                                    (("build", 0), ("build", 1), ("serve", 1), ("drop", 1)))
        _, second, _ = execute_stage(model, 3, 2, {0}, (("build", 2), ("serve", 2)))
        self.assertEqual(first+2+second, 10)

    def test_workspace_counts_operands_output_and_extra_scratch(self):
        model = Register((0, 1), (1, 1), (1, 1), (0, 1), (0, 1), (0, 0))
        self.assertIsNone(solve(model, 2, (1,), ())["value"])
        result = solve(model, 3, (1,), ())
        self.assertEqual(execute_synthesized(model, 3, (1,), (), result)["peak"], 3)
        with self.assertRaises(ValueError):
            execute_stage(model, 2, 1, set(), (("build", 0), ("build", 1), ("serve", 1)))

    def test_unadmitted_builder_cannot_create_a_free_certificate(self):
        model = replace(shared_register(), admitted=0b110, build=(0, 1, 1))
        self.assertIsNone(solve(model, 3, (1,), ())["value"])
        with self.assertRaises(ValueError):
            execute_stage(model, 3, 1, set(), (("build", 0), ("build", 1), ("serve", 1)))

    def test_invalidated_artifact_cleanup_is_charged(self):
        model = Register((0,), (1,), (1,), (1,), (0,), (2,))
        events = hazards(1, 1, F(1))
        result = solve(model, 1, (0, 0), events)
        self.assertEqual(result["value"], 6)
        self.assertEqual(policy_oracle(model, 1, (0, 0), events)["expected"], 6)
        self.assertEqual(execute_synthesized(model, 1, (0, 0), events, result)["expected"], 6)

    def test_zero_cost_cycles_and_final_interval(self):
        model = Register((0, 1), (1, 1), (0, 0), (0, 1), (0, 0), (0, 0))
        self.assertEqual(solve(model, 2, (1, 1), hazards(1))["value"], 2)
        costly = replace(model, holding=F(100), observe=F(20), release=(100, 100))
        self.assertEqual(solve(costly, 2, (1,), (), initial=3)["value"], 1)
        empty = solve(model, 2, (), (), initial=3)
        self.assertEqual(empty["value"], 0)
        self.assertEqual(execute_synthesized(model, 2, (), (), empty, initial=3)["peak"], 2)

    def test_invalid_inputs_cannot_be_admitted_by_infinity(self):
        for memory in (True, -1, math.inf, math.nan):
            with self.assertRaises(ValueError):
                solve(shared_register(), memory, (1,), ())
        for cost in (True, -1, math.inf, math.nan, 0.5):
            with self.assertRaises(ValueError):
                solve(replace(shared_register(), build=(cost, 1, 1)), 3, (1,), ())
        with self.assertRaises(ValueError):
            solve(replace(shared_register(), parents=(1, 0, 0)), 3, (1,), ())
        with self.assertRaises(ValueError):
            solve(shared_register(), 3, (1, 1), (((1, F(1, 2)),),))
        with self.assertRaises(ValueError):
            solve(shared_register(), 3, (1,), (), initial=8)

    def test_isolated_standalone_checker(self):
        path = Path(__file__).with_name("grand_gmi_shared_reuse_checks_v1.py")
        result = subprocess.run([sys.executable, "-I", "-B", str(path)],
                                check=True, capture_output=True, text=True)
        receipt = json.loads(result.stdout)
        self.assertTrue(receipt["all_checks_green"])
        self.assertEqual(receipt["adaptive_oracle"]["expected_matches"], 24)


if __name__ == "__main__":
    unittest.main()
