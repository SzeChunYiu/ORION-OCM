#!/usr/bin/env python3
"""Tests for gmi-unseen-form-prediction-v1 (#602 V6, #592 item 39)."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "unseen_form_prediction_v1", HERE / "unseen_form_prediction_v1.py"
)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


class FreezeTests(unittest.TestCase):
    def test_freeze_digest_matches_authority(self):
        self.assertEqual(MOD.freeze_digest(), MOD.FREEZE_SHA256)
        MOD.assert_freeze_intact()


class PredictionBeforeSearchTests(unittest.TestCase):
    def test_primary_ecology_c0_prediction(self):
        pred = MOD.property_vector_prediction(MOD.Q_P, MOD.Q_O)
        self.assertEqual(pred["min_residual_alphabet"], 3)
        self.assertEqual(pred["min_predictor_classes"], 2)
        self.assertEqual(pred["predicted_min_cost"], 5)
        self.assertEqual(pred["flat_table_cost"], 6)
        self.assertTrue(pred["needs_residual"])
        self.assertTrue(pred["zero_residual_impossible_under_qp"])
        self.assertEqual(pred["fiber_multiplicities"], {0: 3, 1: 2})

    def test_fresh_ecology_c0_prediction(self):
        pred = MOD.property_vector_prediction(MOD.Q_P_FRESH, MOD.Q_O_FRESH)
        self.assertEqual(pred["min_residual_alphabet"], 4)
        self.assertEqual(pred["predicted_min_cost"], 6)
        self.assertEqual(pred["flat_table_cost"], 7)

    def test_pure_predictor_fails_on_primary_under_qp(self):
        self.assertFalse(MOD.pure_predictor_under_qp_succeeds(MOD.Q_P, MOD.Q_O))


class NeutralRecoveryTests(unittest.TestCase):
    def test_canonical_rqm_matches_prediction(self):
        pred = MOD.property_vector_prediction(MOD.Q_P, MOD.Q_O)
        canon = MOD.construct_canonical_rqm(MOD.Q_P, MOD.Q_O)
        self.assertEqual(canon["cost"], 5)
        self.assertEqual(canon["p_size"], 2)
        self.assertEqual(canon["r_size"], 3)
        pv = MOD.classify_property_vector(
            canon["p_assign"], canon["r_assign"], canon["decoder"], MOD.Q_O, pred
        )
        self.assertTrue(all(pv.values()))

    def test_no_cheaper_residual_under_qp(self):
        self.assertFalse(MOD.exists_residual_exact(MOD.Q_P, MOD.Q_O, 2))
        self.assertTrue(MOD.exists_residual_exact(MOD.Q_P, MOD.Q_O, 3))

    def test_neutral_recovery_campaign(self):
        pred = MOD.property_vector_prediction(MOD.Q_P, MOD.Q_O)
        win = MOD.find_matching_residuals(MOD.Q_P, MOD.Q_O, pred)
        self.assertTrue(win["no_cheaper_residual_under_qp"])
        self.assertTrue(win["matches_predicted_min_cost"])
        self.assertTrue(win["any_winner_matches_prediction"])
        self.assertEqual(win["min_cost"], 5)


class NegativeTwinTests(unittest.TestCase):
    def test_twin_needs_no_residual(self):
        pred = MOD.property_vector_prediction(MOD.Q_P_TWIN, MOD.Q_O_TWIN)
        self.assertEqual(pred["min_residual_alphabet"], 1)
        self.assertFalse(pred["needs_residual"])
        self.assertTrue(MOD.pure_predictor_under_qp_succeeds(MOD.Q_P_TWIN, MOD.Q_O_TWIN))

    def test_negative_twin_assay(self):
        twin = MOD.negative_twin_assay()
        self.assertTrue(twin["negative_twin_removes_residual_necessity"])


class ParentReductionTests(unittest.TestCase):
    def test_material_residual_against_flat_and_predictor(self):
        pred = MOD.property_vector_prediction(MOD.Q_P, MOD.Q_O)
        parent = MOD.parent_reduction_residual(MOD.Q_P, MOD.Q_O, pred)
        self.assertTrue(parent["material_residual_positive"])
        self.assertEqual(parent["material_residual_vs_flat"], 1)
        self.assertFalse(parent["pure_predictor_under_qp_succeeds"])
        self.assertEqual(
            parent["parent_first_refusal"],
            "PARENT_REDUCTION_LEAVES_MATERIAL_RESIDUAL",
        )


class RemintTests(unittest.TestCase):
    def test_remint_replication(self):
        remint = MOD.remint_replication()
        self.assertTrue(remint["prediction_invariant_under_remint"])
        self.assertTrue(remint["independent_remint_replication"])


class FreshPredictionTests(unittest.TestCase):
    def test_fresh_residual_specific_prediction(self):
        fresh = MOD.fresh_residual_prediction()
        self.assertTrue(fresh["fresh_prediction_holds"])
        self.assertEqual(fresh["predicted_max_m"], 4)
        self.assertEqual(fresh["measured_min_cost"], 6)
        self.assertFalse(fresh["pure_predictor_under_qp"])


class FullCampaignTests(unittest.TestCase):
    def test_all_six_v6_boxes_green(self):
        receipt = MOD.run_campaign()
        self.assertTrue(receipt["all_six_v6_boxes_green"])
        for name, box in receipt["v6_boxes"].items():
            self.assertTrue(box["tick"], msg=name)
        ladder = receipt["item39_ladder"]
        self.assertTrue(ladder["W2_parent_separation"])
        self.assertTrue(ladder["W3_empirical_niche"])
        self.assertFalse(ladder["W4_domain_status"])
        self.assertFalse(ladder["phase_hole_occupant_claim"])
        self.assertEqual(
            ladder["claim_ceiling"],
            "UNSEEN_FORM_PREDICTION_SUPPORTED_AT_REGISTERED_SCOPE",
        )
        self.assertEqual(
            ladder["item39_ceiling"],
            "NOVEL_INTEL_LADDER_W2_W3_GREEN_AT_EXACT_RQM_SCOPE__W4_NOT_CLAIMED",
        )


if __name__ == "__main__":
    unittest.main()
