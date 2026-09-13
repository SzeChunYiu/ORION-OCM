"""Custody execution seams are replaced: these tests never launch a measurement."""
from concurrent.futures import ThreadPoolExecutor
import json
import shutil
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import attempt_custody_v1 as c
from audit_custody_v1 import audit_attempt
from cross_envelope_v6 import collect
from frozen_contract_v1 import AuditError, canonical, sha, strict_json, write_new
from synthetic_fixture_v1 import packet
import sys


class CustodyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.registry = Path(self.temp.name) / "registry"
        self.calls = []

    def tearDown(self):
        self.temp.cleanup()

    def fake(self, command, stdout, stderr):
        self.calls.append(command)
        p = packet(command[command.index("--host-label") + 1])
        raw = (json.dumps(p, indent=2, sort_keys=True) + "\n").encode()
        Path(command[-1]).write_bytes(raw)
        stdout.write_bytes(raw); stderr.write_bytes(b"")
        return 0

    def make(self):
        with patch.object(c, "_invoke", self.fake):
            return c.run_attempt(self.registry, "synthetic-control")

    def test_complete_custody_and_content_positive(self):
        path = self.make()
        result = audit_attempt(path)
        self.assertEqual(result["status"], "CUSTODY_AND_CONTENT_PASS")
        self.assertTrue(result["valid"])
        self.assertEqual(len(self.calls), 1)

    def test_collision_no_invocation_no_byte_change(self):
        path = self.make()
        before = {str(p.relative_to(path)): p.read_bytes() for p in path.rglob("*") if p.is_file()}
        with patch.object(c, "_invoke", self.fake), self.assertRaises(FileExistsError):
            c.run_attempt(self.registry, "renamed-display-label")
        self.assertEqual(len(self.calls), 1)
        after = {str(p.relative_to(path)): p.read_bytes() for p in path.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_rehashed_display_alias_clone_cannot_count_as_replication(self):
        path = self.make()
        record = strict_json((path / "ATTEMPT.json").read_bytes())
        record["identity"]["display_alias"] = "same-attempt-other-label"
        duplicate = self.registry / sha(canonical(record["identity"]).encode())
        shutil.copytree(path, duplicate)
        raw = (json.dumps(record) + "\n").encode()
        (duplicate / "ATTEMPT.json").write_bytes(raw)
        result = strict_json((duplicate / "RESULT.json").read_bytes())
        result["attempt_sha256"] = sha(raw)
        (duplicate / "RESULT.json").write_text(json.dumps(result))
        self.assertEqual((path / "packet.json").read_bytes(), (duplicate / "packet.json").read_bytes())
        with self.assertRaises(AuditError):
            audit_attempt(duplicate)
        with self.assertRaises(AuditError):
            collect([path, duplicate], [str(Path(sys.executable).resolve())])
        self.assertEqual(len(self.calls), 1)

    def test_atomic_reservation_has_one_winner(self):
        def reserve(_):
            try:
                return str(c.reserve(self.registry, {"synthetic": "shared-key"}))
            except FileExistsError:
                return None
        with ThreadPoolExecutor(max_workers=4) as pool:
            rows = list(pool.map(reserve, range(8)))
        self.assertEqual(sum(r is not None for r in rows), 1)

    def test_failed_launch_remains_reserved(self):
        with patch.object(c, "_invoke", side_effect=OSError("synthetic launch failure")):
            path = c.run_attempt(self.registry, "synthetic-control")
        self.assertEqual(audit_attempt(path)["status"], "RETAINED_LAUNCH_FAILURE")
        with patch.object(c, "_invoke", self.fake), self.assertRaises(FileExistsError):
            c.run_attempt(self.registry, "synthetic-control")
        self.assertEqual(self.calls, [])

    def test_source_drift_before_invocation_retained(self):
        with patch.object(c, "_invoke", self.fake):
            path = c.run_attempt(self.registry, "synthetic-control", Path(self.temp.name) / "absent")
        self.assertEqual(audit_attempt(path)["status"], "RETAINED_LAUNCH_FAILURE")
        self.assertEqual(self.calls, [])

    def test_interrupted_launch_is_incomplete(self):
        with patch.object(c, "_invoke", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                c.run_attempt(self.registry, "synthetic-control")
        path = next(self.registry.iterdir())
        self.assertEqual(audit_attempt(path)["status"], "INCOMPLETE_RESERVED_ATTEMPT")
        with patch.object(c, "_invoke", self.fake), self.assertRaises(FileExistsError):
            c.run_attempt(self.registry, "synthetic-control")

    def test_macos_launch_refused_before_reservation(self):
        with patch.object(c.platform, "system", return_value="Darwin"), self.assertRaises(AuditError):
            c.run_attempt(self.registry, "synthetic-control")
        self.assertFalse(self.registry.exists())

    def test_changed_stdout_rejected(self):
        path = self.make()
        (path / "stdout.json").write_bytes(b"{}\n")
        with self.assertRaises(AuditError):
            audit_attempt(path)

    def test_rehashed_false_terminal_rejected_by_semantics(self):
        path = self.make()
        p = strict_json((path / "packet.json").read_bytes())
        p["terminal"] = "DERIVED_NEURAL_AT_REGISTERED_SCOPE"
        raw = (json.dumps(p) + "\n").encode()
        (path / "packet.json").write_bytes(raw); (path / "stdout.json").write_bytes(raw)
        r = strict_json((path / "RESULT.json").read_bytes())
        r["files"]["packet.json"] = r["files"]["stdout.json"] = sha(raw)
        (path / "RESULT.json").write_text(json.dumps(r))
        with self.assertRaises(AuditError):
            audit_attempt(path)

    def test_static_subprocess_cross_audit(self):
        path = self.make()
        result = collect([path], [str(Path(sys.executable).resolve())])
        self.assertEqual(result["cross_envelope_stability"], "SINGLE_ENVELOPE_NO_REPLICATION")
        self.assertFalse(result["replication_obligation_discharged"])

    def test_duplicate_attempt_cannot_be_replication(self):
        path = self.make()
        with self.assertRaises(AuditError):
            collect([path, path], [str(Path(sys.executable).resolve())])

    def test_missing_interpreter_is_unverifiable(self):
        path = self.make()
        result = collect([path], [])
        self.assertEqual(result["cross_envelope_stability"], "NO_VALID_ENVELOPE")
        self.assertEqual(next(iter(result["per_attempt"].values()))["status"], "UNVERIFIABLE")


if __name__ == "__main__":
    unittest.main()
