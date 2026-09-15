"""Repository gates for Issue #602 relational/sheaf closure."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


BUNDLE = Path(__file__).resolve().parents[1] / "research" / "gmi-relational-sheaf-closure-v1"
SPEC = importlib.util.spec_from_file_location(
    "relational_sheaf_closure_v1", BUNDLE / "relational_sheaf_closure_v1.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_existing_sheaf_receipt_is_exact_and_intact() -> None:
    result = MODULE.validate_receipt()
    assert result["table_equalities"] == 22
    assert result["search_equalities"] == 22
    assert result["negative_twin_separations"] == 22


def test_only_seven_earned_relational_tasks_close() -> None:
    assert MODULE.validate_closure()["ledger_rows"] == 7
