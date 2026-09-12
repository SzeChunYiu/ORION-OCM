import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
MODULE_PATH = HERE / "grand_gmi_proof_search_checks_v1.py"
spec = importlib.util.spec_from_file_location("grand_gmi_proof_search_checks_v1", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestGrandGMIProofSearchV1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = mod.run()

    def test_aggregate_green(self):
        self.assertTrue(self.result["all_checks_green"])
        self.assertEqual(
            self.result["terminal"],
            "GRAND_GMI_PROOF_SEARCH_REUSE_TRANCHE_ALL_GREEN",
        )

    def test_binary_verifier_formulas(self):
        v = self.result["verifier"]
        self.assertEqual(v["truth_cases"], 16)
        self.assertEqual(v["truth_exact"], 16)
        self.assertEqual(v["identification_cases"], 16)
        self.assertEqual(v["identification_exact"], 16)

    def test_reuse_phase_grid(self):
        r = self.result["reuse_phase"]
        self.assertEqual(r["cells"], 7776)
        self.assertEqual(r["inequality_matches"], 7776)
        self.assertEqual(r["beneficial"], 3050)
        self.assertEqual(r["ties"], 284)
        self.assertEqual(r["worse"], 4442)

    def test_reuse_not_universally_better(self):
        r = self.result["reuse_phase"]
        self.assertGreater(r["beneficial"], 0)
        self.assertGreater(r["worse"], 0)
        self.assertGreater(r["ties"], 0)


if __name__ == "__main__":
    unittest.main()
