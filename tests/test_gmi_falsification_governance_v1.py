from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


BUNDLE = Path(__file__).resolve().parents[1] / "research" / "gmi-falsification-governance-v1"
SPEC = importlib.util.spec_from_file_location("falsification_governance_v1", BUNDLE / "falsification_governance_v1.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_four_governance_controls_are_exact_and_registry_scope_stays_open():
    result = MODULE.validate_audit()
    assert result["ledger_rows"] == 4
    assert result["open_registry_tasks"] == 3
    assert result["prospective_coordinate_rule"]
    assert result["pilot_excluded_from_evidence"]
