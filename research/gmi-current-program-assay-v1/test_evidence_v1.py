from pathlib import Path
import copy
import hashlib
import json
import tempfile
import unittest
from unittest.mock import patch
import native_source_v1
from evidence_v1 import verify_manifest


class BindingTests(unittest.TestCase):
    def test_exact_original_source_and_changed_vm_refused(self):
        buffers = native_source_v1.source_bytes()
        self.assertEqual(hashlib.sha256(buffers["vm.py"]).hexdigest(),
                         "2e481d4f5a259b46ada8d74a8f78baf97142ba2193a7c9d8ab4e776d5ea1c1c8")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binding = json.loads((native_source_v1.HERE / "SOURCE_BINDINGS_V1.json").read_text())
            (root / "SOURCE_BINDINGS_V1.json").write_text(json.dumps(binding))
            for row in binding["files"]:
                dest = root / row["path"]
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((native_source_v1.HERE / row["path"]).read_bytes())
            with patch.object(native_source_v1, "HERE", root):
                self.assertEqual(native_source_v1.source_bytes(), buffers)
                p = root / "raw/native-df777cd7/vm.py"
                p.write_bytes(p.read_bytes() + b"\n")
                with self.assertRaises(ValueError):
                    native_source_v1.source_bytes()

    def test_full_membership_symlink_and_mutation_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "control").write_bytes(b"bound")
            manifest = {"files": {"control": {"bytes": 5, "sha256": hashlib.sha256(b"bound").hexdigest()}}}
            (root / "MANIFEST_V1.json").write_text(json.dumps(manifest))
            anchor = verify_manifest(root)
            self.assertTrue(anchor)
            (root / ".unlisted").write_text("additional member")
            with self.assertRaises(ValueError):
                verify_manifest(root)
            (root / ".unlisted").unlink()
            (root / "control").unlink()
            (root / "control").symlink_to(root / "MANIFEST_V1.json")
            with self.assertRaises(ValueError):
                verify_manifest(root)
            (root / "control").unlink()
            (root / "control").write_bytes(b"other")
            with self.assertRaises(ValueError):
                verify_manifest(root)


if __name__ == "__main__":
    unittest.main()
