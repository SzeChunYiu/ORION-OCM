"""G1.1.6 duplicate-core protocol. Production src is imported, not copied or deleted."""
from __future__ import annotations

import ast
import json
import tempfile
import unittest
from pathlib import Path

import experiment as E
import ocm.runtime as runtime_pkg
from ocm.language import field_bridge
from ocm.operators.registry import OperatorSpec
from ocm.runtime import ocm_runtime as live_mod
from ocm.runtime import state as custody_mod
from ocm.science import lifecycle
from ocm.work.contracts import Operator as WorkOperator


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
FREEZE = REPO / "research" / "g1-vessel-freeze-v1"


class TestG1DuplicateCores(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            cls.probe = E.run_shared_core_probe(Path(tmp))
        with tempfile.TemporaryDirectory() as tmp:
            cls.result = E.main(Path(tmp) / "RESULT.json")
        cls.disk = json.loads((HERE / "RESULT.json").read_text())

    def test_live_runtime_is_not_package_export(self):
        self.assertIs(field_bridge.OCMRuntime, live_mod.OCMRuntime)
        self.assertIs(lifecycle.OCMRuntime, live_mod.OCMRuntime)
        self.assertIs(runtime_pkg.OCMRuntime, custody_mod.OCMRuntime)
        self.assertIsNot(live_mod.OCMRuntime, custody_mod.OCMRuntime)
        self.assertIsNot(WorkOperator, OperatorSpec)

    def test_three_domains_write_one_field(self):
        probe = self.probe
        self.assertTrue(probe["shared_one_core"])
        self.assertTrue(probe["F"]["same_knowledge_space_object"])
        self.assertTrue(probe["F"]["same_evidence_registry_object"])
        self.assertTrue(probe["O"]["same_operator_registry_object"])
        self.assertTrue(probe["F"]["language_representation_in_ks"])
        self.assertTrue(probe["F"]["math_conclusion_in_evidence"])
        self.assertTrue(probe["F"]["procedural_demo_in_evidence"])
        self.assertTrue(probe["F"]["science_ledger_is_adapter_on_same_runtime"])
        self.assertTrue(probe["F"]["reopen_shares_all_three"])
        self.assertTrue(probe["O"]["work_operator_apply_does_not_write_ks"])
        self.assertEqual(probe["math"]["kernel_verdict"], "PASS")

    def test_cross_domain_revoke_uses_one_C(self):
        c = self.probe["C"]
        self.assertNotEqual(c["language_liveness_after_utterance_revoke"], "LIVE")
        self.assertEqual(c["math_liveness_after_language_revoke"], "LIVE")
        self.assertEqual(c["procedural_liveness_after_language_revoke"], "LIVE")
        self.assertTrue(c["independent_warrants_survive_cross_domain_revoke"])
        self.assertTrue(c["commit_authority_host_injected_not_constructed"])

    def test_domain_packages_do_not_define_core_classes(self):
        for scan in self.result["domain_scans"]:
            self.assertEqual(scan["core_class_defs"], [], scan["package"])
        forks = [c for c in self.result["classified_constructors"] if c["live_second_core"]]
        self.assertEqual(forks, [])
        kinds = {c["kind"] for c in self.result["classified_constructors"]}
        self.assertTrue(kinds <= {"SHARED_RUNTIME_ENTRY", "SHARED_RUNTIME_REOPEN"})

    def test_lookalikes_classified_none_live_second_core(self):
        items = self.result["lookalikes"]
        self.assertGreaterEqual(len(items), 6)
        self.assertFalse(any(x["live_second_core"] for x in items))
        ids = {x["id"] for x in items}
        self.assertIn("M0_RUNTIME_NAME_COLLISION", ids)
        self.assertIn("WORK_OPERATOR_PARALLEL_SCHEMA", ids)
        self.assertIn("MEANINGGRAPH_COMPACT_VIEW", ids)

    def test_no_production_deletion(self):
        self.assertFalse(self.result["production_code_deleted"])
        self.assertTrue((REPO / "src" / "ocm" / "runtime" / "state.py").is_file())
        self.assertTrue((REPO / "src" / "ocm" / "work" / "contracts.py").is_file())
        src = (HERE / "experiment.py").read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and E._call_name(node) in {"unlink", "rmtree", "remove"}:
                self.fail(f"experiment deletes files at line {node.lineno}")
        self.assertNotIn("shutil.rmtree", src)
        self.assertNotIn("os.remove", src)

    def test_terminal_and_g1_1_6_honesty(self):
        self.assertEqual(self.result["terminal"], "SINGLE_CORE_AT_SCOPE")
        self.assertEqual(self.disk["terminal"], "SINGLE_CORE_AT_SCOPE")
        g = self.result["G1_1_6"]
        self.assertTrue(g["can_be_honestly_checked"])
        self.assertFalse(g["can_be_honestly_earned_as_deletion"])
        self.assertEqual(g["status"], "NOT_EARNED_AS_DELETION")
        self.assertTrue(self.result["all_three_domains_share_one_core"])
        self.assertIn("CURRENT_KSO_PARENT_SUFFICIENT", self.result["not_issued"])
        self.assertIn("DOMAIN_CORE_FORK_REQUIRED", self.result["not_issued"])

    def test_freeze_parent_not_overwritten(self):
        parent = self.result["parent_freeze"]
        self.assertTrue(parent["present"])
        self.assertTrue(parent["not_overwritten"])
        self.assertEqual(parent["freeze_G1_1_6_status"], "NOT_EARNED")
        self.assertEqual(parent["freeze_terminal"], "COMPACT_VESSEL_PARTIAL")
        frozen = json.loads((FREEZE / "DUPLICATE_CORES.json").read_text())
        self.assertEqual(E.sha256_file(FREEZE / "DUPLICATE_CORES.json"), parent["duplicate_cores_sha256"])
        self.assertEqual(frozen["elimination_checkbox"], "NOT_EARNED_AS_DELETION")
        self.assertFalse(frozen["production_code_deleted"])

    def test_capsule_result_matches_run(self):
        self.assertEqual(self.disk["schema"], E.SCHEMA)
        self.assertEqual(self.disk["salt"], E.SALT)
        self.assertEqual(self.disk["terminal"], self.result["terminal"])
        self.assertEqual(self.disk["G1_1_6"]["can_be_honestly_checked"], True)


if __name__ == "__main__":
    unittest.main()
