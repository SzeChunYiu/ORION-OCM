"""Independent complete source-tree enumeration and concrete execution.

No imported kernel, subcube recurrence, adequacy pruning, or frontier routine.
"""
from functools import lru_cache
from itertools import product


@lru_cache(None)
def trees(available, alphabet):
    result = [("emit", a) for a in range(alphabet)]
    for i in available:
        smaller = tuple(j for j in available if j != i)
        children = trees(smaller, alphabet)
        result.extend(("query", i, left, right) for left, right in product(children, repeat=2))
    return tuple(result)


def execute(tree, x, terminal, queries):
    total = [0] * len(terminal[x][0])
    while tree[0] == "query":
        _, i, left, right = tree
        total = [a + b for a, b in zip(total, queries[i])]
        tree = (left, right)[(x >> i) & 1]
    a = tree[1]
    return a, tuple(v + c for v, c in zip(total, terminal[x][a]))


def profiles(n, rows, terminal, queries):
    values, accepted = set(), 0
    candidates = trees(tuple(range(n)), len(terminal[0]))
    for tree in candidates:
        cost = []
        for x, allowed in enumerate(rows):
            a, vector = execute(tree, x, terminal, queries)
            if a not in allowed:
                break
            cost.extend(vector)
        else:
            accepted += 1
            values.add(tuple(cost))
    return values, len(candidates), accepted


def frontier(values):
    result = set()
    for candidate in values:
        dominated = False
        for other in values:
            if other == candidate:
                continue
            if not any(a > b for a, b in zip(other, candidate)):
                dominated = True
                break
        if not dominated:
            result.add(candidate)
    return result
