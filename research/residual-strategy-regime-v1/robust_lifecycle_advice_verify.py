"""Verify frozen robust lifecycle-advice minimax certificates; stdlib only.

The offline generator may use SciPy, but this verifier rebuilds the threshold
ratio matrix from the source-derived regime artifact.  A deterministic advised
policy is a pair (tau_0,tau_1), one threshold for each observed advice bit.  The
frozen primal mixes such pairs.  The frozen dual mixes adversarial scenarios
(horizon, error endpoint).  Recomputed weak-duality bounds certify the finite
zero-sum game value without trusting solver status or objective fields.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import randomized_switch_verify as R


TOL = 5e-8
CERT_SCHEMA = "ocm.residual-strategy-regime.r0b.lifecycle-advice.certificate.v1"
REPORT_SCHEMA = "ocm.residual-strategy-regime.r0b.lifecycle-advice.verify.v1"
COORDINATES = R.COORDINATES


def _load_json(path):
    return json.loads(Path(path).read_text())


def _write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def decision_bits(rows, coordinate, max_horizon):
    bits = []
    for row in rows[:max_horizon]:
        bits.append(0 if float(row["inverse"][coordinate]) <= float(row["semantic"][coordinate]) else 1)
    return tuple(bits)


def monotone_crossover(bits):
    seen_one = False
    first = None
    for index, bit in enumerate(bits, start=1):
        if bit == 1:
            if not seen_one:
                first = index
            seen_one = True
        elif seen_one:
            return None
    return first


def _pair_distribution(thresholds, support):
    result = []
    seen = set()
    total = 0.0
    for item in support:
        t0 = item["threshold_if_advice_0"]
        t1 = item["threshold_if_advice_1"]
        if type(t0) is not int or type(t1) is not int:
            raise ValueError("threshold pair must be integral")
        if not 0 <= t0 < thresholds or not 0 <= t1 < thresholds or (t0, t1) in seen:
            raise ValueError("threshold pair out of range or duplicated")
        probability = float(item["probability"])
        if not math.isfinite(probability) or probability < 0:
            raise ValueError("invalid primal probability")
        result.append((t0, t1, probability))
        total += probability
        seen.add((t0, t1))
    return tuple(result), total


def _dual_distribution(horizons, support):
    result = []
    seen = set()
    total = 0.0
    for item in support:
        horizon = item["horizon"]
        endpoint = item["error_endpoint"]
        if type(horizon) is not int or not 1 <= horizon <= horizons:
            raise ValueError("dual horizon out of range")
        if endpoint not in ("zero", "epsilon") or (horizon, endpoint) in seen:
            raise ValueError("invalid or duplicated dual scenario")
        probability = float(item["probability"])
        if not math.isfinite(probability) or probability < 0:
            raise ValueError("invalid dual probability")
        result.append((horizon - 1, endpoint, probability))
        total += probability
        seen.add((horizon, endpoint))
    return tuple(result), total


def scenario_payoff(matrix, bits, row, endpoint, epsilon, t0, t1):
    bit = bits[row]
    correct_threshold = t0 if bit == 0 else t1
    wrong_threshold = t1 if bit == 0 else t0
    correct = matrix[row][correct_threshold]
    if endpoint == "zero":
        return correct
    wrong = matrix[row][wrong_threshold]
    return (1.0 - epsilon) * correct + epsilon * wrong


def verify_certificate(matrix, bits, certificate, tol=TOL):
    if not matrix or not matrix[0] or len(bits) != len(matrix):
        raise ValueError("invalid matrix/bits")
    horizons = len(matrix)
    thresholds = len(matrix[0])
    if any(len(row) != thresholds for row in matrix):
        raise ValueError("matrix must be rectangular")
    epsilon = float(certificate["epsilon"])
    if not 0.0 <= epsilon <= 1.0:
        raise ValueError("invalid epsilon")

    primal, p_sum = _pair_distribution(thresholds, certificate["primal_support"])
    dual, q_sum = _dual_distribution(horizons, certificate["dual_support"])

    scenario_values = []
    for row in range(horizons):
        for endpoint in ("zero", "epsilon"):
            value = math.fsum(
                probability * scenario_payoff(matrix, bits, row, endpoint, epsilon, t0, t1)
                for t0, t1, probability in primal
            )
            scenario_values.append((row + 1, endpoint, value))
    upper = max(value for _, _, value in scenario_values)

    lower = math.inf
    binding_pairs = []
    pair_values = {}
    for t0 in range(thresholds):
        for t1 in range(thresholds):
            value = math.fsum(
                probability * scenario_payoff(matrix, bits, row, endpoint, epsilon, t0, t1)
                for row, endpoint, probability in dual
            )
            pair_values[(t0, t1)] = value
            if value < lower:
                lower = value
    for pair, value in pair_values.items():
        if value <= lower + 1e-7:
            binding_pairs.append(list(pair))

    gap = upper - lower
    normalization_error = max(abs(p_sum - 1.0), abs(q_sum - 1.0))
    reported_primal_error = abs(float(certificate["primal_value"]) - upper)
    reported_dual_error = abs(float(certificate["dual_value"]) - lower)
    certified = (
        normalization_error <= tol
        and lower <= upper + tol
        and gap <= tol
        and reported_primal_error <= 10 * tol
        and reported_dual_error <= 10 * tol
    )
    return {
        "certified": certified,
        "epsilon": epsilon,
        "target_ratio": float(certificate["target_ratio"]),
        "primal_upper_bound": upper,
        "dual_lower_bound": lower,
        "certified_gap": gap,
        "normalization_error": normalization_error,
        "reported_primal_error": reported_primal_error,
        "reported_dual_error": reported_dual_error,
        "worst_scenarios_under_primal": [
            {"horizon": horizon, "error_endpoint": endpoint}
            for horizon, endpoint, value in scenario_values
            if value >= upper - 1e-7
        ],
        "binding_threshold_pairs_under_dual": binding_pairs,
        "primal_support": certificate["primal_support"],
        "dual_support": certificate["dual_support"],
    }


def build_report(regime, certificate):
    if certificate.get("schema") != CERT_SCHEMA:
        raise ValueError("unexpected lifecycle-advice certificate schema")
    if certificate.get("adversary") != "oblivious horizon; per-horizon advice error q chosen in [0,epsilon]":
        raise ValueError("unexpected adversary scope")
    max_horizon = certificate.get("max_horizon")
    if type(max_horizon) is not int or not 1 <= max_horizon <= 10_000:
        raise ValueError("invalid horizon")
    rows = regime["iid_static"]["rows"]
    coordinates = {}
    all_certified = True
    for coordinate in COORDINATES:
        matrix = R.ratio_matrix(rows, coordinate, max_horizon)
        bits = decision_bits(rows, coordinate, max_horizon)
        result = verify_certificate(matrix, bits, certificate["coordinates"][coordinate])
        result["decision_region_crossover"] = monotone_crossover(bits)
        all_certified = all_certified and result["certified"]
        coordinates[coordinate] = result

    terminal = (
        "ROBUST_LIFECYCLE_ADVICE_1_05_BOUNDARY_CERTIFIED_R0B"
        if all_certified
        else "ROBUST_LIFECYCLE_ADVICE_CERTIFICATE_FAILED_R0B"
    )
    return {
        "schema": REPORT_SCHEMA,
        "study": "Solver-independent verification of robust lifecycle decision-region advice",
        "scope": {
            "effective_horizon": [1, max_horizon],
            "advice": certificate["advice"],
            "adversary": certificate["adversary"],
            "benchmark": certificate["benchmark"],
            "future_horizon_visible": False,
            "future_targets_visible": False,
            "target_features_visible": False,
            "resource_coordinates": list(COORDINATES),
        },
        "certificate_generator": certificate.get("generator"),
        "verification": {
            "solver_imported": False,
            "numpy_imported": False,
            "scipy_imported": False,
            "method": "recomputed primal upper + dual lower bounds on implicit advised-policy game",
            "all_certified": all_certified,
            "tolerance": TOL,
        },
        "coordinates": coordinates,
        "claim_boundary": {
            "one_perfect_decision_region_bit_suffices_for_two_static_arm_benchmark": True,
            "frozen_epsilon_is_numerical_1_05_boundary_candidate": True,
            "exact_maximal_epsilon_beyond_numerical_tolerance_claimed": False,
            "predictor_trained": False,
            "advice_observable_for_free": False,
            "price_independent_policy_claimed": False,
            "ml_authorized": False,
        },
        "terminal": terminal,
    }


def _notice(report):
    return {
        "terminal": report["terminal"],
        "coordinates": {
            coordinate: {
                "epsilon": value["epsilon"],
                "value": value["primal_upper_bound"],
                "lower": value["dual_lower_bound"],
                "gap": value["certified_gap"],
                "crossover": value["decision_region_crossover"],
            }
            for coordinate, value in report["coordinates"].items()
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--regime", required=True, type=Path)
    parser.add_argument("--certificate", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--github-notice", action="store_true")
    args = parser.parse_args()
    report = build_report(_load_json(args.regime), _load_json(args.certificate))
    _write_json(args.out, report)
    rendered = json.dumps(_notice(report), sort_keys=True, separators=(",", ":"))
    if args.github_notice:
        print(f"::notice title=R0B robust lifecycle advice certificate::{rendered}")
    else:
        print(rendered)
    if not report["verification"]["all_certified"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
