"""Independent fault, cost, scope and exact-policy controls for PCA."""
from fractions import Fraction as F
from pathlib import Path
import json
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from grand_gmi_probabilistic_acquisition_model_v1 import (
    ContractError, bellman_certificate, finite_horizon, persistent_probe,
    solve, stationary, validate)
from grand_gmi_probabilistic_acquisition_checks_v1 import (
    execute_table, latent_average, policy_oracle, run)


class ProbabilisticAcquisitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = run()

    def test_exact_committed_receipt(self):
        path = Path(__file__).with_name("GRAND_GMI_PROBABILISTIC_ACQUISITION_RECEIPT_V1.json")
        self.assertEqual(self.receipt, json.loads(path.read_text()))
        self.assertTrue(self.receipt["all_checks_green"])
        self.assertEqual(self.receipt["horizon_two_kernels"], 1296)
        self.assertEqual(self.receipt["stationary_support_graph_start_cases"], 147)

    def test_cost_and_probability_contract(self):
        for cost in (0, -1, True, 1.0, float("nan")):
            with self.assertRaises(ContractError):
                validate((((cost, (0, 1)),), ()))
        for probs in ((0, 0), (-1, 2), (False, 1), (0.0, 1), (1,)):
            with self.assertRaises(ContractError):
                validate((((1, probs),), ()))
        for model in (((), ()), (((1, (0, 1)),),), [(), ()]):
            with self.assertRaises(ContractError):
                validate(model)
        for h in (-1, True, 1.0):
            with self.assertRaises(ContractError):
                finite_horizon(persistent_probe(), h)

    def test_exact_linear_solver_and_singular_rejection(self):
        matrix = ((F(1), F(-1, 2)), (F(-1, 3), F(1)))
        result = solve(matrix, (1, 2))
        self.assertEqual(tuple(sum(a*b for a, b in zip(row, result)) for row in matrix), (1, 2))
        self.assertEqual(result, (F(12, 5), F(14, 5)))
        with self.assertRaises(ContractError):
            solve(((1, 1), (2, 2)), (1, 2))

    def test_zero_probability_goal_does_not_remove_trap(self):
        model = (((1, (1, 0)),), ())
        result = stationary(model, (0,))
        self.assertEqual(result, {"sure": False, "almost_sure": False,
                                  "success": F(0), "expected_cost": None})
        self.assertEqual(finite_horizon(model, 10), ((F(0), F(1)), (None, F(0))))

    def test_cycle_with_exit_is_as_not_sure(self):
        model = (((3, (F(99, 100), F(1, 100))),), ())
        result = stationary(model, (0,))
        self.assertFalse(result["sure"])
        self.assertTrue(result["almost_sure"])
        self.assertEqual(result["expected_cost"], 300)
        sure = (((3, (0, 1)),), ())
        self.assertTrue(stationary(sure, (0,))["sure"])
        self.assertEqual(stationary(sure, (0,))["expected_cost"], 3)

    def test_reachable_trap_positive_probability(self):
        model = (((1, (0, F(1, 3), F(2, 3))),), ((1, (0, 1, 0)),), ())
        result = stationary(model, (0, 0))
        self.assertEqual(result["success"], F(2, 3))
        self.assertFalse(result["almost_sure"])
        self.assertIsNone(result["expected_cost"])

    def test_bellman_certificates_reject_wrong_values_and_policy(self):
        model = persistent_probe(True, True)
        self.assertTrue(bellman_certificate(model, (3, 4, 0), (0, 1)))
        for values, policy in (((2, 3, 0), (0, 1)), ((5, 5, 0), (1, 2)),
                               ((3, 4, 0), (0, 0)), ((3, 4, 1), (0, 1))):
            self.assertFalse(bellman_certificate(model, values, policy))

    def test_biased_mode_cost_law_and_fallback(self):
        for p in (F(1, 3), F(2, 3), F(1)):
            value = (1+(1-p))/p
            fallback = value+2
            model = (((1, (0, 1-p, p)), (fallback, (0, 0, 1))),
                     ((1, (0, 1, 0)), (1, (1, 0, 0)), (fallback, (0, 0, 1))), ())
            self.assertTrue(bellman_certificate(model, (value, value+1, 0), (0, 1)))
            exact = finite_horizon(model, 2)
            oracle = policy_oracle(model, 2)
            self.assertEqual((exact[0][0], exact[1][0]), oracle[:2])
            self.assertEqual(exact[1][0], value+(1-p)*(fallback-1-value))

    def test_cheaper_fallback_reverses_expected_optimal_policy(self):
        model = (((1, (0, F(1, 2), F(1, 2))), (3, (0, 0, 1))),
                 ((1, (0, 1, 0)), (1, (1, 0, 0)), (3, (0, 0, 1))), ())
        self.assertTrue(bellman_certificate(model, (F(5, 2), 3, 0), (0, 2)))
        self.assertFalse(bellman_certificate(model, (3, 4, 0), (0, 1)))
        self.assertEqual(policy_oracle(model, 3)[1], F(5, 2))

    def test_deadline_and_expected_work_objectives_differ(self):
        model = persistent_probe(True, True)
        success, sure_cost = finite_horizon(model, 1)
        self.assertEqual((success[0], sure_cost[0]), (1, 5))
        self.assertEqual(stationary(model, (0, 1))["expected_cost"], 3)
        self.assertEqual(finite_horizon(persistent_probe(True), 1)[0][0], F(1, 2))

    def test_independent_latent_persistence_rejects_iid_approximation(self):
        self.assertEqual(latent_average(8)[0], F(1, 2))
        self.assertNotEqual(latent_average(8)[0], 1-F(1, 2**8))
        self.assertEqual(latent_average(8, True)[0], F(15, 16))
        self.assertEqual(latent_average(4, True, 2), (F(1), F(13, 4), 8))

    def test_direct_vs_cutoff_expected_and_worst_work(self):
        model = persistent_probe(True, True)
        direct = execute_table(model, ((1, 2),), 0)
        cutoff = execute_table(model, ((0, 2), (1, 2)), 0)
        self.assertEqual(direct, (1, 5, 5))
        self.assertEqual(cutoff, (1, F(7, 2), 6))

    def test_zero_horizon_and_absorbing_goal(self):
        model = persistent_probe(True, True)
        self.assertEqual(policy_oracle(model, 0)[:2], (0, None))
        self.assertEqual(policy_oracle(model, 0, 2)[:2], (1, 0))
        self.assertEqual(stationary(model, (0, 1), 2),
                         {"sure": True, "almost_sure": True, "success": F(1), "expected_cost": F(0)})


if __name__ == "__main__":
    unittest.main()
