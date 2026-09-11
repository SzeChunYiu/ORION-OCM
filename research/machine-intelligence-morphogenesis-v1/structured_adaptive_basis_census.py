"""Exact Stage C-v1 structured adaptive basis census.

Two one-bit state cells receive external input x and feedback label l. Update rules
are shallow structured expressions, not arbitrary truth tables. A topology arm may
or may not permit each cell to read the other cell's state.

Calibration/reduction study only; not a general intelligence result.
"""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations
import json

OPS = ("NOT", "AND", "XOR")
UPDATE_ROWS = [
    (self_state, other_state, x, label)
    for self_state in (0, 1)
    for other_state in (0, 1)
    for x in (0, 1)
    for label in (0, 1)
]
OUTPUT_ROWS = [
    (s0, s1, x)
    for s0 in (0, 1)
    for s1 in (0, 1)
    for x in (0, 1)
]
UPDATE_INDEX = {row: i for i, row in enumerate(UPDATE_ROWS)}
OUTPUT_INDEX = {row: i for i, row in enumerate(OUTPUT_ROWS)}
EVENTS = [(x, label) for x in (0, 1) for label in (0, 1)]
HISTORIES = [()]
HISTORIES += [(event,) for event in EVENTS]
HISTORIES += [(a, b) for a in EVENTS for b in EVENTS]


def enumerate_expressions(rows, sources, operators, max_depth=1):
    best = {}
    by_depth = defaultdict(list)

    def add(signature, depth, size, expression):
        old = best.get(signature)
        if old is None or (size, depth, expression) < (old[1], old[0], old[2]):
            if old is None:
                by_depth[depth].append(signature)
            best[signature] = (depth, size, expression)

    for name, values in sources.items():
        add(tuple(values), 0, 1, name)
    add((0,) * len(rows), 0, 1, "0")
    add((1,) * len(rows), 0, 1, "1")

    for depth in range(1, max_depth + 1):
        snapshot = list(best.items())
        if "NOT" in operators:
            for signature, (old_depth, old_size, expression) in snapshot:
                if old_depth <= depth - 1:
                    add(
                        tuple(1 - value for value in signature),
                        depth,
                        old_size + 1,
                        f"not({expression})",
                    )

        for operator in ("AND", "XOR"):
            if operator not in operators:
                continue
            snapshot = list(best.items())
            for sig_a, (depth_a, size_a, expr_a) in snapshot:
                for sig_b, (depth_b, size_b, expr_b) in snapshot:
                    if max(depth_a, depth_b) != depth - 1:
                        continue
                    if operator == "AND":
                        signature = tuple(a & b for a, b in zip(sig_a, sig_b))
                        expression = f"and({expr_a},{expr_b})"
                    else:
                        signature = tuple(a ^ b for a, b in zip(sig_a, sig_b))
                        expression = f"xor({expr_a},{expr_b})"
                    add(signature, depth, size_a + size_b + 1, expression)

    return best


def update_sources(cross_cell):
    sources = {
        "self": [row[0] for row in UPDATE_ROWS],
        "x": [row[2] for row in UPDATE_ROWS],
        "l": [row[3] for row in UPDATE_ROWS],
    }
    if cross_cell:
        sources["other"] = [row[1] for row in UPDATE_ROWS]
    return sources


def output_sources():
    return {
        "s0": [row[0] for row in OUTPUT_ROWS],
        "s1": [row[1] for row in OUTPUT_ROWS],
        "x": [row[2] for row in OUTPUT_ROWS],
    }


def developmental_signature(update0, update1, output):
    signature = []
    for history in HISTORIES:
        s0 = s1 = 0
        for x, label in history:
            next0 = update0[UPDATE_INDEX[(s0, s1, x, label)]]
            next1 = update1[UPDATE_INDEX[(s1, s0, x, label)]]
            s0, s1 = next0, next1
        for x in (0, 1):
            signature.append(output[OUTPUT_INDEX[(s0, s1, x)]])
    return tuple(signature)


def census(cross_cell, operators):
    updates = enumerate_expressions(
        UPDATE_ROWS, update_sources(cross_cell), set(operators), max_depth=1
    )
    outputs = enumerate_expressions(
        OUTPUT_ROWS, output_sources(), set(operators), max_depth=1
    )

    developmental = {}
    current_behavior = set()
    morphology_count = 0

    for sig0, (_, cost0, expr0) in updates.items():
        for sig1, (_, cost1, expr1) in updates.items():
            for out_sig, (_, output_cost, output_expr) in outputs.items():
                morphology_count += 1
                dev = developmental_signature(sig0, sig1, out_sig)
                current_behavior.add(dev[:2])
                cost = cost0 + cost1 + output_cost
                old = developmental.get(dev)
                if old is None or cost < old[0]:
                    developmental[dev] = (cost, expr0, expr1, output_expr)

    costs = [entry[0] for entry in developmental.values()]
    return {
        "cross_cell": cross_cell,
        "operators": list(operators),
        "update_semantic_classes": len(updates),
        "output_semantic_classes": len(outputs),
        "syntactic_semantic_morphology_products": morphology_count,
        "current_behavior_classes": len(current_behavior),
        "developmental_classes": len(developmental),
        "min_compilation_cost": min(costs),
        "max_min_compilation_cost": max(costs),
        "mean_min_compilation_cost": sum(costs) / len(costs),
        "cost_histogram": {
            str(cost): costs.count(cost) for cost in sorted(set(costs))
        },
    }


def run():
    arms = []
    for cross_cell in (False, True):
        for size in range(0, len(OPS) + 1):
            for subset in combinations(OPS, size):
                arms.append(census(cross_cell, subset))

    full_cross = next(
        arm
        for arm in arms
        if arm["cross_cell"] and set(arm["operators"]) == set(OPS)
    )
    and_xor_cross = next(
        arm
        for arm in arms
        if arm["cross_cell"] and set(arm["operators"]) == {"AND", "XOR"}
    )
    full_local = next(
        arm
        for arm in arms
        if not arm["cross_cell"] and set(arm["operators"]) == set(OPS)
    )

    return {
        "schema": "StructuredAdaptiveBasisCensusV1",
        "registered_history_depth": 2,
        "grammar_depth": 1,
        "state_cells": 2,
        "operator_catalogue": list(OPS),
        "arms": arms,
        "derived_findings": {
            "full_cross_developmental_classes": full_cross["developmental_classes"],
            "full_local_developmental_classes": full_local["developmental_classes"],
            "cross_cell_reach_gain": (
                full_cross["developmental_classes"]
                - full_local["developmental_classes"]
            ),
            "and_xor_matches_full_cross_reach": (
                and_xor_cross["developmental_classes"]
                == full_cross["developmental_classes"]
            ),
            "not_reduces_mean_cost_despite_equal_reach": (
                full_cross["mean_min_compilation_cost"]
                < and_xor_cross["mean_min_compilation_cost"]
            ),
            "full_cross_mean_min_cost": full_cross["mean_min_compilation_cost"],
            "and_xor_cross_mean_min_cost": and_xor_cross["mean_min_compilation_cost"],
        },
        "terminal": "STRUCTURED_ADAPTIVE_CENSUS_EXACT__TOPOLOGY_EXPANDS_BOUNDED_REACH__NOT_RESOURCE_USEFUL_NOT_REACH_NECESSARY",
        "claim_boundary": (
            "Exact finite depth-1 two-cell grammar only. Results demonstrate bounded "
            "developmental reach/resource distinctions, not a fundamental intelligence basis. "
            "State-machine/coalgebra/program parents remain live."
        ),
    }


def main():
    print(json.dumps(run(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
