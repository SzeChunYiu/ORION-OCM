#!/usr/bin/env python3
"""Independent raw-syntax census for #768 C1-1/C1-3.

The production search uses semantic dynamic programming and therefore intentionally
prunes syntactically different subexpressions once an equivalent cheaper semantic
table exists.  This checker independently enumerates *every raw syntax tree* through
the frozen node-cost cap and verifies that semantic pruning loses no registered
behavior and does not change any target's global bounded minimum cost.
"""

from __future__ import annotations

from fractions import Fraction
import json
from typing import TypeAlias

from neutral_three_law_v1 import (
    COST_CAP,
    FROZEN_PROTOCOL,
    POINTS,
    enumerate_semantic_quotient,
)

Ast: TypeAlias = tuple

LEAVES: tuple[Ast, ...] = (
    ("var", "w"),
    ("var", "x"),
    ("var", "y"),
    ("var", "r"),
    ("const", -1),
    ("const", 0),
    ("const", 1),
)
BINARY_OPS = ("add", "sub", "mul")
VAR_INDEX = {"w": 0, "x": 1, "y": 2, "r": 3}
EXPECTED_RAW_COUNTS = [7, 7, 154, 448, 7063, 32347]
EXPECTED_SEMANTIC_FIRST_COUNTS = [7, 6, 60, 128, 650, 1834]
EXPECTED_TARGET_COSTS = {"OPAQUE_A": 4, "OPAQUE_B": 6, "OPAQUE_C": 6}


def build_raw_layers() -> dict[int, list[Ast]]:
    """Enumerate every syntax tree at each exact frozen node cost, without quotienting."""
    layers: dict[int, list[Ast]] = {1: list(LEAVES)}
    for cost in range(2, COST_CAP + 1):
        layer: list[Ast] = []
        # Unary node cost is one.
        for child in layers[cost - 1]:
            layer.append(("half", child))
        # Binary node cost is one; order is syntactic and therefore retained.
        for left_cost in range(1, cost - 1):
            right_cost = cost - 1 - left_cost
            if right_cost < 1:
                continue
            for left in layers[left_cost]:
                for right in layers[right_cost]:
                    for op in BINARY_OPS:
                        layer.append((op, left, right))
        layers[cost] = layer
    return layers


def eval_ast(ast: Ast, point: tuple[Fraction, ...]) -> Fraction:
    tag = ast[0]
    if tag == "var":
        return point[VAR_INDEX[ast[1]]]
    if tag == "const":
        return Fraction(ast[1])
    if tag == "half":
        return eval_ast(ast[1], point) / 2
    left = eval_ast(ast[1], point)
    right = eval_ast(ast[2], point)
    if tag == "add":
        return left + right
    if tag == "sub":
        return left - right
    if tag == "mul":
        return left * right
    raise ValueError(f"unknown AST tag: {tag}")


def table(ast: Ast) -> tuple[Fraction, ...]:
    return tuple(eval_ast(ast, point) for point in POINTS)


def independent_targets() -> dict[str, tuple[Fraction, ...]]:
    """Construct target tables independently from the search module's target helper."""
    rows: dict[str, list[Fraction]] = {key: [] for key in EXPECTED_TARGET_COSTS}
    for point in POINTS:
        w, x, y, r = point
        rows["OPAQUE_A"].append((w + y) / 2)
        rows["OPAQUE_B"].append(w + (x * y) / 2)
        rows["OPAQUE_C"].append(w + (r * x) / 2)
    return {key: tuple(values) for key, values in rows.items()}


def main() -> int:
    failures: list[str] = []
    raw_layers = build_raw_layers()
    quotient, semantic_layers = enumerate_semantic_quotient(FROZEN_PROTOCOL)
    targets = independent_targets()

    raw_counts = [len(raw_layers[cost]) for cost in range(1, COST_CAP + 1)]
    if raw_counts != EXPECTED_RAW_COUNTS:
        failures.append(f"raw syntax census drift: {raw_counts} != {EXPECTED_RAW_COUNTS}")

    seen_semantics: set[tuple[Fraction, ...]] = set()
    semantic_first_counts: list[int] = []
    target_min_cost: dict[str, int | None] = {key: None for key in targets}
    missing_from_quotient = 0

    for cost in range(1, COST_CAP + 1):
        first_this_layer = 0
        for ast in raw_layers[cost]:
            semantics = table(ast)
            record = quotient.get(semantics)
            if record is None or record.cost > cost:
                missing_from_quotient += 1
            if semantics not in seen_semantics:
                seen_semantics.add(semantics)
                first_this_layer += 1
            for target_id, target_table in targets.items():
                if target_min_cost[target_id] is None and semantics == target_table:
                    target_min_cost[target_id] = cost
        semantic_first_counts.append(first_this_layer)

    quotient_layer_counts = [len(semantic_layers[cost]) for cost in range(1, COST_CAP + 1)]
    if missing_from_quotient:
        failures.append(f"{missing_from_quotient} raw expressions have semantics absent or too late in quotient")
    if semantic_first_counts != EXPECTED_SEMANTIC_FIRST_COUNTS:
        failures.append(
            f"independent semantic first-hit census drift: {semantic_first_counts} != {EXPECTED_SEMANTIC_FIRST_COUNTS}"
        )
    if quotient_layer_counts != semantic_first_counts:
        failures.append(
            f"quotient first-hit layers disagree with raw enumeration: {quotient_layer_counts} != {semantic_first_counts}"
        )
    if len(seen_semantics) != len(quotient):
        failures.append(
            f"semantic total mismatch: raw={len(seen_semantics)} quotient={len(quotient)}"
        )
    if target_min_cost != EXPECTED_TARGET_COSTS:
        failures.append(f"target raw minimum costs drift: {target_min_cost} != {EXPECTED_TARGET_COSTS}")

    receipt = {
        "schema": "GMI_NEUTRAL_THREE_LAW_RAW_SYNTAX_CERT_V1",
        "verdict": "PASS" if not failures else "FAIL",
        "cost_cap": COST_CAP,
        "raw_syntax_counts": raw_counts,
        "raw_syntax_total": sum(raw_counts),
        "semantic_first_hit_counts": semantic_first_counts,
        "semantic_total": len(seen_semantics),
        "quotient_layer_counts": quotient_layer_counts,
        "quotient_total": len(quotient),
        "raw_expressions_missing_or_late_in_quotient": missing_from_quotient,
        "target_raw_minimum_costs": target_min_cost,
        "failures": failures,
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
