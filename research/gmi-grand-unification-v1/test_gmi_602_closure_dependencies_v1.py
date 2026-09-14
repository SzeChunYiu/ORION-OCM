#!/usr/bin/env python3
"""Regression wrapper for the isolated #602 formal-closure validator."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parent
VALIDATOR = ROOT / "closure-602-v1" / "validate_gmi_602_closure_dependencies_v1.py"


class TestGMI602ClosureDependenciesV1(unittest.TestCase):
    def test_fail_closed_dependency_ledger(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=20,
            check=False,
        )
        self.assertEqual(
            proc.returncode,
            0,
            msg=f"validator failed\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}",
        )
        self.assertIn("GMI_602_CLOSURE_DEPENDENCY_LEDGER_VALID", proc.stdout)
        self.assertIn("complete_empirical_closure=NOT_EARNED", proc.stdout)


if __name__ == "__main__":
    unittest.main()
