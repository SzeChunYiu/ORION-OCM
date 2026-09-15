#!/usr/bin/env python3
"""Exact VSA receipt reconciliation and analytic bundle/noise law."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RECEIPT = REPO / "research/machine-intelligence-morphogenesis-v1/microscopes/results/STAGE_DC_V24_DC1_VSA.json"


def receipt_digest(receipt: dict[str, Any]) -> str:
    payload = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


def bundled_member_coordinate_accuracy(bundle_size: int) -> float:
    """Odd-k majority bundle: exact probability one member's coordinate survives."""
    if bundle_size < 1 or bundle_size % 2 == 0:
        raise ValueError("bundle size must be positive and odd")
    others = bundle_size - 1
    return 0.5 + 0.5 * math.comb(others, others // 2) / (2**others)


def after_independent_bit_noise(accuracy: float, flip_probability: float) -> float:
    if not (0 <= accuracy <= 1 and 0 <= flip_probability <= 1):
        raise ValueError("probabilities must lie in [0,1]")
    return accuracy * (1 - flip_probability) + (1 - accuracy) * flip_probability


def cleanup_failure_upper_bound(
    dimensions: int, codebook_size: int, coordinate_accuracy: float
) -> float:
    """Hoeffding/union bound versus independent random distractors."""
    if dimensions < 1 or codebook_size < 1 or not 0.5 < coordinate_accuracy <= 1:
        raise ValueError("positive dimensions/codebook and accuracy above chance required")
    margin = coordinate_accuracy - 0.5
    return min(1.0, (codebook_size + 1) * math.exp(-dimensions * margin * margin / 2))


def validate_receipt() -> dict[str, Any]:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    if receipt["schema"] != "StageDC1VSAV1" or receipt["status"] != "EXECUTED_EXACT_AT_SCOPE":
        raise ValueError("VSA receipt schema/status drifted")
    if receipt_digest(receipt) != receipt["receipt_sha256"]:
        raise ValueError("VSA receipt digest mismatch")
    equality = receipt["vsa_equals_store_mat_answers"]
    if len(equality) != 7 or not all(equality.values()):
        raise ValueError("VSA/materialized D2 equality is not 7/7")
    candidate_frontier = sum(value == ["VSA"] for value in receipt["frontier"].values())
    parent_frontier = sum(value == ["STORE_MAT"] for value in receipt["frontier"].values())
    if len(receipt["cells"]) != 28 or len(receipt["frontier"]) != 56:
        raise ValueError("VSA receipt coverage drifted")
    if candidate_frontier != 19 or parent_frontier != 5:
        raise ValueError("VSA phase occupancy drifted")
    return {
        "cells": 28,
        "frontier_cells": 56,
        "parent_equalities": 7,
        "vsa_frontier_cells": candidate_frontier,
        "parent_frontier_cells": parent_frontier,
    }


def validate_closure() -> dict[str, Any]:
    ledger = json.loads((HERE / "VSA_REDUCTION_CLOSURE_LEDGER_V1.json").read_text(encoding="utf-8"))
    expected = {
        "Reduce against D1 coefficient systems.",
        "Reduce against D2 memory.",
        "Reduce against D4 symbolic/program.",
        "Quantify noise/capacity/scaling law.",
        "Predict frontier regime.",
    }
    if len(ledger["rows"]) != 5 or {row["task"] for row in ledger["rows"]} != expected:
        raise ValueError("VSA task inventory drifted")
    if any(row["status"] != "GREEN" for row in ledger["rows"]):
        raise ValueError("VSA closure contains a non-green task")
    for row in ledger["rows"]:
        if not (REPO / row["evidence"].split("#", 1)[0]).is_file():
            raise ValueError(f"missing evidence: {row['evidence']}")
    receipt = validate_receipt()
    accuracies = [bundled_member_coordinate_accuracy(k) for k in (1, 3, 5, 7, 9)]
    if not all(left > right for left, right in zip(accuracies, accuracies[1:])):
        raise ValueError("bundle capacity law lost monotonicity")
    if after_independent_bit_noise(0.75, 0.25) != 0.625:
        raise ValueError("noise law drifted")
    if cleanup_failure_upper_bound(1024, 8, 0.75) <= cleanup_failure_upper_bound(2048, 8, 0.75):
        raise ValueError("dimension scaling bound drifted")
    return {"ledger_rows": 5, **receipt, "k9_coordinate_accuracy": accuracies[-1]}


if __name__ == "__main__":
    result = validate_closure()
    print("GMI_VSA_REDUCTION_CLOSURE_V1_VALID")
    for key, value in result.items():
        print(f"{key}={value}")
