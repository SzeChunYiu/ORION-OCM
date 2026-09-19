#!/usr/bin/env python3
"""Route B - independent oracle for AE6 (issue #833, comment 5692689542).

This module contains NO executable import of route A and recomputes every
claimed quantity by a materially different algorithm:

  quantity                route A                      route B (here)
  ----------------------  ---------------------------  ------------------------
  affine dimension        GF(2) Gaussian elimination   affine closure to a fixed
                                                       point, dimension read off
                                                       the closure's cardinality
  cosets                  subspace enumeration by      affine closure of every
                          independent generator tuples subset of the support
  union predicate         maximal-piece pruning plus   exact bitmask cover search
                          itertools.combinations       over closed subsets
  symmetry                subgroup-lattice enumeration direct scan of all 24
                          plus orbit partitions        permutations, orbits by
                                                       union-find
  class accuracies        per-cell argmax identities   enumeration of all 2^16
                                                       truth tables filtered by
                                                       the class predicate
  modular membership      enumeration of (h1,h2,g)     the 4x4 value matrix has
                                                       at most 2 distinct rows
                                                       and at most 2 distinct
                                                       columns
  monomial count          in-place Moebius butterfly   direct subset summation
  cycle rank              |E| - |V| + components       edges minus spanning
                                                       forest size, via union-find
  Kraft sum               closed-form description      explicit enumeration of
                          counts                       every description length

Usage:  python3 -I -B independent_geometry_oracle_v1.py > ORACLE.json
"""
from __future__ import annotations

import itertools
import json
import sys
from fractions import Fraction

N = 4
POINTS = tuple(range(1 << N))
BLOCKS = ((0, 1), (2, 3))
BLOCK_SUPPORT_CAP = 2
UNION_RANK_CAP = 3
NULL_TRIALS = 200
NULL_LCG_MODULUS = 2147483648
NULL_LCG_MULTIPLIER = 1103515245
NULL_LCG_INCREMENT = 12345
NULL_SEED = 20260919
NULL_MASS_TOTAL = 16

TAG_BITS = 2
LOCAL_K_FIELD = 3
SHARED_INDEX_FIELD = 5
MONO_COUNT_FIELD = 5


def fr(x):
    return str(Fraction(x))


def bit(p, j):
    return (p >> j) & 1


# ---------------------------------------------------------------------------
# Affine closure
# ---------------------------------------------------------------------------
def affine_closure(points):
    """Affine span by set doubling: no pivoting, no elimination."""
    pts = sorted(points)
    if not pts:
        return frozenset()
    base = pts[0]
    span = set([0])
    for p in pts[1:]:
        v = p ^ base
        if v in span:
            continue
        span |= set(x ^ v for x in span)
    return frozenset(x ^ base for x in span)


def affine_dim(points):
    if not points:
        return -1
    return len(affine_closure(points)).bit_length() - 1


def _all_cosets():
    """Every GF(2) coset of the cube: a coset of dimension d is the affine
    closure of d+1 affinely independent points, so closing every subset of
    size at most n+1 finds them all."""
    found = set()
    for r in range(1, N + 2):
        for combo in itertools.combinations(POINTS, r):
            found.add(affine_closure(combo))
    return tuple(sorted(found, key=lambda c: (len(c), sorted(c))))


ALL_COSETS = _all_cosets()
ALL_COSET_MASKS = tuple((sum(1 << p for p in c), len(c).bit_length() - 1)
                        for c in ALL_COSETS)


def closed_subsets_of(support):
    m = sum(1 << p for p in support)
    return [c for c in ALL_COSETS if (sum(1 << p for p in c) & ~m) == 0]


def to_mask(points):
    m = 0
    for p in points:
        m |= 1 << p
    return m


def union_or_stratification(support):
    """Recursive exact cover branching on the lowest still-uncovered point."""
    d = affine_dim(support)
    if d < 1:
        return False
    k = d - 1
    m = to_mask(support)
    inside = [cm for cm, cd in ALL_COSET_MASKS
              if cd <= k and (cm & ~m) == 0]
    pieces = [a for a in inside
              if not any(a != b and (a & ~b) == 0 for b in inside)]

    def cover(remaining, depth):
        if remaining == 0:
            return True
        if depth == 0:
            return False
        low = remaining & -remaining
        for pc in pieces:
            if pc & low:
                if cover(remaining & ~pc, depth - 1):
                    return True
        return False

    return cover(m, UNION_RANK_CAP)


def maximal_coset_dims(support):
    m = sum(1 << p for p in support)
    masks = [(cm, cd) for cm, cd in ALL_COSET_MASKS if (cm & ~m) == 0]
    dims = set()
    for cm, cd in masks:
        if not any(cm != c2 and (cm & ~c2) == 0 for c2, _ in masks):
            dims.add(cd)
    return sorted(dims)


# ---------------------------------------------------------------------------
# Graph quantities by union-find
# ---------------------------------------------------------------------------
def graph_stats(support):
    pts = sorted(support)
    parent = dict((p, p) for p in pts)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    edges = 0
    tree_edges = 0
    degrees = dict((p, 0) for p in pts)
    for a in pts:
        for b in pts:
            if a >= b:
                continue
            if bin(a ^ b).count("1") != 1:
                continue
            edges += 1
            degrees[a] += 1
            degrees[b] += 1
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
                tree_edges += 1
    components = len(set(find(p) for p in pts))
    return {
        "edges": edges,
        "components": components,
        "cycle_rank": edges - tree_edges,
        "connected": components == 1,
        "degree_sequence": sorted(degrees[p] for p in pts),
    }


# ---------------------------------------------------------------------------
# Symmetry by direct permutation scan
# ---------------------------------------------------------------------------
PERMS = tuple(itertools.permutations(range(N)))
IDENTITY = tuple(range(N))


def perm_apply(sigma, p):
    q = 0
    for j in range(N):
        if bit(p, j):
            q |= 1 << sigma[j]
    return q


def invariant_permutations(support, masses=None):
    sf = frozenset(support)
    out = []
    for s in PERMS:
        if frozenset(perm_apply(s, p) for p in support) != sf:
            continue
        if masses is not None and any(
                masses[p] != masses[perm_apply(s, p)] for p in support):
            continue
        out.append(s)
    return out


def orbits_of_permset(perms):
    parent = dict((p, p) for p in POINTS)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for s in perms:
        for p in POINTS:
            a, b = find(p), find(perm_apply(s, p))
            if a != b:
                parent[a] = b
    groups = {}
    for p in POINTS:
        groups.setdefault(find(p), []).append(p)
    return sorted(sorted(v) for v in groups.values())


def subgroups_by_closure():
    """Every subgroup of the coordinate-permutation group, found by closing
    permutation subsets under composition."""
    def compose(a, b):
        return tuple(a[b[j]] for j in range(N))

    subs = set()
    for r in (0, 1, 2):
        for combo in itertools.combinations(PERMS, r):
            g = set([IDENTITY]) | set(combo)
            while True:
                new = set(compose(a, b) for a in g for b in g) - g
                if not new:
                    break
                g |= new
            subs.add(frozenset(g))
    return sorted(subs, key=lambda H: (len(H), sorted(H)))


SUBGROUPS = subgroups_by_closure()
ORBIT_COUNTS = tuple(len(orbits_of_permset(H)) for H in SUBGROUPS)
SYM_N_INDEX = len(SUBGROUPS) - 1


# ---------------------------------------------------------------------------
# Blocks
# ---------------------------------------------------------------------------
def block_value(p, b):
    return tuple(bit(p, j) for j in BLOCKS[b])


def block_supports(support):
    return (sorted(set(block_value(p, 0) for p in support)),
            sorted(set(block_value(p, 1) for p in support)))


def is_block_product(support):
    v1, v2 = block_supports(support)
    for a in v1:
        for b in v2:
            p = (a[0] | (a[1] << 1)) | ((b[0] | (b[1] << 1)) << 2)
            if p not in set(support):
                return False
    return True


def block_affine_dim(values):
    return affine_dim([v[0] + 2 * v[1] for v in values])


# ---------------------------------------------------------------------------
# Truth-table enumeration: the model classes as explicit function sets
# ---------------------------------------------------------------------------
def anf_terms_direct(table):
    """Monomial count by the direct subset-summation formula, not a butterfly."""
    count = 0
    for S in POINTS:
        v = 0
        T = S
        while True:
            v ^= table[T]
            if T == 0:
                break
            T = (T - 1) & S
        if v:
            count += 1
    return count


TABLES = tuple(range(1 << (1 << N)))


def table_bits(ff):
    return [(ff >> p) & 1 for p in POINTS]


def is_local(ff, k):
    t = table_bits(ff)
    for J in itertools.combinations(range(N), k):
        ok = True
        seen = {}
        for p in POINTS:
            key = tuple(bit(p, j) for j in J)
            if key in seen and seen[key] != t[p]:
                ok = False
                break
            seen[key] = t[p]
        if ok:
            return True
    return False


def is_invariant_under(ff, perms):
    t = table_bits(ff)
    for s in perms:
        for p in POINTS:
            if t[p] != t[perm_apply(s, p)]:
                return False
    return True


def is_modular(ff):
    """The 4x4 block value matrix has at most 2 distinct rows and at most 2
    distinct columns."""
    t = table_bits(ff)
    rows = set()
    cols = set()
    for a in range(4):
        rows.add(tuple(t[(a) | (b << 2)] for b in range(4)))
    for b in range(4):
        cols.add(tuple(t[(a) | (b << 2)] for a in range(4)))
    return len(rows) <= 2 and len(cols) <= 2


MODULAR_SET = frozenset(ff for ff in TABLES if is_modular(ff))
ANF_COUNT = tuple(anf_terms_direct(table_bits(ff)) for ff in TABLES)


def _local_sets():
    out = []
    for k in range(N + 1):
        acc = set()
        for J in itertools.combinations(range(N), k):
            for tbl in range(1 << (1 << k)):
                ff = 0
                for p in POINTS:
                    idx = 0
                    for i, j in enumerate(J):
                        idx |= bit(p, j) << i
                    if (tbl >> idx) & 1:
                        ff |= 1 << p
                acc.add(ff)
        out.append(frozenset(acc))
    return tuple(out)


LOCAL_SETS = _local_sets()


def _invariant_set(perms):
    orbs = orbits_of_permset(perms)
    acc = set()
    for tbl in range(1 << len(orbs)):
        ff = 0
        for i, o in enumerate(orbs):
            if (tbl >> i) & 1:
                for p in o:
                    ff |= 1 << p
        acc.add(ff)
    return frozenset(acc)


SYM_SET = _invariant_set(SUBGROUPS[SYM_N_INDEX])

MONO_SETS = []
for _t in range(0, (1 << N) + 1):
    MONO_SETS.append(frozenset(ff for ff in TABLES if ANF_COUNT[ff] <= _t))
MONO_SETS = tuple(MONO_SETS)


def accuracy(ff, support, masses, target):
    tot = Fraction(0)
    for p in support:
        if ((ff >> p) & 1) == target[p]:
            tot += masses[p]
    return tot


def best_over_set(fset, support, masses, target):
    best = Fraction(0)
    for ff in sorted(fset):
        a = accuracy(ff, support, masses, target)
        if a > best:
            best = a
    return best


# ---------------------------------------------------------------------------
# Costs and the Kraft sum by explicit enumeration
# ---------------------------------------------------------------------------
def cost_local(k):
    return TAG_BITS + LOCAL_K_FIELD + 2 * k + (1 << k)


def cost_shared(idx):
    return TAG_BITS + SHARED_INDEX_FIELD + ORBIT_COUNTS[idx]


def cost_modular():
    return TAG_BITS + 12


def cost_monolithic(t):
    return TAG_BITS + MONO_COUNT_FIELD + 4 * t


def _anf_histogram():
    hist = [0] * ((1 << N) + 1)
    for ff in TABLES:
        hist[ANF_COUNT[ff]] += 1
    return hist


ANF_HISTOGRAM = _anf_histogram()


def kraft_sum(with_count_field=True):
    total = Fraction(0)
    for k in range(N + 1):
        n_desc = len(list(itertools.combinations(range(N), k))) * (1 << (1 << k))
        total += Fraction(n_desc, 1 << cost_local(k))
    for idx in range(len(SUBGROUPS)):
        total += Fraction(1 << ORBIT_COUNTS[idx], 1 << cost_shared(idx))
    total += Fraction(1 << 12, 1 << cost_modular())
    for t in range(0, (1 << N) + 1):
        length = cost_monolithic(t) if with_count_field else TAG_BITS + 4 * t
        total += Fraction(ANF_HISTOGRAM[t], 1 << length)
    return total


def description_count():
    total = 0
    for k in range(N + 1):
        total += len(list(itertools.combinations(range(N), k))) * (1 << (1 << k))
    for idx in range(len(SUBGROUPS)):
        total += 1 << ORBIT_COUNTS[idx]
    total += 1 << 12
    total += 1 << (1 << N)
    return total


# ---------------------------------------------------------------------------
# Sources, re-declared here from the registered descriptions
# ---------------------------------------------------------------------------
def uniform(points):
    return dict((p, Fraction(1, len(points))) for p in points)


def target_table(support, fn):
    return dict((p, 1 if fn(p) else 0) for p in support)


def circuit_set(tup):
    i, j, k, l, m = tup
    return tuple(p for p in POINTS
                 if ((bit(p, i) & bit(p, j)) ^ bit(p, k)
                     ^ (bit(p, l) | bit(p, m))) == 1)


def geometric_cycle_ranks():
    out = set()
    for d in range(N + 1):
        coset = [p for p in POINTS if p < (1 << d)]
        out.add(graph_stats(coset)["cycle_rank"])
    return sorted(out)


GEOMETRIC_CYCLE_RANKS = geometric_cycle_ranks()


def select_circuit():
    for tup in itertools.product(range(N), repeat=5):
        S = circuit_set(tup)
        if len(S) < 2 or affine_dim(S) != N:
            continue
        if len(invariant_permutations(S)) != 1:
            continue
        g = graph_stats(S)
        if g["cycle_rank"] in GEOMETRIC_CYCLE_RANKS or g["connected"]:
            continue
        return tup, S
    raise RuntimeError("no circuit found")


ALG_CIRCUIT, ALG_SUPPORT = select_circuit()

COMPOSITE_SUPPORT = (0, 3, 4, 7, 8, 11, 12, 15)


def roster():
    r = {}
    r["S_SUBSPACE"] = ((0, 1, 2, 3), uniform((0, 1, 2, 3)),
                       lambda p: bit(p, 0))
    r["S_STRATIFIED"] = ((0, 1, 2, 3, 12, 13),
                         {0: Fraction(1, 4), 1: Fraction(1, 8),
                          2: Fraction(1, 8), 3: Fraction(1, 8),
                          12: Fraction(1, 4), 13: Fraction(1, 8)},
                         lambda p: bit(p, 2))
    r["S_BLOCKPROD"] = ((0, 3, 12, 15), uniform((0, 3, 12, 15)),
                        lambda p: bit(p, 0) ^ bit(p, 2))
    r["S_ORBIT"] = ((0, 1, 2, 4, 8),
                    {0: Fraction(1, 2), 1: Fraction(1, 8), 2: Fraction(1, 8),
                     4: Fraction(1, 8), 8: Fraction(1, 8)},
                    lambda p: 0 if p == 0 else 1)
    r["S_CYCLE"] = ((1, 2, 3, 4, 5, 6),
                    {1: Fraction(1, 2), 2: Fraction(1, 4), 3: Fraction(1, 8),
                     4: Fraction(1, 16), 5: Fraction(1, 32),
                     6: Fraction(1, 32)},
                    lambda p: bit(p, 0))
    r["S_ALGORITHMIC"] = (ALG_SUPPORT, uniform(ALG_SUPPORT),
                          lambda p: bit(p, 3))
    r["S_LOWDIM_USELESS"] = ((0, 3), {0: Fraction(1, 2), 3: Fraction(1, 2)},
                             lambda p: 0)
    r["S_NONMANIFOLD_LEARNABLE"] = ((0, 1, 2, 3, 4),
                                    {0: Fraction(1, 4), 1: Fraction(1, 4),
                                     2: Fraction(1, 4), 3: Fraction(1, 8),
                                     4: Fraction(1, 8)},
                                    lambda p: bit(p, 0) ^ bit(p, 2))
    return r


FULL = uniform(POINTS)


def dworlds():
    return {
        "D_LOCAL_POS": ((0, 1, 2, 3, 4),
                        {0: Fraction(1, 4), 1: Fraction(1, 4),
                         2: Fraction(1, 4), 3: Fraction(1, 8),
                         4: Fraction(1, 8)},
                        lambda p: bit(p, 0) ^ bit(p, 2)),
        "D_LOCAL_NEG": (POINTS, dict(FULL),
                        lambda p: bit(p, 0) & bit(p, 1) & bit(p, 2)
                        & bit(p, 3)),
        "D_SYM_POS": (POINTS, dict(FULL),
                      lambda p: 1 if bin(p).count("1") >= 3 else 0),
        "D_SYM_NEG": (POINTS, dict(FULL), lambda p: bit(p, 0)),
        "D_COMP_POS": (POINTS, dict(FULL),
                       lambda p: (bit(p, 0) & bit(p, 1))
                       ^ (bit(p, 2) | bit(p, 3))),
        "D_COMP_NEG": (POINTS, dict(FULL),
                       lambda p: 1 if bin(p).count("1") >= 3 else 0),
        "D_BLOCKLEAK": (POINTS, dict(FULL),
                        lambda p: bit(p, 0) ^ (bit(p, 1) & bit(p, 2))),
    }


# ---------------------------------------------------------------------------
# Information and intervention
# ---------------------------------------------------------------------------
def block1_information_is_zero(support, masses, target):
    """I(block-1 value ; Y) = 0 iff every conditional P(Y=1 | block1 = a)
    equals the unconditional P(Y=1)."""
    py = sum(masses[p] for p in support if target[p] == 1)
    cond = {}
    for p in support:
        a = block_value(p, 0)
        cell = cond.setdefault(a, [Fraction(0), Fraction(0)])
        cell[0] += masses[p]
        if target[p] == 1:
            cell[1] += masses[p]
    for a in cond:
        tot, ones = cond[a]
        if tot == 0:
            continue
        if ones / tot != py:
            return False
    return True


def is_product_measure(support, masses):
    p1 = {}
    p2 = {}
    for p in support:
        p1[block_value(p, 0)] = p1.get(block_value(p, 0),
                                       Fraction(0)) + masses[p]
        p2[block_value(p, 1)] = p2.get(block_value(p, 1),
                                       Fraction(0)) + masses[p]
    for p in support:
        if masses[p] != p1[block_value(p, 0)] * p2[block_value(p, 1)]:
            return False
    v1, v2 = block_supports(support)
    return len(support) == len(v1) * len(v2)


def interventional_effect_block1(support, masses, target):
    if not is_product_measure(support, masses):
        return None
    p2 = {}
    for p in support:
        p2[block_value(p, 1)] = p2.get(block_value(p, 1),
                                       Fraction(0)) + masses[p]
    v1, v2 = block_supports(support)
    vals = []
    for a in v1:
        tot = Fraction(0)
        for b in v2:
            p = (a[0] | (a[1] << 1)) | ((b[0] | (b[1] << 1)) << 2)
            tot += p2[b] * target[p]
        vals.append(tot)
    return max(vals) - min(vals)


def best_reading_block(support, masses, target, b):
    cells = {}
    for p in support:
        cell = cells.setdefault(block_value(p, b), [Fraction(0), Fraction(0)])
        cell[target[p]] += masses[p]
    tot = Fraction(0)
    for cell in cells.values():
        tot += max(cell)
    return tot


def coordinate_carries_target(support, target, j):
    ys = set(target[p] for p in support)
    if len(ys) < 2:
        return False
    for v in (0, 1):
        vals = set(target[p] for p in support if bit(p, j) == v)
        if len(vals) > 1:
            return False
    return set(bit(p, j) for p in support) == set([0, 1])


# ---------------------------------------------------------------------------
# Null replay
# ---------------------------------------------------------------------------
class Lcg(object):
    def __init__(self, seed):
        self.state = seed % NULL_LCG_MODULUS

    def next(self, bound):
        self.state = (NULL_LCG_MULTIPLIER * self.state
                      + NULL_LCG_INCREMENT) % NULL_LCG_MODULUS
        return (self.state >> 8) % bound


def row3_detector(support, masses, target):
    if not is_block_product(support):
        return False
    if not is_product_measure(support, masses):
        return False
    v1, v2 = block_supports(support)
    if block_affine_dim(v1) != 1 or block_affine_dim(v2) != 2:
        return False
    if not block1_information_is_zero(support, masses, target):
        return False
    eff = interventional_effect_block1(support, masses, target)
    if eff is None or eff != 0:
        return False
    return any(coordinate_carries_target(support, target, j)
               for j in BLOCKS[1])


def null_replay():
    rng = Lcg(NULL_SEED)
    fired = 0
    mags = []
    for _trial in range(NULL_TRIALS):
        m1 = 1 + rng.next(15)
        m2 = 1 + rng.next(15)
        v1 = [(a, b) for a in (0, 1) for b in (0, 1)
              if (m1 >> (a + 2 * b)) & 1]
        v2 = [(a, b) for a in (0, 1) for b in (0, 1)
              if (m2 >> (a + 2 * b)) & 1]
        w1 = [1] * len(v1)
        for _ in range(NULL_MASS_TOTAL - len(v1)):
            w1[rng.next(len(v1))] += 1
        w2 = [1] * len(v2)
        for _ in range(NULL_MASS_TOTAL - len(v2)):
            w2[rng.next(len(v2))] += 1
        p1 = dict((v1[i], Fraction(w1[i], NULL_MASS_TOTAL))
                  for i in range(len(v1)))
        p2 = dict((v2[i], Fraction(w2[i], NULL_MASS_TOTAL))
                  for i in range(len(v2)))
        support = tuple(sorted(p for p in POINTS
                               if block_value(p, 0) in p1
                               and block_value(p, 1) in p2))
        masses = dict((p, p1[block_value(p, 0)] * p2[block_value(p, 1)])
                      for p in support)
        target = {}
        for p in support:
            target[p] = rng.next(2)
        mags.append(best_reading_block(support, masses, target, 1)
                    - best_reading_block(support, masses, target, 0))
        if row3_detector(support, masses, target):
            fired += 1
    return fired, max(mags)


# ---------------------------------------------------------------------------
# Census
# ---------------------------------------------------------------------------
def union_census():
    total = 0
    members = 0
    non_member_sizes = {}
    stab_orders = set()
    for m in range(1, 1 << (1 << N)):
        pts = tuple(p for p in POINTS if (m >> p) & 1)
        if len(pts) < 2:
            continue
        if affine_dim(pts) < 1:
            continue
        total += 1
        if union_or_stratification(pts):
            members += 1
        else:
            non_member_sizes[len(pts)] = non_member_sizes.get(len(pts), 0) + 1
            stab_orders.add(len(invariant_permutations(pts)))
    return {
        "supports_with_dimension_at_least_1": total,
        "members": members,
        "non_members": total - members,
        "non_member_size_histogram": dict(
            (str(k), v) for k, v in sorted(non_member_sizes.items())),
        "non_member_stabilizer_orders": sorted(stab_orders),
    }


def sparse_certificate():
    worst = -1
    trivial = 0
    count = 0
    for m1 in range(1, 16):
        v1 = [(a, b) for a in (0, 1) for b in (0, 1)
              if (m1 >> (a + 2 * b)) & 1]
        if len(v1) > BLOCK_SUPPORT_CAP:
            continue
        for m2 in range(1, 16):
            v2 = [(a, b) for a in (0, 1) for b in (0, 1)
                  if (m2 >> (a + 2 * b)) & 1]
            if len(v2) > BLOCK_SUPPORT_CAP:
                continue
            pts = tuple(sorted(
                (a[0] | (a[1] << 1)) | ((b[0] | (b[1] << 1)) << 2)
                for a in v1 for b in v2))
            count += 1
            worst = max(worst, affine_dim(pts))
            if len(invariant_permutations(pts)) == 1:
                trivial += 1
    return {"supports_checked": count, "maximum_affine_dimension": worst,
            "supports_with_trivial_stabilizer": trivial}


# ---------------------------------------------------------------------------
# Oracle report
# ---------------------------------------------------------------------------
def classify(support, masses):
    d = affine_dim(support)
    v1, v2 = block_supports(support)
    prod = is_block_product(support)
    sparse = (prod and len(v1) <= BLOCK_SUPPORT_CAP
              and len(v2) <= BLOCK_SUPPORT_CAP)
    inv = [s for s in invariant_permutations(support, masses)
           if s != IDENTITY]
    g = graph_stats(support)
    nongeo = (d == N and not inv
              and g["cycle_rank"] not in GEOMETRIC_CYCLE_RANKS)
    return {
        "affine_dimension": d,
        "support_size": len(support),
        "maximal_coset_dimensions": maximal_coset_dims(support),
        "block_support_sizes": [len(v1), len(v2)],
        "is_block_product": prod,
        "graph": g,
        "nontrivial_invariant_permutations": len(inv),
        "membership": {
            "LOW_INTRINSIC_DIMENSION": d < N,
            "UNION_OR_STRATIFICATION": union_or_stratification(support),
            "SPARSE_COMPOSITIONAL": sparse,
            "SYMMETRY_ORBIT": len(inv) > 0,
            "GRAPH_TOPOLOGICAL": g["connected"],
            "NON_GEOMETRIC_ALGORITHMIC": nongeo,
        },
    }


def best_monolithic(support, masses, target, budget):
    tmax = (budget - TAG_BITS - MONO_COUNT_FIELD) // 4
    if tmax < 0:
        return Fraction(0)
    return best_over_set(MONO_SETS[min(tmax, 1 << N)], support, masses, target)


def oracle():
    out = {"schema": "GMI_833_AE6_INDEPENDENT_ORACLE_V1", "route": "B"}
    out["geometric_cycle_ranks"] = GEOMETRIC_CYCLE_RANKS
    out["subgroup_lattice_size"] = len(SUBGROUPS)
    out["orbit_count_SymN"] = ORBIT_COUNTS[SYM_N_INDEX]
    out["algorithmic_circuit"] = {"chosen_tuple": list(ALG_CIRCUIT),
                                  "accepting_set": list(ALG_SUPPORT)}
    r = roster()
    out["structure_classes"] = dict(
        (name, classify(r[name][0], r[name][1])) for name in sorted(r))
    out["union_predicate_census"] = union_census()
    out["sparse_containment_certificate"] = sparse_certificate()

    nm_sup, nm_mass, nm_fn = r["S_NONMANIFOLD_LEARNABLE"]
    nm_t = target_table(nm_sup, nm_fn)
    out["row2"] = {
        "degree_sequence": graph_stats(nm_sup)["degree_sequence"],
        "maximal_coset_dimensions": maximal_coset_dims(nm_sup),
        "M_local_2_accuracy": fr(best_over_set(LOCAL_SETS[2], nm_sup, nm_mass, nm_t)),
    }

    lit_sup, lit_mass, lit_fn = r["S_LOWDIM_USELESS"]
    lit_t = target_table(lit_sup, lit_fn)
    comp_sup = COMPOSITE_SUPPORT
    comp_mass = uniform(comp_sup)
    comp_t = target_table(comp_sup, lambda p: bit(p, 2))
    rel_t = target_table(comp_sup, lambda p: bit(p, 0))
    cv1, cv2 = block_supports(comp_sup)
    lit_cases = 0
    lit_sat = 0
    for pts in itertools.combinations(POINTS, 2):
        if affine_dim(pts) != 1:
            continue
        mass = uniform(pts)
        for ymask in range(4):
            tt = dict((pts[i], (ymask >> i) & 1) for i in range(2))
            lit_cases += 1
            ones = sum(mass[p] for p in pts if tt[p] == 1)
            if (ones == 0 or ones == 1) and any(
                    coordinate_carries_target(pts, tt, j) for j in range(N)):
                lit_sat += 1
    out["row3"] = {
        "literal_affine_dimension": affine_dim(lit_sup),
        "literal_information_is_zero":
            block1_information_is_zero(lit_sup, lit_mass, lit_t),
        "literal_interventional_effect":
            fr(interventional_effect_block1(lit_sup, lit_mass, lit_t)),
        "literal_coordinates_carrying_the_target": [
            j for j in range(N) if coordinate_carries_target(lit_sup, lit_t, j)],
        "dimension_1_cases_checked": lit_cases,
        "dimension_1_cases_satisfying_the_full_conjunction": lit_sat,
        "composite_affine_dimension": affine_dim(comp_sup),
        "composite_block1_factor_dimension": block_affine_dim(cv1),
        "composite_block2_factor_dimension": block_affine_dim(cv2),
        "composite_information_is_zero":
            block1_information_is_zero(comp_sup, comp_mass, comp_t),
        "composite_interventional_effect":
            fr(interventional_effect_block1(comp_sup, comp_mass, comp_t)),
        "composite_accuracy_block1":
            fr(best_reading_block(comp_sup, comp_mass, comp_t, 0)),
        "composite_accuracy_block2":
            fr(best_reading_block(comp_sup, comp_mass, comp_t, 1)),
        "relaxed_information_is_zero":
            block1_information_is_zero(comp_sup, comp_mass, rel_t),
        "relaxed_interventional_effect":
            fr(interventional_effect_block1(comp_sup, comp_mass, rel_t)),
    }

    d = dworlds()
    def tt(name):
        sup, mass, fn = d[name]
        return sup, mass, target_table(sup, fn)

    loc_budget = cost_local(2)
    sup, mass, t = tt("D_LOCAL_POS")
    loc_pos_named = best_over_set(LOCAL_SETS[2], sup, mass, t)
    loc_pos_comp = best_monolithic(sup, mass, t, loc_budget)
    sup, mass, t = tt("D_LOCAL_NEG")
    loc_neg_named = best_over_set(LOCAL_SETS[2], sup, mass, t)
    loc_neg_comp = best_monolithic(sup, mass, t, loc_budget)
    loc_neg_relaxed = best_over_set(LOCAL_SETS[4], sup, mass, t)
    out["derivation_locality"] = {
        "integer_cost": loc_budget,
        "positive_named": fr(loc_pos_named),
        "positive_comparator": fr(loc_pos_comp),
        "failure_named": fr(loc_neg_named),
        "failure_comparator": fr(loc_neg_comp),
        "failure_drop": fr(loc_neg_comp - loc_neg_named),
        "relaxed_class_accuracy": fr(loc_neg_relaxed),
    }

    sym_budget = cost_shared(SYM_N_INDEX)
    symperms = SUBGROUPS[SYM_N_INDEX]
    sup, mass, t = tt("D_SYM_POS")
    sym_pos_named = best_over_set(SYM_SET, sup, mass, t)
    sym_pos_comp = best_monolithic(sup, mass, t, sym_budget)
    sup, mass, t = tt("D_SYM_NEG")
    sym_neg_named = best_over_set(SYM_SET, sup, mass, t)
    sym_neg_comp = best_monolithic(sup, mass, t, sym_budget)
    out["derivation_symmetry"] = {
        "integer_cost": sym_budget,
        "unshared_cost": cost_shared(0),
        "cost_reduction_bits": cost_shared(0) - sym_budget,
        "orbit_count_reduction": ORBIT_COUNTS[0] - ORBIT_COUNTS[SYM_N_INDEX],
        "positive_named": fr(sym_pos_named),
        "positive_comparator": fr(sym_pos_comp),
        "failure_named": fr(sym_neg_named),
        "failure_comparator": fr(sym_neg_comp),
        "failure_drop": fr(sym_neg_comp - sym_neg_named),
    }

    mod_budget = cost_modular()
    sup, mass, t = tt("D_COMP_POS")
    comp_pos_named = best_over_set(MODULAR_SET, sup, mass, t)
    comp_pos_comp = best_monolithic(sup, mass, t, mod_budget)
    sup, mass, t = tt("D_COMP_NEG")
    comp_neg_named = best_over_set(MODULAR_SET, sup, mass, t)
    comp_neg_mono = best_monolithic(sup, mass, t, mod_budget)
    comp_neg_sym = best_over_set(SYM_SET, sup, mass, t)
    tmax = (mod_budget - TAG_BITS - MONO_COUNT_FIELD) // 4
    out["derivation_compositionality"] = {
        "integer_cost": mod_budget,
        "positive_named": fr(comp_pos_named),
        "positive_comparator": fr(comp_pos_comp),
        "failure_named": fr(comp_neg_named),
        "failure_monolithic_comparator": fr(comp_neg_mono),
        "failure_comparator": fr(comp_neg_sym),
        "failure_drop": fr(comp_neg_sym - comp_neg_named),
        "monolithic_functions_at_that_budget":
            sum(1 for ff in TABLES if ANF_COUNT[ff] <= tmax),
        "all_contained_in_M_modular":
            all(ff in MODULAR_SET for ff in TABLES if ANF_COUNT[ff] <= tmax),
        "distinct_modular_functions": len(MODULAR_SET),
    }

    sup, mass, t = tt("D_BLOCKLEAK")
    out["hostiles"] = {
        "H_DIM_INFLATE_true_dimension": affine_dim(r["S_ALGORITHMIC"][0]),
        "H_ORBIT_MERGE_support_only_invariants":
            len([s for s in invariant_permutations(r["S_CYCLE"][0])
                 if s != IDENTITY]),
        "H_ORBIT_MERGE_true_invariants":
            len([s for s in invariant_permutations(r["S_CYCLE"][0],
                                                   r["S_CYCLE"][1])
                 if s != IDENTITY]),
        "H_BLOCK_LEAK_true_modular": fr(
            best_over_set(MODULAR_SET, sup, mass, t)),
        "H_BUDGET_INFLATE_true": fr(comp_pos_comp),
        "H_BUDGET_INFLATE_inflated": fr(best_monolithic(
            *tt("D_COMP_POS"), budget=cost_monolithic(4))),
        "H_CYCLE_RANK_true": graph_stats(r["S_CYCLE"][0])["cycle_rank"],
        "H_CYCLE_RANK_perturbed": graph_stats(
            tuple(sorted(set(r["S_CYCLE"][0]) - set([6]) | set([0]))))[
                "cycle_rank"],
    }

    fired, largest = null_replay()
    out["null"] = {"trials": NULL_TRIALS, "random_worlds_flagged": fired,
                   "largest_null_magnitude": fr(largest),
                   "planted_positive_flagged": row3_detector(
                       comp_sup, comp_mass, comp_t),
                   "planted_positive_magnitude": fr(
                       best_reading_block(comp_sup, comp_mass, comp_t, 1)
                       - best_reading_block(comp_sup, comp_mass, comp_t, 0))}

    out["description_code"] = {
        "costs": {"M_local": dict(("k=%d" % k, cost_local(k))
                                  for k in range(N + 1)),
                  "M_shared[SymN]": cost_shared(SYM_N_INDEX),
                  "M_shared[trivial]": cost_shared(0),
                  "M_modular": cost_modular(),
                  "M_monolithic": dict(("t=%d" % t, cost_monolithic(t))
                                       for t in range(0, 6))},
        "kraft_sum": fr(kraft_sum(True)),
        "relaxed_code_kraft_sum": fr(kraft_sum(False)),
        "registered_description_count": description_count(),
    }
    return out


def main():
    sys.stdout.write(json.dumps(oracle(), sort_keys=True, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
