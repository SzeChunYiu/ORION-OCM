from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from language_meta_strategy import run  # noqa: E402


class LanguageMetaStrategyTests(unittest.TestCase):
    def test_meta_strategy_reduces_target_interactions_without_grammar_fact_transfer(self):
        result = run()
        self.assertTrue(result["target"]["new_role_symbols_only"])
        self.assertFalse(result["grammar_content_transfer_possible"])
        self.assertTrue(result["meta_strategy_improves_later_acquisition"])
        self.assertGreater(result["target"]["saving"], 0)
        self.assertTrue(result["target"]["learned_order_equal"])

    def test_strategy_is_evidence_scoped_and_revocation_reopens_choice(self):
        result = run()
        rev = result["strategy_evidence_revocation"]
        self.assertTrue(rev["falls_back_to_fixed"])
        self.assertTrue(rev["matches_reset"])

    def test_strong_parent_matches_meta_strategy_exactly(self):
        result = run()
        self.assertTrue(result["strong_persistent_strategy_parent"]["matches_ocm"])
        self.assertEqual(result["isolated_terminal"], "PARENT_SUFFICIENT_META_STRATEGY_CALIBRATION")

    def test_meta_training_is_paired_isomorphic_and_discriminating(self):
        result = run()
        train = result["meta_training"]
        self.assertEqual(train["role_overlap"], 0)
        self.assertLess(train["balanced_training_interactions"], train["fixed_training_interactions"])
        self.assertFalse(result["protected_claim_authority"])


if __name__ == "__main__":
    unittest.main()
