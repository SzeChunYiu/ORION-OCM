from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


BUNDLE = Path(__file__).resolve().parents[1] / "research" / "gmi-j2-bounded-completeness-v1"
SPEC = importlib.util.spec_from_file_location("j2_bounded_completeness_v1", BUNDLE / "j2_bounded_completeness_v1.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_bounded_completeness_census_and_claim_count():
    result = MODULE.validate_closure()
    assert result["ledger_rows"] == 11
    assert result["pairwise"]["pairs_with_failure"] == 22
    assert result["pairwise"]["complete_pairs"] == 6
    assert result["higher_order"]["higher_order_only"] == 62
