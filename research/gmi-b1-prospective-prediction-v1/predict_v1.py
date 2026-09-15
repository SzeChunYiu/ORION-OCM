from __future__ import annotations

import json
from typing import Dict, List, Mapping

FREEZE_COMMIT = "526ff2d4ddee43abc2cf69e8ef820e9b55278154"
BASE_COMMIT = "c0501931d44e91910fa7b9518c35a59d914d7bf3"

FORBIDDEN_CASE_KEYS = {
    "family",
    "family_name",
    "architecture",
    "architecture_name",
    "phenotype",
    "donor_path",
    "donor_file",
    "measured",
    "outcome",
    "result",
}

SEQUENCE_CASES = (
    ("Q2_A", 4, 1),
    ("Q2_B", 5, 3),
    ("Q2_C", 6, 2),
    ("Q2_D", 7, 5),
)

COEFFICIENT_CASES = (
    ("L3_A", 2, (2, -1)),
    ("L3_B", 3, (1, -2, 3)),
    ("L3_C", 4, (-1, 2, -3, 1)),
    ("L3_D", 5, (2, -1, 3, -2, 1)),
)


def _validate_case(row: Mapping[str, object]) -> None:
    bad = FORBIDDEN_CASE_KEYS.intersection(row)
    if bad:
        raise ValueError(f"predictor-visible forbidden keys: {sorted(bad)}")
    if set(row) - {
        "case_id",
        "object_kind",
        "period",
        "accepted_residue",
        "dimension",
        "coefficients",
        "coefficient_grid",
        "expected",
    }:
        raise ValueError("unexpected predictor-visible field")


def _sequence_predictions() -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for case_id, period, residue in SEQUENCE_CASES:
        if period <= 1 or not (0 <= residue < period):
            raise ValueError("invalid periodic response parameters")
        row: Dict[str, object] = {
            "case_id": case_id,
            "object_kind": "periodic_sequence_response",
            "period": period,
            "accepted_residue": residue,
            "expected": {
                "quotient_classes": period,
                "minimal_recurrent_states": period,
                "all_residue_pairs_future_distinguishable": True,
                "stateless_sufficient": False,
                "history_cheaper_below_length": period,
                "tie_at_length": period,
                "state_first_cheaper_length": period + 1,
                "exact_period_state_realization_exists": True,
            },
        }
        _validate_case(row)
        rows.append(row)
    return rows


def _coefficient_predictions() -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for case_id, d, weights in COEFFICIENT_CASES:
        if len(weights) != d or any(w < -3 or w > 3 for w in weights):
            raise ValueError("invalid coefficient case")
        row: Dict[str, object] = {
            "case_id": case_id,
            "object_kind": "finite_coefficient_identification",
            "dimension": d,
            "coefficients": list(weights),
            "coefficient_grid": [-3, -2, -1, 0, 1, 2, 3],
            "expected": {
                "consistent_after_d_minus_1_independent": 7,
                "consistent_after_d_independent": 1,
                "consistent_after_d_dependent": 7,
                "identified_at_independent_n": d,
                "dependent_d_identifies": False,
                "full_boolean_monomial_basis_size": 2**d,
                "boolean_input_table_size": 2**d,
            },
        }
        _validate_case(row)
        rows.append(row)
    return rows


def build_predictions() -> Mapping[str, object]:
    cases = _sequence_predictions() + _coefficient_predictions()
    if len({row["case_id"] for row in cases}) != len(cases):
        raise AssertionError("duplicate protected case id")
    return {
        "schema": "B1ProspectivePredictionsV1",
        "issue": 776,
        "freeze_commit": FREEZE_COMMIT,
        "base_commit": BASE_COMMIT,
        "outcomes_seen": False,
        "scorer_exists": False,
        "surface_remints_materialized": False,
        "case_count": len(cases),
        "cases": cases,
        "custody": {
            "phase": "PREDICTION_ONLY",
            "successor_scorer_forbidden_in_authority_commit": True,
            "successor_result_forbidden_in_authority_commit": True,
        },
        "claim_ceiling_if_later_confirmed": (
            "B1_PREOUTCOME_PREDICTION_CUSTODY_SUPPORTED_ON_TWO_FRESH_EXACT_FAMILY_REMINTS"
        ),
    }


if __name__ == "__main__":
    print(json.dumps(build_predictions(), indent=2, sort_keys=True))
