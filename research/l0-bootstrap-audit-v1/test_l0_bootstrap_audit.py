from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import audit  # noqa: E402


REQUIRED_CLASSES = (
    "seed_lexeme",
    "morphology_prior",
    "construction_prior",
    "word_order_assumption",
    "semantic_role_mapping",
    "parser_procedure",
    "realization_template",
    "dialogue_act_rule",
    "pronoun_reference_rule",
    "clarification_rule",
    "explanation_discourse_schema",
    "style_register_rule",
    "authored_example_lesson",
    "constitutional_mechanism",
)


class L0BootstrapAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = audit.build_inventory()
        cls.ablation = audit.run_ablations()
        cls.decision = audit.derive_terminal(cls.inventory, cls.ablation)
        cls.boxes = audit.l0_box_status(cls.inventory, cls.ablation)

    def test_item_inventory_covers_required_classes(self):
        by_class = self.inventory["counts"]["by_class"]
        for klass in REQUIRED_CLASSES:
            self.assertGreater(by_class.get(klass, 0), 0, klass)

    def test_seed_counts_match_runtime(self):
        from ocm.language.bootstrap import acquisition_lexicon, microworld_lexicon
        from ocm.language.constructions import seed_constructions

        micro = [i for i in self.inventory["items"] if i["id"].startswith("L:microworld:")]
        acq = [i for i in self.inventory["items"] if i["id"].startswith("L:acquisition_fixture:")]
        morph_micro = [i for i in self.inventory["items"] if i["id"].startswith("M:microworld:")]
        self.assertEqual(len(micro), len(microworld_lexicon().lexemes))
        self.assertEqual(len(acq), len(acquisition_lexicon().lexemes))
        self.assertEqual(len(morph_micro), len(microworld_lexicon().rules))
        self.assertEqual(len(seed_constructions()), 7)
        self.assertEqual(
            len([i for i in self.inventory["items"] if i["id"].startswith("K:en:")]),
            7,
        )

    def test_classification_is_binary_and_minimal_arm_strips_english(self):
        classes = {i["classification"] for i in self.inventory["items"]}
        self.assertEqual(classes, {"constitutionally_necessary", "convenience"})
        self.assertGreater(self.inventory["counts"]["constitutionally_necessary"], 0)
        self.assertGreater(self.inventory["counts"]["convenience"], 0)
        self.assertEqual(self.inventory["counts"]["retained_language_specific_prior"], 0)
        self.assertGreater(self.inventory["counts"]["stripped_language_specific_for_n1"], 50)

    def test_reduced_bootstrap_and_sov_hostile_ran(self):
        cons = self.ablation["reduced_bootstrap"]["construction_family_removal_recovery"]
        morph = self.ablation["reduced_bootstrap"]["morphology_removal_recovery"]
        sov = self.ablation["sov_artificial_hostile"]
        hist = self.ablation["historical_seed_probe"]
        self.assertTrue(cons["all_seven_recovered"])
        self.assertEqual(cons["time_zero_constructions"], 0)
        self.assertTrue(morph["held_out_jump_generalizes"])
        self.assertEqual(morph["time_zero_morph_rules"], 0)
        self.assertEqual(sov["svo_hypothesis"], "SVO")
        self.assertEqual(sov["sov_hypothesis"], "SOV")
        self.assertTrue(sov["svo_held_out"])
        self.assertTrue(sov["sov_held_out"])
        self.assertTrue(hist["historical_bootstrap_rejects_sov"])
        self.assertFalse(self.ablation["protected_claim_authority"])

    def test_all_l0_boxes_checked_and_terminal(self):
        self.assertTrue(all(b["checked"] for b in self.boxes))
        self.assertEqual(len(self.boxes), 17)
        self.assertEqual(self.decision["terminal"], "MINIMAL_LANGUAGE_SUBSTRATE_REGISTERED")
        self.assertFalse(self.inventory["n1_claim_authority"])
        self.assertTrue(self.inventory["l1_locked"])

    def test_verify_receipt(self):
        r = audit.verify()
        self.assertEqual(r["receipt"], "L0_LANGUAGE_BOOTSTRAP_AUDIT_V1")
        self.assertEqual(r["terminal"], "MINIMAL_LANGUAGE_SUBSTRATE_REGISTERED")
        self.assertTrue(r["l1_locked"])


if __name__ == "__main__":
    unittest.main()
