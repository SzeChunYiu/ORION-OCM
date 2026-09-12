#!/usr/bin/env python3

import json
import unittest
from pathlib import Path

from run_gmi_parent_prediction_discrimination_v1 import (
    EXPECTED_FREEZE_SHA256,
    canonical_sha256,
    run_exact,
)


HERE = Path(__file__).resolve().parent
FREEZE = HERE / "GMI_PARENT_PREDICTION_DISCRIMINATION_FREEZE_V1.json"


class ParentPredictionDiscriminationV1Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
        cls.receipt = run_exact(cls.freeze)

    def test_freeze_hash(self):
        self.assertEqual(canonical_sha256(self.freeze), EXPECTED_FREEZE_SHA256)

    def test_exact_cell_count(self):
        self.assertEqual(self.receipt["checks"]["cells"], 512)

    def test_parent_product_exactly_matches_all_atomics(self):
        checks = self.receipt["checks"]
        self.assertEqual(checks["parent_product_total_mismatches"], 0)
        self.assertEqual(
            checks["parent_product_mismatches_by_mechanism"],
            {
                "A2_dev_side_information_required": 0,
                "A3_incremental_repair_opportunity": 0,
                "A4_rejection_recoverability_required": 0,
                "A5_lineage_persistence_required": 0,
            },
        )

    def test_positive_controls_have_predeclared_disagreements(self):
        self.assertEqual(
            self.receipt["checks"]["positive_control_mismatches"],
            {
                "A2_alias_only_proxy": 128,
                "A3_query_locality_proxy": 256,
                "A4_update_rate_proxy": 256,
                "A5_drift_only_proxy": 256,
            },
        )
        for witness in self.receipt["first_positive_control_witnesses"].values():
            self.assertIsNotNone(witness)

    def test_terminal_and_claim_ceiling(self):
        self.assertEqual(
            self.receipt["terminal"],
            "ATOMIC_MECHANISM_PREDICTIONS_PARENT_PRODUCT_SUFFICIENT_AT_REGISTERED_BINARY_SCOPE",
        )
        self.assertTrue(self.receipt["overall_B1"].startswith("OPEN__"))
        self.assertEqual(self.receipt["first_parent_witnesses"], [])


if __name__ == "__main__":
    unittest.main()
