import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "grand_gmi_physical_bridge_checks_v1",
    HERE / "grand_gmi_physical_bridge_checks_v1.py",
)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class GrandGMIPhysicalBridgeTests(unittest.TestCase):
    def test_binary_capacity(self):
        r = MOD.check_binary_capacity()
        self.assertEqual(r["message_counts_checked"], 64)
        self.assertEqual(r["m_1_bits"], 0)
        self.assertEqual(r["m_64_bits"], 6)
        self.assertTrue(r["all_minimal"])

    def test_microstate_partitions(self):
        r = MOD.check_microstate_partitions()
        self.assertEqual(r["physical_microstate_partition_checks"], 278)
        self.assertEqual(r["bell_counts_n_1_to_6"]["6"], 203)
        self.assertTrue(r["semantic_classes_never_exceed_physical_microstates"])

    def test_parity_separation(self):
        r = MOD.check_parity_irreversibility_separation()
        self.assertEqual(r["direct_uniform_logical_bits_discarded"], 1)
        self.assertEqual(r["reversible_embedding_logical_bits_discarded"], 0)
        self.assertTrue(r["protected_parity_output_identical"])

    def test_symbolic_landauer(self):
        r = MOD.check_symbolic_landauer_multiplicity()
        self.assertEqual(r["power_of_two_reset_cases"], 7)
        self.assertTrue(r["all_symbolic_exact"])

    def test_resource_nonidentity(self):
        r = MOD.check_resource_tradeoff_nonidentity()
        self.assertTrue(r["same_semantics_different_physical_accounting"])

    def test_aggregate(self):
        self.assertEqual(
            MOD.run()["terminal"],
            "GRAND_GMI_PHYSICAL_RESOURCE_BRIDGE_TRANCHE_ALL_GREEN",
        )


if __name__ == "__main__":
    unittest.main()
