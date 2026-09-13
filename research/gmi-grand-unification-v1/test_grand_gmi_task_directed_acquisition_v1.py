import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "task_acquisition", HERE / "grand_gmi_task_directed_acquisition_checks_v1.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class TestTaskDirectedAcquisition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = MOD.run_checks()

    def test_complete_policy_census_and_frozen_receipt(self):
        self.assertTrue(self.result["all_checks_green"])
        self.assertEqual(self.result["census"], {
            "instances": 87808, "recurrence_oracle": 87808,
            "identifiability_iff": 87808, "memory_checks": 263424,
            "memory_oracle": 263424, "adequate": 72928, "inadequate": 14880,
            "action_without_profile_identification": 32832})
        frozen = json.loads((HERE / "GRAND_GMI_TASK_DIRECTED_ACQUISITION_RECEIPT_V1.json").read_text())
        self.assertEqual(json.loads(json.dumps(self.result)), frozen)

    def test_zero_tests_can_succeed_without_identifying_response_profile(self):
        matrix, success = ((), ()), ({0, 1}, {0, 2})
        self.assertNotEqual(success[0], success[1])
        self.assertEqual(MOD.acquisition_cost(matrix, success, ()), 0)
        oracle = MOD.policy_oracle(matrix, (), (0, 1, 2), 0)
        self.assertEqual(MOD.oracle_cost(oracle, success), 0)
        self.assertEqual(MOD.retained_cost(matrix, success, (), 1), 0)

    def test_unnecessary_revealing_test(self):
        matrix, success = ((0,), (1,)), ({0, 1}, {0, 2})
        self.assertEqual(MOD.acquisition_cost(matrix, success, (1,)), 0)
        self.assertEqual(MOD.acquisition_cost(matrix, ({0}, {1}), (1,)), 1)

    def test_higher_order_conflict_is_not_pairwise_identifiability(self):
        matrix, success = ((0,), (0,), (0,)), ({0, 1}, {1, 2}, {0, 2})
        for i in range(3):
            for j in range(i):
                self.assertTrue(success[i].intersection(success[j]))
        self.assertFalse(MOD.observable_adequate(matrix, success))
        self.assertIsNone(MOD.acquisition_cost(matrix, success, (0,)))
        self.assertIsNone(MOD.oracle_cost(MOD.policy_oracle(matrix, (0,), (0, 1, 2), 2), success))

    def test_empty_action_row_is_impossible_even_if_fully_observed(self):
        matrix, success = ((0,), (1,)), (set(), {1})
        self.assertIsNone(MOD.acquisition_cost(matrix, success, (1,)))
        self.assertIsNone(MOD.retained_cost(matrix, success, (1,), 2))

    def test_zero_cost_separator_and_weighted_choice(self):
        matrix, success = ((0, 0), (1, 1)), ({0}, {1})
        self.assertEqual(MOD.acquisition_cost(matrix, success, (0, 9)), 0)
        self.assertEqual(MOD.acquisition_cost(matrix, success, (7, 2)), 2)
        self.assertEqual(MOD.oracle_cost(MOD.policy_oracle(matrix, (7, 2), (0, 1), 1), success), 2)

    def test_actual_policy_oracle_obeys_information_pattern(self):
        profiles = MOD.policy_oracle(((0,), (0,)), (1,), (0, 1), 2)
        self.assertEqual(set(profiles), {(0, 0), (1, 1)})
        self.assertNotIn((0, 1), profiles)
        self.assertEqual(len(MOD.policy_trees((2, 2), 2)), 19)
        self.assertEqual(len(MOD.policy_trees((3, 2, 2, 2), 2)), 201)

    def test_separate_minima_are_jointly_infeasible(self):
        witness = self.result["tradeoff_witness"]
        self.assertEqual(witness["capacity_cost_oracle"], [
            [1, None, None], [2, 2, 2], [3, 1, 1], [4, 1, 1], [5, 1, 1]])
        self.assertEqual(witness["frontier"], [[1, 3], [2, 2]])

    def test_cut_coloring_need_not_be_realizable_by_shallow_tests(self):
        matrix = ((1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 0, 0))
        success = tuple({i} for i in range(4))
        self.assertEqual(MOD.acquisition_cost(matrix, success, (1, 1, 1)), 3)
        oracle = MOD.policy_oracle(matrix, (1, 1, 1), (0, 1, 2, 3), 2)
        self.assertIsNone(MOD.oracle_cost(oracle, success))
        # An explicit three-query policy witnesses the surviving upper bound.
        tree = (0, ((1, ((2, (None, None)), None)), None))
        traces = [MOD.execute(tree, row, (1, 1, 1)) for row in matrix]
        self.assertEqual(len({path for path, _ in traces}), 4)
        self.assertEqual(max(cost for _, cost in traces), 3)


if __name__ == "__main__":
    unittest.main()
