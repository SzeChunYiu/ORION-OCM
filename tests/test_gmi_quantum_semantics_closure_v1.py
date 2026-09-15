"""Repository gates for Issue #602 quantum-semantics closure."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


BUNDLE = Path(__file__).resolve().parents[1] / "research" / "gmi-quantum-semantics-closure-v1"
SPEC = importlib.util.spec_from_file_location(
    "quantum_semantics_closure_v1", BUNDLE / "quantum_semantics_closure_v1.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_exact_quantum_classical_compiler() -> None:
    result = MODULE.exhaustive_semantics_certificate()
    assert result["trajectories"] == 155
    assert result["compiler_mismatches"] == 0
    assert result["trace_violations"] == 0
    assert result["measurement_violations"] == 0


def test_only_three_earned_quantum_tasks_close() -> None:
    assert MODULE.validate_closure()["ledger_rows"] == 3
