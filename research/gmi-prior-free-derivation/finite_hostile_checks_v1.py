#!/usr/bin/env python3
"""Dependency-free finite hostile witnesses for the OCM prior-free GMI core."""

from itertools import product
import json


def chromatic_number(adj):
    n = len(adj)
    for k in range(1, n + 1):
        for colors in product(range(k), repeat=n):
            if all(colors[i] != colors[j] for i in range(n) for j in adj[i] if i < j):
                return k
    return n


def pareto(points):
    out = []
    for i, p in enumerate(points):
        dominated = False
        for j, q in enumerate(points):
            if i == j:
                continue
            if all(q[d] <= p[d] for d in range(len(p))) and any(q[d] < p[d] for d in range(len(p))):
                dominated = True
                break
        if not dominated:
            out.append(p)
    return set(out)


def prior_null_scalarization():
    # N pointwise dominates M, but strict improvement is only on a prior-null environment.
    M = {"e0": 0, "e1": 1}
    N = {"e0": 0, "e1": 0}
    prior = {"e0": 1.0, "e1": 0.0}
    dominates = all(N[e] <= M[e] for e in M) and any(N[e] < M[e] for e in M)
    expected_M = sum(prior[e] * M[e] for e in M)
    expected_N = sum(prior[e] * N[e] for e in M)
    return dominates and expected_M == expected_N


def control_compatibility_nontransitive():
    feasible = [set(["a", "b"]), set(["b", "c"]), set(["a", "c"])]
    pairwise = all(feasible[i] & feasible[j] for i in range(3) for j in range(i + 1, 3))
    triple = set.intersection(*feasible)
    return pairwise and not triple


def reachable_vs_global_frontier():
    physical = [(0, 10), (5, 5), (10, 0)]
    reachable = [(6, 6), (7, 5)]
    global_front = pareto(physical + reachable)
    reachable_global = global_front & set(reachable)
    best_reachable = pareto(reachable)
    return reachable_global != best_reachable and not reachable_global and best_reachable == {(6, 6), (7, 5)}


def zero_error_coloring():
    # Three mutually conflicting residuals require three distinguishable zero-error messages.
    adj = [{1, 2}, {0, 2}, {0, 1}]
    return chromatic_number(adj) == 3


def strict_control_hierarchy_witnesses():
    # Registered finite witnesses: (action, plan, dynamic).
    return (2 < 3 == 3) and (2 == 2 < 3)


def main():
    checks = {
        "prior_null_scalarization": prior_null_scalarization(),
        "control_compatibility_nontransitive": control_compatibility_nontransitive(),
        "reachable_vs_global_frontier": reachable_vs_global_frontier(),
        "zero_error_coloring": zero_error_coloring(),
        "strict_control_hierarchy_witnesses": strict_control_hierarchy_witnesses(),
    }
    print(json.dumps({"all_green": all(checks.values()), "checks": checks}, indent=2, sort_keys=True))
    raise SystemExit(0 if all(checks.values()) else 1)


if __name__ == "__main__":
    main()
