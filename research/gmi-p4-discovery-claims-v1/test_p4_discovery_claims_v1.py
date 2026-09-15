"""Tests for P4 discovery claims."""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("p4", str(HERE / "p4_discovery_claims_v1.py"))
MOD = importlib.util.module_from_spec(SPEC)
sys.modules["p4"] = MOD
SPEC.loader.exec_module(MOD)


class TestP4(unittest.TestCase):
    def test_green(self):
        out = MOD.run()
        self.assertTrue(out["all_p4_boxes_green"])
        self.assertEqual(len(out["boxes"]), 4)
        self.assertEqual(json.loads((HERE / "RECEIPT_V1.json").read_text()), out)


if __name__ == "__main__":
    unittest.main()
