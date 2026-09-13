import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import custody_v1 as c

def rebind(root):
    files = {}
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.name != "MANIFEST_V1.json":
            data = p.read_bytes()
            files[str(p.relative_to(root))] = dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    (root / "MANIFEST_V1.json").write_bytes(c.encoded({"files": files}))

class CustodyTests(unittest.TestCase):
    def fixture(self, tmp):
        root = Path(tmp) / "unit"
        root.mkdir()
        (root / "CORE.md").write_text("bound content")
        (root / "RECEIPT_V1.json").write_bytes(c.encoded({"value": 1, "nested": {"all": [1, 2]}}))
        rebind(root)
        return root

    def test_complete_bound_fixture_no_alarm_and_hidden_member_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(tmp)
            c.verify(root)
            (root / ".unlisted").write_text("extra")
            with self.assertRaises(ValueError):
                c.verify(root)

    def test_symlink_cannot_substitute_a_bound_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(tmp)
            original = root / "CORE.md"
            target = Path(tmp) / "same-bytes"
            target.write_bytes(original.read_bytes())
            original.unlink()
            original.symlink_to(target)
            with self.assertRaises(ValueError):
                c.verify(root)

    def test_other_root_refuses_before_worker(self):
        with tempfile.TemporaryDirectory() as tmp, patch("check_v1.run") as run:
            with self.assertRaisesRegex(ValueError, "source root"):
                c.replay(Path(tmp))
            run.assert_not_called()

    def test_worker_cannot_rebind_changed_content_and_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(tmp)
            payload = json.loads((root / "RECEIPT_V1.json").read_text())
            def hostile():
                (root / "CORE.md").write_text("mutated")
                rebind(root)
                return payload
            with patch.object(c, "HERE", root), patch("check_v1.run", side_effect=hostile):
                with self.assertRaisesRegex(ValueError, "manifest changed"):
                    c.replay(root)

    def test_complete_payload_no_alarm_and_nested_field_change_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(tmp)
            payload = json.loads((root / "RECEIPT_V1.json").read_text())
            with patch.object(c, "HERE", root), patch("check_v1.run", return_value=payload):
                self.assertEqual(c.replay(root), (root / "RECEIPT_V1.json").read_bytes())
            payload["nested"]["all"].pop()
            with patch.object(c, "HERE", root), patch("check_v1.run", return_value=payload):
                with self.assertRaisesRegex(ValueError, "complete payload"):
                    c.replay(root)

if __name__ == "__main__":
    unittest.main()
