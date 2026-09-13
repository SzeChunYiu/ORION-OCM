import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "grand_gmi_end_to_end_checks_v1",
    HERE / "grand_gmi_end_to_end_checks_v1.py",
)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class GrandGMIEndToEndTests(unittest.TestCase):
    def test_selector_neural(self):
        r = MOD.selector_trace()
        self.assertEqual(r["semantic_states"], 4)
        self.assertEqual(r["fixed_route_best_correct_of_8"], [6, 6])
        self.assertEqual(r["dynamic_route_best_correct_of_8"], 8)
        self.assertEqual(r["pareto_frontier"], ["N_route"])
        self.assertEqual(r["derived_family"], "neural")

    def test_parity_non_neural(self):
        r = MOD.parity_controller_trace()
        self.assertEqual(r["semantic_states"], 2)
        self.assertEqual(r["xor_transition_cells_checked"], 4)
        self.assertEqual(r["pareto_frontier"], ["P_fsm"])
        self.assertEqual(r["derived_family"], "non-neural-program")

    def test_hybrid(self):
        r = MOD.hybrid_trace()
        self.assertEqual(r["pareto_frontier"], ["neural+program"])
        self.assertEqual(r["derived_family"], "hybrid-neural-program")

    def test_substrate_inversion(self):
        r = MOD.substrate_inversion_trace()
        self.assertEqual(r["substrate_A_frontier"], ["neural"])
        self.assertEqual(r["substrate_B_frontier"], ["program"])
        self.assertFalse(r["protected_semantics_changed"])
        self.assertTrue(r["family_inversion"])

    def test_aggregate(self):
        self.assertEqual(
            MOD.run()["terminal"],
            "GRAND_GMI_END_TO_END_DERIVATION_TRACES_ALL_GREEN",
        )


if __name__ == "__main__":
    unittest.main()
