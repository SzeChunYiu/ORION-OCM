from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import experiment as E


V1_RESULT = Path(__file__).resolve().parents[1] / "l1-linguistic-g2-v1" / "RESULT.json"
V2_RESULT = Path(__file__).resolve().parents[1] / "l1-linguistic-g2-v2" / "RESULT.json"
V3_RESULT = Path(__file__).resolve().parents[1] / "l1-linguistic-g2-v3" / "RESULT.json"


class TestL1LinguisticG2V4(unittest.TestCase):
    def test_new_salts_exclude_v1_v2_v3_content(self):
        content = E.all_surfaces()
        self.assertTrue(content.isdisjoint(E.V1_SURFACES))
        self.assertTrue(content.isdisjoint(E.V2_CONTENT_SURFACES))
        self.assertTrue(content.isdisjoint(E.V3_CONTENT_SURFACES))
        self.assertNotEqual(E.TRAIN_SALT, E.HELD_SALT)
        self.assertIn("v4", E.TRAIN_SALT)
        self.assertIn("morph", E.TRAIN_SALT)
        self.assertNotIn("v2", E.TRAIN_SALT)
        self.assertNotIn("v3", E.TRAIN_SALT)
        self.assertNotIn("green", E.TRAIN_ANIMATE + E.HELD_ANIMATE)
        self.assertNotIn("lynx", E.TRAIN_ANIMATE + E.HELD_ANIMATE)
        self.assertNotIn("jackal", E.TRAIN_ANIMATE + E.HELD_ANIMATE)
        self.assertNotIn("goblet", E.TRAIN_ARTIFACT + E.HELD_ARTIFACT)
        self.assertNotIn("reliquary", E.TRAIN_ARTIFACT + E.HELD_ARTIFACT)

    def test_held_fillers_disjoint_from_train(self):
        train = set(E.TRAIN_ANIMATE + E.TRAIN_ARTIFACT + E.TRAIN_VERB)
        held = set(E.HELD_ANIMATE + E.HELD_ARTIFACT + E.HELD_VERB)
        self.assertTrue(held.isdisjoint(train))
        self.assertNotIn("entomb", dict(E.REGULAR_PAST))
        self.assertIn("entomb", dict(E.HELD_REGULAR_PAST))

    def test_planted_treebank_is_tiny_not_corpus(self):
        train = list(E.UD.read_conllu(E.HERE / "train.conllu"))
        held = list(E.UD.read_conllu(E.HERE / "held.conllu"))
        self.assertEqual(len(train), 3)
        self.assertEqual(len(held), 3)
        self.assertTrue(all(E.UD.is_simple_clause(s) for s in train))
        self.assertEqual(sum(1 for s in held if E.UD.is_simple_clause(s)), 2)
        self.assertEqual(sum(1 for s in held if not E.UD.is_simple_clause(s)), 1)

    def test_protocol_morphology_ud_curves_tree_bound(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = E.main(Path(tmp) / "RESULT.json")
        self.assertEqual(result["schema"], "ocm.l1.linguistic-g2.v4")
        self.assertEqual(result["terminal"], "COMPOSITIONAL_LANGUAGE_LEARNING_ONLY")
        self.assertEqual(result["past_hypothesis"], "SVO")
        self.assertEqual(result["morph_rule"], "-∅+ed")
        self.assertIn("slay", result["morph_exceptions"])
        self.assertTrue(result["fresh_invoked"])
        self.assertTrue(result["held_past_ok"])
        self.assertTrue(result["agreement_ok"])
        self.assertTrue(result["mismatch_rejected"])
        self.assertTrue(result["question_ok"])
        self.assertTrue(result["modality_ok"])
        self.assertTrue(result["ud_three_token_gold_match"])
        self.assertTrue(result["ud_role_aligned"])
        self.assertTrue(result["ud_amod_incomplete_mapping"])
        self.assertTrue(result["ud_complex_unmapped"])
        self.assertFalse(result["ud_parser_used"])
        self.assertIn("not a UD parser", result["ud_channel"])
        self.assertEqual(result["realized_held_past_form"], "entombed")
        self.assertTrue(result["reverse_read_ok"])
        self.assertEqual(result["irregular_form"], "slew")
        self.assertEqual(result["held_irregular_overregularised"], "bringed")
        self.assertEqual(result["mutant_exception_overridden"], "slayed")
        self.assertTrue(result["curve_monotonic_to_one"])
        self.assertEqual(result["acquisition_curve"][0]["held_regular_accuracy"], 0.0)
        self.assertEqual(result["acquisition_curve"][-1]["held_regular_accuracy"], 1.0)
        self.assertGreater(result["tree9_nodes"], result["canonical_bound"])
        self.assertLessEqual(result["tree11_nodes"], result["explicit_tree_canonical_bound"])
        self.assertTrue(result["tree9_exact"])
        self.assertEqual(result["tree9_tree_digest_prefix"], "tree:")
        self.assertTrue(result["non_tree_over_bound"])
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
        self.assertEqual(cl["learn_morphology_agreement"], "EARNED_AT_SCOPE")
        self.assertEqual(cl["ud_alignment"], "EARNED_AT_PLANTED_GOLDTREE_SCOPE")
        self.assertEqual(cl["ud_parser"], "CANNOT_CHECK_NO_UD_PARSER")
        self.assertEqual(cl["acquisition_curves"], "EARNED_AT_SCOPE")
        self.assertEqual(cl["exact_canonicalization"], "EARNED_AT_SCOPE")
        self.assertEqual(cl["meaning_graphs_beyond_bound"], "EARNED_AT_TREE_BOUND_12")
        self.assertEqual(cl["freeze_realization_bootstrap"], "EARNED_AT_SCOPE")
        self.assertEqual(cl["learn_lexical_realization"], "EARNED_AT_SCOPE")
        self.assertEqual(cl["learn_questions"], "EARNED_AT_SCOPE")
        self.assertEqual(cl["learn_modality"], "EARNED_AT_SCOPE")
        self.assertEqual(cl["learn_questions_negation_modality"], "EARNED_QUESTIONS_MODALITY_CITED_V2_NEGATION")
        self.assertEqual(cl["negation"], "CITED_V2_EARNED_AT_SCOPE")
        self.assertEqual(cl["quantifier_scope"], "CITED_V2_EARNED_AT_SCOPE")
        self.assertEqual(cl["retain_polysemy"], "CITED_V2_EARNED_AT_SCOPE")
        self.assertEqual(cl["typed_entities"], "CITED_V2_EARNED_AT_SCOPE")
        self.assertEqual(cl["artificial_non_english"], "CITED_V3_EARNED_AT_SCOPE")
        self.assertEqual(cl["held_out_construction_families"], "CITED_V3_NO_CROSS_FAMILY_TRANSFER")
        self.assertEqual(cl["neural_realizer"], "CANNOT_CHECK_NO_NN_LIBRARY")
        self.assertEqual(cl["open_weight_lm_reference"], "CANNOT_CHECK_NO_MODEL_WEIGHTS")
        self.assertEqual(cl["acquire_corpus_scale_lexicon"], "CANNOT_CHECK_MINIATURE_MICROWORLD")
        self.assertEqual(cl["ud_corpus"], "CANNOT_CHECK_MINIATURE_MICROWORLD")
        self.assertEqual(cl["recursive_composition_lot_l2"], "CANNOT_CHECK_L2_LOCKED")
        self.assertEqual(cl["multi_session_l3"], "CANNOT_CHECK_L3_LOCKED")
        self.assertNotIn("EARNED", cl["ud_parser"])
        self.assertNotIn("EARNED", cl["neural_realizer"])
        self.assertNotIn("EARNED", cl["acquire_corpus_scale_lexicon"])
        held = result["held_rows"]
        self.assertEqual(held["past"]["roles"]["agent"], "caracal")
        self.assertEqual(held["past"]["roles"]["patient"], "phylactery")
        self.assertEqual(held["past"]["roles"]["event"], "entomb")
        self.assertIn("TENSE", held["past"]["relations"])
        self.assertEqual(held["agreement_mismatch"]["verdict"], "UNKNOWN_CONSTRUCTION")
        self.assertIn("ASKS", held["yesno"]["relations"])
        self.assertIn("MODALITY", held["modality"]["relations"])
        self.assertEqual(held["present_sg"]["verdict"], "INTERPRETED")
        self.assertEqual(held["present_pl"]["verdict"], "INTERPRETED")

    def test_v1_v2_v3_results_not_overwritten(self):
        v1 = json.loads(V1_RESULT.read_text())
        v2 = json.loads(V2_RESULT.read_text())
        v3 = json.loads(V3_RESULT.read_text())
        self.assertEqual(v1["schema"], "ocm.l1.linguistic-g2.v1")
        self.assertEqual(v1["terminal"], "COMPOSITIONAL_LANGUAGE_LEARNING_ONLY")
        self.assertEqual(v2["schema"], "ocm.l1.linguistic-g2.v2")
        self.assertEqual(v2["terminal"], "COMPOSITIONAL_LANGUAGE_LEARNING_ONLY")
        self.assertEqual(v2["checklist"]["negation"], "EARNED_AT_SCOPE")
        self.assertEqual(v2["checklist"]["ud_alignment"], "CANNOT_CHECK_NO_UD_IN_THIS_STUDY")
        self.assertEqual(v3["schema"], "ocm.l1.linguistic-g2.v3")
        self.assertEqual(v3["terminal"], "COMPOSITIONAL_LANGUAGE_LEARNING_ONLY")
        self.assertEqual(v3["checklist"]["held_out_construction_families"], "NO_CROSS_FAMILY_TRANSFER")
        self.assertEqual(v3["checklist"]["artificial_non_english"], "EARNED_AT_SCOPE")


if __name__ == "__main__":
    unittest.main()
