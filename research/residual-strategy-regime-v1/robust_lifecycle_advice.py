"""R0B lifecycle advice gate: exact robust LP over a decision-region bit; no ML.

The advice target is the identity of the cheaper static exact arm at the realized
effective lifetime, not target identity and not the full horizon.  For a declared
per-horizon error bound epsilon, two advice-conditioned distributions over the
existing one-way switch thresholds are optimized against the worst legal advice
error.  This is a finite consistency/robustness parent, not a predictor.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

import online_switch as S
import randomized_switch_lp as G
import regime_sweep as R


TOL = 1e-8
SUPPORT_TOL = 1e-8
ERROR_GRID = (0.0, 0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0)
TARGET_RATIOS = (1.01, 1.02, 1.05, 1.10, 1.20)


def _write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def decision_bits(static_rows, coordinate, max_horizon):
    """Return 0=inverse, 1=semantic for the two-static-arm benchmark."""
    bits = []
    for row in static_rows[:max_horizon]:
        inverse = row["inverse"][coordinate]
        semantic = row["semantic"][coordinate]
        bits.append(0 if inverse <= semantic else 1)
    return tuple(bits)


def monotone_crossover(bits):
    """Return first semantic-winning horizon if bits are 0*1*, else None."""
    seen_one = False
    first = None
    for index, bit in enumerate(bits, start=1):
        if bit not in (0, 1):
            raise ValueError("decision bits must be binary")
        if bit == 1:
            if not seen_one:
                first = index
            seen_one = True
        elif seen_one:
            return None
    return first


def solve_robust_advice(matrix, bits, epsilon):
    """Minimax LP for a bit correct with probability at least 1-epsilon per row."""
    matrix = np.asarray(matrix, dtype=float)
    bits = tuple(bits)
    if matrix.ndim != 2 or not matrix.size or not np.isfinite(matrix).all():
        raise ValueError("matrix must be nonempty finite 2D")
    if len(bits) != matrix.shape[0] or any(bit not in (0, 1) for bit in bits):
        raise ValueError("one binary decision bit is required per matrix row")
    if not 0.0 <= epsilon <= 1.0:
        raise ValueError("epsilon must be in [0,1]")

    rows, thresholds = matrix.shape
    # Variables: p0[thresholds], p1[thresholds], rho.
    variables = 2 * thresholds + 1
    objective = np.zeros(variables)
    objective[-1] = 1.0
    inequalities = []

    for row_index, bit in enumerate(bits):
        costs = matrix[row_index]

        # q=0 endpoint: advice is correct.
        correct = np.zeros(variables)
        start = bit * thresholds
        correct[start:start + thresholds] = costs
        correct[-1] = -1.0
        inequalities.append(correct)

        # q=epsilon endpoint.  Expected ratio is affine in q, so endpoints
        # certify every q in [0,epsilon].
        mixed = np.zeros(variables)
        right = bit * thresholds
        wrong = (1 - bit) * thresholds
        mixed[right:right + thresholds] = (1.0 - epsilon) * costs
        mixed[wrong:wrong + thresholds] = epsilon * costs
        mixed[-1] = -1.0
        inequalities.append(mixed)

    equality = np.zeros((2, variables))
    equality[0, :thresholds] = 1.0
    equality[1, thresholds:2 * thresholds] = 1.0
    result = linprog(
        objective,
        A_ub=np.asarray(inequalities),
        b_ub=np.zeros(len(inequalities)),
        A_eq=equality,
        b_eq=np.ones(2),
        bounds=[(0.0, None)] * (2 * thresholds) + [(0.0, None)],
        method="highs",
    )
    if not result.success:
        return {
            "certified": False,
            "message": result.message,
        }

    p0 = result.x[:thresholds]
    p1 = result.x[thresholds:2 * thresholds]
    rho = float(result.x[-1])

    violations = []
    for row_index, bit in enumerate(bits):
        costs = matrix[row_index]
        correct_value = float(costs @ (p0 if bit == 0 else p1))
        wrong_value = float(costs @ (p1 if bit == 0 else p0))
        mixed_value = (1.0 - epsilon) * correct_value + epsilon * wrong_value
        violations.extend((correct_value - rho, mixed_value - rho))
    max_violation = max(
        0.0,
        max(violations),
        abs(float(np.sum(p0)) - 1.0),
        abs(float(np.sum(p1)) - 1.0),
        max(0.0, -float(np.min(p0))),
        max(0.0, -float(np.min(p1))),
    )

    def support(probabilities):
        return [
            {"threshold": index, "probability": float(value)}
            for index, value in enumerate(probabilities)
            if value > SUPPORT_TOL
        ]

    return {
        "certified": max_violation <= TOL,
        "ratio": rho,
        "max_primal_violation": max_violation,
        "advice_0_threshold_support": support(p0),
        "advice_1_threshold_support": support(p1),
    }


def max_error_for_target(matrix, bits, target_ratio, iterations=32):
    """Largest epsilon whose robust optimum is at most target_ratio."""
    if target_ratio < 1.0:
        raise ValueError("target ratio must be at least one")
    lo, hi = 0.0, 1.0
    hi_solution = solve_robust_advice(matrix, bits, hi)
    if hi_solution.get("certified") and hi_solution["ratio"] <= target_ratio + TOL:
        return {"epsilon": 1.0, "ratio": hi_solution["ratio"]}
    for _ in range(iterations):
        mid = (lo + hi) / 2.0
        solution = solve_robust_advice(matrix, bits, mid)
        if not solution.get("certified"):
            raise RuntimeError("robust advice LP failed during bisection")
        if solution["ratio"] <= target_ratio:
            lo = mid
        else:
            hi = mid
    solution = solve_robust_advice(matrix, bits, lo)
    return {"epsilon": lo, "ratio": solution["ratio"]}


def build_report(max_horizon=R.MAX_HORIZON):
    _, _, _, static_rows, _, _ = R.calibrate()
    coordinates = {}
    all_controls = True

    for coordinate in R.PHASE_COORDS:
        matrix = G.ratio_matrix(static_rows, coordinate, max_horizon)
        bits = decision_bits(static_rows, coordinate, max_horizon)
        crossover = monotone_crossover(bits)
        no_advice = G.solve_zero_sum_minimax(matrix)
        perfect = solve_robust_advice(matrix, bits, 0.0)
        arbitrary = solve_robust_advice(matrix, bits, 1.0)

        endpoint_controls = {
            "perfect_advice_ratio_one": (
                perfect.get("certified", False)
                and abs(perfect["ratio"] - 1.0) <= TOL
            ),
            "arbitrary_advice_equals_no_advice": (
                arbitrary.get("certified", False)
                and no_advice.get("certified", False)
                and abs(arbitrary["ratio"] - no_advice["value_primal"]) <= TOL
            ),
        }
        all_controls = all_controls and all(endpoint_controls.values())

        grid = []
        previous = -float("inf")
        monotone = True
        for epsilon in ERROR_GRID:
            solution = solve_robust_advice(matrix, bits, epsilon)
            ratio = solution.get("ratio")
            if solution.get("certified", False) and ratio is not None:
                monotone = monotone and ratio + TOL >= previous
                previous = ratio
            else:
                monotone = False
            grid.append({"epsilon": epsilon, "solution": solution})
        all_controls = all_controls and monotone

        target_bounds = {
            f"ratio_{target:.2f}": max_error_for_target(matrix, bits, target)
            for target in TARGET_RATIOS
        }

        coordinates[coordinate] = {
            "decision_region": {
                "monotone_crossover": crossover,
                "inverse_region_size": bits.count(0),
                "semantic_region_size": bits.count(1),
                "perfect_advice_bits": 1,
            },
            "no_advice_randomized_ratio": no_advice.get("value_primal"),
            "endpoint_controls": endpoint_controls,
            "error_ratio_grid": grid,
            "target_error_bounds": target_bounds,
            "ratio_monotone_in_error_allowance": monotone,
        }

    terminal = (
        "LEARNED_ROUTER_NOT_AUTHORIZED_R0B_LIFECYCLE_ADVICE_GATE"
        if all_controls
        else "LIFECYCLE_ADVICE_GATE_CONTROL_FAILURE"
    )
    return {
        "schema": "ocm.residual-strategy-regime.r0b.lifecycle-advice.v1",
        "study": "Robust decision-region advice LP; no predictor and no ML",
        "scope": {
            "effective_horizon": [1, max_horizon],
            "demand": "iid uniform frozen 142-target population",
            "advice": "one bit naming the cheaper two-static-arm decision region",
            "advice_error_contract": "per-horizon P(correct|H) >= 1-epsilon",
            "policy_family": "advice-conditioned randomized one-way switch thresholds",
            "future_horizon_visible": False,
            "future_targets_visible": False,
            "target_features_visible": False,
            "resource_coordinates": list(R.PHASE_COORDS),
        },
        "coordinates": coordinates,
        "claim_boundary": {
            "perfect_bit_observable_for_free": False,
            "predictor_trained": False,
            "price_independent_policy_claimed": False,
            "robust_lp_optimal_only_within_declared_policy_family": True,
            "feature_acquisition_and_prediction_cost_charged_here": False,
            "next_gate": "measure a legal lifecycle signal, calibration, and complete acquisition/maintenance cost",
            "ml_authorized": False,
        },
        "terminal": terminal,
    }


def _notice(report):
    summary = {}
    for coordinate, value in report["coordinates"].items():
        summary[coordinate] = {
            "crossover": value["decision_region"]["monotone_crossover"],
            "no_advice_ratio": value["no_advice_randomized_ratio"],
            "max_epsilon_for_1.05": value["target_error_bounds"]["ratio_1.05"]["epsilon"],
            "controls": value["endpoint_controls"],
        }
    return {"terminal": report["terminal"], "coordinates": summary}


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
        print(f"::notice title=R0B lifecycle advice gate::{rendered}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
