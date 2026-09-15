"""Repository gates for Issue #602 analog-semantics closure."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


BUNDLE = Path(__file__).resolve().parents[1] / "research" / "gmi-analog-semantics-closure-v1"
SPEC = importlib.util.spec_from_file_location(
    "analog_semantics_closure_v1", BUNDLE / "analog_semantics_closure_v1.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_exact_sampled_analog_compiler() -> None:
    result = MODULE.exhaustive_sampled_certificate()
    assert result["cases"] == 162
    assert result["mismatches"] == 0
    assert result["invalid_intervals"] == 0


def test_only_two_earned_analog_tasks_close() -> None:
    result = MODULE.validate_closure()
    assert result["ledger_rows"] == 2
    assert result["accounting_coordinates"] == 23
