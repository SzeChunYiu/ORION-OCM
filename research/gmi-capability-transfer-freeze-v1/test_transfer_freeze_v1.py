import copy
import hashlib
import importlib.util
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("freeze_transfer_predictions_v1", ROOT / "freeze_transfer_predictions_v1.py")
mod = importlib.util.module_from_spec(SPEC)
if SPEC.loader is None:
    raise RuntimeError("cannot load transfer freeze module")
SPEC.loader.exec_module(mod)


class TransferFreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stored = json.loads((ROOT / "TRANSFER_PREDICTIONS_V1.json").read_text())
        cls.generated = mod.build_freeze_manifest()

    def canonical_digest(self, payload):
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def test_generated_freeze_matches_committed_receipt_exactly(self):
        self.assertEqual(self.stored, self.generated)

    def test_claim_gate_metadata(self):
        for field in ("scope", "assumptions", "evidence_class", "claim_ceiling", "strongest_parent", "negative_twin", "nearest_counterexample", "falsifier", "status"):
            self.assertTrue(self.stored[field], field)
        self.assertEqual("G2", self.stored["claim_ceiling"])
        self.assertEqual("FROZEN_NOT_YET_SCORED", self.stored["status"])
        self.assertIs(False, self.stored["outcomes_present"])

    def test_exact_six_opaque_target_families(self):
        families = self.stored["target_task_families"]
        self.assertEqual(6, len(families))
        for family in families:
            self.assertRegex(family["task_family_id"], r"^HTF_\d{3}$")
            self.assertFalse(set(family).intersection(mod.OUTCOME_FIELDS))

    def test_target_margins_and_predictions_recompute(self):
        predictor = mod.predictor_mod.fit_registered_development_predictor()
        for family in self.stored["target_task_families"]:
            recomputed_margins = mod.margins(self.stored["system_capacity"], family["requirements"])
            self.assertEqual(family["margins"], recomputed_margins)
            self.assertEqual(family["frozen_prediction"], predictor.predict_vector(recomputed_margins))

    def test_family_and_freeze_digests_recompute(self):
        for family in self.stored["target_task_families"]:
            payload = dict(family)
            digest = payload.pop("family_digest")
            self.assertEqual(digest, self.canonical_digest(payload))
        payload = dict(self.stored)
        digest = payload.pop("freeze_digest")
        self.assertEqual(digest, self.canonical_digest(payload))

    def test_remint_negative_twin_is_invariant(self):
        source = self.stored["source_task"]
        remint = self.stored["target_task_families"][0]
        self.assertEqual(source["requirements"], remint["requirements"])
        self.assertEqual(source["margins"], remint["margins"])
        self.assertEqual(source["source_prediction"], remint["frozen_prediction"])

    def test_held_targets_are_nontrivial_and_include_abstention(self):
        families = self.stored["target_task_families"]
        outside = sum(any(abs(v) > 1 for v in family["margins"].values()) for family in families)
        self.assertGreaterEqual(outside, 5)
        self.assertTrue(any(mod.CANNOT_IDENTIFY in family["frozen_prediction"].values() for family in families))
        self.assertEqual(mod.CANNOT_IDENTIFY, families[-1]["frozen_prediction"]["planning_exact"])

    def test_outcome_leakage_and_bad_ids_are_refused(self):
        bad = copy.deepcopy(self.stored)
        bad["target_task_families"][0]["observed_outcome"] = 1
        with self.assertRaises(ValueError):
            mod.validate_clean_freeze(bad)
        self.assertIsNone(re.fullmatch(r"HTF_\d{3}", "transformer_task"))

    def test_invalid_requirement_vector_refused(self):
        bad = dict(mod.SOURCE_REQUIREMENTS)
        bad["memory_margin"] = -1
        with self.assertRaises(ValueError):
            mod.margins(mod.SYSTEM_CAPACITY, bad)
        bad_bool = dict(mod.SOURCE_REQUIREMENTS)
        bad_bool["memory_margin"] = True
        with self.assertRaises(ValueError):
            mod.margins(mod.SYSTEM_CAPACITY, bad_bool)


if __name__ == "__main__":
    unittest.main()
