"""Repository-discovered tests for issue #602 J1 domain infrastructure."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


BUNDLE = Path(__file__).resolve().parents[1] / "research" / "gmi-domain-registry-v1"
SPEC = importlib.util.spec_from_file_location(
    "domain_infrastructure_v1", BUNDLE / "domain_infrastructure_v1.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_registry_has_exact_j1_inventory() -> None:
    assert MODULE.validate_registry() == {
        "domains": 8,
        "matrix_cells": 64,
        "burden_classes": 4,
        "grammar_symbols": 24,
    }


def test_exact_collision_and_negative_control() -> None:
    records = [
        {"id": "a", "present_output": 0, "ordinary_score": 1, "future_response": "L"},
        {"id": "b", "present_output": 0, "ordinary_score": 1, "future_response": "R"},
        {"id": "c", "present_output": 1, "ordinary_score": 1, "future_response": "R"},
    ]
    certificate = MODULE.collision_pairs(records)
    assert certificate["pair_count"] == 3
    assert certificate["collision_count"] == 1
    assert certificate["collisions"][0]["left"] == "a"
    assert certificate["collisions"][0]["right"] == "b"


def test_parent_tournament_fails_closed() -> None:
    result = MODULE.parent_reduction_tournament(
        [
            MODULE.ParentAttempt("p1", 1, "REFUTES", "mismatch", "NONE", "proof"),
            MODULE.ParentAttempt("p2", 2, "OPEN", "unknown", "UNKNOWN", "missing"),
        ]
    )
    assert result["verdict"] == "CANNOT_IDENTIFY"


def test_protected_receipt_detects_tampering() -> None:
    metadata = {
        "candidate_id": "c",
        "ecology_digest": "e",
        "resource_digest": "r",
        "grammar_digest": "g",
        "split_digest": "s",
        "prediction": "candidate wins",
        "negative_twin_digest": "n",
        "falsifier": "parent wins",
        "evaluator": "external",
    }
    freeze = MODULE.freeze_receipt(metadata, {"winner": "c"}, "salt")
    try:
        MODULE.reveal_receipt(freeze, {"winner": "parent"}, "salt")
    except ValueError:
        pass
    else:
        raise AssertionError("tampered reveal was accepted")
