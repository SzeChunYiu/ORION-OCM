import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
MODULE_PATH = HERE / "grand_gmi_epistemic_checks_v1.py"
spec = importlib.util.spec_from_file_location("grand_gmi_epistemic_checks_v1", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestGrandGMIEpistemicAcquisitionV1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = mod.enumerate_checks()

    def test_aggregate_green(self):
        self.assertTrue(self.result["all_checks_green"])
        self.assertEqual(
            self.result["terminal"],
            "GRAND_GMI_EPISTEMIC_ACQUISITION_TRANCHE_ALL_GREEN",
        )

    def test_exhaustive_counts(self):
        self.assertEqual(self.result["observed"], self.result["expected"])
        self.assertEqual(self.result["observed"]["matrix_count"], 4096)
        self.assertEqual(self.result["observed"]["semantic_instances"], 65536)
        self.assertEqual(self.result["observed"]["strict_adaptive_advantage"], 576)
        self.assertEqual(self.result["observed"]["semantic_cheaper_than_full_world"], 27472)

    def test_canonical_obligation_witness(self):
        w = self.result["canonical_obligation_witness"]
        self.assertEqual(w["semantic_adaptive_depth"], 1)
        self.assertEqual(w["full_world_adaptive_depth"], 2)
        self.assertEqual(w["full_world_fixed_panel_size"], 3)

    def test_unidentifiable_semantics_are_detected(self):
        matrix = ((0, 0, 0), (0, 0, 0), (1, 0, 0), (1, 0, 0))
        labels = (0, 1, 0, 0)
        self.assertIsNone(mod.semantic_adaptive_depth(matrix, labels))

    def test_semantic_sufficiency_can_be_strict(self):
        matrix = ((0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 0, 1))
        semantic = (0, 0, 1, 1)
        full = mod._row_labels(matrix)
        self.assertEqual(mod.semantic_adaptive_depth(matrix, semantic), 1)
        self.assertEqual(mod.semantic_adaptive_depth(matrix, full), 2)
        self.assertEqual(mod.semantic_nonadaptive_size(matrix, full), 3)


if __name__ == "__main__":
    unittest.main()
