#!/usr/bin/env python3
"""GMI #833 AE10 -- independent oracle, route B.

No executable import of the route-A module.

  route A                                  route B (here)
  ---------------------------------------  -------------------------------
  budget-restricted optimum from a          explicit construction of every
  subcube dynamic program over coordinate   admissible decision tree, each
  subsets                                   evaluated to a truth table
  identification curve from a closed-form   exhaustive enumeration over every
  GF(2) coset argument                      (secret, training tuple, test
                                            point), scoring the posterior
                                            majority directly
  proper-subset uniformity by counting      by comparing every restricted
  cells                                     conditional against the uniform
                                            reference distribution
"""
from fractions import Fraction as F

NBITS = 3
XS = list(range(2 ** NBITS))
B2 = [0, 1]


def _bit(x, i):
    return (x >> i) & 1


# -- explicit decision trees over a permitted coordinate set ----------------

_CACHE = {}


def oracle_tables(coords, depth):
    """Every truth table realisable by a depth<=`depth` tree that queries only
    coordinates in `coords`, built bottom-up by explicit composition."""
    key = (tuple(sorted(coords)), depth)
    if key in _CACHE:
        return _CACHE[key]
    if depth == 0:
        out = set(tuple(leaf for _ in XS) for leaf in B2)
        _CACHE[key] = out
        return out
    prev = oracle_tables(coords, depth - 1)
    out = set(prev)
    items = sorted(prev)
    for i in coords:
        for t0 in items:
            for t1 in items:
                out.add(tuple(t1[x] if _bit(x, i) else t0[x] for x in XS))
    _CACHE[key] = out
    return out


def oracle_subsets(pool, k):
    out = [()]
    for i in pool:
        out = out + [s + (i,) for s in out if len(s) < k]
    return [s for s in out if len(s) <= k]


def oracle_acc_base(P):
    return max(sum((P[(x, y)] for x in XS), F(0)) for y in B2)


def oracle_acc_full(P):
    return sum((max(P[(x, y)] for y in B2) for x in XS), F(0))


def oracle_best_acc(P, k, d, p):
    visible = [i for i in range(NBITS) if i >= NBITS - p]
    best = oracle_acc_base(P)
    for S in oracle_subsets(visible, k):
        for tab in oracle_tables(S, d):
            a = sum((P[(x, tab[x])] for x in XS), F(0))
            if a > best:
                best = a
    return best


def oracle_usable_information(P, k, d, p):
    return oracle_best_acc(P, k, d, p) - oracle_acc_base(P)


def oracle_parity_world(secret):
    P = {}
    for x in XS:
        c = 0
        v = x & secret
        while v:
            c += v & 1
            v >>= 1
        y = c % 2
        P[(x, y)] = F(1, 8)
        P[(x, 1 - y)] = F(0)
    return P


# -- identification curve by exhaustive enumeration -------------------------

def oracle_identification_curve(candidates, m):
    def par(s, x):
        c = 0
        v = s & x
        while v:
            c += v & 1
            v >>= 1
        return c % 2

    tuples = [()]
    for _ in range(m):
        tuples = [t + (v,) for t in tuples for v in XS]
    num = 0
    den = 0
    for tr in tuples:
        for s in candidates:
            labels = tuple(par(s, v) for v in tr)
            cons = [c for c in candidates
                    if tuple(par(c, v) for v in tr) == labels]
            for xt in XS:
                ones = sum(1 for c in cons if par(c, xt) == 1)
                zeros = len(cons) - ones
                truth = par(s, xt)
                if ones > zeros:
                    num += 2 if truth == 1 else 0
                elif zeros > ones:
                    num += 2 if truth == 0 else 0
                else:
                    num += 1
                den += 2
    return F(num, den)


# -- proper-subset uniformity against an explicit uniform reference ---------

def oracle_proper_subset_uniformity(secret):
    def par(s, x):
        c = 0
        v = s & x
        while v:
            c += v & 1
            v >>= 1
        return c % 2

    checked = 0
    viols = 0
    for mask in range(2 ** NBITS):
        if mask == (2 ** NBITS) - 1:
            continue
        bits = [i for i in range(NBITS) if mask & (1 << i)]
        cells = 2 ** (len(bits) + 1)
        reference = F(1, cells)
        observed = {}
        for x in XS:
            key = (tuple(_bit(x, i) for i in bits), par(secret, x))
            observed[key] = observed.get(key, F(0)) + F(1, 8)
        checked += 1
        if len(observed) != cells or any(v != reference
                                         for v in observed.values()):
            viols += 1
    return checked, viols
