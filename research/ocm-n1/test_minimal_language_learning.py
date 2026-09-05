from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE))

from ocm.kso.warrant import Liveness  # noqa: E402
from ocm.language.interpret import Verdict, interpret  # noqa: E402

from minimal_language_learning import (  # noqa: E402
    empty_language,
    held_out_check,
    learn_language,
    run,
    transitive_meaning,
)


class MinimalLanguageLearningTests(unittest.TestCase):
    def test_time_zero_inventory_is_empty(self):
        state = empty_language("x")
        self.assertEqual(state.language_specific_objects, 0)
        self.assertEqual(len(state.information_events), 0)

    def test_same_learner_acquires_svo_and_conflicting_sov(self):
        svo, svo_c = learn_language("a", "SVO")
        sov, sov_c = learn_language("b", "SOV")
        expected = transitive_meaning("girl", "push", "ball")
        self.assertTrue(held_out_check(svo, "girl push ball", expected))
        self.assertTrue(held_out_check(sov, "girl ball push", expected))
        self.assertEqual([slot.name for slot in svo_c.pattern], ["subj", "verb", "obj"])
        self.assertEqual([slot.name for slot in sov_c.pattern], ["subj", "obj", "verb"])

    def test_wrong_order_is_not_accepted_by_learned_inventory(self):
        svo, _ = learn_language("a", "SVO")
        sov, _ = learn_language("b", "SOV")
        self.assertEqual(interpret("girl ball push", svo.lexicon, svo.constructions).verdict, Verdict.UNKNOWN_CONSTRUCTION)
        self.assertEqual(interpret("girl push ball", sov.lexicon, sov.constructions).verdict, Verdict.UNKNOWN_CONSTRUCTION)

    def test_learned_construction_depends_on_its_demonstration(self):
        svo, c = learn_language("a", "SVO")
        self.assertIs(c.liveness(()), Liveness.LIVE)
        self.assertIs(c.liveness({"demo:a:transitive-order"}), Liveness.DEAD)

    def test_registered_receipt_is_calibration_only(self):
        result = run()
        self.assertEqual(result["time_zero_language_specific_objects"], 0)
        self.assertFalse(result["protected_claim_authority"])
        self.assertEqual(result["svo"]["learned_hypothesis"], "SVO")
        self.assertEqual(result["sov"]["learned_hypothesis"], "SOV")
        self.assertTrue(result["svo"]["held_out_composition"])
        self.assertTrue(result["sov"]["held_out_composition"])
        self.assertTrue(result["construction_warrant_revocable"])
        self.assertEqual(result["terminal"], "MINIMAL_EMPTY_LANGUAGE_INVENTORY_LEARNS_SVO_AND_SOV_CALIBRATION")


if __name__ == "__main__":
    unittest.main()
