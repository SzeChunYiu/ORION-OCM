"""Tests for P0 zero-prior closure."""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("p0", str(HERE / "p0_zero_prior_closure_v1.py"))
MOD = importlib.util.module_from_spec(SPEC)
sys.modules["p0"] = MOD
SPEC.loader.exec_module(MOD)


class TestP0(unittest.TestCase):
    def test_tick(self):
        out = MOD.run()
        self.assertTrue(out["tick"])
        self.assertEqual(out["n_open_blocking"], 0)
        self.assertGreaterEqual(out["n_closed_exact"], 5)
        self.assertEqual(json.loads((HERE / "RECEIPT_V1.json").read_text()), out)


if __name__ == "__main__":
    unittest.main()
