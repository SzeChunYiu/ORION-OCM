from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/gmi-resource-lifecycle-ledger-v1/resource_lifecycle_ledger_v1.py"
SPEC = importlib.util.spec_from_file_location("gmi_resource_lifecycle_ledger_v1", SOURCE)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_registered_resource_ledger_is_exact_and_physical_gaps_remain_open():
    result = MODULE.validate_registry()
    assert result["coordinates"] == 14
    assert result["vectors"] == 27
    assert result["unordered_pairs"] == 351
    assert result["physical_metering"] == "OPEN"
    assert result["energy_metering"] == "OPEN"
