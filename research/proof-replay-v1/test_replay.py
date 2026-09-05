"""Content, missing-tool and actual runtime controls; real Lean runs in the required CI job."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import replay


class ReplayTests(unittest.TestCase):
    def test_exact_source_custody(self):
        self.assertEqual(len(replay.custody()["files"]), 3)

    def test_each_modified_source_refused(self):
        for name in ("Foundation.lean", "Composition.lean", "verify_lean.py", "MANIFEST.json"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                for source in replay.HERE.iterdir():
                    if source.is_file():
                        shutil.copyfile(source, root / source.name)
                with (root / name).open("ab") as stream:
                    stream.write(b"\n-- unbound change\n")
                with self.assertRaises(ValueError):
                    replay.custody(root)

    def test_missing_source_cannot_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(OSError):
                replay.custody(Path(tmp))

    def test_source_symlink_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "MANIFEST.json").symlink_to(replay.HERE / "MANIFEST.json")
            with self.assertRaises(ValueError):
                replay.custody(root)

    def test_unrelated_ancestor_symlink_is_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "checkout"
            link.symlink_to(replay.HERE, target_is_directory=True)
            self.assertEqual(replay.custody(link), replay.custody())

    def test_wrong_archive_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "not-the-release"
            archive.write_bytes(b"not a Lean distribution")
            with self.assertRaises(ValueError):
                replay.archive_identity(archive, replay.custody())

    def test_missing_archive_is_not_a_successful_proof(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "receipt.json"
            proc = subprocess.run([sys.executable, "-I", str(replay.HERE / "replay.py"),
                                   "--archive", str(Path(tmp) / "missing"), "--out", str(out)],
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
            self.assertEqual(json.loads(proc.stdout)["terminal"], "CANNOT_CHECK")
            self.assertFalse(out.exists())

    def test_existing_receipt_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "receipt.json"
            out.write_text("historical receipt")
            proc = subprocess.run([sys.executable, str(replay.HERE / "replay.py"),
                                   "--archive", "missing", "--out", str(out)],
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, 1)
            self.assertEqual(out.read_text(), "historical receipt")

    def test_actual_runtime_lifecycle(self):
        cells = replay.runtime_lifecycle(replay.custody(), replay.HERE.parents[1])
        self.assertEqual(len(cells), 7)
        self.assertEqual(cells["alternate-run-preserved"], "LIVE")
        self.assertEqual(cells["revoked-run-evidence"], "DEAD")
        self.assertEqual(cells["kernel-does-not-create-correspondence"], "UNKNOWN")

    def test_changed_runtime_source_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "src/ocm/kso/warrant.py"
            source.parent.mkdir(parents=True)
            source.write_text("raise RuntimeError('must not execute modified source')")
            with self.assertRaisesRegex(ValueError, "warrant source"):
                replay.runtime_lifecycle(replay.custody(), root)


if __name__ == "__main__":
    unittest.main()
