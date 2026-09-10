"""H3 planted-oracle protocol tests. Production src is imported, not copied."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import experiment as E
from ocm.kso.revocation import impact_cone, mutant_impact_cone_direct_only
from ocm.kso.warrant import Liveness


class TestH3LocalRevision(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ks = E.plant_world()

    def test_compose_inherits_source_warrant_and_alt_is_join(self):
        ks = self.ks
        self.assertEqual(ks.atom(E.MID).warrant.lower, ks.atom(E.SOURCE).warrant.lower)
        self.assertEqual(ks.atom(E.DEEP).warrant.lower, ks.atom(E.SOURCE).warrant.lower)
        self.assertEqual(len(ks.atom(E.ALT).warrant.lower), 2)
        self.assertEqual(len(ks.atom(E.DUAL).warrant.lower), 2)

    def test_true_dependents_die_unrelated_and_alt_live(self):
        ks = self.ks
        rv = (E.EV_SRC,)
        for atom_id in E.MUST_REOPEN:
            self.assertIs(ks.atom(atom_id).liveness(rv), Liveness.DEAD, atom_id)
        for atom_id in E.MUST_REMAIN_UNRELATED | E.MUST_REMAIN_ALT | {E.GOAL}:
            self.assertIs(ks.atom(atom_id).liveness(rv), Liveness.LIVE, atom_id)

    def test_shallow_mutant_misses_deep_dependent(self):
        ks = self.ks
        cone = impact_cone(ks, {E.SOURCE})
        mutant = mutant_impact_cone_direct_only(ks, {E.SOURCE})
        self.assertIn(E.DEEP, cone)
        self.assertNotIn(E.DEEP, mutant)
        self.assertEqual(cone, E.STRUCTURAL_DEPENDENTS_OF_SOURCE)

    def test_experiment_earns_planted_h3_boxes_without_programme_close(self):
        capsule = Path(E.__file__).resolve().parent / "RESULT.json"
        frozen_before = capsule.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            result = E.main(Path(tmp) / "RESULT.json")
        self.assertEqual(frozen_before, capsule.read_text(encoding="utf-8"))
        self.assertEqual(result["schema"], E.SCHEMA)
        self.assertEqual(result["issue"], 165)
        self.assertFalse(result["programme_wide_close"])
        self.assertFalse(result["production_src_edited"])
        self.assertEqual(result["terminal"], "PARENT_SUFFICIENT_AT_PLANTED_KSO_SCOPE")
        boxes = result["boxes"]
        for key in (
            "H3/001-true_dependents_reopen",
            "H3/002-unrelated_competence_remains",
            "H3/003-alternate_support_preserves_valid_competence",
            "H3/004-restoration_returns_exactly_justified_state",
            "H3/005-dependency_precision_recall_measured",
        ):
            self.assertEqual(boxes[key]["status"], "EARNED_AT_SCOPE", key)
        planted = boxes["H3/005-dependency_precision_recall_measured"]["planted_oracle"]
        self.assertEqual(planted["cone_vs_authored_structural_dependents"]["precision"], 1.0)
        self.assertEqual(planted["cone_vs_authored_structural_dependents"]["recall"], 1.0)
        self.assertTrue(planted["perfect_at_this_oracle"])
        mutant = boxes["H3/005-dependency_precision_recall_measured"]["mutant_shallow_cone"]
        self.assertLess(mutant["recall"], 1.0)
        self.assertTrue(mutant["misses_deep_dependent"])
        self.assertEqual(
            boxes["H3/005-dependency_precision_recall_measured"]["induced_or_unknown_support_graphs"],
            "CANNOT_CHECK_NO_INDEPENDENT_INDUCED_ORACLE",
        )
        self.assertIn("PROGRAMME_WIDE_H3_CLOSE", result["not_issued"])

    def test_precision_recall_cannot_check_on_empty_prediction(self):
        pr = E.precision_recall(frozenset(), frozenset({"a"}))
        self.assertEqual(pr["status"], "CANNOT_CHECK_EMPTY_PREDICTION")
        self.assertEqual(pr["precision"], "CANNOT_CHECK_EMPTY_PREDICTION")

    def test_capsule_does_not_import_or_patch_production_revocation(self):
        text = Path(E.__file__).read_text()
        self.assertNotIn("src/ocm", text)
        self.assertNotIn("monkeypatch", text)
        self.assertIn("from ocm.kso.revocation import", text)
        self.assertIn("from ocm.kso.warrant import", text)


class TestH3ResultFreeze(unittest.TestCase):
    def test_written_result_matches_terminal(self):
        path = Path(__file__).resolve().parent / "RESULT.json"
        if not path.exists():
            self.skipTest("RESULT.json not yet written")
        data = json.loads(path.read_text())
        self.assertEqual(data["schema"], E.SCHEMA)
        self.assertEqual(data["terminal"], "PARENT_SUFFICIENT_AT_PLANTED_KSO_SCOPE")
        self.assertFalse(data["programme_wide_close"])


if __name__ == "__main__":
    unittest.main()
