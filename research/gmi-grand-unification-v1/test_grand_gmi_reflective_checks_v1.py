import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "grand_gmi_reflective_checks_v1", HERE / "grand_gmi_reflective_checks_v1.py"
)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)


class ReflectiveGrandGMITests(unittest.TestCase):
    def test_full_receipt(self):
        r = MOD.run_all()
        self.assertEqual(r["terminal"], "GRAND_GMI_REFLECTIVE_SELF_REFERENCE_TRANCHE_ALL_GREEN")
        self.assertEqual(r["reflective_semantic_refinement"]["response_tables"], 4096)
        self.assertEqual(r["reflective_semantic_refinement"]["refinement_checks"], 8192)
        self.assertEqual(r["diagonal_impossibility"]["diagonal_failures"], 2048)
        self.assertEqual(r["diagonal_impossibility"]["diagonal_exact_successes"], 0)
        self.assertEqual(r["nonreactive_self_prediction"]["exact_context_predictions"], 2048)
        self.assertEqual(r["self_modification_reachability"]["budget_checks"][-1]["reachable"], [0, 1, 2, 3])


if __name__ == "__main__":
    unittest.main()
