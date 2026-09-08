from __future__ import annotations

import prospective_selector as P


def test_feature_ladder_refines_without_forbidden_fingerprint_key():
    report = P.build_report(max_horizon=3)
    for coordinate_rows in report["rows"].values():
        for row in coordinate_rows:
            f0 = row["features"]["F0"]
            f1 = row["features"]["F1"]
            f2 = row["features"]["F2"]
            f3 = row["features"]["F3"]
            assert f0["feature_buckets"] <= f1["feature_buckets"] <= f2["feature_buckets"] <= f3["feature_buckets"]
            assert f0["collision_state_fraction"] >= f1["collision_state_fraction"] >= f2["collision_state_fraction"] >= f3["collision_state_fraction"]


def test_identity_saturated_f3_is_only_an_information_upper_bound():
    report = P.build_report(max_horizon=9)
    assert report["claim_boundary"]["f3_is_information_upper_bound_only"] is True
    assert report["claim_boundary"]["ml_authorized"] is False
    for coordinate_rows in report["rows"].values():
        for row in coordinate_rows:
            f3 = row["features"]["F3"]
            assert f3["feature_buckets"] == 142
            assert f3["collision_states"] == 0
            assert abs(f3["regret_expected_cost"]) < 1e-9


def test_feature_acquisition_is_explicit_and_monotone():
    report = P.build_report(max_horizon=1)
    work = report["feature_work_mean_per_query"]
    assert work["F0"] == {}
    assert work["F1"]["feature_coefficient_visits"] > 0
    assert work["F2"]["feature_numerator_bit_length_reads"] > 0
    assert work["F3"]["feature_identity_key_coefficients"] > 0


def test_phase2a_scope_does_not_overclaim_a_deployable_selector():
    report = P.build_report(max_horizon=1)
    assert report["scope"]["frontier"] == 0
    assert report["claim_boundary"]["full_information_oracle_deployable"] is False
    assert report["terminal"] == "LEARNED_ROUTER_NOT_AUTHORIZED_R0B_PHASE2A_COLD_AUDIT"
