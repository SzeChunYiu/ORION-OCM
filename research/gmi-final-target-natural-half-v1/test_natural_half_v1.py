"""Exact controls for final-target natural-intelligence half V1.

Schema, L1–L3, V7 composition, claim ceiling. CPython 3.8+; unittest; no network.
"""

import importlib.util
import json
import sys
import unittest
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_SPEC = importlib.util.spec_from_file_location(
    "natural_half_v1", str(_DIR / "natural_half_v1.py")
)
_MOD = importlib.util.module_from_spec(_SPEC)
sys.modules["natural_half_v1"] = _MOD
_SPEC.loader.exec_module(_MOD)


class TestDualSchema(unittest.TestCase):
    def test_registry_loads(self):
        meta, rows = _MOD.load_registry()
        self.assertEqual(meta["schema"], "GMI_BIOLOGICAL_BRIDGE_QUAD_V1")
        self.assertTrue(meta["frozen"])
        self.assertEqual(len(rows), 7)

    def test_every_row_complete_quad(self):
        _, rows = _MOD.load_registry()
        for row in rows:
            self.assertTrue(_MOD.quad_fields_complete(row), row.id)

    def test_holdout_never_consulted(self):
        _, rows = _MOD.load_registry()
        for row in rows:
            self.assertEqual(row.D_holdout["status"], "HELD_OUT")
            self.assertIsNone(row.D_holdout["content"])

    def test_forbidden_claims_listed(self):
        meta, _ = _MOD.load_registry()
        forbidden = set(meta["claim_ceiling"]["forbidden"])
        self.assertTrue(_MOD.FORBIDDEN_CLAIMS.issubset(forbidden))


class TestL1DescriptorsAndLaws(unittest.TestCase):
    def test_six_descriptors(self):
        self.assertEqual(len(_MOD.DESCRIPTOR_IDS), 6)

    def test_profile_laws_cover_descriptors(self):
        covered = {law.descriptor for law in _MOD.PROFILE_LAWS}
        self.assertEqual(covered, set(_MOD.DESCRIPTOR_IDS))

    def test_profiles_distinct_across_taxa(self):
        _, rows = _MOD.load_registry()
        self.assertTrue(_MOD.profiles_distinct(rows))


class TestL2SevenTaxa(unittest.TestCase):
    def test_exactly_seven_taxa(self):
        self.assertEqual(len(_MOD.TAXA), 7)
        _, rows = _MOD.load_registry()
        self.assertEqual(len(rows), 7)

    def test_taxon_names_match_module_table(self):
        _, rows = _MOD.load_registry()
        self.assertEqual(
            sorted(r.taxon for r in rows),
            sorted(t.name for t in _MOD.TAXA),
        )

    def test_phase_winners_match_machine_half(self):
        _, rows = _MOD.load_registry()
        for row in rows:
            self.assertTrue(_MOD.phase_winner_matches(row), row.id)

    def test_soft_reuse_biology_prediction_regimes(self):
        """First four taxa reuse biology-predictions (E,R,V) numbers."""
        expected = {
            "corvid": (8.0, 5.0, 7.0),
            "cephalopod": (8.0, 3.0, 4.0),
            "rodent": (5.0, 7.0, 3.0),
            "nonhuman_primate": (9.0, 8.0, 9.0),
        }
        for name, (E, R, V) in expected.items():
            tax = _MOD.TAXA_BY_NAME[name]
            self.assertEqual((tax.E, tax.R, tax.V), (E, R, V))


class TestL3HumanArchitecture(unittest.TestCase):
    def test_human_architecture_ok(self):
        _, rows = _MOD.load_registry()
        human = [r for r in rows if r.taxon == "human"][0]
        self.assertTrue(_MOD.human_architecture_ok(human))

    def test_no_neuroanatomy(self):
        _, rows = _MOD.load_registry()
        human = [r for r in rows if r.taxon == "human"][0]
        self.assertIsNone(human.C_pred["architecture"]["neuroanatomy"])

    def test_four_memory_regimes(self):
        _, rows = _MOD.load_registry()
        human = [r for r in rows if r.taxon == "human"][0]
        regimes = set(human.C_pred["architecture"]["memory_regimes"])
        self.assertEqual(
            regimes, {"working", "episodic", "semantic", "procedural"}
        )


class TestV7Composition(unittest.TestCase):
    def test_lesion_alignment(self):
        self.assertTrue(_MOD.lesion_alignment_ok())

    def test_compose_passes(self):
        result = _MOD.compose_natural_half()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["terminal"], _MOD.TERMINAL)
        self.assertFalse(result["phenotype_consulted"])
        self.assertTrue(result["machine_half_composed"])

    def test_honest_ticks_surface(self):
        ticks = _MOD.honest_ticks()
        self.assertIn("admissible", ticks["592.40(a)"])
        self.assertIn("admissible", ticks["602.L1"])
        self.assertIn("admissible", ticks["602.L2"])
        self.assertIn("admissible", ticks["602.L3"])
        self.assertIn("admissible", ticks["602.V7"])
        self.assertIn("OPEN", ticks["592.40(b)"])
        self.assertIn("NOT claimed", ticks["HUMAN_COGNITION_EXPLAINED"])
        self.assertIn("NOT claimed", ticks["G10_empirical"])


class TestNegatives(unittest.TestCase):
    def test_incomplete_quad_rejected(self):
        row = _MOD.BridgeQuad(
            id="X",
            taxon="corvid",
            E_bio={"E": 1},
            M={},
            C_pred={},
            D_holdout={"status": "HELD_OUT", "content": None},
        )
        self.assertFalse(_MOD.quad_fields_complete(row))

    def test_unsealed_holdout_rejected(self):
        _, rows = _MOD.load_registry()
        row = rows[0]
        bad = _MOD.BridgeQuad(
            id=row.id,
            taxon=row.taxon,
            E_bio=dict(row.E_bio),
            M=dict(row.M),
            C_pred=dict(row.C_pred),
            D_holdout={"status": "UNSEALED", "content": {"n": 1}, "provenance_slot": "x"},
        )
        self.assertFalse(_MOD.quad_fields_complete(bad))

    def test_theorem_mentions_ceiling(self):
        text = (_DIR / "FINAL_TARGET_NATURAL_HALF_THEOREM_V1.md").read_text()
        for token in (
            "HUMAN_COGNITION_EXPLAINED",
            "admissible",
            "reachable",
            "D_holdout",
            "neuroanatom",
        ):
            self.assertIn(token, text)

    def test_core_lists_required_files(self):
        text = (_DIR / "CORE.md").read_text()
        for name in (
            "FINAL_TARGET_NATURAL_HALF_THEOREM_V1.md",
            "PREDICTIONS_REGISTRY_V1.json",
            "natural_half_v1.py",
            "test_natural_half_v1.py",
            "MANIFEST.json",
        ):
            self.assertIn(name, text)


class TestManifest(unittest.TestCase):
    def test_manifest_parents(self):
        data = json.loads((_DIR / "MANIFEST.json").read_text())
        parents = data.get("parents") or []
        for p in (
            "research/gmi-biological-bridge-v1",
            "research/gmi-natural-intelligence-bridge-v1",
            "research/gmi-derived-lesion-v1",
            "research/gmi-morphology-phase-rv-v1",
        ):
            self.assertIn(p, parents)


if __name__ == "__main__":
    unittest.main()
