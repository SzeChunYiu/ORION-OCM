"""Tests for P3 transfer/energy."""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("p3", str(HERE / "p3_transfer_energy_v1.py"))
MOD = importlib.util.module_from_spec(SPEC)
sys.modules["p3"] = MOD
SPEC.loader.exec_module(MOD)


class TestP3(unittest.TestCase):
    def test_green(self):
        out = MOD.run()
        self.assertTrue(out["all_p3_boxes_green"])
        self.assertEqual(out["n_transfer_arms"], 4)
        self.assertIn("energy", out["meters"])
        self.assertEqual(json.loads((HERE / "RECEIPT_V1.json").read_text()), out)


if __name__ == "__main__":
    unittest.main()
