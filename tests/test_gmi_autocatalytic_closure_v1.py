from __future__ import annotations
import importlib.util, sys
from pathlib import Path

BUNDLE = Path(__file__).resolve().parents[1] / "research" / "gmi-autocatalytic-closure-v1"
SPEC = importlib.util.spec_from_file_location("autocatalytic_closure_v1", BUNDLE / "autocatalytic_closure_v1.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

def test_constructor_collision_and_receipt():
    assert MODULE.collision_certificate()["productive_future"]
    assert MODULE.validate_receipt()["parent_equalities"] == 18

def test_only_six_earned_tasks_close():
    assert MODULE.validate_closure()["ledger_rows"] == 6
