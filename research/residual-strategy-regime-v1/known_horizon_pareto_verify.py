"""Verify the all-horizon raw-resource Pareto frontier of one-way thresholds.

For every source-derived horizon H, enumerate all inverse-then-semantic thresholds
and remove raw-vector dominated points across the three registered primary
coordinates.  The current donor should expose no Pareto-efficient intermediate
threshold: only all-inverse and/or all-semantic survive.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import randomized_switch_verify as R


REPORT_SCHEMA = "ocm.residual-strategy-regime.r0b.known-horizon-pareto.verify.v1"


def _load(path):
    return json.loads(Path(path).read_text())


def _write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def threshold_vectors(rows, horizon, max_horizon):
    curves = {
        coordinate: R.lifetime_curves(rows, coordinate, max_horizon)
        for coordinate in R.COORDINATES
    }
    vectors = {}
    for threshold in range(horizon + 1):
        vector = tuple(
            R.threshold_cost(horizon, threshold, *curves[coordinate])
            for coordinate in R.COORDINATES
        )
        # threshold=H canonicalizes all thresholds >=H, which are all-inverse.
        vectors[threshold] = vector
    return vectors


def dominates(left, right, tol=1e-10):
    weak = all(a <= b + tol for a, b in zip(left, right))
    strict = any(a < b - tol for a, b in zip(left, right))
    return weak and strict


def pareto_thresholds(vectors):
    result = []
    for threshold, vector in vectors.items():
        if not any(
            other != threshold and dominates(other_vector, vector)
            for other, other_vector in vectors.items()
        ):
            result.append(threshold)
    return tuple(sorted(result))


def build_report(regime, max_horizon=142):
    rows = regime["iid_static"]["rows"]
    if len(rows) < max_horizon:
        raise ValueError("regime artifact too short")
    horizons = []
    no_intermediate = True
    for horizon in range(1, max_horizon + 1):
        vectors = threshold_vectors(rows, horizon, max_horizon)
        frontier = pareto_thresholds(vectors)
        allowed_static = {0, horizon}
        intermediate = [threshold for threshold in frontier if threshold not in allowed_static]
        no_intermediate = no_intermediate and not intermediate
        horizons.append({
            "horizon": horizon,
            "pareto_thresholds": list(frontier),
            "intermediate_pareto_thresholds": intermediate,
            "semantic_vector": dict(zip(R.COORDINATES, vectors[0])),
            "inverse_vector": dict(zip(R.COORDINATES, vectors[horizon])),
        })

    expected_pattern = all(
        row["pareto_thresholds"] == (
            [row["horizon"]] if row["horizon"] <= 3
            else [0, row["horizon"]] if row["horizon"] <= 8
            else [0]
        )
        for row in horizons
    )
    return {
        "schema": REPORT_SCHEMA,
        "study": "All-horizon Pareto audit of deterministic one-way switch thresholds",
        "scope": {
            "effective_horizon": [1, max_horizon],
            "raw_resource_coordinates": list(R.COORDINATES),
            "policy_family": "deterministic one-way inverse-to-semantic threshold",
            "post_hoc_scalarization_used": False,
            "ml_used": False,
        },
        "horizons": horizons,
        "summary": {
            "no_intermediate_threshold_is_pareto_efficient": no_intermediate,
            "source_pattern_inverse_only_through": 3 if expected_pattern else None,
            "source_pattern_two_static_arms_band": [4, 8] if expected_pattern else None,
            "source_pattern_semantic_only_from": 9 if expected_pattern else None,
            "expected_pattern_verified": expected_pattern,
        },
        "claim_boundary": {
            "known_horizon_intermediate_switch_adds_pareto_point": False,
            "randomized_convex_combinations_are_pareto_dominated": False,
            "unknown_horizon_switching_is_useless": False,
            "learned_router_authorized": False,
        },
        "terminal": (
            "INTERMEDIATE_SWITCH_PARETO_DOMINATED_KNOWN_H_R0B"
            if no_intermediate and expected_pattern
            else "KNOWN_HORIZON_PARETO_PATTERN_CHANGED_R0B"
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--regime", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--max-horizon", type=int, default=142)
    parser.add_argument("--github-notice", action="store_true")
    args = parser.parse_args()
    report = build_report(_load(args.regime), args.max_horizon)
    _write(args.out, report)
    rendered = json.dumps(
        {"terminal": report["terminal"], "summary": report["summary"]},
        sort_keys=True,
        separators=(",", ":"),
    )
    if args.github_notice:
        print(f"::notice title=R0B known-horizon Pareto audit::{rendered}")
    else:
        print(rendered)
    if report["terminal"] != "INTERMEDIATE_SWITCH_PARETO_DOMINATED_KNOWN_H_R0B":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
