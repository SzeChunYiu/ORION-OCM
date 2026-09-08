"""R0B Phase-2B0: exact fixed-frontier investment reduction; no ML.

This does NOT implement a learned horizon predictor or claim that the existing
semantic donor is ordinary ski rental.  It constructs a stronger exact parent:
prebuild semantic frontier f, prohibit target-triggered semantic expansion, and
use exact inverse fallback outside the frontier.  Under the frozen iid demand
model, each fixed frontier has setup b_f and recurring expected rate r_f.

If the Pareto-pruned points have increasing setup and decreasing rate, the
expected-cost problem satisfies the additive multislope geometry in
FORMAL_DECISION_CORE_V2 Theorem 15 on the registered phase coordinate.  That
licenses importing ordinary online-investment parents for the UNKNOWN-HORIZON
tranche; it does not license ML.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import decision_core as D
import regime_sweep as R


def _write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def fixed_frontier_points(tasks, profile, inverse, coordinate):
    """Return every (setup, expected recurring rate, frontier) point."""
    points = []
    n = len(tasks)
    for frontier in range(profile["frontier_transitions"] + 1):
        setup = float(profile["build"][frontier].get(coordinate, 0))
        recurring = 0.0
        for task in tasks:
            fingerprint = task.fingerprint
            if profile["ranks"][fingerprint] <= frontier:
                recurring += profile["hit"][fingerprint].get(coordinate, 0)
            else:
                recurring += inverse[fingerprint].get(coordinate, 0)
        points.append((setup, recurring / n, frontier))
    return tuple(points)


def efficient_slopes(points):
    """Collapse exact point duplicates and remove Pareto-dominated levels."""
    # If two frontiers have exactly the same scalar setup/rate, keep the larger
    # frontier as the more informative non-authoritative state at no extra cost.
    unique = {}
    for setup, recurring, frontier in points:
        key = (setup, recurring)
        unique[key] = max(frontier, unique.get(key, frontier))
    collapsed = tuple((setup, recurring, frontier)
                      for (setup, recurring), frontier in unique.items())
    return D.prune_dominated_slopes(collapsed)


def offline_envelope(slopes, max_horizon=R.MAX_HORIZON):
    """Best known-horizon fixed-frontier parent b_f + H r_f."""
    rows = []
    for horizon in range(1, max_horizon + 1):
        scored = [
            (setup + horizon * recurring, setup, recurring, frontier)
            for setup, recurring, frontier in slopes
        ]
        total, setup, recurring, frontier = min(
            scored, key=lambda row: (row[0], row[1], row[3])
        )
        rows.append({
            "horizon": horizon,
            "frontier": frontier,
            "setup": setup,
            "recurring_rate": recurring,
            "expected_cost": total,
        })
    return rows


def envelope_breakpoints(rows):
    changes = []
    previous = None
    for row in rows:
        if row["frontier"] != previous:
            changes.append({
                "horizon": row["horizon"],
                "frontier": row["frontier"],
                "setup": row["setup"],
                "recurring_rate": row["recurring_rate"],
            })
            previous = row["frontier"]
    return changes


def compare_known_horizon_parent(rows, static_rows, oracle_rows, coordinate):
    by_horizon_static = {row["horizon"]: row for row in static_rows}
    by_horizon_oracle = {row["horizon"]: row for row in oracle_rows}
    result = []
    best_parent_gap = {"fraction": 0.0, "horizon": 1}
    max_oracle_residual = {"fraction": 0.0, "horizon": 1}
    for row in rows:
        horizon = row["horizon"]
        static = by_horizon_static[horizon]
        best_static = min(static["semantic"][coordinate], static["inverse"][coordinate])
        parent = row["expected_cost"]
        oracle = by_horizon_oracle[horizon]["oracle"]
        static_gain = max(0.0, (best_static - parent) / best_static) if best_static else 0.0
        oracle_gap = max(0.0, (parent - oracle) / parent) if parent else 0.0
        if static_gain > best_parent_gap["fraction"]:
            best_parent_gap = {"fraction": static_gain, "horizon": horizon}
        if oracle_gap > max_oracle_residual["fraction"]:
            max_oracle_residual = {"fraction": oracle_gap, "horizon": horizon}
        result.append({
            "horizon": horizon,
            "best_static": best_static,
            "fixed_frontier_parent": parent,
            "full_information_oracle": oracle,
            "gain_over_best_static_fraction": static_gain,
            "remaining_oracle_gap_fraction": oracle_gap,
        })
    return result, best_parent_gap, max_oracle_residual


def build_report(max_horizon=R.MAX_HORIZON):
    tasks, profile, inverse, static_rows, _, oracle = R.calibrate()
    coordinates = {}
    all_multislope = True
    for coordinate in R.PHASE_COORDS:
        points = fixed_frontier_points(tasks, profile, inverse, coordinate)
        slopes = efficient_slopes(points)
        monotone = D.multislope_monotone(slopes)
        all_multislope = all_multislope and monotone
        envelope = offline_envelope(slopes, max_horizon=max_horizon)
        comparisons, max_static_gain, max_oracle_gap = compare_known_horizon_parent(
            envelope,
            static_rows[:max_horizon],
            oracle[coordinate]["rows"][:max_horizon],
            coordinate,
        )
        coordinates[coordinate] = {
            "raw_frontier_points": len(points),
            "pareto_slopes": [
                {"setup": setup, "recurring_rate": recurring, "frontier": frontier}
                for setup, recurring, frontier in slopes
            ],
            "multislope_monotone": monotone,
            "breakpoints": envelope_breakpoints(envelope),
            "known_horizon_rows": envelope,
            "comparison_rows": comparisons,
            "max_gain_over_best_static": max_static_gain,
            "max_remaining_gap_to_full_information_oracle": max_oracle_gap,
        }

    terminal = (
        "EXPECTED_MULTISLOPE_REDUCTION_SUPPORTED_R0B_PHASE2B0"
        if all_multislope
        else "GENERAL_CAPITAL_INVESTMENT_PARENT_REQUIRED_R0B_PHASE2B0"
    )
    return {
        "schema": "ocm.residual-strategy-regime.r0b.phase2b0.investment.v1",
        "study": "Exact fixed-frontier expected investment reduction; no ML",
        "scope": {
            "demand": "iid uniform frozen 142-target population",
            "investment_decision_sees_future_targets": False,
            "semantic_target_triggered_expansion": False,
            "out_of_frontier_fallback": "exact inverse parent",
            "known_horizon_envelope_is_deployable_without_target_features": True,
            "unknown_horizon_competitive_policy_implemented": False,
            "runtime_prebuild_parent_executed": False,
            "resource_coordinates": list(R.PHASE_COORDS),
        },
        "coordinates": coordinates,
        "claim_boundary": {
            "exact_reduction_is_expected_cost_only": True,
            "target_sequence_adversarial_multislope_claimed": False,
            "ml_authorized": False,
            "next_parent": (
                "multislope/capital-investment competitive policy"
                if all_multislope
                else "general finite-state capital-investment/online-control policy"
            ),
        },
        "terminal": terminal,
    }


def _notice(report):
    compact = {
        coordinate: {
            "slopes": len(value["pareto_slopes"]),
            "multislope": value["multislope_monotone"],
            "breakpoints": [
                [row["horizon"], row["frontier"]] for row in value["breakpoints"]
            ],
            "max_static_gain": value["max_gain_over_best_static"],
            "max_oracle_gap": value["max_remaining_gap_to_full_information_oracle"],
        }
        for coordinate, value in report["coordinates"].items()
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
        print(f"::notice title=R0B Phase 2B0 investment reduction::{rendered}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
