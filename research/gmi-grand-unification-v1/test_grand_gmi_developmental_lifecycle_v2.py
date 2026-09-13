"""Regression tests for development costs in the finite path witness."""
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "developmental_lifecycle", HERE / "grand_gmi_developmental_reachability_checks_v1.py"
)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class DevelopmentalLifecycleTests(unittest.TestCase):
    def test_budget_three_preserves_training_deployment_tradeoff(self):
        frontier, families, _ = M.selected_family("S_neutral", 3)
        self.assertEqual(frontier, ["N_good", "P_good"])
        self.assertEqual(families, ["neural", "program"])

    def test_larger_budget_retains_three_lifecycle_tradeoffs(self):
        self.assertEqual(M.selected_family("S_neutral", 10)[0],
                         ["N_good", "P_good", "X_ideal"])

    def test_deployment_only_projection_is_explicit(self):
        self.assertEqual(M.selected_family("S_neutral", 3, objective="deployment_only")[0],
                         ["P_good"])
        self.assertEqual(M.selected_family("S_neutral", 10, objective="deployment_only")[0],
                         ["X_ideal"])

    def test_start_condition_and_equal_cost_mechanisms_survive(self):
        self.assertEqual(M.selected_family("S_program", 2)[0], ["P_good"])
        paths = M.selected_family("S_neutral", 2)[2]
        mechanisms = {tuple(e[2] for e in p) for n, cost, p in paths
                      if n == "N_good" and cost == 2}
        self.assertEqual(mechanisms, {("gradient", "gradient"), ("evolution", "evolution")})

    def test_unknown_objective_fails_closed(self):
        with self.assertRaises(ValueError):
            M.selected_family("S_neutral", 3, objective="ignore_costs")

    def test_invalid_budget_fails_closed(self):
        for budget in (-1, True, 1.5):
            with self.subTest(budget=budget), self.assertRaises(ValueError):
                M.reachable_paths("S_neutral", budget)

    def test_zero_cost_cycle_keeps_endpoint_certificate_finite(self):
        edges = {"S_neutral": [("S_neutral", 0, "loop"),
                                ("N_good", 1, "construct")]}
        with patch.object(M, "EDGES", edges):
            paths = M.reachable_paths("S_neutral", 1)
        self.assertEqual([(n, c) for n, c, _ in paths], [("N_good", 1)])

    def test_invalid_development_cost_is_rejected(self):
        for cost in (-1, True, 0.5):
            with patch.object(M, "EDGES", {"S_neutral": [("N_good", cost, "bad")]}):
                with self.subTest(cost=cost), self.assertRaises(ValueError):
                    M.reachable_paths("S_neutral", 2)

    def test_cheaper_alternative_path_uses_its_own_cost(self):
        edges = {"S_neutral": [("P_good", 3, "costly"),
                                ("P_good", 1, "cheap"),
                                ("N_good", 2, "neural")]}
        with patch.object(M, "EDGES", edges):
            self.assertEqual(M.selected_family("S_neutral", 3)[0], ["P_good"])

    def test_current_receipt_reproduces_checker_output(self):
        from contextlib import redirect_stdout
        from io import StringIO
        out = StringIO()
        with redirect_stdout(out):
            M.main()
        expected = json.loads((HERE / "GRAND_GMI_DEVELOPMENTAL_LIFECYCLE_RECEIPT_V2.json").read_text())
        self.assertEqual(json.loads(out.getvalue()), expected)

    def test_charged_budget_cannot_displace_an_old_frontier(self):
        previous = set()
        for budget in range(12):
            current = set(M.selected_family("S_neutral", budget)[0])
            self.assertLessEqual(previous, current)
            previous = current


if __name__ == "__main__":
    unittest.main()
