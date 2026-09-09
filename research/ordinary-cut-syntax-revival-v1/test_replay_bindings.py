"""Bind the completed revival replay without rerunning matching."""
import json
import unittest
from pathlib import Path

REVIVAL = Path(__file__).resolve().parent
RESULT = json.loads((REVIVAL / "records" / "replay-02" / "RESULT.json").read_text())


class ReplayBindings(unittest.TestCase):
    def test_terminal_and_populations(self):
        self.assertEqual(RESULT["terminal"], "SYNTAX_ADMISSION_REPAIRED_MATCHING_REACHED")
        self.assertEqual(RESULT["proposal_occurrences"], 76)
        self.assertEqual(RESULT["admitted"], 76)
        self.assertEqual(RESULT["still_unknown"], 0)
        self.assertEqual(RESULT["aliases_found"], 44)
        self.assertEqual(RESULT["screened_negative"], 32)
        self.assertEqual(RESULT["native_calls"], 0)
        self.assertEqual(RESULT["causal_method_reuse_supported"], False)
        self.assertEqual(RESULT["g2_4_causal_use_box"], "NOT_YET")
        self.assertEqual(RESULT["g2_3_primitive_alias_box"], "MIXED_ALIAS_AND_NEGATIVE")
        self.assertEqual(RESULT["frozen_root_status_counts"],
                         {"ENUMERATED": 17, "TRACE_UNUSABLE": 57, "UNKNOWN_INTERFACE": 54})
        self.assertEqual(len(RESULT["screens"]), 76)
        self.assertTrue(all(row["ground_admitted"] and row["coverage_complete"] for row in RESULT["screens"]))
        self.assertEqual(RESULT["work"]["P1_assertions_visited"], 76 * 4323)
        self.assertLessEqual(RESULT["work"]["token_states"], 2000000)
        self.assertFalse(RESULT["token_bound_reached"])


if __name__ == "__main__":
    unittest.main()
