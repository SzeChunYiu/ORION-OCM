"""Exact finite query/terminal-cost antichains; no learned or physical costs."""
from fractions import Fraction
from functools import lru_cache
from itertools import product


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(n, rows, terminal, queries):
    require(type(n) is int and n >= 0, "nonnegative integer dimension required")
    require(len(rows) == 2**n and len(terminal) == 2**n, "cube dimensions")
    require(len(queries) == n, "query dimensions")
    require(bool(terminal[0]), "nonempty action alphabet")
    k, d = len(terminal[0]), len(terminal[0][0])
    require(d > 0, "nonempty cost dimension")
    for row, costs in zip(rows, terminal):
        require(len(costs) == k, "action dimensions")
        require(all(type(a) is int and 0 <= a < k for a in row), "action index")
        for vector in costs:
            require(len(vector) == d, "terminal dimensions")
    for vector in (*queries, *(v for row in terminal for v in row)):
        require(len(vector) == d, "cost dimensions")
        require(all(type(v) in (int, Fraction) and v >= 0 for v in vector),
                "exact finite nonnegative costs required")
    return k, d


def pareto(values):
    """Keep actual witnesses; never combine independently minimal coordinates."""
    return {v: witness for v, witness in values.items()
            if not any(u != v and all(a <= b for a, b in zip(u, v))
                       for u in values)}


def cells(n):
    return tuple(product((-1, 0, 1), repeat=n))


def members(p):
    return tuple(x for x in range(2**len(p))
                 if all(bit == -1 or ((x >> i) & 1) == bit
                        for i, bit in enumerate(p)))


def terminal_kernel(n, rows, terminal, queries, prune=True):
    k, d = validate(n, rows, terminal, queries)
    result = {}
    for p in cells(n):
        xs = members(p)
        values = {tuple(terminal[x][a][j] for x in xs for j in range(d)):
                  ("emit", a) for a in range(k) if all(a in rows[x] for x in xs)}
        result[p] = pareto(values) if prune else values
    return result


def reconstruct(n, rows, terminal, queries, prune=True):
    """Cost vectors flatten labelled input first, then resource coordinate."""
    _, d = validate(n, rows, terminal, queries)
    kernel = terminal_kernel(n, rows, terminal, queries, prune)
    counts = {"cells": 0, "child_pairs": 0, "constructed_entries": 0}

    @lru_cache(None)
    def visit(p):
        counts["cells"] += 1
        xs = members(p)
        values = dict(kernel[p])
        for i, bit in enumerate(p):
            if bit != -1:
                continue
            children = [p[:i] + (b,) + p[i+1:] for b in (0, 1)]
            positions = [{x: j for j, x in enumerate(members(q))} for q in children]
            for u, tu in visit(children[0]).items():
                for v, tv in visit(children[1]).items():
                    counts["child_pairs"] += 1
                    w = tuple(queries[i][j] + (u, v)[(x >> i) & 1][
                        d * positions[(x >> i) & 1][x] + j]
                              for x in xs for j in range(d))
                    counts["constructed_entries"] += len(w)
                    values[w] = ("query", i, tu, tv)
        return pareto(values) if prune else values

    return visit((-1,) * n), counts
