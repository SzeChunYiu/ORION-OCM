from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "research/gmi-physical-resource-metering-v1"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_physical_metering_and_b19_real_sequences_close_open_boxes():
    metering = _load("gmi_physical_resource_metering_v1", PKG / "physical_resource_metering_v1.py")
    b19 = _load("gmi_continual_real_sequence_b19_v1", PKG / "continual_real_sequence_b19_v1.py")

    validated = metering.validate_contract()
    assert validated["coordinates"] == 7
    assert validated["sibling_physical"] == "OPEN"
    assert validated["sibling_energy"] == "OPEN"

    scope = metering.ScopeRegistration(
        "repo-wrapper-scope",
        "wrapper smoke",
        registered_before_outcomes=True,
    )
    receipt = metering.run_metered(scope)
    assert receipt.claim_ceiling.startswith("PHYSICAL_COUNTERS_CLOSED_AT_SCOPE")

    witness = b19.run_witness()
    assert witness["claim_ceiling"] == "REAL_SEQUENCE_WITNESS_AT_PLANTED_SCOPE"
    assert all(row["winners"] == ["expand"] for row in witness["cheap_capacity"])
    assert all(row["winners"] == ["modularize"] for row in witness["dear_capacity"])
