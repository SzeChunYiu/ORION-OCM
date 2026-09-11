import copy

import pytest

from gmi_semantic_quotient_certificate import (
    STATES,
    as_jsonable,
    canonical_partition,
    census,
    exact_encoding,
    factor_map,
    semantic_quotient,
)


def test_exact_census_values_are_frozen():
    receipt = census()
    assert receipt.quotient == (("u0", "u1"), ("s",), ("l",))
    assert receipt.partition_count == 15
    assert receipt.exact_encoding_count == 2
    assert receipt.minimum_exact_encoded_states == 3
    assert receipt.minimum_exact_partitions == ((("u0", "u1"), ("s",), ("l",)),)
    assert receipt.distinguishing_word_for_teachable_vs_stubborn == ("teach", "query")


def test_fully_split_realization_is_exact_refinement():
    quotient = semantic_quotient()
    split = (("u0",), ("u1",), ("s",), ("l",))
    assert exact_encoding(split, quotient)
    phi = factor_map(split, quotient)
    assert phi == {0: 0, 1: 0, 2: 1, 3: 2}


def test_minimal_realization_is_canonical_quotient():
    quotient = semantic_quotient()
    assert exact_encoding(quotient, quotient)
    assert factor_map(quotient, quotient) == {0: 0, 1: 1, 2: 2}


def test_merging_teachable_and_stubborn_is_rejected():
    quotient = semantic_quotient()
    invalid = canonical_partition((("u0", "u1", "s"), ("l",)))
    assert not exact_encoding(invalid, quotient)
    with pytest.raises(ValueError, match="aliases required semantic distinction"):
        factor_map(invalid, quotient)


def test_two_state_realization_cannot_be_exact():
    quotient = semantic_quotient()
    candidate = canonical_partition((("u0", "u1", "s"), ("l",)))
    assert len(candidate) == 2
    assert not exact_encoding(candidate, quotient)


def test_receipt_has_no_fundamental_atom_claim():
    receipt = as_jsonable()
    assert receipt["terminal"] == "GMI_SEMANTIC_QUOTIENT_FINITE_EXACT_GREEN_V1"
    assert receipt["all_exact_encodings_factor_through_quotient"] is True
    boundary = receipt["claim_boundary"].lower()
    assert "no unique local cognitive atom" in boundary
    assert "no" in boundary and "universal architecture" in boundary
