import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "grand_gmi_strategic_checks_v1", HERE / "grand_gmi_strategic_checks_v1.py"
)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)


class StrategicGrandGMITests(unittest.TestCase):
    def test_full_receipt(self):
        r = MOD.run_all()
        self.assertEqual(r["terminal"], "GRAND_GMI_STRATEGIC_MULTIAGENT_TRANCHE_ALL_GREEN")
        self.assertEqual(r["local_obligation_equilibrium"]["games"], 6561)
        self.assertEqual(r["local_obligation_equilibrium"]["games_without_pure_equilibrium"], 162)
        self.assertEqual(r["strategic_semantic_refinement"]["refinement_checks"], 196608)
        self.assertEqual(r["ecology_robust_nonexistence"]["intersection"], [])
        self.assertEqual(r["semantic_signaling_cut"]["minimum_message_symbols"], 2)


if __name__ == "__main__":
    unittest.main()
