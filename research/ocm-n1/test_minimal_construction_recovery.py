from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE))

from minimal_construction_recovery import run  # noqa: E402


class MinimalConstructionRecoveryTests(unittest.TestCase):
    def test_all_seven_families_recover_from_zero_constructions(self):
        result = run()
        self.assertEqual(result["time_zero_constructions"], 0)
        self.assertEqual(result["learned_construction_objects"], 7)
        self.assertEqual(len(result["families"]), 7)
        self.assertTrue(result["all_seven_recovered"])

    def test_every_family_generalizes_and_is_revocable(self):
        result = run()
        self.assertTrue(result["all_seven_revocable"])
        for family in result["families"]:
            self.assertTrue(family["held_out_composition"], family["family"])
            self.assertTrue(family["dead_after_own_revocation"], family["family"])

    def test_hypothesis_classes_are_nontrivial_and_declared(self):
        result = run()
        counts = {row["family"]: row["hypothesis_count"] for row in result["families"]}
        self.assertEqual(counts["noun_phrase"], 6)
        self.assertEqual(counts["transitive"], 6)
        self.assertEqual(counts["intransitive"], 2)
        self.assertEqual(counts["passive"], 120)
        self.assertEqual(counts["negation"], 120)
        self.assertEqual(counts["yes_no_question"], 24)
        self.assertEqual(counts["wh_question"], 120)

    def test_wh_unresolved_reference_does_not_masquerade_as_parse_failure(self):
        result = run()
        wh = next(row for row in result["families"] if row["family"] == "wh_question")
        self.assertTrue(wh["held_out_composition"])

    def test_teacher_information_is_explicit(self):
        result = run()
        self.assertEqual(result["teacher_information"]["token_lessons"], 18)
        self.assertEqual(result["teacher_information"]["aligned_family_demonstrations"], 7)
        self.assertEqual(result["teacher_information"]["semantic_target_schemas_registered"], 7)
        self.assertFalse(result["protected_claim_authority"])
        self.assertEqual(result["terminal"], "ZERO_CONSTRUCTION_INVENTORY_RECOVERS_SEVEN_FUNCTIONAL_FAMILIES_CALIBRATION")


if __name__ == "__main__":
    unittest.main()
