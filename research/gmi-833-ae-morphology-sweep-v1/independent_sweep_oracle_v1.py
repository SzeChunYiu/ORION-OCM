#!/usr/bin/env python3
"""Route B oracle for the AE morphology sweep.

Independently written.  It imports nothing from ``morphology_sweep_v1`` and
shares no algorithm with it: every class member is materialised as an explicit
8-entry truth table and scored by direct summation, the selection rule is
re-implemented from the parent's written definition, and the causal fixtures are
rebuilt from their structural equations rather than from the other module's
joints.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product

NP = 8
BITS = [tuple((x >> i) & 1 for i in range(3)) for x in range(NP)]

CLASS_RESOURCES = {
    "m0_constant": (0, 0, 1),
    "m1_arity1_junta": (1, 1, 2),
    "m2_arity2_junta": (2, 2, 4),
    "m4_gf2_affine": (3, 1, 4),
    "m3_arity3_table": (3, 3, 8),
}
ORDER = [
    "m0_constant",
    "m1_arity1_junta",
    "m2_arity2_junta",
    "m4_gf2_affine",
    "m3_arity3_table",
]


def _all_tables():
    return [tuple((c >> x) & 1 for x in range(NP)) for c in range(1 << NP)]


def _depends_on(table, coord):
    for x in range(NP):
        y = x ^ (1 << coord)
        if table[x] != table[y]:
            return True
    return False


def _support(table):
    return tuple(c for c in range(3) if _depends_on(table, c))


def class_members(name):
    """Explicit enumeration of every hypothesis in the class."""
    out = []
    for t in _all_tables():
        sup = _support(t)
        if name == "m0_constant":
            keep = len(sup) == 0
        elif name == "m1_arity1_junta":
            keep = len(sup) <= 1
        elif name == "m2_arity2_junta":
            keep = len(sup) <= 2
        elif name == "m3_arity3_table":
            keep = True
        elif name == "m4_gf2_affine":
            keep = False
            for a in range(NP):
                for b in (0, 1):
                    cand = tuple(
                        (bin(a & x).count("1") % 2) ^ b for x in range(NP)
                    )
                    if cand == t:
                        keep = True
                        break
                if keep:
                    break
        else:
            raise KeyError(name)
        if keep:
            out.append(t)
    return out


MEMBERS = dict((n, class_members(n)) for n in ORDER)


def accuracy(px, py1, table):
    tot = Fraction(0)
    for x in range(NP):
        tot += px[x] * (py1[x] if table[x] == 1 else 1 - py1[x])
    return tot


def best_accuracy(px, py1, name):
    best = Fraction(0)
    for t in MEMBERS[name]:
        a = accuracy(px, py1, t)
        if a > best:
            best = a
    return best


def profile(px, py1):
    return tuple(best_accuracy(px, py1, n) for n in ORDER)


def selection(prof, tau, price):
    for p in price:
        if p <= 0:
            raise ValueError("price must be strictly positive")
    act = [ORDER[i] for i in range(len(ORDER)) if prof[i] >= tau]
    if not act:
        return ("NO_VIABLE_MORPHOLOGY", ())
    cost = {}
    for m in act:
        r = CLASS_RESOURCES[m]
        cost[m] = sum(price[i] * r[i] for i in range(3))
    lo = min(cost.values())
    win = tuple(m for m in act if cost[m] == lo)
    return ("SELECTED" if len(win) == 1 else "TIED", win)


UNI = tuple(Fraction(1, NP) for _ in range(NP))


def deterministic_profile(table):
    return profile(UNI, tuple(Fraction(v) for v in table))


# --- causal fixtures rebuilt from structural equations -----------------------

HI = Fraction(3, 4)
LO = Fraction(1, 4)
H = Fraction(1, 2)


def _collect(samples):
    """samples: dict (a,b,d,c) -> Fraction; returns (px, py1)."""
    px = [Fraction(0)] * NP
    p1 = [Fraction(0)] * NP
    for key in samples:
        a, b, d, c = key
        x = a | (b << 1) | (d << 2)
        px[x] += samples[key]
        if c:
            p1[x] += samples[key]
    py1 = []
    for x in range(NP):
        py1.append(p1[x] / px[x] if px[x] else Fraction(0))
    return tuple(px), tuple(py1)


def world_L(do_a):
    """A -> C.  do(A) leaves the A -> C edge intact."""
    s = {}
    for a, b, d, c in product((0, 1), repeat=4):
        pa = H
        pc = HI if a == 1 else LO
        pc = pc if c == 1 else 1 - pc
        s[(a, b, d, c)] = pa * pc * H * H
    return _collect(s)


def world_R(do_a):
    """C -> A.  do(A) severs the C -> A edge, so C becomes independent of A."""
    s = {}
    for a, b, d, c in product((0, 1), repeat=4):
        pc = H
        if do_a:
            pa = H
        else:
            pr = HI if c == 1 else LO
            pa = pr if a == 1 else 1 - pr
        s[(a, b, d, c)] = pc * pa * H * H
    return _collect(s)


def joint(px, py1):
    return tuple((px[x] * (1 - py1[x]), px[x] * py1[x]) for x in range(NP))
