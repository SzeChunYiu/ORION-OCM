from __future__ import annotations

import json
from pathlib import Path

import pytest

import randomized_switch_verify as V


def test_symmetric_two_by_two_game_has_half_half_certificate():
    matrix = ((1.0, 2.0), (2.0, 1.0))
    certificate = {
        "primal_value": 1.5,
        "dual_value": 1.5,
        "primal_support": [
            {"threshold": 0, "probability": "0.5"},
            {"threshold": 1, "probability": "0.5"},
        ],
        "dual_support": [
            {"horizon": 1, "probability": "0.5"},
            {"horizon": 2, "probability": "0.5"},
        ],
    }
    result = V.verify_matrix_certificate(matrix, certificate)
    assert result["certified"] is True
    assert abs(result["primal_upper_bound"] - 1.5) < 1e-12
    assert abs(result["dual_lower_bound"] - 1.5) < 1e-12
    assert result["certified_gap"] < 1e-12


def test_certificate_freezes_oblivious_adversary_and_no_future_signal():
    path = Path(__file__).with_name("RANDOMIZED_SWITCH_CERTIFICATE_V1.json")
    certificate = json.loads(path.read_text())
    assert certificate["schema"] == V.CERT_SCHEMA
    assert certificate["max_horizon"] == 142
    assert certificate["adversary"] == "oblivious horizon; cannot observe private threshold draw"
    for coordinate in V.COORDINATES:
        entry = certificate["coordinates"][coordinate]
        assert abs(sum(float(item["probability"]) for item in entry["primal_support"]) - 1.0) < V.TOL
        assert abs(sum(float(item["probability"]) for item in entry["dual_support"]) - 1.0) < V.TOL


def test_duplicate_or_out_of_range_support_is_rejected():
    matrix = ((1.0, 2.0), (2.0, 1.0))
    certificate = {
        "primal_value": 1.5,
        "dual_value": 1.5,
        "primal_support": [
            {"threshold": 0, "probability": "0.5"},
            {"threshold": 0, "probability": "0.5"},
        ],
        "dual_support": [
            {"horizon": 1, "probability": "0.5"},
            {"horizon": 2, "probability": "0.5"},
        ],
    }
    with pytest.raises(ValueError):
        V.verify_matrix_certificate(matrix, certificate)


def test_primal_dual_gap_is_checked_not_solver_status():
    matrix = ((1.0, 2.0), (2.0, 1.0))
    bad = {
        "primal_value": 1.0,
        "dual_value": 1.0,
        "primal_support": [{"threshold": 0, "probability": "1.0"}],
        "dual_support": [{"horizon": 1, "probability": "1.0"}],
    }
    result = V.verify_matrix_certificate(matrix, bad)
    assert result["certified"] is False
    assert result["certified_gap"] > V.TOL
