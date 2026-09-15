from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


BUNDLE = Path(__file__).resolve().parents[1] / "research" / "gmi-neutral-safeguards-audit-v1"
SPEC = importlib.util.spec_from_file_location("neutral_safeguards_audit_v1", BUNDLE / "neutral_safeguards_audit_v1.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_neutral_suite_safeguards_are_fail_closed():
    result = MODULE.validate_audit()
    assert result["ledger_rows"] == 10
    assert result["positive_recovery_cells"] == 8
    assert result["twin_target_recovery_cells"] == 0
    assert result["preserved_failure_terminals"] == 2
