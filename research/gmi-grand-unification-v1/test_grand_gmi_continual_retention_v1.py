import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
MODULE_PATH = HERE / "grand_gmi_continual_retention_checks_v1.py"
spec = importlib.util.spec_from_file_location("grand_gmi_continual_retention_checks_v1", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestGrandGMIContinualRetentionV1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = mod.run()

    def test_aggregate_green(self):
        self.assertTrue(self.result["all_checks_green"])
        self.assertEqual(
            self.result["terminal"],
            "GRAND_GMI_CONTINUAL_RETENTION_TRANCHE_ALL_GREEN",
        )

    def test_semantic_growth(self):
        s = self.result["sequence_semantics"]
        self.assertEqual(s["prefix_states"], 12816)
        self.assertEqual(s["monotone_prefix_states"], 12816)
        self.assertEqual(s["zero_growth_additions"], 2900)
        self.assertEqual(s["positive_growth_additions"], 5548)

    def test_memory_width_criterion(self):
        m = self.result["memory_encoder"]
        self.assertEqual(m["cases"], 1024)
        self.assertEqual(m["criterion_matches"], 1024)
        self.assertEqual(m["feasible_cases"], 580)

    def test_update_injectivity_boundary(self):
        u = self.result["update_injectivity"]
        self.assertEqual(u["four_class_update_maps"], 256)
        self.assertEqual(u["injective_updates"], 24)
        self.assertEqual(u["merging_updates"], 232)

    def test_replay_product_capacity(self):
        r = self.result["replay_capacity"]
        self.assertEqual(r["cases"], 128)
        self.assertEqual(r["criterion_matches"], 128)
        self.assertEqual(r["feasible_cases"], 83)


if __name__ == "__main__":
    unittest.main()
