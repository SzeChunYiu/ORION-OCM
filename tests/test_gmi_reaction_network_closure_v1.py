"""Repository gates for Issue #602 reaction-network closure."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


BUNDLE = Path(__file__).resolve().parents[1] / "research" / "gmi-reaction-network-closure-v1"
SPEC = importlib.util.spec_from_file_location(
    "reaction_network_closure_v1", BUNDLE / "reaction_network_closure_v1.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_exact_generator_compiler_family() -> None:
    result = MODULE.exhaustive_generator_certificate()
    assert result["systems"] == 54
    assert result["state_rows"] == 243
    assert result["compiler_mismatches"] == 0
    assert result["generator_violations"] == 0


def test_all_three_reaction_tasks_close() -> None:
    result = MODULE.validate_closure()
    assert result["ledger_rows"] == 3
    assert result["resource_coordinates"] == 16
