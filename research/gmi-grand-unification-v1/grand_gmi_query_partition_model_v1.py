"""Exact labelled-partition query reconstruction; rational costs, all-input correctness."""
from fractions import Fraction as F
from functools import lru_cache
from itertools import product


def canonical(table):
    if not isinstance(table, tuple) or not table or len(table) & (len(table)-1):
        raise ValueError("nonempty power-of-two tuple required")
    if any(type(x) is not int or x < 0 for x in table):
        raise ValueError("output labels must be nonnegative integers")
    labels = {}
    return tuple(labels.setdefault(x, len(labels)) for x in table)


def rational(x):
    if isinstance(x, bool) or not isinstance(x, (int, F)) or x < 0:
        raise ValueError("finite nonnegative exact rational required")
    return F(x)


def register(table, costs=None, prior=None):
    table = canonical(table)
    n = len(table).bit_length()-1
    costs = (1,)*n if costs is None else costs
    prior = (F(1, len(table)),)*len(table) if prior is None else prior
    if len(costs) != n or len(prior) != len(table):
        raise ValueError("cost/prior dimensions mismatch")
    costs, prior = tuple(map(rational, costs)), tuple(map(rational, prior))
    if sum(prior) != 1:
        raise ValueError("prior must sum to one")
    return table, costs, prior, n


def optimize(table, costs=None, prior=None):
    table, costs, prior, n = register(table, costs, prior)
    count = dict(states=0, membership_tests=0, output_table_reads=0,
                 prior_mass_additions=0, candidate_queries=0)

    @lru_cache(None)
    def visit(mask, value):
        worlds = tuple(x for x in range(1 << n) if x & mask == value)
        count["states"] += 1
        count["membership_tests"] += 1 << n
        count["output_table_reads"] += len(worlds)
        count["prior_mass_additions"] += len(worlds)
        total = sum(prior[x] for x in worlds)
        classes = {table[x] for x in worlds}
        if len(classes) == 1:
            leaf = ("leaf", next(iter(classes)))
            return F(0), F(0), leaf, leaf
        choices = []
        for i in range(n):
            if mask >> i & 1:
                continue
            count["candidate_queries"] += 1
            a = visit(mask | 1 << i, value)
            b = visit(mask | 1 << i, value | 1 << i)
            choices.append((costs[i]*total+a[0]+b[0], costs[i]+max(a[1], b[1]),
                            (i, a[2], b[2]), (i, a[3], b[3])))
        mean = min(choices, key=lambda x: x[0])
        worst = min(choices, key=lambda x: x[1])
        return mean[0], worst[1], mean[2], worst[3]

    mean, worst, mean_tree, worst_tree = visit(0, 0)
    return dict(mean=mean, worst=worst, mean_tree=mean_tree, worst_tree=worst_tree,
                canonical_table=table, development=count)


def pareto(vectors):
    vectors = set(vectors)
    return frozenset(v for v in vectors if not any(
        u != v and all(a <= b for a, b in zip(u, v)) for u in vectors))


def pointwise_frontier(table, costs=None):
    table, costs, _, n = register(table, costs)
    count = dict(states=0, child_profile_combinations=0)

    @lru_cache(None)
    def visit(mask, value):
        count["states"] += 1
        worlds = tuple(x for x in range(1 << n) if x & mask == value)
        if len({table[x] for x in worlds}) == 1:
            return worlds, frozenset({(F(0),)*len(worlds)})
        candidates = set()
        for i in range(n):
            if mask >> i & 1:
                continue
            wa, va = visit(mask | 1 << i, value)
            wb, vb = visit(mask | 1 << i, value | 1 << i)
            for a, b in product(va, vb):
                count["child_profile_combinations"] += 1
                branch = dict(zip(wa, a)) | dict(zip(wb, b))
                candidates.add(tuple(costs[i]+branch[x] for x in worlds))
        return worlds, pareto(candidates)

    _, frontier = visit(0, 0)
    return dict(frontier=frontier, development=count)


def feasible(frontier, prior, mean_bound, worst_bound):
    mean_bound, worst_bound = rational(mean_bound), rational(worst_bound)
    prior = tuple(map(rational, prior))
    frontier = tuple(tuple(map(rational, v)) for v in frontier)
    if sum(prior) != 1 or any(len(v) != len(prior) for v in frontier):
        raise ValueError("invalid profile/prior dimensions")
    return any(sum(p*c for p, c in zip(prior, v)) <= mean_bound
               and max(v) <= worst_bound for v in frontier)


def execute(tree, x, n, costs):
    total, seen = F(0), set()
    while tree[0] != "leaf":
        i, left, right = tree
        if type(i) is not int or not 0 <= i < n or i in seen:
            raise ValueError("illegal or repeated query")
        seen.add(i)
        total += costs[i]
        tree = right if x >> i & 1 else left
    return tree[1], total
