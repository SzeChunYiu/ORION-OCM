"""R0B Phase-2B2: randomized time-only switch minimax via primal/dual LP.

Research-only.  The finite ratio matrix is solved as a zero-sum game with a
mature LP solver.  We solve primal and dual independently and report numerical
feasibility/duality certificates.  This does not expose the future horizon to the
policy and does not authorize ML.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

import online_switch as S
import regime_sweep as R


TOL = 1e-8
SUPPORT_TOL = 1e-8


def _write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def ratio_matrix(static_rows, coordinate, max_horizon):
    inverse, semantic = S.lifetime_curves(static_rows, coordinate, max_horizon)
    matrix = np.empty((max_horizon, max_horizon + 1), dtype=float)
    for horizon in range(1, max_horizon + 1):
        clairvoyant = min(inverse[horizon], semantic[horizon])
        if clairvoyant <= 0:
            raise ValueError("clairvoyant benchmark must be positive")
        for threshold in range(max_horizon + 1):
            matrix[horizon - 1, threshold] = (
                S.threshold_cost(horizon, threshold, inverse, semantic) / clairvoyant
            )
    return matrix


def solve_zero_sum_minimax(matrix):
    """Solve min_p max_h A[h]p and its dual independently."""
    matrix = np.asarray(matrix, dtype=float)
    if matrix.ndim != 2 or not matrix.size or not np.isfinite(matrix).all():
        raise ValueError("matrix must be nonempty finite 2D")
    rows, cols = matrix.shape

    # Primal variables: p_0..p_{cols-1}, r.
    c_primal = np.zeros(cols + 1)
    c_primal[-1] = 1.0
    a_ub_primal = np.hstack([matrix, -np.ones((rows, 1))])
    b_ub_primal = np.zeros(rows)
    a_eq_primal = np.zeros((1, cols + 1))
    a_eq_primal[0, :cols] = 1.0
    b_eq = np.array([1.0])
    bounds_primal = [(0.0, None)] * cols + [(0.0, None)]
    primal = linprog(
        c_primal,
        A_ub=a_ub_primal,
        b_ub=b_ub_primal,
        A_eq=a_eq_primal,
        b_eq=b_eq,
        bounds=bounds_primal,
        method="highs",
    )

    # Dual variables: q_0..q_{rows-1}, v; maximize v -> minimize -v.
    c_dual = np.zeros(rows + 1)
    c_dual[-1] = -1.0
    a_ub_dual = np.hstack([-matrix.T, np.ones((cols, 1))])
    b_ub_dual = np.zeros(cols)
    a_eq_dual = np.zeros((1, rows + 1))
    a_eq_dual[0, :rows] = 1.0
    bounds_dual = [(0.0, None)] * rows + [(0.0, None)]
    dual = linprog(
        c_dual,
        A_ub=a_ub_dual,
        b_ub=b_ub_dual,
        A_eq=a_eq_dual,
        b_eq=b_eq,
        bounds=bounds_dual,
        method="highs",
    )

    if not primal.success or not dual.success:
        return {
            "certified": False,
            "primal_success": bool(primal.success),
            "dual_success": bool(dual.success),
            "primal_message": primal.message,
            "dual_message": dual.message,
        }

    p = primal.x[:cols]
    r = float(primal.x[-1])
    q = dual.x[:rows]
    v = float(dual.x[-1])
    row_values = matrix @ p
    column_values = q @ matrix

    primal_violation = max(
        0.0,
        float(np.max(row_values - r)),
        abs(float(np.sum(p)) - 1.0),
        max(0.0, -float(np.min(p))),
    )
    dual_violation = max(
        0.0,
        float(np.max(v - column_values)),
        abs(float(np.sum(q)) - 1.0),
        max(0.0, -float(np.min(q))),
    )
    duality_gap = abs(r - v)
    certified = max(primal_violation, dual_violation, duality_gap) <= TOL

    p_support = [
        {"threshold": index, "probability": float(probability)}
        for index, probability in enumerate(p)
        if probability > SUPPORT_TOL
    ]
    q_support = [
        {"horizon": index + 1, "probability": float(probability)}
        for index, probability in enumerate(q)
        if probability > SUPPORT_TOL
    ]
    worst_rows = np.flatnonzero(row_values >= r - 1e-7)
    binding_columns = np.flatnonzero(column_values <= v + 1e-7)

    return {
        "certified": certified,
        "value_primal": r,
        "value_dual": v,
        "duality_gap": duality_gap,
        "primal_max_violation": primal_violation,
        "dual_max_violation": dual_violation,
        "primal_support": p_support,
        "dual_support": q_support,
        "worst_horizons_under_primal": [int(index + 1) for index in worst_rows],
        "binding_thresholds_under_dual": [int(index) for index in binding_columns],
        "mean_ratio_under_uniform_horizon": float(np.mean(row_values)),
        "max_ratio_recomputed": float(np.max(row_values)),
        "min_dual_column_recomputed": float(np.min(column_values)),
    }


def build_report(max_horizon=R.MAX_HORIZON):
    _, _, _, static_rows, _, _ = R.calibrate()
    coordinates = {}
    all_certified = True
    values = []
    support_signatures = []
    for coordinate in R.PHASE_COORDS:
        matrix = ratio_matrix(static_rows, coordinate, max_horizon)
        solution = solve_zero_sum_minimax(matrix)
        all_certified = all_certified and solution.get("certified", False)
        if solution.get("certified", False):
            values.append(solution["value_primal"])
            support_signatures.append(tuple(
                item["threshold"] for item in solution["primal_support"]
            ))
        coordinates[coordinate] = {
            "matrix_shape": list(matrix.shape),
            "solution": solution,
        }

    if not all_certified:
        terminal = "RANDOMIZED_SWITCH_LP_CANNOT_CERTIFY"
    elif max(values) <= 1.05 + TOL:
        terminal = "RANDOMIZED_TIME_ONLY_SWITCH_SUFFICIENT_R0B_PHASE2B2"
    else:
        terminal = "RANDOMIZED_TIME_ONLY_SWITCH_LEAVES_ONLINE_RESIDUAL_R0B_PHASE2B2"

    return {
        "schema": "ocm.residual-strategy-regime.r0b.phase2b2.randomized-switch.v1",
        "study": "Finite zero-sum randomized switch-time minimax; no ML",
        "scope": {
            "effective_horizon": [1, max_horizon],
            "demand": "iid uniform frozen 142-target population",
            "policy_observation_before_switch": "elapsed query count + private randomness only",
            "future_horizon_visible": False,
            "future_targets_visible": False,
            "query_features_visible_to_switch_policy": False,
            "switches": "at most one, inverse -> semantic",
            "benchmark": "clairvoyant best static exact arm at realized horizon",
            "resource_coordinates": list(R.PHASE_COORDS),
        },
        "solver": {
            "library": "scipy.optimize.linprog",
            "method": "highs",
            "numerical_tolerance": TOL,
            "strong_duality_parent": "finite zero-sum minimax / linear programming duality",
        },
        "coordinates": coordinates,
        "cross_coordinate": {
            "same_threshold_support": (
                len(set(support_signatures)) == 1 if support_signatures else False
            ),
            "price_independent_policy_claimed": False,
        },
        "claim_boundary": {
            "exact_real_arithmetic_certificate": False,
            "independent_primal_dual_numerical_certificate": True,
            "optimal_within_randomized_time_only_one_way_switch_family": all_certified,
            "optimal_among_target_feature_aware_or_multi_switch_policies": False,
            "residual_is_learnable_algorithm_selection": False,
            "ml_authorized": False,
            "next_question_if_residual": (
                "which legal observation about stopping/reuse or strategy state can reduce the minimax gap, "
                "and is acquiring it cheaper than the gap?"
            ),
        },
        "terminal": terminal,
    }


def _notice(report):
    compact = {}
    for coordinate, value in report["coordinates"].items():
        solution = value["solution"]
        compact[coordinate] = {
            "certified": solution.get("certified", False),
            "value": solution.get("value_primal"),
            "gap": solution.get("duality_gap"),
            "support": [
                [item["threshold"], round(item["probability"], 8)]
                for item in solution.get("primal_support", [])
            ],
            "dual_horizons": [
                [item["horizon"], round(item["probability"], 8)]
                for item in solution.get("dual_support", [])
            ],
        }
    return {"terminal": report["terminal"], "coordinates": compact}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--max-horizon", type=int, default=R.MAX_HORIZON)
    parser.add_argument("--github-notice", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.max_horizon <= R.MAX_HORIZON:
        raise SystemExit(f"--max-horizon must be in 1..{R.MAX_HORIZON}")
    report = build_report(args.max_horizon)
    _write_json(args.out, report)
    rendered = json.dumps(_notice(report), sort_keys=True, separators=(",", ":"))
    if args.github_notice:
        print(f"::notice title=R0B Phase 2B2 randomized switch minimax::{rendered}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
