"""H4 planted method/cache/composition protocol tests. Production src is imported, not copied."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import experiment as E
from ocm.kso.admission import TypedRejection, compose
from ocm.kso.extraction_index import ExtractionIndex
from ocm.kso.procedures import Reading
from ocm.kso.revocation import prune
from ocm.kso.warrant import CannotCheck, Liveness


class TestH4ExactRevocation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ks = E.plant_world()
        cls.methods = E.plant_methods()

    def test_h3_capsule_not_overwritten(self):
        h3 = Path(E.REPO) / "research" / "h3-local-revision-v1"
        self.assertTrue((h3 / "CORE.md").is_file())
        self.assertTrue((h3 / "experiment.py").is_file())
        self.assertTrue((h3 / "RESULT.json").is_file())
        data = json.loads((h3 / "RESULT.json").read_text())
        self.assertEqual(data["terminal"], "PARENT_SUFFICIENT_AT_PLANTED_KSO_SCOPE")
        self.assertEqual(data["schema"], "ocm.h3.local-revision.v1")
        h4_text = Path(E.__file__).read_text()
        self.assertNotIn("PARENT_SUFFICIENT_AT_PLANTED_KSO_SCOPE", h4_text)

    def test_compose_meets_src_and_unrel_unlike_h3_atom_chain(self):
        ks = self.ks
        both = ks.atom(E.COMP_BOTH).warrant
        expected = ks.atom(E.SRC).warrant.meet(ks.atom(E.UNREL).warrant)
        self.assertEqual(both, expected)
        self.assertFalse(ks.atom(E.COMP_BOTH).is_live((E.EV_SRC,)))
        self.assertTrue(ks.atom(E.UNREL).is_live((E.EV_SRC,)))

    def test_prune_removes_source_keeps_alternate(self):
        pruned = prune(self.ks, (E.EV_SRC,))
        for atom_id in E.MUST_REMOVE:
            self.assertIn(atom_id, pruned.removed_atoms, atom_id)
            self.assertNotIn(atom_id, pruned.space.ids, atom_id)
        for atom_id in E.MUST_KEEP:
            self.assertIn(atom_id, pruned.space.ids, atom_id)
        self.assertIn(E.SRC, self.ks.ids)

    def test_methods_are_not_atoms_and_follow_readings(self):
        ks_ids = set(self.ks.ids)
        for name, lp in self.methods.items():
            self.assertNotIn(name, ks_ids)
        rv = (E.EV_SRC,)
        self.assertIs(self.methods["method_src"].liveness_for_input(0, rv), Liveness.DEAD)
        self.assertIs(self.methods["method_alt"].liveness_for_input(0, rv), Liveness.LIVE)
        self.assertIs(self.methods["method_trace"].liveness_for_input(2, rv), Liveness.DEAD)
        self.assertIs(self.methods["method_trace"].liveness_for_input(3, rv), Liveness.LIVE)
        self.assertIs(self.methods["method_trace"].reading, Reading.TRACE)

    def test_extraction_index_refuses_pruned_snapshot(self):
        index = ExtractionIndex(self.ks)
        pruned = prune(self.ks, (E.EV_SRC,))
        with self.assertRaises(CannotCheck) as ctx:
            index.check(pruned.space)
        self.assertIn("EXTRACTION_INDEX_SNAPSHOT_MISMATCH", str(ctx.exception))

    def test_pruned_store_cannot_recompose_missing_source(self):
        pruned = prune(self.ks, (E.EV_SRC,))
        with self.assertRaises(TypedRejection) as ctx:
            compose(pruned.space, [E.SRC], "relearned_head")
        self.assertEqual(ctx.exception.code, "UNKNOWN_ATOM")

    def test_experiment_earns_planted_h4_boxes_without_programme_close(self):
        capsule = Path(E.__file__).resolve().parent / "RESULT.json"
        frozen_before = capsule.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            result = E.main(Path(tmp) / "RESULT.json")
        self.assertEqual(frozen_before, capsule.read_text(encoding="utf-8"))
        self.assertEqual(result["schema"], E.SCHEMA)
        self.assertEqual(result["issue"], 165)
        self.assertFalse(result["programme_wide_close"])
        self.assertFalse(result["production_src_edited"])
        self.assertTrue(result["h3_capsule_untouched"])
        self.assertEqual(result["terminal"], "PARENT_SUFFICIENT_AT_PLANTED_EXACT_REVOCATION_SCOPE")
        boxes = result["boxes"]
        for key in (
            "H4/001-source_removal",
            "H4/002-warrant_invalidation",
            "H4/003-method_invalidation",
            "H4/004-cache_invalidation",
            "H4/005-composition_reopening",
            "H4/006-alternate_support_preservation",
            "H4/007-relearning_restoration",
        ):
            self.assertEqual(boxes[key]["status"], "EARNED_AT_SCOPE", key)
        self.assertTrue(boxes["H4/002-warrant_invalidation"]["warrants_not_rewritten"])
        self.assertTrue(boxes["H4/002-warrant_invalidation"]["strip_all_warrants_is_collateral"])
        self.assertTrue(boxes["H4/003-method_invalidation"]["static_mutant_kills_live_trace_branch"])
        self.assertEqual(
            boxes["H4/004-cache_invalidation"]["prune_snapshot_mismatch"],
            "EXTRACTION_INDEX_SNAPSHOT_MISMATCH",
        )
        self.assertTrue(boxes["H4/005-composition_reopening"]["mutant_join_compose_survives_src_revoke"])
        self.assertTrue(boxes["H4/007-relearning_restoration"]["pruned_store_lacks_source"])
        self.assertTrue(boxes["H4/007-relearning_restoration"]["recompose_on_pruned_store_rejected"])
        self.assertIn("PROGRAMME_WIDE_H4_CLOSE", result["not_issued"])
        self.assertIn("H3_OVERWRITE", result["not_issued"])

    def test_capsule_does_not_import_or_patch_production_src_paths(self):
        text = Path(E.__file__).read_text()
        self.assertNotIn("src/ocm", text)
        self.assertNotIn("monkeypatch", text)
        self.assertIn("from ocm.kso.revocation import", text)
        self.assertIn("from ocm.kso.procedures import", text)
        self.assertIn("from ocm.kso.extraction_index import", text)


class TestH4ResultFreeze(unittest.TestCase):
    def test_written_result_matches_terminal(self):
        path = Path(__file__).resolve().parent / "RESULT.json"
        if not path.exists():
            self.skipTest("RESULT.json not yet written")
        data = json.loads(path.read_text())
        self.assertEqual(data["schema"], E.SCHEMA)
        self.assertEqual(data["terminal"], "PARENT_SUFFICIENT_AT_PLANTED_EXACT_REVOCATION_SCOPE")
        self.assertFalse(data["programme_wide_close"])
        self.assertTrue(data["h3_capsule_untouched"])


if __name__ == "__main__":
    unittest.main()
