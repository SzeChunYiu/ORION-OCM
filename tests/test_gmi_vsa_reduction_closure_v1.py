"""Repository gates for Issue #602 VSA reductions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


BUNDLE = Path(__file__).resolve().parents[1] / "research" / "gmi-vsa-reduction-closure-v1"
SPEC = importlib.util.spec_from_file_location(
    "vsa_reduction_closure_v1", BUNDLE / "vsa_reduction_closure_v1.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_hash_verified_vsa_receipt_and_scaling_law() -> None:
    assert MODULE.validate_receipt()["parent_equalities"] == 7
    assert MODULE.bundled_member_coordinate_accuracy(3) == 0.75
    assert MODULE.after_independent_bit_noise(0.75, 0.25) == 0.625


def test_only_five_earned_vsa_tasks_close() -> None:
    assert MODULE.validate_closure()["ledger_rows"] == 5
