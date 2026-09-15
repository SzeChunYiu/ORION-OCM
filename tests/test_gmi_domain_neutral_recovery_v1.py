from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


BUNDLE = Path(__file__).resolve().parents[1] / "research" / "gmi-domain-neutral-recovery-v1"
SPEC = importlib.util.spec_from_file_location("domain_neutral_recovery_v1", BUNDLE / "domain_neutral_recovery_v1.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_three_family_hidden_searches_and_twins():
    result = MODULE.validate_closure()
    assert result["family_label_free"]
    assert result["relational"]["winner"] != result["relational"]["twin_winner"]
    assert result["local"]["winner"] != result["local"]["twin_winner"]
    assert result["constructive"]["winner"] != result["constructive"]["twin_winner"]


def test_exactly_three_scoped_tasks_close():
    assert MODULE.validate_closure()["ledger_rows"] == 3
