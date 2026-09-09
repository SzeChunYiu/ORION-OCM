"""§8 GEF planted-oracle protocol tests. Production src is imported, not copied."""
from __future__ import annotations

import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import experiment as E
from ocm.kso.admission import compose
from ocm.kso.navigation import fixed_point, seed_vector
from ocm.kso.revocation import impact_cone, reopening_report
from ocm.kso.space import Atom, KnowledgeSpace
from ocm.kso.types import CORE_ATOM_TYPES, DEFAULT_REGISTRY, Authority, TypeRegistry
from ocm.kso.warrant import Liveness


class TestKsoGeneralField(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ks = E.plant_world()

    def test_default_registry_is_core_and_untouched_by_extras(self):
        self.assertEqual(set(DEFAULT_REGISTRY.atom_types), set(CORE_ATOM_TYPES))
        extra = E.fresh_registry_with_extras()
        for name in E.EXTRA_ATOM_TYPES:
            self.assertIn(name, extra.atom_types)
            self.assertNotIn(name, DEFAULT_REGISTRY.atom_types)
        self.assertIn("SIMILAR_TO", extra.relation_types)
        self.assertNotIn("SIMILAR_TO", DEFAULT_REGISTRY.relation_types)
        self.assertNotIn("SIMILAR_TO", extra.dependency_types)

    def test_unregistered_type_rejected_on_core_and_extra_registry(self):
        self.assertTrue(E.unregistered_rejected("vibe", TypeRegistry()))
        self.assertTrue(E.unregistered_rejected("vibe", E.fresh_registry_with_extras()))
        with self.assertRaises(Exception):
            KnowledgeSpace((Atom("x", "vibe"),), ())

    def test_compose_warrant_identical_across_language_math_science_types(self):
        core = TypeRegistry()
        extra = E.fresh_registry_with_extras()
        claim = E.compose_warrant_for_type("claim", core)
        for name in E.EXTRA_ATOM_TYPES:
            other = E.compose_warrant_for_type(name, extra)
            self.assertEqual(other["warrant"], claim["warrant"], name)
            self.assertEqual(other["liveness_revoke_0"], claim["liveness_revoke_0"], name)
            self.assertEqual(other["liveness_revoke_1_2"], "DEAD", name)

    def test_warrant_fingerprint_stable_after_type_registration(self):
        before = E.warrant_algebra_fingerprint()
        E.fresh_registry_with_extras()
        E.plant_world()
        after = E.warrant_algebra_fingerprint()
        self.assertEqual(before, after)
        self.assertEqual(before["n_profiles"], 20)
        self.assertEqual(before["n_join_meet"], 400)

    def test_speaker_commitment_is_not_world_truth(self):
        ks = self.ks
        self.assertEqual(ks.atom(E.SAID).authority, Authority.of(speaker=1))
        self.assertEqual(ks.atom(E.WORLD).authority, Authority.of(world_truth=1))
        self.assertEqual(ks.atom(E.SAID).authority.rank("world_truth"), 0)
        self.assertEqual(ks.atom(E.SAID_AND_WORLD).authority.rank("speaker"), 0)
        self.assertEqual(ks.atom(E.SAID_AND_WORLD).authority.rank("world_truth"), 0)
        self.assertIs(ks.atom(E.SAID).liveness((E.EV_METER,)), Liveness.LIVE)
        self.assertIs(ks.atom(E.WORLD).liveness((E.EV_SAID,)), Liveness.LIVE)
        self.assertIs(ks.atom(E.SAID_AND_WORLD).liveness((E.EV_SAID,)), Liveness.DEAD)

    def test_formal_proof_is_not_empirical_applicability(self):
        ks = self.ks
        self.assertEqual(ks.atom(E.PROVED).authority.rank("empirical"), 0)
        self.assertEqual(ks.atom(E.MEASURED).authority.rank("formal_proof"), 0)
        self.assertEqual(ks.atom(E.APPLICABILITY).authority.as_dict(), {})
        self.assertIs(ks.atom(E.PROVED).liveness((E.EV_METER2,)), Liveness.LIVE)
        self.assertIs(ks.atom(E.MEASURED).liveness((E.EV_KERNEL,)), Liveness.LIVE)
        self.assertIs(ks.atom(E.APPLICABILITY).liveness((E.EV_KERNEL,)), Liveness.DEAD)

    def test_similarity_activation_is_not_identity_or_warrant(self):
        ks = self.ks
        self.assertNotEqual(ks.atom(E.CAT).warrant, ks.atom(E.KAT).warrant)
        self.assertNotIn(E.KAT, impact_cone(ks, {E.CAT}))
        self.assertIs(ks.atom(E.KAT).liveness((E.EV_LEX,)), Liveness.LIVE)

    def test_shared_identity_needs_correspondence_witness(self):
        ks = self.ks
        self.assertEqual(ks.atom(E.CAT).content_ref, ks.atom(E.TWIN).content_ref)
        self.assertNotEqual(ks.atom(E.CAT).warrant, ks.atom(E.TWIN).warrant)
        self.assertIn(E.EV_CORR, ks.atom(E.IDENT).warrant.evidence)
        self.assertIs(ks.atom(E.IDENT).liveness((E.EV_CORR,)), Liveness.DEAD)
        self.assertIs(ks.atom(E.CAT).liveness((E.EV_CORR,)), Liveness.LIVE)
        hostile = E.mutant_identify_by_content_ref(ks)
        self.assertNotEqual(hostile[E.CAT]["warrant"], ks.atom(E.CAT).warrant.as_dict())

    def test_revision_by_dependency_across_views(self):
        ks = self.ks
        cone = impact_cone(ks, {E.FACT})
        self.assertTrue({E.LANG_OF_FACT, E.MATH_OF_FACT, E.SCI_OF_FACT} <= cone)
        self.assertNotIn(E.COLOR, cone)
        report = reopening_report(
            ks, (), (E.EV_SRC,), seed=seed_vector(ks, {E.GOAL: Fraction(1)})
        )
        self.assertTrue({E.LANG_OF_FACT, E.MATH_OF_FACT, E.SCI_OF_FACT} <= report.reopen)
        self.assertIn(E.COLOR, report.unaffected)
        self.assertIs(ks.atom(E.COLOR).liveness((E.EV_SRC,)), Liveness.LIVE)

    def test_same_executive_modules(self):
        self.assertEqual(compose.__module__, "ocm.kso.admission")
        self.assertEqual(fixed_point.__module__, "ocm.kso.navigation")
        self.assertEqual(impact_cone.__module__, "ocm.kso.revocation")

    def test_experiment_earns_gef_boxes_without_programme_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = E.main(Path(tmp) / "RESULT.json")
        self.assertEqual(result["schema"], E.SCHEMA)
        self.assertEqual(result["issue"], 165)
        self.assertFalse(result["programme_wide_close"])
        self.assertFalse(result["production_src_edited"])
        self.assertFalse(result["second_truth_store"])
        self.assertTrue(result["fingerprint_unchanged"])
        self.assertEqual(result["terminal"], "CURRENT_KSO_ALREADY_GENERAL_ENOUGH")
        for key in (
            "GEF/001-language_types_register_without_changing_core_warrant_semant",
            "GEF/002-mathematics_types_register_without_changing_core_warrant_sem",
            "GEF/003-procedural_scientific_types_register_without_changing_core_w",
            "GEF/004-speaker_commitment_remains_distinct_from_world_truth",
            "GEF/005-formal_proof_remains_distinct_from_empirical_applicability",
            "GEF/006-retrieved_similarity_remains_distinct_from_identity_warrant",
            "GEF/007-shared_identity_requires_correspondence_witness",
            "GEF/008-revision_propagates_across_views_by_dependency",
            "GEF/009-same_executive_architecture_works_across_domains",
        ):
            self.assertEqual(result["boxes"][key]["status"], "EARNED_AT_SCOPE", key)
        self.assertIn("GEF/010-grow_unrelated_cross_domain_n", result["not_issued"])
        self.assertIn("PROGRAMME_WIDE_GEF_CLOSE", result["not_issued"])

    def test_capsule_does_not_import_or_patch_production_by_path(self):
        text = Path(E.__file__).read_text()
        self.assertNotIn("src/ocm", text)
        self.assertNotIn("monkeypatch", text)
        self.assertIn("from ocm.kso.admission import", text)
        self.assertIn("from ocm.kso.warrant import", text)
        self.assertIn("from ocm.kso.types import", text)

    def test_default_registry_still_core_after_study(self):
        E.run_study()
        self.assertEqual(set(DEFAULT_REGISTRY.atom_types), set(CORE_ATOM_TYPES))


class TestGefResultFreeze(unittest.TestCase):
    def test_written_result_matches_terminal(self):
        path = Path(__file__).resolve().parent / "RESULT.json"
        if not path.exists():
            self.skipTest("RESULT.json not yet written")
        data = json.loads(path.read_text())
        self.assertEqual(data["schema"], E.SCHEMA)
        self.assertEqual(data["terminal"], "CURRENT_KSO_ALREADY_GENERAL_ENOUGH")
        self.assertFalse(data["programme_wide_close"])
        self.assertTrue(data["fingerprint_unchanged"])


if __name__ == "__main__":
    unittest.main()
