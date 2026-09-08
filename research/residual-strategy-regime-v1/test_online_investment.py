from __future__ import annotations

import online_investment as O


def test_synthetic_fixed_frontier_geometry_prunes_to_multislope():
    points = (
        (0.0, 10.0, 0),
        (2.0, 9.0, 1),
        (3.0, 9.5, 2),  # dominated by frontier 1
        (5.0, 6.0, 3),
        (9.0, 2.0, 4),
    )
    slopes = O.efficient_slopes(points)
    assert tuple(frontier for _, _, frontier in slopes) == (0, 1, 3, 4)
    assert O.D.multislope_monotone(slopes) is True


def test_offline_envelope_is_exact_b_plus_h_r():
    slopes = (
        (0.0, 10.0, 0),
        (5.0, 6.0, 1),
        (20.0, 1.0, 2),
    )
    rows = O.offline_envelope(slopes, max_horizon=6)
    for row in rows:
        h = row["horizon"]
        expected = min(setup + h * recurring for setup, recurring, _ in slopes)
        assert row["expected_cost"] == expected
    assert [row["horizon"] for row in O.envelope_breakpoints(rows)] == [1, 2, 4]


def test_real_reduction_report_is_explicitly_expected_cost_and_no_ml():
    report = O.build_report(max_horizon=3)
    assert report["scope"]["demand"] == "iid uniform frozen 142-target population"
    assert report["scope"]["investment_decision_sees_future_targets"] is False
    assert report["scope"]["semantic_target_triggered_expansion"] is False
    assert report["claim_boundary"]["exact_reduction_is_expected_cost_only"] is True
    assert report["claim_boundary"]["target_sequence_adversarial_multislope_claimed"] is False
    assert report["claim_boundary"]["phase1_oracle_is_upper_bound_for_phase2b0"] is False
    assert report["claim_boundary"]["multislope_geometry_alone_is_not_useful_parent_evidence"] is True
    assert report["claim_boundary"]["ml_authorized"] is False
    assert set(report["coordinates"]) == {
        "transitions", "arithmetic_additions", "arithmetic_multiplications"
    }
    assert all(value["raw_frontier_points"] == 257
               for value in report["coordinates"].values())


def test_real_full_horizon_parent_is_dominated_despite_valid_multislope_geometry():
    report = O.build_report(max_horizon=O.R.MAX_HORIZON)
    assert all(value["multislope_monotone"] for value in report["coordinates"].values())
    assert all(not value["beats_best_static_at_any_horizon"]
               for value in report["coordinates"].values())
    assert all(value["max_gain_over_best_static"]["fraction"] == 0.0
               for value in report["coordinates"].values())
    assert report["terminal"] == "FIXED_FRONTIER_MULTISLOPE_PARENT_DOMINATED_R0B_PHASE2B0"
