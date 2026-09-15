#!/usr/bin/env python3
"""Unit tests for gmi-novel-intelligence-w4-v1 (Py3.8-safe; -I safe)."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import unittest
from pathlib import Path

_path = Path(__file__).with_name("novel_intelligence_w4_v1.py")
_spec = importlib.util.spec_from_file_location("novel_intelligence_w4_v1", _path)
w4 = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(w4)


class TestFreeze(unittest.TestCase):
    def test_freeze_digest(self):
        self.assertEqual(
            hashlib.sha256(w4.FREEZE_LITERAL).hexdigest(),
            w4.FREEZE_SHA256,
        )
        w4.assert_freeze_intact()


class TestEcologyFamily(unittest.TestCase):
    def test_ecology_for_k_max_m(self):
        v6 = w4._load_upstream()
        for k in w4.FAMILY_KS + (w4.FRESH_K,):
            q_p, q_o = w4.ecology_for_k(k)
            self.assertEqual(v6.max_multiplicity(q_p, q_o), k)
            pred = v6.property_vector_prediction(q_p, q_o)
            self.assertEqual(pred["predicted_min_cost"], 2 + k)
            self.assertEqual(pred["flat_table_cost"], k + 3)
            self.assertGreater(pred["flat_table_cost"], pred["predicted_min_cost"])


class TestCampaign(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = w4.run_campaign()

    def test_upstream_compose(self):
        up = self.receipt["upstream_compose"]
        self.assertTrue(up["compose_ok"])
        self.assertTrue(up["W2_parent_separation"])
        self.assertTrue(up["W3_empirical_niche"])
        self.assertFalse(up["W4_domain_status_upstream"])
        self.assertFalse(up["phase_hole_occupant_claim_upstream"])

    def test_all_w4_boxes_green(self):
        self.assertTrue(self.receipt["all_w4_boxes_green"])
        for name, box in self.receipt["w4_boxes"].items():
            self.assertTrue(box["tick"], msg=name)

    def test_ladder_w4(self):
        ladder = self.receipt["item39_ladder"]
        self.assertTrue(ladder["W4_domain_status"])
        self.assertFalse(ladder["phase_hole_occupant_claim"])
        self.assertFalse(ladder["j4_new_domain_claimed"])
        self.assertFalse(ladder["p4_surviving_unseen_domain"])
        self.assertTrue(ladder["p4_surviving_unseen_morphology"])
        self.assertEqual(
            ladder["claim_ceiling"],
            "W4_RESIDUAL_QUOTIENT_STRUCTURAL_DOMAIN_AT_REGISTERED_FINITE_FAMILY_SCOPE",
        )
        self.assertEqual(
            ladder["item39_ceiling"],
            "NOVEL_INTEL_LADDER_W2_W3_W4_GREEN_AT_EXACT_RQM_FAMILY_SCOPE",
        )

    def test_fixed_budget_family_residual(self):
        assays = {a["k"]: a for a in self.receipt["family_assays"]}
        self.assertEqual(assays[2]["fixed_budget_parent"]["verdict"], "OVERPROVISIONS__DOES_NOT_TRACK_MAX_M")
        self.assertEqual(assays[3]["fixed_budget_parent"]["verdict"], "LOCALLY_MATCHES_AT_B_ONLY")
        self.assertEqual(assays[4]["fixed_budget_parent"]["verdict"], "FAILS_RECOVERY")

    def test_fresh_outside_family(self):
        fresh = self.receipt["fresh_prediction"]
        self.assertTrue(fresh["outside_family"])
        self.assertTrue(fresh["fresh_prediction_holds"])
        self.assertEqual(fresh["k"], 5)
        self.assertFalse(fresh["measured"]["fixed_budget_succeeds"])

    def test_emit_receipt_roundtrip(self):
        here = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(here, "RESULT_V1.json")
        w4.emit_receipt(path)
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        self.assertTrue(data["all_w4_boxes_green"])
        self.assertTrue(data["item39_ladder"]["W4_domain_status"])


if __name__ == "__main__":
    unittest.main()
