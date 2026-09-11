from math import isclose

import pytest

from gmi_bayesian_realization_microscope import (
    BinaryBayesWorld,
    binary_entropy,
    calibration_receipt,
    expected_information_gain,
    map_accuracy_gain,
    observe_is_worthwhile_under_accuracy_utility,
    posterior_map_expected_accuracy,
    posterior_theta1,
    prior_map_accuracy,
)


def test_balanced_prior_exact_values():
    world = BinaryBayesWorld(0.5, 0.1)
    assert binary_entropy(world.prior_theta1) == 1.0
    assert isclose(posterior_theta1(world, 1), 0.9)
    assert isclose(posterior_theta1(world, 0), 0.1)
    assert isclose(expected_information_gain(world), 0.5310044064107189)
    assert isclose(prior_map_accuracy(world), 0.5)
    assert isclose(posterior_map_expected_accuracy(world), 0.9)
    assert isclose(map_accuracy_gain(world), 0.4)


def test_positive_information_gain_can_have_zero_map_decision_value():
    world = BinaryBayesWorld(0.9, 0.1)
    assert expected_information_gain(world) > 0.2
    assert isclose(expected_information_gain(world), 0.21108145213899854)
    assert isclose(prior_map_accuracy(world), 0.9)
    assert isclose(posterior_map_expected_accuracy(world), 0.9)
    assert isclose(map_accuracy_gain(world), 0.0, abs_tol=1e-12)


def test_observation_value_depends_on_declared_decision_utility_and_cost():
    balanced = BinaryBayesWorld(0.5, 0.1)
    strong_prior = BinaryBayesWorld(0.9, 0.1)
    assert observe_is_worthwhile_under_accuracy_utility(balanced, observation_cost=0.1)
    assert not observe_is_worthwhile_under_accuracy_utility(balanced, observation_cost=0.5)
    assert not observe_is_worthwhile_under_accuracy_utility(strong_prior, observation_cost=0.0)


def test_invalid_probabilities_fail_closed():
    with pytest.raises(ValueError):
        BinaryBayesWorld(0.0, 0.1)
    with pytest.raises(ValueError):
        BinaryBayesWorld(0.5, 0.5)
    with pytest.raises(ValueError):
        binary_entropy(-0.1)
    with pytest.raises(ValueError):
        posterior_theta1(BinaryBayesWorld(0.5, 0.1), 2)


def test_receipt_preserves_information_vs_decision_boundary():
    receipt = calibration_receipt()
    strong = receipt["rows"]["STRONG_PRIOR"]
    assert strong["expected_information_gain_bits"] > 0
    assert isclose(strong["map_accuracy_gain"], 0.0, abs_tol=1e-12)
    assert receipt["terminal"] == "BAYESIAN_NATIVE_INFORMATION_AND_DECISION_VALUE_CALIBRATED_EXACT"
    assert "not identical" in receipt["key_hostile"]
