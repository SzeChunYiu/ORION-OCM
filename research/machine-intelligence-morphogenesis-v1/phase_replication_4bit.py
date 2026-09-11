"""Exact execution of PHASE_REPLICATION_4BIT_FREEZE_V1.md.

Stdlib-only exhaustive complexity census + prospectively frozen sampled evaluation.
"""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations, product
import json
import random

MASK = (1 << 16) - 1
L = 1.0
V = 0.5
SEED = 20260911
ROWS = list(product((0, 1), repeat=4))


def encode(values):
    signature = 0
    for index, value in enumerate(values):
        signature |= (value & 1) << index
    return signature


def minimum_expression_sizes():
    variable_signatures = [encode(row[index] for row in ROWS) for index in range(4)]
    best = {}
    by_size = defaultdict(set)

    for signature in variable_signatures + [0, MASK]:
        best[signature] = 1
        by_size[1].add(signature)

    for size in range(2, 30):
        for a in tuple(by_size[size - 1]):
            signature = (~a) & MASK
            if signature not in best:
                best[signature] = size
                by_size[size].add(signature)

        for left_size in range(1, size - 1):
            right_size = size - 1 - left_size
            if left_size > right_size:
                continue
            left = tuple(by_size[left_size])
            right = tuple(by_size[right_size])
            if left_size == right_size:
                pairs = (
                    (a, b)
                    for index, a in enumerate(left)
                    for b in left[index:]
                )
            else:
                pairs = ((a, b) for a in left for b in right)

            for a, b in pairs:
                for signature in (a & b, a ^ b):
                    if signature not in best:
                        best[signature] = size
                        by_size[size].add(signature)

        if len(best) == 65536:
            break

    assert len(best) == 65536
    return best


def observation_pattern(function, training_rows):
    pattern = 0
    for index, row in enumerate(training_rows):
        pattern |= ((function >> row) & 1) << index
    return pattern


def build_policy(complexity, training_rows):
    groups = [[] for _ in range(16)]
    for function in range(65536):
        groups[observation_pattern(function, training_rows)].append(function)

    held_out = [row for row in range(16) if row not in training_rows]
    policies = {}
    for pattern, candidates in enumerate(groups):
        minimum = min(complexity[function] for function in candidates)
        hypotheses = [
            function for function in candidates if complexity[function] == minimum
        ]
        proposals = {}
        for query in held_out:
            first = (hypotheses[0] >> query) & 1
            proposals[query] = (
                first
                if all(((function >> query) & 1) == first for function in hypotheses)
                else None
            )
        policies[pattern] = proposals
    return held_out, policies


def evaluate(targets, complexity, training_subsets):
    prepared = [
        (training_rows, *build_policy(complexity, training_rows))
        for training_rows in training_subsets
    ]

    correct = wrong = abstain = queries = 0
    cost = 0.0
    for target in targets:
        for training_rows, held_out, policies in prepared:
            proposals = policies[observation_pattern(target, training_rows)]
            for query in held_out:
                queries += 1
                proposal = proposals[query]
                truth = (target >> query) & 1
                if proposal is None:
                    abstain += 1
                    cost += L
                elif proposal == truth:
                    correct += 1
                    cost += V
                else:
                    wrong += 1
                    cost += V + L

    attempt = correct + wrong
    return {
        "queries": queries,
        "correct": correct,
        "wrong": wrong,
        "abstain": abstain,
        "correct_rate": correct / queries,
        "wrong_rate": wrong / queries,
        "abstain_rate": abstain / queries,
        "proposal_precision": correct / attempt,
        "mean_acquisition_cost": cost / queries,
    }


def run():
    complexity = minimum_expression_sizes()
    simple = [function for function in range(65536) if complexity[function] <= 4]
    complex_pool = [function for function in range(65536) if complexity[function] >= 15]

    complex_sample = random.Random(SEED).sample(sorted(complex_pool), 256)
    all_training_subsets = list(combinations(range(16), 4))
    training_subsets = random.Random(SEED).sample(sorted(all_training_subsets), 64)

    simple_result = evaluate(simple, complexity, training_subsets)
    complex_result = evaluate(complex_sample, complexity, training_subsets)
    gap = complex_result["mean_acquisition_cost"] - simple_result["mean_acquisition_cost"]

    return {
        "schema": "PhaseReplication4BitV1",
        "freeze": "PHASE_REPLICATION_4BIT_FREEZE_V1.md",
        "universe_size": 65536,
        "max_minimum_expression_size": max(complexity.values()),
        "strata": {
            "simple_threshold": "<=4",
            "simple_count": len(simple),
            "complex_threshold": ">=15",
            "complex_pool_count": len(complex_pool),
            "complex_sample_count": len(complex_sample),
        },
        "training": {"examples": 4, "subset_count": len(training_subsets), "seed": SEED},
        "costs": {"label": L, "verify": V},
        "simple": simple_result,
        "complex": complex_result,
        "frozen_predictions": {
            "R1_simple_cost_lt_direct": simple_result["mean_acquisition_cost"] < 1.0,
            "R2_complex_cost_ge_direct": complex_result["mean_acquisition_cost"] >= 1.0,
            "R3_complex_cost_gt_simple": gap > 0,
            "complex_minus_simple_cost": gap,
        },
        "terminal": "DESCRIPTION_COMPLEXITY_AND_VERIFIER_PRICE_PREDICT_PARENT_POLICY_REGION_AT_4BIT_SCOPE",
        "claim_boundary": (
            "Prospectively frozen exact/sampled finite parent-policy crossover. The mechanism is "
            "MDL/version-space/value-of-verification and is parent-owned. This calibrates a D3-style "
            "ecology/resource -> policy-region prediction; it is not a new GMI mechanism or a "
            "cross-paradigm morphology law."
        ),
    }


def main():
    print(json.dumps(run(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
