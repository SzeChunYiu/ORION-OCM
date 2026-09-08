"""R0B Phase-2B1: exact deterministic online switch threshold; no ML.

Use inverse for the first tau queries of an effective stable lifetime, then switch
once to the incumbent target-triggered persistent semantic arm.  The controller
never sees the future horizon or future targets.  We exhaustively minimize the
worst competitive ratio over H=1..Hmax against the clairvoyant best *static* exact
arm for each declared resource coordinate.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import regime_sweep as R


EPS = 1e-12


def _write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def lifetime_curves(static_rows, coordinate, max_horizon):
    inverse = {0: 0.0}
    semantic = {0: 0.0}
    for row in static_rows[:max_horizon]:
        h = row["horizon"]
        inverse[h] = float(row["inverse"][coordinate])
        semantic[h] = float(row["semantic"][coordinate])
    return inverse, semantic


def threshold_cost(horizon, threshold, inverse, semantic):
    if horizon <= threshold:
        return inverse[horizon]
    return inverse[threshold] + semantic[horizon - threshold]


def evaluate_threshold(threshold, inverse, semantic, max_horizon):
    rows = []
    worst_ratio = 1.0
    worst_horizon = 1
    worst_regret_fraction = 0.0
    worst_regret_horizon = 1
    mean_ratio = 0.0
    for horizon in range(1, max_horizon + 1):
        cost = threshold_cost(horizon, threshold, inverse, semantic)
        clairvoyant = min(inverse[horizon], semantic[horizon])
        ratio = cost / clairvoyant if clairvoyant else 1.0
        regret_fraction = ((cost - clairvoyant) / clairvoyant) if clairvoyant else 0.0
        mean_ratio += ratio
        if ratio > worst_ratio + EPS:
            worst_ratio = ratio
            worst_horizon = horizon
        if regret_fraction > worst_regret_fraction + EPS:
            worst_regret_fraction = regret_fraction
            worst_regret_horizon = horizon
        rows.append({
            "horizon": horizon,
            "threshold_cost": cost,
            "clairvoyant_best_static": clairvoyant,
            "competitive_ratio": ratio,
            "regret_fraction": regret_fraction,
        })
    return {
        "threshold": threshold,
        "worst_competitive_ratio": worst_ratio,
        "worst_ratio_horizon": worst_horizon,
        "worst_regret_fraction": worst_regret_fraction,
        "worst_regret_horizon": worst_regret_horizon,
        "mean_competitive_ratio": mean_ratio / max_horizon,
        "rows": rows,
    }


def best_deterministic_threshold(inverse, semantic, max_horizon):
    candidates = [
        evaluate_threshold(threshold, inverse, semantic, max_horizon)
        for threshold in range(max_horizon + 1)
    ]
    return min(
        candidates,
        key=lambda row: (
            row["worst_competitive_ratio"],
            row["mean_competitive_ratio"],
            row["threshold"],
        ),
    ), candidates


def crossover_horizons(inverse, semantic, max_horizon):
    inverse_better = []
    semantic_better = []
    ties = []
    for h in range(1, max_horizon + 1):
        if inverse[h] + EPS < semantic[h]:
            inverse_better.append(h)
        elif semantic[h] + EPS < inverse[h]:
            semantic_better.append(h)
        else:
            ties.append(h)
    return {
        "inverse_better": inverse_better,
        "semantic_better": semantic_better,
        "ties": ties,
    }


def build_report(max_horizon=R.MAX_HORIZON):
    _, _, _, static_rows, _, _ = R.calibrate()
    coordinates = {}
    best_thresholds = []
    for coordinate in R.PHASE_COORDS:
        inverse, semantic = lifetime_curves(static_rows, coordinate, max_horizon)
        best, candidates = best_deterministic_threshold(inverse, semantic, max_horizon)
        best_thresholds.append(best["threshold"])
        coordinates[coordinate] = {
            "best_threshold": best,
            "all_threshold_summaries": [
                {key: value for key, value in row.items() if key != "rows"}
                for row in candidates
            ],
            "static_crossover": crossover_horizons(inverse, semantic, max_horizon),
        }

    same_threshold = len(set(best_thresholds)) == 1
    worst_ratio = max(
        value["best_threshold"]["worst_competitive_ratio"]
        for value in coordinates.values()
    )
    terminal = (
        "EXACT_TIME_THRESHOLD_SUFFICIENT_R0B_PHASE2B1"
        if worst_ratio <= 1.05 + EPS
        else "DETERMINISTIC_THRESHOLD_LEAVES_ONLINE_RESIDUAL_R0B_PHASE2B1"
    )
    return {
        "schema": "ocm.residual-strategy-regime.r0b.phase2b1.online-switch.v1",
        "study": "Exact bounded unknown-horizon deterministic switch parent; no ML",
        "scope": {
            "effective_horizon": [1, max_horizon],
            "demand": "iid uniform frozen 142-target population",
            "future_horizon_visible_to_policy": False,
            "future_targets_visible_to_policy": False,
            "pre_switch_arm": "exact stateless inverse",
            "post_switch_arm": "incumbent target-triggered persistent semantic from cold",
            "switches": "at most one, inverse -> semantic",
            "randomized_threshold": False,
            "reset_invalidation_sweep": False,
            "resource_coordinates": list(R.PHASE_COORDS),
        },
        "coordinates": coordinates,
        "cross_coordinate": {
            "same_optimal_threshold": same_threshold,
            "best_thresholds": dict(zip(R.PHASE_COORDS, best_thresholds)),
            "price_independent_threshold_claimed": same_threshold,
        },
        "claim_boundary": {
            "clairvoyant_benchmark_deployable": False,
            "optimal_among_arbitrary_online_policies": False,
            "optimal_within_deterministic_time_only_one_way_switch_family": True,
            "five_percent_terminal_is_protocol_threshold_not_general_theorem": True,
            "ml_authorized": False,
            "next_parent_if_residual": "randomized switch-time / stronger online stopping parent before demand prediction",
        },
        "terminal": terminal,
    }


def _notice(report):
    return {
        "terminal": report["terminal"],
        "coordinates": {
            coordinate: {
                "threshold": value["best_threshold"]["threshold"],
                "worst_ratio": value["best_threshold"]["worst_competitive_ratio"],
                "worst_horizon": value["best_threshold"]["worst_ratio_horizon"],
            }
            for coordinate, value in report["coordinates"].items()
        },
        "same_threshold": report["cross_coordinate"]["same_optimal_threshold"],
    }


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
        print(f"::notice title=R0B Phase 2B1 online switch::{rendered}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
