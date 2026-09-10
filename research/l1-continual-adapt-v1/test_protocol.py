"""Protocol tests for L1 continual-adaptation parent. Do not `import experiment`.

g5-packed-field-v1/experiment.py shadows a naive `import experiment` when that
directory precedes this capsule on sys.path. Load this study by path.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SRC = REPO / "src"
G5 = REPO / "research" / "g5-packed-field-v1"


def _prefer(path: Path) -> None:
    p = str(path)
    while p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)


_prefer(SRC)
_prefer(G5)
_prefer(HERE)

_spec = importlib.util.spec_from_file_location(
    "l1_continual_adapt_experiment", HERE / "experiment.py"
)
E = importlib.util.module_from_spec(_spec)
sys.modules["l1_continual_adapt_experiment"] = E
assert _spec.loader is not None
_spec.loader.exec_module(E)

V1_RESULT = REPO / "research" / "l1-linguistic-g2-v1" / "RESULT.json"
V2_RESULT = REPO / "research" / "l1-linguistic-g2-v2" / "RESULT.json"
V3_RESULT = REPO / "research" / "l1-linguistic-g2-v3" / "RESULT.json"
V4_RESULT = REPO / "research" / "l1-linguistic-g2-v4" / "RESULT.json"


class TestL1ContinualAdapt(unittest.TestCase):
    def test_loaded_module_is_this_capsule_not_g5_packed_field(self):
        self.assertEqual(Path(E.__file__).resolve(), HERE / "experiment.py")
        self.assertNotEqual(Path(E.__file__).name, "packed_space.py")
        self.assertIn("l1-continual-adapt-v1", str(E.__file__))

    def test_new_salts_exclude_v1_v2_v3_v4_content(self):
        content = E.all_surfaces()
        self.assertTrue(content.isdisjoint(E.V1_SURFACES))
        self.assertTrue(content.isdisjoint(E.V2_CONTENT_SURFACES))
        self.assertTrue(content.isdisjoint(E.V3_CONTENT_SURFACES))
        self.assertTrue(content.isdisjoint(E.V4_CONTENT_SURFACES))
        self.assertNotEqual(E.TRAIN_SALT, E.HELD_SALT)
        self.assertIn("continual-adapt-v1", E.TRAIN_SALT)
        self.assertNotIn("v2", E.TRAIN_SALT)
        self.assertNotIn("v3", E.TRAIN_SALT)
        self.assertNotIn("v4", E.TRAIN_SALT)
        self.assertNotIn("green", E.S1_ANIMATE + E.S2_ANIMATE)
        self.assertNotIn("lynx", E.S1_ANIMATE + E.S2_ANIMATE)
        self.assertNotIn("jackal", E.S1_ANIMATE + E.S2_ANIMATE)
        self.assertNotIn("caracal", E.S1_ANIMATE + E.S2_ANIMATE)
        self.assertNotIn("goblet", E.S1_ARTIFACT + E.S2_ARTIFACT)
        self.assertNotIn("reliquary", E.S1_ARTIFACT + E.S2_ARTIFACT)
        self.assertNotIn("phylactery", E.S1_ARTIFACT + E.S2_ARTIFACT)

    def test_session2_filler_disjoint_from_session1(self):
        s1 = set(E.S1_ANIMATE + E.S1_ARTIFACT + E.S1_VERB)
        s2 = set(E.S2_ANIMATE + E.S2_ARTIFACT + E.S2_VERB)
        self.assertTrue(s2.isdisjoint(s1))
        self.assertNotIn(E.s2_filler_probe(), E.s1_train_utterances())
        self.assertNotIn(E.s1_held_probe(), E.s1_train_utterances())
        self.assertNotEqual(E.s1_held_probe(), E.s2_drift_probe())
        self.assertEqual(set(E.tokenize(E.s1_held_probe())), set(E.tokenize(E.s2_drift_probe())))

    def test_protocol_two_session_parent_comparison(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = E.main(Path(tmp) / "RESULT.json")
        self.assertEqual(result["schema"], "ocm.l1.continual-adapt.v1")
        self.assertIn(result["terminal"], E.LEGAL_TERMINALS)
        self.assertEqual(result["s1_hypothesis"], "SVO")
        self.assertEqual(result["replay_hypothesis"], "SVO")
        self.assertTrue(result["restart_equivalent"])
        self.assertTrue(result["reset_has_no_construction"])
        self.assertFalse(result["grammar_induction_parent_has_fresh_identity"])
        self.assertTrue(result["spelling_parent_maps_s2_to_s1"])
        self.assertTrue(result["additive"]["continued"]["s1_retention"])
        self.assertTrue(result["additive"]["continued"]["s2_filler"])
        self.assertTrue(result["additive"]["parent_replay"]["s1_retention"])
        self.assertTrue(result["additive"]["parent_replay"]["s2_filler"])
        self.assertFalse(result["additive"]["reset"]["s1_retention"])
        self.assertFalse(result["additive"]["reset"]["s2_filler"])
        self.assertEqual(result["additive"]["continued"]["n_construction_demos"], 0)
        self.assertEqual(result["additive"]["parent_replay"]["n_construction_demos"], 2)
        self.assertEqual(result["additive"]["continued"]["row_s2"]["roles"]["agent"], "fennec")
        self.assertEqual(result["additive"]["continued"]["row_s2"]["roles"]["patient"], "pyx")
        self.assertEqual(result["additive"]["continued"]["row_s2"]["roles"]["event"], "inlay")
        self.assertEqual(result["additive"]["reset"]["row_s2"]["verdict"], "UNKNOWN_CONSTRUCTION")
        self.assertTrue(result["drift"]["continued_revoke_reacquire"])
        self.assertTrue(result["drift"]["parent_live_replay"])
        self.assertTrue(result["drift"]["reset_s2_only"])
        self.assertTrue(result["union_contradiction"])
        self.assertFalse(result["drift"]["naive_union_replay"])
        self.assertTrue(result["naive_persist_without_revoke_fails_sov"])
        self.assertTrue(result["svo_forgotten_after_drift_revoke"])
        self.assertEqual(result["live_drift_hypothesis"], "SOV")
        self.assertFalse(result["l2_started"])
        self.assertFalse(result["l3_started"])
        self.assertFalse(result["morphology_n2_started"])
        self.assertFalse(result["corpus_n1_claimed"])
        self.assertFalse(result["programme_tick"])
        self.assertTrue(result["parent_sufficient_is_not_failure"])
        self.assertLessEqual(result["max_nodes"], result["canonical_bound"])
        self.assertEqual(result["terminal"], "PARENT_SUFFICIENT")
        cl = result["checklist"]
        self.assertEqual(cl["continual_adaptation_parent"], "PARENT_SUFFICIENT")
        self.assertEqual(cl["acquire_corpus_scale_lexicon"], "CANNOT_CHECK_MINIATURE_MICROWORLD")
        self.assertEqual(cl["learn_morphology_agreement"], "CANNOT_CHECK_N2_LOCKED")
        self.assertEqual(cl["multi_session_l3"], "CANNOT_CHECK_L3_LOCKED")
        self.assertEqual(cl["recursive_composition_lot_l2"], "CANNOT_CHECK_L2_LOCKED")
        self.assertEqual(cl["persistent_grammar_parent"], "CITED_V1_V4_EARNED_AT_SCOPE")
        self.assertNotIn("EARNED", cl["acquire_corpus_scale_lexicon"])
        self.assertNotIn("EARNED", cl["learn_morphology_agreement"])
        for box in result["boxes"]:
            self.assertFalse(box["programme_tick"], box["id"])
        claimed = [b for b in result["boxes"] if b["id"] == "L1/021-continual_adaptation_parent"]
        self.assertEqual(len(claimed), 1)
        self.assertEqual(claimed[0]["at_this_microscope"], "CHECK")
        self.assertFalse(claimed[0]["programme_tick"])

    def test_v1_v2_v3_v4_results_cited_not_overwritten(self):
        v1 = json.loads(V1_RESULT.read_text())
        v2 = json.loads(V2_RESULT.read_text())
        v3 = json.loads(V3_RESULT.read_text())
        v4 = json.loads(V4_RESULT.read_text())
        self.assertEqual(v1["schema"], "ocm.l1.linguistic-g2.v1")
        self.assertEqual(v1["terminal"], "COMPOSITIONAL_LANGUAGE_LEARNING_ONLY")
        self.assertEqual(v1["checklist"]["continual_adaptation_parent"], "CANNOT_CHECK_NOT_RUN")
        self.assertEqual(v2["schema"], "ocm.l1.linguistic-g2.v2")
        self.assertEqual(v2["checklist"]["continual_adaptation_parent"], "CANNOT_CHECK_NOT_RUN")
        self.assertEqual(v3["schema"], "ocm.l1.linguistic-g2.v3")
        self.assertEqual(v3["checklist"]["continual_adaptation_parent"], "CANNOT_CHECK_NOT_RUN")
        self.assertEqual(v4["schema"], "ocm.l1.linguistic-g2.v4")
        self.assertEqual(v4["terminal"], "COMPOSITIONAL_LANGUAGE_LEARNING_ONLY")
        self.assertEqual(v4["checklist"]["continual_adaptation_parent"], "CANNOT_CHECK_NOT_RUN")
        self.assertEqual(E.file_sha256(V1_RESULT), E.FROZEN_CAPS[0][2])
        self.assertEqual(E.file_sha256(V2_RESULT), E.FROZEN_CAPS[1][2])
        self.assertEqual(E.file_sha256(V3_RESULT), E.FROZEN_CAPS[2][2])
        self.assertEqual(E.file_sha256(V4_RESULT), E.FROZEN_CAPS[3][2])


if __name__ == "__main__":
    unittest.main()
