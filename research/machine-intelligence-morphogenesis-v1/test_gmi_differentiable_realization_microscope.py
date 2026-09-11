from math import isclose

import pytest

from gmi_differentiable_realization_microscope import (
    QuadraticWorld,
    calibration_receipt,
    exact_preconditioned_cost,
    preferred_update_law,
    real_horizon_crossover,
    vanilla_gd_cost,
    vanilla_gd_iterations,
    vanilla_gd_objective_after_steps,
)


def test_kappa100_native_geometry_and_horizon_phase():
    h1 = QuadraticWorld(20, 100.0, 1e-3, 1)
    h2 = QuadraticWorld(20, 100.0, 1e-3, 2)
    assert vanilla_gd_iterations(h1) == 310
    assert vanilla_gd_cost(h1).per_task == 6200.0
    assert exact_preconditioned_cost(h1).build == 8000.0
    assert exact_preconditioned_cost(h1).per_task == 400.0
    assert preferred_update_law(h1) == ("VANILLA_GD",)
    assert preferred_update_law(h2) == ("EXACT_PRECONDITIONED",)
    assert isclose(real_horizon_crossover(20, 100.0, 1e-3), 1.3793103448275863)


def test_low_condition_number_does_not_pay_for_dense_preconditioner_at_h2():
    world = QuadraticWorld(20, 2.0, 1e-3, 2)
    assert vanilla_gd_iterations(world) == 5
    assert vanilla_gd_cost(world).per_task == 100.0
    assert exact_preconditioned_cost(world).per_task == 400.0
    assert preferred_update_law(world) == ("VANILLA_GD",)
    assert real_horizon_crossover(20, 2.0, 1e-3) is None


def test_same_gradient_feedback_does_not_fix_update_law_ranking():
    # The obligation-side feedback channel is identical; only native objective
    # geometry and horizon differ.
    high = QuadraticWorld(20, 100.0, 1e-3, 2)
    low = QuadraticWorld(20, 2.0, 1e-3, 2)
    assert preferred_update_law(high) == ("EXACT_PRECONDITIONED",)
    assert preferred_update_law(low) == ("VANILLA_GD",)


def test_objective_contracts_as_expected():
    world = QuadraticWorld(20, 100.0, 1e-3, 1)
    assert vanilla_gd_objective_after_steps(world, 0) > 900
    assert vanilla_gd_objective_after_steps(world, 310) <= 1e-3
    assert vanilla_gd_objective_after_steps(world, 309) > 1e-3


def test_invalid_quadratic_worlds_fail_closed():
    with pytest.raises(ValueError):
        QuadraticWorld(1, 2.0, 1e-3, 1)
    with pytest.raises(ValueError):
        QuadraticWorld(20, 0.5, 1e-3, 1)
    with pytest.raises(ValueError):
        QuadraticWorld(20, 2.0, 0.5, 1)
    with pytest.raises(ValueError):
        QuadraticWorld(20, 2.0, 1e-3, 0)


def test_receipt_keeps_neural_claim_locked():
    receipt = calibration_receipt()
    assert receipt["rows"]["KAPPA100_H1"]["winner"] == ("VANILLA_GD",)
    assert receipt["rows"]["KAPPA100_H2"]["winner"] == ("EXACT_PRECONDITIONED",)
    assert receipt["rows"]["KAPPA2_H2"]["winner"] == ("VANILLA_GD",)
    assert receipt["terminal"] == "DIFFERENTIABLE_NATIVE_CONDITIONING_AND_AMORTIZATION_CALIBRATED"
    assert "not a neural architecture law" in receipt["claim_boundary"]
