import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
MODULE_PATH = HERE / "grand_gmi_planning_resolution_checks_v1.py"
spec = importlib.util.spec_from_file_location("grand_gmi_planning_resolution_checks_v1", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestGrandGMIPlanningResolutionV1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = mod.run()

    def test_aggregate_green(self):
        self.assertTrue(self.result["all_checks_green"])
        self.assertEqual(
            self.result["terminal"],
            "GRAND_GMI_PLANNING_RESOLUTION_TRANCHE_ALL_GREEN",
        )

    def test_class_query_formula(self):
        self.assertEqual(self.result["class_query_theorem"], {"cases": 1360, "formula_exact": 1360})

    def test_prefix_cells(self):
        self.assertEqual(self.result["prefix_tree"]["cases"], 18)
        self.assertEqual(self.result["prefix_tree"]["formula_exact"], 18)

    def test_semantic_state_dp(self):
        q = self.result["semantic_state_planning"]
        self.assertEqual(q["value_checks"], 180)
        self.assertEqual(q["value_exact"], 180)
        self.assertEqual(q["first_action_checks"], 160)
        self.assertEqual(q["first_action_exact"], 160)

    def test_exponential_first_action_witness(self):
        w = self.result["canonical_exponential_first_action_witness"]
        self.assertEqual(w["output_bits"], 1)
        self.assertEqual(w["leaf_verifier_queries"], 512)

    def test_arbitrary_class_sizes(self):
        self.assertEqual(mod.min_label_queries((1, 2, 4)), 3)
        self.assertEqual(mod.min_label_queries((4, 4, 4)), 8)


if __name__ == "__main__":
    unittest.main()
