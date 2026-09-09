from __future__ import annotations

import online_switch as O


def test_threshold_cost_uses_inverse_then_cold_semantic_suffix():
    inverse = {0: 0.0, 1: 3.0, 2: 6.0, 3: 9.0, 4: 12.0}
    semantic = {0: 0.0, 1: 8.0, 2: 10.0, 3: 11.0, 4: 12.0}
    assert O.threshold_cost(2, 2, inverse, semantic) == 6.0
    assert O.threshold_cost(4, 2, inverse, semantic) == 6.0 + 10.0
    assert O.threshold_cost(4, 0, inverse, semantic) == 12.0


def test_exhaustive_threshold_optimizer_finds_global_family_minimum():
    inverse = {0: 0.0, 1: 2.0, 2: 4.0, 3: 6.0, 4: 8.0}
    semantic = {0: 0.0, 1: 5.0, 2: 6.0, 3: 6.5, 4: 7.0}
    best, candidates = O.best_deterministic_threshold(inverse, semantic, 4)
    assert len(candidates) == 5
    assert best["worst_competitive_ratio"] == min(
        row["worst_competitive_ratio"] for row in candidates
    )


def test_real_online_switch_never_receives_future_horizon_or_targets():
    report = O.build_report(max_horizon=3)
    assert report["scope"]["future_horizon_visible_to_policy"] is False
    assert report["scope"]["future_targets_visible_to_policy"] is False
    assert report["scope"]["switches"] == "at most one, inverse -> semantic"
    assert report["claim_boundary"]["optimal_within_deterministic_time_only_one_way_switch_family"] is True
    assert report["claim_boundary"]["optimal_among_arbitrary_online_policies"] is False
    assert report["claim_boundary"]["ml_authorized"] is False


def test_real_full_range_reports_valid_competitive_ratios_and_thresholds():
    report = O.build_report(max_horizon=O.R.MAX_HORIZON)
    for value in report["coordinates"].values():
        best = value["best_threshold"]
        assert 0 <= best["threshold"] <= O.R.MAX_HORIZON
        assert best["worst_competitive_ratio"] >= 1.0
        assert 1 <= best["worst_ratio_horizon"] <= O.R.MAX_HORIZON
