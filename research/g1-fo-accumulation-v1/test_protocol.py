"""G1 F/O accumulation protocol. Production src is imported, not edited."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import experiment as E

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PROTECTED = (
    REPO / "research" / "g1-controller-growth-v1" / "RESULT.json",
    REPO / "research" / "g1-fo-competence-v2" / "RESULT.json",
    REPO / "research" / "g1-pi-small-v1" / "RESULT.json",
    REPO / "research" / "g1-duplicate-cores-v1" / "RESULT.json",
)


class TestG1FOAccumulationProtocol(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protected_before = {
            str(path): E.sha256_file(path) if path.is_file() and E.git_tracked(path) else None
            for path in PROTECTED
        }
        capsule = HERE / "RESULT.json"
        cls.frozen_before = capsule.read_text(encoding="utf-8") if capsule.is_file() else None
        with tempfile.TemporaryDirectory() as tmp:
            cls.result = E.main(Path(tmp) / "RESULT.json")
        cls.frozen_after = capsule.read_text(encoding="utf-8") if capsule.is_file() else None
        cls.disk = json.loads(capsule.read_text(encoding="utf-8"))
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

    def test_pi_nloc_constant(self):
        world = self.world
        self.assertTrue(world["pi_nloc_constant"])
        cmp_ = world["controller_compare"]
        self.assertTrue(cmp_["all_nloc_constant"])
        self.assertTrue(cmp_["all_byte_identical"])
        self.assertFalse(cmp_["any_grew"])
        self.assertEqual(cmp_["nloc_before"], cmp_["nloc_after"])
        for row in cmp_["files"]:
            self.assertEqual(row["nloc_before"], row["nloc_after"], row["path"])
            self.assertEqual(row["sha256_before"], row["sha256_after"], row["path"])
            self.assertFalse(row["grew"], row["path"])
            self.assertEqual(E.nloc_path(REPO / row["path"]), row["nloc_after"])
        self.assertEqual(
            world["freeze_pi_before"]["live_nloc"],
            world["freeze_pi_after_nloc"],
        )
        self.assertTrue(world["freeze_pi_compare"]["all_nloc_constant"])

    def test_ledger_fo_bytes_grow_across_g2_and_l1(self):
        world = self.world
        self.assertGreater(world["g2_delta_bytes"], 0)
        self.assertGreater(world["l1_delta_bytes"], 0)
        self.assertEqual(world["fo_delta_bytes"], world["g2_delta_bytes"] + world["l1_delta_bytes"])
        self.assertTrue(world["fo_bytes_grew"])
        self.assertTrue(world["macro_live_after_both_admits"])
        self.assertTrue(world["l1_live_after_both_admits"])
        self.assertTrue(world["two_domains_in_fo_state"])
        self.assertIn(world["macro_atom_id"], world["live_procedure_atoms_after_both"])
        self.assertIn(world["l1"]["atom_id"], world["live_procedure_atoms_after_both"])
        self.assertTrue(world["l1"]["held_out_invoked"])
        self.assertTrue(world["l1"]["reset_has_no_construction"])
        self.assertTrue(world["authored_fo_nloc_constant"])
        self.assertEqual(world["freeze_f_nloc_before"], world["freeze_f_nloc_after"])
        self.assertEqual(world["freeze_o_nloc_before"], world["freeze_o_nloc_after"])

    def test_terminal_follows_pi_constant_and_fo_growth(self):
        world = self.world
        if world["pi_nloc_constant"] and world["fo_bytes_grew"] and world["two_domains_in_fo_state"]:
            expected = "FO_ACCUMULATION_AT_MICRO_SCOPE"
        elif not world["pi_nloc_constant"]:
            expected = "CONTROLLER_GREW_AT_SCOPE"
        elif not world["two_domains_in_fo_state"]:
            expected = "FO_ACCUMULATION_INCOMPLETE_AT_SCOPE"
        else:
            expected = "NO_FO_BYTE_GROWTH_AT_SCOPE"
        self.assertEqual(self.result["terminal"], expected)
        self.assertEqual(self.disk["terminal"], expected)
        self.assertEqual(self.result["programme_terminal"], "COMPACT_VESSEL_PARTIAL")
        self.assertFalse(self.result["production_code_deleted"])
        self.assertIn("MINIMUM_SELF_EXTENDING_VESSEL", self.result["not_issued"])
        self.assertIn("MINIMUM_SELF_EXTENDING_VESSEL_SUPPORTED_AT_SCOPE", self.result["not_issued"])
        self.assertNotEqual(self.result["terminal"], "MINIMUM_SELF_EXTENDING_VESSEL")
        self.assertEqual(
            self.result["architecture_rules_empirical"]["INTELLIGENCE_IN_F_AND_O_PROGRAMME"],
            "PARTIAL",
        )
        box = self.result["architecture_boxes"]["intelligence_in_f_and_o"]
        self.assertEqual(box["text"], E.BOX_TEXT)
        self.assertEqual(box["programme_status"], "PARTIAL")

    def test_fo_competence_and_pi_small_cited_if_present(self):
        parents = self.result["parents"]
        fo = parents["g1-fo-competence-v2"]
        self.assertTrue(fo["present"])
        self.assertTrue(fo["git_tracked"])
        self.assertEqual(fo["terminal"], "COMPETENCE_IN_FO_STATE_AT_MICRO_SCOPE")
        self.assertTrue(fo["not_rewritten"])
        pi_small = parents["g1-pi-small-v1"]
        if pi_small["present"]:
            self.assertTrue(pi_small["git_tracked"])
            self.assertEqual(pi_small["terminal"], "PI_REMAINS_SMALL_AT_MICRO_SCOPE")
            self.assertTrue(pi_small["not_rewritten"])
        else:
            self.assertFalse(pi_small["git_tracked"])
            self.assertFalse((E.PARENT_PI_SMALL).is_file() and E.git_tracked(E.PARENT_PI_SMALL))
        growth = parents["g1-controller-growth-v1"]
        cores = parents["g1-duplicate-cores-v1"]
        self.assertTrue(growth["present"])
        self.assertEqual(growth["terminal"], "COMPACT_VESSEL_PARTIAL")
        self.assertTrue(cores["present"])
        self.assertEqual(cores["terminal"], "SINGLE_CORE_AT_SCOPE")
        unchanged = self.world["parent_result_sha256_unchanged"]
        self.assertTrue(unchanged["g1-controller-growth-v1"])
        self.assertTrue(unchanged["g1-fo-competence-v2"])
        self.assertTrue(unchanged["g1-duplicate-cores-v1"])
        self.assertTrue(unchanged["g1-pi-small-v1"])

    def test_protected_result_files_not_overwritten(self):
        after = {
            str(path): E.sha256_file(path) if path.is_file() and E.git_tracked(path) else None
            for path in PROTECTED
        }
        self.assertEqual(after, self.protected_before)
        g132 = self.result["G1_checkboxes"]["G1.3"][0]
        self.assertEqual(g132["id"], "G1.3.2")
        self.assertEqual(g132["status"], "CITED_FROM_G1_FO_COMPETENCE_V2")
        self.assertFalse(g132["predominantly_across_three_domains"])

    def test_src_custody(self):
        self.assertTrue(self.result["src_custody"]["git_diff_src_clean"])
        self.assertFalse(self.result["src_custody"]["deleted"])

    def test_capsule_result_matches_run(self):
        self.assertIsNotNone(self.frozen_before)
        self.assertEqual(self.frozen_before, self.frozen_after)
        self.assertEqual(self.disk["schema"], E.SCHEMA)
        self.assertEqual(self.disk["salt"], E.SALT)
        self.assertEqual(self.disk["terminal"], self.result["terminal"])
        self.assertEqual(self.disk["gate"], "INTELLIGENCE_IN_F_AND_O")
        self.assertEqual(self.disk["programme_terminal"], "COMPACT_VESSEL_PARTIAL")


if __name__ == "__main__":
    unittest.main()
