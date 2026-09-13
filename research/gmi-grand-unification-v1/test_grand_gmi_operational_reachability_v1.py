import importlib.util
from fractions import Fraction as F
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "grand_gmi_operational_reachability_checks_v1",
    HERE / "grand_gmi_operational_reachability_checks_v1.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class ReachableFrontierCorrectionTests(unittest.TestCase):
    def test_unreachable_dominator_cannot_remove_reachable_optimum(self):
        reachable = {(2,)}
        self.assertEqual(MOD.pareto({(1,), (2,)}) & reachable, set())
        self.assertEqual(MOD.pareto(reachable), {(2,)})

    def test_zero_cost_loop_terminates_and_returns_minimum_steps(self):
        result = MOD.reachable_labels((0, 1), ((0, 0, (0,)), (0, 1, (1,))), (0,), (1,))
        self.assertEqual(result, {(0, (F(0),)): 0, (1, (F(1),)): 1})

    def test_zero_budget_still_allows_zero_cost_progress(self):
        edges = ((0, 1, (0,)), (1, 0, (0,)), (1, 2, (1,)))
        result = MOD.reachable_labels((0, 1, 2), edges, (0,), (0,))
        self.assertEqual({state for state, _ in result}, {0, 1})

    def test_same_state_retains_distinct_cost_labels(self):
        result = MOD.reachable_labels((0,), ((0, 0, (F(1, 2),)),), (0,), (1,))
        self.assertEqual(result, {(0, (F(0),)): 0, (0, (F(1, 2),)): 1, (0, (F(1),)): 2})

    def test_vector_budget_cannot_use_unattainable_coordinatewise_minimum(self):
        edges = ((0, 1, (1, 3)), (0, 1, (3, 1)))
        denied = MOD.reachable_labels((0, 1), edges, (0,), (2, 2))
        self.assertEqual({state for state, _ in denied}, {0})
        allowed = MOD.reachable_labels((0, 1), edges, (0,), (3, 3))
        self.assertEqual({label for state, label in allowed if state == 1}, {(1, 3), (3, 1)})

    def test_negative_or_dimension_mismatched_edges_are_rejected(self):
        for cost in ((-1,), (1, 0)):
            with self.subTest(cost=cost), self.assertRaises(ValueError):
                MOD.reachable_labels((0,), ((0, 0, cost),), (0,), (1,))

    def test_exhaustive_finite_frontier_and_graph_oracles(self):
        frontiers = MOD.frontier_restriction_checks()
        self.assertEqual(frontiers["finite_profile_scope_cases"], 5103)
        self.assertGreater(frontiers["filter_global_frontier_loses_reachable_optima"], 0)
        graphs = MOD.graph_closure_checks()
        self.assertEqual(graphs["graph_budget_cases"], 2187)
        self.assertGreater(graphs["cases_containing_zero_cost_two_cycle"], 0)

    def test_computable_real_zero_is_unresolved_at_finite_precision(self):
        never = MOD.delayed_halting_interval(None, 5)
        later = MOD.delayed_halting_interval(6, 5)
        self.assertEqual(never, later)
        self.assertEqual(never, (F(0), F(1, 32)))
        self.assertEqual(MOD.delayed_halting_interval(6, 6), (F(1, 64), F(1, 64)))

    def test_bounded_receipt(self):
        result = MOD.run()
        self.assertEqual(result["terminal"], "GMI_OPERATIONAL_REACHABILITY_CORRECTION_GREEN_AT_FINITE_SCOPE")
        self.assertEqual(result["computable_real_boundary"]["certified_interval_cases"], 1088)
        self.assertEqual(result["cycle_and_cost_labels"]["zero_loop_distinct_history_prefix"], 65)

    def test_finite_responses_do_not_bound_resource_profiles_or_registered_fibers(self):
        result = MOD.realization_universe_boundary_checks()
        self.assertEqual(result["largest_prefix_response_classes"], 1)
        self.assertEqual(result["largest_prefix_resource_profiles"], 65)
        self.assertEqual(result["same_profile_registered_fiber_size"], 65)
        self.assertEqual(result["finite_grid_budget_six_profiles"], 7)


if __name__ == "__main__":
    unittest.main()
