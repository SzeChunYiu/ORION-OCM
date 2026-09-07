"""New authored capture packets through the unchanged qualified environment CLI.

This is development integration, not the historical 47-control replay or a
real-corpus run. Each invocation and both successful/failed packets are retained.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import unittest

RUNTIME = Path("/home/billy/orion-director-work/20260907/proof-environment-qualified-runtime-20260907-v1/runtime.json")
RUNTIME_SHA = "c9acc789908a216809a509facfc06c5aaf02206197fbc2f9f1531d3ae1c6d4e8"
PRIMITIVE = Path("/home/billy/orion-director-work/20260907/proof-environment-development/environment-controls-v4/composition/primitive.ndjson")
PRIMITIVE_SHA = "aee5ebb7190d92ca6b7e30d6c803f971c10ab6dc7c4e31d319ab1429262311c0"
PYTHON = "/home/billy/.local/share/uv/python/cpython-3.11.14-linux-x86_64-gnu/bin/python3.11"
ENTRY = "/home/billy/orion-director-work/20260907/ocm-proof-environment/research/proof-environment-v1/environment.py"


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()


def record(path):
    raw = path.read_bytes()
    return {"path": str(path.resolve()), "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


class PacketIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.captures = Path(os.environ["OCM_CAPTURE_RECORDS"])
        cls.out = Path(os.environ["OCM_PACKET_RECORDS"])
        cls.out.mkdir(parents=True, exist_ok=False)
        for path, expected in ((RUNTIME, RUNTIME_SHA), (PRIMITIVE, PRIMITIVE_SHA)):
            if record(path)["sha256"] != expected: raise ValueError("qualified input binding differs")
        (cls.out / "test-source.py").write_bytes(Path(__file__).read_bytes())
        (cls.out / "authorization.json").write_bytes(canonical({
            "scope": "NEW_AUTHORED_CAPTURE_PACKET_CONTROLS_ONLY", "runtime": record(RUNTIME),
            "primitive": record(PRIMITIVE), "python": record(Path(PYTHON)), "entry": record(Path(ENTRY)),
            "capture_records": str(cls.captures), "old47_rerun": False, "corpus_rows": 0}))

    def setUp(self):
        self.work = self.out / self._testMethodName
        self.work.mkdir()
        self.counter = 0

    def capture(self, name):
        hits = []
        for path in self.captures.glob("capture-*/out/association.json"):
            value = json.loads(path.read_bytes())
            if value["resolved_name"] == name: hits.append((path.parent, value))
        self.assertEqual(len(hits), 1, name)
        return hits[0]

    def invoke(self, freeze, expected, stage, reason=""):
        self.counter += 1
        base = self.work / str(self.counter)
        freeze_path = self.work / (str(self.counter) + "-freeze.json")
        freeze_path.write_bytes(canonical(freeze))
        argv = [PYTHON, "-I", "-S", ENTRY, freeze["operation"],
                "--freeze", str(freeze_path), "--freeze-sha256", record(freeze_path)["sha256"],
                "--runtime", str(RUNTIME), "--runtime-sha256", RUNTIME_SHA,
                "--output", str(base), "--timeout-s", "30", "--max-output-bytes", "1048576"]
        started = time.monotonic()
        proc = subprocess.run(argv, capture_output=True, check=False)
        (self.work / (str(self.counter) + "-stdout")).write_bytes(proc.stdout)
        (self.work / (str(self.counter) + "-stderr")).write_bytes(proc.stderr)
        (self.work / (str(self.counter) + "-process.json")).write_bytes(canonical({
            "argv": argv, "returncode": proc.returncode, "wall_s": time.monotonic() - started}))
        result_path = base / ("receipt.json" if freeze["operation"] == "prepare" else "check.json")
        result = json.loads(result_path.read_bytes())
        self.assertEqual(proc.returncode, 0 if expected in {"PREPARED", "KERNEL_PASS"} else 2, result)
        self.assertEqual(proc.stderr, b"", result)
        self.assertEqual(result["terminal"], expected, result)
        self.assertEqual(result["stage"], stage, result)
        self.assertIn(reason, result["reason"])
        self.assertEqual(result["native"]["terminal"], expected, result)
        return base, result

    def prepare(self, name, change=None, expected="PREPARED",
                stage="replay_and_independent_target", reason=""):
        capture, assoc = self.capture(name)
        policy = {"schema": "ocm.proof-environment.policy.v1", "target": name,
                  "target_root": assoc["goal"]["target_root"],
                  "target_level_params": assoc["goal"]["target_level_params"],
                  "roots": assoc["reference_dependencies"], "excluded": [name], "axioms": [],
                  "max_heartbeats": 1000000, "max_rec_depth": 4096}
        if change: change(policy, assoc)
        path = self.work / "policy.json"; path.write_bytes(canonical(policy))
        freeze = {"schema": "ocm.proof-environment.freeze.v1", "operation": "prepare", "inputs": {
            "source_packet": record(capture / "source.ndjson"), "policy": record(path),
            "registered_target_packet": record(capture / "goal.ndjson"), "primitive_packet": record(PRIMITIVE)}}
        base, result = self.invoke(freeze, expected, stage, reason)
        return base, result, capture, assoc

    def check(self, prepared, candidate=None, root=None, expected="KERNEL_PASS",
              stage="kernel_and_axioms", reason=""):
        base, result, capture, assoc = prepared
        freeze = {"schema": "ocm.proof-environment.freeze.v1", "operation": "check",
                  "prepared_receipt": record(base / "receipt.json"), "environment_id": result["environment_id"],
                  "candidate_packet": record(candidate or (capture / "reference.ndjson")),
                  "candidate_root": assoc["reference"]["target_root"] if root is None else root}
        return self.invoke(freeze, expected, stage, reason)

    def test_exposed_reference_support_is_replayed_and_checked(self):
        prepared = self.prepare("RenamedPublicScope.passage")
        self.assertIn("P2MW.S_authored.solution", prepared[1]["native"]["dependencies"])
        self.check(prepared)

    def test_ordered_universes_roundtrip(self):
        self.check(self.prepare("UniverseOrder.universes"))

    def test_changed_independent_goal_refuses(self):
        self.prepare("RenamedPublicScope.passage", lambda policy, _: policy.update(target_root=0),
                     "REJECTED", "independent_target_and_policy", "INDEPENDENT_TARGET_MISMATCH")

    def test_changed_universe_order_refuses(self):
        self.prepare("UniverseOrder.universes",
                     lambda policy, _: policy["target_level_params"].reverse(),
                     "REJECTED", "independent_target_and_policy", "INDEPENDENT_TARGET_MISMATCH")

    def test_unregistered_axiom_cannot_become_support(self):
        self.prepare("UnregisteredSupport.dependent", expected="REJECTED",
                     stage="closure_and_replay", reason="UNREGISTERED_AXIOM")

    def test_wrong_expression_type_is_kernel_rejected(self):
        prepared = self.prepare("RenamedPublicScope.passage")
        candidate = prepared[2] / "goal.ndjson"
        rows = [json.loads(line) for line in candidate.read_bytes().splitlines()]
        self.assertIn({"ie": 0, "sort": 0}, rows)
        self.check(prepared, candidate=candidate, root=0,
                   expected="REJECTED", stage="kernel", reason="declaration type mismatch")

    def test_candidate_declaration_packet_is_refused(self):
        prepared = self.prepare("RenamedPublicScope.passage")
        self.check(prepared, candidate=prepared[2] / "source.ndjson",
                   expected="CANNOT_CHECK", stage="candidate_packet", reason="CANDIDATE_DECLARATION")

    def test_original_target_constant_is_excluded(self):
        prepared = self.prepare("RenamedPublicScope.passage")
        _, _, capture, assoc = prepared
        raw = (capture / "reference.ndjson").read_bytes()
        rows = [json.loads(line) for line in raw.splitlines()]
        new_root = sum("ie" in row for row in rows)
        raw += canonical({"ie": new_root, "const": {
            "name": assoc["reference"]["target_name_index"], "us": []}})
        candidate = self.work / "target-constant.ndjson"; candidate.write_bytes(raw)
        self.check(prepared, candidate, new_root, "REJECTED",
                   "candidate_dependencies_and_kernel", "EXCLUDED_DEPENDENCY")


if __name__ == "__main__": unittest.main()
