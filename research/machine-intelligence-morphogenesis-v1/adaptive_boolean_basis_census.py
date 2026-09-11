#!/usr/bin/env python3
"""Exact Stage-C-v0 census for tiny one-bit adaptive transducers.

A morphology has:
  output f(s, x) -> y
  update g(s, x, label) -> s'
with initial state s=0.

Free projections expose the registered variables. The primitive basis is a subset
of {NOT, AND, OR, XOR, NAND, NOR}; compositions synthesize f and g. This is
intentionally a *calibration* at the boundary of Boolean clone theory, not a new
intelligence result.

Developmental equivalence is evaluated exhaustively over all training histories of
length <= 2 and both post-history probe inputs.
"""

from __future__ import annotations

from itertools import combinations, product
from statistics import mean
from typing import Dict, Iterable, Sequence, Tuple

PRIMITIVES = ("NOT", "AND", "OR", "XOR", "NAND", "NOR")


def assignments(nvars: int) -> tuple[tuple[int, ...], ...]:
    return tuple(product((0, 1), repeat=nvars))


def variable_table(nvars: int, index: int) -> int:
    value = 0
    for i, row in enumerate(assignments(nvars)):
        value |= row[index] << i
    return value


def unary(nvars: int, a: int, op: str) -> int:
    mask = (1 << (1 << nvars)) - 1
    if op == "NOT":
        return (~a) & mask
    raise ValueError(op)


def binary(nvars: int, a: int, b: int, op: str) -> int:
    mask = (1 << (1 << nvars)) - 1
    if op == "AND":
        return a & b
    if op == "OR":
        return a | b
    if op == "XOR":
        return a ^ b
    if op == "NAND":
        return (~(a & b)) & mask
    if op == "NOR":
        return (~(a | b)) & mask
    raise ValueError(op)


def closure_depth(nvars: int, primitives: Sequence[str]) -> dict[int, int]:
    """Minimum expression depth for every reachable Boolean function."""
    depth: dict[int, int] = {variable_table(nvars, i): 0 for i in range(nvars)}
    changed = True
    while changed:
        changed = False
        current = tuple(depth.items())
        if "NOT" in primitives:
            for a, da in current:
                out = unary(nvars, a, "NOT")
                candidate = da + 1
                if out not in depth or candidate < depth[out]:
                    depth[out] = candidate
                    changed = True

        current = tuple(depth.items())
        for op in primitives:
            if op == "NOT":
                continue
            for a, da in current:
                for b, db in current:
                    out = binary(nvars, a, b, op)
                    candidate = max(da, db) + 1
                    if out not in depth or candidate < depth[out]:
                        depth[out] = candidate
                        changed = True
    return depth


def evaluate(table: int, nvars: int, values: Sequence[int]) -> int:
    rows = assignments(nvars)
    return (table >> rows.index(tuple(values))) & 1


def histories(max_length: int = 2) -> tuple[tuple[tuple[int, int], ...], ...]:
    events = tuple(product((0, 1), (0, 1)))  # (x, label)
    result: list[tuple[tuple[int, int], ...]] = [tuple()]
    for length in range(1, max_length + 1):
        result.extend(product(events, repeat=length))
    return tuple(result)


def developmental_signature(output_table: int, update_table: int) -> tuple[int, ...]:
    signature: list[int] = []
    for history in histories(2):
        state = 0
        for x, label in history:
            state = evaluate(update_table, 3, (state, x, label))
        for probe_x in (0, 1):
            signature.append(evaluate(output_table, 2, (state, probe_x)))
    return tuple(signature)


def inclusion_minimal_complete(rows: Sequence[dict]) -> list[dict]:
    complete = [row for row in rows if row["complete"]]
    result = []
    for row in complete:
        basis = set(row["basis"])
        if not any(set(other["basis"]) < basis for other in complete):
            result.append(row)
    return result


def run_census() -> dict:
    # Precompute developmental identity over the entire finite morphology universe.
    signatures = {
        (f, g): developmental_signature(f, g)
        for f in range(16)
        for g in range(256)
    }
    full_developmental_classes = len(set(signatures.values()))

    rows: list[dict] = []
    for size in range(1, len(PRIMITIVES) + 1):
        for basis_tuple in combinations(PRIMITIVES, size):
            output_depth = closure_depth(2, basis_tuple)
            update_depth = closure_depth(3, basis_tuple)
            dev_classes = {
                signatures[(f, g)]
                for f in output_depth
                for g in update_depth
            }
            complete = len(output_depth) == 16 and len(update_depth) == 256
            row = {
                "basis": list(basis_tuple),
                "output_functions": len(output_depth),
                "update_functions": len(update_depth),
                "morphologies": len(output_depth) * len(update_depth),
                "developmental_classes": len(dev_classes),
                "complete": complete,
            }
            if complete:
                costs = [
                    output_depth[f] + update_depth[g]
                    for f in range(16)
                    for g in range(256)
                ]
                row.update(
                    mean_depth_sum=mean(costs),
                    max_depth_sum=max(costs),
                )
            rows.append(row)

    minimal = inclusion_minimal_complete(rows)
    complete_rows = [row for row in rows if row["complete"]]
    best_mean = min(row["mean_depth_sum"] for row in complete_rows)
    best_resource = [
        row for row in complete_rows if row["mean_depth_sum"] == best_mean
    ]

    return {
        "terminal": "ADAPTIVE_BOOLEAN_BASIS_CENSUS_EXACT__PARENT_MATHEMATICS_DOMINATES",
        "primitive_catalogue": list(PRIMITIVES),
        "basis_count": len(rows),
        "morphology_universe": 16 * 256,
        "current_behavior_classes_from_initial_state": 4,
        "developmental_classes_history_le_2": full_developmental_classes,
        "complete_basis_count": len(complete_rows),
        "inclusion_minimal_complete": minimal,
        "best_mean_depth_complete_bases": best_resource,
        "rows": rows,
        "claim_boundary": (
            "Exact one-bit adaptive-transducer calibration over Boolean clone-style "
            "composition. Functional completeness/minimal Boolean bases are parent "
            "mathematics; this does not establish a cognitive atom or general "
            "machine-intelligence basis."
        ),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run_census(), indent=2, sort_keys=True))
