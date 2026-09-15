"""Tests for V2 domain-basis closure."""
from __future__ import annotations
import importlib.util, json, sys, unittest
from pathlib import Path
HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("v2", str(HERE / "v2_domain_basis_closure_v1.py"))
MOD = importlib.util.module_from_spec(SPEC)
sys.modules["v2"] = MOD
SPEC.loader.exec_module(MOD)

class TestV2(unittest.TestCase):
    def test_green(self):
        out = MOD.run()
        self.assertTrue(out["all_v2_boxes_green"])
        self.assertEqual(out["terminal"], MOD.TERMINAL)
        self.assertEqual(out["n_domains"], 8)
        self.assertGreaterEqual(out["n_candidates"], 8)
        self.assertGreaterEqual(out["n_paradigms_screened"], 8)
        committed = json.loads((HERE / "RECEIPT_V1.json").read_text())
        self.assertEqual(committed, out)

if __name__ == "__main__":
    unittest.main()
