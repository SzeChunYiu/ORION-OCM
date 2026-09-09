from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import experiment as E


V1_RESULT = Path(__file__).resolve().parents[1] / "l1-linguistic-g2-v1" / "RESULT.json"


class TestL1LinguisticG2V2(unittest.TestCase):
    def test_new_salts_exclude_v1_surfaces(self):
        self.assertTrue(E.all_surfaces().isdisjoint(E.V1_SURFACES))
        self.assertNotEqual(E.TRAIN_SALT, E.HELD_SALT)
        self.assertIn("v2", E.TRAIN_SALT)
        self.assertNotIn("green", E.TRAIN_ANIMATE + E.HELD_ANIMATE)
        self.assertNotIn("pyramid", E.TRAIN_ARTIFACT + E.HELD_ARTIFACT)

    def test_held_fillers_are_not_training_fillers(self):
        train = set(E.TRAIN_ANIMATE + E.TRAIN_ARTIFACT + E.TRAIN_VERB)
        held = set(E.HELD_ANIMATE + E.HELD_ARTIFACT + E.HELD_VERB)
        self.assertTrue(held.isdisjoint(train))
        train_utts = {u for utts in E.train_utterances().values() for u in utts}
        for u in E.held_probes().values():
            if u in train_utts:
                self.fail(f"held probe leaked into train: {u}")

    def test_same_multiset_scope_pair_differs_in_order(self):
        probes = E.held_probes()
        self.assertEqual(set(E.tokenize(probes["not_every"])), set(E.tokenize(probes["every_not"])))
        self.assertNotEqual(probes["not_every"], probes["every_not"])

    def test_protocol_and_new_boxes(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = E.main(Path(tmp) / "RESULT.json")
        self.assertEqual(result["schema"], "ocm.l1.linguistic-g2.v2")
        self.assertEqual(result["terminal"], "COMPOSITIONAL_LANGUAGE_LEARNING_ONLY")
        self.assertTrue(result["fresh_invoked"])
        self.assertTrue(result["restart_equivalent"])
        self.assertTrue(result["revocation_removes_effect"])
        self.assertTrue(result["unrelated_survives_revocation"])
        self.assertTrue(result["alternate_support_restores"])
        self.assertTrue(result["reset_has_no_construction"])
        self.assertTrue(result["held_out_combination"])
        self.assertFalse(result["grammar_induction_parent_has_fresh_identity"])
        self.assertTrue(result["type_mismatch_rejected"])
        self.assertTrue(result["polysemy_ambiguous_until_evidence"])
        self.assertTrue(result["negation_distinct_from_affirmative"])
        self.assertTrue(result["scope_readings_distinct"])
        self.assertFalse(result["l2_started"])
        self.assertFalse(result["l3_started"])
        self.assertLessEqual(result["max_nodes"], result["canonical_bound"])
        cl = result["checklist"]
        self.assertEqual(cl["negation"], "EARNED_AT_SCOPE")
        self.assertEqual(cl["quantifier_scope"], "EARNED_AT_SCOPE")
        self.assertEqual(cl["typed_entities"], "EARNED_AT_SCOPE")
        self.assertEqual(cl["retain_polysemy"], "EARNED_AT_SCOPE")
        self.assertEqual(cl["correction_revocation"], "EARNED_AT_SCOPE")
        self.assertEqual(cl["g2_causal_reuse_linguistic"], "EARNED_AT_SCOPE")
        self.assertEqual(cl["open_weight_lm_reference"], "CANNOT_CHECK_NO_MODEL_WEIGHTS")
        self.assertEqual(cl["acquire_corpus_scale_lexicon"], "CANNOT_CHECK_MINIATURE_MICROWORLD")
        self.assertEqual(cl["ud_alignment"], "CANNOT_CHECK_NO_UD_IN_THIS_STUDY")
        self.assertTrue(cl["ud_alignment"].startswith("CANNOT_CHECK"))
        self.assertEqual(cl["meaning_graphs_beyond_bound"], "CANNOT_CHECK_MICROWORLD_SMALL")
        self.assertEqual(cl["held_out_construction_families"], "CANNOT_CHECK_FAMILIES_TAUGHT_EXPLICITLY")
        self.assertEqual(cl["continual_adaptation_parent"], "CANNOT_CHECK_NOT_RUN")
        self.assertEqual(cl["artificial_non_english"], "CANNOT_CHECK_NOT_RUN_SOV_HERE")
        self.assertEqual(cl["acquisition_curves"], "CANNOT_CHECK_N_TOO_SMALL")

    def test_v1_result_not_overwritten(self):
        data = json.loads(V1_RESULT.read_text())
        self.assertEqual(data["schema"], "ocm.l1.linguistic-g2.v1")
        self.assertEqual(data["terminal"], "COMPOSITIONAL_LANGUAGE_LEARNING_ONLY")
        self.assertEqual(data["checklist"]["negation"], "CANNOT_CHECK_NOT_IN_MICROWORLD")
        self.assertEqual(data["checklist"]["retain_polysemy"], "OPEN")


if __name__ == "__main__":
    unittest.main()
