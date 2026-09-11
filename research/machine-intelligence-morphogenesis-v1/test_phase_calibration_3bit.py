from phase_calibration_3bit import run


def test_frozen_phase_predictions_hold():
    result = run()
    assert result["universe_size"] == 256
    assert result["max_minimum_expression_size"] == 12
    assert result["simple"]["target_count"] == 14
    assert result["complex"]["target_count"] == 87
    assert result["frozen_predictions"]["P1_simple_cost_lt_1"] is True
    assert result["frozen_predictions"]["P2_complex_cost_ge_simple"] is True
    assert result["frozen_predictions"]["P3_positive_gap"] is True


def test_complex_stratum_was_not_relabelled_as_parent_loss():
    result = run()
    assert result["complex"]["mean_acquisition_cost"] < 1.0
    assert result["complex"]["mean_acquisition_cost"] > result["simple"]["mean_acquisition_cost"]
