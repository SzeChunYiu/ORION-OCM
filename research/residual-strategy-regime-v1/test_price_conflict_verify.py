from __future__ import annotations

import price_conflict_verify as P


def test_symmetric_coordinate_game_has_matching_certificate():
    matrix = ((1.0, 2.0), (2.0, 1.0), (1.25, 1.25))
    certificate = {
        "primal_value": 1.5,
        "dual_value": 1.5,
        "primal_support": [
            {"threshold": 0, "probability": "0.5"},
            {"threshold": 1, "probability": "0.5"},
        ],
        "dual_support": [
            {"coordinate": "transitions", "probability": "0.5"},
            {"coordinate": "arithmetic_additions", "probability": "0.5"},
        ],
    }
    result = P.verify_fixed_horizon(matrix, certificate)
    assert result["certified"] is True
    assert abs(result["primal_upper_bound"] - 1.5) < 1e-12
    assert abs(result["dual_lower_bound"] - 1.5) < 1e-12


def test_bad_dual_cannot_fake_a_lower_bound_certificate():
    matrix = ((1.0, 2.0), (2.0, 1.0), (1.25, 1.25))
    certificate = {
        "primal_value": 1.5,
        "dual_value": 1.5,
        "primal_support": [
            {"threshold": 0, "probability": "0.5"},
            {"threshold": 1, "probability": "0.5"},
        ],
        "dual_support": [
            {"coordinate": "transitions", "probability": "1.0"},
        ],
    }
    result = P.verify_fixed_horizon(matrix, certificate)
    assert result["certified"] is False
    assert result["certified_gap"] > P.TOL
