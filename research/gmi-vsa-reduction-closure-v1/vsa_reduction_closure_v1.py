#!/usr/bin/env python3
"""Exact VSA receipt reconciliation and analytic bundle/noise law."""

from __future__ import annotations

import hashlib
import json
import math
from itertools import product
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


# Neutral construction/search -------------------------------------------------
# Candidate tuples contain only low-level operation choices.  Morphology names
# occur solely in the post-search documentation, never in this search space.
DIMENSIONS = 64
MASK = (1 << DIMENSIONS) - 1
STRUCTURED_RECORDS = (
    ((0, 0, 1), (1, 1, 4), (2, 2, 6)),
    ((0, 3, 0), (1, 0, 5), (2, 1, 7)),
    ((0, 2, 3), (1, 3, 1), (2, 0, 4)),
    ((0, 1, 6), (1, 2, 0), (2, 3, 5)),
)
TARGET = ("xor", "majority", "rotate", "nearest")


def _lcg_word(seed: int) -> int:
    value = (seed * 1103515245 + 12345) & 0xFFFFFFFF
    word = 0
    for bit in range(DIMENSIONS):
        value = (value * 1103515245 + 12345) & 0xFFFFFFFF
        word |= ((value >> 16) & 1) << bit
    return word


ROLES = tuple(_lcg_word(1000 + index) for index in range(4))
FILLERS = tuple(_lcg_word(2000 + index) for index in range(8))


def _rotate(word: int, distance: int) -> int:
    distance %= DIMENSIONS
    return word if distance == 0 else ((word << distance) | (word >> (DIMENSIONS - distance))) & MASK


def _combine(left: int, right: int, operation: str) -> int:
    if operation == "xor":
        return left ^ right
    if operation == "and":
        return left & right
    if operation == "or":
        return left | right
    raise ValueError("unknown Boolean operation")


def _fold(words: tuple[int, ...], operation: str) -> int:
    if not words:
        raise ValueError("cannot fold an empty word list")
    if operation == "first":
        return words[0]
    if operation == "parity":
        result = 0
        for word in words:
            result ^= word
        return result
    if operation == "majority":
        result = 0
        for bit in range(DIMENSIONS):
            if 2 * sum((word >> bit) & 1 for word in words) > len(words):
                result |= 1 << bit
        return result
    raise ValueError("unknown fold operation")


def _role_word(role: int, slot: int, transform: str) -> int:
    if transform == "identity":
        return ROLES[role]
    if transform == "rotate":
        return _rotate(ROLES[role], 7 * slot)
    raise ValueError("unknown index transform")


def _choose(word: int, method: str) -> tuple[int, int]:
    distances = [(word ^ filler).bit_count() for filler in FILLERS]
    if method == "exact":
        for index, distance in enumerate(distances):
            if distance == 0:
                return index, DIMENSIONS * (index + 1)
        return -1, DIMENSIONS * len(FILLERS)
    if method == "nearest":
        return min(range(len(distances)), key=distances.__getitem__), DIMENSIONS * len(FILLERS)
    raise ValueError("unknown chooser")


def apply_candidate(
    candidate: tuple[str, str, str, str], records: tuple[tuple[tuple[int, int, int], ...], ...]
) -> tuple[tuple[tuple[int, tuple[int, ...]], ...], int]:
    """Return exact record/query outputs and a deterministic charged-op count."""
    boolean, fold, transform, chooser = candidate
    outputs = []
    cost = 0
    for items in records:
        item_words = []
        for slot, role, filler in items:
            item_words.append(_combine(FILLERS[filler], _role_word(role, slot, transform), boolean))
            cost += DIMENSIONS + (DIMENSIONS if transform == "rotate" and slot else 0)
        cue = _fold(tuple(item_words), fold)
        if fold == "parity":
            cost += DIMENSIONS * (len(items) - 1)
        elif fold == "majority":
            cost += DIMENSIONS * len(items)
        answers = []
        for slot, role, _filler in items:
            key = _role_word(role, slot, transform)
            residual = _combine(cue, key, boolean)
            cost += DIMENSIONS + (DIMENSIONS if transform == "rotate" and slot else 0)
            answer, chooser_cost = _choose(residual, chooser)
            cost += chooser_cost
            answers.append(answer)
        outputs.append((cue, tuple(answers)))
    return tuple(outputs), cost


def candidate_space() -> tuple[tuple[str, str, str, str], ...]:
    return tuple(product(
        ("xor", "and", "or"),
        ("first", "parity", "majority"),
        ("identity", "rotate"),
        ("exact", "nearest"),
    ))


def _obligation_outputs(
    records: tuple[tuple[tuple[int, int, int], ...], ...]
) -> tuple[tuple[int, tuple[int, ...]], ...]:
    """Build reference cues, but take answers independently from declared labels."""
    target_outputs, _ = apply_candidate(TARGET, records)
    return tuple(
        (target_outputs[index][0], tuple(filler for _slot, _role, filler in items))
        for index, items in enumerate(records)
    )


def neutral_recovery_certificate() -> dict[str, Any]:
    serialized_grammar = repr(candidate_space()).lower()
    forbidden = ("vsa", "hypervector", "bind", "bundle", "permutation", "cleanup", "attention")
    if any(token in serialized_grammar for token in forbidden):
        raise ValueError("candidate grammar leaks a family/macro label")
    expected = _obligation_outputs(STRUCTURED_RECORDS)
    scored = [(cost, candidate) for candidate in candidate_space()
              if (result := apply_candidate(candidate, STRUCTURED_RECORDS))[0] == expected
              for cost in (result[1],)]
    twin_records = tuple(((0, index % 4, (3 * index + 1) % 8),) for index in range(8))
    twin_expected = _obligation_outputs(twin_records)
    twin_scored = [(cost, candidate) for candidate in candidate_space()
                   if (result := apply_candidate(candidate, twin_records))[0] == twin_expected
                   for cost in (result[1],)]
    if not scored or not twin_scored:
        raise ValueError("neutral search found no exact candidate")
    scored.sort()
    twin_scored.sort()
    return {
        "candidate_count": len(candidate_space()),
        "candidate_grammar_family_label_free": True,
        "structured_exact_count": len(scored),
        "structured_winner": scored[0][1],
        "structured_cost": scored[0][0],
        "twin_exact_count": len(twin_scored),
        "twin_winner": twin_scored[0][1],
        "twin_cost": twin_scored[0][0],
    }


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
        "Implement binding/bundling/permutation/cleanup primitives neutrally.",
        "Neutral recovery.",
    }
    if len(ledger["rows"]) != 7 or {row["task"] for row in ledger["rows"]} != expected:
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
    neutral = neutral_recovery_certificate()
    if neutral["structured_exact_count"] != 1 or neutral["structured_winner"] != TARGET:
        raise ValueError("structured neutral recovery drifted")
    if neutral["twin_winner"] == TARGET or neutral["twin_exact_count"] != 12:
        raise ValueError("matched neutral-recovery twin drifted")
    return {"ledger_rows": 7, **receipt, "k9_coordinate_accuracy": accuracies[-1], **neutral}


if __name__ == "__main__":
    result = validate_closure()
    print("GMI_VSA_REDUCTION_CLOSURE_V1_VALID")
    for key, value in result.items():
        print(f"{key}={value}")
