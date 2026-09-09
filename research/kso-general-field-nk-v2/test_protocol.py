"""§8 GEF N/k/index/federation protocol tests. Production src is imported, not copied."""
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
import indexes as I
from packed_space import PackedKnowledgeSpace
from ocm.kso.types import CORE_ATOM_TYPES, DEFAULT_REGISTRY, TypeRegistry


class TestGefNkIndexes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ks = E.plant_world(64)
        cls.packed = PackedKnowledgeSpace.from_reference(cls.ks)
        cls.index = I.CrossDomainIndex.build(cls.packed)

    def test_capsule_is_nk_v2_not_v1(self):
        self.assertEqual(HERE.name, "kso-general-field-nk-v2")
        self.assertTrue((HERE / "experiment.py").is_file())
        self.assertNotEqual(HERE, REPO / "research" / "kso-general-field-v1")
        self.assertFalse(E.v1_capsule_overwritten())

    def test_default_registry_untouched_by_two_typed_domains(self):
        self.assertEqual(set(DEFAULT_REGISTRY.atom_types), set(CORE_ATOM_TYPES))
        extra = E.fresh_registry()
        self.assertIn(I.LANG_TYPE, extra.atom_types)
        self.assertIn(I.MATH_TYPE, extra.atom_types)
        self.assertNotIn(I.LANG_TYPE, DEFAULT_REGISTRY.atom_types)
        self.assertNotIn(I.MATH_TYPE, DEFAULT_REGISTRY.atom_types)

    def test_unrelated_cross_domain_n_on_one_field(self):
        ks = self.ks
        lang = [a for a in ks.atoms if a.atom_type == I.LANG_TYPE]
        math = [a for a in ks.atoms if a.atom_type == I.MATH_TYPE]
        self.assertEqual(len(ks.atoms), 64)
        self.assertEqual(len(lang) + len(math), 64)
        self.assertGreater(len(lang), I.K_LANG)
        self.assertGreater(len(math), I.K_MATH)
        self.assertEqual(len(ks.registry.atom_types), len(set(CORE_ATOM_TYPES) | {I.LANG_TYPE, I.MATH_TYPE}))
        self.assertTrue(self.packed.digest() == ks.digest())

    def test_relevant_k_is_planted_targets_not_type_size(self):
        lang_tag = self.index.retrieve_tag(I.LANG_TAG, relevant_k=I.K_LANG)
        math_tag = self.index.retrieve_tag(I.MATH_TAG, relevant_k=I.K_MATH)
        lang_type = self.index.retrieve_type(I.LANG_TYPE)
        self.assertEqual(lang_tag["hit_count"], I.K_LANG)
        self.assertEqual(math_tag["hit_count"], I.K_MATH)
        self.assertEqual(lang_tag["retrieval_units"], I.K_LANG)
        self.assertGreater(lang_type["hit_count"], I.K_LANG)
        self.assertEqual(lang_type["hit_count"], len(self.index.type_postings[I.LANG_TYPE]))

    def test_construction_and_update_are_charged(self):
        self.assertEqual(self.index.construction_units, 64)
        self.assertGreater(self.index.packed_index_build_touches, 0)
        from ocm.kso.space import Atom
        from ocm.kso.types import Authority
        from ocm.kso.warrant import WarrantProfile

        extra = Atom(
            "math_u_extra_test",
            I.MATH_TYPE,
            WarrantProfile.of({E.EV_UNREL_MATH}),
            Authority.of(formal_proof=1),
            content_ref=f"{I.UNREL_MATH_PREFIX}test",
        )
        incremental = self.index.incremental_update(extra)
        rebuilt = self.index.rebuild_update(extra)
        self.assertEqual(incremental.update_units, 1)
        self.assertEqual(rebuilt.update_units, 65)
        lang_after = incremental.retrieve_tag(I.LANG_TAG, relevant_k=I.K_LANG)
        self.assertEqual(lang_after["hit_count"], I.K_LANG)

    def test_linear_hidden_scan_and_mutant(self):
        linear = I.g5_linear_query(self.index, prefix=I.LANG_PREFIX, relevant_k=I.K_LANG)
        mutant = I.mutant_uninstrumented_linear(self.packed, prefix=I.LANG_PREFIX)
        self.assertEqual(linear["hidden_scan_units"], 64)
        self.assertEqual(linear["relevant_k"], I.K_LANG)
        self.assertEqual(I.classify_hidden_scan(linear), "CHARGED")
        self.assertEqual(mutant["status"], "CANNOT_CHECK_UNINSTRUMENTED_GLOBAL_SCAN")
        self.assertEqual(I.classify_hidden_scan(mutant), "CANNOT_CHECK_UNINSTRUMENTED_GLOBAL_SCAN")

    def test_parent_federation_ties_k_but_copies_to_compose(self):
        lang_ks = E.isolated_domain(self.ks, I.LANG_TYPE)
        math_ks = E.isolated_domain(self.ks, I.MATH_TYPE)
        lang_index = I.CrossDomainIndex.build(PackedKnowledgeSpace.from_reference(lang_ks))
        unified = self.index.retrieve_tag(I.LANG_TAG, relevant_k=I.K_LANG)
        routed = lang_index.retrieve_tag(I.LANG_TAG, relevant_k=I.K_LANG)
        self.assertEqual(unified["query_work_units"], routed["query_work_units"])
        unified_compose = E.try_compose(self.ks, ["lang_t0", "math_t0"], "bridge", "claim")
        isolated_compose = E.try_compose(lang_ks, ["lang_t0", "math_t0"], "bridge", "claim")
        copied = E.federation_copy_math_into_lang(lang_ks, math_ks, "math_t0")
        self.assertTrue(unified_compose["ok"])
        self.assertFalse(isolated_compose["ok"])
        self.assertTrue(copied["duplicated_identity"])
        self.assertTrue(copied["ok"])

    def test_experiment_earns_nk_boxes_without_programme_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = E.main(Path(tmp) / "RESULT.json")
        self.assertEqual(result["schema"], E.SCHEMA)
        self.assertEqual(result["issue"], 165)
        self.assertEqual(result["section"], 8)
        self.assertFalse(result["programme_wide_close"])
        self.assertFalse(result["production_src_edited"])
        self.assertFalse(result["second_truth_store"])
        self.assertFalse(result["v1_capsule_overwritten"])
        self.assertTrue(result["default_registry_untouched"])
        self.assertEqual(result["terminal"], "CURRENT_KSO_ALREADY_GENERAL_ENOUGH")
        for key in (
            "GEF/010-grow_unrelated_cross_domain_n",
            "GEF/011-measure_relevant_k",
            "GEF/012-charge_cross_domain_indexes",
            "GEF/013-compare_parent_federation",
        ):
            self.assertEqual(result["boxes"][key]["status"], "EARNED_AT_SCOPE", key)
        self.assertIn("PROGRAMME_WIDE_GEF_CLOSE", result["not_issued"])
        self.assertIn("PARENT_PRODUCT_SUFFICIENT", result["not_issued"])
        self.assertEqual([row["n"] for row in result["rows"]], [64, 256, 1024])
        self.assertTrue(result["scaling"]["posting_tracks_k_better_than_n"])
        self.assertTrue(result["scaling"]["k_over_N_decreases"])
        self.assertLess(result["rows"][2]["lang_tag"]["k_over_N"], result["rows"][0]["lang_tag"]["k_over_N"])

    def test_capsule_does_not_patch_production_or_v1(self):
        text = Path(E.__file__).read_text() + Path(I.__file__).read_text()
        self.assertNotIn("monkeypatch", text)
        self.assertIn("v1_capsule_overwritten", text)
        self.assertIn("from packed_space import PackedKnowledgeSpace", text)
        self.assertIn("from ocm.kso.space import", text)
        self.assertFalse(E.production_src_edited())

    def test_default_registry_still_core_after_study(self):
        E.measure_n(64)
        self.assertEqual(set(DEFAULT_REGISTRY.atom_types), set(CORE_ATOM_TYPES))
        self.assertIsInstance(TypeRegistry(), TypeRegistry)


class TestGefNkResultFreeze(unittest.TestCase):
    def test_written_result_matches_terminal(self):
        path = HERE / "RESULT.json"
        if not path.exists():
            self.skipTest("RESULT.json not yet written")
        data = json.loads(path.read_text())
        self.assertEqual(data["schema"], E.SCHEMA)
        self.assertEqual(data["terminal"], "CURRENT_KSO_ALREADY_GENERAL_ENOUGH")
        self.assertFalse(data["programme_wide_close"])
        for key in (
            "GEF/010-grow_unrelated_cross_domain_n",
            "GEF/011-measure_relevant_k",
            "GEF/012-charge_cross_domain_indexes",
            "GEF/013-compare_parent_federation",
        ):
            self.assertEqual(data["boxes"][key]["status"], "EARNED_AT_SCOPE", key)


if __name__ == "__main__":
    unittest.main()
