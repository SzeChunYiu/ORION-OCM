import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "proof_reuse", Path(__file__).with_name("grand_gmi_proof_search_checks_v1.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ProofReuseTests(unittest.TestCase):
    def test_actual_query_trees_include_no_certificate_world(self):
        for n in range(1, 9):
            self.assertEqual(mod.query_tree_value(n, False), n)
            self.assertEqual(mod.query_tree_value(n, True), n - 1)

    def test_enumerated_request_traces_and_subset_schedules(self):
        result = mod.run()
        self.assertTrue(result["all_checks_green"])
        self.assertEqual(result["request_schedules"], {"cases": 500, "matches": 500})
        self.assertEqual(result["capacity"], {"cases": 1000, "matches": 1000})
        self.assertEqual(result["certificate_transport"], {
            "solve_profiles_equal": True, "raw_reuse_accepted": False,
            "transported_reuse_accepted": True})

    def test_capacity_changes_optimal_admission(self):
        items = ((7, 0, 0, 2, 4), (5, 0, 0, 2, 3), (5, 0, 0, 2, 3))
        self.assertEqual(mod.capacity_solution(items, 6), (24, (1, 2)))
        self.assertEqual(mod.capacity_solution(items, 4), (27, (0,)))
        self.assertEqual(mod.capacity_solution(items, 0), (34, ()))
        self.assertEqual(mod.greedy_execution(items, 6, False), (27, (0,)))
        self.assertEqual(mod.greedy_execution(items, 6, True), (27, (0,)))

    def test_density_greedy_can_also_be_optimal(self):
        items = ((6, 0, 0, 2, 4), (5, 0, 0, 2, 3), (5, 0, 0, 2, 3))
        self.assertEqual(mod.greedy_execution(items, 6, True), (22, (1, 2)))
        self.assertEqual(mod.greedy_execution(items, 6, False), (26, (0,)))

    def test_storage_and_validation_can_remove_reuse_benefit(self):
        self.assertEqual(mod.request_schedule_cost(2, 100, 0, 4), 8)
        self.assertEqual(mod.request_schedule_cost(2, 0, 3, 4), 8)
        self.assertEqual(mod.capacity_solution(((2, 3, 3, 4, 1),), 9), (8, ()))

    def test_context_specific_certificate_transport(self):
        verifier = lambda context, certificate: context == certificate
        solve = lambda context: context
        self.assertEqual([verifier(x, solve(x)) for x in (0, 1)], [True, True])
        self.assertFalse(verifier(1, solve(0)))
        transported = lambda old_context, new_context, proof: new_context
        self.assertTrue(verifier(1, transported(0, 1, solve(0))))

    def test_invalid_contract_rejected(self):
        for value in (-1, True, 1.5):
            with self.assertRaises(ValueError):
                mod.capacity_solution((), value)
        with self.assertRaises(ValueError):
            mod.capacity_solution(((1, 0, 0, 2, 0),), 2)
        with self.assertRaises(ValueError):
            mod.query_tree_value(0, False)


if __name__ == "__main__":
    unittest.main()
