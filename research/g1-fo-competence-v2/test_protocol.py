import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("g1_fo_competence_study", HERE / "study.py")
S = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(S)


class TestG1FOCompetenceProtocol(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = S.write_outputs()

    def test_solve_and_planner_nloc_stay_constant(self):
        world = self.result["microworld"]
        self.assertEqual(world["solve_nloc_before"], world["solve_nloc_after"])
        self.assertEqual(world["planner_nloc_before"], world["planner_nloc_after"])
        self.assertEqual(world["solve_nloc_after"], S.nloc_path(S.SOLVE))
        self.assertEqual(world["planner_nloc_after"], S.nloc_path(S.PLANNER))
        self.assertGreater(world["solve_nloc_after"], 0)
        self.assertGreater(world["planner_nloc_after"], 0)

    def test_g2_and_l1_competence_land_in_ledger_fo_state(self):
        world = self.result["microworld"]
        self.assertGreater(world["g2_delta_bytes"], 0)
        self.assertGreater(world["l1_delta_bytes"], 0)
        self.assertEqual(world["fo_delta_bytes"], world["g2_delta_bytes"] + world["l1_delta_bytes"])
        self.assertTrue(world["macro_live_after_both_admits"])
        self.assertTrue(world["l1_live_after_both_admits"])
        self.assertTrue(world["l1"]["held_out_invoked"])
        self.assertTrue(world["l1"]["reset_has_no_construction"])
        self.assertIn(world["macro_atom_id"], world["live_procedure_atoms_after_both"])
        self.assertIn(world["l1"]["atom_id"], world["live_procedure_atoms_after_both"])
        self.assertTrue(world["new_competence_in_fo_state"])

    def test_hostile_present_here_absent_from_mechanism(self):
        hostile = self.result["hostile"]
        self.assertLessEqual(hostile["hostile_function_nloc"], 10)
        self.assertTrue(hostile["hostile_solves_all_table_tasks"])
        self.assertTrue(hostile["hostile_absent_from_mechanism_arm"])
        for path, row in hostile["mechanism_contains_hostile"].items():
            self.assertFalse(row["marker"], path)
            self.assertFalse(row["function_name"], path)
        self.assertIn(S.HOSTILE_MARKER, (HERE / "study.py").read_text())

    def test_terminal_and_ceiling(self):
        self.assertEqual(self.result["terminal"], "COMPETENCE_IN_FO_STATE_AT_MICRO_SCOPE")
        self.assertFalse(self.result["production_code_deleted"])
        self.assertIn("MINIMUM_SELF_EXTENDING_VESSEL", self.result["not_issued"])
        self.assertIn("MINIMUM_SELF_EXTENDING_VESSEL_SUPPORTED_AT_SCOPE", self.result["not_issued"])
        g132 = self.result["G1_checkboxes"]["G1.3"][0]
        self.assertEqual(g132["id"], "G1.3.2")
        self.assertEqual(g132["status"], "EARNED_AT_MICRO_SCOPE")
        self.assertFalse(g132["predominantly_across_three_domains"])
        self.assertFalse(g132["procedural"])
        self.assertEqual(
            self.result["architecture_rules_empirical"]["INTELLIGENCE_IN_F_AND_O"],
            "EARNED_AT_POLYNOMIAL_AND_L1_MICRO_SCOPE",
        )

    def test_v1_result_not_salt_rescued(self):
        parent = self.result["parent_v1"]
        self.assertTrue(parent["present"])
        self.assertEqual(parent["terminal"], "COMPACT_VESSEL_PARTIAL")
        self.assertEqual(parent["G1_3_2_status"], "PARTIAL_AT_POLYNOMIAL_SCOPE")
        frozen = json.loads((S.PARENT_V1).read_text())
        self.assertEqual(frozen["terminal"], "COMPACT_VESSEL_PARTIAL")
        self.assertEqual(frozen["schema"], "ocm.g1-controller-growth.result.v1")

    def test_outputs_are_written(self):
        result = json.loads((HERE / "RESULT.json").read_text())
        summary = json.loads((HERE / "SUMMARY.json").read_text())
        self.assertEqual(result["schema"], "ocm.g1-fo-competence.result.v2")
        self.assertEqual(summary["terminal"], result["terminal"])
        self.assertGreater(summary["fo_delta_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
