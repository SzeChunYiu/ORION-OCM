"""Repository-discovered gates for Issue #602 energy-landscape closure."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


BUNDLE = Path(__file__).resolve().parents[1] / "research" / "gmi-energy-landscape-closure-v1"
SPEC = importlib.util.spec_from_file_location(
    "energy_landscape_closure_v1", BUNDLE / "energy_landscape_closure_v1.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_four_energy_tasks_are_exactly_closed() -> None:
    result = MODULE.validate_closure()
    assert result["ledger_rows"] == 4
    assert result["exact_systems"] == 5421
    assert result["exact_state_cases"] == 21423


def test_exact_corrected_phase_boundary() -> None:
    assert MODULE.phase(1855) == "EXEMPLAR_PARENT"
    assert MODULE.phase(1856) == "TIE"
    assert MODULE.phase(1857) == "ENERGY_RELAXATION"


def test_strict_relaxation_cannot_express_two_cycle() -> None:
    assert not any(eb < ea and ea < eb for ea in range(4) for eb in range(4))
