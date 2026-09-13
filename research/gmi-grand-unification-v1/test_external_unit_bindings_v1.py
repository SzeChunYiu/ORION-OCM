"""Complete-unit controls use the actual frozen FQC packet, never toy-only maps."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
HELPER = HERE / "external_unit_bindings_v1.py"
BIND = {"__file__": str(HELPER)}
exec(compile(HELPER.read_bytes(), str(HELPER), "exec"), BIND)
UNIT = "research/gmi-finite-quantum-cover-v1"
MANIFEST_SHA = "6f9d3ee193e7da7918bee85bde75e1579b60fa0faeb0a0ab7a8b40364c604a1c"


class ExternalUnitBindingTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repository = Path(tmp.name)
        self.unit = self.repository / UNIT
        shutil.copytree(HERE.parent.parent / UNIT, self.unit)
        self.record = {"manifest": "MANIFEST.json", "sha256": MANIFEST_SHA}

    def verify(self):
        return BIND["verify_unit"](self.repository, UNIT, self.record)

    def manifest(self, change):
        p = self.unit / "MANIFEST.json"
        data = json.loads(p.read_text())
        change(data)
        raw = json.dumps(data).encode()
        p.write_bytes(raw)
        self.record["sha256"] = hashlib.sha256(raw).hexdigest()

    def test_actual_frozen_complete_packet_has_no_alarm(self):
        self.assertEqual(self.verify(), {"manifest_sha256": MANIFEST_SHA,
                                       "payload_files": 23, "payload_bytes": 101887})

    def test_changed_transitive_raw_parent_is_rejected(self):
        p = self.unit / "raw/QUANTUM_PROCESS_INSTANTIATION_THEOREM_V1.md"
        p.write_bytes(p.read_bytes() + b"\nUnreviewed theorem change.\n")
        with self.assertRaisesRegex(ValueError, "content changed"):
            self.verify()

    def test_missing_transitive_log_is_rejected(self):
        (self.unit / "raw/validation/tests-normal.log").unlink()
        with self.assertRaisesRegex(ValueError, "membership changed"):
            self.verify()

    def test_extra_hidden_file_is_rejected(self):
        (self.unit / ".unregistered").write_text("outside the frozen map")
        with self.assertRaisesRegex(ValueError, "membership changed"):
            self.verify()

    def test_symlink_inside_unit_is_rejected(self):
        (self.unit / "linked").symlink_to(self.unit / "CORE.md")
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.verify()

    def test_symlink_in_ancestor_is_rejected(self):
        original = self.repository / "research"
        original.rename(self.repository / "payload")
        original.symlink_to(self.repository / "payload", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.verify()

    def test_fifo_rejected_before_any_read_can_block(self):
        os.mkfifo(self.unit / "pipe")
        with self.assertRaisesRegex(ValueError, "unsupported"):
            self.verify()

    def test_unreadable_directory_is_not_silently_omitted(self):
        opaque = self.unit / "opaque"
        opaque.mkdir()
        scandir = os.scandir
        def denied(path):
            if Path(path) == opaque:
                raise PermissionError("opaque directory")
            return scandir(path)
        with patch("os.scandir", side_effect=denied):
            with self.assertRaises(PermissionError):
                self.verify()

    def test_changed_manifest_cannot_be_laundered_by_unchanged_files(self):
        p = self.unit / "MANIFEST.json"
        p.write_bytes(p.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "manifest changed"):
            self.verify()

    def test_duplicate_manifest_keys_are_rejected(self):
        p = self.unit / "MANIFEST.json"
        raw = p.read_bytes().replace(b'"schema":', b'"schema": "shadow", "schema":', 1)
        p.write_bytes(raw)
        self.record["sha256"] = hashlib.sha256(raw).hexdigest()
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.verify()

    def test_nonfinite_constants_and_overflowing_exponents_are_rejected(self):
        for token in ("NaN", "Infinity", "-Infinity", "1e999"):
            with self.subTest(token=token), self.assertRaises(ValueError):
                BIND["strict_object"]('{"metadata": ' + token + '}')

    def test_boolean_size_and_wrong_payload_totals_are_rejected(self):
        for change in (lambda d: d["files"]["CORE.md"].update(bytes=True),
                       lambda d: d.update(payload_files=24),
                       lambda d: d.update(payload_bytes=0)):
            with self.subTest(change=change):
                original = (self.unit / "MANIFEST.json").read_bytes()
                self.manifest(change)
                with self.assertRaises(ValueError):
                    self.verify()
                (self.unit / "MANIFEST.json").write_bytes(original)
                self.record["sha256"] = hashlib.sha256(original).hexdigest()

    def test_dot_escape_absolute_and_noncanonical_paths_are_rejected(self):
        for name in (".", "..", "../elsewhere", "/tmp/unit", "./unit", "a//b", ""):
            with self.subTest(name=name), self.assertRaises(ValueError):
                BIND["local_name"](name)
        self.assertEqual(BIND["local_name"]("raw/validation"), Path("raw/validation"))


if __name__ == "__main__":
    unittest.main()
