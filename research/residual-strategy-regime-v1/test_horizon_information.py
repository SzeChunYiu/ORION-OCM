from __future__ import annotations

import math

import pytest

import horizon_information as H


def classical_curves(max_horizon=6, buy=3.0):
    inverse = {0: 0.0}
    semantic = {0: 0.0}
    for horizon in range(1, max_horizon + 1):
        inverse[horizon] = float(horizon)
        semantic[horizon] = float(buy)
    return inverse, semantic


def test_free_uninformative_signal_has_zero_value():
    prior = H.normalize_prior([1, 1, 1, 1, 1, 1])
    inverse, semantic = classical_curves()
    bounds = H.information_bounds(
        prior, H.uninformative_kernel(6), inverse, semantic
    )
    assert abs(bounds["gross_signal_value"]) < 1e-12
    assert bounds["perfect_horizon_value_cap"] >= 0


def test_perfect_signal_reaches_perfect_horizon_risk():
    prior = H.normalize_prior([1, 1, 1, 1, 1, 1])
    inverse, semantic = classical_curves()
    signal = H.free_signal_risk(
        prior, H.perfect_horizon_kernel(6), inverse, semantic
    )
    perfect = H.perfect_horizon_risk(prior, inverse, semantic)
    assert abs(signal["risk"] - perfect["risk"]) < 1e-12
    bounds = H.information_bounds(
        prior, H.perfect_horizon_kernel(6), inverse, semantic
    )
    assert abs(
        bounds["gross_signal_value"] - bounds["perfect_horizon_value_cap"]
    ) < 1e-12


def test_expensive_signal_is_ignored_by_optional_policy():
    prior = H.normalize_prior([1, 1, 1, 1, 1, 1])
    inverse, semantic = classical_curves()
    policy = H.best_optional_signal_policy(
        prior,
        H.perfect_horizon_kernel(6),
        inverse,
        semantic,
        signal_cost=1000.0,
    )
    assert policy["uses_signal"] is False
    assert policy["net_saving_vs_no_signal"] == 0.0


def test_delayed_signal_charges_only_surviving_sessions():
    prior = H.normalize_prior([0.5, 0.25, 0.125, 0.075, 0.03, 0.02])
    inverse, semantic = classical_curves()
    result = H.delayed_signal_risk(
        prior,
        H.perfect_horizon_kernel(6),
        inverse,
        semantic,
        delay=2,
        signal_cost=4.0,
    )
    survival = sum(prior[2:])
    assert abs(result["survival_probability_at_acquisition"] - survival) < 1e-12
    assert abs(result["expected_signal_cost"] - 4.0 * survival) < 1e-12


def test_survival_posterior_conditions_without_extra_predictor():
    prior = H.normalize_prior([1, 2, 3, 4])
    posterior = H.posterior_after_survival(prior, age=2)
    assert posterior["posterior"][0] == 0.0
    assert posterior["posterior"][1] == 0.0
    assert abs(sum(posterior["posterior"]) - 1.0) < 1e-12
    assert abs(posterior["posterior"][2] - 3 / 7) < 1e-12
    assert abs(posterior["posterior"][3] - 4 / 7) < 1e-12


def test_invalid_signal_kernel_cannot_smuggle_probability_mass():
    inverse, semantic = classical_curves()
    prior = H.normalize_prior([1, 1, 1, 1, 1, 1])
    bad = {"z": (0.5,) * 6}
    with pytest.raises(ValueError):
        H.free_signal_risk(prior, bad, inverse, semantic)


def test_randomization_cannot_beat_fixed_prior_best_threshold():
    prior = H.normalize_prior([1, 3, 2, 5, 1, 4])
    inverse, semantic = classical_curves()
    risks = H.all_threshold_risks(prior, inverse, semantic)
    best = min(risk for risk, _ in risks)
    mixture = {0: 0.2, 1: 0.3, 4: 0.5}
    mixed_risk = math.fsum(
        probability * dict((threshold, risk) for risk, threshold in risks)[threshold]
        for threshold, probability in mixture.items()
    )
    assert mixed_risk + 1e-12 >= best
