#!/usr/bin/env python3
"""Blind exhaustive prefix-code morphology recovery under frozen protocol.

The search receives only valid code-length vectors and expected-depth cost. Class
labels are applied after the winning set is known. Parent-owned coding calibration.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

OUT = Path(__file__).with_name("EXACT_BLIND_PREFIX_RECOVERY_V1.json")
P_POINTS = (0.10, 0.25, 0.50, 0.75, 0.90)


def valid_codes():
    out = []
    for d in itertools.product((1, 2, 3), repeat=4):
        if abs(sum(2.0 ** (-x) for x in d) - 1.0) < 1e-12:
            out.append(d)
    return out


def ecology(p):
    return (p / 2.0, p / 2.0, (1.0 - p) / 2.0, (1.0 - p) / 2.0)


def cost(d, p):
    return sum(prob * depth for prob, depth in zip(ecology(p), d))


def classify(d):
    if sorted(d) == [2, 2, 2, 2]:
        return "BALANCED"
    if sorted(d) == [1, 2, 3, 3]:
        shortest = set(sorted(range(4), key=lambda i: d[i])[:2])
        if shortest == {0, 1}:
            return "BIASED_TO_FIRST_PAIR"
        if shortest == {2, 3}:
            return "BIASED_TO_SECOND_PAIR"
    return "OTHER"


def build_receipt():
    candidates = valid_codes()
    assert len(candidates) == 13
    predictions = {
        0.10: "BIASED_TO_SECOND_PAIR",
        0.25: "BIASED_TO_SECOND_PAIR",
        0.50: "BALANCED",
        0.75: "BIASED_TO_FIRST_PAIR",
        0.90: "BIASED_TO_FIRST_PAIR",
    }
    rows = []
    for p in P_POINTS:
        scored = [(cost(d, p), d) for d in candidates]
        best = min(c for c, _ in scored)
        winners = [d for c, d in scored if abs(c - best) < 1e-12]
        classes = sorted(set(classify(d) for d in winners))
        recovered = classes == [predictions[p]]
        if not recovered:
            raise AssertionError((p, predictions[p], classes, winners))
        rows.append({
            "p": p,
            "predicted_class": predictions[p],
            "best_expected_depth": best,
            "winning_depth_vectors": [list(d) for d in winners],
            "winning_classes": classes,
            "prediction_recovered": recovered,
        })
    return {
        "schema": "ExactBlindPrefixRecoveryV1",
        "protocol": "BLIND_RECOVERY_PREFIX_PROTOCOL_V1.md",
        "candidate_count": len(candidates),
        "candidate_generation": "all d_i in {1,2,3} satisfying Kraft equality; no class labels used by search",
        "rows": rows,
        "terminal": "BLIND_RECOVERY_CALIBRATED_ON_PREFIX_CODE_PARENT",
        "interpretation": [
            "All five prospectively named morphology-class predictions were recovered exactly.",
            "Class labels were applied only after exhaustive cost minimization.",
            "This is a source-coding/Huffman calibration and gives no new-form or general-intelligence credit.",
            "The next real test must use a cognitive/adaptive grammar whose phase result is not already a classical coding theorem."
        ]
    }


def main():
    r = build_receipt()
    OUT.write_text(json.dumps(r, indent=2) + "\n")
    print(r["terminal"])


if __name__ == "__main__":
    main()
