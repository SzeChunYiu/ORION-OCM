from phase_replication_4bit import run


def test_frozen_4bit_predictions_hold():
    result = run()
    assert result["universe_size"] == 65536
    assert result["max_minimum_expression_size"] == 21
    assert result["strata"]["simple_count"] == 46
    assert result["strata"]["complex_pool_count"] == 37351
    assert result["strata"]["complex_sample_count"] == 256
    assert result["training"]["subset_count"] == 64
    assert result["frozen_predictions"]["R1_simple_cost_lt_direct"] is True
    assert result["frozen_predictions"]["R2_complex_cost_ge_direct"] is True
    assert result["frozen_predictions"]["R3_complex_cost_gt_simple"] is True


def test_exact_registered_costs_are_stable():
    result = run()
    assert abs(result["simple"]["mean_acquisition_cost"] - 0.8145946557971014) < 1e-15
    assert abs(result["complex"]["mean_acquisition_cost"] - 1.0143458048502605) < 1e-15
    assert abs(result["frozen_predictions"]["complex_minus_simple_cost"] - 0.19975114905315905) < 1e-15
