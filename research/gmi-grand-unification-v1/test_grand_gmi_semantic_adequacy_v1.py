import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("semantic_adequacy", HERE / "grand_gmi_semantic_adequacy_checks_v1.py")
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class SemanticAdequacyTests(unittest.TestCase):
    def test_full_response_count_is_not_task_memory_requirement(self):
        rows = M.overlap_witnesses()
        self.assertEqual(rows["common_action"]["task_messages"], 1)
        self.assertEqual(rows["three_way_conflict"]["task_messages"], 2)

    def test_zero_probability_versions_are_not_all_history_identity(self):
        self.assertEqual(M.null_history_versions()["all_history_response_class_counts"], [1, 2])

    def test_new_receipt_matches_exact_enumeration(self):
        actual = M.run()
        expected = json.loads((HERE / "GRAND_GMI_SEMANTIC_ADEQUACY_RECEIPT_V1.json").read_text())
        self.assertEqual(actual, expected)
        self.assertEqual(actual["relational_enumeration"]["three_state_three_action_instances"], 343)
        self.assertEqual(actual["relational_enumeration"]["singleton_function_equalities"], 27)
        self.assertEqual(actual["continuation"]["countdown_update_checks"], 432)
        self.assertGreater(actual["relational_enumeration"]["strict_response_vs_task_gaps"], 0)


if __name__ == "__main__":
    unittest.main()
