from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "research"
    / "orion-machine"
    / "reference"
    / "ocm_wll_interface_hierarchy_exact.py"
)
SPEC = importlib.util.spec_from_file_location(
    "ocm_wll_interface_hierarchy_exact", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


def test_world_count() -> None:
    assert len(M.enumerate_worlds()) == 256


def test_interfaces_are_nested_refinements() -> None:
    worlds = M.enumerate_worlds()
    for (_, lower), (_, upper) in zip(M.INTERFACES, M.INTERFACES[1:]):
        assert M.interface_refines(worlds, lower, upper)


def test_every_step_has_strict_target_witness() -> None:
    worlds = M.enumerate_worlds()
    for (_, lower), (_, upper) in zip(M.INTERFACES, M.INTERFACES[1:]):
        witness = M.find_strict_witness(worlds, lower, upper)
        assert witness["left_world"]["target"] != witness["right_world"]["target"]


def test_only_closure_certified_interface_is_exact() -> None:
    result = M.run_exact_calibration()
    metrics = result["metrics"]
    assert metrics["I0_ENDPOINT_ONLY"]["exact_lifecycle_identification"] is False
    assert metrics["I1_RAW_LOCAL_TRACE"]["exact_lifecycle_identification"] is False
    assert metrics["I2_POSITIVE_CERTIFIED_SUPPORT"]["exact_lifecycle_identification"] is False
    assert metrics["I3_CLOSURE_CERTIFIED_WARRANT"]["exact_lifecycle_identification"] is True


def test_raw_trace_recovers_function_but_not_warrant() -> None:
    metrics = M.run_exact_calibration()["metrics"]["I1_RAW_LOCAL_TRACE"]
    assert metrics["minimum_guaranteed_answerable_coordinates"] == 3
    assert metrics["maximum_required_abstentions_zero_error"] == 3


def test_positive_certificate_has_local_gain() -> None:
    gain = M.run_exact_calibration()["positive_certificate_local_gain"]
    coordinate = gain["newly_answerable_backup_coordinate"]
    assert coordinate not in gain["I1_constant_coordinates"]
    assert coordinate in gain["I2_constant_coordinates"]


def test_missing_positive_is_not_negative_certificate() -> None:
    planted = M.run_exact_calibration()["planted_false_completion"]
    assert planted["I2_observation_identical"] is True
    assert planted["left_required_backup_action"] != planted["right_required_backup_action"]
    assert planted["fired"] is True


def test_top_interface_has_zero_abstention() -> None:
    metrics = M.run_exact_calibration()["metrics"]["I3_CLOSURE_CERTIFIED_WARRANT"]
    assert metrics["maximum_required_abstentions_zero_error"] == 0
    assert metrics["minimum_guaranteed_answerable_coordinates"] == 6


def test_invalid_world_vector_is_rejected() -> None:
    try:
        M.World((0, 1), (0,), (0, 1))
    except ValueError:
        pass
    else:
        raise AssertionError("invalid world was accepted")
