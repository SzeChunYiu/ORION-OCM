#!/usr/bin/env python3
"""Finite-exact D1--D8 and composition attacks for Issue #602 J2."""

from __future__ import annotations

import json
import math
from fractions import Fraction
from itertools import combinations, permutations, product
from pathlib import Path
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def inputs(bits: int) -> tuple[tuple[int, ...], ...]:
    return tuple(product((0, 1), repeat=bits))


def signature(bits: int, function: Callable[[tuple[int, ...]], int]) -> tuple[int, ...]:
    return tuple(int(function(row)) for row in inputs(bits))


def d1_signatures(bits: int) -> tuple[set[tuple[int, ...]], int]:
    result = set()
    parameter_count = 0
    for weights in product(range(-2, 3), repeat=bits):
        for bias in range(-2, 3):
            parameter_count += 1
            result.add(signature(bits, lambda row, w=weights, b=bias: sum(x * y for x, y in zip(row, w)) + b >= 0))
    return result, parameter_count


def d2_signatures() -> set[tuple[int, ...]]:
    result = set()
    for default in (0, 1):
        for size in range(4):
            for exceptions in combinations(range(8), size):
                result.add(tuple(1 - default if index in exceptions else default for index in range(8)))
    return result


def d4_signatures(max_steps: int = 2) -> set[tuple[int, ...]]:
    rows = inputs(3)
    base = {(0,) * 8, (1,) * 8, *(tuple(row[index] for row in rows) for index in range(3))}
    reachable = set(base)
    pools = {tuple(sorted(base))}
    for _ in range(max_steps):
        next_pools = set()
        for packed in pools:
            pool = set(packed)
            generated = {tuple(1 - bit for bit in value) for value in pool}
            for left in pool:
                for right in pool:
                    generated.add(tuple(a & b for a, b in zip(left, right)))
                    generated.add(tuple(a | b for a, b in zip(left, right)))
            for value in generated:
                reachable.add(value)
                next_pools.add(tuple(sorted(pool | {value})))
        pools = next_pools
    return reachable


def serial_two_state_signatures() -> set[tuple[int, ...]]:
    result = set()
    for transition in product(range(2), repeat=4):
        for output in product((0, 1), repeat=2):
            values = []
            for row in inputs(3):
                state = 0
                for bit in row:
                    state = transition[2 * state + bit]
                values.append(output[state])
            result.add(tuple(values))
    return result


def shared_signature_families() -> dict[str, set[tuple[int, ...]]]:
    rows = inputs(3)
    d1, _ = d1_signatures(3)
    d3 = {(0,) * 8, (1,) * 8}
    d5 = set(d3)
    for index in range(3):
        for when_zero, when_one in product((0, 1), repeat=2):
            d5.add(signature(3, lambda row, i=index, a=when_zero, b=when_one: (a, b)[row[i]]))
    d7 = {signature(3, lambda row, table=table: table[2 * row[0] + row[1]]) for table in product((0, 1), repeat=4)}
    bases = set(d3)
    for index in range(3):
        projection = tuple(row[index] for row in rows)
        bases.update((projection, tuple(1 - bit for bit in projection)))
    d8 = set(bases)
    for base in bases:
        for index in range(8):
            edited = list(base)
            edited[index] ^= 1
            d8.add(tuple(edited))
    return {
        "D1": d1,
        "D2": d2_signatures(),
        "D3": d3,
        "D4": d4_signatures(),
        "D5": d5,
        "D6": serial_two_state_signatures(),
        "D7": d7,
        "D8": d8,
    }


def _combine(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    return (
        tuple(a & b for a, b in zip(left, right)),
        tuple(a | b for a, b in zip(left, right)),
        tuple(a ^ b for a, b in zip(left, right)),
    )


def individual_attacks() -> dict[str, dict[str, Any]]:
    xor2 = signature(2, lambda row: row[0] ^ row[1])
    and2 = signature(2, lambda row: row[0] & row[1])
    d1, d1_parameters = d1_signatures(2)

    parity3 = signature(3, lambda row: row[0] ^ row[1] ^ row[2])
    d2 = d2_signatures()
    d3 = {Fraction(0), Fraction(1, 2), Fraction(1)}
    d4 = d4_signatures()

    orders = tuple(permutations(range(8)))
    d5_exact_7 = sum(all(goal in order[:7] for goal in range(8)) for order in orders)
    d5_exact_8 = sum(all(goal in order[:8] for goal in range(8)) for order in orders)

    target_mod3 = tuple(int(length % 3 == 0) for length in range(6))
    d6_counts = {}
    for states in (2, 3):
        exact = 0
        candidates = 0
        for transition in product(range(states), repeat=states):
            for output in product((0, 1), repeat=states):
                candidates += 1
                state = 0
                trace = [output[state]]
                for _ in range(5):
                    state = transition[state]
                    trace.append(output[state])
                exact += tuple(trace) == target_mod3
        d6_counts[states] = (candidates, exact)

    # Root sees only (root mark, neighbour mark) after one path round.
    d7_target = tuple(int(any(row)) for row in inputs(3))
    d7_control = tuple(int(row[0] or row[1]) for row in inputs(3))
    d7_signatures = {tuple(table[2 * row[0] + row[1]] for row in inputs(3)) for table in product((0, 1), repeat=4)}

    d8_reachable = {"00", "10", "01"}
    return {
        "D1": {"candidates": d1_parameters, "semantic_signatures": len(d1), "exact": int(xor2 in d1), "positive": and2 in d1},
        "D2": {"candidates": len(d2), "exact": int(parity3 in d2), "positive": any(sum(row) == 3 for row in d2)},
        "D3": {"candidates": len(d3), "exact": int(Fraction(1, 3) in d3), "positive": Fraction(1, 2) in d3},
        "D4": {"semantic_signatures": len(d4), "exact": int(parity3 in d4), "positive": signature(3, lambda row: row[0] & row[1]) in d4},
        "D5": {"candidates": len(orders), "exact_at_7": d5_exact_7, "positive_at_8": d5_exact_8},
        "D6": {"candidates_at_2": d6_counts[2][0], "exact_at_2": d6_counts[2][1], "candidates_at_3": d6_counts[3][0], "positive_at_3": d6_counts[3][1]},
        "D7": {"candidates": len(d7_signatures), "exact": int(d7_target in d7_signatures), "positive": d7_control in d7_signatures},
        "D8": {"candidates": len(d8_reachable), "exact": int("11" in d8_reachable), "positive": "10" in d8_reachable},
    }


def pairwise_census() -> dict[str, Any]:
    families = shared_signature_families()
    universe = set(product((0, 1), repeat=8))
    rows = {}
    for left_name, right_name in combinations(families, 2):
        combined = families[left_name] | families[right_name]
        for left in families[left_name]:
            for right in families[right_name]:
                combined.update(_combine(left, right))
        missing = sorted(universe - combined)
        rows[f"{left_name}+{right_name}"] = {
            "reachable": len(combined),
            "missing": len(missing),
            "nearest_witness": "" if not missing else "".join(map(str, missing[0])),
        }
    return {
        "family_sizes": {name: len(values) for name, values in families.items()},
        "pairs": rows,
        "pairs_with_failure": sum(row["missing"] > 0 for row in rows.values()),
        "complete_pairs": sum(row["missing"] == 0 for row in rows.values()),
    }


def higher_order_census() -> dict[str, Any]:
    families = shared_signature_families()
    names = ("D5", "D6", "D7")
    pairwise = set().union(*(families[name] for name in names))
    for left_name, right_name in combinations(names, 2):
        for left in families[left_name]:
            for right in families[right_name]:
                pairwise.update(_combine(left, right))
    triple = set()
    for d5 in families["D5"]:
        for d6 in families["D6"]:
            for first in _combine(d5, d6):
                for d7 in families["D7"]:
                    triple.update(_combine(first, d7))
    residual = sorted(triple - pairwise)
    return {
        "pairwise_reachable": len(pairwise),
        "triple_reachable": len(triple),
        "higher_order_only": len(residual),
        "nearest_witness": "".join(map(str, residual[0])),
    }


def validate_closure() -> dict[str, Any]:
    freeze = json.loads((HERE / "FREEZE_V1.json").read_text(encoding="utf-8"))
    ledger = json.loads((HERE / "J2_CLOSURE_LEDGER_V1.json").read_text(encoding="utf-8"))
    receipt = json.loads((HERE / "RESULT_V1.json").read_text(encoding="utf-8"))
    if freeze["schema"] != "GMI_J2_BOUNDED_COMPLETENESS_FREEZE_V1" or len(freeze["individual_bounds"]) != 8:
        raise ValueError("J2 freeze drifted")
    if len(ledger["rows"]) != 11 or any(row["status"] != "GREEN" for row in ledger["rows"]):
        raise ValueError("J2 task ledger drifted")
    for row in ledger["rows"]:
        if not (REPO / row["evidence"].split("#", 1)[0]).is_file():
            raise ValueError(f"missing evidence: {row['evidence']}")

    attacks = individual_attacks()
    for name, row in attacks.items():
        exact_key = "exact_at_7" if name == "D5" else "exact_at_2" if name == "D6" else "exact"
        positive_key = "positive_at_8" if name == "D5" else "positive_at_3" if name == "D6" else "positive"
        if row[exact_key] != 0 or not row[positive_key]:
            raise ValueError(f"{name} attack/control drifted")
    if attacks["D5"]["candidates"] != math.factorial(8) or attacks["D6"]["candidates_at_3"] != 216:
        raise ValueError("independent finite candidate count drifted")

    pairs = pairwise_census()
    expected_sizes = {"D1": 100, "D2": 186, "D3": 2, "D4": 40, "D5": 8, "D6": 18, "D7": 16, "D8": 72}
    if pairs["family_sizes"] != expected_sizes or len(pairs["pairs"]) != math.comb(8, 2):
        raise ValueError("shared family/pair census drifted")
    if (pairs["pairs_with_failure"], pairs["complete_pairs"]) != (22, 6):
        raise ValueError("pairwise result drifted")
    higher = higher_order_census()
    if higher != {"pairwise_reachable": 194, "triple_reachable": 256, "higher_order_only": 62, "nearest_witness": "00000111"}:
        raise ValueError("higher-order result drifted")
    if receipt["schema"] != "GMI_J2_BOUNDED_COMPLETENESS_RESULT_V1" or receipt["status"] != "EXECUTED_FINITE_EXACT":
        raise ValueError("J2 receipt schema/status drifted")
    for name, expected in receipt["individual"].items():
        if any(attacks[name][key] != value for key, value in expected.items()):
            raise ValueError(f"{name} receipt reconciliation failed")
    if receipt["shared_family_sizes"] != pairs["family_sizes"]:
        raise ValueError("family-size receipt reconciliation failed")
    if receipt["pairwise"] != {"pairs": len(pairs["pairs"]), "pairs_with_failure": pairs["pairs_with_failure"], "complete_pairs": pairs["complete_pairs"]}:
        raise ValueError("pairwise receipt reconciliation failed")
    if any(higher[key] != value for key, value in receipt["higher_order"].items() if key != "families"):
        raise ValueError("higher-order receipt reconciliation failed")
    return {"ledger_rows": 11, "attacks": attacks, "pairwise": pairs, "higher_order": higher}


if __name__ == "__main__":
    result = validate_closure()
    print("GMI_J2_BOUNDED_COMPLETENESS_V1_VALID")
    print(json.dumps(result, sort_keys=True))
