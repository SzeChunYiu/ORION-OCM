import pytest

from gmi_morphology_selection_no_go import (
    Candidate,
    bounded_search_winner,
    calibration_receipt,
    hardware_response,
    scalar_cost,
    winner,
)


def test_frozen_price_reversal():
    receipt = calibration_receipt()
    assert receipt["price_reversal"]["winner_1"] == ("A",)
    assert receipt["price_reversal"]["winner_2"] == ("B",)


def test_frozen_hardware_reversal():
    receipt = calibration_receipt()
    assert receipt["hardware_reversal"]["winner_hardware_1"] == ("A",)
    assert receipt["hardware_reversal"]["winner_hardware_2"] == ("B",)


def test_bounded_search_misses_normative_optimum():
    receipt = calibration_receipt()
    assert receipt["bounded_discovery"]["normative_winner"] == ("C",)
    assert receipt["bounded_discovery"]["found_winner"] == ("B",)


def test_semantically_wrong_free_candidate_is_excluded():
    candidates = (
        Candidate("RIGHT", True, (10.0,)),
        Candidate("WRONG_FREE", False, (0.0,)),
    )
    assert winner(candidates, (1.0,)) == ("RIGHT",)


def test_negative_price_rejected():
    with pytest.raises(ValueError, match="prices must be non-negative"):
        scalar_cost((1.0,), (-1.0,))


def test_missing_hardware_response_rejected():
    candidates = {"A": Candidate("A", True, (1.0,))}
    with pytest.raises(KeyError):
        hardware_response(candidates, {})


def test_unknown_proposal_rejected():
    candidates = {"A": Candidate("A", True, (1.0,))}
    with pytest.raises(KeyError):
        bounded_search_winner(candidates, ("UNKNOWN",), 1, (1.0,))


def test_claim_boundary_does_not_assert_new_selection_law():
    receipt = calibration_receipt()
    assert receipt["terminal"] == "GMI_DEMAND_ONLY_MORPHOLOGY_SELECTION_NO_GO_GREEN_V1"
    assert "no new architecture-selection theorem" in receipt["claim_boundary"].lower()
