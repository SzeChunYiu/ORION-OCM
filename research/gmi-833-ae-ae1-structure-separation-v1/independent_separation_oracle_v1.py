#!/usr/bin/env python3
"""GMI #833 AE1 -- independent oracle, route B.

Imports nothing from ae1_structure_separation_v1.  Every quantity is recomputed
by a materially different method:

  route A                                  route B (here)
  ---------------------------------------  --------------------------------
  acc_obs = sum_x max_y P(x,y)             maximise over the enumerated space
                                           of every deterministic rule X -> Y
  independence = entrywise product test    rank-1 test of the joint matrix
                                           over the rationals (2x2 minors)
  class membership = essential arity and   explicit recursive construction of
  memoised decision-tree depth             decision trees, evaluated to tables
  learning curve = span/rank formula       exhaustive enumeration over every
                                           (secret, training tuple, test point)
"""
from fractions import Fraction as F

B2 = [0, 1]
NBITS = 3
XS3 = list(range(2 ** NBITS))


# -- accuracies by exhaustive rule enumeration ------------------------------

def all_rules(xs, ys):
    rules = [{}]
    for x in xs:
        nxt = []
        for r in rules:
            for y in ys:
                r2 = dict(r)
                r2[x] = y
                nxt.append(r2)
        rules = nxt
    return rules


def oracle_acc_obs(P, xs, ys):
    best = None
    for r in all_rules(xs, ys):
        a = sum((P[(x, r[x])] for x in xs), F(0))
        if best is None or a > best:
            best = a
    return best


def oracle_acc_base(P, xs, ys):
    best = None
    for y0 in ys:
        a = sum((P[(x, y0)] for x in xs), F(0))
        if best is None or a > best:
            best = a
    return best


# -- independence by a rank-1 minor test ------------------------------------

def oracle_independent(P, xs, ys):
    """A nonnegative joint is a product measure iff every 2x2 minor vanishes."""
    for i in range(len(xs)):
        for j in range(i + 1, len(xs)):
            for a in range(len(ys)):
                for b in range(a + 1, len(ys)):
                    m = (P[(xs[i], ys[a])] * P[(xs[j], ys[b])]
                         - P[(xs[i], ys[b])] * P[(xs[j], ys[a])])
                    if m != 0:
                        return False
    return True


def oracle_marg_nonunif(P, xs, ys):
    tot = {}
    for x in xs:
        tot[x] = sum((P[(x, y)] for y in ys), F(0))
    u = F(1, len(xs))
    for x in xs:
        if tot[x] != u:
            return True
    return False


# -- control by exhaustive policy enumeration -------------------------------

def oracle_control(P, xs, ys, acts, U):
    py = dict((y, sum((P[(x, y)] for x in xs), F(0))) for y in ys)
    blind = None
    for a in acts:
        v = sum((py[y] * U[(a, y)] for y in ys), F(0))
        if blind is None or v > blind:
            blind = v
    best = None
    for pol in all_rules(xs, acts):
        v = sum((P[(x, y)] * U[(pol[x], y)] for x in xs for y in ys), F(0))
        if best is None or v > best:
            best = v
    return blind, best


# -- rule classes by explicit decision-tree construction --------------------

def _bit(x, i):
    return (x >> i) & 1


_DEPTH_CACHE = {}


def _tables_at_depth(d):
    """Set of (truth table, frozenset of coordinates the tree queries) pairs
    realisable by some decision tree of depth at most `d`.

    Built bottom-up by explicit tree composition: a depth-`d` tree is a root
    query on some coordinate `i` together with two depth-(d-1) subtrees, and
    the queried-coordinate set is the union plus `i`.  Nothing here classifies
    a function by essential variables or by a minimal-depth recursion, so this
    route shares no argument with the route-A rule classifier.
    """
    if d in _DEPTH_CACHE:
        return _DEPTH_CACHE[d]
    if d == 0:
        out = set((tuple(leaf for _ in XS3), frozenset()) for leaf in B2)
        _DEPTH_CACHE[0] = out
        return out
    prev = _tables_at_depth(d - 1)
    out = set(prev)
    items = sorted(prev)
    for i in range(NBITS):
        for (t0, u0) in items:
            for (t1, u1) in items:
                tab = tuple(t1[x] if _bit(x, i) else t0[x] for x in XS3)
                out.add((tab, frozenset([i]) | u0 | u1))
    _DEPTH_CACHE[d] = out
    return out


_CLASS_CACHE = {}


def oracle_rule_class(k, d):
    """Tables realisable by a depth<=d tree querying at most k coordinates."""
    key = (k, d)
    if key in _CLASS_CACHE:
        return _CLASS_CACHE[key]
    out = sorted(set(tab for (tab, used) in _tables_at_depth(d)
                     if len(used) <= k))
    _CLASS_CACHE[key] = out
    return out


def oracle_best_acc_in_class(P, k, d):
    best = None
    for tab in oracle_rule_class(k, d):
        a = sum((P[(x, tab[x])] for x in XS3), F(0))
        if best is None or a > best:
            best = a
    return best


# -- worlds (re-declared here; no import from route A) ----------------------

def oracle_parity_world(secret):
    P = {}
    for x in XS3:
        c = 0
        v = x & secret
        while v:
            c += v & 1
            v >>= 1
        y = c % 2
        P[(x, 0)] = F(1, 8) if y == 0 else F(0)
        P[(x, 1)] = F(1, 8) if y == 1 else F(0)
    return P


def oracle_noisy_dictator(num, den):
    p = F(num, den)
    P = {}
    for x in XS3:
        y = _bit(x, 0)
        P[(x, y)] = F(1, 8) * p
        P[(x, 1 - y)] = F(1, 8) - F(1, 8) * p
    return P


# -- learning curve by exhaustive enumeration -------------------------------

def oracle_learning_curve(m):
    """Expected Bayes-optimal test accuracy after m i.i.d. labelled pairs.

    Enumerates every (secret, training tuple, test point) with uniform weights
    and scores the posterior-predictive rule directly: no span, rank or
    subspace argument is used anywhere.
    """
    secrets = list(range(8))

    def par(s, x):
        c = 0
        v = s & x
        while v:
            c += v & 1
            v >>= 1
        return c % 2

    train_tuples = [()]
    for _ in range(m):
        train_tuples = [t + (v,) for t in train_tuples for v in XS3]

    num = 0
    den = 0
    for tr in train_tuples:
        for s in secrets:
            labels = tuple(par(s, v) for v in tr)
            consistent = [c for c in secrets
                          if tuple(par(c, v) for v in tr) == labels]
            for xt in XS3:
                ones = sum(1 for c in consistent if par(c, xt) == 1)
                zeros = len(consistent) - ones
                truth = par(s, xt)
                if ones > zeros:
                    num += 2 if truth == 1 else 0
                elif zeros > ones:
                    num += 2 if truth == 0 else 0
                else:
                    num += 1          # exact tie: score 1/2, doubled
                den += 2
    return F(num, den)


def oracle_marginalised_family_world():
    P = {}

    def par(s, x):
        c = 0
        v = s & x
        while v:
            c += v & 1
            v >>= 1
        return c % 2

    for x in XS3:
        ones = sum(1 for s in range(8) if par(s, x) == 1)
        P[(x, 1)] = F(1, 8) * F(ones, 8)
        P[(x, 0)] = F(1, 8) * F(8 - ones, 8)
    return P


# -- causal tables (re-derived) ---------------------------------------------

def oracle_causal():
    pz = {0: F(1, 2), 1: F(1, 2)}
    px_z = {(0, 0): F(4, 5), (1, 0): F(1, 5), (0, 1): F(1, 5), (1, 1): F(4, 5)}
    py_z = {(0, 0): F(3, 4), (1, 0): F(1, 4), (0, 1): F(1, 4), (1, 1): F(3, 4)}
    joint = {}
    for x in B2:
        for y in B2:
            joint[(x, y)] = sum((pz[z] * px_z[(x, z)] * py_z[(y, z)]
                                 for z in B2), F(0))
    do = {}
    for x in B2:
        for y in B2:
            do[(x, y)] = sum((pz[z] * py_z[(y, z)] for z in B2), F(0))
    return joint, do


# -- realizability map (independent predicates, same frozen grid) -----------

GRID_DEN = 8
MAX_SHAPE = 4


def _compositions(total, parts):
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in _compositions(total - first, parts - 1):
            yield (first,) + rest


def _oracle_integer_pattern(counts, a, b, den):
    """Independent integer re-derivation.

    MARG_NONUNIF is read off the row sums; DEP is decided by the rank-1 minor
    test on the integer matrix (all 2x2 minors vanish iff the joint is a
    product measure); PRED is decided by maximising over the enumerated space
    of every deterministic rule, exactly as oracle_acc_obs does, but on
    integers.  No entrywise product test and no argmax identity is used.
    """
    rows = [counts[x * b:(x + 1) * b] for x in range(a)]
    nx = [sum(r) for r in rows]
    ny = [sum(rows[x][y] for x in range(a)) for y in range(b)]
    marg = False
    for x in range(a):
        if nx[x] * a != den:
            marg = True
            break
    indep = True
    for i1 in range(a):
        for j1 in range(i1 + 1, a):
            for u in range(b):
                for v in range(u + 1, b):
                    if rows[i1][u] * rows[j1][v] != rows[i1][v] * rows[j1][u]:
                        indep = False
                        break
                if not indep:
                    break
            if not indep:
                break
        if not indep:
            break
    best = None
    stack = [0]
    for x in range(a):
        nxt = []
        for acc in stack:
            for y in range(b):
                nxt.append(acc + rows[x][y])
        stack = nxt
    best = max(stack)
    base = max(ny)
    return (marg, not indep, best > base)


_ORACLE_RMAP = {}


def oracle_realizability_map():
    if _ORACLE_RMAP:
        return _ORACLE_RMAP
    out = {}
    for a in range(1, MAX_SHAPE + 1):
        for b in range(1, MAX_SHAPE + 1):
            seen = set()
            for comp in _compositions(GRID_DEN, a * b):
                seen.add(_oracle_integer_pattern(comp, a, b, GRID_DEN))
            out[(a, b)] = seen
    _ORACLE_RMAP.update(out)
    return out


def oracle_minimal_shapes(rmap, pattern):
    hits = [s for s in rmap if pattern in rmap[s]]
    minimal = []
    for s in hits:
        if not any((o != s and o[0] <= s[0] and o[1] <= s[1]) for o in hits):
            minimal.append(s)
    return sorted(minimal)
