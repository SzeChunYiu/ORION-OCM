#!/usr/bin/env python3
"""GMI #833 AE2 -- independent oracle, route B.

No executable import of the route-A module.  Each quantity is recomputed by a
materially different method:

  route A                                 route B (here)
  --------------------------------------  --------------------------------
  risk from the min-over-actions identity exhaustive enumeration of every
                                          deterministic rule, plus a grid of
                                          randomised rules
  logarithm from the atanh series         the Mercator series on the
                                          reciprocal-reduced argument, plus
                                          containment in the crude analytic
                                          bracket [1 - 1/t, t - 1]
  depth-bounded optimum from a subcube    explicit bottom-up construction of
  dynamic program                         every decision tree, evaluated
  gain <= D/2 checked as a conclusion     each STEP of the proof chain
                                          checked separately on the grid
"""
from fractions import Fraction as F

B2 = [0, 1]
NBITS = 3
XS = list(range(2 ** NBITS))


# -- exhaustive rule enumeration --------------------------------------------

def all_maps(domain, codomain):
    out = [{}]
    for x in domain:
        nxt = []
        for r in out:
            for y in codomain:
                r2 = dict(r)
                r2[x] = y
                nxt.append(r2)
        out = nxt
    return out


def oracle_blind_risk(P, xs, ys, loss):
    py = dict((y, sum((P[(x, y)] for x in xs), F(0))) for y in ys)
    best = None
    for a in ys:
        v = sum((py[y] * loss(a, y) for y in ys), F(0))
        if best is None or v < best:
            best = v
    return best


def oracle_informed_risk(P, xs, ys, loss):
    """Minimum over every deterministic rule X -> Y, enumerated in full."""
    best = None
    for r in all_maps(xs, ys):
        v = sum((P[(x, y)] * loss(r[x], y) for x in xs for y in ys), F(0))
        if best is None or v < best:
            best = v
    return best


def oracle_randomised_risk_floor(P, xs, ys, loss, grid=4):
    """Smallest risk over a grid of randomised rules; must not beat the best
    deterministic rule."""
    weights = []
    if len(ys) == 2:
        weights = [(F(i, grid), F(grid - i, grid)) for i in range(grid + 1)]
    else:
        return None
    best = None
    stack = [{}]
    for x in xs:
        nxt = []
        for part in stack:
            for w in weights:
                q = dict(part)
                q[x] = w
                nxt.append(q)
        stack = nxt
    for q in stack:
        v = sum((P[(x, y)] * q[x][j] * loss(ys[j], y)
                 for x in xs for y in ys for j in range(2)), F(0))
        if best is None or v < best:
            best = v
    return best


# -- Mercator logarithm bracket ---------------------------------------------

MERCATOR_TERMS = 96


def oracle_ln_bracket(t, terms=MERCATOR_TERMS):
    """Exact rational [lo, hi] with lo <= ln(t) <= hi.

    For t >= 1 put u = (t-1)/t in [0,1); then ln(t) = -ln(1-u) = sum_k u^k/k,
    a positive series whose partial sum is a lower bound and whose tail is at
    most u^(K+1) / ((K+1)(1-u)).  For t < 1, ln(t) = -ln(1/t).
    This is a different series from route A's atanh expansion.
    """
    t = F(t)
    if t <= 0:
        raise ValueError("ln of a non-positive rational")
    if t < 1:
        lo, hi = oracle_ln_bracket(F(1) / t, terms)
        return -hi, -lo
    if t == 1:
        return F(0), F(0)
    u = (t - 1) / t
    s = F(0)
    up = u
    for k in range(1, terms + 1):
        s += up / k
        up *= u
    tail = up / ((terms + 1) * (F(1) - u))
    return s, s + tail


def oracle_crude_ln_bracket(t):
    """Parent-owned crude bracket: 1 - 1/t <= ln(t) <= t - 1 for t > 0."""
    t = F(t)
    return F(1) - F(1) / t, t - F(1)


def oracle_mutual_information_bracket(P, xs, ys):
    px = dict((x, sum((P[(x, y)] for y in ys), F(0))) for x in xs)
    py = dict((y, sum((P[(x, y)] for x in xs), F(0))) for y in ys)
    lo = F(0)
    hi = F(0)
    for x in xs:
        for y in ys:
            p = P[(x, y)]
            if p == 0:
                continue
            a, b = oracle_ln_bracket(p / (px[x] * py[y]))
            lo += p * a
            hi += p * b
    return lo, hi


# -- explicit decision trees ------------------------------------------------

def _bit(x, i):
    return (x >> i) & 1


_TREE_CACHE = {}


def oracle_tables_at_depth(d):
    """Every truth table realisable by some decision tree of depth <= d,
    built bottom-up by explicit composition of subtrees."""
    if d in _TREE_CACHE:
        return _TREE_CACHE[d]
    if d == 0:
        out = set(tuple(leaf for _ in XS) for leaf in B2)
        _TREE_CACHE[0] = out
        return out
    prev = oracle_tables_at_depth(d - 1)
    out = set(prev)
    items = sorted(prev)
    for i in range(NBITS):
        for t0 in items:
            for t1 in items:
                out.add(tuple(t1[x] if _bit(x, i) else t0[x] for x in XS))
    _TREE_CACHE[d] = out
    return out


def oracle_best_depth_bounded_accuracy(P, depth):
    best = None
    for tab in oracle_tables_at_depth(depth):
        a = sum((P[(x, tab[x])] for x in XS), F(0))
        if best is None or a > best:
            best = a
    return best


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


# -- the proof chain for gain <= D/2, step by step --------------------------

GRID_DEN = 8
GRID_MAX_SHAPE = 4


def _compositions(total, parts):
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in _compositions(total - first, parts - 1):
            yield (first,) + rest


def oracle_sweep_proof_chain():
    """Verify BOTH steps of the proof separately, not just the conclusion.

    With Delta(x,y) = n(x,y)*den - nx*ny (the joint minus the product, scaled
    by den^2) and yhat(x) any argmax of the row:

      step 1:  den * gain_numerator  <=  sum_x Delta(x, yhat(x))
      step 2:  sum_x Delta(x, yhat(x))  <=  (1/2) * sum_{x,y} |Delta(x,y)|

    Route A only checked the composed inequality, so this is an independent
    verification of the argument and not merely of its conclusion.
    """
    cases = 0
    step1_viol = 0
    step2_viol = 0
    zero_column_sum_viol = 0
    for a in range(1, GRID_MAX_SHAPE + 1):
        for b in range(1, GRID_MAX_SHAPE + 1):
            for comp in _compositions(GRID_DEN, a * b):
                rows = [comp[x * b:(x + 1) * b] for x in range(a)]
                nx = [sum(r) for r in rows]
                ny = [sum(rows[x][y] for x in range(a)) for y in range(b)]
                delta = [[rows[x][y] * GRID_DEN - nx[x] * ny[y]
                          for y in range(b)] for x in range(a)]
                for y in range(b):
                    if sum(delta[x][y] for x in range(a)) != 0:
                        zero_column_sum_viol += 1
                gnum = sum(max(r) for r in rows) - max(ny)
                mid = 0
                for x in range(a):
                    top = max(rows[x])
                    yhat = rows[x].index(top)
                    mid += delta[x][yhat]
                habs = sum(abs(delta[x][y]) for x in range(a)
                           for y in range(b))
                cases += 1
                if GRID_DEN * gnum > mid:
                    step1_viol += 1
                if 2 * mid > habs:
                    step2_viol += 1
    return cases, step1_viol, step2_viol, zero_column_sum_viol


# -- fixture re-derivations by direct simulation ----------------------------

def oracle_cyclic_gain():
    """Enumerate the Z_4 cycle directly rather than using the argmax identity."""
    zs = [0, 1, 2, 3]
    P = dict(((a, b), F(1, 4) if b == (a + 1) % 4 else F(0))
             for a in zs for b in zs)
    base = max(sum((P[(a, b)] for a in zs), F(0)) for b in zs)
    best = None
    for r in all_maps(zs, zs):
        v = sum((P[(a, r[a])] for a in zs), F(0))
        if best is None or v > best:
            best = v
    return base, best


def oracle_doubling_horizon(b, c):
    """Re-derive the certainty horizon by simulating every state path."""
    states = list(range(2 ** b))
    horizon = None
    accs = []
    for t in range(b):
        groups = {}
        for s in states:
            groups.setdefault(s >> (b - c), []).append((s >> (b - 1 - t)) & 1)
        det = all(len(set(v)) == 1 for v in groups.values())
        num = 0
        for v in groups.values():
            ones = sum(v)
            num += max(ones, len(v) - ones)
        accs.append(F(num, len(states)))
        if not det and horizon is None:
            horizon = t
    return horizon, accs


def oracle_drift_phase2_accuracy():
    """Score the phase-1 rule h(x) = x directly against phase 2."""
    ph2 = dict(((x, y), F(1, 2) if y != x else F(0))
               for x in B2 for y in B2)
    return sum((ph2[(x, x)] for x in B2), F(0))
