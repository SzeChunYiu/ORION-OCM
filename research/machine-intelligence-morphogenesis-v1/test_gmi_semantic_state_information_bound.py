from math import ceil, log2

import pytest

from gmi_semantic_state_information_bound import (
    calibration_receipt,
    fixed_length_bits,
    flat_global_state_count,
    shared_local_model_entry_count,
    ternary_factored_state_bits,
)


def test_fixed_length_bound_exact_small_cases():
    assert fixed_length_bits(1) == 0
    assert fixed_length_bits(2) == 1
    assert fixed_length_bits(3) == 2
    assert fixed_length_bits(4) == 2
    assert fixed_length_bits(5) == 3


def test_ternary_global_state_information_is_linear_in_n():
    for n in (1, 2, 4, 8, 16):
        bits = ternary_factored_state_bits(n)
        assert bits == ceil(n * log2(3))
        assert bits <= 2 * n
        if n >= 3:
            assert bits < 2 * n


def test_global_state_enumeration_is_exponential_while_bits_are_linear():
    assert flat_global_state_count(4) == 81
    assert ternary_factored_state_bits(4) == 7
    assert flat_global_state_count(16) == 43046721
    assert ternary_factored_state_bits(16) == 26


def test_model_entry_count_is_a_distinct_quantity():
    assert shared_local_model_entry_count(16, 6) == 96
    assert flat_global_state_count(16) == 43046721


def test_invalid_counts_fail_closed():
    with pytest.raises(ValueError):
        fixed_length_bits(0)
    with pytest.raises(ValueError):
        ternary_factored_state_bits(-1)
    with pytest.raises(ValueError):
        shared_local_model_entry_count(-1, 6)


def test_receipt_preserves_interpretation_boundary():
    receipt = calibration_receipt()
    assert receipt["terminal"] == "SEMANTIC_STATE_INFORMATION_BOUND_FINITE_CALIBRATION_GREEN_V1"
    row = next(r for r in receipt["rows"] if r["n"] == 16)
    assert row["global_state_count"] == 43046721
    assert row["minimum_fixed_length_bits"] == 26
    assert "must not be confused" in receipt["claim_boundary"]
