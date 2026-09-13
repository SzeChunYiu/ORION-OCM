import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from custody_v1 import replay, verify
from check_v1 import run


class CustodyTests(unittest.TestCase):
    def copy_unit(self, directory):
        dst = Path(directory) / "copy"
        shutil.copytree(HERE, dst)
        return dst

    def test_real_complete_receipt_no_alarm(self):
        self.assertEqual(replay(), run())

    def test_actual_bound_sources_match(self):
        binding = json.loads((HERE / "raw/SOURCE_BINDINGS_V1.json").read_text())
        self.assertEqual(len(binding["complete_delta_paths"]), 5)
        self.assertEqual(len(binding["first_parent_commits"]), 5)
        self.assertTrue(binding["preregistration_precedes_result_ancestry"])
        for row in binding["records"]:
            raw = (HERE / row["path"]).read_bytes()
            self.assertEqual(len(raw), row["bytes"])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row["sha256"])

    def test_changed_transitive_raw_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_unit(tmp)
            path = root / "raw/tip/STAGE_FRESH_ECOLOGY_CAPABILITY_V1.json"
            path.write_bytes(path.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "payload differs"):
                verify(root)

    def test_extra_missing_and_symlink_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_unit(tmp)
            extra = root / ".unexpected"
            extra.write_text("extra")
            with self.assertRaisesRegex(ValueError, "membership"):
                verify(root)
            extra.unlink()
            path = root / "CORE.md"
            content = path.read_bytes()
            path.unlink()
            with self.assertRaisesRegex(ValueError, "membership"):
                verify(root)
            elsewhere = Path(tmp) / "source"
            elsewhere.write_bytes(content)
            path.symlink_to(elsewhere)
            with self.assertRaisesRegex(ValueError, "symlink"):
                verify(root)

    def test_worker_cannot_rebind_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_unit(tmp)
            expected = json.loads((root / "RECEIPT_V1.json").read_text())
            def mutate():
                path = root / "CORE.md"
                path.write_bytes(path.read_bytes() + b"\nchanged\n")
                manifest = root / "MANIFEST_V1.json"
                data = json.loads(manifest.read_text())
                raw = path.read_bytes()
                data["files"]["CORE.md"] = {"bytes": len(raw),
                    "sha256": hashlib.sha256(raw).hexdigest()}
                manifest.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
                return expected
            with self.assertRaisesRegex(ValueError, "manifest changed"):
                replay(mutate, root)


if __name__ == "__main__":
    unittest.main()
