from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


BUNDLE = Path(__file__).resolve().parents[1] / "research" / "gmi-local-field-closure-v1"
SPEC = importlib.util.spec_from_file_location("local_field_closure_v1", BUNDLE / "local_field_closure_v1.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_local_interventions_and_receipt():
    assert MODULE.lesion_regeneration_certificate()["repaired"][32] == 32
    topology = MODULE.topology_sensitivity_certificate()
    assert topology["differing"] == topology["expected"]
    assert MODULE.validate_receipt()["answer_equalities"] == 60


def test_only_seven_earned_tasks_close():
    assert MODULE.validate_closure()["ledger_rows"] == 7
