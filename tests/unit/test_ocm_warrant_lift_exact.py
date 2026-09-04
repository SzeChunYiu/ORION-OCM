from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "research"
    / "orion-machine"
    / "reference"
    / "ocm_warrant_lift_exact.py"
)
SPEC = importlib.util.spec_from_file_location("ocm_warrant_lift_exact", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


def test_partition_counts() -> None:
    assert [len(M.set_partitions(n)) for n in range(1, 6)] == [1, 2, 5, 15, 52]


def test_zero_criterion() -> None:
    behavior = (0, 0, 1, 1)
    lifecycle = (0, 0, 1, 1)
    assert M.warrant_lift_real(behavior, lifecycle) == 0
    assert M.warrant_lift_bits(behavior, lifecycle) == 0


def test_exact_side_code_characterization() -> None:
    behavior = (0, 0, 0, 1, 1)
    lifecycle = (0, 1, 2, 3, 4)
    bits, code = M.minimal_side_code(behavior, lifecycle)
    assert bits == 2
    assert M.code_identifies_lifecycle(behavior, lifecycle, code)


def test_planted_code_merge_breaks_identification() -> None:
    behavior = (0, 0, 0, 1)
    lifecycle = (0, 1, 2, 3)
    _, code = M.minimal_side_code(behavior, lifecycle)
    broken = M.collapsed_code(code, 0, 1)
    assert not M.code_identifies_lifecycle(behavior, lifecycle, broken)


def test_obligation_monotonicity_example() -> None:
    behavior = (0, 0, 0, 0)
    coarse = (0, 0, 1, 1)
    fine = (0, 1, 2, 3)
    assert M.refines(fine, coarse)
    assert M.warrant_lift_real(behavior, fine) >= M.warrant_lift_real(
        behavior, coarse
    )


def test_product_additivity_example() -> None:
    b1, l1 = (0, 0), (0, 1)
    b2, l2 = (0, 0, 0), (0, 1, 2)
    bp = M.product_partition(b1, b2)
    lp = M.product_partition(l1, l2)
    assert M.warrant_lift_real(bp, lp) == (
        M.warrant_lift_real(b1, l1) + M.warrant_lift_real(b2, l2)
    )


def test_current_accuracy_can_hide_arbitrary_lift() -> None:
    for bits in range(9):
        behavior, lifecycle = M.current_accuracy_blind_spot(bits)
        assert len(set(behavior)) == 1
        assert M.warrant_lift_bits(behavior, lifecycle) == bits


def test_conditional_entropy_bounded_by_worst_case_lift() -> None:
    behavior = (0, 0, 0, 1, 1)
    lifecycle = (0, 1, 2, 3, 3)
    entropy = M.conditional_entropy_uniform(behavior, lifecycle)
    assert 0 <= entropy <= M.warrant_lift_real(behavior, lifecycle)


def test_invalid_non_refinement_rejected() -> None:
    try:
        M.warrant_lift_bits((0, 1), (0, 0))
    except ValueError:
        pass
    else:
        raise AssertionError("non-refining lifecycle partition was accepted")


def test_full_sweep_passes() -> None:
    result = M.run_exact_calibration()
    assert result["terminal"] == "PASS_FINITE_WARRANT_LIFT_THEORY"
    assert result["partition_sweep"]["planted_code_collisions_fired"] > 0
