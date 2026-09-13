#!/usr/bin/env python3
"""Exact finite witnesses for Grand GMI reflective self-reference theorem V1."""

from __future__ import annotations

import json
from collections import defaultdict
from itertools import product


def partition(rows, columns):
    groups = defaultdict(set)
    for i, row in enumerate(rows):
        groups[tuple(row[:columns])].add(i)
    return list(groups.values())


def check_reflective_semantic_refinement():
    matrices = 0
    refinement_checks = 0
    cardinality_checks = 0
    for bits in product((0, 1), repeat=12):
        rows = [bits[3 * i : 3 * (i + 1)] for i in range(4)]
        matrices += 1
        for columns in (1, 2):
            coarse = partition(rows, columns)
            fine = partition(rows, columns + 1)
            assert all(any(fc <= cc for cc in coarse) for fc in fine)
            assert len(fine) >= len(coarse)
            refinement_checks += 1
        exact_classes = len(partition(rows, 3))
        distinct_rows = len(set(tuple(r) for r in rows))
        assert exact_classes == distinct_rows
        cardinality_checks += 1
    return {
        "response_tables": matrices,
        "refinement_checks": refinement_checks,
        "minimal_cardinality_checks": cardinality_checks,
        "all_exact": True,
    }


def check_diagonal_impossibility():
    contexts = tuple(product((0, 1), repeat=3))
    predictor_count = 0
    failures = 0
    exact_successes = 0
    for truth_table in product((0, 1), repeat=len(contexts)):
        predictor_count += 1
        for i, _ctx in enumerate(contexts):
            p = truth_table[i]
            future = 1 - p
            failures += int(p != future)
            exact_successes += int(p == future)
    assert predictor_count == 256
    assert failures == 2048
    assert exact_successes == 0
    return {
        "predictors": predictor_count,
        "contexts_per_predictor": len(contexts),
        "diagonal_failures": failures,
        "diagonal_exact_successes": exact_successes,
        "all_exact": True,
    }


def check_nonreactive_self_prediction():
    contexts = tuple(product((0, 1), repeat=3))
    target_functions = 0
    exact_predictions = 0
    for target in product((0, 1), repeat=len(contexts)):
        predictor = tuple(target)
        target_functions += 1
        for i, _ctx in enumerate(contexts):
            assert predictor[i] == target[i]
            exact_predictions += 1
    assert target_functions == 256
    assert exact_predictions == 2048
    return {
        "fixed_target_functions": target_functions,
        "exact_context_predictions": exact_predictions,
        "all_exact": True,
    }


def update(state, action):
    if action == 0:
        return (state + 1) % 4
    if action == 1:
        return state ^ 2
    raise ValueError(action)


def sequence_reachable(budget):
    reached = {0}
    for length in range(1, budget + 1):
        for actions in product((0, 1), repeat=length):
            state = 0
            for action in actions:
                state = update(state, action)
            reached.add(state)
    return reached


def bfs_reachable(budget):
    distance = {0: 0}
    queue = [0]
    while queue:
        state = queue.pop(0)
        if distance[state] >= budget:
            continue
        for action in (0, 1):
            nxt = update(state, action)
            if nxt not in distance or distance[nxt] > distance[state] + 1:
                distance[nxt] = distance[state] + 1
                queue.append(nxt)
    return set(distance)


def lifted_reachable(budget):
    # Lift morphology state into a reflective state carrying a fixed self-model tag.
    start = (0, "self_model_v1")
    distance = {start: 0}
    queue = [start]
    while queue:
        state, tag = queue.pop(0)
        if distance[(state, tag)] >= budget:
            continue
        for action in (0, 1):
            nxt = (update(state, action), tag)
            if nxt not in distance or distance[nxt] > distance[(state, tag)] + 1:
                distance[nxt] = distance[(state, tag)] + 1
                queue.append(nxt)
    return {state for state, _tag in distance}


def check_self_modification_reachability():
    checks = []
    for budget in range(5):
        direct_seq = sequence_reachable(budget)
        direct_bfs = bfs_reachable(budget)
        lifted = lifted_reachable(budget)
        assert direct_seq == direct_bfs == lifted
        checks.append({"budget": budget, "reachable": sorted(direct_seq)})
    return {"budget_checks": checks, "all_exact": True}


def run_all():
    result = {
        "schema": "GRAND_GMI_REFLECTIVE_CHECKS_V1",
        "reflective_semantic_refinement": check_reflective_semantic_refinement(),
        "diagonal_impossibility": check_diagonal_impossibility(),
        "nonreactive_self_prediction": check_nonreactive_self_prediction(),
        "self_modification_reachability": check_self_modification_reachability(),
    }
    result["terminal"] = "GRAND_GMI_REFLECTIVE_SELF_REFERENCE_TRANCHE_ALL_GREEN"
    return result


if __name__ == "__main__":
    print(json.dumps(run_all(), indent=2, sort_keys=True))
