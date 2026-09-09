"""G4 remaining non-ML decision-adequacy protocol. Imports the horizon toy; no ML."""
from __future__ import annotations

import ast
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import experiment as E


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
HORIZON = REPO / "research" / "g4-horizon-exact-v1"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestImportNotCopy(unittest.TestCase):
    def test_horizon_engine_is_imported_not_copied(self):
        source = (HERE / "experiment.py").read_text(encoding="utf-8")
        self.assertIn("g4-horizon-exact-v1", source)
        self.assertIn("import horizon_exact as H", source)
        self.assertIn("H.exact_dp_unlimited", source)
        self.assertIn("H.simulate", source)
        self.assertIn("H.residual_after_exact_parents", source)
        self.assertNotIn("def exact_dp_unlimited", source)
        self.assertNotIn("def pareto_insert_payload", source)
        tree = ast.parse(source)
        names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
        self.assertNotIn("exact_dp_unlimited", names)
        self.assertNotIn("simulate", names)

    def test_no_ml_training(self):
        source = (HERE / "experiment.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertTrue(imported.isdisjoint({"sklearn", "torch", "tensorflow", "jax"}))
        self.assertNotIn("def train", source)
        study = E.run_study()
        self.assertFalse(study["ml_trained"])
        self.assertFalse(study["neural_router"])

    def test_horizon_capsule_not_overwritten(self):
        self.assertTrue((HORIZON / "horizon_exact.py").is_file())
        self.assertTrue((HORIZON / "CORE.md").is_file())
        self.assertTrue((HORIZON / "SUMMARY.json").is_file())
        summary = json.loads((HORIZON / "SUMMARY.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["schema"], "ocm.g4-horizon-exact.v1")
        self.assertEqual(summary["g4_boxes"]["G4.4_learned_routing"], "NOT_UNLOCKED")
        self.assertIn("EXACT_META_POLICY_SUFFICIENT", summary["terminals"])
        cited = E.horizon_citations()
        for name, digest in cited["sha256"].items():
            self.assertEqual(digest, _sha256(HORIZON / name), name)


class TestFeatureSufficiency(unittest.TestCase):
    def test_full_legal_set_succeeds_and_dropping_remaining_fails(self):
        features = E.feature_sufficiency()
        self.assertTrue(features["full_succeeds"])
        self.assertTrue(features["drop_necessary_bit_fails"])
        self.assertTrue(features["full_legal_set"]["sufficient"])
        self.assertGreater(features["drop_remaining"]["n_collisions"], 0)
        self.assertGreater(features["drop_cached"]["n_collisions"], 0)
        self.assertTrue(features["drop_item"]["sufficient"])
        self.assertTrue(features["drop_time"]["sufficient"])
        self.assertTrue(features["earned_at_toy"])


class TestHypothesisClass(unittest.TestCase):
    def test_dp_is_adequate_myopic_is_not(self):
        hypo = E.hypothesis_class()
        self.assertTrue(hypo["dp_in_class"])
        self.assertTrue(hypo["dp_contains_analytic_on_constant"])
        self.assertEqual(hypo["required_first_miss_on_constant_h8"], "buy")
        self.assertEqual(hypo["myopic_first_miss_on_constant_h8"], "rent")
        self.assertTrue(hypo["myopic_cannot_represent_required_buy"])
        self.assertTrue(hypo["myopic_h_eff_strictly_below_dp"])
        self.assertEqual(hypo["myopic_constant"]["h_eff"], 0)
        self.assertEqual(hypo["analytic_constant"]["h_eff"], 7)
        self.assertTrue(hypo["earned_at_toy"])


class TestResidualAndPareto(unittest.TestCase):
    def test_analytic_residual_vs_dp_is_zero(self):
        residual = E.residual_analytic_vs_dp()
        self.assertTrue(residual["refuted"])
        self.assertFalse(residual["any_material_residual"])
        for row in residual["families"]:
            self.assertTrue(row["cited_horizon_residual"]["analytic_on_dp_pareto"], row["family"])
            self.assertEqual(row["nonzero_components"], {}, row["family"])
            self.assertFalse(row["material_residual"], row["family"])

    def test_pareto_band_cites_and_does_not_contradict(self):
        band = E.pareto_band()
        self.assertEqual(band["cited_pr154_band"], "H=4..8")
        self.assertEqual(band["toy_break_even_remaining_strict"], 4)
        self.assertEqual(band["toy_constant_analytic_switch_horizon"], 5)
        self.assertTrue(band["does_not_contradict_cited_band"])
        self.assertTrue(band["mixed_rent_vs_buy_incomparable"])
        rows = {row["horizon"]: row for row in band["constant_rows"]}
        self.assertTrue(rows[4]["analytic_equals_rent"])
        self.assertTrue(rows[5]["analytic_equals_buy"])
        self.assertFalse(E.H.analytic_should_buy(4))
        self.assertTrue(E.H.analytic_should_buy(5))


class TestLifecycleAndLifetime(unittest.TestCase):
    def test_reset_cache_matches_empty_rebuild(self):
        life = E.lifecycle_reset_rebuild()
        self.assertTrue(life["all_reset_intervals_match_rebuild"])
        self.assertEqual([row["interval"] for row in life["rows"]], [1, 2, 4, 8])
        for row in life["rows"]:
            self.assertTrue(row["cached_value_after_reset_equals_rebuild"], row["interval"])
            self.assertGreater(row["reset"]["invalidation"], 0)
            self.assertTrue(row["h_eff_match"])
            self.assertTrue(row["service_match"])
        self.assertTrue(life["checkpoint"]["checkpoint_preserves_heff_on_constant"])
        self.assertEqual(life["checkpoint"]["checkpoint_h_eff"], 7)
        self.assertTrue(life["earned_at_toy"])

    def test_lifetime_raw_vector_no_scalarization_learner_not_positive(self):
        lifetime = E.lifetime_vectors()
        self.assertFalse(lifetime["scalarization"])
        self.assertTrue(lifetime["exact_parent_price_conditional"])
        self.assertTrue(lifetime["heff_preserved_under_checkpoint"])
        self.assertTrue(lifetime["heff_killed_by_reset_every_1"])
        self.assertFalse(lifetime["learner_lifetime_positive_after_train_infer_update_maintain"])
        self.assertTrue(lifetime["learner_strictly_adds_cost_with_no_residual_to_amortize"])
        self.assertFalse(lifetime["earned_as_g44_unlock"])
        overhead = lifetime["hypothetical_learner_overhead"]
        self.assertGreater(overhead["train"], 0)
        self.assertGreater(overhead["infer"], 0)


class TestResultAndUnlockLock(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            cls.result = E.main(Path(tmp) / "RESULT.json")
        cls.disk = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))

    def test_terminal_does_not_claim_g44(self):
        self.assertEqual(self.result["terminal"], "G4_NON_ML_ADEQUACY_SUPPORTED_AT_TOY_SCOPE")
        self.assertEqual(self.disk["terminal"], self.result["terminal"])
        self.assertFalse(self.result["g4_4_unlocked"])
        self.assertEqual(self.result["g4_4_unlock_score"], "0/9")
        self.assertEqual(self.result["g4_4_4th"], "REFUTED")
        self.assertEqual(self.result["g4_4_learned_routing"], "NOT_UNLOCKED")
        self.assertFalse(self.result["ml_trained"])
        self.assertIn("G4.4", self.result["not_issued"])
        self.assertIn("NEURAL_ROUTER", self.result["not_issued"])
        self.assertNotIn("SMALL_LEARNED_ROUTER_VALUE_SUPPORTED", self.result["earned"])

    def test_box_mapping(self):
        boxes = self.result["boxes"]
        self.assertEqual(len(boxes), 9)
        self.assertEqual(
            boxes[E.G44_BOXES[3]]["status"],
            "REFUTED_AT_TOY",
        )
        self.assertEqual(
            boxes[E.G44_BOXES[4]]["status"],
            "EARNED_AT_TOY_SCOPE",
        )
        self.assertEqual(
            boxes[E.G44_BOXES[5]]["status"],
            "EARNED_AT_TOY_SCOPE",
        )
        self.assertEqual(
            boxes[E.G44_BOXES[6]]["status"],
            "MEASURED_EXACT_PARENT_PRICE_CONDITIONAL_LEARNER_NOT_POSITIVE",
        )
        self.assertEqual(
            boxes[E.G44_BOXES[7]]["status"],
            "EARNED_AT_TOY_SCOPE",
        )
        self.assertEqual(
            boxes[E.G44_BOXES[8]]["status"],
            "EARNED_AT_TOY_SCOPE",
        )
        for row in boxes.values():
            self.assertFalse(row["g4_4_unlock"])
        self.assertEqual(len(self.result["earned"]), 4)
        self.assertEqual(self.result["refuted"], [E.G44_BOXES[3]])

    def test_capsule_result_matches_run(self):
        self.assertEqual(self.disk["schema"], E.SCHEMA)
        self.assertEqual(self.disk["salt"], E.SALT)
        self.assertEqual(self.disk["g4_4_unlock_score"], "0/9")
        self.assertEqual(self.disk["earned"], self.result["earned"])
        self.assertFalse(self.disk["horizon_engine_copied"])
        self.assertFalse(self.disk["production_src_edited"])


if __name__ == "__main__":
    unittest.main()
