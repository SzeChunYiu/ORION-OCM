"""Protocol tests: identifiability boxes at the polynomial microscope, no ML."""
from __future__ import annotations

from pathlib import Path
import json
import unittest

import experiment as E


class TestPinnedSource(unittest.TestCase):
    def test_methods_blob_pinned(self):
        self.assertEqual(E.git_blob_sha1(E.SRC / "ocm" / "learning" / "methods.py"), E.METHOD_BLOB)
        self.assertEqual(E.METHOD_BLOB, "50323a33418b8ef8bb6500ddeba4b9d1f795e9e3")

    def test_world_is_tiny_and_disjoint(self):
        states = E.frozen_tasks()
        self.assertEqual(len(states), 4)
        ids = [s["fingerprint"] for s in states]
        self.assertEqual(len(ids), len(set(ids)))
        families = {s["family"] for s in states}
        self.assertEqual(families, {"MATCH", "MISMATCH"})
        self.assertEqual(E.FRAGMENT, ("inc", "square"))


class TestIdentifiability(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = E.run()

    def test_terminal_is_parent_sufficient_not_g24_close(self):
        self.assertEqual(self.result["terminal"], "PARENT_SUFFICIENT_AT_SCOPE")
        self.assertFalse(self.result["g24_complete"])
        self.assertFalse(self.result["g44_ml_authorized"])
        self.assertFalse(self.result["ml_trained"])
        self.assertTrue(self.result["no_sampling"])
        self.assertTrue(all(self.result["criteria"].values()))

    def test_multiple_safe_strategies_after_admissibility(self):
        self.assertTrue(self.result["all_arms_verify_all_states"])
        self.assertGreaterEqual(self.result["safe_strategies"]["n_distinct_all_succeed"], 2)
        self.assertTrue(self.result["safe_strategies"]["policies"]["always_primitive"]["all_verified"])
        self.assertTrue(self.result["safe_strategies"]["policies"]["always_macro"]["all_verified"])
        for arms in self.result["q_table"].values():
            for action in E.ACTIONS:
                self.assertTrue(arms[action]["verified"])
                self.assertEqual(arms[action]["status"], "VERIFIED_POLYNOMIAL_IDENTITY")

    def test_optimal_arm_changes_across_states(self):
        optima = {sid: row["optimal"] for sid, row in self.result["exact_backup"].items()}
        self.assertEqual(optima["match-0"], "MACRO")
        self.assertEqual(optima["match-1"], "MACRO")
        self.assertEqual(optima["mismatch-0"], "PRIMITIVE")
        self.assertEqual(optima["mismatch-1"], "PRIMITIVE")
        self.assertTrue(self.result["two_decision_episode"]["optimal_changes"])
        self.assertEqual(self.result["two_decision_episode"]["trajectory"][0]["optimal"], "MACRO")
        self.assertEqual(self.result["two_decision_episode"]["trajectory"][1]["optimal"], "PRIMITIVE")

    def test_counterfactual_is_exact_backup_not_sampling(self):
        match = self.result["exact_backup"]["match-0"]
        self.assertEqual(match["optimal"], "MACRO")
        unused = match["unused_counterfactuals"]["PRIMITIVE"]
        self.assertGreater(unused["advantage_of_best"], 0)
        self.assertEqual(unused["mechanism"], "exact_arm_rollout_slots")
        self.assertEqual(unused["slots"], match["q_slots"]["PRIMITIVE"])
        self.assertEqual(unused["slots"], self.result["q_table"]["match-0"]["PRIMITIVE"]["slots"])
        mismatch = self.result["exact_backup"]["mismatch-0"]
        self.assertGreater(mismatch["unused_counterfactuals"]["MACRO"]["advantage_of_best"], 0)

    def test_analytic_parent_recovers_dp_greedy_does_not(self):
        residual = self.result["residual_table"]
        self.assertEqual(residual["analytic_degree_threshold"]["residual_slots"], 0)
        self.assertEqual(residual["exact_dp"]["residual_slots"], 0)
        self.assertGreater(residual["always_macro"]["residual_slots"], 0)
        self.assertGreater(residual["always_primitive"]["residual_slots"], 0)
        self.assertEqual(
            residual["always_macro"]["residual_slots"] + residual["oracle_slots"],
            residual["always_macro"]["total_slots"],
        )
        self.assertIn("degree-1", residual["always_macro"]["mechanism"])
        self.assertNotIn("salt", residual["always_macro"]["mechanism"].lower())

    def test_legal_degree_suffices_aliasing_channel_does_not(self):
        degree = self.result["legal_features"]["registered_degree"]
        alias = self.result["legal_features"]["deficient_constant_term_nonzero"]
        self.assertTrue(degree["unanimous_buckets"])
        self.assertEqual(degree["regret_floor_slots"], 0)
        self.assertFalse(alias["unanimous_buckets"])
        self.assertGreater(alias["regret_floor_slots"], 0)

    def test_threshold_class_adequate_constant_class_not(self):
        h = self.result["hypothesis_class"]
        self.assertTrue(h["threshold_on_degree_adequate"])
        self.assertFalse(h["constant_class_adequate"])
        self.assertIn(2, h["thresholds_that_recover_dp"])

    def test_box_mapping_does_not_tick_programme_boxes(self):
        mapping = {row["id"]: row for row in self.result["box_mapping"]}
        for row in mapping.values():
            self.assertFalse(row["programme_tick"])
        self.assertEqual(mapping["G4.4.1"]["at_this_microscope"], "CHECK")
        self.assertEqual(mapping["G4.4.2"]["at_this_microscope"], "CHECK")
        self.assertEqual(mapping["G4.4.3"]["at_this_microscope"], "CHECK")
        self.assertEqual(mapping["G4.4.4"]["at_this_microscope"], "FAIL_PARENT_CAPTURES")
        self.assertEqual(mapping["G4.4.5"]["at_this_microscope"], "CHECK")
        self.assertEqual(mapping["G4.4.6"]["at_this_microscope"], "CHECK")
        self.assertEqual(mapping["G2.4-complete"]["at_this_microscope"], "NOT_CLAIMED")
        self.assertEqual(mapping["G4.4-ml-unlock"]["at_this_microscope"], "NOT_UNLOCKED")

    def test_legal_actions_are_snapshotted_before_q(self):
        source = (Path(__file__).resolve().parent / "experiment.py").read_text(encoding="utf-8")
        self.assertIn("def legal_actions", source)
        self.assertIn("Snapshot acceptable actions", source)
        self.assertNotIn("torch", source)
        self.assertNotIn("sklearn", source)
        self.assertNotIn("CAUSAL_METHOD_REUSE_SUPPORTED\n", source)


class TestResultFileContract(unittest.TestCase):
    def test_committed_result_matches_schema_and_ceiling(self):
        path = Path(__file__).resolve().parent / "RESULT.json"
        if not path.is_file():
            self.skipTest("RESULT.json not yet written")
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], E.SCHEMA)
        self.assertEqual(data["methods_blob"], E.METHOD_BLOB)
        self.assertEqual(data["terminal"], "PARENT_SUFFICIENT_AT_SCOPE")
        self.assertFalse(data["g24_complete"])
        self.assertFalse(data["g44_ml_authorized"])
        self.assertEqual(data["residual_table"]["analytic_degree_threshold"]["residual_slots"], 0)
        self.assertGreaterEqual(data["safe_strategies"]["n_distinct_all_succeed"], 2)


if __name__ == "__main__":
    unittest.main()
