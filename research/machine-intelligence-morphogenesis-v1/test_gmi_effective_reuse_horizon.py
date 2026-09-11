from math import isclose, isinf

import pytest

from gmi_effective_reuse_horizon import (
    calibration_receipt,
    can_ever_pay_under_one_shot_hazard,
    effective_reuse_horizon,
    expected_net_gain,
    infinite_horizon_useful_reuses,
)


def test_zero_hazard_reduces_to_nominal_horizon():
    assert effective_reuse_horizon(20, 0.0) == 20.0
    assert isinf(infinite_horizon_useful_reuses(0.0))


def test_geometric_effective_horizon_exact_examples():
    assert isclose(effective_reuse_horizon(20, 0.05), 12.83028155182915)
    assert isclose(effective_reuse_horizon(20, 0.2), 4.942353924769659)
    assert effective_reuse_horizon(20, 1.0) == 1.0
    assert infinite_horizon_useful_reuses(0.2) == 5.0


def test_drift_can_make_nominally_long_horizon_unprofitable_forever():
    assert not can_ever_pay_under_one_shot_hazard(
        build_cost=10.0,
        maintenance_cost=0.0,
        per_use_saving=1.0,
        invalidation_hazard=0.2,
    )
    assert can_ever_pay_under_one_shot_hazard(
        build_cost=4.0,
        maintenance_cost=0.0,
        per_use_saving=1.0,
        invalidation_hazard=0.2,
    )


def test_expected_net_gain_uses_effective_not_nominal_reuse():
    no_drift = expected_net_gain(
        build_cost=10.0,
        maintenance_cost=0.0,
        per_use_saving=1.0,
        horizon=20,
        invalidation_hazard=0.0,
    )
    drift = expected_net_gain(
        build_cost=10.0,
        maintenance_cost=0.0,
        per_use_saving=1.0,
        horizon=20,
        invalidation_hazard=0.2,
    )
    assert no_drift == 10.0
    assert drift < 0.0


def test_invalid_inputs_fail_closed():
    with pytest.raises(ValueError):
        effective_reuse_horizon(-1, 0.1)
    with pytest.raises(ValueError):
        effective_reuse_horizon(1, 1.1)
    with pytest.raises(ValueError):
        expected_net_gain(
            build_cost=-1.0,
            maintenance_cost=0.0,
            per_use_saving=1.0,
            horizon=1,
            invalidation_hazard=0.0,
        )


def test_receipt_preserves_one_shot_boundary():
    receipt = calibration_receipt()
    assert receipt["terminal"] == "GMI_EFFECTIVE_REUSE_HORIZON_FINITE_CALIBRATION_GREEN_V1"
    assert receipt["key_boundaries"]["A10_D1_q02_ever_pays"] is False
    assert receipt["key_boundaries"]["A4_D1_q02_ever_pays"] is True
    assert "renewal" in receipt["claim_boundary"]
