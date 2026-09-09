"""G1 Π-small / domain-general protocol. Production src is imported, not edited."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import experiment as E

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


class TestG1PiSmallProtocol(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            cls.result = E.main(Path(tmp) / "RESULT.json")
        cls.disk = json.loads((HERE / "RESULT.json").read_text())
        cls.world = cls.result["microworld"]

    def test_measured_controller_files_are_justified(self):
        paths = [row["path"] for row in self.world["controllers_before"]]
        self.assertEqual(
            paths,
            [
                "src/ocm/runtime/solve.py",
                "src/ocm/runtime/ocm_runtime.py",
                "src/ocm/dialogue/planner.py",
            ],
        )
        for row in self.world["controllers_before"]:
            self.assertGreater(row["nloc"], 0, row["path"])
            self.assertTrue((REPO / row["path"]).is_file())
            self.assertTrue(row["justification"])

    def test_controller_nloc_constant_and_byte_identical(self):
        cmp_ = self.world["controller_compare"]
        self.assertTrue(cmp_["all_nloc_constant"])
        self.assertTrue(cmp_["all_byte_identical"])
        self.assertFalse(cmp_["any_grew"])
        self.assertEqual(cmp_["controller_nloc_before"], cmp_["controller_nloc_after"])
        for row in cmp_["files"]:
            self.assertEqual(row["nloc_before"], row["nloc_after"], row["path"])
            self.assertEqual(row["sha256_before"], row["sha256_after"], row["path"])
            self.assertFalse(row["grew"], row["path"])
            self.assertEqual(E.nloc_path(REPO / row["path"]), row["nloc_after"])

    def test_freeze_pi_inventory_also_byte_identical(self):
        cmp_ = self.world["freeze_pi_compare"]
        self.assertGreaterEqual(len(cmp_["files"]), 21)
        self.assertTrue(cmp_["all_byte_identical"])
        self.assertFalse(cmp_["any_grew"])
        self.assertEqual(
            self.world["freeze_pi_before"]["live_pi_nloc"],
            self.world["freeze_pi_after_nloc"],
        )

    def test_fo_competence_grows_in_two_domains(self):
        world = self.world
        self.assertGreater(world["g2_delta_bytes"], 0)
        self.assertGreater(world["l1_delta_bytes"], 0)
        self.assertEqual(world["fo_delta_bytes"], world["g2_delta_bytes"] + world["l1_delta_bytes"])
        self.assertTrue(world["fo_competence_grew"])
        self.assertTrue(world["macro_live_after_both_admits"])
        self.assertTrue(world["l1_live_after_both_admits"])
        self.assertTrue(world["two_domains_in_fo_state"])
        self.assertIn(world["macro_atom_id"], world["live_procedure_atoms_after_both"])
        self.assertIn(world["l1"]["atom_id"], world["live_procedure_atoms_after_both"])
        self.assertTrue(world["l1"]["held_out_invoked"])
        self.assertTrue(world["l1"]["reset_has_no_construction"])

    def test_same_pi_across_domains_without_forked_planner(self):
        world = self.world
        self.assertTrue(world["same_runtime_class"])
        self.assertEqual(world["g2_runtime_class"], "ocm.runtime.ocm_runtime.OCMRuntime")
        self.assertEqual(world["l1_runtime_class"], world["g2_runtime_class"])
        self.assertFalse(world["planner_fork_scan"]["domain_forked_planner"])
        self.assertTrue(world["planner_fork_scan"]["unique_production_planner"])
        self.assertEqual(
            world["planner_fork_scan"]["production_planner_paths"],
            ["src/ocm/dialogue/planner.py"],
        )
        self.assertEqual(world["language_pi_use"]["domain"], "language_construction")
        self.assertEqual(world["polynomial_pi_use"]["domain"], "polynomial_procedure")
        self.assertTrue(world["used_across_two_domains_without_forked_planner"])

    def test_terminal_is_micro_scope_not_programme_close(self):
        self.assertEqual(self.result["terminal"], "PI_REMAINS_SMALL_AT_MICRO_SCOPE")
        self.assertEqual(self.result["programme_terminal"], "COMPACT_VESSEL_PARTIAL")
        self.assertEqual(self.disk["terminal"], "PI_REMAINS_SMALL_AT_MICRO_SCOPE")
        self.assertFalse(self.result["production_code_deleted"])
        self.assertIn("MINIMUM_SELF_EXTENDING_VESSEL", self.result["not_issued"])
        self.assertIn("MINIMUM_SELF_EXTENDING_VESSEL_SUPPORTED_AT_SCOPE", self.result["not_issued"])
        self.assertIn("PI_REMAINS_SMALL", self.result["not_issued"])
        self.assertIn("PI_SMALL_DOMAIN_GENERAL", self.result["not_issued"])
        self.assertEqual(self.result["architecture_rules_empirical"]["PI_SMALL_DOMAIN_GENERAL"], "PARTIAL")
        self.assertEqual(
            self.result["architecture_rules_empirical"]["PI_SMALL_DOMAIN_GENERAL_MICRO_SCOPE"],
            "PI_REMAINS_SMALL_AT_MICRO_SCOPE",
        )
        self.assertEqual(
            self.result["architecture_boxes"]["pi_small_domain_general"]["programme_status"],
            "PARTIAL",
        )
        self.assertFalse(
            self.result["architecture_boxes"]["competence_in_fo_state"]["predominantly_across_three_domains"]
        )
        self.assertEqual(self.result["G1_1_6_duplicate_cores"], "NOT_THIS_TASK_CITED_SINGLE_CORE_AT_SCOPE")

    def test_parents_cited_not_overwritten(self):
        parents = self.result["parents"]
        self.assertTrue(parents["g1-controller-growth-v1"]["present"])
        self.assertTrue(parents["g1-fo-competence-v2"]["present"])
        self.assertTrue(parents["g1-duplicate-cores-v1"]["present"])
        self.assertEqual(parents["g1-controller-growth-v1"]["terminal"], "COMPACT_VESSEL_PARTIAL")
        self.assertEqual(parents["g1-fo-competence-v2"]["terminal"], "COMPETENCE_IN_FO_STATE_AT_MICRO_SCOPE")
        self.assertEqual(parents["g1-duplicate-cores-v1"]["terminal"], "SINGLE_CORE_AT_SCOPE")
        unchanged = self.world["parent_result_sha256_unchanged"]
        self.assertTrue(unchanged["g1-controller-growth-v1"])
        self.assertTrue(unchanged["g1-fo-competence-v2"])
        self.assertTrue(unchanged["g1-duplicate-cores-v1"])
        self.assertEqual(
            E.sha256_file(E.PARENT_GROWTH),
            parents["g1-controller-growth-v1"]["sha256"],
        )
        self.assertEqual(
            E.sha256_file(E.PARENT_FO),
            parents["g1-fo-competence-v2"]["sha256"],
        )
        self.assertEqual(
            E.sha256_file(E.PARENT_CORES),
            parents["g1-duplicate-cores-v1"]["sha256"],
        )

    def test_src_custody(self):
        self.assertTrue(self.result["src_custody"]["git_diff_src_clean"])

    def test_capsule_result_matches_run(self):
        self.assertEqual(self.disk["schema"], E.SCHEMA)
        self.assertEqual(self.disk["salt"], E.SALT)
        self.assertEqual(self.disk["terminal"], self.result["terminal"])
        self.assertEqual(self.disk["programme_terminal"], "COMPACT_VESSEL_PARTIAL")


if __name__ == "__main__":
    unittest.main()
