"""Tests for P1 predictive domain closure."""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("p1", str(HERE / "p1_predictive_domain_v1.py"))
MOD = importlib.util.module_from_spec(SPEC)
sys.modules["p1"] = MOD
SPEC.loader.exec_module(MOD)


class TestP1(unittest.TestCase):
    def test_green(self):
        out = MOD.run()
        self.assertTrue(out["all_p1_boxes_green"])
        self.assertEqual(out["forms"], ["IQL", "LMHM", "RQM", "SCDI", "VGSC", "VRQM"])
        self.assertEqual(json.loads((HERE / "RECEIPT_V1.json").read_text()), out)


if __name__ == "__main__":
    unittest.main()
