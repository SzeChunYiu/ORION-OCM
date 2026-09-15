"""Tests for #602 J3 burden disposition. CPython 3.8+."""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("j3", str(HERE / "j3_quantum_burden_v1.py"))
MOD = importlib.util.module_from_spec(SPEC)
sys.modules["j3"] = MOD
SPEC.loader.exec_module(MOD)


class TestAnalog(unittest.TestCase):
    def test_no_separation(self):
        a = MOD.analog_assay()
        self.assertFalse(a["separation_identified"])
        self.assertEqual(a["material_positive_gaps"], 0)
        self.assertTrue(a["box_tick"])


class TestQuantum(unittest.TestCase):
    def test_no_unexplained_frontier(self):
        q = MOD.quantum_assay()
        self.assertEqual(q["unexplained_frontier_count"], 0)
        self.assertFalse(q["frontier_not_explainable_by_known_parents"])
        self.assertTrue(q["box_tick"])
        self.assertEqual(q["n_obligations_tested"], 9)


class TestReceipt(unittest.TestCase):
    def test_terminal_and_identity(self):
        out = MOD.run()
        self.assertTrue(out["all_j3_remaining_boxes_green"])
        self.assertEqual(out["terminal"], MOD.TERMINAL)
        committed = json.loads((HERE / "RECEIPT_V1.json").read_text())
        self.assertEqual(
            json.dumps(committed, sort_keys=True),
            json.dumps(out, sort_keys=True),
        )


if __name__ == "__main__":
    unittest.main()
