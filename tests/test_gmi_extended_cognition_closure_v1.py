"""Repository-level gates for Issue #602 body-environment closure."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


BUNDLE = Path(__file__).resolve().parents[1] / "research" / "gmi-extended-cognition-closure-v1"
SPEC = importlib.util.spec_from_file_location(
    "extended_cognition_closure_v1", BUNDLE / "extended_cognition_closure_v1.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_external_state_collision_and_matched_parent() -> None:
    minimality = MODULE.minimality_certificate()
    reduction = MODULE.reduction_certificate()
    assert minimality["same_agent_projection"]
    assert minimality["different_required_future_outputs"]
    assert reduction["protected_answers_equal"]


def test_exact_delayed_bit_predictions() -> None:
    result = MODULE.validate_prediction()
    assert result["extended_capability"] == 1.0
    assert result["agent_only_zero_bit_upper_bound"] == 0.5
    assert result["erase_write_negative_twin_capability"] == 0.5
    assert result["one_bit_internal_memory_parent_capability"] == 1.0


def test_all_four_extended_cognition_tasks_close() -> None:
    assert MODULE.validate_closure()["ledger_rows"] == 4
