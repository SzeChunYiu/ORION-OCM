import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "grand_gmi_compositional_checks_v1",
    HERE / "grand_gmi_compositional_checks_v1.py",
)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class GrandGMICompositionalTests(unittest.TestCase):
    def test_frontier_tensorization(self):
        r = MOD.check_frontier_tensorization()
        self.assertEqual(r["set_pair_checks"], 225)
        self.assertTrue(r["all_exact"])

    def test_semantic_width_tensorization(self):
        r = MOD.check_semantic_width_tensorization()
        self.assertEqual(r["ternary_function_pairs"], 729)
        self.assertTrue(r["all_exact"])

    def test_xor_cut(self):
        r = MOD.check_xor_distributed_cut()
        self.assertEqual(r["minimum_message_symbols"], 2)
        self.assertEqual(r["by_alphabet"]["1"]["successful"], 0)
        self.assertEqual(r["by_alphabet"]["2"]["successful"], 2)

    def test_coupled_boundary(self):
        r = MOD.check_coupled_obligation_boundary()
        self.assertEqual(r["separate_pair_message_symbols"], 4)
        self.assertEqual(r["coupled_parity_message_symbols"], 2)
        self.assertFalse(r["tensorization_without_factorized_obligation"])

    def test_team_centralization(self):
        r = MOD.check_team_centralization()
        self.assertEqual(r["trace_checks"], 508)
        self.assertTrue(r["all_exact"])

    def test_aggregate(self):
        self.assertEqual(
            MOD.run()["terminal"],
            "GRAND_GMI_COMPOSITIONAL_DISTRIBUTED_TRANCHE_ALL_GREEN",
        )


if __name__ == "__main__":
    unittest.main()
