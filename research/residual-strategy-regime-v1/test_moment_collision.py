from __future__ import annotations

import moment_collision_verify as M


def _classical_rows(max_horizon=6, buy=2.5):
    return [
        {
            "horizon": horizon,
            "inverse": {"transitions": float(horizon)},
            "semantic": {"transitions": float(buy)},
        }
        for horizon in range(1, max_horizon + 1)
    ]


def test_equal_mean_equal_region_mass_can_require_disjoint_thresholds():
    witness = M.find_witness(_classical_rows(), "transitions", 6)
    assert witness["certified"] is True
    left = witness["left_prior"]
    right = witness["right_prior"]
    assert left["mean_horizon"] == right["mean_horizon"]
    assert left["semantic_region_probability"] == right["semantic_region_probability"] == 0.5
    assert set(left["optimal_thresholds"]).isdisjoint(right["optimal_thresholds"])


def test_witness_search_keeps_one_support_point_in_each_static_region():
    witness = M.find_witness(_classical_rows(), "transitions", 6)
    crossover = witness["crossover"]
    for side in ("left_prior", "right_prior"):
        short_h, long_h = [item[0] for item in witness[side]["support"]]
        assert short_h < crossover <= long_h
