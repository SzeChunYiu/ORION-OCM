import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "grand_gmi_master_checks_v1",
    HERE / "grand_gmi_master_checks_v1.py",
)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class GrandGMIMasterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aggregate = MOD.run()

    def test_receipt_stack(self):
        r = self.aggregate["receipt_stack"]
        self.assertEqual(r["receipts"], len(list(HERE.glob("grand_gmi*checks*.py"))) - 1)
        self.assertTrue(r["all_green"])
        self.assertEqual(r["verification"], "FULL_PAYLOAD_SOURCE_BOUND_REPLAY")

    def test_approximate_relation_is_not_quotient(self):
        r = MOD.check_approximate_nontransitivity()
        self.assertTrue(r["q0_near_q1"])
        self.assertTrue(r["q1_near_q2"])
        self.assertFalse(r["q0_near_q2"])
        self.assertFalse(r["distance_threshold_is_transitive"])

    def test_cover_monotonicity(self):
        r = MOD.check_approximate_cover_monotonicity()
        self.assertEqual(r["scalar_cover_counts_eps_0_1_2"], [4, 2, 1])
        self.assertEqual(r["richer_probe_exact_classes_coarse"], 2)
        self.assertEqual(r["richer_probe_exact_classes_rich"], 3)
        self.assertTrue(r["monotonicity_green"])

    def test_aggregate(self):
        self.assertEqual(self.aggregate["terminal"], "GRAND_GMI_MASTER_INTEGRATION_V2_ALL_GREEN")

    def test_pareto_frontier_is_not_componentwise_infimum(self):
        r = MOD.check_componentwise_infimum_not_attained()
        self.assertEqual(r["pareto_frontier"], [[1, 3], [3, 1]])
        self.assertEqual(r["componentwise_infimum"], [1, 1])
        self.assertFalse(r["componentwise_infimum_attained"])


if __name__ == "__main__":
    unittest.main()
