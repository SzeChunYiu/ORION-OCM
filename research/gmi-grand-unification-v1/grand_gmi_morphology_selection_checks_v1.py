#!/usr/bin/env python3
"""Exact finite witness for MORPHOLOGY_SELECTION_THEOREM_V1."""

import json


CANDIDATES = [
    {"name": "N_shared", "family": "neural", "profile": (4, 3, 2), "reachable": True, "shared_local": True},
    {"name": "P_shared", "family": "program", "profile": (3, 5, 1), "reachable": True, "shared_local": True},
    {"name": "N_dense", "family": "neural", "profile": (8, 8, 4), "reachable": True, "shared_local": False},
    {"name": "T_table", "family": "table", "profile": (2, 16, 1), "reachable": True, "shared_local": False},
    {"name": "X_ideal", "family": "exotic", "profile": (1, 1, 1), "reachable": False, "shared_local": True},
]


def dominates(a, b):
    pa, pb = a["profile"], b["profile"]
    return all(x <= y for x, y in zip(pa, pb)) and any(x < y for x, y in zip(pa, pb))


def pareto(xs):
    return [x for x in xs if not any(dominates(y, x) for y in xs if y is not x)]


def names(xs):
    return [x["name"] for x in xs]


def main():
    reachable = [x for x in CANDIDATES if x["reachable"]]
    base = names(pareto(reachable))
    assert base == ["N_shared", "P_shared", "T_table"]
    assert "N_dense" not in base

    memory6 = [x for x in reachable if x["profile"][1] <= 6]
    memory6_frontier = names(pareto(memory6))
    assert memory6_frontier == ["N_shared", "P_shared"]

    tight = [x for x in reachable if x["profile"][1] <= 4 and x["profile"][2] <= 2]
    tight_frontier = names(pareto(tight))
    assert tight_frontier == ["N_shared"]

    static_frontier = names(pareto(CANDIDATES))
    assert static_frontier == ["X_ideal"]

    receipt = {
        "terminal": "GRAND_GMI_MORPHOLOGY_SELECTION_FINITE_CHECKS_ALL_GREEN",
        "reachable_frontier": base,
        "memory_le_6_frontier": memory6_frontier,
        "memory_le_4_latency_le_2_frontier": tight_frontier,
        "static_frontier_if_reachability_removed": static_frontier,
        "neurality_derived_on_base_frontier": all(x["family"] == "neural" for x in pareto(reachable)),
        "neurality_derived_under_tight_registered_constraints": all(x["family"] == "neural" for x in pareto(tight)),
        "scope_boundary": "Synthetic exact finite resource profiles; verifies selection logic, not empirical hardware costs."
    }
    assert receipt["neurality_derived_on_base_frontier"] is False
    assert receipt["neurality_derived_under_tight_registered_constraints"] is True
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
