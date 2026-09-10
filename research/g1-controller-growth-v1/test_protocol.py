import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("g1_controller_growth_study", HERE / "study.py")
S = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(S)


class TestG1ControllerGrowthProtocol(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = S.write_outputs()
        cls.result = cls.payload["result"]
        cls.counts = cls.payload["counts"]

    def test_nloc_matches_freeze_planner_and_solve(self):
        self.assertEqual(S.nloc_path(S.SRC / "ocm" / "dialogue" / "planner.py"), 170)
        self.assertEqual(S.nloc_path(S.SRC / "ocm" / "runtime" / "solve.py"), 536)
        self.assertEqual(self.counts["language"]["authored_controller"]["nloc"], 170)
        self.assertEqual(self.counts["math"]["shared_executive"]["nloc"], 536)

    def test_three_domain_slices_and_growth_series(self):
        series = self.counts["growth_series"]
        self.assertEqual([row["after"] for row in series], ["language", "math", "procedural"])
        self.assertEqual(series[0]["pi_delta_from_previous"], 170)
        self.assertEqual(series[1]["pi_delta_from_previous"], 0)
        self.assertEqual(series[2]["pi_delta_from_previous"], 0)
        self.assertGreater(series[0]["fo_delta_from_previous"], series[0]["pi_delta_from_previous"])
        self.assertGreater(series[1]["fo_delta_from_previous"], 0)
        self.assertGreater(series[2]["fo_delta_from_previous"], 0)
        self.assertEqual(series[1]["cumulative_controller_nloc"], series[2]["cumulative_controller_nloc"])
        self.assertGreater(series[2]["authored_fo_nloc"], series[1]["authored_fo_nloc"])
        self.assertGreater(series[1]["authored_fo_nloc"], series[0]["authored_fo_nloc"])

    def test_math_competence_is_admitted_state_not_new_pi(self):
        learned = self.counts["learned"]
        competence = self.counts["competence_in_learned_imported_fo_state"]
        self.assertGreater(learned["admitted_ledger_bytes"], 0)
        self.assertEqual(self.counts["math"]["authored_controller_delta_nloc"], 0)
        self.assertTrue(competence["math_polynomial_g2_admit"])
        self.assertFalse(competence["language"])
        self.assertFalse(competence["procedural"])
        self.assertFalse(competence["predominantly_across_three_domains"])
        self.assertEqual(competence["status"], "PARTIAL_AT_POLYNOMIAL_SCOPE")
        self.assertFalse(self.result["inventory"]["controller_growth_dominates"])
        self.assertFalse(self.result["inventory"]["state_size_dominates"])

    def test_hostile_is_short_solves_tasks_and_is_absent_from_mechanism(self):
        hostile = self.result["hostile"]
        self.assertLessEqual(hostile["hostile_function_nloc"], 10)
        self.assertTrue(hostile["hostile_solves_all_table_tasks"])
        self.assertEqual(len(hostile["hostile_tasks"]), 8)
        self.assertTrue(hostile["mechanism_arm_solves_same_tasks_by_enumeration"])
        self.assertTrue(hostile["hostile_absent_from_mechanism_arm"])
        for path, row in hostile["mechanism_contains_hostile"].items():
            self.assertFalse(row["marker"], path)
            self.assertFalse(row["function_name"], path)
        self.assertIn(S.HOSTILE_MARKER, (HERE / "study.py").read_text())

    def test_sqlite_stub_keeps_jsonl_capability_and_changes_resource(self):
        probe = self.result["subtraction"]["sqlite_vs_jsonl"]
        self.assertTrue(probe["jsonl_capability_unchanged_under_sqlite_stub"])
        self.assertTrue(probe["live_comparison"]["capability_hash_chain_match"])
        self.assertTrue(probe["live_comparison"]["resource_changed"])
        self.assertNotEqual(
            probe["live_comparison"]["jsonl_dir_bytes"],
            probe["live_comparison"]["sqlite_dir_bytes"],
        )
        self.assertIsNotNone(probe["g5"])
        self.assertEqual(probe["g5"]["terminal"], "DATABASE_PARENT_SUFFICIENT")
        self.assertGreater(probe["g5"]["jsonl_write_amplification"], 1)

    def test_warrant_collapse_drops_unknown(self):
        probe = self.result["subtraction"]["warrant_interval"]
        self.assertEqual(probe["partial_revoked_interval"], "UNKNOWN")
        self.assertEqual(probe["partial_revoked_boolean_collapse"], "DEAD")
        self.assertGreater(probe["unknown_count_with_interval"], 0)
        self.assertEqual(probe["unknown_count_after_boolean_collapse"], 0)
        self.assertTrue(probe["epistemic_invariant_failure"])

    def test_work_operator_stub_fails_and_operatorspec_wrap_survives(self):
        probe = self.result["subtraction"]["work_Operator"]
        self.assertTrue(probe["m9_construction_fails_when_Operator_stubbed"])
        self.assertTrue(probe["wrap_preserves_classify_transform"])
        self.assertTrue(probe["wrap_survives_Operator_stub"])
        self.assertTrue(probe["cognitive_capability_via_OperatorSpec"])
        self.assertTrue(probe["algebraic_api_necessity"])
        self.assertTrue(probe["m9_tests_not_preserved_by_wrap"])
        self.assertTrue(probe["restored_work_Operator"])

    def test_necessity_classifications(self):
        by_id = {row["component"]: row for row in self.result["classifications"]}
        sqlite = by_id["sqlite_ledger_vs_jsonl"]
        warrant = by_id["warrant_interval"]
        operator = by_id["work.Operator"]
        self.assertEqual((sqlite["algebraic_necessity"], sqlite["resource_necessity"], sqlite["epistemic_necessity"]), (False, True, False))
        self.assertEqual((warrant["algebraic_necessity"], warrant["resource_necessity"], warrant["epistemic_necessity"]), (False, False, True))
        self.assertEqual((operator["algebraic_necessity"], operator["resource_necessity"], operator["epistemic_necessity"]), (True, False, False))
        self.assertTrue(operator["compensating_composition"]["permitted"])
        self.assertFalse(operator["compensating_composition"]["preserves_m9_tests"])
        self.assertTrue(operator["compensating_composition"]["preserves_backend_transform"])

    def test_terminal_stays_compact_vessel_partial(self):
        self.assertEqual(self.result["terminal"], "COMPACT_VESSEL_PARTIAL")
        self.assertFalse(self.result["production_code_deleted"])
        self.assertIn("MINIMUM_SELF_EXTENDING_VESSEL_SUPPORTED_AT_SCOPE", self.result["not_issued"])
        self.assertEqual(self.result["G1_1_6_duplicate_cores"], "NOT_EARNED_AS_DELETION")
        self.assertEqual(self.result["architecture_rules_empirical"]["INTELLIGENCE_IN_F_AND_O"], "PARTIAL_AT_POLYNOMIAL_SCOPE")

    def test_outputs_are_written(self):
        result = json.loads((HERE / "RESULT.json").read_text())
        counts = json.loads((HERE / "COUNTS.json").read_text())
        self.assertEqual(result["schema"], "ocm.g1-controller-growth.result.v1")
        self.assertEqual(counts["schema"], "ocm.g1-controller-growth.counts.v1")
        self.assertEqual(result["terminal"], counts["terminal"])


if __name__ == "__main__":
    unittest.main()
