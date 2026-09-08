"""Exact finite paid-horizon-information calculus for R0B; no ML.

This module deliberately has no empirical lifetime prior.  It provides the
finite Bayes/value-of-information parents that a future, prospectively admitted
lifetime prior or signal must beat.  Synthetic priors/channels are for theorem
and hostile tests only.
"""
from __future__ import annotations

import math


EPS = 1e-12


def normalize_prior(probabilities):
    """Return a normalized finite prior P(H=h), represented for h=1..M."""
    values = tuple(float(value) for value in probabilities)
    if not values or any(not math.isfinite(value) or value < 0 for value in values):
        raise ValueError("prior must be finite, nonempty and nonnegative")
    total = math.fsum(values)
    if total <= 0:
        raise ValueError("prior must have positive mass")
    return tuple(value / total for value in values)


def validate_curves(inverse, semantic, max_horizon):
    if set(inverse) != set(range(max_horizon + 1)):
        raise ValueError("inverse curve must cover 0..M exactly")
    if set(semantic) != set(range(max_horizon + 1)):
        raise ValueError("semantic curve must cover 0..M exactly")
    if abs(float(inverse[0])) > EPS or abs(float(semantic[0])) > EPS:
        raise ValueError("zero-horizon cost must be zero")
    for curve in (inverse, semantic):
        if any(not math.isfinite(float(value)) or float(value) < 0 for value in curve.values()):
            raise ValueError("cost curves must be finite and nonnegative")


def threshold_cost(horizon, threshold, inverse, semantic):
    """Inverse for threshold demands, then one cold semantic lifetime."""
    if type(horizon) is not int or type(threshold) is not int:
        raise ValueError("horizon and threshold must be integers")
    if horizon < 0 or threshold < 0:
        raise ValueError("horizon and threshold must be nonnegative")
    if horizon <= threshold:
        return float(inverse[horizon])
    return float(inverse[threshold]) + float(semantic[horizon - threshold])


def all_threshold_risks(prior, inverse, semantic):
    prior = normalize_prior(prior)
    max_horizon = len(prior)
    validate_curves(inverse, semantic, max_horizon)
    risks = []
    for threshold in range(max_horizon + 1):
        risk = math.fsum(
            prior[horizon - 1] * threshold_cost(horizon, threshold, inverse, semantic)
            for horizon in range(1, max_horizon + 1)
        )
        risks.append((risk, threshold))
    return tuple(risks)


def bayes_no_signal(prior, inverse, semantic):
    """Exact fixed-prior optimum among time-only deterministic thresholds."""
    risk, threshold = min(all_threshold_risks(prior, inverse, semantic))
    return {"risk": risk, "threshold": threshold}


def perfect_horizon_risk(prior, inverse, semantic):
    """Clairvoyant-H optimum within the same one-way threshold action family."""
    prior = normalize_prior(prior)
    max_horizon = len(prior)
    validate_curves(inverse, semantic, max_horizon)
    rows = []
    total = 0.0
    for horizon in range(1, max_horizon + 1):
        best_cost, best_threshold = min(
            (threshold_cost(horizon, threshold, inverse, semantic), threshold)
            for threshold in range(max_horizon + 1)
        )
        total += prior[horizon - 1] * best_cost
        rows.append({
            "horizon": horizon,
            "threshold": best_threshold,
            "cost": best_cost,
        })
    return {"risk": total, "rows": rows}


def validate_signal_kernel(kernel, max_horizon):
    """Validate finite K(z|H); values are sequences indexed by H=1..M."""
    if not isinstance(kernel, dict) or not kernel:
        raise ValueError("signal kernel must be a nonempty mapping")
    normalized = {}
    for label, likelihoods in kernel.items():
        if not isinstance(label, str) or not label:
            raise ValueError("signal labels must be nonempty strings")
        values = tuple(float(value) for value in likelihoods)
        if len(values) != max_horizon:
            raise ValueError("every signal likelihood vector must cover H=1..M")
        if any(not math.isfinite(value) or value < 0 for value in values):
            raise ValueError("signal likelihoods must be finite and nonnegative")
        normalized[label] = values
    for index in range(max_horizon):
        total = math.fsum(values[index] for values in normalized.values())
        if abs(total - 1.0) > 1e-10:
            raise ValueError("signal probabilities must sum to one for every horizon")
    return normalized


def perfect_horizon_kernel(max_horizon):
    return {
        f"H={horizon}": tuple(
            1.0 if candidate == horizon else 0.0
            for candidate in range(1, max_horizon + 1)
        )
        for horizon in range(1, max_horizon + 1)
    }


def uninformative_kernel(max_horizon):
    return {"constant": (1.0,) * max_horizon}


def posterior_after_survival(prior, age):
    """Return P(H=h | H>age), still indexed over h=1..M with zeros before."""
    prior = normalize_prior(prior)
    max_horizon = len(prior)
    if type(age) is not int or not 0 <= age <= max_horizon:
        raise ValueError("age must lie in 0..M")
    surviving = [
        prior[horizon - 1] if horizon > age else 0.0
        for horizon in range(1, max_horizon + 1)
    ]
    mass = math.fsum(surviving)
    if mass <= 0:
        return {"survival_probability": 0.0, "posterior": tuple(surviving)}
    return {
        "survival_probability": mass,
        "posterior": tuple(value / mass for value in surviving),
    }


def free_signal_risk(prior, kernel, inverse, semantic):
    """Bayes risk when a finite signal is observed at session start for free."""
    prior = normalize_prior(prior)
    max_horizon = len(prior)
    validate_curves(inverse, semantic, max_horizon)
    kernel = validate_signal_kernel(kernel, max_horizon)
    total = 0.0
    decisions = {}
    for label, likelihoods in kernel.items():
        scored = []
        outcome_mass = math.fsum(
            prior[horizon - 1] * likelihoods[horizon - 1]
            for horizon in range(1, max_horizon + 1)
        )
        if outcome_mass <= EPS:
            decisions[label] = {"mass": outcome_mass, "threshold": None, "joint_cost": 0.0}
            continue
        for threshold in range(max_horizon + 1):
            joint_cost = math.fsum(
                prior[horizon - 1]
                * likelihoods[horizon - 1]
                * threshold_cost(horizon, threshold, inverse, semantic)
                for horizon in range(1, max_horizon + 1)
            )
            scored.append((joint_cost, threshold))
        joint_cost, threshold = min(scored)
        total += joint_cost
        decisions[label] = {
            "mass": outcome_mass,
            "threshold": threshold,
            "joint_cost": joint_cost,
        }
    return {"risk": total, "decisions": decisions}


def delayed_signal_risk(prior, kernel, inverse, semantic, delay, signal_cost=0.0):
    """Use inverse for `delay`, then acquire one signal iff the session survives.

    Signal cost is scalar here because this is a Bayes-risk primitive.  Raw-vector
    acquisition cost must still be reported separately by any experiment that
    scalarizes resources.
    """
    prior = normalize_prior(prior)
    max_horizon = len(prior)
    validate_curves(inverse, semantic, max_horizon)
    kernel = validate_signal_kernel(kernel, max_horizon)
    if type(delay) is not int or not 0 <= delay <= max_horizon:
        raise ValueError("delay must lie in 0..M")
    signal_cost = float(signal_cost)
    if not math.isfinite(signal_cost) or signal_cost < 0:
        raise ValueError("signal cost must be finite and nonnegative")

    ended_cost = math.fsum(
        prior[horizon - 1] * float(inverse[horizon])
        for horizon in range(1, delay + 1)
    )
    survival_probability = math.fsum(prior[delay:])
    if survival_probability <= EPS:
        return {
            "risk": ended_cost,
            "delay": delay,
            "survival_probability_at_acquisition": 0.0,
            "expected_signal_cost": 0.0,
            "decisions": {},
        }

    signal_total = 0.0
    decisions = {}
    residual_max = max_horizon - delay
    for label, likelihoods in kernel.items():
        outcome_mass = math.fsum(
            prior[horizon - 1] * likelihoods[horizon - 1]
            for horizon in range(delay + 1, max_horizon + 1)
        )
        if outcome_mass <= EPS:
            decisions[label] = {"surviving_joint_mass": outcome_mass, "threshold": None}
            continue
        scored = []
        for threshold in range(residual_max + 1):
            joint_cost = math.fsum(
                prior[horizon - 1]
                * likelihoods[horizon - 1]
                * (
                    float(inverse[delay])
                    + signal_cost
                    + threshold_cost(
                        horizon - delay, threshold, inverse, semantic
                    )
                )
                for horizon in range(delay + 1, max_horizon + 1)
            )
            scored.append((joint_cost, threshold))
        joint_cost, threshold = min(scored)
        signal_total += joint_cost
        decisions[label] = {
            "surviving_joint_mass": outcome_mass,
            "threshold": threshold,
            "joint_cost": joint_cost,
        }

    return {
        "risk": ended_cost + signal_total,
        "delay": delay,
        "survival_probability_at_acquisition": survival_probability,
        "expected_signal_cost": survival_probability * signal_cost,
        "decisions": decisions,
    }


def best_optional_signal_policy(prior, kernel, inverse, semantic, signal_cost=0.0):
    """Choose no signal or the best delayed one-shot acquisition time."""
    prior = normalize_prior(prior)
    baseline = bayes_no_signal(prior, inverse, semantic)
    candidates = [
        delayed_signal_risk(
            prior, kernel, inverse, semantic, delay, signal_cost=signal_cost
        )
        for delay in range(len(prior) + 1)
    ]
    best_signal = min(candidates, key=lambda row: (row["risk"], row["delay"]))
    if baseline["risk"] <= best_signal["risk"] + EPS:
        return {
            "risk": baseline["risk"],
            "uses_signal": False,
            "baseline_threshold": baseline["threshold"],
            "best_signal_candidate": best_signal,
            "net_saving_vs_no_signal": 0.0,
        }
    return {
        "risk": best_signal["risk"],
        "uses_signal": True,
        "baseline_threshold": baseline["threshold"],
        "best_signal_candidate": best_signal,
        "net_saving_vs_no_signal": baseline["risk"] - best_signal["risk"],
    }


def information_bounds(prior, kernel, inverse, semantic):
    """Gross free-signal VOI and perfect-H upper bound under one fixed prior."""
    prior = normalize_prior(prior)
    baseline = bayes_no_signal(prior, inverse, semantic)
    signal = free_signal_risk(prior, kernel, inverse, semantic)
    perfect = perfect_horizon_risk(prior, inverse, semantic)
    gross = baseline["risk"] - signal["risk"]
    perfect_cap = baseline["risk"] - perfect["risk"]
    if gross < -1e-9 or gross > perfect_cap + 1e-9:
        raise AssertionError("signal value violated decision-information bounds")
    return {
        "no_signal_risk": baseline["risk"],
        "signal_risk": signal["risk"],
        "perfect_horizon_risk": perfect["risk"],
        "gross_signal_value": max(0.0, gross),
        "perfect_horizon_value_cap": max(0.0, perfect_cap),
    }
