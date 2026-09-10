"""G1 hostile work-operator Π protocol.

Load THIS capsule's experiment.py by path. unittest discover plus a naive
insert-if-absent would promote research/g5-packed-field-v1/experiment.py and
plant_world would disappear.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SRC = REPO / "src"


def _prefer(path: Path) -> None:
    p = str(path)
    while p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)


_prefer(SRC)
_prefer(HERE)

_spec = importlib.util.spec_from_file_location("g1_hostile_pi_experiment", HERE / "experiment.py")
E = importlib.util.module_from_spec(_spec)
assert _spec is not None and _spec.loader is not None
sys.modules["g1_hostile_pi_experiment"] = E
sys.modules["experiment"] = E
_spec.loader.exec_module(E)
# experiment.py inserts src at [0] for standalone runs; this capsule must stay first.
_prefer(HERE)


class TestImportIsolation(unittest.TestCase):
    def test_experiment_is_this_capsule(self):
        self.assertEqual(Path(E.__file__).resolve(), HERE / "experiment.py")
        self.assertEqual(sys.path[0], str(HERE))
        self.assertTrue(hasattr(E, "plant_world"))
        self.assertTrue(hasattr(E, "hostile_work_pi_lookup"))
        self.assertEqual(E.HOSTILE_MARKER, "HOSTILE_PI_WORK_OPERATOR_V1")
        self.assertIn("spec_from_file_location", Path(__file__).read_text(encoding="utf-8"))


class TestG1HostilePiProtocol(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen_before = (HERE / "RESULT.json").read_text(encoding="utf-8") if (HERE / "RESULT.json").is_file() else None
        with tempfile.TemporaryDirectory(prefix="g1-hostile-pi-test-") as tmp:
            cls.result = E.main(Path(tmp) / "RESULT.json")
        cls.frozen_after = (HERE / "RESULT.json").read_text(encoding="utf-8") if (HERE / "RESULT.json").is_file() else None
        cls.disk = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
        cls.world = cls.result["microworld"]

    def test_frozen_result_not_rewritten_by_test_run(self):
        self.assertIsNotNone(self.frozen_before)
        self.assertEqual(self.frozen_before, self.frozen_after)
        self.assertEqual(self.disk["schema"], E.SCHEMA)
        self.assertEqual(self.disk["salt"], E.SALT)
        self.assertEqual(self.disk["terminal"], self.result["terminal"])
        self.assertEqual(self.disk["programme_terminal"], "COMPACT_VESSEL_PARTIAL")

    def test_methods_blob_pinned(self):
        self.assertEqual(E.METHOD_BLOB, "50323a33418b8ef8bb6500ddeba4b9d1f795e9e3")
        self.assertEqual(E.git_blob_sha1(E.METHODS), E.METHOD_BLOB)
        self.assertEqual(self.result["methods_blob"], E.METHOD_BLOB)
        self.assertEqual(self.disk["methods_blob"], E.METHOD_BLOB)

    def test_plant_world_is_this_capsule(self):
        tasks = E.plant_world()
        self.assertEqual(len(tasks), E.PLANTED_N)
        self.assertEqual([t.initial_state["case_id"] for t in tasks], [f"A{i}" for i in range(E.PLANTED_N)])
        self.assertEqual(len(self.world["hostile"]["hostile_tasks"]), E.PLANTED_N)

    def test_hostile_solves_and_is_absent_from_mechanism(self):
        hostile = self.world["hostile"]
        self.assertTrue(hostile["hostile_solves_all_table_tasks"])
        self.assertEqual(hostile["marker"], E.HOSTILE_MARKER)
        self.assertLessEqual(hostile["hostile_function_nloc"], 10)
        self.assertTrue(hostile["hostile_absent_from_mechanism_arm"])
        self.assertIn(E.HOSTILE_MARKER, (HERE / "experiment.py").read_text(encoding="utf-8"))
        self.assertNotIn(E.HOSTILE_MARKER, (REPO / "src" / "ocm" / "work" / "envs.py").read_text(encoding="utf-8"))
        for path, row in hostile["mechanism_contains_hostile"].items():
            self.assertFalse(row["marker"], path)
            self.assertFalse(row["function_name"], path)
        g133 = self.result["G1_checkboxes"]["G1.3"][0]
        g134 = self.result["G1_checkboxes"]["G1.3"][1]
        self.assertEqual(g133["id"], "G1.3.3")
        self.assertEqual(g133["status"], "EARNED")
        self.assertEqual(g134["id"], "G1.3.4")
        self.assertEqual(g134["status"], "EARNED")

    def test_parent_mechanism_solves_without_calling_hostile(self):
        mech = self.world["mechanism"]
        self.assertTrue(mech["solves_all_planted_tasks"])
        self.assertEqual(mech["hostile_calls"], 0)
        self.assertEqual(mech["skeleton"], list(E.ROLES))
        for row in mech["rows"]:
            self.assertTrue(row["success"], row)
            self.assertTrue(row["action_matches"], row)
        self.assertGreater(self.world["hostile"]["hostile_calls_probe"], 0)

    def test_fo_admission_and_controller_nloc(self):
        world = self.world
        cmp_ = world["controller_compare"]
        self.assertTrue(cmp_["all_nloc_constant"])
        self.assertTrue(cmp_["all_byte_identical"])
        self.assertFalse(cmp_["any_grew"])
        self.assertGreater(world["g2_delta_bytes"], 0)
        self.assertGreater(world["work_delta_bytes"], 0)
        self.assertTrue(world["fo_competence_grew"])
        self.assertTrue(world["macro_live_after_both_admits"])
        self.assertTrue(world["work_skill_live_after_both_admits"])
        self.assertTrue(world["same_runtime_class"])
        self.assertIn(world["macro_atom_id"], world["live_procedure_atoms_after_both"])
        self.assertIn(world["work_skill"]["atom_id"], world["live_procedure_atoms_after_both"])

    def test_terminal_is_legal_and_does_not_close_programme(self):
        self.assertIn(self.result["terminal"], E.LEGAL_TERMINALS)
        self.assertEqual(self.result["programme_terminal"], "COMPACT_VESSEL_PARTIAL")
        self.assertEqual(self.disk["terminal"], self.result["terminal"])
        self.assertFalse(self.result["production_code_deleted"])
        self.assertIn("MINIMUM_SELF_EXTENDING_VESSEL", self.result["not_issued"])
        self.assertIn("MINIMUM_SELF_EXTENDING_VESSEL_SUPPORTED", self.result["not_issued"])
        self.assertIn("PI_REMAINS_SMALL", self.result["not_issued"])
        self.assertIn("PI_SMALL_DOMAIN_GENERAL", self.result["not_issued"])
        self.assertIn("G1_1_6_DELETION", self.result["not_issued"])
        self.assertEqual(self.result["architecture_rules_empirical"]["PI_SMALL_DOMAIN_GENERAL"], "PARTIAL")
        self.assertEqual(self.result["G1_1_6_duplicate_cores"], "NOT_THIS_TASK")
        self.assertNotEqual(self.result["terminal"], "MINIMUM_SELF_EXTENDING_VESSEL_SUPPORTED")
        if self.result["terminal"] == "PARENT_SUFFICIENT":
            self.assertTrue(self.result["architecture_rules_empirical"]["PARENT_SUFFICIENT_WITHOUT_HOSTILE"])

    def test_parents_cited_not_overwritten(self):
        parents = self.result["parents"]
        self.assertTrue(parents["g1-pi-small-v1"]["present"])
        self.assertTrue(parents["g1-fo-competence-v2"]["present"])
        self.assertTrue(parents["g1-controller-growth-v1"]["present"])
        self.assertEqual(parents["g1-pi-small-v1"]["terminal"], "PI_REMAINS_SMALL_AT_MICRO_SCOPE")
        self.assertEqual(parents["g1-fo-competence-v2"]["terminal"], "COMPETENCE_IN_FO_STATE_AT_MICRO_SCOPE")
        self.assertEqual(parents["g1-controller-growth-v1"]["terminal"], "COMPACT_VESSEL_PARTIAL")
        unchanged = self.world["parent_result_sha256_unchanged"]
        self.assertTrue(unchanged["g1-pi-small-v1"])
        self.assertTrue(unchanged["g1-fo-competence-v2"])
        self.assertTrue(unchanged["g1-controller-growth-v1"])
        self.assertEqual(E.sha256_file(E.PARENT_PI), parents["g1-pi-small-v1"]["sha256"])
        self.assertEqual(E.sha256_file(E.PARENT_FO), parents["g1-fo-competence-v2"]["sha256"])
        self.assertEqual(E.sha256_file(E.PARENT_GROWTH), parents["g1-controller-growth-v1"]["sha256"])

    def test_src_custody(self):
        self.assertTrue(self.result["src_custody"]["git_diff_src_clean"])
        diff = __import__("subprocess").run(
            ["git", "diff", "--exit-code", "--", "src"],
            cwd=REPO,
            capture_output=True,
            text=True,
        )
        self.assertEqual(diff.returncode, 0)


if __name__ == "__main__":
    unittest.main()
