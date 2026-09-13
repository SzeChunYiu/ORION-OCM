"""Exact subcube stopping table and complete no-repeat query-cost profiles."""
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from itertools import product


@dataclass(frozen=True)
class Problem:
    actions: tuple
    outputs: int
    costs: tuple

    def __post_init__(self):
        n = len(self.costs)
        if type(self.outputs) is not int or self.outputs < 1 or len(self.actions) != 1 << n:
            raise ValueError("finite nonempty output alphabet and complete cube required")
        if any(type(a) is not int or not 0 <= a < (1 << self.outputs) for a in self.actions):
            raise ValueError("action rows must be valid bitsets; empty rows are allowed")
        if any(isinstance(c, bool) or not isinstance(c, (int, F)) or c < 0 for c in self.costs):
            raise ValueError("query costs must be finite nonnegative exact rationals")
        object.__setattr__(self, "costs", tuple(map(F, self.costs)))


def table(problem):
    n = len(problem.costs)
    cells, stats = {}, dict(states=0, membership_tests=0, pattern_bit_visits=0,
                           relation_row_reads=0, bitset_intersections=0)
    for p in product((-1, 0, 1), repeat=n):
        mask = sum(1 << i for i, bit in enumerate(p) if bit != -1)
        value = sum(bit << i for i, bit in enumerate(p) if bit != -1)
        worlds = tuple(x for x in range(1 << n) if x & mask == value)
        common = (1 << problem.outputs)-1
        for x in worlds:
            common &= problem.actions[x]
        cells[p] = (worlds, common)
        stats["states"] += 1
        stats["membership_tests"] += 1 << n
        stats["pattern_bit_visits"] += 2*n
        stats["relation_row_reads"] += len(worlds)
        stats["bitset_intersections"] += len(worlds)
    return cells, stats


def synthesize(problem):
    cells, stats = table(problem)
    stats.update(query_choices=0, child_profile_pairs=0, vector_entries=0, stop_options=0)

    @lru_cache(None)
    def solve(p):
        worlds, common = cells[p]
        result = {}
        if common:
            action = (common & -common).bit_length()-1
            result[(F(0),)*len(worlds)] = ("emit", action)
            stats["stop_options"] += 1
        for i, bit in enumerate(p):
            if bit != -1:
                continue
            stats["query_choices"] += 1
            p0, p1 = list(p), list(p)
            p0[i], p1[i] = 0, 1
            p0, p1 = tuple(p0), tuple(p1)
            left, right = solve(p0), solve(p1)
            for (a, ta), (b, tb) in product(left.items(), right.items()):
                stats["child_profile_pairs"] += 1
                charged = dict(zip(cells[p0][0], a))
                charged.update(zip(cells[p1][0], b))
                vector = tuple(problem.costs[i]+charged[x] for x in worlds)
                stats["vector_entries"] += len(worlds)
                result.setdefault(vector, ("ask", i, ta, tb))
        return result

    profiles = solve((-1,)*len(problem.costs))
    return {"profiles": profiles, "gamma": tuple(bool(common) for _, common in cells.values()),
            "stats": stats, "cells": cells}


def pareto(vectors):
    vectors = set(vectors)
    return frozenset(v for v in vectors if not any(
        u != v and all(a <= b for a, b in zip(u, v)) for u in vectors))


def joint(vectors, prior):
    prior = tuple(map(F, prior))
    if any(p < 0 for p in prior) or sum(prior) != 1:
        raise ValueError("prior must be a probability distribution")
    vectors = tuple(vectors)
    if any(len(v) != len(prior) for v in vectors):
        raise ValueError("prior dimension mismatch")
    return pareto((sum(p*c for p, c in zip(prior, v)), max(v)) for v in vectors)


def feasible(vectors, prior, mean, worst):
    for bound in (mean, worst):
        if isinstance(bound, bool) or not isinstance(bound, (int, F)) or bound < 0:
            raise ValueError("resource allowances must be finite nonnegative rationals")
    return any(a <= mean and b <= worst for a, b in joint(vectors, prior))
