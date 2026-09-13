from pathlib import Path
import hashlib
import json
import tempfile
import unittest
from unittest.mock import patch
from custody_v1 import replay, verify


class CustodyTests(unittest.TestCase):
    def test_alternate_root_refused_before_worker(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("check_v1.run") as worker:
                with self.assertRaisesRegex(ValueError, "imported source root"):
                    replay(Path(directory))
                worker.assert_not_called()

    def test_full_membership_no_alarm_and_hostile_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "control").write_bytes(b"bound")
            manifest = {"files": {"control": {"bytes": 5, "sha256": hashlib.sha256(b"bound").hexdigest()}}}
            (root / "MANIFEST_V1.json").write_text(json.dumps(manifest))
            self.assertTrue(verify(root))
            (root / ".extra").write_bytes(b"hidden")
            with self.assertRaises(ValueError):
                verify(root)
            (root / ".extra").unlink()
            (root / "control").unlink()
            (root / "control").symlink_to(root / "MANIFEST_V1.json")
            with self.assertRaises(ValueError):
                verify(root)
            (root / "control").unlink()
            (root / "control").write_bytes(b"wrong")
            with self.assertRaises(ValueError):
                verify(root)


if __name__ == "__main__":
    unittest.main()
