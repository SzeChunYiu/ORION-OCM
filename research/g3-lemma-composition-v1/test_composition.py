"""G3 composition records. Native mmverify is exercised by compose.py; tests lock the inventory."""
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "g2-causal-lemma-reuse-v1"))
sys.path.insert(0, str(HERE))
import compose as C  # noqa: E402
import extract as E  # noqa: E402


class PairTests(unittest.TestCase):
    def test_pair_is_the_known_zero_premise_cuts(self):
        inner, outer = C.pair_lemmas()
        self.assertEqual(inner["source_label"], "ssdifim")
        self.assertEqual(outer["source_label"], "ssdifsym")
        self.assertFalse(inner["hypotheses"])
        self.assertFalse(outer["hypotheses"])
        self.assertIn("ssdifim", outer["proof"])
        self.assertNotIn("ssdifim", inner["proof"])
        self.assertEqual(inner["ordinal"] + 1, outer["ordinal"])

    def test_composed_proof_cites_inner_cut_not_named_ssdifim(self):
        self.assertIn(C.INNER_LABEL, C.COMPOSED_PROOF)
        self.assertNotIn("ssdifim", C.COMPOSED_PROOF)
        self.assertNotIn(C.INNER_LABEL, C.INLINED_PROOF)
        self.assertGreater(len(C.INLINED_PROOF), len(C.COMPOSED_PROOF))

    def test_unique_negatives_still_hold_both(self):
        rows = E.unique_negatives()
        labels = [r["source_label"] for r in rows if not r["hypotheses"]]
        self.assertIn("ssdifim", labels)
        self.assertIn("ssdifsym", labels)


class RecordTests(unittest.TestCase):
    def test_run_record_refuses_g3_1_and_g2_4(self):
        result = json.loads((HERE / "records" / "run-01" / "RESULT.json").read_text())
        summary = json.loads((HERE / "SUMMARY.json").read_text())
        self.assertEqual(
            result["terminal"],
            "TRAINING_PAIR_CUT_COMPOSITION_VERIFIED__NO_FRESH_COMPOSITION",
        )
        self.assertFalse(result["g3_1_can_check"])
        self.assertEqual(result["g3_1"], "CANNOT_CHECK")
        self.assertEqual(result["g2_4"], "NOT_YET")
        self.assertFalse(result["causal_method_reuse_supported"])
        self.assertFalse(result["method_composition_supported"])
        self.assertEqual(result["fresh_terminal"], "NO_FRESH_COMPOSITION")
        self.assertEqual(result["composed"]["terminal"], "NATIVE_VERIFIED")
        self.assertTrue(result["ablation"]["remove_inner_cut"]["breaks"])
        self.assertTrue(result["ablation"]["inline_inner_body"]["lengthens"])
        self.assertFalse(result["same_family"]["disjoint_families"])
        self.assertFalse(result["invocation"]["inner_statement_equals_named_ssdifim"])
        self.assertFalse(result["invocation"]["outer_statement_equals_named_ssdifsym"])
        self.assertEqual(summary["g3_1"], "CANNOT_CHECK")
        self.assertEqual(summary["g2_4"], "NOT_YET")
        self.assertGreaterEqual(result["native_calls"], 6)


if __name__ == "__main__":
    unittest.main()
