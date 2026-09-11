#!/usr/bin/env python3
"""Exact finite calibration for Track-B GMI-D2.

Enumerates the closure of binary Boolean functions under small primitive sets.
This is a machinery calibration only: Boolean functional completeness is parent-owned
and is NOT evidence for a machine-intelligence basis.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
import json

MASK = 0b1111
PROJECTIONS = {"x": 0b1100, "y": 0b1010}


@dataclass(frozen=True)
class Primitive:
    name: str
    arity: int


PRIMITIVES = {
    "NOT": Primitive("NOT", 1),
    "AND": Primitive("AND", 2),
    "OR": Primitive("OR", 2),
    "XOR": Primitive("XOR", 2),
    "NAND": Primitive("NAND", 2),
    "NOR": Primitive("NOR", 2),
}


def apply_primitive(name: str, args: tuple[int, ...]) -> int:
    if name == "NOT":
        return (~args[0]) & MASK
    if name == "AND":
        return args[0] & args[1]
    if name == "OR":
        return args[0] | args[1]
    if name == "XOR":
        return args[0] ^ args[1]
    if name == "NAND":
        return (~(args[0] & args[1])) & MASK
    if name == "NOR":
        return (~(args[0] | args[1])) & MASK
    raise KeyError(name)


def closure(names: tuple[str, ...]) -> dict[int, tuple[int, str]]:
    """Return truth table -> (minimum expression depth, one expression)."""
    known = {v: (0, k) for k, v in PROJECTIONS.items()}
    changed = True
    while changed:
        changed = False
        snapshot = list(known.items())
        for name in names:
            prim = PRIMITIVES[name]
            if prim.arity == 1:
                iterator = ((a,) for a, _ in snapshot)
            else:
                vals = [a for a, _ in snapshot]
                iterator = product(vals, repeat=2)
            for args in iterator:
                out = apply_primitive(name, args)
                depth = 1 + max(known[a][0] for a in args)
                expr = f"{name}({','.join(known[a][1] for a in args)})"
                old = known.get(out)
                if old is None or depth < old[0]:
                    known[out] = (depth, expr)
                    changed = True
    return known


def all_subsets(items):
    for r in range(1, len(items) + 1):
        for subset in combinations(items, r):
            yield subset


def run_census() -> dict:
    names = tuple(PRIMITIVES)
    results = []
    for subset in all_subsets(names):
        c = closure(subset)
        results.append(
            {
                "basis": list(subset),
                "closure_size": len(c),
                "functionally_complete_2bit": len(c) == 16,
                "max_min_depth": max(d for d, _ in c.values()),
            }
        )

    complete = [r for r in results if r["functionally_complete_2bit"]]
    minimal = []
    for r in complete:
        s = set(r["basis"])
        if not any(
            set(q["basis"]) < s and q["functionally_complete_2bit"]
            for q in results
        ):
            minimal.append(r)

    compensation = {}
    for r in minimal:
        basis = tuple(r["basis"])
        compensation["+".join(basis)] = {
            p: len(closure(tuple(q for q in basis if q != p))) for p in basis
        }

    return {
        "schema": "ExactBooleanBasisCensusV1",
        "scope": "all 16 binary Boolean functions under composition with projections x,y",
        "claim_boundary": "calibration only; no intelligence or novelty claim",
        "subset_count": len(results),
        "complete_subset_count": len(complete),
        "minimal_complete_bases": minimal,
        "compensation_aware_removal_closure_sizes": compensation,
        "all_results": results,
    }


def main() -> None:
    print(json.dumps(run_census(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
