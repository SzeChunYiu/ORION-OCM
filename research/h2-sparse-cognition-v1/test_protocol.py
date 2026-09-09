"""H2 planted sparse-cognition protocol tests. Production src is imported, not copied."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
G5 = REPO / "research" / "g5-packed-field-v1"
SRC = REPO / "src"
for path in (str(SRC), str(G5), str(HERE)):
    if path not in sys.path:
        sys.path.insert(0, path)

import experiment as E
import sparse_index as S
from packed_space import PackedKnowledgeSpace


class TestH2SparseCognition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ks = E.plant_world(64)
        cls.packed = PackedKnowledgeSpace.from_reference(cls.ks)
        cls.index = S.SparseCognitionIndex.build(cls.packed)

    def test_planted_k_goals_among_n(self):
        ks = self.ks
        goals = [a.atom_id for a in ks.atoms if a.atom_type == S.TARGET_TYPE]
        self.assertEqual(len(ks.atoms), 64)
        self.assertEqual(len(ks.hyperedges), 64)
        self.assertEqual(len(goals), S.K_TARGETS)
        self.assertEqual(goals, [f"v{i}" for i in range(S.K_TARGETS)])

    def test_construction_scans_n_and_packed_build_is_charged(self):
        index = self.index
        self.assertEqual(index.construction_units, 64)
        self.assertGreater(index.packed_index_build_touches, 0)
        self.assertEqual(len(index.postings[S.TARGET_TYPE]), S.K_TARGETS)

    def test_posting_retrieval_is_k_linear_is_n_bitmap_is_n_over_8(self):
        posting = self.index.retrieve_type(S.TARGET_TYPE)
        bitmap = S.g5_bitmap_query(self.index, S.TARGET_TYPE)
        linear = S.g5_linear_query(self.index, S.TARGET_TYPE)
        self.assertEqual(posting.retrieval_units, S.K_TARGETS)
        self.assertEqual(posting.materialization_units, S.K_TARGETS)
        self.assertEqual(posting.k, S.K_TARGETS)
        self.assertEqual(posting.hidden_scan_units, 0)
        self.assertEqual(linear.retrieval_units, 64)
        self.assertEqual(linear.hidden_scan_units, 64)
        self.assertEqual(linear.k, 64)
        self.assertEqual(bitmap.retrieval_units, 8)
        self.assertEqual(set(posting.hits), set(bitmap.hits))
        self.assertEqual(set(posting.hits), set(linear.hits))
        self.assertLess(posting.query_work_units, linear.query_work_units)
        self.assertLessEqual(bitmap.retrieval_units, linear.retrieval_units)

    def test_incremental_update_is_one_rebuild_is_n(self):
        from ocm.kso.space import Atom
        from ocm.kso.warrant import WarrantProfile

        extra = Atom("v64", S.TARGET_TYPE, WarrantProfile.of({0}))
        incremental = self.index.incremental_update(extra)
        rebuilt = self.index.rebuild_update(extra)
        self.assertEqual(incremental.update_units, 1)
        self.assertEqual(rebuilt.update_units, 65)
        self.assertGreater(incremental.packed_index_build_touches, 0)
        self.assertEqual(len(incremental.retrieve_type(S.TARGET_TYPE).hits), S.K_TARGETS + 1)

    def test_live_atoms_and_mutant_hidden_scans(self):
        live = S.live_atoms_hidden_scan(self.index)
        mutant = S.mutant_uninstrumented_linear(self.packed, S.TARGET_TYPE)
        self.assertEqual(live.hidden_scan_units, 64)
        self.assertEqual(live.k, 64)
        self.assertEqual(S.classify_hidden_scan(live), "CHARGED")
        self.assertEqual(mutant.status, "CANNOT_CHECK_UNINSTRUMENTED_GLOBAL_SCAN")
        self.assertEqual(
            S.classify_hidden_scan(mutant), "CANNOT_CHECK_UNINSTRUMENTED_GLOBAL_SCAN"
        )
        self.assertEqual(mutant.hidden_scan_units, 0)
        self.assertEqual(mutant.k, S.K_TARGETS)

    def test_experiment_earns_h2_boxes_without_programme_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = E.main(Path(tmp) / "RESULT.json")
        self.assertEqual(result["schema"], E.SCHEMA)
        self.assertEqual(result["issue"], 165)
        self.assertFalse(result["programme_wide_close"])
        self.assertFalse(result["production_src_edited"])
        self.assertEqual(result["terminal"], "PARENT_SUFFICIENT_AT_PLANTED_INDEX_SCOPE")
        boxes = result["boxes"]
        for key in (
            "H2/001-charge_index_construction",
            "H2/002-charge_index_update",
            "H2/003-charge_retrieval",
            "H2/004-charge_materialization",
            "H2/005-charge_hidden_scans",
        ):
            self.assertEqual(boxes[key]["status"], "EARNED_AT_SCOPE", key)
        scaling = result["scaling"]
        self.assertEqual(scaling["status"], "MEASURED")
        self.assertTrue(scaling["posting_tracks_k_better_than_n"])
        self.assertTrue(scaling["linear_tracks_n"])
        self.assertTrue(scaling["bitmap_tracks_n_not_k"])
        self.assertTrue(scaling["k_over_N_decreases"])
        self.assertTrue(scaling["k_ll_N_at_largest"])
        rows = result["rows"]
        self.assertEqual([row["n"] for row in rows], [64, 256, 1024])
        self.assertEqual(rows[0]["g5_bitmap_units_touched"], 8)
        self.assertEqual(rows[0]["g5_linear_units_touched"], 64)
        self.assertEqual(rows[1]["g5_bitmap_units_touched"], 32)
        self.assertEqual(rows[1]["g5_linear_units_touched"], 256)
        self.assertEqual(rows[2]["g5_bitmap_units_touched"], 128)
        self.assertEqual(rows[2]["g5_linear_units_touched"], 1024)
        self.assertEqual(rows[0]["posting"]["retrieval_units"], 8)
        self.assertEqual(rows[2]["posting"]["retrieval_units"], 8)
        self.assertLess(rows[2]["posting"]["k_over_N"], rows[0]["posting"]["k_over_N"])
        self.assertIn("PROGRAMME_WIDE_H2_CLOSE", result["not_issued"])

    def test_capsule_does_not_patch_production_space(self):
        text = Path(E.__file__).read_text() + Path(S.__file__).read_text()
        self.assertNotIn("monkeypatch", text)
        self.assertIn("from packed_space import PackedKnowledgeSpace", text)
        self.assertIn("from ocm.kso.space import", text)
        self.assertFalse(E.production_src_edited())
        self.assertTrue((REPO / "src" / "ocm" / "kso" / "space.py").is_file())


class TestH2ResultFreeze(unittest.TestCase):
    def test_written_result_matches_terminal(self):
        path = Path(__file__).resolve().parent / "RESULT.json"
        if not path.exists():
            self.skipTest("RESULT.json not yet written")
        data = json.loads(path.read_text())
        self.assertEqual(data["schema"], E.SCHEMA)
        self.assertEqual(data["terminal"], "PARENT_SUFFICIENT_AT_PLANTED_INDEX_SCOPE")
        self.assertFalse(data["programme_wide_close"])
        for key in (
            "H2/001-charge_index_construction",
            "H2/002-charge_index_update",
            "H2/003-charge_retrieval",
            "H2/004-charge_materialization",
            "H2/005-charge_hidden_scans",
        ):
            self.assertEqual(data["boxes"][key]["status"], "EARNED_AT_SCOPE", key)


if __name__ == "__main__":
    unittest.main()
