from __future__ import annotations

import distributional_lifecycle_verify as D


def test_region_probability_can_alias_disjoint_bayes_actions_synthetically():
    # Classical rent-vs-buy-shaped curves with M=6.  The static semantic region
    # begins at H=3.  Both priors put half their mass in each static region, but
    # one has its long mass at H=3 and the other at H=6.
    inverse = {h: float(h) for h in range(7)}
    semantic = {0: 0.0, **{h: 2.5 for h in range(1, 7)}}
    bits = tuple(1 if semantic[h] < inverse[h] else 0 for h in range(1, 7))
    assert D.first_semantic_region(bits) == 3

    p = ((1, 0.5), (3, 0.5))
    q = ((1, 0.5), (6, 0.5))
    assert D.region_mass(p, bits) == D.region_mass(q, bits) == 0.5

    p_opt = D.optimal_thresholds(D.threshold_risk(p, inverse, semantic, 6))
    q_opt = D.optimal_thresholds(D.threshold_risk(q, inverse, semantic, 6))
    assert not set(p_opt["thresholds"]).intersection(q_opt["thresholds"])


def test_randomized_controller_cannot_restore_collision_when_optima_disjoint():
    # If fixed-prior expected loss is linear in a mixture over thresholds, an
    # optimal mixture can put positive mass only on deterministic minimizers.
    risks_p = ((1.0, 0), (2.0, 1), (3.0, 2))
    risks_q = ((3.0, 0), (2.0, 1), (1.0, 2))
    p_opt = D.optimal_thresholds(risks_p)
    q_opt = D.optimal_thresholds(risks_q)
    assert p_opt["thresholds"] == (0,)
    assert q_opt["thresholds"] == (2,)
    assert not set(p_opt["thresholds"]).intersection(q_opt["thresholds"])


def test_triangular_loss_rank_uses_additivity_not_numerical_rank():
    rows = [
        {
            "horizon": horizon,
            "inverse": {"transitions": float(horizon)},
            "semantic": {"transitions": 2.5},
        }
        for horizon in range(1, 7)
    ]
    result = D.loss_rank_premises(rows, "transitions", 6)
    assert result["inverse_additive_across_iid_queries"] is True
    assert result["cold_semantic_premium"] == 1.5
    assert result["all_diagonal_entries_nonzero"] is True
    assert result["full_rank_by_triangular_determinant"] is True
    assert result["determinant_formula"] == "(S(1)-I(1))^M"


def test_nonadditive_inverse_curve_does_not_use_triangular_rank_shortcut():
    rows = [
        {
            "horizon": horizon,
            "inverse": {"transitions": float(horizon * horizon)},
            "semantic": {"transitions": 2.5},
        }
        for horizon in range(1, 7)
    ]
    result = D.loss_rank_premises(rows, "transitions", 6)
    assert result["inverse_additive_across_iid_queries"] is False
    assert result["full_rank_by_triangular_determinant"] is False


def test_first_semantic_region_rejects_nonmonotone_decision_regions():
    assert D.first_semantic_region((0, 0, 1, 1)) == 3
    assert D.first_semantic_region((0, 1, 0, 1)) is None
    assert D.first_semantic_region((0, 0, 0)) is None
