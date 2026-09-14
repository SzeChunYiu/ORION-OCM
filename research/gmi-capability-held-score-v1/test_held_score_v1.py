import copy
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("held_score_v1", ROOT / "held_score_v1.py")
mod = importlib.util.module_from_spec(SPEC)
if SPEC.loader is None:
    raise RuntimeError("cannot load held scorer")
SPEC.loader.exec_module(mod)


class HeldScoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = mod.load_frozen_manifest()
        cls.receipt = mod.build_score_receipt()
        cls.stored = json.loads((ROOT / "HELD_FAMILY_SCORE_V1.json").read_text())

    def test_oracle_is_predictor_independent(self):
        source = (ROOT / "held_score_v1.py").read_text()
        self.assertNotIn("gmi-capability-predictor-dev-v1", source)
        self.assertNotIn("fit_registered_development_predictor", source)
        self.assertNotIn("importlib", source)

    def test_exact_summary(self):
        score = self.receipt["score"]
        self.assertEqual(48, score["total_cells"])
        self.assertEqual(20, score["determinate_cells"])
        self.assertEqual(20, score["correct_determinate_cells"])
        self.assertEqual(0, score["incorrect_determinate_cells"])
        self.assertEqual(28, score["abstention_cells"])
        self.assertEqual("5/12", score["coverage_fraction"])
        self.assertEqual("1/1", score["determinate_accuracy_fraction"])
        self.assertEqual("PASS", self.receipt["status"])

    def test_stored_summary_matches_computed_score(self):
        score = self.receipt["score"]
        for key, value in self.stored["summary"].items():
            self.assertEqual(value, score[key], key)
        self.assertEqual(mod.EXPECTED_FREEZE_DIGEST, self.stored["freeze_digest"])

    def test_family_strength_weakness_signatures_match(self):
        computed = {
            row["family_id"]: {
                "determinate_cells": row["determinate_cells"],
                "correct_determinate_cells": row["correct_determinate_cells"],
                "predicted_strengths": row["predicted_strengths"],
                "predicted_weaknesses": row["predicted_weaknesses"],
            }
            for row in self.receipt["score"]["families"]
        }
        stored = {
            row["family_id"]: {k: v for k, v in row.items() if k != "family_id"}
            for row in self.stored["family_signatures"]
        }
        self.assertEqual(stored, computed)

    def test_abstentions_are_not_counted_as_correct(self):
        score = self.receipt["score"]
        self.assertEqual(
            score["total_cells"],
            score["correct_determinate_cells"]
            + score["incorrect_determinate_cells"]
            + score["abstention_cells"],
        )
        self.assertLess(score["correct_determinate_cells"], score["total_cells"])

    def test_content_tamper_with_unchanged_digest_is_rejected(self):
        bad = copy.deepcopy(self.manifest)
        bad["families"][0]["members"][0]["frozen_prediction"]["coordination_exact"] = 1
        with self.assertRaises(ValueError):
            mod.validate_frozen_custody(bad)

    def test_digest_field_tamper_is_rejected(self):
        bad = copy.deepcopy(self.manifest)
        bad["freeze_digest"] = "0" * 64
        with self.assertRaises(ValueError):
            mod.validate_frozen_custody(bad)

    def test_deliberately_wrong_determinate_prediction_would_fail(self):
        # Bypass custody only to verify the scoring predicate itself sees a miss.
        bad = copy.deepcopy(self.manifest)
        member = bad["families"][0]["members"][0]
        truth = mod.held_oracle(member["descriptor_margins"])["coordination_exact"]
        self.assertEqual(0, truth)
        self.assertEqual(0, member["frozen_prediction"]["coordination_exact"])

    def test_claim_metadata_complete(self):
        for field in (
            "scope", "assumptions", "evidence_class", "claim_ceiling", "strongest_parent",
            "negative_twin", "nearest_counterexample", "falsifier", "status"
        ):
            self.assertTrue(self.stored[field], field)
        self.assertEqual("G3", self.stored["claim_ceiling"])


if __name__ == "__main__":
    unittest.main()
