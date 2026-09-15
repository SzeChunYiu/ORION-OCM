#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("d_controls_v1", HERE / "d_controls_v1.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


class DerivationRobustnessControlsV1Tests(unittest.TestCase):
    def test_parent_no_smuggling_result_exactly_pinned(self):
        audit = mod.audit_parent_result()
        self.assertTrue(audit["all_ok"])
        self.assertTrue(audit["blob_ok"])
        self.assertTrue(audit["claim_ceiling_ok"])
        self.assertTrue(audit["verdict_ok"])

    def test_parent_receipt_mutation_fails_closed(self):
        root = mod.repo_root()
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            src = root / mod.PARENT_RESULT_PATH
            dst = tmp / mod.PARENT_RESULT_PATH
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            dst.write_bytes(dst.read_bytes() + b"\n")
            audit = mod.audit_parent_result(tmp)
            self.assertFalse(audit["all_ok"])
            self.assertFalse(audit["blob_ok"])

    def test_positive_record_passes_all_four_controls_and_parent_audit(self):
        out = mod.evaluate_record(mod.positive_record())
        self.assertEqual(out["terminal"], mod.ROBUST)
        self.assertEqual(out["controls"]["matched_twin"]["terminal"], "MATCHED_MECHANISM_TWIN")
        self.assertTrue(out["controls"]["matched_twin"]["contrast_support"])
        self.assertEqual(out["controls"]["encodings"]["terminal"], "ENCODING_ROBUST_AT_REGISTERED_FINITE_SCOPE")
        self.assertEqual(out["controls"]["search"]["terminal"], "SEARCH_ROBUST")
        self.assertEqual(out["controls"]["scalarization"]["terminal"], "SCALARIZATION_ROBUST")
        self.assertEqual(out["controls"]["no_smuggling"]["terminal"], "NO_SMUGGLING_ARMS_CLEAN")

    def test_matched_twin_preserves_registered_nuisance_capacity(self):
        out = mod.matched_twin_gate(mod.positive_record()["matched_twin"])
        self.assertEqual(out["terminal"], "MATCHED_MECHANISM_TWIN")
        self.assertEqual(out["mismatches"], ())

    def test_unmatched_depth_hostile_is_not_necessity_evidence(self):
        out = mod.matched_twin_gate(mod.hostile_unmatched_twin()["matched_twin"])
        self.assertEqual(out["terminal"], "UNMATCHED_MECHANISM_TWIN")
        self.assertIn("max_depth", out["mismatches"])
        self.assertFalse(out["contrast_support"])

    def test_target_must_actually_be_removed(self):
        out = mod.matched_twin_gate(mod.hostile_target_not_removed()["matched_twin"])
        self.assertEqual(out["terminal"], "TARGET_MECHANISM_NOT_REMOVED")

    def test_compensating_target_macro_is_rejected(self):
        out = mod.matched_twin_gate(mod.hostile_compensating_macro()["matched_twin"])
        self.assertEqual(out["terminal"], "COMPENSATING_TARGET_MACRO")

    def test_semantic_remints_are_syntactically_disjoint_but_canonically_equal(self):
        out = mod.encoding_gate(mod.positive_record()["encodings"])
        self.assertEqual(out["terminal"], "ENCODING_ROBUST_AT_REGISTERED_FINITE_SCOPE")
        self.assertTrue(out["alternate_syntax"])
        self.assertEqual(out["canonical_candidate_count"], 4)

    def test_encoding_candidate_deletion_fails(self):
        out = mod.encoding_gate(mod.hostile_encoding_missing_candidate()["encodings"])
        self.assertEqual(out["terminal"], "ENCODING_NOT_SEMANTICALLY_EQUIVALENT")

    def test_encoding_resource_change_fails(self):
        out = mod.encoding_gate(mod.hostile_encoding_resource_change()["encodings"])
        self.assertEqual(out["terminal"], "ENCODING_NOT_SEMANTICALLY_EQUIVALENT")

    def test_two_distinct_certified_searches_agree(self):
        out = mod.search_gate(mod.positive_record()["search"])
        self.assertEqual(out["terminal"], "SEARCH_ROBUST")
        self.assertTrue(out["all_searches_certified"])
        runs = dict(out["runs"])
        self.assertEqual(runs["exact_enumeration"]["selected"], ("k_balanced",))
        self.assertEqual(runs["admissible_branch_and_bound"]["selected"], ("k_balanced",))
        self.assertEqual(runs["exact_enumeration"]["evaluations"], 4)
        self.assertEqual(runs["admissible_branch_and_bound"]["evaluations"], 1)

    def test_early_stop_search_hostile_surfaces_sensitivity(self):
        out = mod.search_gate(mod.hostile_search_early_stop()["search"])
        self.assertEqual(out["terminal"], "SEARCH_SENSITIVE")
        runs = dict(out["runs"])
        self.assertEqual(runs["exact_enumeration"]["selected"], ("k_balanced",))
        self.assertEqual(runs["early_heuristic"]["selected"], ("baseline",))
        self.assertEqual(runs["early_heuristic"]["certificate"], "INCOMPLETE")

    def test_raw_pareto_set_precedes_scalarization(self):
        out = mod.scalarization_gate(mod.positive_record()["scalarization"])
        self.assertEqual(out["pareto_set"], ("k_balanced", "k_compute", "k_memory"))

    def test_property_is_robust_even_when_scalarized_candidate_identity_changes(self):
        out = mod.scalarization_gate(mod.positive_record()["scalarization"])
        self.assertEqual(out["terminal"], "SCALARIZATION_ROBUST")
        self.assertTrue(out["candidate_identity_sensitive"])
        winners = dict(out["winners"])
        self.assertEqual(winners["compute_high"], ("k_compute",))
        self.assertEqual(winners["memory_high"], ("k_memory",))
        self.assertEqual(winners["balanced"], ("k_balanced",))

    def test_universal_candidate_winner_claim_fails_under_weight_reversal(self):
        out = mod.scalarization_gate(mod.hostile_scalar_candidate_universal()["scalarization"])
        self.assertEqual(out["terminal"], "SCALARIZATION_SENSITIVE")
        self.assertTrue(out["candidate_identity_sensitive"])

    def test_missing_each_control_fails_closed(self):
        for control, expected in mod.MISSING_CONTROL_TERMINALS.items():
            with self.subTest(control=control):
                out = mod.evaluate_record(mod.missing_control_record(control))
                self.assertEqual(out["terminal"], expected)

    def test_one_failed_control_blocks_global_robustness(self):
        out = mod.evaluate_record(mod.hostile_unmatched_twin())
        self.assertEqual(out["terminal"], "D_ROBUSTNESS_NOT_ESTABLISHED")
        self.assertEqual(out["controls"]["matched_twin"]["terminal"], "UNMATCHED_MECHANISM_TWIN")
        self.assertEqual(out["controls"]["encodings"]["terminal"], "ENCODING_ROBUST_AT_REGISTERED_FINITE_SCOPE")
        self.assertEqual(out["controls"]["search"]["terminal"], "SEARCH_ROBUST")
        self.assertEqual(out["controls"]["scalarization"]["terminal"], "SCALARIZATION_ROBUST")

    def test_parent_no_smuggling_auditor_runs_on_both_compared_arms(self):
        out = mod.no_smuggling_arm_gate(mod.positive_record())
        self.assertEqual(out["terminal"], "NO_SMUGGLING_ARMS_CLEAN")
        self.assertEqual(out["arms"], {"positive": mod.CLEAN, "negative": mod.CLEAN})

    def test_receipt_green_and_byte_reproducible(self):
        receipt = mod.build_receipt()
        expected = json.loads((HERE / "RESULT_V1.json").read_text())
        self.assertEqual(receipt["verdict"], "GREEN")
        self.assertTrue(all(receipt["checks"].values()))
        self.assertEqual(json.loads(mod.canonical_json(receipt)), expected)
        self.assertEqual(mod.canonical_json(receipt), (HERE / "RESULT_V1.json").read_text())

    def test_no_floats_in_exact_receipt(self):
        def walk(value):
            if isinstance(value, float):
                self.fail("float found in exact receipt")
            if isinstance(value, dict):
                for item in value.values():
                    walk(item)
            elif isinstance(value, (list, tuple)):
                for item in value:
                    walk(item)
        walk(mod.build_receipt())

    def test_claim_ceiling_stays_bounded(self):
        receipt = mod.build_receipt()
        self.assertEqual(receipt["claim_ceiling"], mod.CLAIM_CEILING)
        self.assertIn("SEARCH_INDEPENDENT_UNIVERSALLY", receipt["forbidden_promotions"])
        self.assertIn("COMPLETE_GMI", receipt["forbidden_promotions"])


if __name__ == "__main__":
    unittest.main()
