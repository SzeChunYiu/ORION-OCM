"""Find source-derived lifetime-belief collisions beyond a decision-region bit.

For each primary resource coordinate, search equal-weight two-point lifetime
priors with one support point in the inverse-static region and one in the
semantic-static region.  Require two priors that have both the same mean horizon
and the same semantic-region probability but disjoint Bayes-optimal one-way
switch thresholds.

The witness priors are theorem counterexamples only, never operational demand
evidence.  Stdlib only; no ML.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import distributional_lifecycle_verify as D
import randomized_switch_verify as R


REPORT_SCHEMA = "ocm.residual-strategy-regime.r0b.moment-collision.verify.v1"


def _load(path):
    return json.loads(Path(path).read_text())


def _write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def _candidate(short_h, long_h, bits, inverse, semantic, max_horizon):
    support = ((short_h, 0.5), (long_h, 0.5))
    optimum = D.optimal_thresholds(
        D.threshold_risk(support, inverse, semantic, max_horizon)
    )
    return {
        "support": [[short_h, 0.5], [long_h, 0.5]],
        "mean_horizon": (short_h + long_h) / 2.0,
        "semantic_region_probability": D.region_mass(support, bits),
        "optimal_raw_cost": optimum["risk"],
        "optimal_thresholds": list(optimum["thresholds"]),
    }


def find_witness(rows, coordinate, max_horizon):
    bits = D.decision_bits(rows, coordinate, max_horizon)
    crossover = D.first_semantic_region(bits)
    if crossover is None or crossover <= 1:
        raise ValueError("coordinate does not expose strict short/long regions")
    inverse, semantic = R.lifetime_curves(rows, coordinate, max_horizon)

    by_sum = {}
    for short_h in range(1, crossover):
        if bits[short_h - 1] != 0:
            continue
        for long_h in range(crossover, max_horizon + 1):
            if bits[long_h - 1] != 1:
                continue
            candidate = _candidate(
                short_h, long_h, bits, inverse, semantic, max_horizon
            )
            by_sum.setdefault(short_h + long_h, []).append(candidate)

    for total in sorted(by_sum):
        candidates = by_sum[total]
        for left_index, left in enumerate(candidates):
            left_set = set(left["optimal_thresholds"])
            for right in candidates[left_index + 1:]:
                if left_set.isdisjoint(right["optimal_thresholds"]):
                    same_mean = abs(left["mean_horizon"] - right["mean_horizon"]) <= 1e-12
                    same_region = abs(
                        left["semantic_region_probability"]
                        - right["semantic_region_probability"]
                    ) <= 1e-12
                    return {
                        "certified": same_mean and same_region,
                        "crossover": crossover,
                        "representation": [
                            "E[H]",
                            "P(static-semantic-winning-region)",
                        ],
                        "left_prior": left,
                        "right_prior": right,
                        "optimal_threshold_intersection": [],
                        "same_mean_horizon": same_mean,
                        "same_semantic_region_probability": same_region,
                    }
    return {
        "certified": False,
        "crossover": crossover,
        "reason": "no equal-mean equal-region disjoint-optimum witness found",
    }


def build_report(regime, max_horizon=142):
    rows = regime["iid_static"]["rows"]
    coordinates = {
        coordinate: find_witness(rows, coordinate, max_horizon)
        for coordinate in R.COORDINATES
    }
    all_certified = all(value["certified"] for value in coordinates.values())
    return {
        "schema": REPORT_SCHEMA,
        "study": "Mean horizon plus static decision-region probability is not Bayes-sufficient",
        "scope": {
            "effective_horizon": [1, max_horizon],
            "witness_priors_are_operational_demand_evidence": False,
            "witness_priors_are_theorem_counterexamples": True,
            "prior_family": "equal-weight two-point, one point in each static decision region",
            "policy_family": "deterministic one-way switch thresholds",
            "ml_used": False,
        },
        "coordinates": coordinates,
        "theorem": {
            "premise": "same (E[H], P[semantic-static-region]) with disjoint Bayes-optimal threshold sets",
            "conclusion": "no controller using only those two belief statistics can be Bayes-optimal on both priors",
            "model_capacity_can_repair_missing_statistics": False,
        },
        "claim_boundary": {
            "mean_horizon_is_sufficient": False,
            "mean_plus_region_probability_is_sufficient": False,
            "full_posterior_is_minimal_claimed": False,
            "cost_loss_vector_remains_a_sufficient_finite_parent": True,
            "operational_lifetime_prior_established": False,
            "learned_lifecycle_router_authorized": False,
        },
        "terminal": (
            "MEAN_PLUS_DECISION_REGION_INSUFFICIENT_R0B_PHASE2C0"
            if all_certified
            else "MOMENT_COLLISION_WITNESS_NOT_ESTABLISHED_R0B_PHASE2C0"
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--regime", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--max-horizon", type=int, default=142)
    parser.add_argument("--github-notice", action="store_true")
    args = parser.parse_args()
    report = build_report(_load(args.regime), args.max_horizon)
    _write(args.out, report)
    notice = {
        "terminal": report["terminal"],
        "witnesses": {
            coordinate: {
                "left": value.get("left_prior", {}).get("support"),
                "right": value.get("right_prior", {}).get("support"),
                "mean": value.get("left_prior", {}).get("mean_horizon"),
                "region_probability": value.get("left_prior", {}).get("semantic_region_probability"),
                "left_optima": value.get("left_prior", {}).get("optimal_thresholds"),
                "right_optima": value.get("right_prior", {}).get("optimal_thresholds"),
            }
            for coordinate, value in report["coordinates"].items()
        },
    }
    rendered = json.dumps(notice, sort_keys=True, separators=(",", ":"))
    if args.github_notice:
        print(f"::notice title=R0B lifetime moment collision::{rendered}")
    else:
        print(rendered)
    if not all(value["certified"] for value in report["coordinates"].values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
