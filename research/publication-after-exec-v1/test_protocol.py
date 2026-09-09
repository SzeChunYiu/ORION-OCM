"""Protocol tests for #165 §15 after-execution harvest."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

import experiment as E

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


class TestPinnedHarvest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = E.run()

    def test_terminal_is_receipts_present_with_gaps(self):
        self.assertEqual(self.result["terminal"], E.TERMINAL)
        self.assertEqual(self.result["terminal"], "PUBLICATION_AFTER_EXEC_RECEIPTS_PRESENT_WITH_GAPS")
        self.assertFalse(self.result["closes_issue_144"])
        self.assertEqual(self.result["evidence_class"], "E3_INTERNAL_GENERATOR_ONLY")
        self.assertNotIn(self.result["evidence_class"], E.FORBIDDEN_EVIDENCE)

    def test_earned_versus_cannot_check_partition(self):
        earned = set(self.result["earned"])
        cannot_check = set(self.result["cannot_check"])
        self.assertEqual(earned, set(E.EARNED_BOXES))
        self.assertIn("fresh_host_rerun", cannot_check)
        self.assertIn("disjoint_replication", cannot_check)
        self.assertIn("independent_scorer_checker", cannot_check)
        self.assertTrue(earned.isdisjoint(cannot_check))
        self.assertEqual(earned | cannot_check, set(E.AFTER_BOXES))

    def test_cannot_check_codes_are_explicit(self):
        boxes = self.result["boxes"]
        self.assertEqual(boxes["fresh_host_rerun"]["status"], "CANNOT_CHECK_NO_SECOND_MACHINE")
        self.assertIn("second machine", boxes["fresh_host_rerun"]["conversion"].lower())
        self.assertEqual(
            boxes["disjoint_replication"]["status"],
            "CANNOT_CHECK_NO_E4_DISJOINT_REPLICATION",
        )
        self.assertEqual(
            boxes["independent_scorer_checker"]["status"],
            "CANNOT_CHECK_NO_INDEPENDENT_SCORER",
        )
        self.assertIn("not an independent scorer", boxes["independent_scorer_checker"]["conversion"].lower())
        self.assertTrue(boxes["red_team_reviewer_simulation"]["status"].startswith("CANNOT_CHECK"))
        self.assertEqual(
            self.result["section16"]["independently_authored_families_E3"],
            "CANNOT_CHECK_NO_INDEPENDENT_AUTHORSHIP",
        )

    def test_cited_receipts_exist_and_hashes_recompute(self):
        self.assertGreaterEqual(len(self.result["cited_receipts"]), 20)
        for row in self.result["cited_receipts"]:
            path = REPO / row["path"]
            self.assertTrue(path.is_file(), row["path"])
            self.assertEqual(row["sha256"], E.sha256_file(path))
            self.assertEqual(len(row["sha256"]), 64)
            self.assertGreater(row["bytes"], 0)

    def test_existing_sha256sums_verify(self):
        for row in self.result["checksum_manifest"]["existing_sha256sums"]:
            self.assertTrue(row["verified"], row)
            self.assertGreater(row["ok"], 0)
            self.assertEqual(row["missing"], 0)
            self.assertEqual(row["mismatch"], 0)

    def test_failures_and_raw_traces_are_present(self):
        failures = self.result["boxes"]["failures"]
        traces = self.result["boxes"]["raw_traces"]
        self.assertEqual(failures["status"], "EARNED")
        self.assertGreater(failures["failure_attempts_n"], 0)
        self.assertEqual(traces["status"], "EARNED")
        self.assertGreater(traces["failure_attempts_n"], 0)
        g3 = next(row for row in self.result["cited_receipts"] if row["path"].endswith("g3-failure-memory-v1/RESULT.json"))
        self.assertGreaterEqual(g3["failure_attempts_n"], 6)
        self.assertIn("stored_records", g3["accounting_keys"])

    def test_crashes_timeouts_retained(self):
        box = self.result["boxes"]["crashes_timeouts"]
        self.assertEqual(box["status"], "EARNED")
        self.assertGreaterEqual(box["retained_timeout_or_crash_n"], 3)
        timeout = next(
            row
            for row in self.result["cited_receipts"]
            if row["path"].endswith("controls-final/timeout/result.json")
        )
        self.assertTrue(timeout["gnu_timeout_exit"])
        self.assertEqual(timeout["exit_code"], 124)
        error = next(
            row
            for row in self.result["cited_receipts"]
            if row["path"].endswith("controls-final/error/result.json")
        )
        self.assertEqual(error["exit_code"], 7)
        watchdog = next(
            row
            for row in self.result["cited_receipts"]
            if row["path"].endswith("controls-final/watchdog/result.json")
        )
        self.assertEqual(watchdog["exit_code"], -9)
        self.assertTrue(watchdog["supervisor_timeout"])

    def test_cost_vectors_and_figure_tables(self):
        self.assertEqual(self.result["boxes"]["raw_cost_vectors"]["status"], "EARNED")
        self.assertEqual(self.result["boxes"]["immutable_figure_tables"]["status"], "EARNED")
        self.assertGreaterEqual(self.result["boxes"]["immutable_figure_tables"]["scaling_n"], 3)
        packed = next(
            row
            for row in self.result["cited_receipts"]
            if row["path"].endswith("g5-packed-field-v1/RESULT.json")
        )
        self.assertGreaterEqual(packed["scaling_n"], 3)
        g3 = next(
            row
            for row in self.result["cited_receipts"]
            if row["path"].endswith("g3-failure-memory-v1/RESULT.json")
        )
        self.assertIn("study_wall_seconds", g3["accounting_keys"])
        self.assertIn("storage_bytes", g3["accounting_keys"])

    def test_exclusions_have_reasons(self):
        box = self.result["boxes"]["exclusions_with_reasons"]
        self.assertEqual(box["status"], "EARNED")
        self.assertGreater(box["prior_exposed_length6_n"], 0)
        self.assertEqual(box["held_out_construction_families"], "NO_CROSS_FAMILY_TRANSFER")

    def test_correspondence_has_no_contradiction(self):
        box = self.result["boxes"]["claim_result_correspondence_review"]
        self.assertEqual(box["status"], "EARNED")
        self.assertEqual(box["kind"], "MECHANICAL_AUTHOR_SIDE_CORE_VS_RESULT")
        self.assertEqual(box["n_contradictions"], 0)
        statuses = {row["status"] for row in self.result["correspondence"]}
        self.assertNotIn("CONTRADICTION", statuses)
        self.assertTrue(
            statuses
            & {"MATCH", "DEFERRED_TO_RESULT", "MATCH_TIMEOUT_NOT_JUMP", "MATCH_GAPS_DOCUMENTED"}
        )

    def test_g24_confirmatory_traces_remain_missing(self):
        gaps = self.result["g24_g31_raw_traces"]
        self.assertTrue(gaps["all_absent"])
        self.assertIn("MISSING_ON_THIS_HEAD_CI_ARTIFACT", gaps["note"])
        for row in gaps["rows"]:
            self.assertFalse(row["present"])
        self.assertIn("MISSING_ON_THIS_HEAD_CI_ARTIFACT", self.result["claim_ceiling"])

    def test_does_not_overwrite_constitution_result_json(self):
        for rel in E.CONSTITUTION_RESULT_PATHS:
            self.assertFalse((REPO / rel).exists(), rel)
        frozen = self.result["constitution_not_overwritten"]
        self.assertEqual(
            frozen["v1_protocol_sha256"],
            E.sha256_file(REPO / "research/publication-constitution-v1/PROTOCOL.json"),
        )
        self.assertEqual(
            frozen["v2_protocol_sha256"],
            E.sha256_file(REPO / "research/publication-constitution-v2/PROTOCOL.json"),
        )
        v2 = json.loads((REPO / "research/publication-constitution-v2/PROTOCOL.json").read_text())
        self.assertEqual(v2["terminal"], "PUBLICATION_CONSTITUTION_FROZEN_WITH_GAPS")
        self.assertFalse(v2["closes_issue_144"])
        after = v2["section15"]["after_execution"]
        self.assertTrue(str(after["fresh_host_rerun"]["status"]).startswith("CANNOT_CHECK"))
        self.assertEqual(after["disjoint_replication"]["status"], "MISSING")

    def test_core_names_earned_and_cannot_check(self):
        core = (HERE / "CORE.md").read_text(encoding="utf-8")
        self.assertIn("PUBLICATION_AFTER_EXEC_RECEIPTS_PRESENT_WITH_GAPS", core)
        self.assertIn("retain raw traces", core)
        self.assertIn("CANNOT_CHECK_NO_SECOND_MACHINE", core)
        self.assertIn("CANNOT_CHECK_NO_E4_DISJOINT_REPLICATION", core)
        self.assertIn("CANNOT_CHECK_NO_INDEPENDENT_SCORER", core)
        self.assertIn("human independent author", core)
        self.assertIn("second machine", core)
        self.assertNotIn("#144 scientifically closed", core.lower())
        self.assertIn("MISSING_ON_THIS_HEAD_CI_ARTIFACT", core)

    def test_committed_result_matches_live_harvest_identity(self):
        committed_path = HERE / "RESULT.json"
        self.assertTrue(committed_path.is_file())
        committed = json.loads(committed_path.read_text(encoding="utf-8"))
        self.assertEqual(committed["terminal"], self.result["terminal"])
        self.assertEqual(committed["earned"], self.result["earned"])
        self.assertEqual(committed["cannot_check"], self.result["cannot_check"])
        live_hashes = {row["path"]: row["sha256"] for row in self.result["checksum_manifest"]["cited"]}
        committed_hashes = {row["path"]: row["sha256"] for row in committed["checksum_manifest"]["cited"]}
        self.assertEqual(live_hashes, committed_hashes)


if __name__ == "__main__":
    unittest.main()
