"""Exact execution of CROSS_REP_PHASE_4BIT_FREEZE_V1.md."""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations, product
import json
import random

MASK = (1 << 16) - 1
L = 1.0
V = 0.25
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
                pairs = ((a, b) for index, a in enumerate(left) for b in left[index:])
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


def threshold_class():
    functions = set()
    for weights in product(range(-2, 3), repeat=4):
        for bias in range(-4, 5):
            signature = 0
            for index, row in enumerate(ROWS):
                if sum(weight * bit for weight, bit in zip(weights, row)) + bias >= 0:
                    signature |= 1 << index
            functions.add(signature)
    return functions


def observation_pattern(function, subset):
    pattern = 0
    for index, row in enumerate(subset):
        pattern |= ((function >> row) & 1) << index
    return pattern


def prepare_policy(hypotheses, subset):
    groups = [[] for _ in range(16)]
    for hypothesis in hypotheses:
        groups[observation_pattern(hypothesis, subset)].append(hypothesis)
    held_out = [row for row in range(16) if row not in subset]
    proposals = {}
    for pattern, group in enumerate(groups):
        by_query = {}
        if not group:
            by_query = {query: None for query in held_out}
        else:
            for query in held_out:
                first = (group[0] >> query) & 1
                by_query[query] = (
                    first
                    if all(((hypothesis >> query) & 1) == first for hypothesis in group)
                    else None
                )
        proposals[pattern] = by_query
    return held_out, proposals, [len(group) for group in groups]


def evaluate(targets, hypotheses, subsets):
    prepared = [(subset, *prepare_policy(hypotheses, subset)) for subset in subsets]
    correct = wrong = abstain = queries = 0
    cost = 0.0
    version_sizes = []

    for target in targets:
        for subset, held_out, proposals, group_sizes in prepared:
            pattern = observation_pattern(target, subset)
            version_sizes.append(group_sizes[pattern])
            by_query = proposals[pattern]
            for query in held_out:
                queries += 1
                proposal = by_query[query]
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

    attempts = correct + wrong
    return {
        "queries": queries,
        "correct": correct,
        "wrong": wrong,
        "abstain": abstain,
        "correct_rate": correct / queries,
        "wrong_rate": wrong / queries,
        "abstain_rate": abstain / queries,
        "proposal_precision": None if attempts == 0 else correct / attempts,
        "mean_cost": cost / queries,
        "mean_version_space_size": sum(version_sizes) / len(version_sizes),
    }


def run():
    complexity = minimum_expression_sizes()
    h_threshold = threshold_class()
    h_program = {function for function, size in complexity.items() if size <= 8}

    threshold_only = sorted(h_threshold - h_program)
    program_only = sorted(h_program - h_threshold)
    overlap = sorted(h_threshold & h_program)

    subsets = random.Random(SEED).sample(sorted(combinations(range(16), 4)), 64)

    result = {
        "schema": "CrossRepresentationPhase4BitV1",
        "freeze": "CROSS_REP_PHASE_4BIT_FREEZE_V1.md",
        "class_sizes": {"H_T": len(h_threshold), "H_P": len(h_program)},
        "ecology_sizes": {
            "E_T_ONLY": len(threshold_only),
            "E_P_ONLY": len(program_only),
            "E_OVERLAP": len(overlap),
        },
        "costs": {"label": L, "verify": V},
        "results": {},
    }

    for name, targets in (
        ("E_T_ONLY", threshold_only),
        ("E_P_ONLY", program_only),
        ("E_OVERLAP", overlap),
    ):
        result["results"][name] = {
            "H_T": evaluate(targets, h_threshold, subsets),
            "H_P": evaluate(targets, h_program, subsets),
        }

    et = result["results"]["E_T_ONLY"]
    ep = result["results"]["E_P_ONLY"]
    result["frozen_predictions"] = {
        "CR_P1_threshold_region": et["H_T"]["mean_cost"] < et["H_P"]["mean_cost"],
        "CR_P2_program_region": ep["H_P"]["mean_cost"] < ep["H_T"]["mean_cost"],
        "CR_P4_reversal": (
            et["H_T"]["mean_cost"] < et["H_P"]["mean_cost"]
            and ep["H_P"]["mean_cost"] < ep["H_T"]["mean_cost"]
        ),
    }
    result["terminal"] = "REPRESENTATION_MEMBERSHIP_INSUFFICIENT__VERSION_SPACE_IDENTIFIABILITY_DOMINATES_AT_4BIT_SCOPE"
    result["claim_boundary"] = (
        "Frozen CR-P2/CR-P4 failed. H_P abstains on every held-out query after four labels, "
        "while H_T makes some checked proposals even in E_P_ONLY. Class membership alone is "
        "therefore insufficient to predict the cheaper morphology; predictive identifiability "
        "under the available experience must enter the phase law."
    )
    return result


def main():
    print(json.dumps(run(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
