import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "grand_gmi_proof_reasoning_checks_v1", HERE / "grand_gmi_proof_reasoning_checks_v1.py"
)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)


class ProofReasoningGrandGMITests(unittest.TestCase):
    def test_full_receipt(self):
        r = MOD.run_all()
        self.assertEqual(r["terminal"], "GRAND_GMI_FORMAL_REASONING_PROOF_SEARCH_TRANCHE_ALL_GREEN")
        self.assertEqual(r["unique_proof_search"]["query_orders_checked"], 46233)
        self.assertEqual(r["unique_proof_search"]["candidate_sizes"][-1]["worst_negative_queries_before_forced"], 7)
        self.assertEqual(r["proof_response_quotients"]["response_tables"], 4096)
        self.assertEqual(r["semantic_quotient_dp"]["merged_states"], ["B", "C"])
        self.assertFalse(r["unsound_verifier_boundary"]["verifier_acceptance_implies_truth"])
        self.assertTrue(r["sound_incomplete_boundary"]["false_refutation_avoided"])


if __name__ == "__main__":
    unittest.main()
