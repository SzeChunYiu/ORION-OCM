"""Verify frozen randomized time-only switch minimax certificates; stdlib only.

The LP solve is an offline research generator.  This verifier trusts neither
SciPy nor the solver-reported objective.  It rebuilds the finite ratio matrices
from the source-derived regime artifact and recomputes primal upper bounds and
dual lower bounds from frozen mixed strategies.

Scope is an oblivious horizon adversary: the realized effective horizon is fixed
without observing the policy's private threshold draw.  Against an adversary
that sees the draw first, no randomized improvement is claimed.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


TOL = 5e-8
COORDINATES = ("transitions", "arithmetic_additions", "arithmetic_multiplications")
CERT_SCHEMA = "ocm.residual-strategy-regime.r0b.phase2b2.randomized-switch.certificate.v1"
REPORT_SCHEMA = "ocm.residual-strategy-regime.r0b.phase2b2.randomized-switch.verify.v2"


def _write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def _load_json(path):
    return json.loads(Path(path).read_text())


def lifetime_curves(rows, coordinate, max_horizon):
    inverse = {0: 0.0}
    semantic = {0: 0.0}
    if len(rows) < max_horizon:
        raise ValueError("regime artifact does not cover requested horizon")
    for expected_h, row in enumerate(rows[:max_horizon], start=1):
        if row.get("horizon") != expected_h:
            raise ValueError("regime horizons must be contiguous from one")
        inverse[expected_h] = float(row["inverse"][coordinate])
        semantic[expected_h] = float(row["semantic"][coordinate])
    return inverse, semantic


def threshold_cost(horizon, threshold, inverse, semantic):
    if horizon <= threshold:
        return inverse[horizon]
    return inverse[threshold] + semantic[horizon - threshold]


def ratio_matrix(rows, coordinate, max_horizon):
    inverse, semantic = lifetime_curves(rows, coordinate, max_horizon)
    result = []
    for horizon in range(1, max_horizon + 1):
        benchmark = min(inverse[horizon], semantic[horizon])
        if not math.isfinite(benchmark) or benchmark <= 0:
            raise ValueError("clairvoyant static benchmark must be finite and positive")
        result.append(tuple(
            threshold_cost(horizon, threshold, inverse, semantic) / benchmark
            for threshold in range(max_horizon + 1)
        ))
    return tuple(result)


def _distribution(size, support, index_key, one_based=False):
    vector = [0.0] * size
    seen = set()
    for item in support:
        raw_index = item[index_key]
        if type(raw_index) is not int:
            raise ValueError("support index must be an integer")
        index = raw_index - 1 if one_based else raw_index
        if not 0 <= index < size or index in seen:
            raise ValueError("support index out of range or duplicated")
        probability = float(item["probability"])
        if not math.isfinite(probability) or probability < 0:
            raise ValueError("support probability must be finite and nonnegative")
        vector[index] = probability
        seen.add(index)
    return tuple(vector)


def _finish_certificate(row_values, column_values, p_sum, q_sum, certificate, tol):
    upper = max(row_values)
    lower = min(column_values)
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
        "primal_upper_bound": upper,
        "dual_lower_bound": lower,
        "certified_gap": gap,
        "normalization_error": normalization_error,
        "reported_primal_error": reported_primal_error,
        "reported_dual_error": reported_dual_error,
    }


def verify_matrix_certificate(matrix, certificate, tol=TOL):
    """Verify one resource-coordinate finite zero-sum game.

    For ratio matrix A[h,t], any threshold mixture p gives
        U = max_h sum_t A[h,t] p[t].
    Any horizon mixture q gives
        L = min_t sum_h q[h] A[h,t].
    Weak duality gives L <= V <= U.  Because the game is finite,
    von Neumann minimax / LP strong duality gives equality at the optimum; a
    small recomputed U-L is therefore a numerical near-optimality certificate.
    """
    if not matrix or not matrix[0]:
        raise ValueError("matrix must be nonempty")
    row_count = len(matrix)
    column_count = len(matrix[0])
    if any(len(row) != column_count for row in matrix):
        raise ValueError("matrix must be rectangular")
    if any(not math.isfinite(value) for row in matrix for value in row):
        raise ValueError("matrix must be finite")

    p = _distribution(column_count, certificate["primal_support"], "threshold")
    q = _distribution(row_count, certificate["dual_support"], "horizon", one_based=True)
    row_values = tuple(
        math.fsum(matrix[h][t] * p[t] for t in range(column_count))
        for h in range(row_count)
    )
    column_values = tuple(
        math.fsum(q[h] * matrix[h][t] for h in range(row_count))
        for t in range(column_count)
    )
    result = _finish_certificate(
        row_values, column_values, math.fsum(p), math.fsum(q), certificate, tol
    )
    result.update({
        "primal_support": certificate["primal_support"],
        "dual_support": certificate["dual_support"],
        "worst_horizons_under_primal": [
            index + 1 for index, value in enumerate(row_values)
            if value >= result["primal_upper_bound"] - 1e-7
        ],
        "binding_thresholds_under_dual": [
            index for index, value in enumerate(column_values)
            if value <= result["dual_lower_bound"] + 1e-7
        ],
    })
    return result


def verify_joint_certificate(matrices, certificate, tol=TOL):
    """Verify one threshold distribution against every primary coordinate.

    Rows of this game are (resource-coordinate, horizon) pairs.  The minimizer
    chooses one threshold distribution before learning either a price vector or
    the realized horizon.  Thus a certified alpha bounds every primary resource
    coordinate simultaneously.
    """
    if set(matrices) != set(COORDINATES):
        raise ValueError("joint game requires exactly the registered coordinates")
    first = matrices[COORDINATES[0]]
    row_count = len(first)
    column_count = len(first[0])
    if any(len(matrices[c]) != row_count for c in COORDINATES):
        raise ValueError("coordinate matrices must have equal horizon count")

    p = _distribution(column_count, certificate["primal_support"], "threshold")
    dual = {}
    dual_sum = 0.0
    for item in certificate["dual_support"]:
        coordinate = item.get("coordinate")
        horizon = item.get("horizon")
        if coordinate not in COORDINATES or type(horizon) is not int or not 1 <= horizon <= row_count:
            raise ValueError("invalid joint dual support row")
        key = (coordinate, horizon)
        if key in dual:
            raise ValueError("duplicate joint dual support row")
        probability = float(item["probability"])
        if not math.isfinite(probability) or probability < 0:
            raise ValueError("joint dual probability must be finite and nonnegative")
        dual[key] = probability
        dual_sum += probability

    row_labels = []
    row_values = []
    for coordinate in COORDINATES:
        matrix = matrices[coordinate]
        for horizon in range(1, row_count + 1):
            row_labels.append((coordinate, horizon))
            row_values.append(math.fsum(
                matrix[horizon - 1][threshold] * p[threshold]
                for threshold in range(column_count)
            ))
    column_values = tuple(
        math.fsum(
            probability * matrices[coordinate][horizon - 1][threshold]
            for (coordinate, horizon), probability in dual.items()
        )
        for threshold in range(column_count)
    )
    result = _finish_certificate(
        tuple(row_values), column_values, math.fsum(p), dual_sum, certificate, tol
    )
    upper = result["primal_upper_bound"]
    lower = result["dual_lower_bound"]
    per_coordinate = {}
    for coordinate in COORDINATES:
        values = [
            value for label, value in zip(row_labels, row_values) if label[0] == coordinate
        ]
        per_coordinate[coordinate] = {
            "max_ratio": max(values),
            "worst_horizons": [
                index + 1 for index, value in enumerate(values)
                if value >= max(values) - 1e-7
            ],
        }
    result.update({
        "primal_support": certificate["primal_support"],
        "dual_support": certificate["dual_support"],
        "worst_coordinate_horizons_under_primal": [
            {"coordinate": coordinate, "horizon": horizon}
            for (coordinate, horizon), value in zip(row_labels, row_values)
            if value >= upper - 1e-7
        ],
        "binding_thresholds_under_dual": [
            index for index, value in enumerate(column_values) if value <= lower + 1e-7
        ],
        "per_coordinate": per_coordinate,
    })
    return result


def price_independent_scalarization_corollary(alpha):
    """State the elementary raw-vector implication used by the joint game.

    If C_i <= alpha * min(A_i,B_i) for every resource i, then for every w>=0,

        w.C <= alpha * sum_i w_i min(A_i,B_i)
             <= alpha * min(w.A, w.B).

    Thus a coordinatewise competitive guarantee against the two static arms is
    sufficient for the same competitive factor under every nonnegative linear
    scalarization, without choosing w after seeing outcomes.
    """
    return {
        "alpha": alpha,
        "holds_for_all_nonnegative_price_vectors": True,
        "benchmark": "best of the same two static exact arms under that price vector",
        "proof": "componentwise bound then sum-of-coordinate-minima <= minimum-of-weighted-sums",
    }


def build_report(regime, certificate):
    if certificate.get("schema") != CERT_SCHEMA:
        raise ValueError("unexpected certificate schema")
    max_horizon = certificate.get("max_horizon")
    if type(max_horizon) is not int or not 1 <= max_horizon <= 10_000:
        raise ValueError("invalid certificate horizon")
    if certificate.get("adversary") != "oblivious horizon; cannot observe private threshold draw":
        raise ValueError("certificate must freeze the oblivious-adversary scope")

    rows = regime["iid_static"]["rows"]
    matrices = {
        coordinate: ratio_matrix(rows, coordinate, max_horizon)
        for coordinate in COORDINATES
    }
    coordinates = {}
    all_coordinate_certified = True
    for coordinate in COORDINATES:
        result = verify_matrix_certificate(
            matrices[coordinate], certificate["coordinates"][coordinate]
        )
        all_coordinate_certified = all_coordinate_certified and result["certified"]
        coordinates[coordinate] = result

    joint = verify_joint_certificate(matrices, certificate["joint_primary_coordinates"])
    all_certified = all_coordinate_certified and joint["certified"]
    joint_alpha = joint["primal_upper_bound"]
    terminal = (
        "RANDOMIZED_TIME_ONLY_SWITCH_SUFFICIENT_R0B_PHASE2B2"
        if all_certified and joint_alpha <= 1.05 + TOL
        else "RANDOMIZED_TIME_ONLY_SWITCH_LEAVES_ONLINE_RESIDUAL_R0B_PHASE2B2"
        if all_certified
        else "RANDOMIZED_SWITCH_CERTIFICATE_FAILED_R0B_PHASE2B2"
    )
    return {
        "schema": REPORT_SCHEMA,
        "study": "Independent finite-game verification of randomized time-only switch parents",
        "scope": {
            "effective_horizon": [1, max_horizon],
            "policy_observation": "elapsed query count + private randomness only",
            "future_horizon_visible": False,
            "future_targets_visible": False,
            "query_features_visible": False,
            "adversary": certificate["adversary"],
            "adaptive_adversary_claimed": False,
            "benchmark": certificate["benchmark"],
            "resource_coordinates": list(COORDINATES),
        },
        "certificate_generator": certificate.get("generator"),
        "verification": {
            "solver_imported": False,
            "numpy_imported": False,
            "scipy_imported": False,
            "method": "recomputed primal upper + dual lower bounds",
            "tolerance": TOL,
            "all_coordinate_certified": all_coordinate_certified,
            "joint_certified": joint["certified"],
            "all_certified": all_certified,
        },
        "coordinate_specific": coordinates,
        "joint_primary_coordinates": joint,
        "price_independent_scalarization": price_independent_scalarization_corollary(joint_alpha),
        "claim_boundary": {
            "finite_zero_sum_minimax_parent": True,
            "near_optimal_within_randomized_time_only_one_way_switch_family": all_certified,
            "joint_policy_is_price_independent_over_registered_linear_scalarizations": joint["certified"],
            "optimal_among_feature_aware_or_multi_switch_policies": False,
            "randomization_guarantee_against_oblivious_horizon_only": True,
            "ml_authorized": False,
            "residual_is_learnable_algorithm_selection": False,
        },
        "terminal": terminal,
    }


def _notice(report):
    return {
        "terminal": report["terminal"],
        "coordinate_values": {
            coordinate: value["primal_upper_bound"]
            for coordinate, value in report["coordinate_specific"].items()
        },
        "joint": {
            "value": report["joint_primary_coordinates"]["primal_upper_bound"],
            "lower": report["joint_primary_coordinates"]["dual_lower_bound"],
            "gap": report["joint_primary_coordinates"]["certified_gap"],
            "support": [
                [item["threshold"], float(item["probability"])]
                for item in report["joint_primary_coordinates"]["primal_support"]
            ],
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
        print(f"::notice title=R0B Phase 2B2 randomized switch certificate::{rendered}")
    else:
        print(rendered)
    if not report["verification"]["all_certified"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
