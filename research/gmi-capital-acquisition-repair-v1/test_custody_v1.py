import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import custody_v1 as C


class CustodyTests(unittest.TestCase):
    def copy(self, destination):
        root = Path(destination) / "unit"
        shutil.copytree(C.HERE, root)
        return root

    def test_actual_no_alarm_full_membership(self):
        original, receipt = C.verify()
        self.assertTrue(original)
        self.assertEqual(C.finite_json(receipt)["status"], "PASS")

    def test_missing_modified_extra_and_symlink_refuse(self):
        for mode in ("missing", "modified", "extra", "symlink"):
            with tempfile.TemporaryDirectory() as d:
                root = self.copy(d)
                p = root / "CORE.md"
                if mode == "missing":
                    p.unlink()
                elif mode == "modified":
                    p.write_text("changed")
                elif mode == "extra":
                    (root / "unbound.txt").write_text("extra")
                else:
                    p.unlink()
                    p.symlink_to(C.HERE / "CORE.md")
                with self.assertRaises(ValueError):
                    C.verify(root)

    def test_alternate_root_refuses_before_worker(self):
        calls = []
        with tempfile.TemporaryDirectory() as d:
            root = self.copy(d)
            with self.assertRaises(ValueError):
                C.replay(root, worker=lambda: calls.append(True))
        self.assertEqual(calls, [])

    def test_worker_cannot_rebind_changed_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            root = self.copy(d)
            receipt = (root / C.RECEIPT).read_bytes()
            def worker():
                p = root / "CORE.md"
                p.write_text("mutated and rebound")
                m = json.loads((root / C.MANIFEST).read_bytes())
                m["files"]["CORE.md"] = {"bytes": p.stat().st_size,
                    "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                (root / C.MANIFEST).write_text(json.dumps(m))
                return receipt
            with patch.object(C, "HERE", root):
                with self.assertRaisesRegex(ValueError, "manifest changed"):
                    C.replay(root, worker)

    def test_complete_payload_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError, "payload"):
            C.replay(worker=lambda: b'{"status":"PASS"}\n')

    def test_finite_json_rejects_duplicate_and_overflow(self):
        for text in ('{"x":1,"x":2}', '{"x":1e999}', '{"x":NaN}'):
            with self.assertRaises(ValueError):
                C.finite_json(text)


if __name__ == "__main__":
    unittest.main()
