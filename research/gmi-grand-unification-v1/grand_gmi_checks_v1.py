#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from itertools import product
import json


def nonempty_subsets(items):
    items = tuple(items)
    out = []
    for mask in range(1, 1 << len(items)):
        out.append(frozenset(items[i] for i in range(len(items)) if mask & (1 << i)))
    return tuple(out)


def conflict_hyperedges(gamma, X, Y, A):
    X = tuple(X)
    A = set(A)
    edges = set()
    for mask in range(1, 1 << len(X)):
        B = tuple(X[i] for i in range(len(X)) if mask & (1 << i))
        if len(B) < 2:
            continue
        for y in Y:
            inter = set(A)
            for x in B:
                inter &= set(gamma[(x, y)])
            if not inter:
                edges.add(frozenset(B))
                break
    return frozenset(edges)


def hypergraph_chromatic_number(edges, X):
    X = tuple(X)
    for m in range(1, len(X) + 1):
        for colors in product(range(m), repeat=len(X)):
            c = {x: colors[i] for i, x in enumerate(X)}
            if all(len({c[x] for x in e}) > 1 for e in edges):
                return m
    raise AssertionError("finite coloring must exist")


def minimum_protocol_messages(gamma, X, Y, A):
    X = tuple(X)
    A = set(A)
    for m in range(1, len(X) + 1):
        for colors in product(range(m), repeat=len(X)):
            ok = True
            for y in Y:
                for z in range(m):
                    cell = [x for i, x in enumerate(X) if colors[i] == z]
                    if not cell:
                        continue
                    inter = set(A)
                    for x in cell:
                        inter &= set(gamma[(x, y)])
                    if not inter:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                return m
    raise AssertionError("identity protocol always exists")


def exhaustive_hypergraph_cut_check():
    X = (0, 1, 2)
    Y = (0, 1)
    A = (0, 1, 2)
    subsets = nonempty_subsets(A)
    checked = 0
    for choices in product(subsets, repeat=len(X) * len(Y)):
        gamma = {}
        k = 0
        for x in X:
            for y in Y:
                gamma[(x, y)] = choices[k]
                k += 1
        protocol = minimum_protocol_messages(gamma, X, Y, A)
        hyper = hypergraph_chromatic_number(conflict_hyperedges(gamma, X, Y, A), X)
        if protocol != hyper:
            raise AssertionError((choices, protocol, hyper))
        checked += 1
    return checked


def graph_only_failure():
    X = (0, 1, 2)
    Y = (0,)
    A = (0, 1, 2)
    sets = (frozenset((0, 1)), frozenset((1, 2)), frozenset((0, 2)))
    gamma = {(x, 0): sets[x] for x in X}
    edges = conflict_hyperedges(gamma, X, Y, A)
    pair_edges = frozenset(e for e in edges if len(e) == 2)
    return {
        "protocol_messages": minimum_protocol_messages(gamma, X, Y, A),
        "hypergraph_chromatic": hypergraph_chromatic_number(edges, X),
        "pairwise_graph_chromatic": hypergraph_chromatic_number(pair_edges, X),
        "minimal_conflict_sizes": sorted({len(e) for e in edges}),
    }


def bayes_binary_risk(q):
    return min(q, 1 - q)


def bsc_compose(q, r):
    return q * (1 - r) + (1 - q) * r


def data_processing_check():
    qs = (Fraction(0), Fraction(1, 8), Fraction(1, 4), Fraction(3, 8), Fraction(1, 2))
    rs = (Fraction(0), Fraction(1, 7), Fraction(1, 3), Fraction(1, 2))
    n = 0
    strict = 0
    for q in qs:
        for r in rs:
            q2 = bsc_compose(q, r)
            fine = bayes_binary_risk(q)
            coarse = bayes_binary_risk(q2)
            if fine > coarse:
                raise AssertionError((q, r, fine, coarse))
            strict += int(fine < coarse)
            n += 1
    return {"checks": n, "strict": strict}


def min_decision_tree_depth(n, truth):
    X = tuple(product((0, 1), repeat=n))
    values = tuple(truth(x) for x in X)

    @lru_cache(None)
    def rec(indices):
        outs = {values[i] for i in indices}
        if len(outs) <= 1:
            return 0
        best = n + 1
        for j in range(n):
            groups = []
            for b in (0, 1):
                groups.append(tuple(i for i in indices if X[i][j] == b))
            if not groups[0] or not groups[1]:
                continue
            best = min(best, 1 + max(rec(groups[0]), rec(groups[1])))
        return best

    return rec(tuple(range(len(X))))


def information_computation_separation(max_n=7):
    rows = []
    for n in range(2, max_n + 1):
        first = lambda x: x[0]
        disjunction = lambda x: int(any(x))
        d_first = min_decision_tree_depth(n, first)
        d_or = min_decision_tree_depth(n, disjunction)
        if d_first != 1 or d_or != n:
            raise AssertionError((n, d_first, d_or))
        rows.append(
            {
                "n": n,
                "final_cut_bits_first": 1,
                "final_cut_bits_or": 1,
                "query_depth_first": d_first,
                "query_depth_or": d_or,
            }
        )
    return rows


def run():
    return {
        "terminal": "GRAND_GMI_SEMANTIC_CUT_TRANCHE_ALL_GREEN",
        "determinism": "exhaustive/no-rng/exact-rational",
        "hypergraph_cut_theorem": {
            "task_families_checked": exhaustive_hypergraph_cut_check(),
            "all_equal": True,
            "graph_only_counterexample": graph_only_failure(),
        },
        "data_processing": data_processing_check(),
        "information_computation_separation": information_computation_separation(),
    }


def main():
    print(json.dumps(run(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
