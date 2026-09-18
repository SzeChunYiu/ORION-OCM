#!/usr/bin/env python3
"""GMI #833 AE4 -- route B.  Materially independent oracle.

Imports NOTHING from route A, and in particular shares none of its arithmetic.

Route A carries every entropy as a rational combination of PRIME LOGARITHMS and
orders values by an exact integer power product built from that decomposition.
Route B never factorises anything.  It works with the EXPONENTIATED entropy
directly: for an exact rational distribution whose masses all have denominator
dividing `M`,

    (2^H)^M = prod_i (1/p_i)^(M p_i)

is an exact rational, because every exponent `M p_i` is an integer.  Comparing
two entropies is then comparing two exact rationals raised to a common power,
which route B does by cross-multiplying integers.  Encoders are also generated
differently: by an insert-into-a-block recursion over frozensets rather than by
restricted-growth strings.

    python3 -I -B independent_ib_oracle_v1.py
"""

from fractions import Fraction as F
import itertools
import json
import sys

N = 8
M = 8           # every atom has mass 1/8, so block masses have denominator 8


def bits(x):
    return (x & 1, (x >> 1) & 1, (x >> 2) & 1)


def y_dictator(x):
    return {bits(x)[0]: F(1)}


def y_and(x):
    b = bits(x)
    return {b[0] & b[1]: F(1)}


def y_parity(x):
    b = bits(x)
    return {b[0] ^ b[1] ^ b[2]: F(1)}


def y_pair(x):
    b = bits(x)
    return {2 * b[0] + b[1]: F(1)}


def y_skew(x):
    return {1 if x == 0 else 0: F(1)}


def y_noisy(x):
    p = F(3, 4) if bits(x)[0] == 1 else F(1, 4)
    return {1: p, 0: F(1) - p}


def y_triple(x):
    return {(0 if x < 3 else (1 if x < 6 else 2)): F(1)}


WORLDS = (("W_dictator", y_dictator), ("W_and", y_and),
          ("W_parity", y_parity), ("W_pair", y_pair),
          ("W_skew", y_skew), ("W_noisy", y_noisy), ("W_triple", y_triple))

BETAS = tuple(F(k, 2) for k in (0, 1, 2, 3, 4, 6, 8, 12, 16))


# ---------------------------------------------------------------- encoders --

def gen_partitions(n):
    """Insert-into-a-block recursion over sorted tuples of sorted blocks."""
    parts = [((0,),)]
    for e in range(1, n):
        nxt = []
        for p in parts:
            for i in range(len(p)):
                q = list(p)
                q[i] = tuple(sorted(q[i] + (e,)))
                nxt.append(tuple(sorted(q)))
            nxt.append(tuple(sorted(list(p) + [(e,)])))
        parts = nxt
    return sorted(set(parts))


def labelling(part):
    lab = [0] * N
    for i, blk in enumerate(sorted(part, key=lambda b: min(b))):
        for s in blk:
            lab[s] = i
    return "".join(str(x) for x in lab)


def refines(a, b):
    where = {}
    for i, blk in enumerate(b):
        for s in blk:
            where[s] = i
    for blk in a:
        t = where[blk[0]]
        for s in blk:
            if where[s] != t:
                return False
    return True


# -------------------------------------------- exponentiated exact entropy ---

def pow_entropy(masses, scale):
    """(2^H)^scale as an exact Fraction.

    Requires every `scale * p` to be an integer; the caller supplies a `scale`
    that clears the denominators, and a non-integral exponent raises rather than
    being rounded.
    """
    out = F(1)
    for p in masses:
        if p == 0:
            continue
        e = p * scale
        if e.denominator != 1:
            raise ValueError("scale does not clear the mass denominator")
        out *= (1 / p) ** e.numerator
    return out


def mass_scale(masses):
    sc = 1
    for p in masses:
        if p == 0:
            continue
        d = p.denominator
        g = sc
        h = d
        while h:
            g, h = h, g % h
        sc = sc * d // g
    return sc


def pow_h_t(part, scale):
    return pow_entropy([F(len(b), N) for b in part], scale)


def pow_h_y_given_t(part, pyx, scale):
    """(2^H(Y|T))^scale, exactly.

    H(Y|T) = sum_b p(b) H(Y|b), so the exponentiated form is the PRODUCT over
    blocks of (2^H(Y|b))^(scale * p(b)) -- each factor an exact rational.
    """
    out = F(1)
    for blk in part:
        mass = F(len(blk), N)
        agg = {}
        for x in blk:
            for y, p in pyx[x].items():
                agg[y] = agg.get(y, F(0)) + F(1, N) * p
        cond = [v / mass for v in agg.values()]
        out *= pow_entropy(cond, mass * scale)
    return out


def world_tables(yfun):
    py = {}
    pyx = []
    for x in range(N):
        d = yfun(x)
        pyx.append(d)
        for y, p in d.items():
            py[y] = py.get(y, F(0)) + F(1, N) * p
    return py, pyx


def gmi_state(pyx):
    key = {}
    lab = []
    for x in range(N):
        k = tuple(sorted((y, str(p)) for y, p in pyx[x].items() if p != 0))
        if k not in key:
            key[k] = len(key)
        lab.append(key[k])
    groups = {}
    for x, v in enumerate(lab):
        groups.setdefault(v, []).append(x)
    return tuple(sorted(tuple(v) for v in groups.values()))


def main():
    parts = gen_partitions(N)
    labs = [labelling(p) for p in parts]
    out_worlds = {}

    for wname, yfun in WORLDS:
        py, pyx = world_tables(yfun)
        tg = gmi_state(pyx)
        # one scale clearing every denominator in this world
        sc = 8
        for x in range(N):
            for p in pyx[x].values():
                sc = sc * p.denominator // _gcd(sc, p.denominator)
        sc *= 8
        ph = [pow_h_t(p, sc) for p in parts]
        pc = [pow_h_y_given_t(p, pyx, sc) for p in parts]

        rows = []
        threshold = None
        for beta in BETAS:
            # minimise H(T) + beta*H(Y|T); after multiplying by the positive
            # denominator of beta the comparison is of
            #   (2^H(T))^(sc*q) * (2^H(Y|T))^(sc*p)
            pn, qn = beta.numerator, beta.denominator
            best = None
            opt = []
            for i in range(len(parts)):
                v = (ph[i] ** qn) * (pc[i] ** pn)
                if best is None or v < best:
                    best, opt = v, [i]
                elif v == best:
                    opt.append(i)
            rel = {"EQUAL": 0, "GMI_STRICTLY_REFINES": 0,
                   "IB_STRICTLY_REFINES": 0, "INCOMPARABLE": 0}
            gmi_opt = False
            for i in opt:
                if parts[i] == tg:
                    gmi_opt = True
                a = refines(tg, parts[i])
                b = refines(parts[i], tg)
                if a and b:
                    rel["EQUAL"] += 1
                elif a:
                    rel["GMI_STRICTLY_REFINES"] += 1
                elif b:
                    rel["IB_STRICTLY_REFINES"] += 1
                else:
                    rel["INCOMPARABLE"] += 1
            if gmi_opt and threshold is None:
                threshold = beta
            rows.append({"beta": str(beta), "optima": len(opt),
                         "gmi_state_is_optimal": gmi_opt, "relations": rel,
                         "example_optimum": labs[opt[0]]})
        out_worlds[wname] = {
            "T_GMI": labelling(tg),
            "T_GMI_blocks": len(tg),
            "smallest_beta_at_which_T_GMI_is_IB_optimal":
                None if threshold is None else str(threshold),
            "ladder": rows,
        }

    totals = {"EQUAL": 0, "GMI_STRICTLY_REFINES": 0,
              "IB_STRICTLY_REFINES": 0, "INCOMPARABLE": 0}
    for w in out_worlds.values():
        for r in w["ladder"]:
            for k in totals:
                totals[k] += r["relations"][k]

    # a direct check of the exponentiated-entropy engine against three values
    # whose exact entropies are known by hand
    engine = {
        "H_uniform_4_is_2_bits": pow_entropy([F(1, 4)] * 4, 4) == 256,
        "H_half_is_1_bit": pow_entropy([F(1, 2)] * 2, 2) == 4,
        "H_thirds_is_log2_3": pow_entropy([F(1, 3)] * 3, 3) == 27,
        "H_thirds_exceeds_H_half": (pow_entropy([F(1, 3)] * 3, 6)
                                    > pow_entropy([F(1, 2)] * 2, 6)),
        "H_dyadic_mixture_is_seven_quarters": (
            pow_entropy([F(1, 2), F(1, 4), F(1, 8), F(1, 8)], 8) == 2 ** 14),
        "non_integral_exponent_raises": _raises(),
    }

    sys.stdout.write(json.dumps({
        "schema": "GMI_833_AE4_INDEPENDENT_ORACLE_V1",
        "route": "B",
        "method": ("insert-recursion encoders; entropies handled in "
                   "EXPONENTIATED exact-rational form (2^H)^M, never "
                   "factorised into prime logarithms"),
        "encoders_enumerated": len(parts),
        "engine_self_check": engine,
        "relation_totals": totals,
        "per_world": out_worlds,
    }, indent=2) + "\n")
    return 0


def _raises():
    """The engine must REFUSE a scale that does not clear a denominator rather
    than silently rounding it."""
    try:
        pow_entropy([F(1, 3)] * 3, 1)
    except ValueError:
        return True
    return False


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


if __name__ == "__main__":
    sys.exit(main())
