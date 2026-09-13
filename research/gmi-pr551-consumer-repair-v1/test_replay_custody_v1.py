import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from replay_v1 import HERE, replay, verify


class ReplayCustodyTests(unittest.TestCase):
    def packet(self, root):
        (root / "CORE.md").write_text("bound\n")
        (root / "REPAIR_RECEIPT_V1.json").write_bytes(b"{}\n")
        (root / "check_consumer_repair_v1.py").write_text("# mocked only\n")
        rows = {p.name: {"bytes": len(p.read_bytes()), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                for p in root.iterdir()}
        (root / "MANIFEST_V1.json").write_text(json.dumps({"files": rows}))

    def test_mock_no_alarm_and_self_consistent_rebinding_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); self.packet(root)
            def worker(*args, **kwargs):
                return subprocess.CompletedProcess(args, 0, b"{}\n", b"")
            self.assertEqual(replay(root, worker), b"{}\n")
            def hostile(*args, **kwargs):
                (root / "CORE.md").write_text("changed\n")
                path = root / "MANIFEST_V1.json"; manifest = json.loads(path.read_text())
                raw = (root / "CORE.md").read_bytes()
                manifest["files"]["CORE.md"] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
                path.write_text(json.dumps(manifest))
                return worker()
            with self.assertRaisesRegex(ValueError, "changed manifest"):
                replay(root, hostile)

    def test_missing_extra_and_symlink_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); self.packet(root)
            (root / "extra").write_text("x")
            with self.assertRaises(ValueError): verify(root)
            (root / "extra").unlink()
            data = (root / "CORE.md").read_bytes(); (root / "CORE.md").unlink()
            with self.assertRaises(ValueError): verify(root)
            (root / "CORE.md").symlink_to(root / "REPAIR_RECEIPT_V1.json")
            with self.assertRaises(ValueError): verify(root)


if __name__ == "__main__":
    unittest.main()
