"""Repository gates for Issue #602 population-heredity closure."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


BUNDLE = Path(__file__).resolve().parents[1] / "research" / "gmi-population-heredity-closure-v1"
SPEC = importlib.util.spec_from_file_location(
    "population_heredity_closure_v1", BUNDLE / "population_heredity_closure_v1.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_exact_price_law_has_no_violations() -> None:
    certificate = MODULE.exhaustive_price_certificate()
    assert certificate["cases"] == 2187
    assert certificate["violations"] == 0


def test_diversity_regime_and_parent_reduction() -> None:
    certificate = MODULE.option_value_certificate()
    assert certificate["conclusion"] == "SUPPORT_TWO_NECESSARY_AND_SUFFICIENT; D7_D8_PARENT_EXACT"
    assert all(row["parent_exact"] for row in certificate["rows"])


def test_all_four_population_tasks_close() -> None:
    assert MODULE.validate_closure()["ledger_rows"] == 4
