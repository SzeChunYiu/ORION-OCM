from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import experiment as E


V1_RESULT = Path(__file__).resolve().parents[1] / "l1-linguistic-g2-v1" / "RESULT.json"
V2_RESULT = Path(__file__).resolve().parents[1] / "l1-linguistic-g2-v2" / "RESULT.json"


class TestL1LinguisticG2V3(unittest.TestCase):
    def test_new_salts_exclude_v1_and_v2_content(self):
        content = E.all_surfaces() - {E.NEG_PARTICLE}
        self.assertTrue(content.isdisjoint(E.V1_SURFACES))
        self.assertTrue(content.isdisjoint(E.V2_CONTENT_SURFACES))
        self.assertNotEqual(E.TRAIN_SALT, E.HELD_SALT)
        self.assertIn("v3", E.TRAIN_SALT)
        self.assertIn("sov", E.TRAIN_SALT)
        self.assertNotIn("v2", E.TRAIN_SALT)
        self.assertNotIn("green", E.TRAIN_ANIMATE + E.HELD_ANIMATE)
        self.assertNotIn("lynx", E.TRAIN_ANIMATE + E.HELD_ANIMATE)
        self.assertNotIn("goblet", E.TRAIN_ARTIFACT + E.HELD_ARTIFACT)

    def test_held_fillers_and_orders_are_disjoint_from_train(self):
        train = set(E.TRAIN_ANIMATE + E.TRAIN_ARTIFACT + E.TRAIN_VERB)
        held = set(E.HELD_ANIMATE + E.HELD_ARTIFACT + E.HELD_VERB)
        self.assertTrue(held.isdisjoint(train))
        train_pool = set(E.train_svo_utterances()) | set(E.train_sov_utterances()) | set(E.train_neg_utterances())
        for key, u in E.held_probes().items():
            if u in train_pool:
                self.fail(f"held probe leaked into train ({key}): {u}")
        self.assertNotEqual(E.held_probes()["svo"], E.held_probes()["sov"])
        self.assertEqual(set(E.tokenize(E.held_probes()["svo"])), set(E.tokenize(E.held_probes()["sov"])))

    def test_protocol_sov_hostile_and_honest_family_miss(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = E.main(Path(tmp) / "RESULT.json")
        self.assertEqual(result["schema"], "ocm.l1.linguistic-g2.v3")
        self.assertEqual(result["terminal"], "COMPOSITIONAL_LANGUAGE_LEARNING_ONLY")
        self.assertEqual(result["svo_hypothesis"], "SVO")
        self.assertEqual(result["sov_hypothesis"], "SOV")
        self.assertTrue(result["fresh_invoked"])
        self.assertTrue(result["english_rejects_sov"])
        self.assertTrue(result["sov_rejects_svo"])
        self.assertTrue(result["sov_meaning_intact"])
        self.assertTrue(result["forced_word_order_hostile"])
        self.assertTrue(result["scope_blocks_silent_relabel"])
        self.assertTrue(result["word_order_transfer_refused"])
        self.assertTrue(result["meaning_structure_transfer_allowed"])
        self.assertFalse(result["family_transfer_succeeded"])
        self.assertTrue(result["family_transfer_failure_is_mechanism"])
        self.assertEqual(result["trained_family"], "transitive")
        self.assertEqual(result["held_out_family"], "negation")
        self.assertTrue(result["negation_acquirable_from_own_family"])
        self.assertTrue(result["restart_equivalent"])
        self.assertTrue(result["revocation_removes_effect"])
        self.assertTrue(result["unrelated_survives_revocation"])
        self.assertTrue(result["alternate_support_restores"])
        self.assertTrue(result["reset_has_no_construction"])
        self.assertFalse(result["grammar_induction_parent_has_fresh_identity"])
        self.assertTrue(result["type_mismatch_rejected"])
        self.assertFalse(result["l2_started"])
        self.assertFalse(result["l3_started"])
        self.assertLessEqual(result["max_nodes"], result["canonical_bound"])
        cl = result["checklist"]
        self.assertEqual(cl["artificial_non_english"], "EARNED_AT_SCOPE")
        self.assertEqual(cl["held_out_construction_families"], "NO_CROSS_FAMILY_TRANSFER")
        self.assertEqual(cl["induce_constructions"], "EARNED_AT_SCOPE")
        self.assertEqual(cl["held_out_lexical_fillers"], "EARNED_AT_SCOPE")
        self.assertEqual(cl["correction_revocation"], "EARNED_AT_SCOPE")
        self.assertEqual(cl["g2_causal_reuse_linguistic"], "EARNED_AT_SCOPE")
        self.assertEqual(cl["negation"], "EARNED_AT_SCOPE")
        self.assertEqual(cl["open_weight_lm_reference"], "CANNOT_CHECK_NO_MODEL_WEIGHTS")
        self.assertEqual(cl["acquire_corpus_scale_lexicon"], "CANNOT_CHECK_MINIATURE_MICROWORLD")
        self.assertEqual(cl["ud_alignment"], "CANNOT_CHECK_NO_UD_IN_THIS_STUDY")
        self.assertTrue(cl["ud_alignment"].startswith("CANNOT_CHECK"))
        self.assertEqual(cl["meaning_graphs_beyond_bound"], "CANNOT_CHECK_MICROWORLD_SMALL")
        self.assertEqual(cl["acquisition_curves"], "CANNOT_CHECK_N_TOO_SMALL")
        self.assertEqual(cl["continual_adaptation_parent"], "CANNOT_CHECK_NOT_RUN")
        self.assertNotIn("EARNED", cl["acquire_corpus_scale_lexicon"])
        self.assertNotIn("EARNED", cl["ud_alignment"])
        held = result["held_rows"]
        self.assertEqual(held["svo_on_sov"]["verdict"], "UNKNOWN_CONSTRUCTION")
        self.assertEqual(held["family_transfer_negation"]["verdict"], "UNKNOWN_CONSTRUCTION")
        self.assertEqual(held["sov_on_sov"]["roles"]["agent"], "jackal")
        self.assertEqual(held["sov_on_sov"]["roles"]["patient"], "reliquary")
        self.assertEqual(held["svo_on_svo"]["roles"]["agent"], "jackal")
        self.assertEqual(held["svo_on_svo"]["roles"]["patient"], "reliquary")
        self.assertIn("NEGATES", held["negation_own_family"]["relations"])

    def test_v1_and_v2_results_not_overwritten(self):
        v1 = json.loads(V1_RESULT.read_text())
        v2 = json.loads(V2_RESULT.read_text())
        self.assertEqual(v1["schema"], "ocm.l1.linguistic-g2.v1")
        self.assertEqual(v1["terminal"], "COMPOSITIONAL_LANGUAGE_LEARNING_ONLY")
        self.assertEqual(v1["checklist"]["artificial_non_english"], "CANNOT_CHECK_NOT_RUN_SOV_HERE")
        self.assertEqual(v1["checklist"]["held_out_construction_families"], "CANNOT_CHECK_ONE_FAMILY")
        self.assertEqual(v2["schema"], "ocm.l1.linguistic-g2.v2")
        self.assertEqual(v2["terminal"], "COMPOSITIONAL_LANGUAGE_LEARNING_ONLY")
        self.assertEqual(v2["checklist"]["artificial_non_english"], "CANNOT_CHECK_NOT_RUN_SOV_HERE")
        self.assertEqual(v2["checklist"]["held_out_construction_families"], "CANNOT_CHECK_FAMILIES_TAUGHT_EXPLICITLY")


if __name__ == "__main__":
    unittest.main()
