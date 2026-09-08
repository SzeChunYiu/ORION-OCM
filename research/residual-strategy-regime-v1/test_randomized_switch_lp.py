from __future__ import annotations

import numpy as np

import randomized_switch_lp as M


def test_symmetric_two_by_two_game_has_half_half_value():
    matrix = np.array([[1.0, 2.0], [2.0, 1.0]])
    result = M.solve_zero_sum_minimax(matrix)
    assert result["certified"] is True
    assert abs(result["value_primal"] - 1.5) < 1e-9
    assert abs(result["value_dual"] - 1.5) < 1e-9
    assert result["duality_gap"] <= M.TOL
    probs = {item["threshold"]: item["probability"] for item in result["primal_support"]}
    assert abs(probs[0] - 0.5) < 1e-9
    assert abs(probs[1] - 0.5) < 1e-9


def test_real_short_report_hides_future_and_is_no_ml():
    report = M.build_report(max_horizon=3)
    assert report["scope"]["future_horizon_visible"] is False
    assert report["scope"]["future_targets_visible"] is False
    assert report["scope"]["query_features_visible_to_switch_policy"] is False
    assert report["claim_boundary"]["residual_is_learnable_algorithm_selection"] is False
    assert report["claim_boundary"]["ml_authorized"] is False
    assert report["solver"]["method"] == "highs"
    assert all(value["solution"]["certified"]
               for value in report["coordinates"].values())


def test_real_full_range_primal_dual_certificates_close():
    report = M.build_report(max_horizon=M.R.MAX_HORIZON)
    for value in report["coordinates"].values():
        solution = value["solution"]
        assert solution["certified"] is True
        assert solution["duality_gap"] <= M.TOL
        assert solution["primal_max_violation"] <= M.TOL
        assert solution["dual_max_violation"] <= M.TOL
        assert abs(solution["max_ratio_recomputed"] - solution["value_primal"]) <= 1e-7
        assert abs(solution["min_dual_column_recomputed"] - solution["value_dual"]) <= 1e-7
        assert solution["value_primal"] >= 1.0
