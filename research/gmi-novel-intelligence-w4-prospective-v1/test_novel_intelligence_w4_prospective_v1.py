#!/usr/bin/env python3
"""Tests for the W4 prospective replication package.

Includes checker-validation cases (planted defects must alarm; identical
inputs must not) per the validate-the-checker-first rule, and script-asserted
counts for the CI-scope campaign. Py3.8-safe, stdlib-only.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import independent_route_v1 as ind  # noqa: E402
import novel_intelligence_w4_prospective_v1 as ex  # noqa: E402


class FreezeCustodyTests(unittest.TestCase):
    def test_prospective_seed_digest(self):
        self.assertEqual(
            ex.hashlib.sha256(ex.PROSPECTIVE_LITERAL).hexdigest(),
            ex.PROSPECTIVE_SHA256,
        )

    def test_freeze_plan_shape_and_counts(self):
        plan, plan_sha = ex.load_freeze_plan()
        self.assertEqual(plan["schema"], "GMI_NOVEL_INTELLIGENCE_W4_PROSPECTIVE_FREEZE_V2")
        self.assertEqual(plan["ticket"], "REV-L47-NOVEL-INTELLIGENCE-W4")
        self.assertEqual(len(plan["family_ks"]), 3)
        self.assertEqual(len(plan["extended_heldout_ks"]), 3)
        self.assertEqual(plan["extended_heldout_ks"], [6, 7, 8])
        self.assertEqual(len(plan["negative_control_ks"]), 7)
        self.assertEqual(plan["fresh_k"], 5)
        rule = plan["decision_rule"]["confirmed_iff"]
        self.assertEqual(len(rule), 5)
        law = plan["predictions"]["family_law_F"]["per_k"]
        self.assertEqual(sorted(law.keys()), ["2", "3", "4"])
        for k, row in law.items():
            self.assertEqual(row["max_m"], int(k))
            self.assertEqual(row["C_star"], 2 + int(k))
            self.assertEqual(row["flat"], int(k) + 3)
        self.assertEqual(len(plan["seeds"]["prospective_sha256"]), 64)
        self.assertEqual(plan_sha, ex.sha256_file(os.path.join(HERE, ex.FREEZE_JSON)))


class IndependentRouteTests(unittest.TestCase):
    def test_family_ecology_hand_checked(self):
        # F(2): fiber targets {0,1} and {2,3}; max_m=2; C*=2+2; flat=1+4.
        q_p, q_o = (0, 0, 1, 1), (0, 1, 2, 3)
        got = ind.ecology_properties(q_p, q_o, 3)
        self.assertEqual(got["max_m"], 2)
        self.assertEqual(got["C_star"], 4)
        self.assertEqual(got["flat"], 5)
        self.assertTrue(got["needs_residual"])
        self.assertFalse(got["pure_predictor_succeeds"])
        self.assertTrue(got["fixed_budget_recovers"])

    def test_trivial_single_target_ecology(self):
        got = ind.ecology_properties((0,), (5,), 3)
        self.assertEqual(got["max_m"], 1)
        self.assertFalse(got["needs_residual"])
        self.assertTrue(got["pure_predictor_succeeds"])
        self.assertEqual(got["C_star"], 2)

    def test_negative_control_ecology_constant_law(self):
        for k in (2, 3, 5, 8):
            q_p, q_o = ex.ecology_g(k)
            got = ind.ecology_properties(q_p, q_o, 3)
            self.assertEqual(got["max_m"], 2, "G(%d) max_m" % k)
            self.assertEqual(got["C_star"], 4, "G(%d) C*" % k)
            self.assertEqual(got["flat"], 5, "G(%d) flat" % k)
            self.assertTrue(got["fixed_budget_recovers"], "G(%d) budget" % k)
            self.assertFalse(got["pure_predictor_succeeds"], "G(%d) predictor" % k)

    def test_brute_force_witness_runs_and_finds_none(self):
        q_p, q_o = (0, 0, 0, 1, 1, 1), (0, 1, 2, 3, 4, 3)
        wit = ind.brute_force_no_decoder_below_m(q_p, q_o)
        self.assertTrue(wit["witness_run"])
        self.assertEqual(wit["tuples_enumerated"], 2 ** 6)
        self.assertEqual(wit["consistent_found"], 0)
        self.assertTrue(wit["no_decoder_below_m"])

    def test_brute_force_witness_respects_budget(self):
        # F(6): (m-1)^n = 5^12 > 2^20 -> witness must decline with a reason.
        q_p = (0,) * 6 + (1,) * 6
        q_o = tuple(range(6)) + tuple(6 + (i % 2) for i in range(6))
        wit = ind.brute_force_no_decoder_below_m(q_p, q_o)
        self.assertFalse(wit["witness_run"])
        self.assertIn("budget", str(wit["reason"]))


class CheckerValidationTests(unittest.TestCase):
    """The checkers must alarm on planted defects (no silent pass)."""

    def test_deep_diff_catches_planted_mismatch(self):
        a = {"x": [1, {"y": 2}], "z": 3}
        b = {"x": [1, {"y": 2}], "z": 4}
        diffs = ex._deep_diff(a, b, "$")
        self.assertTrue(diffs and any("z" in d for d in diffs))
        self.assertEqual(ex._deep_diff(a, {"x": [1, {"y": 2}], "z": 3}, "$"), [])

    def test_deep_diff_catches_missing_key(self):
        diffs = ex._deep_diff({"a": 1, "b": 2}, {"a": 1}, "$")
        self.assertEqual(len(diffs), 1)
        self.assertIn("missing in original", diffs[0])

    def test_finalize_verdicts(self):
        base = {
            "decision_flags": {
                "D1_replication_structured_equal": True,
                "D2_registered_predictions_match": True,
                "D3_negative_control_constant_law": True,
                "D4_independent_route_exact_agreement": True,
                "D5_determinism_bit_identity": None,
            }
        }
        ok = ex.finalize_with_determinism(json.loads(json.dumps(base)), True)
        self.assertEqual(
            ok["verdict"], "PROSPECTIVE_CONTENT_CONFIRMED__SUSPICION_CLEARED"
        )
        bad_det = ex.finalize_with_determinism(json.loads(json.dumps(base)), False)
        self.assertEqual(bad_det["verdict"], "REFUTED_AT_DETERMINISM")
        broken = json.loads(json.dumps(base))
        broken["decision_flags"]["D2_registered_predictions_match"] = False
        self.assertEqual(
            ex.finalize_with_determinism(broken, True)["verdict"], "REFUTED"
        )

    def test_multihost_tool_rejects_drift_and_accepts_identity(self):
        result = {
            "verdict": "PROSPECTIVE_CONTENT_CONFIRMED__SUSPICION_CLEARED",
            "decision_flags": {"D5_determinism_bit_identity": True},
        }
        runtime = {"host": "h1", "same_host_bit_identical": True}
        runtime2 = {"host": "h2", "same_host_bit_identical": True}
        with tempfile.TemporaryDirectory() as td:
            def dump(name, obj):
                path = os.path.join(td, name)
                with open(path, "w", encoding="utf-8") as fh:
                    json.dump(obj, fh)
                return path

            r1 = dump("r1.json", result)
            rt1 = dump("rt1.json", runtime)
            r2 = dump("r2.json", result)
            rt2 = dump("rt2.json", runtime2)
            out = os.path.join(td, "multi.json")
            tool = os.path.join(HERE, "make_multihost_receipt_v1.py")
            # no-alarm case: identical results, two hosts -> exit 0
            proc = subprocess.run(
                [sys.executable, tool, "--primary-result", r1,
                 "--primary-runtime", rt1, "--secondary-result", r2,
                 "--secondary-runtime", rt2, "--out", out],
                capture_output=True, text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            receipt = json.load(open(out, "r", encoding="utf-8"))
            self.assertEqual(receipt["host_count"], 2)
            self.assertTrue(receipt["cross_host_bit_identical"])
            # alarm case: drifted secondary result -> exit 2
            drifted = dict(result)
            drifted["verdict"] = "REFUTED"
            r2d = dump("r2d.json", drifted)
            proc2 = subprocess.run(
                [sys.executable, tool, "--primary-result", r1,
                 "--primary-runtime", rt1, "--secondary-result", r2d,
                 "--secondary-runtime", rt2, "--out", out],
                capture_output=True, text=True,
            )
            self.assertEqual(proc2.returncode, 2)
            # cannot-check case: missing file -> exit 3
            proc3 = subprocess.run(
                [sys.executable, tool, "--primary-result", r1,
                 "--primary-runtime", rt1, "--secondary-result",
                 os.path.join(td, "nope.json"), "--secondary-runtime", rt2,
                 "--out", out],
                capture_output=True, text=True,
            )
            self.assertEqual(proc3.returncode, 3)


class CIScopeCampaignTests(unittest.TestCase):
    """Full CI-scope campaign against the in-repo parent + upstream packages."""

    @classmethod
    def setUpClass(cls):
        cls.receipt = ex.run_campaign("ci")

    def test_d1_through_d4_all_true(self):
        flags = self.receipt["decision_flags"]
        for f in ex.D_FIELDS[:4]:
            self.assertTrue(flags[f], f)

    def test_counts_script_asserted(self):
        c = self.receipt["counts"]
        self.assertEqual(c["family_rows"], 3)
        self.assertEqual(c["fresh_rows"], 1)
        self.assertEqual(c["extended_rows"], 0)
        self.assertEqual(c["assay_timeouts_extended"], 0)
        self.assertEqual(c["control_rows"], 2)
        self.assertEqual(c["agreement_rows"], 8)  # F{2,3,4,5} + G{2,3,4,5}
        self.assertEqual(c["witnesses_run"], 8)

    def test_replication_zero_diffs(self):
        self.assertEqual(self.receipt["replication"]["deep_field_diffs"], [])
        self.assertTrue(self.receipt["replication"]["structured_equal_to_parent_result"])

    def test_extended_leg_absent_in_ci(self):
        self.assertIsNone(self.receipt["registered_predictions"]["extended_heldout"])

    def test_verdict_pending_determinism(self):
        # a bare (non-protocol) run cannot clear; only --protocol stamps D5
        self.assertEqual(self.receipt["verdict"], "PENDING_DETERMINISM")


if __name__ == "__main__":
    unittest.main(verbosity=2)
