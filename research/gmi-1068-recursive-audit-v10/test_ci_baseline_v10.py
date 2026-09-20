"""Real-history regression for inherited closure versus new promotion."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SELECT = load("baseline", HERE / "select_ci_baseline.py")
GATE = load("gate", ROOT / "research/gmi-1068-recursive-audit-v3/gate.py")
V8 = "research/gmi-1068-recursive-audit-v8/SCOPE_SNAPSHOT_V8.json"
V9 = "research/gmi-1068-recursive-audit-v9/SCOPE_SNAPSHOT_V9.json"
V10 = "research/gmi-1068-recursive-audit-v10/SCOPE_SNAPSHOT_V10.json"
H = "32d5ae32776af16cdae1f20904e4f1cd0a0a1c16"
I = "1de456db6f87ab7e33d0f0af919c90ffa54b8b85"
NEW = ["research/gmi-1068-resource-threshold-v10/threshold_v10.py"]


class BaselineTests(unittest.TestCase):
    def test_existing_round_uses_target_current(self):
        raw, path = SELECT.select_baseline(ROOT, I, V9, V8)
        self.assertEqual(path, V9)
        self.assertEqual(raw, (ROOT / V9).read_bytes())
        current = json.loads((ROOT / V9).read_text())
        GATE.validate_baseline(current, json.loads(raw), NEW)
        # The former workflow fails on these real, unchanged round artifacts.
        with self.assertRaisesRegex(ValueError, "STATUS_ONLY_PROMOTION:R0"):
            GATE.validate_baseline(current, json.loads((ROOT / V8).read_text()), NEW)

    def test_introduction_preserves_promotion_guard(self):
        raw, path = SELECT.select_baseline(ROOT, H, V9, V8)
        self.assertEqual(path, V8)
        current = json.loads((ROOT / V9).read_text())
        with self.assertRaisesRegex(ValueError, "STATUS_ONLY_PROMOTION:R0"):
            GATE.validate_baseline(current, json.loads(raw), NEW)
        touched = GATE.validate_baseline(current, json.loads(raw),
            ["research/gmi-1068-r0-foundation-repair-v9/r0_audit_v9.py"])
        self.assertIn("R0", touched)

    def test_v10_introduction_uses_unchanged_v9(self):
        raw, path = SELECT.select_baseline(ROOT, I, V10, V9)
        self.assertEqual(path, V9)
        current = json.loads((ROOT / V10).read_text())
        GATE.validate_baseline(current, json.loads(raw), NEW)

    def test_missing_evidence_never_silently_falls_back(self):
        with self.assertRaises(SELECT.CannotCheck):
            SELECT.select_baseline(ROOT, "0" * 40, V9, V8)
        with self.assertRaises(SELECT.CannotCheck):
            SELECT.select_baseline(ROOT, H, "missing-current", "missing-predecessor")
        with self.assertRaises(ValueError):
            SELECT.select_baseline(ROOT, I, "research/gmi-1068-r0-foundation-repair-v9/RESULT_V9.json", V8)
        for base, code in (("0" * 40, 2), ("bad-ref", 1)):
            result = subprocess.run([sys.executable, str(HERE / "select_ci_baseline.py"),
                "--repo", str(ROOT), "--base-sha", base, "--current", V9,
                "--predecessor", V8, "--output", "/tmp/never-created-baseline-v10.json"],
                capture_output=True)
            self.assertEqual(result.returncode, code)


if __name__ == "__main__":
    unittest.main()
