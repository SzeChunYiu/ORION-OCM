#!/usr/bin/env python3
"""Route B oracle for AE3.

Independently written: it materialises every program of a language as an
explicit (table, length) pair and minimises by enumeration, rebuilds the rule
basis from its own boolean definitions, and recomputes accuracies by direct
counting.  It imports nothing from ``ae3_compression_learning_v1``.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations

NP = 8


def b(x):
    return ((x >> 0) & 1, (x >> 1) & 1, (x >> 2) & 1)


def _basis():
    f = [
        lambda v: 0,
        lambda v: 1,
        lambda v: v[0],
        lambda v: v[1],
        lambda v: v[2],
        lambda v: v[0] ^ v[1],
        lambda v: v[0] ^ v[2],
        lambda v: v[1] ^ v[2],
        lambda v: v[0] ^ v[1] ^ v[2],
        lambda v: v[0] & v[1],
        lambda v: v[0] & v[2],
        lambda v: v[1] & v[2],
        lambda v: v[0] | v[1],
        lambda v: v[0] | v[2],
        lambda v: v[1] | v[2],
        lambda v: 1 if sum(v) >= 2 else 0,
    ]
    return [tuple(g(b(x)) for x in range(NP)) for g in f]


BASIS = _basis()
TABLES = [tuple((c >> x) & 1 for x in range(NP)) for c in range(1 << NP)]


def programs(lengths):
    """Every program of the language, as (table, code length in bits)."""
    a, n, c, d = lengths
    out = []
    for t in BASIS:
        out.append((t, a))
    for t in BASIS:
        out.append((tuple(1 - v for v in t), n))
    for i in range(len(BASIS)):
        for j in range(len(BASIS)):
            out.append(
                (tuple(BASIS[i][k] ^ BASIS[j][k] for k in range(NP)), c)
            )
    for t in TABLES:
        out.append((t, d))
    return out


def kraft(lengths):
    total = Fraction(0)
    for _t, ln in programs(lengths):
        total += Fraction(1, 1 << ln)
    return total


def code_length(table, lengths):
    best = None
    for t, ln in programs(lengths):
        if t == table and (best is None or ln < best):
            best = ln
    return best


def shortest_consistent(target, sample, lengths):
    best = None
    winners = []
    for t, ln in programs(lengths):
        if any(t[x] != target[x] for x in sample):
            continue
        if best is None or ln < best:
            best, winners = ln, [t]
        elif ln == best and t not in winners:
            winners.append(t)
    return best, winners


def junta_accuracy(target, coords):
    cells = {}
    for x in range(NP):
        v = b(x)
        k = tuple(v[c] for c in coords)
        z, o = cells.get(k, (0, 0))
        cells[k] = (z + 1 - target[x], o + target[x])
    tot = 0
    for k in cells:
        z, o = cells[k]
        tot += max(z, o)
    return Fraction(tot, NP)


def min_junta_arity(target, tau):
    for k in range(4):
        for coords in combinations(range(3), k):
            if junta_accuracy(target, coords) >= tau:
                return k
    return 4


def accuracy_on(hyp, target, points):
    return Fraction(sum(1 for x in points if hyp[x] == target[x]), len(points))


def representation_usefulness(obs, target):
    cells = {0: [0, 0], 1: [0, 0]}
    for x in range(NP):
        cells[obs[x]][target[x]] += 1
    return Fraction(sum(max(c) for c in cells.values()), NP)


def runs(table):
    return 1 + sum(1 for i in range(1, NP) if table[i] != table[i - 1])
