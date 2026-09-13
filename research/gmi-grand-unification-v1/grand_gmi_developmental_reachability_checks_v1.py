#!/usr/bin/env python3
"""Exact finite checks for DEVELOPMENTAL_REACHABILITY_SELECTION_THEOREM_V1."""

import json


EDGES = {
    "S_neutral": [
        ("N_seed", 1, "gradient"),
        ("N_alt", 1, "evolution"),
        ("P_good", 3, "synthesis"),
        ("X_ideal", 10, "exotic"),
    ],
    "N_seed": [("N_good", 1, "gradient")],
    "N_alt": [("N_good", 1, "evolution")],
    "S_program": [("P_good", 1, "synthesis")],
}

ADEQUATE = {
    "N_good": {"family": "neural", "profile": (2, 2)},
    "P_good": {"family": "program", "profile": (1, 1)},
    "X_ideal": {"family": "exotic", "profile": (0, 0)},
}


def reachable_paths(start, budget):
    out = []
    stack = [(start, 0, [])]
    while stack:
        node, cost, path = stack.pop()
        if node in ADEQUATE:
            out.append((node, cost, path))
        for nxt, step_cost, mechanism in EDGES.get(node, []):
            new_cost = cost + step_cost
            if new_cost <= budget:
                stack.append((nxt, new_cost, path + [(node, nxt, mechanism, step_cost)]))
    return out


def dominates(a, b):
    pa = ADEQUATE[a]["profile"]
    pb = ADEQUATE[b]["profile"]
    return all(x <= y for x, y in zip(pa, pb)) and any(x < y for x, y in zip(pa, pb))


def pareto(nodes):
    nodes = sorted(set(nodes))
    return [n for n in nodes if not any(dominates(m, n) for m in nodes if m != n)]


def selected_family(start, budget):
    paths = reachable_paths(start, budget)
    frontier = pareto([n for n, _, _ in paths])
    families = sorted({ADEQUATE[n]["family"] for n in frontier})
    return frontier, families, paths


def main():
    f2, fam2, p2 = selected_family("S_neutral", 2)
    assert f2 == ["N_good"]
    assert fam2 == ["neural"]

    f3, fam3, p3 = selected_family("S_neutral", 3)
    assert f3 == ["P_good"]
    assert fam3 == ["program"]

    f10, fam10, p10 = selected_family("S_neutral", 10)
    assert f10 == ["X_ideal"]
    assert fam10 == ["exotic"]

    fp, famp, pp = selected_family("S_program", 2)
    assert fp == ["P_good"]
    assert famp == ["program"]

    n_paths = [p for p in p2 if p[0] == "N_good" and p[1] == 2]
    mechanisms = sorted(tuple(edge[2] for edge in path) for _, _, path in n_paths)
    assert mechanisms == [("evolution", "evolution"), ("gradient", "gradient")]

    receipt = {
        "terminal": "GRAND_GMI_DEVELOPMENTAL_REACHABILITY_SELECTION_ALL_GREEN",
        "neutral_start_budget_2_frontier": f2,
        "neutral_start_budget_2_families": fam2,
        "neutral_start_budget_3_frontier": f3,
        "neutral_start_budget_3_families": fam3,
        "neutral_start_budget_10_frontier": f10,
        "neutral_start_budget_10_families": fam10,
        "program_start_budget_2_frontier": fp,
        "program_start_budget_2_families": famp,
        "equal_cost_distinct_mechanisms_to_neural_endpoint": [list(x) for x in mechanisms],
        "endpoint_identifies_learning_mechanism": False,
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
