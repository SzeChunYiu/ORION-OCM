"""Recorded experiment: REFACTOR residual without claiming search invocation."""
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent


class RecordedRun(unittest.TestCase):
    def test_summary_is_refactor_residual_not_search_success(self):
        summary = json.loads((HERE / "SUMMARY.json").read_text())
        self.assertEqual(summary["terminal"], "GETSTEPS_ZERO_LABEL_SPINE_ONLY")
        self.assertEqual(summary["g2_4"], "NOT_YET")
        self.assertFalse(summary["causal_method_reuse_supported"])
        self.assertFalse(summary["github_g2_4_checked"])
        self.assertEqual(summary["n_refactored_proofs_proper_native"], 1)
        self.assertEqual(summary["search_invocations"], 48)
        self.assertEqual(summary["lemma_used_in_search"], [])
        self.assertTrue(summary["lemma_actions_nonzero"])
        self.assertEqual(summary["save_value"]["save_value"], 0)
        self.assertTrue(summary["one_step_identity_excluded"])

    def test_proper_hit_is_inundif_not_acquisition(self):
        payload = json.loads((HERE / "records" / "replay-01" / "RESULT.json").read_text())
        proper = [t for t in payload["refactor"]["theorems"] if t.get("n_proper_spine", 0) > 0]
        self.assertEqual([t["label"] for t in proper], ["inundif"])
        self.assertNotIn("inundif", {
            "inss", "elsymdif", "indif1", "dif32", "sscon34b",
        })


if __name__ == "__main__":
    unittest.main()
