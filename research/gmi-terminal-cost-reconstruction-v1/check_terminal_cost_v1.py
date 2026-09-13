"""Finite falsifying census with an independent complete syntax parent."""
import hashlib
import json
import sys
from itertools import product
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from terminal_controls_v1 import compare, controls
from terminal_kernel_v1 import terminal_kernel, reconstruct, require


def relations(size, k):
    actions = [tuple(a for a in range(k) if mask & (1 << a)) for mask in range(2**k)]
    yield from product(actions, repeat=size)


def census():
    total = {"instances": 0, "candidate_tree_executions": 0, "adequate_tree_executions": 0,
             "frontier_witnesses": 0, "cells": 0, "child_pairs": 0,
             "constructed_entries": 0, "label_transport_controls": 0}
    digest = hashlib.sha256()
    for n in range(3):
        size, queries = 2**n, tuple((i+1,) for i in range(n))
        for flat in product((0, 1), repeat=size*2):
            costs = tuple(((flat[2*x],), (flat[2*x+1],)) for x in range(size))
            for rows in relations(size, 2):
                result = compare(n, rows, costs, queries)
                total["instances"] += 1
                total["candidate_tree_executions"] += result["candidate_trees"]
                total["adequate_tree_executions"] += result["adequate_trees"]
                total["frontier_witnesses"] += len(result["frontier"])
                for key, value in result["counts"].items():
                    total[key] += value
                digest.update(json.dumps(sorted(result["frontier"]), separators=(",", ":")).encode())
                # All scalar cases: actual label-and-cost dictionary transport.
                switched = tuple(tuple(1-a for a in row) for row in rows)
                reversed_costs = tuple(tuple(reversed(row)) for row in costs)
                require(terminal_kernel(n, rows, costs, queries).keys() ==
                        terminal_kernel(n, switched, reversed_costs, queries).keys(), "cube changed")
                moved, _ = reconstruct(n, switched, reversed_costs, queries)
                require(set(moved) == result["frontier"], "transport changed frontier")
                total["label_transport_controls"] += 1
    total["frontier_census_sha256"] = digest.hexdigest()
    return total


def vector_census():
    count, digest = 0, hashlib.sha256()
    for flat in product((0, 1), repeat=8):
        costs = tuple(tuple(tuple(flat[4*x+2*a+j] for j in range(2))
                            for a in range(2)) for x in range(2))
        for rows in relations(2, 2):
            for charge in product((0, 1), repeat=2):
                result = compare(1, rows, costs, (charge,))
                count += 1
                digest.update(json.dumps(sorted(result["frontier"]), separators=(",", ":")).encode())
    return {"instances": count, "frontier_census_sha256": digest.hexdigest()}


def run():
    root = Path(__file__).resolve().parent
    names = ("terminal_kernel_v1.py", "syntax_parent_v1.py", "terminal_controls_v1.py",
             "check_terminal_cost_v1.py", "TERMINAL_COST_RECONSTRUCTION_THEOREM_V1.md")
    return {"schema": "gmi-terminal-cost-reconstruction-v1", "status": "PASS",
            "scalar_census": census(), "vector_census": vector_census(),
            "controls": controls(),
            "source_sha256": {name: hashlib.sha256((root/name).read_bytes()).hexdigest()
                              for name in names},
            "scope": "finite deterministic exact coordinate queries and supplied terminal costs",
            "physical_costs_included": False, "randomized_policies_included": False}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
