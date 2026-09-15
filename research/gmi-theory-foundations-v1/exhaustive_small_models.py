#!/usr/bin/env python3
"""Exhaustive bounded reconstruction for B1-B3.

This is corroboration only. FORMALIZATION.md contains the unbounded analytic proof.
"""
from __future__ import annotations

import itertools
import json
from typing import Dict, Tuple

import validate_foundations as vf


def check_size(n: int) -> int:
    actions = ("a", "b")
    choices = tuple(itertools.product(range(2), range(n)))  # (output, next_state)
    checked = 0
    for assignment in itertools.product(choices, repeat=n * len(actions)):
        machine: Dict[int, Dict[str, Tuple[int, int]]] = {}
        i = 0
        for state in range(n):
            machine[state] = {}
            for action in actions:
                machine[state][action] = assignment[i]
                i += 1

        blocks = vf.behavioral_partition(machine)
        quotient_labels = [None] * n
        for label, block in enumerate(blocks):
            for state in block:
                quotient_labels[state] = label
        if not vf.exact_map(machine, quotient_labels):
            raise vf.ValidationError(f"quotient map failed for n={n}, machine={machine}")

        minimum = len(blocks)
        for k in range(1, minimum):
            for candidate in itertools.product(range(k), repeat=n):
                if vf.exact_map(machine, candidate):
                    raise vf.ValidationError(
                        f"too-small exact abstraction for n={n}, k={k}, machine={machine}, map={candidate}"
                    )
        checked += 1
    return checked


def main() -> None:
    counts = {str(n): check_size(n) for n in (2, 3)}
    print(json.dumps({
        "claim": "bounded exhaustive corroboration of B1-B3",
        "machine_counts": counts,
        "total_machines": sum(counts.values()),
        "universal_proof": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
