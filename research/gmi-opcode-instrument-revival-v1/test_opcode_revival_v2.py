"""Portable static replay tests; never repeat a registered measurement cell."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import test_opcode_revival_v1 as historical


class PortableOpcodeRevivalTests(historical.OpcodeRevivalTests):
    def test_exact_receipt_replay_when_exact_version(self):
        if tuple(sys.version_info[:3]) != (3, 13, 12):
            self.skipTest("native receipt replay needs the recorded CPython 3.13.12")
        from opcode_audit_v2 import audit
        self.assertEqual(audit(), json.loads((HERE / "OPCODE_REVIVAL_RECEIPT_V2.json").read_text()))

    def test_static_replay_after_relocation(self):
        if tuple(sys.version_info[:3]) != (3, 13, 12):
            self.skipTest("native relocated replay needs the recorded CPython 3.13.12")
        with tempfile.TemporaryDirectory() as tmp:
            copied = Path(tmp) / "relocated"
            shutil.copytree(HERE, copied, ignore=shutil.ignore_patterns("__pycache__"))
            result = subprocess.run([sys.executable, "-I", "-B",
                                     str(copied / "opcode_audit_v2.py")],
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout),
                             json.loads((HERE / "OPCODE_REVIVAL_RECEIPT_V2.json").read_text()))


if __name__ == "__main__":
    unittest.main()
