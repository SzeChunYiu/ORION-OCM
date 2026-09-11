from gmi_vlc_exact_phase import (
    N,
    MODULE_SIZES,
    REGIMES,
    exact_average_module_count,
    evaluate,
)


def test_exact_query_module_counts_are_bounded():
    for k in MODULE_SIZES:
        q = exact_average_module_count(k, 4)
        assert 1 <= q <= 4


def test_exact_update_module_counts_are_bounded():
    for regime in REGIMES:
        for k in MODULE_SIZES:
            u = exact_average_module_count(k, regime.update_cone)
            assert 1 <= u <= min(regime.update_cone, N // k)


def test_receipt_contains_all_candidates_and_predictions():
    result = evaluate()
    assert len(result["rows"]) == len(REGIMES) * len(MODULE_SIZES) * 2
    assert set(result["winners"]) == {r.name for r in REGIMES}
    assert result["terminal"] in {
        "VLC_PHASE_PREDICTION_EXACT_MICROSCOPE_GREEN",
        "VLC_PHASE_PREDICTION_EXACT_MICROSCOPE_FAIL",
    }
    assert result["predictions"]
