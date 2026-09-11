from fractions import Fraction

from gmi_vlc_exact_phase_v2 import (
    MODULE_SIZES,
    UPDATE_SWEEP,
    analytic_versioned_wins,
    enumerated_versioned_wins,
    evaluate,
)


def test_analytic_versioning_threshold_matches_enumeration():
    for k in MODULE_SIZES:
        for updates in UPDATE_SWEEP:
            assert analytic_versioned_wins(k, updates, Fraction(3, 1), 1) == enumerated_versioned_wins(
                k, updates, Fraction(3, 1), 1
            )


def test_receipt_is_structurally_complete():
    result = evaluate()
    assert result["threshold_rows"]
    assert len(result["threshold_rows"]) == len(MODULE_SIZES) * len(UPDATE_SWEEP)
    assert result["terminal"] in {
        "VLC_PHASE_DECOMPOSITION_V2_EXACT_GREEN",
        "VLC_PHASE_DECOMPOSITION_V2_EXACT_FAIL",
    }
