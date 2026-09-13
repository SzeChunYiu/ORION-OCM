import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from source_contract_v1 import HERE, retained_inputs

ACTIVE = HERE.parent / "machine-intelligence-morphogenesis-v1/gmi_microscope/b6_dense_consumer_scan.py"


class ActiveScannerTests(unittest.TestCase):
    def test_actual_active_adapter_and_live_source_drift(self):
        files = retained_inputs()
        name = next(n for n in files if n.startswith("pr551/STAGE_B6_DEV_"))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); inputs = root / "inputs"; inputs.mkdir()
            (inputs / Path(name).name).write_bytes(files[name])
            positive = subprocess.run([sys.executable, "-I", "-B", str(ACTIVE), str(inputs)],
                                      capture_output=True, text=True)
            self.assertEqual((positive.returncode, positive.stderr), (0, ""))
            self.assertEqual(json.loads(positive.stdout)["status"], "COMPLETE_SELECTED_FIELD_INSPECTION")
            research = root / "research"
            unit = research / HERE.name; shutil.copytree(HERE, unit)
            native = research / "machine-intelligence-morphogenesis-v1/gmi_microscope"
            native.mkdir(parents=True)
            shutil.copy2(ACTIVE, native / ACTIVE.name)
            for f in ("vm.py", "morph.py"):
                shutil.copy2(HERE / "raw/native" / f, native / f)
            (native / "vm.py").write_bytes((native / "vm.py").read_bytes() + b"\n")
            failed = subprocess.run([sys.executable, "-I", "-B", str(native / ACTIVE.name), str(inputs)],
                                    capture_output=True, text=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("live native source drift", failed.stderr)

    def test_missing_cli_directory_returns_unknown_not_success(self):
        result = subprocess.run([sys.executable, "-I", "-B", str(ACTIVE),
                                "/this/explicitly/nonexistent/retained/path"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "INPUT_UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()
