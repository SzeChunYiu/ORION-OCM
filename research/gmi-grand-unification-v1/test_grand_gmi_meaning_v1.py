import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "grand_gmi_meaning_checks_v1",
    HERE / "grand_gmi_meaning_checks_v1.py",
)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class GrandGMIMeaningTests(unittest.TestCase):
    def test_semantic_nullity(self):
        r = MOD.check_semantic_nullity()
        self.assertEqual(r["base_response_tables"], 16)
        self.assertEqual(r["z_equivalence_checks"], 32)
        self.assertTrue(r["all_z_variants_response_equivalent"])

    def test_data_processing(self):
        r = MOD.check_semantic_information_data_processing()
        self.assertEqual(r["binary_support_channels"], 9)
        self.assertEqual(r["deterministic_garbling_checks"], 36)
        self.assertTrue(r["garbling_never_improves_zero_error_semantic_information"])

    def test_viability_signal(self):
        r = MOD.check_viability_signal()
        self.assertEqual(r["perfect_signal_robust_policies"], 1)
        self.assertEqual(r["erased_signal_robust_policies"], 0)
        self.assertEqual(r["zero_error_semantic_bits_gained"], 1)

    def test_obligation_nonidentifiability(self):
        r = MOD.check_obligation_nonidentifiability()
        self.assertEqual(r["constitution_V0_optimal_action"], 0)
        self.assertEqual(r["constitution_V1_optimal_action"], 1)
        self.assertFalse(r["physics_alone_selects_unique_nontrivial_obligation"])

    def test_aggregate(self):
        self.assertEqual(
            MOD.run()["terminal"],
            "GRAND_GMI_CAUSAL_SEMANTIC_VIABILITY_TRANCHE_ALL_GREEN",
        )


if __name__ == "__main__":
    unittest.main()
