"""Verify the exact known-horizon linear-objective coverage set for R0B.

The verifier consumes the source-derived regime artifact, enumerates all
one-way deterministic thresholds, checks raw-resource Pareto dominance, and
verifies which surviving static arms are supported by registered basis-price
objectives.  Stdlib only; no ML and no post-hoc scalar objective is selected.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import known_horizon_pareto_verify as P
import randomized_switch_verify as R


REPORT_SCHEMA = "ocm.residual-strategy-regime.r0b.objective-coverage.verify.v1"


def _load(path):
    return json.loads(Path(path).read_text())


def _write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def basis_preferences(vectors, horizon):
    semantic = vectors[0]
    inverse = vectors[horizon]
    result = {}
    for index, coordinate in enumerate(R.COORDINATES):
        if semantic[index] < inverse[index]:
            result[coordinate] = "semantic"
        elif inverse[index] < semantic[index]:
            result[coordinate] = "inverse"
        else:
            result[coordinate] = "tie"
    return result


def expected_coverage(horizon):
    if horizon <= 3:
        return ("inverse",)
    if horizon <= 8:
        return ("inverse", "semantic")
    return ("semantic",)


def build_report(regime, max_horizon=142):
    rows = regime["iid_static"]["rows"]
    horizons = []
    all_verified = True
    for horizon in range(1, max_horizon + 1):
        vectors = P.threshold_vectors(rows, horizon, max_horizon)
        pareto = P.pareto_thresholds(vectors)
        intermediate = tuple(
            threshold for threshold in pareto if threshold not in (0, horizon)
        )
        basis = basis_preferences(vectors, horizon)
        supported = []
        if any(choice in ("inverse", "tie") for choice in basis.values()):
            # A tie alone is not enough to keep a dominated point, so require it
            # to be on the Pareto frontier as well.
            if horizon in pareto:
                supported.append("inverse")
        if any(choice in ("semantic", "tie") for choice in basis.values()):
            if 0 in pareto:
                supported.append("semantic")
        supported = tuple(sorted(set(supported)))
        expected = tuple(sorted(expected_coverage(horizon)))
        verified = not intermediate and supported == expected
        all_verified = all_verified and verified
        horizons.append({
            "horizon": horizon,
            "pareto_thresholds": list(pareto),
            "basis_price_preferences": basis,
            "linear_objective_coverage_set": list(supported),
            "expected_coverage_set": list(expected),
            "verified": verified,
        })

    return {
        "schema": REPORT_SCHEMA,
        "study": "Exact known-horizon coverage set for nonnegative linear resource objectives",
        "scope": {
            "effective_horizon": [1, max_horizon],
            "registered_primary_resources": list(R.COORDINATES),
            "objective_family": "nonnegative linear scalarizations",
            "objective_revealed_before_action": True,
            "policy_family": "deterministic one-way inverse-to-semantic thresholds",
            "ml_used": False,
        },
        "horizons": horizons,
        "summary": {
            "all_verified": all_verified,
            "coverage_set_size_at_most": max(len(row["linear_objective_coverage_set"]) for row in horizons),
            "inverse_only_through": 3 if all_verified else None,
            "two_arm_coverage_band": [4, 8] if all_verified else None,
            "semantic_only_from": 9 if all_verified else None,
        },
        "theorem": {
            "known_linear_objective_randomization_needed": False,
            "reason": "expected scalar cost of a mixture is a convex combination of deterministic scalar costs",
            "coverage_parent": "convex coverage set / Pareto set under linear scalarization",
        },
        "claim_boundary": {
            "objective_known_or_declared": True,
            "unknown_objective_robust_minimax_equated_with_this_problem": False,
            "learned_objective_inference_authorized": False,
            "learned_router_authorized": False,
        },
        "terminal": (
            "EXACT_COVERAGE_SET_SUFFICIENT_FOR_KNOWN_H_OBJECTIVE_SELECTION_R0B"
            if all_verified
            else "OBJECTIVE_COVERAGE_PATTERN_CHANGED_R0B"
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
    notice = {"terminal": report["terminal"], "summary": report["summary"]}
    rendered = json.dumps(notice, sort_keys=True, separators=(",", ":"))
    if args.github_notice:
        print(f"::notice title=R0B objective coverage set::{rendered}")
    else:
        print(rendered)
    if report["terminal"] != "EXACT_COVERAGE_SET_SUFFICIENT_FOR_KNOWN_H_OBJECTIVE_SELECTION_R0B":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
