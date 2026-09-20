#!/usr/bin/env python3
"""Adversarial integrity checks; these do not adjudicate scientific claims."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
spec = importlib.util.spec_from_file_location("scope_gate", HERE / "gate.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def seal(snapshot):
    for name in gate.NODES:
        row = snapshot["rounds"][name]
        row["parent_bindings"] = {p: snapshot["rounds"][p]["evidence_digest"] for p in gate.DAG[name]}
        row["evidence_digest"] = gate.evidence_digest(row)


class ScopeGateTests(unittest.TestCase):
    def setUp(self):
        self.s = json.loads((HERE / "SCOPE_SNAPSHOT_V3.json").read_text())

    def reject(self, token, snapshot=None):
        with self.assertRaisesRegex(ValueError, token):
            gate.validate(self.s if snapshot is None else snapshot, REPO)

    def witness(self):
        artifact = next(a for a in self.s["rounds"]["R0"]["artifacts"] if a["path"].endswith("ATOMIC_CHECKLIST_V1.json"))
        return dict(artifact, kind="json_pointer", locator="/schema")

    def close_r0_fixture(self):
        # Synthetic shape-valid closure demonstrates the trust boundary, not a
        # scientific adjudication: a locator may exist without proving a claim.
        row = self.s["rounds"]["R0"]
        row["status"] = "EARNED"
        for atom in row["obligations"]:
            atom["status"] = "CLOSED"
            atom["evidence"] = [self.witness()]
        seal(self.s)

    def test_current_snapshot_has_no_global_certificate(self):
        result = gate.validate(self.s, REPO)
        self.assertEqual(result["registered_atoms"], 222)
        self.assertEqual(result["earned_rounds"], [])
        self.assertEqual(result["overall_closure"], "OPEN")
        self.assertIn("R17", result["stale_closure"])

    def test_forged_evidence_string(self):
        self.s["rounds"]["R0"]["artifacts"] = ["forged"]
        self.reject("ARTIFACT_SCHEMA")

    def test_missing_evidence_file(self):
        self.s["rounds"]["R0"]["artifacts"][0]["path"] = "does-not-exist.json"
        self.reject("MISSING_OR_EXTERNAL_FILE")

    def test_changed_evidence_hash(self):
        self.s["rounds"]["R0"]["artifacts"][0]["sha256"] = "0" * 64
        self.reject("ARTIFACT_DRIFT")

    def test_deleted_graph_edges(self):
        self.s["dependencies"] = {n: [] for n in gate.NODES}
        self.reject("CANONICAL_DAG_DRIFT")

    def test_all_round_promotion_with_unresolved_atoms(self):
        for row in self.s["rounds"].values():
            row["status"] = "EARNED"
        seal(self.s)
        self.reject("EARNED_WITH_UNRESOLVED_ATOM")

    def test_closed_atom_without_evidence(self):
        self.s["rounds"]["R0"]["obligations"][0]["status"] = "CLOSED"
        self.reject("CLOSED_WITHOUT_WITNESS")

    def test_removed_atomic_obligation(self):
        self.s["rounds"]["R4"]["obligations"].pop()
        seal(self.s)
        self.reject("ATOMIC_COVERAGE:R4")

    def test_forged_witness_string(self):
        self.s["rounds"]["R0"]["obligations"][0]["evidence"] = ["forged"]
        self.reject("WITNESS_SCHEMA")

    def test_unbound_witness(self):
        witness = self.witness()
        witness["sha256"] = "0" * 64
        self.s["rounds"]["R0"]["obligations"][0]["evidence"] = [witness]
        self.reject("UNBOUND_WITNESS")

    def test_nonexistent_locator(self):
        witness = self.witness()
        witness["locator"] = "/made_up_claim"
        self.s["rounds"]["R0"]["obligations"][0]["evidence"] = [witness]
        self.reject("MISSING_WITNESS_LOCATOR")

    def test_changed_parent_receipt(self):
        row = self.s["rounds"]["R0"]
        row["scope"] += " changed scope"
        row["evidence_digest"] = gate.evidence_digest(row)
        self.reject("PARENT_EVIDENCE_DRIFT:R1:R0")

    def test_stale_parent_prevents_reearning(self):
        row = self.s["rounds"]["R6"]
        artifact = next(a for a in row["artifacts"] if a["path"].endswith("RESULT_V1.json"))
        for atom in row["obligations"]:
            atom["status"] = "CLOSED"
            atom["evidence"] = [dict(artifact, kind="json_pointer", locator="/schema")]
        row["status"] = "EARNED"
        seal(self.s)
        self.reject("EARNED_WITH_UNEARNED_PARENT:R6")

    def test_global_promotion(self):
        self.s["overall_closure"] = "EARNED"
        self.reject("GLOBAL_PROMOTION_FORBIDDEN")

    def test_unknown_top_level_claim(self):
        self.s["all_known_intelligence_derived"] = True
        self.reject("SNAPSHOT_FIELDS")

    def test_outside_evidence_path(self):
        self.s["rounds"]["R0"]["artifacts"][0]["path"] = "../outside"
        self.reject("UNSAFE_PATH")

    def test_r0_actual_name_inference(self):
        self.assertEqual(gate.infer_rounds([
            "research/gmi-1068-grand-unified-v2-r0/THEORY_DAG_V1.json",
            ".github/workflows/gmi-1068-r5-successor-v2.yml",
        ]), {"R0", "R5"})

    def test_status_only_promotion_against_baseline(self):
        baseline = copy.deepcopy(self.s)
        self.close_r0_fixture()
        gate.validate(self.s, REPO)
        with self.assertRaisesRegex(ValueError, "STATUS_ONLY_PROMOTION:R0"):
            gate.validate_baseline(self.s, baseline, [])
        self.assertEqual(gate.validate_baseline(self.s, baseline, [
            "research/gmi-1068-grand-unified-v2-r0/RESULT_V1.json"
        ]), ["R0"])

    def test_missing_baseline_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            changes = Path(temp) / "changed.txt"
            changes.write_text("")
            result = subprocess.run([
                sys.executable, str(HERE / "gate.py"), "--baseline", str(Path(temp) / "missing.json"),
                "--changed-files", str(changes),
            ], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SCOPE_GATE_RED", result.stderr)

    def test_baseline_and_changes_cannot_be_omitted_individually(self):
        result = subprocess.run([
            sys.executable, str(HERE / "gate.py"), "--baseline", "missing.json",
        ], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("BASELINE_AND_CHANGED_FILES_REQUIRED_TOGETHER", result.stderr)

    def test_local_repair_does_not_reearn_round(self):
        row = self.s["rounds"]["R0"]
        row["local_repairs"] = [{"id": "fixture", "scope": "locator integrity only",
                                 "status": "LOCAL_VERIFIED", "evidence": [self.witness()]}]
        seal(self.s)
        self.assertEqual(gate.validate(self.s, REPO)["earned_rounds"], [])

    def test_changed_parent_requires_descendant_review(self):
        self.close_r0_fixture()
        row = self.s["rounds"]["R1"]
        artifact = next(a for a in row["artifacts"] if a["path"].endswith("RESULT_V1.json"))
        row["status"] = "EARNED"
        for atom in row["obligations"]:
            atom["status"] = "CLOSED"
            atom["evidence"] = [dict(artifact, kind="json_pointer", locator="/schema")]
        seal(self.s)
        gate.validate(self.s, REPO)
        baseline = copy.deepcopy(self.s)
        self.s["rounds"]["R0"]["scope"] += " revised"
        seal(self.s)
        gate.validate(self.s, REPO)
        with self.assertRaisesRegex(ValueError, "CHANGED_PARENT_WITHOUT_DESCENDANT_REVIEW:R1"):
            gate.validate_baseline(self.s, baseline, ["research/gmi-1068-grand-unified-v2-r0/RESULT_V1.json"])

    def test_empty_baseline_cannot_disable_custody(self):
        result = subprocess.run([
            sys.executable, str(HERE / "gate.py"), "--baseline", "",
        ], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("EMPTY_BASELINE_FORBIDDEN", result.stderr)

    def test_cli_requires_explicit_custody_mode(self):
        result = subprocess.run([sys.executable, str(HERE / "gate.py")], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)

    def test_broken_python_or_lean_locator_rejected(self):
        row = self.s["rounds"]["R1"]
        artifact = next(a for a in row["artifacts"] if a["path"].endswith(".lean"))
        row["obligations"][0]["evidence"] = [dict(artifact, kind="lean_declaration", locator="nonexistent_theorem")]
        self.reject("MISSING_WITNESS_LOCATOR")


if __name__ == "__main__":
    unittest.main()
