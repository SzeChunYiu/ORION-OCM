from __future__ import annotations

import json
from pathlib import Path

import pytest

import robust_lifecycle_advice_verify as V


def test_decision_region_crossover_is_0_star_1_star_only():
    assert V.monotone_crossover((0, 0, 0, 1, 1)) == 4
    assert V.monotone_crossover((1, 1)) == 1
    assert V.monotone_crossover((0, 0)) is None
    assert V.monotone_crossover((0, 1, 0)) is None


def test_perfect_decision_bit_has_ratio_one_certificate():
    matrix = ((1.0, 2.0), (2.0, 1.0))
    certificate = {
        "epsilon": "0.0",
        "target_ratio": "1.0",
        "primal_value": "1.0",
        "dual_value": "1.0",
        "primal_support": [
            {
                "threshold_if_advice_0": 0,
                "threshold_if_advice_1": 1,
                "probability": "1.0",
            }
        ],
        "dual_support": [
            {"horizon": 1, "error_endpoint": "zero", "probability": "0.5"},
            {"horizon": 2, "error_endpoint": "zero", "probability": "0.5"},
        ],
    }
    result = V.verify_certificate(matrix, (0, 1), certificate)
    assert result["certified"] is True
    assert abs(result["primal_upper_bound"] - 1.0) < 1e-12
    assert abs(result["dual_lower_bound"] - 1.0) < 1e-12


def test_frozen_real_certificate_has_one_entry_per_primary_coordinate():
    path = Path(__file__).with_name("ROBUST_LIFECYCLE_ADVICE_CERTIFICATE_V1.json")
    certificate = json.loads(path.read_text())
    assert certificate["schema"] == V.CERT_SCHEMA
    assert certificate["max_horizon"] == 142
    assert set(certificate["coordinates"]) == set(V.COORDINATES)
    for entry in certificate["coordinates"].values():
        assert 0.0 < float(entry["epsilon"]) < 0.05
        assert abs(float(entry["target_ratio"]) - 1.05) < 1e-12
        assert abs(sum(float(item["probability"]) for item in entry["primal_support"]) - 1.0) < V.TOL
        assert abs(sum(float(item["probability"]) for item in entry["dual_support"]) - 1.0) < V.TOL


def test_duplicate_threshold_pair_is_rejected():
    matrix = ((1.0, 2.0), (2.0, 1.0))
    bad = {
        "epsilon": "0.0",
        "target_ratio": "1.0",
        "primal_value": "1.0",
        "dual_value": "1.0",
        "primal_support": [
            {"threshold_if_advice_0": 0, "threshold_if_advice_1": 1, "probability": "0.5"},
            {"threshold_if_advice_0": 0, "threshold_if_advice_1": 1, "probability": "0.5"},
        ],
        "dual_support": [
            {"horizon": 1, "error_endpoint": "zero", "probability": "0.5"},
            {"horizon": 2, "error_endpoint": "zero", "probability": "0.5"},
        ],
    }
    with pytest.raises(ValueError):
        V.verify_certificate(matrix, (0, 1), bad)
