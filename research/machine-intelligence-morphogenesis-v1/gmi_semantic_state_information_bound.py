"""Exact finite checks for the GMI semantic-state information correction.

Parent-owned counting/source-coding calibration only.
"""

from __future__ import annotations

from math import ceil, log2


def fixed_length_bits(number_of_states: int) -> int:
    """Minimum fixed-length binary bits needed for N exact distinguishable states."""
    if number_of_states < 1:
        raise ValueError("number_of_states must be >= 1")
    return ceil(log2(number_of_states)) if number_of_states > 1 else 0


def ternary_factored_state_bits(number_of_factors: int) -> int:
    """Minimum fixed-length bits for 3**n exact global states."""
    if number_of_factors < 0:
        raise ValueError("number_of_factors must be >= 0")
    return fixed_length_bits(3 ** number_of_factors)


def flat_global_state_count(number_of_factors: int) -> int:
    if number_of_factors < 0:
        raise ValueError("number_of_factors must be >= 0")
    return 3 ** number_of_factors


def shared_local_model_entry_count(number_of_factors: int, entries_per_factor: int) -> int:
    """Toy factored-model entry count with one local table per factor.

    This is deliberately a model-description count, not a state-information bound.
    """
    if number_of_factors < 0 or entries_per_factor < 0:
        raise ValueError("counts must be non-negative")
    return number_of_factors * entries_per_factor


def calibration_receipt() -> dict:
    rows = []
    for n in (1, 2, 4, 8, 16):
        states = flat_global_state_count(n)
        bits = ternary_factored_state_bits(n)
        rows.append(
            {
                "n": n,
                "global_state_count": states,
                "minimum_fixed_length_bits": bits,
                "n_log2_3": n * log2(3),
                "toy_flat_transition_rows": states,
                "toy_factored_local_model_entries_at_6_per_factor": shared_local_model_entry_count(n, 6),
            }
        )
    return {
        "schema": "GMISemanticStateInformationCalibrationV1",
        "rows": rows,
        "terminal": "SEMANTIC_STATE_INFORMATION_BOUND_FINITE_CALIBRATION_GREEN_V1",
        "claim_boundary": (
            "Counting/source-coding calibration only. Exponential global-state or "
            "transition enumeration must not be confused with bits for one current state."
        ),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(calibration_receipt(), indent=2, sort_keys=True))
