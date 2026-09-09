"""Verify perfect-horizon robust-price lower-bound witnesses; stdlib only."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import randomized_switch_verify as R


TOL = 5e-8
CERT_SCHEMA = "ocm.residual-strategy-regime.r0b.price-objective-conflict.certificate.v1"
REPORT_SCHEMA = "ocm.residual-strategy-regime.r0b.price-objective-conflict.verify.v1"


def _load(path):
    return json.loads(Path(path).read_text())


def _write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def fixed_horizon_matrix(regime_rows, horizon):
    max_horizon = len(regime_rows)
    if type(horizon) is not int or not 1 <= horizon <= max_horizon:
        raise ValueError("horizon out of source-derived range")
    return tuple(
        R.ratio_matrix(regime_rows, coordinate, max_horizon)[horizon - 1]
        for coordinate in R.COORDINATES
    )


def verify_fixed_horizon(matrix, certificate, tol=TOL):
    row_count = len(matrix)
    column_count = len(matrix[0])
    if row_count != len(R.COORDINATES):
        raise ValueError("matrix must contain the registered resource rows")
    if any(len(row) != column_count for row in matrix):
        raise ValueError("matrix must be rectangular")

    p = R._distribution(column_count, certificate["primal_support"], "threshold")
    q = [0.0] * row_count
    seen = set()
    for item in certificate["dual_support"]:
        coordinate = item.get("coordinate")
        if coordinate not in R.COORDINATES or coordinate in seen:
            raise ValueError("unknown or duplicate dual coordinate")
        probability = float(item["probability"])
        if not math.isfinite(probability) or probability < 0:
            raise ValueError("dual probability must be finite and nonnegative")
        q[R.COORDINATES.index(coordinate)] = probability
        seen.add(coordinate)

    row_values = tuple(
        math.fsum(matrix[row][threshold] * p[threshold]
                  for threshold in range(column_count))
        for row in range(row_count)
    )
    column_values = tuple(
        math.fsum(q[row] * matrix[row][threshold] for row in range(row_count))
        for threshold in range(column_count)
    )
    upper = max(row_values)
    lower = min(column_values)
    gap = upper - lower
    normalization_error = max(abs(math.fsum(p) - 1.0), abs(math.fsum(q) - 1.0))
    reported_error = max(
        abs(float(certificate["primal_value"]) - upper),
        abs(float(certificate["dual_value"]) - lower),
    )
    certified = (
        normalization_error <= tol
        and lower <= upper + tol
        and gap <= tol
        and reported_error <= 10 * tol
    )
    return {
        "certified": certified,
        "primal_upper_bound": upper,
        "dual_lower_bound": lower,
        "certified_gap": gap,
        "normalization_error": normalization_error,
        "reported_value_error": reported_error,
        "primal_support": certificate["primal_support"],
        "dual_support": certificate["dual_support"],
        "coordinate_ratios": {
            coordinate: row_values[index]
            for index, coordinate in enumerate(R.COORDINATES)
        },
        "binding_coordinates": [
            coordinate for index, coordinate in enumerate(R.COORDINATES)
            if row_values[index] >= upper - 1e-7
        ],
        "binding_thresholds_under_dual": [
            threshold for threshold, value in enumerate(column_values)
            if value <= lower + 1e-7
        ],
    }


def build_report(regime, certificate):
    if certificate.get("schema") != CERT_SCHEMA:
        raise ValueError("unexpected price-conflict certificate schema")
    if tuple(certificate.get("registered_coordinates", ())) != R.COORDINATES:
        raise ValueError("registered coordinate drift")
    rows = regime["iid_static"]["rows"]
    results = {}
    all_certified = True
    for horizon_text, entry in sorted(
        certificate["horizons"].items(), key=lambda item: int(item[0])
    ):
        horizon = int(horizon_text)
        result = verify_fixed_horizon(fixed_horizon_matrix(rows, horizon), entry)
        results[horizon_text] = result
        all_certified = all_certified and result["certified"]

    worst_horizon, worst = max(
        ((int(h), value) for h, value in results.items()),
        key=lambda pair: pair[1]["primal_upper_bound"],
    )
    exceeds_105 = [
        int(h) for h, value in results.items()
        if value["dual_lower_bound"] > 1.05 + TOL
    ]
    terminal = (
        "PRICE_OBJECTIVE_CONFLICT_BEFORE_LEARNING_R0B"
        if all_certified and exceeds_105
        else "PRICE_CONFLICT_CERTIFICATE_FAILED_R0B"
        if not all_certified
        else "PRICE_BLIND_105_NOT_REFUTED_BY_REGISTERED_WITNESSES"
    )
    return {
        "schema": REPORT_SCHEMA,
        "study": "Perfect-horizon lower bound for a price-blind randomized threshold controller",
        "scope": {
            "horizon_is_revealed": True,
            "price_vector_is_revealed": False,
            "price_family": "all nonnegative linear scalarizations of registered primary resources",
            "policy_family": "randomized one-way inverse-to-semantic thresholds",
            "benchmark": certificate["benchmark"],
            "ml_authorized": False,
        },
        "theorem": {
            "robust_price_ratio_identity": (
                "sup_{w>=0,w!=0} (w.C)/min(w.A,w.B) "
                "= max_i C_i/min(A_i,B_i)"
            ),
            "reason_basis_prices_are_complete": True,
        },
        "horizons": results,
        "summary": {
            "all_certified": all_certified,
            "witness_horizons_strictly_above_1_05": exceeds_105,
            "worst_registered_witness_horizon": worst_horizon,
            "worst_registered_witness_value": worst["primal_upper_bound"],
        },
        "claim_boundary": {
            "perfect_horizon_solves_price_ambiguity": False,
            "price_objective_should_be_registered_or_pareto_reported": True,
            "this_is_not_a_prediction_lower_bound": True,
            "learned_router_authorized": False,
        },
        "terminal": terminal,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--regime", type=Path, required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--github-notice", action="store_true")
    args = parser.parse_args()
    report = build_report(_load(args.regime), _load(args.certificate))
    _write(args.out, report)
    notice = {
        "terminal": report["terminal"],
        "above_1_05": report["summary"]["witness_horizons_strictly_above_1_05"],
        "worst_horizon": report["summary"]["worst_registered_witness_horizon"],
        "worst_value": report["summary"]["worst_registered_witness_value"],
    }
    rendered = json.dumps(notice, sort_keys=True, separators=(",", ":"))
    if args.github_notice:
        print(f"::notice title=R0B perfect-H price conflict::{rendered}")
    else:
        print(rendered)
    if not report["summary"]["all_certified"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
