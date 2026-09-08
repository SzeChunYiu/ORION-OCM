"""Source-derived counterexample: decision-region probability is not Bayes state.

Stdlib only.  This verifier consumes the R0B source-derived regime artifact and
constructs two synthetic theorem-witness lifetime priors with identical mass on
the inverse/semantic static decision regions.  It enumerates every one-way
switch threshold and requires the Bayes-optimal threshold sets to be disjoint.

The priors are mathematical counterexamples, not operational demand evidence.
No predictor is trained and no ML is authorized.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import randomized_switch_verify as R


COORDINATES = R.COORDINATES
TOL = 1e-9
REPORT_SCHEMA = "ocm.residual-strategy-regime.r0b.distributional-lifecycle.verify.v1"


def _load_json(path):
    return json.loads(Path(path).read_text())


def _write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def decision_bits(rows, coordinate, max_horizon):
    if len(rows) < max_horizon:
        raise ValueError("regime artifact does not cover requested horizon")
    bits = []
    for expected_h, row in enumerate(rows[:max_horizon], start=1):
        if row.get("horizon") != expected_h:
            raise ValueError("regime horizons must be contiguous from one")
        inverse = float(row["inverse"][coordinate])
        semantic = float(row["semantic"][coordinate])
        if not math.isfinite(inverse) or not math.isfinite(semantic):
            raise ValueError("static costs must be finite")
        bits.append(1 if semantic < inverse else 0)
    return tuple(bits)


def first_semantic_region(bits):
    """Return first 1 only when the region is monotone 0*1*."""
    first = None
    seen_one = False
    for horizon, bit in enumerate(bits, start=1):
        if bit not in (0, 1):
            raise ValueError("decision region must be binary")
        if bit == 1:
            if first is None:
                first = horizon
            seen_one = True
        elif seen_one:
            return None
    return first


def threshold_risk(support, inverse, semantic, max_horizon):
    """Enumerate exact expected raw cost for each threshold under finite support."""
    if not support:
        raise ValueError("support must be nonempty")
    total_mass = math.fsum(float(probability) for _, probability in support)
    if abs(total_mass - 1.0) > 1e-12:
        raise ValueError("support probabilities must sum to one")
    if any(
        type(horizon) is not int
        or not 1 <= horizon <= max_horizon
        or not math.isfinite(float(probability))
        or float(probability) < 0
        for horizon, probability in support
    ):
        raise ValueError("invalid finite prior support")

    rows = []
    for threshold in range(max_horizon + 1):
        risk = math.fsum(
            float(probability)
            * R.threshold_cost(horizon, threshold, inverse, semantic)
            for horizon, probability in support
        )
        rows.append((risk, threshold))
    return tuple(rows)


def optimal_thresholds(risks, tol=TOL):
    best = min(risk for risk, _ in risks)
    scale = max(1.0, abs(best))
    threshold_set = tuple(
        threshold for risk, threshold in risks
        if abs(risk - best) <= tol * scale
    )
    return {
        "risk": best,
        "thresholds": threshold_set,
    }


def region_mass(support, bits, region=1):
    return math.fsum(
        float(probability)
        for horizon, probability in support
        if bits[horizon - 1] == region
    )


def witness_for_coordinate(rows, coordinate, max_horizon):
    bits = decision_bits(rows, coordinate, max_horizon)
    crossover = first_semantic_region(bits)
    if crossover is None or crossover <= 1:
        raise ValueError("source-derived decision region must contain strict short and long regimes")
    if bits[0] != 0 or bits[crossover - 1] != 1 or bits[max_horizon - 1] != 1:
        raise ValueError("witness endpoints must span inverse and semantic regions")

    inverse, semantic = R.lifetime_curves(rows, coordinate, max_horizon)
    short_prior = ((1, 0.5), (crossover, 0.5))
    long_prior = ((1, 0.5), (max_horizon, 0.5))

    short_mass = region_mass(short_prior, bits)
    long_mass = region_mass(long_prior, bits)
    short_optimum = optimal_thresholds(
        threshold_risk(short_prior, inverse, semantic, max_horizon)
    )
    long_optimum = optimal_thresholds(
        threshold_risk(long_prior, inverse, semantic, max_horizon)
    )
    intersection = sorted(
        set(short_optimum["thresholds"]).intersection(long_optimum["thresholds"])
    )

    same_representation = abs(short_mass - long_mass) <= 1e-12
    disjoint_optima = not intersection
    certified = (
        same_representation
        and abs(short_mass - 0.5) <= 1e-12
        and abs(long_mass - 0.5) <= 1e-12
        and disjoint_optima
    )
    return {
        "certified": certified,
        "crossover": crossover,
        "coarse_representation": "P(static-semantic-winning-region)",
        "short_prior": {
            "support": [[1, 0.5], [crossover, 0.5]],
            "semantic_region_probability": short_mass,
            "optimal_raw_cost": short_optimum["risk"],
            "optimal_thresholds": list(short_optimum["thresholds"]),
        },
        "long_prior": {
            "support": [[1, 0.5], [max_horizon, 0.5]],
            "semantic_region_probability": long_mass,
            "optimal_raw_cost": long_optimum["risk"],
            "optimal_thresholds": list(long_optimum["thresholds"]),
        },
        "optimal_threshold_intersection": intersection,
        "same_coarse_representation": same_representation,
        "disjoint_bayes_optimal_threshold_sets": disjoint_optima,
    }


def build_report(regime, max_horizon=142):
    if type(max_horizon) is not int or not 2 <= max_horizon <= 10_000:
        raise ValueError("invalid horizon")
    rows = regime["iid_static"]["rows"]
    coordinates = {
        coordinate: witness_for_coordinate(rows, coordinate, max_horizon)
        for coordinate in COORDINATES
    }
    all_certified = all(value["certified"] for value in coordinates.values())
    return {
        "schema": REPORT_SCHEMA,
        "study": "Decision-region probability insufficiency for Bayes lifecycle control",
        "scope": {
            "effective_horizon": [1, max_horizon],
            "witness_priors_are_operational_demand_evidence": False,
            "witness_priors_are_theorem_counterexamples": True,
            "policy_family": "deterministic one-way switch thresholds",
            "resource_coordinates": list(COORDINATES),
            "ml_used": False,
        },
        "coordinates": coordinates,
        "theorem": {
            "premise": "same coarse belief representation with disjoint Bayes-optimal action sets",
            "conclusion": "no controller using only that representation can be Bayes-optimal on both beliefs",
            "randomized_extension": "fixed-prior mixtures attain Bayes optimum only on optimal deterministic support",
        },
        "claim_boundary": {
            "binary_decision_region_probability_is_general_bayes_state": False,
            "full_horizon_posterior_is_minimal_state_claimed": False,
            "cost_loss_vector_is_a_sufficient_finite_representation": True,
            "operational_lifetime_prior_established": False,
            "learned_lifecycle_router_authorized": False,
        },
        "terminal": (
            "DECISION_REGION_PROBABILITY_INSUFFICIENT_R0B_PHASE2C0"
            if all_certified
            else "DISTRIBUTIONAL_LIFECYCLE_WITNESS_FAILED_R0B_PHASE2C0"
        ),
    }


def _notice(report):
    return {
        "terminal": report["terminal"],
        "coordinates": {
            coordinate: {
                "crossover": value["crossover"],
                "region_probability": value["short_prior"]["semantic_region_probability"],
                "short_optima": value["short_prior"]["optimal_thresholds"],
                "long_optima": value["long_prior"]["optimal_thresholds"],
                "intersection": value["optimal_threshold_intersection"],
            }
            for coordinate, value in report["coordinates"].items()
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--regime", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--max-horizon", type=int, default=142)
    parser.add_argument("--github-notice", action="store_true")
    args = parser.parse_args()
    report = build_report(_load_json(args.regime), args.max_horizon)
    _write_json(args.out, report)
    rendered = json.dumps(_notice(report), sort_keys=True, separators=(",", ":"))
    if args.github_notice:
        print(f"::notice title=R0B distributional lifecycle state::{rendered}")
    else:
        print(rendered)
    if report["terminal"] != "DECISION_REGION_PROBABILITY_INSUFFICIENT_R0B_PHASE2C0":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
