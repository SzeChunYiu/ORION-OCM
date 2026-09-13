import json
import tempfile
from pathlib import Path
import shutil
import unittest
from source_evidence_v1 import HERE, verify_sources, original_replay, independent_original
from independent_oracle_v1 import census

class EvidenceTests(unittest.TestCase):
    def test_full_original_receipt_no_alarm(self):
        actual, output = original_replay()
        self.assertEqual(actual, independent_original())
        self.assertIn("C_mixed", output)
        self.assertEqual([r["total_saving_bits"] for r in actual["regimes"]], [0, 3, 3])

    def test_actual_retained_intermediate_row_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "unit"
            shutil.copytree(HERE, root)
            p = root / "raw/upstream/STAGE_CONSOLIDATION_WITNESS_V1.json"
            data = json.loads(p.read_text())
            data["regimes"][1]["rows"][2]["N_t"] = 8
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "source mismatch"):
                verify_sources(root)

    def test_complete_pair_graph_oracle_matches_refinement(self):
        r = census()
        self.assertEqual(r["machines"], 2752)
        self.assertEqual(r["ordered_state_pairs"], 19648)
        self.assertEqual(r["equivalent_pairs"] + r["distinguishable_pairs"], 19648)

if __name__ == "__main__":
    unittest.main()
