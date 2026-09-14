import copy
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("freeze_held_predictions_v1", ROOT / "freeze_held_predictions_v1.py")
mod = importlib.util.module_from_spec(SPEC)
if SPEC.loader is None:
    raise RuntimeError("cannot load freeze module")
SPEC.loader.exec_module(mod)


class FreezeReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stored = json.loads((ROOT / "HELD_FAMILY_PREDICTIONS_V1.json").read_text())

    def test_stored_manifest_matches_prefit_predictor_exactly(self):
        self.assertEqual(mod.build_freeze_manifest(), self.stored)
        mod.validate_freeze_manifest(self.stored)

    def test_six_opaque_families_and_twelve_members(self):
        self.assertEqual(6, len(self.stored["families"]))
        self.assertEqual(12, sum(len(f["members"]) for f in self.stored["families"]))
        for family in self.stored["families"]:
            self.assertTrue(family["family_id"].startswith("HF_"))

    def test_every_held_member_is_outside_development_cube(self):
        for family in self.stored["families"]:
            for member in family["members"]:
                point = member["descriptor_margins"]
                self.assertTrue(any(abs(value) > 1 for value in point.values()))

    def test_freeze_contains_both_determinate_predictions_and_abstentions(self):
        values = []
        for family in self.stored["families"]:
            for member in family["members"]:
                values.extend(member["frozen_prediction"].values())
        self.assertIn(0, values)
        self.assertIn(1, values)
        self.assertIn(mod.CANNOT_IDENTIFY, values)

    def test_outcome_insertion_is_rejected(self):
        bad = copy.deepcopy(self.stored)
        bad["families"][0]["members"][0]["observed_outcome"] = 1
        with self.assertRaises(ValueError):
            mod.validate_freeze_manifest(bad)

    def test_prediction_edit_is_rejected(self):
        bad = copy.deepcopy(self.stored)
        pred = bad["families"][0]["members"][0]["frozen_prediction"]
        pred["coordination_exact"] = 1
        with self.assertRaises(ValueError):
            mod.validate_freeze_manifest(bad)

    def test_development_overlap_is_rejected(self):
        bad = copy.deepcopy(self.stored)
        point = bad["families"][0]["members"][0]["descriptor_margins"]
        for key in point:
            point[key] = 0
        with self.assertRaises(ValueError):
            mod.validate_freeze_manifest(bad)

    def test_digest_edit_is_rejected(self):
        bad = copy.deepcopy(self.stored)
        bad["freeze_digest"] = "0" * 64
        with self.assertRaises(ValueError):
            mod.validate_freeze_manifest(bad)


if __name__ == "__main__":
    unittest.main()
