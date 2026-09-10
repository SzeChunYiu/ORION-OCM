from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import experiment as E


class TestL1LinguisticG2(unittest.TestCase):
    def test_fresh_pairs_are_not_training_pairs(self):
        train = {(a, n) for a in E.TRAIN_ADJ for n in E.TRAIN_NOUN}
        fresh = [(a, n) for a in E.HELD_ADJ for n in E.HELD_NOUN]
        self.assertTrue(all(p not in train for p in fresh))

    def test_revocation_and_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = E.main(Path(tmp) / "RESULT.json")
        self.assertTrue(result["fresh_invoked"])
        self.assertTrue(result["restart_equivalent"])
        self.assertTrue(result["revocation_removes_effect"])
        self.assertTrue(result["reset_has_no_construction"])
        self.assertTrue(result["held_out_combination"])
        self.assertFalse(result["grammar_induction_parent_has_fresh_identity"])
        self.assertEqual(result["checklist"]["g2_causal_reuse_linguistic"], "EARNED_AT_SCOPE")
        self.assertEqual(result["checklist"]["open_weight_lm_reference"], "CANNOT_CHECK_NO_MODEL_WEIGHTS")
        self.assertTrue(result["numeral_dropped_in_combo"])
        self.assertEqual(
            result["checklist"]["recursive_composition"],
            "EARNED_ADJ_NOUN_SUFFIX_NUMERAL_DROPPED",
        )
        self.assertIn("tokens[-2:]", (Path(__file__).resolve().parent / "experiment.py").read_text())

    def test_answer_cache_excluded_by_new_surface_strings(self):
        self.assertNotIn("green", E.TRAIN_ADJ)
        self.assertNotIn("pyramid", E.TRAIN_NOUN)


if __name__ == "__main__":
    unittest.main()
