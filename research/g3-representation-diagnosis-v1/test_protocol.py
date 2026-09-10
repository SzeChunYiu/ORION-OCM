from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import diagnose as D
import experiment as E
from diagnose import Diagnosis, classify, features_for, frozen_cases, parent_timeout_jump


class TestG34Diagnosis(unittest.TestCase):
    def test_timeout_is_not_jump(self):
        timeout = next(c for c in frozen_cases() if c["id"] == "timeout-only")
        feat = features_for(timeout)
        self.assertIsNot(classify(feat), Diagnosis.JUMP)
        self.assertIs(parent_timeout_jump(feat), Diagnosis.JUMP)
        self.assertIn(classify(feat), {Diagnosis.RESOURCE_BOUND, Diagnosis.CANNOT_CHECK, Diagnosis.SEARCH_MORE})

    def test_each_witness_matches_independent_truth(self):
        misses = []
        for case in frozen_cases():
            pred = classify(features_for(case))
            truth = Diagnosis(case["truth_reserved"])
            if pred is not truth:
                misses.append((case["id"], pred.value, truth.value, features_for(case)))
        self.assertEqual(misses, [])

    def test_parents_overclaim(self):
        cases = frozen_cases()
        self.assertGreater(
            sum(D.parent_search_more(features_for(c)) is not Diagnosis(c["truth_reserved"]) for c in cases),
            0,
        )
        self.assertGreater(
            sum(D.parent_always_representation(features_for(c)) is not Diagnosis(c["truth_reserved"]) for c in cases),
            0,
        )

    def test_experiment_confusion_is_perfect(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = E.main(Path(tmp) / "RESULT.json")
        self.assertTrue(result["jump_refused_on_timeout"])
        self.assertEqual(result["n_correct"], result["n_cases"])
        self.assertTrue(result["timeout_parent_emits_jump"])


if __name__ == "__main__":
    unittest.main()
