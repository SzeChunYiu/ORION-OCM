from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ocm.learning import methods as M

import regime_sweep as R


ROOT = Path(__file__).resolve().parent
PROTOCOL = json.loads((ROOT / "FROZEN_PROTOCOL_V1.json").read_text())


def git_blob_sha(path):
    data = Path(path).read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def test_transplanted_donor_and_base_source_custody():
    assert git_blob_sha(ROOT / "semantic_session.py") == PROTOCOL["source"]["semantic_session_git_blob"]
    assert git_blob_sha(ROOT / "inverse_parent.py") == PROTOCOL["source"]["inverse_parent_git_blob"]
    assert git_blob_sha(Path(M.__file__)) == PROTOCOL["source"]["main_methods_git_blob"]


def test_frozen_population_and_frontier():
    tasks, profile, _, _, _, _ = R.calibrate()
    assert len(tasks) == 142
    assert profile["frontier_transitions"] == 256
    assert profile["frontier_states"] == 206
    assert len(set(profile["ranks"].values())) == 142


def test_source_derived_expected_phase_boundary():
    _, _, _, _, crossover, _ = R.calibrate()
    assert crossover["first_semantic_expected_win"] == {
        "transitions": 4,
        "arithmetic_additions": 6,
        "arithmetic_multiplications": 9,
    }
    assert crossover["inverse_pareto_through_horizon"] == 3
    assert crossover["semantic_pareto_from_horizon"] == 9
    assert crossover["price_sensitive_band"] == [4, 8]


def test_cost_free_oracle_residual_is_below_eight_percent():
    _, _, _, _, _, oracle = R.calibrate()
    for coordinate in R.PHASE_COORDS:
        assert 0.0 < oracle[coordinate]["max_residual"]["fraction"] < 0.08


def test_stable_semantic_phase_cost_is_order_invariant_for_same_target_set():
    tasks, _, _, _, _, _ = R.calibrate()
    selected = list(tasks[:32])
    forward = R.semantic_sequence(selected)["work"]
    reverse = R.semantic_sequence(list(reversed(selected)))["work"]
    assert {key: forward[key] for key in R.PHASE_COORDS} == {
        key: reverse[key] for key in R.PHASE_COORDS
    }


def test_reset_transition_cost_is_sum_of_epoch_frontier_maxima():
    tasks, profile, _, _, _, _ = R.calibrate()
    selected = list(tasks[:32])
    interval = 4
    expected = sum(
        max(profile["ranks"][task.fingerprint] for task in selected[start:start + interval])
        for start in range(0, len(selected), interval)
    )
    actual = R.semantic_sequence(selected, reset_every=interval)["work"]["transitions"]
    assert actual == expected
