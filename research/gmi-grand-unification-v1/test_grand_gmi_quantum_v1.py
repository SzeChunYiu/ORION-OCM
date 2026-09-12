import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "grand_gmi_quantum_checks_v1",
    HERE / "grand_gmi_quantum_checks_v1.py",
)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class GrandGMIQuantumTests(unittest.TestCase):
    def test_probe_refinement(self):
        r = MOD.check_probe_refinement()
        self.assertTrue(r["z_only_equivalent"])
        self.assertTrue(r["z_plus_x_refines"])

    def test_cut_capacity(self):
        r = MOD.check_quantum_cut_capacities()
        self.assertEqual(r["message_thresholds_checked"], 256)
        self.assertEqual(r["m_256_bare_qubits"], 8)
        self.assertEqual(r["m_256_dense_coding_transmitted_qubits"], 4)
        self.assertTrue(r["free_entanglement_changes_cut_capacity"])

    def test_no_cloning(self):
        r = MOD.check_no_cloning_witness()
        self.assertEqual(r["input_fidelity"], "1/2")
        self.assertEqual(r["perfect_two_copy_fidelity"], "1/4")
        self.assertFalse(r["universal_perfect_cloner_possible"])

    def test_classical_sector(self):
        r = MOD.check_classical_diagonal_sector()
        self.assertEqual(r["rational_distributions_checked"], 5)
        self.assertTrue(r["all_exact"])

    def test_effect_span(self):
        r = MOD.check_effect_span_refinement()
        self.assertEqual(r["effect_span_ranks_Z_ZX_ZXY"], [2, 3, 4])
        self.assertEqual(r["tomographic_full_qubit_rank"], 4)

    def test_aggregate(self):
        self.assertEqual(
            MOD.run()["terminal"],
            "GRAND_GMI_QUANTUM_PROCESS_INSTANTIATION_TRANCHE_ALL_GREEN",
        )


if __name__ == "__main__":
    unittest.main()
