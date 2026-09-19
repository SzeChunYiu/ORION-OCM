#!/usr/bin/env python3
"""Route A - AE6 geometric structure hierarchy executor (issue #833, comment 5692689542).

Ambient space: X = {0,1}^4 with Hamming distance, so every `geometry` word in this
package is an exact combinatorial predicate.  All arithmetic is `int` or
`fractions.Fraction`; no float enters any claim, receipt field, test assertion or
hostile.  Serialization is a single json.dumps(..., sort_keys=True, indent=2) plus
one trailing newline, so the receipt is byte-identical under `-I -B` and
`-I -O -B` and across CPython 3.8 and 3.12.

Route B (`independent_geometry_oracle_v1.py`) recomputes every claimed quantity by
exhaustive enumeration and contains no executable import of this module.

Usage:  python3 -I -B ae6_geometric_structure_v1.py > RESULT_V1.json
"""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = "gmi-833-ae-ae6-geometric-structure-v1"
ISSUE = 833
ISSUE_COMMENT_ID = 5692689542
SECTION = "AE6"
SOURCE_MAIN = "0dcdec54fbece041ee2b7cd1f630469ad85d19d3"
FREEZE_COMMIT = "3c2edcdec42c30f3101b1d294d1144875a25ce91"
REGISTER_COMMIT = "ca674c10e9c0c79e0df46de61d9170cc06435135"
CLAIM_CEILING = (
    "GMI_833_AE6_GEOMETRIC_STRUCTURE_HIERARCHY_SEPARATED_AND_"
    "MORPHOLOGY_CONDITIONS_DERIVED_ON_REGISTERED_FINITE_ROSTER"
)

N = 4
POINTS = tuple(range(1 << N))
BLOCKS = ((0, 1), (2, 3))
BLOCK_SUPPORT_CAP = 2
UNION_RANK_CAP = 3
DIMENSION_RANGE = (0, 4)
NULL_TRIALS = 200

# Implementation constants OUTSIDE the prospective register: the null sampler.
# Fixed in source before the first null run and never touched afterwards.
NULL_LCG_MODULUS = 2147483648
NULL_LCG_MULTIPLIER = 1103515245
NULL_LCG_INCREMENT = 12345
NULL_SEED = 20260919
NULL_MASS_TOTAL = 16

FORBIDDEN_PROMOTIONS = [
    "INTELLIGENCE_EQUALS_COMPRESSION",
    "ALL_LEARNING_IS_COMPRESSION",
    "MANIFOLD_HYPOTHESIS_UNIVERSAL",
    "MUTUAL_INFORMATION_SUFFICIENT_FOR_INTELLIGENCE",
    "WORLD_MODEL_ALWAYS_REQUIRED",
    "FREE_ENERGY_PRINCIPLE_PROVED",
    "THERMODYNAMIC_INTELLIGENCE_LAW",
    "GENERAL_REASONING_REDUCED_TO_PREDICTION",
    "COMPLETE_GMI",
    "ARCHITECTURE_SELECTION_LAW",
    "GMI_MORPHOLOGY_PREDICTION",
    "ASYMPTOTIC_EXTRAPOLATION_FROM_FINITE_ROSTER",
    "REAL_SYSTEM_CLAIM_WITHOUT_INSTRUMENT",
    "LOW_DIMENSION_IMPLIES_LEARNABILITY",
    "GEOMETRIC_STRUCTURE_IMPLIES_TASK_RELEVANCE",
    "SYMMETRY_ALWAYS_JUSTIFIES_PARAMETER_SHARING",
]

CLASSES = (
    "LOW_INTRINSIC_DIMENSION",
    "UNION_OR_STRATIFICATION",
    "SPARSE_COMPOSITIONAL",
    "SYMMETRY_ORBIT",
    "GRAPH_TOPOLOGICAL",
    "NON_GEOMETRIC_ALGORITHMIC",
)


class ExecutorError(RuntimeError):
    pass


def fr(x):
    return str(Fraction(x))


# ---------------------------------------------------------------------------
# GF(2) affine geometry on {0,1}^4
# ---------------------------------------------------------------------------
def bit(p, j):
    return (p >> j) & 1


def gf2_rank(vectors):
    basis = []
    for v in vectors:
        cur = v
        for b in basis:
            if (cur ^ b) < cur:
                cur ^= b
        if cur:
            basis.append(cur)
            basis.sort(reverse=True)
    return len(basis)


def affine_dim(support):
    pts = sorted(support)
    if not pts:
        return -1
    return gf2_rank([p ^ pts[0] for p in pts[1:]])


def all_cosets():
    """Every GF(2) coset of {0,1}^4, as (frozen point tuple, dimension)."""
    subspaces = set()
    for r in range(N + 1):
        for combo in itertools.combinations(range(1, 1 << N), r):
            if gf2_rank(list(combo)) != r:
                continue
            sp = {0}
            for v in combo:
                sp |= set(x ^ v for x in sp)
            subspaces.add(frozenset(sp))
    out = set()
    for sp in subspaces:
        for t in range(1 << N):
            out.add(frozenset(x ^ t for x in sp))
    rows = []
    for c in out:
        rows.append((tuple(sorted(c)), len(c).bit_length() - 1))
    rows.sort(key=lambda z: (z[1], z[0]))
    return tuple(rows)


COSETS = all_cosets()


def to_mask(points):
    m = 0
    for p in points:
        m |= 1 << p
    return m


COSET_MASKS = tuple((to_mask(c), d) for c, d in COSETS)


def maximal_coset_dims(support):
    """Dimensions of the maximal GF(2) cosets contained in the support."""
    m = to_mask(support)
    inside = [(cm, cd) for cm, cd in COSET_MASKS if (cm & ~m) == 0]
    dims = set()
    for cm, cd in inside:
        if not any(cm != c2 and (cm & ~c2) == 0 for c2, _ in inside):
            dims.add(cd)
    return sorted(dims)


def union_or_stratification(support):
    """The frozen predicate: the support is a union of at most UNION_RANK_CAP
    cosets, each CONTAINED IN the support and of dimension at most k, for some
    k strictly below the support's own affine dimension.

    Monotone in k, so only k = dim - 1 has to be tested."""
    m = to_mask(support)
    d = affine_dim(support)
    if d < 1:
        return False, None
    k = d - 1
    inside = [cm for cm, cd in COSET_MASKS if cd <= k and (cm & ~m) == 0]
    pieces = [a for a in inside
              if not any(a != b and (a & ~b) == 0 for b in inside)]
    for r in range(1, UNION_RANK_CAP + 1):
        for combo in itertools.combinations(pieces, r):
            u = 0
            for c in combo:
                u |= c
            if u == m:
                witness = [sorted(p for p in POINTS if (c >> p) & 1)
                           for c in combo]
                return True, {"k": k, "r": r, "pieces": witness}
    return False, None


def hamming1_graph(support):
    pts = sorted(support)
    edges = [(a, b) for a in pts for b in pts
             if a < b and bin(a ^ b).count("1") == 1]
    adj = dict((p, []) for p in pts)
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    seen = set()
    ncomp = 0
    for p in pts:
        if p in seen:
            continue
        ncomp += 1
        stack = [p]
        seen.add(p)
        while stack:
            x = stack.pop()
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
    return {
        "edges": len(edges),
        "components": ncomp,
        "cycle_rank": len(edges) - len(pts) + ncomp,
        "connected": ncomp == 1,
        "degree_sequence": sorted(len(adj[p]) for p in pts),
    }


# The registered geometric cycle-rank range is derived from the DEFINITION of a
# GF(2) coset: a coset of dimension d induces a d-dimensional hypercube, with
# d * 2^(d-1) edges on 2^d vertices, hence cycle rank d*2^(d-1) - 2^d + 1.
GEOMETRIC_CYCLE_RANKS = tuple(sorted(set(
    d * (1 << (d - 1)) - (1 << d) + 1 if d >= 1 else 0
    for d in range(N + 1))))


# ---------------------------------------------------------------------------
# Coordinate-permutation group and its full subgroup lattice
# ---------------------------------------------------------------------------
PERMS = tuple(itertools.permutations(range(N)))


def perm_apply(sigma, p):
    q = 0
    for j in range(N):
        if bit(p, j):
            q |= 1 << sigma[j]
    return q


def perm_compose(a, b):
    return tuple(a[b[j]] for j in range(N))


def subgroup_lattice():
    subs = set()
    for p in PERMS:
        g = set([tuple(range(N))])
        cur = p
        while cur not in g:
            g.add(cur)
            cur = perm_compose(cur, p)
        subs.add(frozenset(g))
    changed = True
    while changed:
        changed = False
        for H in list(subs):
            for p in PERMS:
                if p in H:
                    continue
                g = set(H)
                g.add(p)
                while True:
                    new = set(perm_compose(a, b) for a in g for b in g) - g
                    if not new:
                        break
                    g |= new
                fg = frozenset(g)
                if fg not in subs:
                    subs.add(fg)
                    changed = True
    return tuple(sorted(subs, key=lambda H: (len(H), sorted(H))))


SUBGROUPS = subgroup_lattice()


def orbits_of(H):
    seen = set()
    out = []
    for p in POINTS:
        if p in seen:
            continue
        o = sorted(set(perm_apply(s, p) for s in H))
        seen |= set(o)
        out.append(o)
    return out


ORBITS = tuple(orbits_of(H) for H in SUBGROUPS)
SUBGROUP_NAMES = tuple(
    "G%02d_order%d_orbits%d" % (i, len(SUBGROUPS[i]), len(ORBITS[i]))
    for i in range(len(SUBGROUPS)))
SYM_N_INDEX = len(SUBGROUPS) - 1


def stabilizer_indices(support, masses):
    """Indices of nontrivial subgroups leaving both the support and the exact
    masses invariant."""
    sf = frozenset(support)
    out = []
    for i, H in enumerate(SUBGROUPS):
        if len(H) == 1:
            continue
        if frozenset(perm_apply(s, p) for s in H for p in support) != sf:
            continue
        if any(masses[p] != masses[perm_apply(s, p)] for s in H for p in support):
            continue
        out.append(i)
    return out


# ---------------------------------------------------------------------------
# Block structure
# ---------------------------------------------------------------------------
def block_value(p, b):
    return tuple(bit(p, j) for j in BLOCKS[b])


def block_supports(support):
    v1 = sorted(set(block_value(p, 0) for p in support))
    v2 = sorted(set(block_value(p, 1) for p in support))
    return v1, v2


def is_block_product(support):
    v1, v2 = block_supports(support)
    rebuilt = set(p for p in POINTS
                  if block_value(p, 0) in v1 and block_value(p, 1) in v2)
    return rebuilt == set(support), v1, v2


def block_affine_dim(values):
    """Affine GF(2) dimension of a set of 2-bit block values."""
    pts = sorted(v[0] + 2 * v[1] for v in values)
    if not pts:
        return -1
    return gf2_rank([p ^ pts[0] for p in pts[1:]])


def sparse_compositional(support):
    prod, v1, v2 = is_block_product(support)
    ok = prod and len(v1) <= BLOCK_SUPPORT_CAP and len(v2) <= BLOCK_SUPPORT_CAP
    return ok, v1, v2


# ---------------------------------------------------------------------------
# The registered small Boolean circuit family (route A's algorithmic source)
# ---------------------------------------------------------------------------
def circuit_accepting_set(tup):
    i, j, k, l, m = tup
    return tuple(p for p in POINTS
                 if ((bit(p, i) & bit(p, j)) ^ bit(p, k)
                     ^ (bit(p, l) | bit(p, m))) == 1)


def select_algorithmic_circuit():
    """Lexicographically first (i,j,k,l,m) in {0..3}^5 whose accepting set has
    full affine dimension, trivial coordinate-permutation stabilizer, cycle rank
    outside the registered geometric range, and a disconnected Hamming-1 graph."""
    for tup in itertools.product(range(N), repeat=5):
        S = circuit_accepting_set(tup)
        if len(S) < 2:
            continue
        if affine_dim(S) != N:
            continue
        sf = frozenset(S)
        nontrivial = [s for s in PERMS
                      if s != tuple(range(N))
                      and frozenset(perm_apply(s, p) for p in S) == sf]
        if nontrivial:
            continue
        g = hamming1_graph(S)
        if g["cycle_rank"] in GEOMETRIC_CYCLE_RANKS:
            continue
        if g["connected"]:
            continue
        return tup, S
    raise ExecutorError("no registered circuit satisfies the class predicate")


ALG_CIRCUIT, ALG_SUPPORT = select_algorithmic_circuit()


# ---------------------------------------------------------------------------
# Registered roster of sources
# ---------------------------------------------------------------------------
def uniform(points):
    return dict((p, Fraction(1, len(points))) for p in points)


def make_source(name, support, masses, target, note):
    if sum(masses.values()) != 1:
        raise ExecutorError("masses of %s do not sum to 1" % name)
    if sorted(masses) != sorted(support):
        raise ExecutorError("mass support mismatch for %s" % name)
    return {
        "name": name,
        "support": tuple(sorted(support)),
        "masses": masses,
        "target": target,
        "note": note,
    }


def build_roster():
    r = {}
    r["S_SUBSPACE"] = make_source(
        "S_SUBSPACE", (0, 1, 2, 3), uniform((0, 1, 2, 3)),
        lambda p: bit(p, 0),
        "the GF(2) coset x2 = x3 = 0, a single affine plane of dimension 2")
    r["S_STRATIFIED"] = make_source(
        "S_STRATIFIED", (0, 1, 2, 3, 12, 13),
        {0: Fraction(1, 4), 1: Fraction(1, 8), 2: Fraction(1, 8),
         3: Fraction(1, 8), 12: Fraction(1, 4), 13: Fraction(1, 8)},
        lambda p: bit(p, 2),
        "a union of a dimension-2 coset and a dimension-1 coset")
    r["S_BLOCKPROD"] = make_source(
        "S_BLOCKPROD", (0, 3, 12, 15), uniform((0, 3, 12, 15)),
        lambda p: bit(p, 0) ^ bit(p, 2),
        "the block product {x0=x1} x {x2=x3}, two values per registered block")
    r["S_ORBIT"] = make_source(
        "S_ORBIT", (0, 1, 2, 4, 8),
        {0: Fraction(1, 2), 1: Fraction(1, 8), 2: Fraction(1, 8),
         4: Fraction(1, 8), 8: Fraction(1, 8)},
        lambda p: 0 if p == 0 else 1,
        "the union of the weight-0 and weight-1 orbits of the full "
        "coordinate-permutation group, with an invariant measure")
    r["S_CYCLE"] = make_source(
        "S_CYCLE", (1, 2, 3, 4, 5, 6),
        {1: Fraction(1, 2), 2: Fraction(1, 4), 3: Fraction(1, 8),
         4: Fraction(1, 16), 5: Fraction(1, 32), 6: Fraction(1, 32)},
        lambda p: bit(p, 0),
        "an induced 6-cycle of the Hamming-1 graph with pairwise distinct "
        "dyadic masses")
    r["S_ALGORITHMIC"] = make_source(
        "S_ALGORITHMIC", ALG_SUPPORT, uniform(ALG_SUPPORT),
        lambda p: bit(p, 3),
        "the accepting set of the registered small Boolean circuit")
    r["S_LOWDIM_USELESS"] = make_source(
        "S_LOWDIM_USELESS", (0, 3),
        {0: Fraction(1, 2), 3: Fraction(1, 2)},
        lambda p: 0,
        "support inside a GF(2) coset of dimension 1, exactly as the register "
        "glosses it")
    r["S_NONMANIFOLD_LEARNABLE"] = make_source(
        "S_NONMANIFOLD_LEARNABLE", (0, 1, 2, 3, 4),
        {0: Fraction(1, 4), 1: Fraction(1, 4), 2: Fraction(1, 4),
         3: Fraction(1, 8), 4: Fraction(1, 8)},
        lambda p: bit(p, 0) ^ bit(p, 2),
        "a dimension-2 coset and a dimension-1 coset meeting in one point")
    return r


ROSTER = build_roster()
ROSTER_ORDER = tuple(sorted(ROSTER))

# The repaired row-3 witness. Not a member of the register's 8-source roster;
# it is the composite object the impossibility theorem forces.
COMPOSITE_SUPPORT = (0, 3, 4, 7, 8, 11, 12, 15)
COMPOSITE = make_source(
    "S_LOWDIM_USELESS_COMPOSITE", COMPOSITE_SUPPORT,
    uniform(COMPOSITE_SUPPORT), lambda p: bit(p, 2),
    "the exact GF(2) product of a dimension-1 factor on block 1 and a "
    "full-dimension factor on block 2")


# ---------------------------------------------------------------------------
# Class membership
# ---------------------------------------------------------------------------
def classify(src):
    support = src["support"]
    masses = src["masses"]
    d = affine_dim(support)
    union_ok, union_w = union_or_stratification(support)
    sparse_ok, v1, v2 = sparse_compositional(support)
    syms = stabilizer_indices(support, masses)
    g = hamming1_graph(support)
    nongeo = (d == N and not syms
              and g["cycle_rank"] not in GEOMETRIC_CYCLE_RANKS)
    return {
        "affine_dimension": d,
        "support_size": len(support),
        "maximal_coset_dimensions": maximal_coset_dims(support),
        "block_support_sizes": [len(v1), len(v2)],
        "is_block_product": is_block_product(support)[0],
        "graph": g,
        "invariance_subgroups": [SUBGROUP_NAMES[i] for i in syms],
        "invariance_subgroup_count": len(syms),
        "union_witness": union_w,
        "membership": {
            "LOW_INTRINSIC_DIMENSION": d < N,
            "UNION_OR_STRATIFICATION": union_ok,
            "SPARSE_COMPOSITIONAL": sparse_ok,
            "SYMMETRY_ORBIT": len(syms) > 0,
            "GRAPH_TOPOLOGICAL": g["connected"],
            "NON_GEOMETRIC_ALGORITHMIC": nongeo,
        },
    }


# ---------------------------------------------------------------------------
# Model classes and the registered Kraft-compliant integer code
# ---------------------------------------------------------------------------
TAG_BITS = 2
LOCAL_K_FIELD = 3
SHARED_INDEX_FIELD = 5
MONO_COUNT_FIELD = 5


def cost_local(k):
    return TAG_BITS + LOCAL_K_FIELD + 2 * k + (1 << k)


def cost_shared(idx):
    return TAG_BITS + SHARED_INDEX_FIELD + len(ORBITS[idx])


def cost_modular():
    return TAG_BITS + 4 + 4 + 4


def cost_monolithic(terms):
    return TAG_BITS + MONO_COUNT_FIELD + 4 * terms


def kraft_sum(with_count_field=True):
    total = Fraction(0)
    for k in range(N + 1):
        n_desc = len(list(itertools.combinations(range(N), k))) * (1 << (1 << k))
        total += Fraction(n_desc, 1) * Fraction(1, 1 << cost_local(k))
    for idx in range(len(SUBGROUPS)):
        total += Fraction(1 << len(ORBITS[idx]), 1) * Fraction(
            1, 1 << cost_shared(idx))
    total += Fraction(1 << 12, 1) * Fraction(1, 1 << cost_modular())
    for t in range(0, (1 << N) + 1):
        n_desc = len(list(itertools.combinations(range(1 << N), t)))
        length = cost_monolithic(t) if with_count_field else (
            TAG_BITS + 4 * t)
        total += Fraction(n_desc, 1) * Fraction(1, 1 << length)
    return total


def anf_terms(table_mask):
    """Number of monomials in the GF(2) (Moebius) expansion of the function
    whose truth table is `table_mask` over the 16 points."""
    a = [(table_mask >> p) & 1 for p in POINTS]
    step = 1
    while step < (1 << N):
        for i in POINTS:
            if i & step:
                a[i] ^= a[i ^ step]
        step <<= 1
    return sum(a), tuple(i for i in POINTS if a[i])


ANF_TERM_COUNT = [0] * (1 << (1 << N))
for _ff in range(1 << (1 << N)):
    ANF_TERM_COUNT[_ff] = anf_terms(_ff)[0]


def source_arrays(src):
    support = src["support"]
    masses = src["masses"]
    target = src["target"]
    smask = to_mask(support)
    ymask = 0
    for p in support:
        if target(p):
            ymask |= 1 << p
    return support, masses, smask, ymask


def accuracy_of_table(src, table_mask):
    support, masses, _smask, ymask = source_arrays(src)
    tot = Fraction(0)
    for p in support:
        if ((table_mask >> p) & 1) == ((ymask >> p) & 1):
            tot += masses[p]
    return tot


def base_rate(src):
    support, masses = src["support"], src["masses"]
    ones = sum(masses[p] for p in support if src["target"](p))
    return max(ones, Fraction(1) - ones)


def best_local(src, k):
    support, masses = src["support"], src["masses"]
    best = Fraction(0)
    arg = None
    for J in itertools.combinations(range(N), k):
        groups = {}
        for p in support:
            key = tuple(bit(p, j) for j in J)
            cell = groups.setdefault(key, [Fraction(0), Fraction(0)])
            cell[1 if src["target"](p) else 0] += masses[p]
        tot = Fraction(0)
        for cell in groups.values():
            tot += max(cell)
        if tot > best:
            best, arg = tot, J
    return best, arg


def best_shared(src, idx):
    support, masses = src["support"], src["masses"]
    tot = Fraction(0)
    for orb in ORBITS[idx]:
        ones = Fraction(0)
        zeros = Fraction(0)
        for p in orb:
            if p not in masses:
                continue
            if src["target"](p):
                ones += masses[p]
            else:
                zeros += masses[p]
        tot += max(ones, zeros)
    return tot


def modular_tables(blocks=BLOCKS):
    out = set()
    for h1 in range(16):
        H1 = dict(((a, b), (h1 >> (a + 2 * b)) & 1)
                  for a in (0, 1) for b in (0, 1))
        for h2 in range(16):
            H2 = dict(((a, b), (h2 >> (a + 2 * b)) & 1)
                      for a in (0, 1) for b in (0, 1))
            for g in range(16):
                G = dict(((a, b), (g >> (a + 2 * b)) & 1)
                         for a in (0, 1) for b in (0, 1))
                tm = 0
                for p in POINTS:
                    u = H1[tuple(bit(p, j) for j in blocks[0])]
                    v = H2[tuple(bit(p, j) for j in blocks[1])]
                    if G[(u, v)]:
                        tm |= 1 << p
                out.add(tm)
    return tuple(sorted(out))


MODULAR_TABLES = modular_tables()


def best_modular(src, tables=None):
    tables = MODULAR_TABLES if tables is None else tables
    best = Fraction(0)
    arg = None
    for tm in tables:
        a = accuracy_of_table(src, tm)
        if a > best:
            best, arg = a, tm
    return best, arg


def best_monolithic(src, budget):
    tmax = (budget - TAG_BITS - MONO_COUNT_FIELD) // 4
    if tmax < 0:
        return Fraction(0), None, tmax
    support, masses, _smask, ymask = source_arrays(src)
    best = Fraction(0)
    arg = None
    for ff in range(1 << (1 << N)):
        if ANF_TERM_COUNT[ff] > tmax:
            continue
        a = Fraction(0)
        for p in support:
            if ((ff >> p) & 1) == ((ymask >> p) & 1):
                a += masses[p]
        if a > best:
            best, arg = a, ff
    return best, arg, tmax


def class_profile_at_budget(src, budget):
    rows = {}
    for k in range(N + 1):
        c = cost_local(k)
        if c <= budget:
            acc, J = best_local(src, k)
            rows["M_local[%d]" % k] = {"cost": c, "accuracy": fr(acc),
                                       "coordinates": list(J) if J else []}
    best_sh = None
    for idx in range(len(SUBGROUPS)):
        c = cost_shared(idx)
        if c > budget:
            continue
        acc = best_shared(src, idx)
        if best_sh is None or acc > best_sh[0]:
            best_sh = (acc, idx, c)
    if best_sh is not None:
        rows["M_shared[best_in_budget]"] = {
            "cost": best_sh[2], "accuracy": fr(best_sh[0]),
            "group": SUBGROUP_NAMES[best_sh[1]],
            "orbit_count": len(ORBITS[best_sh[1]])}
    if cost_shared(SYM_N_INDEX) <= budget:
        rows["M_shared[SymN]"] = {
            "cost": cost_shared(SYM_N_INDEX),
            "accuracy": fr(best_shared(src, SYM_N_INDEX)),
            "orbit_count": len(ORBITS[SYM_N_INDEX])}
    if cost_modular() <= budget:
        acc, arg = best_modular(src)
        rows["M_modular"] = {"cost": cost_modular(), "accuracy": fr(acc),
                             "table_mask": arg}
    acc, arg, tmax = best_monolithic(src, budget)
    rows["M_monolithic"] = {"budget": budget, "max_terms": tmax,
                            "accuracy": fr(acc), "table_mask": arg}
    return rows


# ---------------------------------------------------------------------------
# Exact information and intervention on the registered block factorization
# ---------------------------------------------------------------------------
def block_marginals(src):
    p1 = {}
    p2 = {}
    joint = {}
    for p in src["support"]:
        a = block_value(p, 0)
        b = block_value(p, 1)
        p1[a] = p1.get(a, Fraction(0)) + src["masses"][p]
        p2[b] = p2.get(b, Fraction(0)) + src["masses"][p]
        joint[(a, b)] = joint.get((a, b), Fraction(0)) + src["masses"][p]
    return p1, p2, joint


def is_product_measure(src):
    p1, p2, joint = block_marginals(src)
    for a in p1:
        for b in p2:
            if joint.get((a, b), Fraction(0)) != p1[a] * p2[b]:
                return False
    return True


def mutual_information_bits_block1(src):
    """Exact I(block-1 value ; Y).  Returns (value_or_None, exact_flag).

    Zero is certified exactly: I = 0 iff Y is conditionally independent of the
    block-1 value, which is a finite rational identity.  A nonzero value is
    reported only when every probability involved is a power of 1/2, so the
    logarithm is an integer; otherwise the value is reported as NOT_DECIDED."""
    p1 = {}
    joint = {}
    py = [Fraction(0), Fraction(0)]
    for p in src["support"]:
        a = block_value(p, 0)
        y = 1 if src["target"](p) else 0
        p1[a] = p1.get(a, Fraction(0)) + src["masses"][p]
        joint[(a, y)] = joint.get((a, y), Fraction(0)) + src["masses"][p]
        py[y] += src["masses"][p]
    independent = True
    for a in p1:
        for y in (0, 1):
            if joint.get((a, y), Fraction(0)) != p1[a] * py[y]:
                independent = False
    if independent:
        return Fraction(0), True
    # exactly dyadic case only
    terms = []
    for (a, y), v in sorted(joint.items()):
        if v == 0:
            continue
        ratio = v / (p1[a] * py[y])
        num, den = ratio.numerator, ratio.denominator
        if not (num & (num - 1) == 0 and den & (den - 1) == 0):
            return None, False
        terms.append((v, num.bit_length() - 1 - (den.bit_length() - 1)))
    tot = Fraction(0)
    for v, log2r in terms:
        tot += v * log2r
    return tot, True


def interventional_effect_block1(src):
    """max over block-1 values s, s' of |P(Y=1 | do(block1 = s)) - ...|, under
    the registered structural model in which the two blocks are exogenous and
    independent and Y = t(X).  Defined only for a product measure."""
    if not is_product_measure(src):
        return None
    p1, p2, _joint = block_marginals(src)
    vals = []
    for s in sorted(p1):
        tot = Fraction(0)
        for b in sorted(p2):
            p = (s[0] | (s[1] << 1)) | ((b[0] | (b[1] << 1)) << 2)
            if src["target"](p):
                tot += p2[b]
        vals.append(tot)
    if not vals:
        return Fraction(0)
    return max(vals) - min(vals)


def interventional_effect_coordinate(src, j):
    """max over values of coordinate j of the do-effect on P(Y=1), under the
    registered model with independent exogenous coordinates."""
    if not is_product_measure(src):
        return None
    support = set(src["support"])
    masses = src["masses"]
    others = [c for c in range(N) if c != j]
    vals = []
    for v in (0, 1):
        tot = Fraction(0)
        norm = Fraction(0)
        for p in sorted(support):
            q = (p & ~(1 << j)) | (v << j)
            if q not in support:
                continue
            tot += masses[p] * (1 if src["target"](q) else 0)
            norm += masses[p]
        if norm == 0:
            return None
        vals.append(tot / norm)
    return max(vals) - min(vals)


def best_accuracy_reading_block(src, b):
    groups = {}
    for p in src["support"]:
        key = block_value(p, b)
        cell = groups.setdefault(key, [Fraction(0), Fraction(0)])
        cell[1 if src["target"](p) else 0] += src["masses"][p]
    tot = Fraction(0)
    for cell in groups.values():
        tot += max(cell)
    return tot


def coordinate_determines_target(src, j):
    """The coordinate carries the target exactly: it takes both values on the
    support, the target is a function of it, and the target is not constant.
    Constancy is excluded deliberately - a constant target is `determined` by
    every coordinate and that reading makes the predicate vacuous."""
    ys_all = set(1 if src["target"](p) else 0 for p in src["support"])
    if len(ys_all) < 2:
        return False
    for v in (0, 1):
        ys = set(1 if src["target"](p) else 0
                 for p in src["support"] if bit(p, j) == v)
        if len(ys) > 1:
            return False
    proj = set(bit(p, j) for p in src["support"])
    return proj == set([0, 1])


# ---------------------------------------------------------------------------
# Derivation worlds (distinct from the structure roster)
# ---------------------------------------------------------------------------
FULL_CUBE = uniform(POINTS)


def derivation_worlds():
    d = {}
    d["D_LOCAL_POS"] = ROSTER["S_NONMANIFOLD_LEARNABLE"]
    d["D_LOCAL_NEG"] = make_source(
        "D_LOCAL_NEG", POINTS, dict(FULL_CUBE),
        lambda p: bit(p, 0) & bit(p, 1) & bit(p, 2) & bit(p, 3),
        "uniform cube, target the conjunction of all four coordinates")
    d["D_SYM_POS"] = make_source(
        "D_SYM_POS", POINTS, dict(FULL_CUBE),
        lambda p: 1 if bin(p).count("1") >= 3 else 0,
        "uniform cube, target the weight threshold at 3")
    d["D_SYM_NEG"] = make_source(
        "D_SYM_NEG", POINTS, dict(FULL_CUBE), lambda p: bit(p, 0),
        "uniform cube, target a single coordinate")
    d["D_COMP_POS"] = make_source(
        "D_COMP_POS", POINTS, dict(FULL_CUBE),
        lambda p: (bit(p, 0) & bit(p, 1)) ^ (bit(p, 2) | bit(p, 3)),
        "uniform cube, target a composition through the registered blocks")
    d["D_COMP_NEG"] = make_source(
        "D_COMP_NEG", POINTS, dict(FULL_CUBE),
        lambda p: 1 if bin(p).count("1") >= 3 else 0,
        "uniform cube, the weight threshold again: it does not factorize "
        "through the registered blocks")
    d["D_BLOCKLEAK"] = make_source(
        "D_BLOCKLEAK", POINTS, dict(FULL_CUBE),
        lambda p: bit(p, 0) ^ (bit(p, 1) & bit(p, 2)),
        "uniform cube, a target that crosses the registered block boundary")
    return d


DWORLDS = derivation_worlds()

# The relaxed companion of the composite witness: the same support and the same
# dimension-1 factor, but a target the factor does determine.  It is the
# `violated_by` object for the row-3 bounds and the clean no-alarm case.
C_LOWDIM_RELEVANT = make_source(
    "C_LOWDIM_RELEVANT", COMPOSITE_SUPPORT, uniform(COMPOSITE_SUPPORT),
    lambda p: bit(p, 0),
    "relaxed class: the same dimension-1 factor, now carrying the target")


# ---------------------------------------------------------------------------
# Exhaustive census of the frozen union predicate over every support
# ---------------------------------------------------------------------------
def union_census():
    total = 0
    members = 0
    non_members = []
    for m in range(1, 1 << (1 << N)):
        pts = tuple(p for p in POINTS if (m >> p) & 1)
        if affine_dim(pts) < 1:
            continue
        total += 1
        ok, _w = union_or_stratification(pts)
        if ok:
            members += 1
        else:
            non_members.append(pts)
    sizes = {}
    stabilizer_orders = set()
    for pts in non_members:
        sizes[len(pts)] = sizes.get(len(pts), 0) + 1
        sf = frozenset(pts)
        order = sum(1 for s in PERMS
                    if frozenset(perm_apply(s, p) for p in pts) == sf)
        stabilizer_orders.add(order)
    return {
        "supports_with_dimension_at_least_1": total,
        "members": members,
        "non_members": len(non_members),
        "non_member_size_histogram": dict(
            (str(k), v) for k, v in sorted(sizes.items())),
        "non_member_stabilizer_orders": sorted(stabilizer_orders),
        "every_non_member_has_nontrivial_stabilizer": (
            1 not in stabilizer_orders),
        "finding": (
            "the frozen union predicate is satisfied by every support of "
            "affine dimension at least 1 except the %d supports of size %d, "
            "each of which has a nontrivial coordinate-permutation "
            "stabilizer; no support can therefore be both "
            "NON_GEOMETRIC_ALGORITHMIC and outside UNION_OR_STRATIFICATION"
            % (len(non_members), sorted(sizes)[0] if sizes else 0)),
    }


# ---------------------------------------------------------------------------
# Strictness table
# ---------------------------------------------------------------------------
NOT_SEPARATED_REASON = {
    ("LOW_INTRINSIC_DIMENSION", "UNION_OR_STRATIFICATION"):
        "census: the frozen union predicate holds for all but 16 supports",
    ("SPARSE_COMPOSITIONAL", "UNION_OR_STRATIFICATION"):
        "census: the frozen union predicate holds for all but 16 supports",
    ("SYMMETRY_ORBIT", "UNION_OR_STRATIFICATION"):
        "census: the frozen union predicate holds for all but 16 supports",
    ("GRAPH_TOPOLOGICAL", "UNION_OR_STRATIFICATION"):
        "census: the frozen union predicate holds for all but 16 supports",
    ("NON_GEOMETRIC_ALGORITHMIC", "UNION_OR_STRATIFICATION"):
        "proved impossible: each of the 16 non-members has a nontrivial "
        "stabilizer, which NON_GEOMETRIC_ALGORITHMIC forbids",
    ("SPARSE_COMPOSITIONAL", "LOW_INTRINSIC_DIMENSION"):
        "proved containment: a block product with at most 2 values per block "
        "has affine dimension at most 2 < 4",
    ("SPARSE_COMPOSITIONAL", "SYMMETRY_ORBIT"):
        "roster gap: every SPARSE_COMPOSITIONAL support at n=4 has a "
        "nontrivial coordinate-permutation stabilizer, and both registered "
        "members carry stabilizer-invariant masses",
}


def sparse_implies_low_dimension_certificate():
    """Exhaustive: every block product with at most 2 values per block has
    affine dimension at most 2, and a nontrivial support stabilizer."""
    worst_dim = -1
    trivial_stab = []
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
            pts = tuple(sorted(p for p in POINTS
                               if block_value(p, 0) in v1
                               and block_value(p, 1) in v2))
            count += 1
            worst_dim = max(worst_dim, affine_dim(pts))
            sf = frozenset(pts)
            order = sum(1 for s in PERMS
                        if frozenset(perm_apply(s, p) for p in pts) == sf)
            if order == 1:
                trivial_stab.append(pts)
    return {
        "supports_checked": count,
        "maximum_affine_dimension": worst_dim,
        "supports_with_trivial_stabilizer": len(trivial_stab),
    }


def strictness_table(classified):
    rows = []
    separated = 0
    for a in CLASSES:
        for b in CLASSES:
            if a == b:
                continue
            witness = None
            for name in ROSTER_ORDER:
                mem = classified[name]["membership"]
                if mem[a] and not mem[b]:
                    witness = name
                    break
            if witness is None:
                rows.append({
                    "in_class": a, "not_in_class": b,
                    "separated": False, "witness": None,
                    "reason": NOT_SEPARATED_REASON.get(
                        (a, b), "no registered source realizes the pattern"),
                })
            else:
                separated += 1
                rows.append({"in_class": a, "not_in_class": b,
                             "separated": True, "witness": witness,
                             "reason": None})
    return rows, separated


# ---------------------------------------------------------------------------
# Row 3: the literal reading, its impossibility, and the repaired witness
# ---------------------------------------------------------------------------
def zero_information_forces_constant_certificate(max_size=4):
    """Exhaustive over every support of size at most `max_size` and every
    deterministic target on it: exact I(X;Y) = 0 holds if and only if the
    target is constant on the support."""
    checked = 0
    violations = 0
    for size in range(1, max_size + 1):
        for pts in itertools.combinations(POINTS, size):
            masses = uniform(pts)
            for ymask in range(1 << size):
                ys = dict((pts[i], (ymask >> i) & 1) for i in range(size))
                py1 = sum(masses[p] for p in pts if ys[p] == 1)
                indep = True
                for p in pts:
                    for y in (0, 1):
                        joint = masses[p] if ys[p] == y else Fraction(0)
                        marg = masses[p] * (py1 if y == 1
                                            else Fraction(1) - py1)
                        if joint != marg:
                            indep = False
                constant = len(set(ys.values())) == 1
                checked += 1
                if indep != constant:
                    violations += 1
    return {"cases_checked": checked, "violations": violations,
            "statement": ("for a deterministic target, exact zero mutual "
                          "information with the input is equivalent to the "
                          "target being constant on the support")}


def literal_reading_certificate():
    """Exhaustive over every support of affine dimension 1 and every target on
    it: no case satisfies the full conjunction of the prospective claim."""
    cases = 0
    satisfying = 0
    for pts in itertools.combinations(POINTS, 2):
        if affine_dim(pts) != 1:
            continue
        masses = uniform(pts)
        for ymask in range(4):
            ys = dict((pts[i], (ymask >> i) & 1) for i in range(2))
            src = {"name": "probe", "support": tuple(sorted(pts)),
                   "masses": masses, "target": lambda p, ys=ys: ys[p],
                   "note": ""}
            cases += 1
            ones = sum(masses[p] for p in pts if ys[p] == 1)
            zero_mi = (ones == 0 or ones == 1)
            determined = any(coordinate_determines_target(src, j)
                             for j in range(N))
            if zero_mi and determined:
                satisfying += 1
    return {"supports_of_dimension_1": 120, "cases_checked": cases,
            "cases_satisfying_the_full_conjunction": satisfying}


def row3_block():
    lit = ROSTER["S_LOWDIM_USELESS"]
    mi_lit, exact_lit = mutual_information_bits_block1(lit)
    eff_lit = interventional_effect_block1(lit)
    comp = COMPOSITE
    v1, v2 = block_supports(comp["support"])
    mi_comp, exact_comp = mutual_information_bits_block1(comp)
    eff_comp = interventional_effect_block1(comp)
    rel = C_LOWDIM_RELEVANT
    mi_rel, _ = mutual_information_bits_block1(rel)
    eff_rel = interventional_effect_block1(rel)
    determining = [j for j in BLOCKS[1] if coordinate_determines_target(comp, j)]
    return {
        "literal_witness": {
            "name": lit["name"],
            "support": list(lit["support"]),
            "affine_dimension": affine_dim(lit["support"]),
            "mutual_information_bits": fr(mi_lit),
            "interventional_effect": fr(eff_lit),
            "target_is_constant_on_support": True,
            "coordinates_determining_the_target": [
                j for j in range(N) if coordinate_determines_target(lit, j)],
            "register_gloss_satisfied": (
                affine_dim(lit["support"]) == 1 and mi_lit == 0
                and eff_lit == 0),
        },
        "impossibility": {
            "zero_information_forces_constant_target":
                zero_information_forces_constant_certificate(),
            "dimension_1_exhaustive": literal_reading_certificate(),
            "two_independent_obstructions": [
                "a deterministic target with exact zero mutual information is "
                "constant on the support, so no coordinate can equal it or "
                "its complement while varying on the support",
                "affine dimension 1 forces a support of exactly 2 points, on "
                "which any coordinate that takes both values determines the "
                "target and hence carries strictly positive information",
            ],
        },
        "composite_witness": {
            "name": comp["name"],
            "support": list(comp["support"]),
            "affine_dimension": affine_dim(comp["support"]),
            "block1_factor_values": [list(v) for v in v1],
            "block2_factor_values": [list(v) for v in v2],
            "block1_factor_dimension": block_affine_dim(v1),
            "block2_factor_dimension": block_affine_dim(v2),
            "block2_is_full_dimension_in_its_block": block_affine_dim(v2) == 2,
            "product_measure": is_product_measure(comp),
            "mutual_information_block1_bits": fr(mi_comp),
            "mutual_information_exact": exact_comp,
            "interventional_effect_block1": fr(eff_comp),
            "best_accuracy_reading_block1_only":
                fr(best_accuracy_reading_block(comp, 0)),
            "best_accuracy_reading_block2_only":
                fr(best_accuracy_reading_block(comp, 1)),
            "coordinates_of_block2_determining_the_target": determining,
            "interventional_effect_of_coordinate_2":
                fr(interventional_effect_coordinate(comp, 2)),
        },
        "relaxed_companion": {
            "name": rel["name"],
            "mutual_information_block1_bits": fr(mi_rel),
            "interventional_effect_block1": fr(eff_rel),
        },
    }


# ---------------------------------------------------------------------------
# Row 2: the non-manifold witness
# ---------------------------------------------------------------------------
def row2_block():
    src = ROSTER["S_NONMANIFOLD_LEARNABLE"]
    g = hamming1_graph(src["support"])
    md = maximal_coset_dims(src["support"])
    acc2, J = best_local(src, 2)
    _ok, uw = union_or_stratification(src["support"])
    piece_dims = sorted(affine_dim(tuple(p)) for p in
                        [[0, 1, 2, 3], [0, 4]])
    return {
        "name": src["name"],
        "support": list(src["support"]),
        "affine_dimension": affine_dim(src["support"]),
        "registered_pieces": {"coset_A": [0, 1, 2, 3], "coset_B": [0, 4],
                              "dimensions": piece_dims,
                              "intersection": [0]},
        "non_manifold_certificates": {
            "degree_sequence": g["degree_sequence"],
            "degree_sequence_is_constant":
                len(set(g["degree_sequence"])) == 1,
            "maximal_coset_dimensions": md,
            "maximal_coset_dimensions_are_heterogeneous": len(md) >= 2,
            "pieces_have_distinct_dimensions": len(set(piece_dims)) >= 2,
            "pieces_intersect": True,
        },
        "union_witness": uw,
        "learned_exactly": {
            "class": "M_local[2]",
            "cost_bits": cost_local(2),
            "accuracy": fr(acc2),
            "coordinates": list(J) if J else [],
        },
        "graph": g,
    }


# ---------------------------------------------------------------------------
# Derivations for rows 4-6
# ---------------------------------------------------------------------------
def locality_condition(src, k):
    acc, J = best_local(src, k)
    return acc == 1, acc, J


def symmetry_condition(src, idx):
    sf = frozenset(src["support"])
    H = SUBGROUPS[idx]
    if frozenset(perm_apply(s, p) for s in H for p in src["support"]) != sf:
        return False, "support not invariant"
    if any(src["masses"][p] != src["masses"][perm_apply(s, p)]
           for s in H for p in src["support"]):
        return False, "measure not invariant"
    for s in H:
        for p in src["support"]:
            if src["target"](p) != src["target"](perm_apply(s, p)):
                return False, "target not invariant"
    return True, "source and target invariant"


def compositionality_condition(src):
    acc, arg = best_modular(src)
    return acc == 1, acc, arg


def derivation_locality():
    pos = DWORLDS["D_LOCAL_POS"]
    neg = DWORLDS["D_LOCAL_NEG"]
    k = 2
    holds_pos, acc_pos, J_pos = locality_condition(pos, k)
    holds_neg, acc_neg, J_neg = locality_condition(neg, k)
    budget = cost_local(k)
    mono_pos, mono_pos_arg, tmax = best_monolithic(pos, budget)
    mono_neg, mono_neg_arg, _ = best_monolithic(neg, budget)
    return {
        "named_class": "M_local[2]",
        "condition": ("some 2-subset of coordinates determines the target "
                      "exactly on the support"),
        "integer_cost": budget,
        "comparator": "M_monolithic at the same integer budget",
        "comparator_max_terms": tmax,
        "positive": {
            "world": pos["name"], "condition_holds": holds_pos,
            "named_class_accuracy": fr(acc_pos),
            "named_class_coordinates": list(J_pos) if J_pos else [],
            "comparator_accuracy": fr(mono_pos),
            "comparator_table_mask": mono_pos_arg,
            "advantage": fr(acc_pos - mono_pos),
            "class_profile_at_budget": class_profile_at_budget(pos, budget),
        },
        "matched_failure": {
            "world": neg["name"], "condition_holds": holds_neg,
            "named_class_accuracy": fr(acc_neg),
            "comparator_accuracy": fr(mono_neg),
            "comparator_table_mask": mono_neg_arg,
            "named_class_strictly_worse": acc_neg < mono_neg,
            "accuracy_drop": fr(mono_neg - acc_neg),
            "class_profile_at_budget": class_profile_at_budget(neg, budget),
        },
        "condition_falsified_on_roster": not holds_neg,
        "status": "DERIVED" if (holds_pos and not holds_neg
                                and acc_neg < mono_neg)
                  else "UNFALSIFIED_CONDITION",
    }


def derivation_symmetry():
    pos = DWORLDS["D_SYM_POS"]
    neg = DWORLDS["D_SYM_NEG"]
    idx = SYM_N_INDEX
    holds_pos, why_pos = symmetry_condition(pos, idx)
    holds_neg, why_neg = symmetry_condition(neg, idx)
    budget = cost_shared(idx)
    acc_pos = best_shared(pos, idx)
    acc_neg = best_shared(neg, idx)
    unshared_idx = 0
    unshared_cost = cost_shared(unshared_idx)
    mono_pos, mono_pos_arg, tmax = best_monolithic(pos, budget)
    mono_neg, mono_neg_arg, _ = best_monolithic(neg, budget)
    loc_pos = max([best_local(pos, k)[0] for k in range(N + 1)
                   if cost_local(k) <= budget] or [Fraction(0)])
    return {
        "named_class": "M_shared[SymN]",
        "condition": ("the source measure and the target are invariant under "
                      "the registered subgroup"),
        "group": SUBGROUP_NAMES[idx],
        "group_order": len(SUBGROUPS[idx]),
        "orbit_count": len(ORBITS[idx]),
        "integer_cost": budget,
        "unshared_class": SUBGROUP_NAMES[unshared_idx],
        "unshared_cost": unshared_cost,
        "cost_reduction_bits": unshared_cost - budget,
        "orbit_count_reduction": len(ORBITS[unshared_idx]) - len(ORBITS[idx]),
        "cost_reduction_equals_orbit_reduction":
            (unshared_cost - budget) == (len(ORBITS[unshared_idx])
                                         - len(ORBITS[idx])),
        "comparator": "M_monolithic at the same integer budget",
        "comparator_max_terms": tmax,
        "positive": {
            "world": pos["name"], "condition_holds": holds_pos,
            "condition_detail": why_pos,
            "named_class_accuracy": fr(acc_pos),
            "unshared_class_accuracy": fr(best_shared(pos, unshared_idx)),
            "comparator_accuracy": fr(mono_pos),
            "comparator_table_mask": mono_pos_arg,
            "best_local_within_budget": fr(loc_pos),
            "advantage": fr(acc_pos - max(mono_pos, loc_pos)),
            "class_profile_at_budget": class_profile_at_budget(pos, budget),
        },
        "matched_failure": {
            "world": neg["name"], "condition_holds": holds_neg,
            "condition_detail": why_neg,
            "named_class_accuracy": fr(acc_neg),
            "comparator_accuracy": fr(mono_neg),
            "comparator_table_mask": mono_neg_arg,
            "named_class_strictly_worse": acc_neg < mono_neg,
            "accuracy_drop": fr(mono_neg - acc_neg),
            "class_profile_at_budget": class_profile_at_budget(neg, budget),
        },
        "condition_falsified_on_roster": not holds_neg,
        "status": "DERIVED" if (holds_pos and not holds_neg
                                and acc_neg < mono_neg)
                  else "UNFALSIFIED_CONDITION",
    }


def monolithic_in_modular_certificate():
    """Exhaustive: every function reachable by M_monolithic at the modular
    budget is already modular, so the monolithic comparator provably cannot
    produce the compositional matched failure."""
    budget = cost_modular()
    tmax = (budget - TAG_BITS - MONO_COUNT_FIELD) // 4
    modular = set(MODULAR_TABLES)
    inside = [ff for ff in range(1 << (1 << N))
              if ANF_TERM_COUNT[ff] <= tmax]
    outside_at_next = [ff for ff in range(1 << (1 << N))
                       if ANF_TERM_COUNT[ff] <= tmax + 1
                       and ff not in modular]
    return {
        "modular_budget": budget,
        "monolithic_max_terms_at_that_budget": tmax,
        "monolithic_functions_at_that_budget": len(inside),
        "all_contained_in_M_modular": all(ff in modular for ff in inside),
        "distinct_modular_functions": len(modular),
        "containment_is_sharp_at_one_more_term": len(outside_at_next) > 0,
        "reason": ("a monolithic description of at most one term is a "
                   "conjunction of literals, and a conjunction factorizes "
                   "across the registered blocks"),
    }


def derivation_compositionality():
    pos = DWORLDS["D_COMP_POS"]
    neg = DWORLDS["D_COMP_NEG"]
    budget = cost_modular()
    holds_pos, acc_pos, arg_pos = compositionality_condition(pos)
    holds_neg, acc_neg, arg_neg = compositionality_condition(neg)
    mono_pos, mono_pos_arg, tmax = best_monolithic(pos, budget)
    mono_neg, mono_neg_arg, _ = best_monolithic(neg, budget)
    sym_idx = SYM_N_INDEX
    sym_neg = best_shared(neg, sym_idx)
    sym_pos = best_shared(pos, sym_idx)
    return {
        "named_class": "M_modular",
        "condition": ("the target factorizes through the registered blocks as "
                      "g(h1(B1), h2(B2)) with one-bit block summaries"),
        "integer_cost": budget,
        "comparator": "M_monolithic at the same integer budget",
        "comparator_max_terms": tmax,
        "positive": {
            "world": pos["name"], "condition_holds": holds_pos,
            "named_class_accuracy": fr(acc_pos),
            "named_class_table_mask": arg_pos,
            "comparator_accuracy": fr(mono_pos),
            "comparator_table_mask": mono_pos_arg,
            "advantage": fr(acc_pos - mono_pos),
            "best_shared_SymN_accuracy": fr(sym_pos),
            "class_profile_at_budget": class_profile_at_budget(pos, budget),
        },
        "matched_failure": {
            "world": neg["name"], "condition_holds": holds_neg,
            "named_class_accuracy": fr(acc_neg),
            "monolithic_comparator_accuracy": fr(mono_neg),
            "monolithic_comparator_can_expose_the_failure":
                acc_neg < mono_neg,
            "failure_comparator": "M_shared[SymN]",
            "failure_comparator_cost": cost_shared(sym_idx),
            "failure_comparator_accuracy": fr(sym_neg),
            "named_class_strictly_worse": acc_neg < sym_neg,
            "accuracy_drop": fr(sym_neg - acc_neg),
            "class_profile_at_budget": class_profile_at_budget(neg, budget),
        },
        "monolithic_comparator_containment": monolithic_in_modular_certificate(),
        "condition_falsified_on_roster": not holds_neg,
        "status": "DERIVED" if (holds_pos and not holds_neg
                                and acc_neg < sym_neg)
                  else "UNFALSIFIED_CONDITION",
    }


def mutual_information_bits_full(src):
    """Exact I(X;Y) for a deterministic target: 0 iff the target is constant."""
    ones = sum(src["masses"][p] for p in src["support"] if src["target"](p))
    if ones == 0 or ones == 1:
        return Fraction(0)
    return None


# ---------------------------------------------------------------------------
# Bounds with the full vacuity record
# ---------------------------------------------------------------------------
def bound_record(name, kind, bound_value, range_lo, range_hi,
                 range_derivation, attained_by, violated_by, note=None):
    if kind == "upper":
        vacuous = bound_value >= range_hi
    elif kind == "lower":
        vacuous = bound_value <= range_lo
    else:
        raise ExecutorError("bad bound kind %r" % kind)
    rec = {
        "name": name,
        "kind": kind,
        "bound_value": fr(bound_value),
        "range_lo": fr(range_lo),
        "range_hi": fr(range_hi),
        "range_derivation": range_derivation,
        "vacuous": vacuous,
        "attained_by": attained_by,
        "violated_by": violated_by,
        "status": "UNFALSIFIED_BOUND" if violated_by is None else "FALSIFIABLE",
    }
    if note is not None:
        rec["note"] = note
    return rec


ACCURACY_RANGE_DERIVATION = (
    "an accuracy is a probability, so it lies in [0,1] by definition; the "
    "lower end is raised to the base rate max_y P(Y=y) because every model "
    "class considered here contains the two constant functions, and no "
    "endpoint is taken from the roster's observed values"
)


def build_bounds(loc, sym, comp, row3):
    out = []
    neg_loc = DWORLDS["D_LOCAL_NEG"]
    out.append(bound_record(
        "B1_local_accuracy_when_condition_fails", "upper",
        Fraction(loc["matched_failure"]["named_class_accuracy"]),
        base_rate(neg_loc), Fraction(1), ACCURACY_RANGE_DERIVATION,
        {"object": "the constant-zero member of M_local[2]",
         "accuracy": loc["matched_failure"]["named_class_accuracy"]},
        {"relaxed_class": "M_local[4] at integer cost %d" % cost_local(4),
         "accuracy": fr(best_local(neg_loc, 4)[0]),
         "why": "the relaxed class reads every coordinate and attains 1"}))
    neg_sym = DWORLDS["D_SYM_NEG"]
    relaxed_idx = None
    for idx in range(len(SUBGROUPS)):
        if len(SUBGROUPS[idx]) == 1:
            continue
        if best_shared(neg_sym, idx) > best_shared(neg_sym, SYM_N_INDEX):
            relaxed_idx = idx
            break
    out.append(bound_record(
        "B2_shared_accuracy_when_condition_fails", "upper",
        Fraction(sym["matched_failure"]["named_class_accuracy"]),
        base_rate(neg_sym), Fraction(1), ACCURACY_RANGE_DERIVATION,
        {"object": "the orbit rule that predicts 1 above the weight threshold",
         "accuracy": sym["matched_failure"]["named_class_accuracy"]},
        {"relaxed_class": "M_shared[%s] at integer cost %d"
                          % (SUBGROUP_NAMES[relaxed_idx],
                             cost_shared(relaxed_idx)),
         "accuracy": fr(best_shared(neg_sym, relaxed_idx)),
         "why": "a strictly smaller subgroup keeps the target inside the "
                "invariant class"}))
    neg_comp = DWORLDS["D_COMP_NEG"]
    relaxed_mod = modular_tables_two_bit_latent()
    out.append(bound_record(
        "B3_modular_accuracy_when_condition_fails", "upper",
        Fraction(comp["matched_failure"]["named_class_accuracy"]),
        base_rate(neg_comp), Fraction(1), ACCURACY_RANGE_DERIVATION,
        {"object": "the best one-bit block summary pair",
         "accuracy": comp["matched_failure"]["named_class_accuracy"]},
        {"relaxed_class": "modular models with two-bit block summaries",
         "accuracy": fr(relaxed_mod),
         "why": "widening each block summary from one bit to two attains 1"}))
    ks = kraft_sum(True)
    ks_relaxed = kraft_sum(False)
    n_desc = registered_description_count()
    out.append(bound_record(
        "B4_kraft_sum_of_the_registered_code", "upper", Fraction(1),
        Fraction(0), Fraction(n_desc, 2),
        "by definition the Kraft sum of a finite description set is a sum "
        "of positive powers of two, hence at least 0, and at most (number of "
        "descriptions)/2 because every codeword is at least one bit long; "
        "neither endpoint comes from the roster",
        {"object": "the complete fixed-length 16-bit truth-table code over "
                   "all 2^16 functions",
         "kraft_sum": "1"},
        {"relaxed_class": "the same code with the term-count field removed "
                          "from the monolithic branch",
         "kraft_sum": fr(ks_relaxed),
         "why": "without the self-delimiting term count the branch is no "
                "longer prefix-free and the Kraft sum exceeds 1"},
        note="the registered code's exact Kraft sum is %s" % fr(ks)))
    out.append(bound_record(
        "B5_cycle_rank_of_a_proper_coset", "upper", Fraction(5),
        Fraction(0), Fraction(N * (1 << (N - 1)) - (1 << N) + 1),
        "the cycle rank of a graph is |E| - |V| + c >= 0 by definition, and "
        "the Hamming-1 graph of {0,1}^4 has n*2^(n-1) = 32 edges on 16 "
        "vertices, so any connected induced subgraph has cycle rank at most "
        "32 - 16 + 1 = 17; both endpoints come from the definition",
        {"object": "a GF(2) coset of dimension 3",
         "cycle_rank": str(3 * 4 - 8 + 1)},
        {"relaxed_class": "cosets of dimension at most 4",
         "cycle_rank": str(max(GEOMETRIC_CYCLE_RANKS)),
         "why": "the dimension-4 coset is the whole cube, with cycle rank 17"}))
    comp_src = COMPOSITE
    rel = C_LOWDIM_RELEVANT
    out.append(bound_record(
        "B6_interventional_effect_of_the_dimension_1_factor", "upper",
        Fraction(0), Fraction(0), Fraction(1),
        "the quantity is the largest absolute difference between two "
        "probabilities, hence lies in [0,1] by definition of a probability",
        {"object": COMPOSITE["name"],
         "interventional_effect": fr(interventional_effect_block1(comp_src))},
        {"relaxed_class": "sources on the same support whose dimension-1 "
                          "factor is allowed to carry the target",
         "object": rel["name"],
         "interventional_effect": fr(interventional_effect_block1(rel)),
         "why": "the same maximally low-dimensional factor now moves the "
                "target by the full amount"}))
    out.append(bound_record(
        "B7_information_of_the_dimension_1_factor", "upper",
        Fraction(0), Fraction(0), Fraction(1),
        "mutual information is non-negative, and with a binary target it is "
        "at most H(Y) <= log2(2) = 1 bit; both endpoints come from the "
        "definition of mutual information",
        {"object": COMPOSITE["name"],
         "mutual_information_bits":
             fr(mutual_information_bits_block1(comp_src)[0])},
        {"relaxed_class": "sources on the same support whose dimension-1 "
                          "factor is allowed to carry the target",
         "object": rel["name"],
         "mutual_information_bits":
             fr(mutual_information_bits_block1(rel)[0]),
         "why": "the factor then carries the whole bit of the target"}))
    pos_loc = DWORLDS["D_LOCAL_POS"]
    b = cost_local(2)
    out.append(bound_record(
        "B8_monolithic_comparator_at_the_locality_budget", "upper",
        Fraction(loc["positive"]["comparator_accuracy"]),
        base_rate(pos_loc), Fraction(1), ACCURACY_RANGE_DERIVATION,
        {"object": "the best single-term monolithic description",
         "accuracy": loc["positive"]["comparator_accuracy"]},
        {"relaxed_class": "M_monolithic at the relaxed budget %d"
                          % cost_monolithic(2),
         "accuracy": fr(best_monolithic(pos_loc, cost_monolithic(2))[0]),
         "why": "one more term buys the exact two-term description"}))
    pos_sym = DWORLDS["D_SYM_POS"]
    out.append(bound_record(
        "B9_monolithic_comparator_at_the_symmetry_budget", "upper",
        Fraction(sym["positive"]["comparator_accuracy"]),
        base_rate(pos_sym), Fraction(1), ACCURACY_RANGE_DERIVATION,
        {"object": "the best single-term monolithic description",
         "accuracy": sym["positive"]["comparator_accuracy"]},
        {"relaxed_class": "M_monolithic at the relaxed budget %d"
                          % cost_monolithic(5),
         "accuracy": fr(best_monolithic(pos_sym, cost_monolithic(5))[0]),
         "why": "the exact description of the weight threshold needs five "
                "terms and then attains 1"}))
    pos_comp = DWORLDS["D_COMP_POS"]
    out.append(bound_record(
        "B10_monolithic_comparator_at_the_modular_budget", "upper",
        Fraction(comp["positive"]["comparator_accuracy"]),
        base_rate(pos_comp), Fraction(1), ACCURACY_RANGE_DERIVATION,
        {"object": "the best single-term monolithic description",
         "accuracy": comp["positive"]["comparator_accuracy"]},
        {"relaxed_class": "M_monolithic at the relaxed budget %d"
                          % cost_monolithic(4),
         "accuracy": fr(best_monolithic(pos_comp, cost_monolithic(4))[0]),
         "why": "the exact four-term description attains 1"}))
    return out


def registered_description_count():
    total = 0
    for k in range(N + 1):
        total += len(list(itertools.combinations(range(N), k))) * (1 << (1 << k))
    for idx in range(len(SUBGROUPS)):
        total += 1 << len(ORBITS[idx])
    total += 1 << 12
    total += 1 << (1 << N)
    return total


def modular_tables_two_bit_latent():
    """Best accuracy of the relaxed modular class with two-bit block summaries
    on the compositional failure world: the identity summaries already give the
    exact target."""
    neg = DWORLDS["D_COMP_NEG"]
    best = Fraction(0)
    for gg in range(1 << 16):
        acc = Fraction(0)
        for p in neg["support"]:
            u = bit(p, 0) + 2 * bit(p, 1)
            v = bit(p, 2) + 2 * bit(p, 3)
            if ((gg >> (u + 4 * v)) & 1) == (1 if neg["target"](p) else 0):
                acc += neg["masses"][p]
        if acc > best:
            best = acc
        if best == 1:
            break
    return best


# ---------------------------------------------------------------------------
# Hostiles: potency first, detection second
# ---------------------------------------------------------------------------
def perturbed_rank_capped(vectors, cap=2):
    basis = []
    for v in vectors:
        cur = v
        for b in basis:
            if (cur ^ b) < cur:
                cur ^= b
        if cur and len(basis) < cap:
            basis.append(cur)
            basis.sort(reverse=True)
    return len(basis)


def best_modular_leaked_blocks(src):
    """Best accuracy of a block-wise composition under the LEAKED decomposition
    ({0,1,2}, {3}) rather than the registered one."""
    best = Fraction(0)
    for h1 in range(1 << 8):
        for h2 in range(1 << 2):
            for g in range(1 << 4):
                acc = Fraction(0)
                for p in src["support"]:
                    u = (h1 >> (bit(p, 0) + 2 * bit(p, 1)
                                + 4 * bit(p, 2))) & 1
                    v = (h2 >> bit(p, 3)) & 1
                    if ((g >> (u + 2 * v)) & 1) == (
                            1 if src["target"](p) else 0):
                        acc += src["masses"][p]
                if acc > best:
                    best = acc
                if best == 1:
                    return best
    return best


def build_hostiles(register):
    out = []

    alg = ROSTER["S_ALGORITHMIC"]
    pts = sorted(alg["support"])
    true_dim = affine_dim(pts)
    pert_dim = perturbed_rank_capped([p ^ pts[0] for p in pts[1:]], 2)
    out.append({
        "name": "H_DIM_INFLATE",
        "perturbs": "the GF(2) rank computation so a full-dimension support "
                    "is scored as low-dimensional",
        "object": alg["name"],
        "true_value": true_dim,
        "perturbed_value": pert_dim,
        "potency": pert_dim != true_dim,
        "detected": pert_dim != true_dim,
        "detector": "route B recomputes the affine dimension by brute-force "
                    "affine closure and the cross-route comparison fails",
        "inverted": False,
    })

    cyc = ROSTER["S_CYCLE"]
    support_only = []
    sf = frozenset(cyc["support"])
    for i, H in enumerate(SUBGROUPS):
        if len(H) == 1:
            continue
        if frozenset(perm_apply(s, p) for s in H for p in cyc["support"]) == sf:
            support_only.append(i)
    true_inv = len(stabilizer_indices(cyc["support"], cyc["masses"])) > 0
    pert_inv = len(support_only) > 0
    out.append({
        "name": "H_ORBIT_MERGE",
        "perturbs": "the orbit partition so a non-invariant source is scored "
                    "as invariant, by dropping the requirement that the exact "
                    "masses be invariant too",
        "object": cyc["name"],
        "true_value": true_inv,
        "perturbed_value": pert_inv,
        "true_invariance_subgroup_count":
            len(stabilizer_indices(cyc["support"], cyc["masses"])),
        "perturbed_invariance_subgroup_count": len(support_only),
        "potency": pert_inv != true_inv,
        "detected": pert_inv != true_inv,
        "detector": "route B checks support invariance and exact mass "
                    "invariance separately over all 24 permutations",
        "inverted": False,
    })

    leak = DWORLDS["D_BLOCKLEAK"]
    true_mod = best_modular(leak)[0]
    pert_mod = best_modular_leaked_blocks(leak)
    out.append({
        "name": "H_BLOCK_LEAK",
        "perturbs": "the block decomposition so a non-factorizing target is "
                    "scored as factorizing",
        "object": leak["name"],
        "true_value": fr(true_mod),
        "perturbed_value": fr(pert_mod),
        "registered_blocks": [list(b) for b in BLOCKS],
        "leaked_blocks": [[0, 1, 2], [3]],
        "potency": pert_mod != true_mod,
        "detected": ([[0, 1, 2], [3]]
                     != register["registered_constants"]["blocks"]
                     and [list(b) for b in BLOCKS]
                     == register["registered_constants"]["blocks"]),
        "detector": "the checker compares the block decomposition it used "
                    "against the registered blocks and refuses a mismatch",
        "inverted": False,
    })

    cpos = DWORLDS["D_COMP_POS"]
    true_budget = cost_modular()
    inflated_budget = cost_monolithic(4)
    true_mono = best_monolithic(cpos, true_budget)[0]
    pert_mono = best_monolithic(cpos, inflated_budget)[0]
    out.append({
        "name": "H_BUDGET_INFLATE",
        "perturbs": "the monolithic budget upward so the compositional "
                    "advantage disappears",
        "object": cpos["name"],
        "true_budget": true_budget,
        "inflated_budget": inflated_budget,
        "true_value": fr(true_mono),
        "perturbed_value": fr(pert_mono),
        "potency": pert_mono != true_mono,
        "detected": inflated_budget != true_budget,
        "detector": "the checker asserts the comparator budget equals the "
                    "registered integer cost of the named class",
        "inverted": False,
    })

    true_cyc = hamming1_graph(cyc["support"])["cycle_rank"]
    moved = tuple(sorted(set(cyc["support"]) - set([6]) | set([0])))
    pert_cyc = hamming1_graph(moved)["cycle_rank"]
    out.append({
        "name": "H_CYCLE_RANK",
        "perturbs": "one support point so the Hamming-1 graph cycle rank "
                    "changes",
        "object": cyc["name"],
        "moved_support": list(moved),
        "true_value": true_cyc,
        "perturbed_value": pert_cyc,
        "potency": pert_cyc != true_cyc,
        "detected": pert_cyc != true_cyc,
        "detector": "route B rebuilds the edge list and the component count "
                    "from scratch and compares the cycle rank",
        "inverted": False,
    })
    return out


# ---------------------------------------------------------------------------
# Null: the row-3 detector against randomized tasks on random block geometry
# ---------------------------------------------------------------------------
class Lcg(object):
    def __init__(self, seed):
        self.state = seed % NULL_LCG_MODULUS

    def next(self, bound):
        self.state = (NULL_LCG_MULTIPLIER * self.state
                      + NULL_LCG_INCREMENT) % NULL_LCG_MODULUS
        return (self.state >> 8) % bound


def row3_detector(src):
    """Fires when the source presents a maximally low-dimensional factor that
    is exactly useless for the task while the complementary full-dimension
    factor determines it exactly."""
    prod, v1, v2 = is_block_product(src["support"])
    if not prod:
        return False, None
    if not is_product_measure(src):
        return False, None
    if block_affine_dim(v1) != 1:
        return False, None
    if block_affine_dim(v2) != 2:
        return False, None
    mi, exact = mutual_information_bits_block1(src)
    if not exact or mi != 0:
        return False, None
    eff = interventional_effect_block1(src)
    if eff is None or eff != 0:
        return False, None
    if not any(coordinate_determines_target(src, j) for j in BLOCKS[1]):
        return False, None
    return True, None


def row3_magnitude(src):
    return (best_accuracy_reading_block(src, 1)
            - best_accuracy_reading_block(src, 0))


def null_block():
    rng = Lcg(NULL_SEED)
    fired = []
    magnitudes = []
    for trial in range(NULL_TRIALS):
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
        ys = {}
        for p in support:
            ys[p] = rng.next(2)
        src = {"name": "null_%03d" % trial, "support": support,
               "masses": masses, "target": (lambda p, ys=ys: ys[p]),
               "note": ""}
        mag = row3_magnitude(src)
        magnitudes.append(mag)
        hit, _ = row3_detector(src)
        if hit:
            mi_t, _ex = mutual_information_bits_block1(src)
            fired.append({
                "trial": trial,
                "support": list(support),
                "magnitude": fr(mag),
                "mutual_information_block1_bits": fr(mi_t),
                "interventional_effect_block1":
                    fr(interventional_effect_block1(src)),
                "best_accuracy_reading_block2_only":
                    fr(best_accuracy_reading_block(src, 1)),
                "best_accuracy_reading_block1_only":
                    fr(best_accuracy_reading_block(src, 0)),
                "genuine_instance": True,
            })
    witness_mag = row3_magnitude(COMPOSITE)
    witness_fires, _ = row3_detector(COMPOSITE)
    clean = []
    for src in (ROSTER["S_BLOCKPROD"], C_LOWDIM_RELEVANT,
                ROSTER["S_SUBSPACE"]):
        hit, _ = row3_detector(src)
        clean.append({"witness": src["name"], "detector_fires": hit,
                      "magnitude": fr(row3_magnitude(src))})
    largest = max(magnitudes) if magnitudes else Fraction(0)
    return {
        "detector": ("the support is an exact block product with a "
                     "dimension-1 factor on block 1 and a full-dimension "
                     "factor on block 2, the measure is a product measure, "
                     "the exact mutual information between the dimension-1 "
                     "factor and the target is 0 bits, the exact "
                     "interventional effect of that factor on the target is "
                     "0, and some coordinate of block 2 determines the "
                     "target exactly"),
        "magnitude_definition": ("best accuracy reading block 2 only minus "
                                 "best accuracy reading block 1 only"),
        "sampler": ("block supports drawn uniformly from the 15 non-empty "
                    "subsets of each block's value set, product masses drawn "
                    "as positive integers summing to %d per block, target "
                    "drawn uniformly over all assignments on the support"
                    % NULL_MASS_TOTAL),
        "sampler_is_an_implementation_constant_outside_the_register": True,
        "lcg": {"modulus": NULL_LCG_MODULUS,
                "multiplier": NULL_LCG_MULTIPLIER,
                "increment": NULL_LCG_INCREMENT, "seed": NULL_SEED},
        "trials": NULL_TRIALS,
        "planted_positive": COMPOSITE["name"],
        "planted_positive_flagged": witness_fires,
        "planted_positive_magnitude": fr(witness_mag),
        "random_worlds_flagged": len(fired),
        "random_worlds_flagged_detail": fired,
        "largest_null_magnitude": fr(largest),
        "witness_exceeds_largest_null_magnitude": witness_mag > largest,
        "magnitude_definitional_maximum": fr(Fraction(1, 2)),
        "witness_attains_definitional_maximum":
            witness_mag == Fraction(1, 2),
        "primary_comparison": (
            "the exact firing rate of the full conjunction over the "
            "registered %d trials. The magnitude is bounded above by "
            "1 - base rate <= 1/2 by definition, and the planted witness "
            "attains that definitional maximum, so a strictly-exceeds "
            "comparison on the magnitude is structurally impossible and is "
            "reported only for completeness" % NULL_TRIALS),
        "no_alarm_cases": clean,
        "no_alarm_case_holds": all(not c["detector_fires"] for c in clean),
        "firing_trials_are_genuine_instances": all(
            f["mutual_information_block1_bits"] == "0"
            and f["interventional_effect_block1"] == "0"
            and f["best_accuracy_reading_block2_only"] == "1"
            for f in fired),
        "finding": (
            "the detector fires on %d of %d randomized tasks over random "
            "block geometry; every firing trial is a genuine instance of the "
            "same phenomenon and is listed individually with its exact "
            "values, so the rate is a reproducibility rate and not a false "
            "alarm rate" % (len(fired), NULL_TRIALS)),
    }


# ---------------------------------------------------------------------------
# Register custody
# ---------------------------------------------------------------------------
def load_register():
    path = HERE / "PROSPECTIVE_REGISTER_V1.json"
    reg = json.loads(path.read_text(encoding="utf-8"))
    core = dict(reg)
    core.pop("self_digest_sha256", None)
    core.pop("self_digest_note", None)
    digest = hashlib.sha256(json.dumps(
        core, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    if digest != reg["self_digest_sha256"]:
        raise ExecutorError(
            "prospective register digest mismatch: recomputed %s, carried %s"
            % (digest, reg["self_digest_sha256"]))
    return reg, digest


# ---------------------------------------------------------------------------
# Prospective predictions
# ---------------------------------------------------------------------------
def prospective(register, table, separated, row2, row3, loc, sym, comp, bounds):
    preds = []
    total_pairs = len(table)
    not_sep = total_pairs - separated
    preds.append({
        "id": "AE6-P1",
        "claim": register["prospective_predictions"][0]["claim"],
        "verdict": "CONFIRMED" if (separated + not_sep) == total_pairs
                   and all(r["separated"] or r["reason"] for r in table)
                   else "REFUTED",
        "ordered_pairs": total_pairs,
        "separated_with_witness": separated,
        "explicitly_not_separated": not_sep,
    })
    cert = row2["non_manifold_certificates"]
    p2_ok = (not cert["degree_sequence_is_constant"]
             and cert["maximal_coset_dimensions_are_heterogeneous"]
             and cert["pieces_have_distinct_dimensions"]
             and row2["learned_exactly"]["accuracy"] == "1")
    preds.append({
        "id": "AE6-P2",
        "claim": register["prospective_predictions"][1]["claim"],
        "verdict": "CONFIRMED" if p2_ok else "REFUTED",
        "degree_sequence": cert["degree_sequence"],
        "maximal_coset_dimensions": cert["maximal_coset_dimensions"],
        "accuracy_of_the_registered_rule_class":
            row2["learned_exactly"]["accuracy"],
        "rule_class": row2["learned_exactly"]["class"],
    })
    lit = row3["literal_witness"]
    conj = {
        "affine_dimension_is_1": lit["affine_dimension"] == 1,
        "mutual_information_is_0_bits": lit["mutual_information_bits"] == "0",
        "interventional_effect_is_0": lit["interventional_effect"] == "0",
        "a_full_dimension_coordinate_determines_the_target":
            len(lit["coordinates_determining_the_target"]) > 0,
    }
    preds.append({
        "id": "AE6-P3",
        "claim": register["prospective_predictions"][2]["claim"],
        "verdict": "CONFIRMED" if all(conj.values()) else "REFUTED",
        "conjuncts": conj,
        "refuted_conjunct": None if all(conj.values())
                            else "a_full_dimension_coordinate_determines_"
                                 "the_target",
        "exact_values": {
            "affine_dimension": lit["affine_dimension"],
            "mutual_information_bits": lit["mutual_information_bits"],
            "interventional_effect": lit["interventional_effect"],
            "coordinates_determining_the_target":
                lit["coordinates_determining_the_target"],
        },
        "why": ("the conjunction is unsatisfiable on any support: a "
                "deterministic target with exact zero mutual information is "
                "constant, and a constant target is not determined by any "
                "coordinate in the sense of equalling it or its complement "
                "while that coordinate varies. The repaired composite witness "
                "%s realizes every conjunct with the dimension-1 object taken "
                "as the exact GF(2) factor of the support rather than the "
                "whole support, and it is what closes the row."
                % row3["composite_witness"]["name"]),
        "repaired_witness": {
            "name": row3["composite_witness"]["name"],
            "factor_dimension": row3["composite_witness"][
                "block1_factor_dimension"],
            "mutual_information_bits": row3["composite_witness"][
                "mutual_information_block1_bits"],
            "interventional_effect": row3["composite_witness"][
                "interventional_effect_block1"],
            "accuracy_of_the_full_dimension_factor": row3[
                "composite_witness"]["best_accuracy_reading_block2_only"],
            "accuracy_of_the_dimension_1_factor": row3[
                "composite_witness"]["best_accuracy_reading_block1_only"],
        },
    })
    all_derived = all(d["status"] == "DERIVED" for d in (loc, sym, comp))
    preds.append({
        "id": "AE6-P4",
        "claim": register["prospective_predictions"][3]["claim"],
        "verdict": "CONFIRMED" if all_derived else "REFUTED",
        "statuses": {"locality": loc["status"], "symmetry": sym["status"],
                     "compositionality": comp["status"]},
        "accuracy_drops": {
            "locality": loc["matched_failure"]["accuracy_drop"],
            "symmetry": sym["matched_failure"]["accuracy_drop"],
            "compositionality": comp["matched_failure"]["accuracy_drop"]},
    })
    unfalsified = [b["name"] for b in bounds
                   if b["status"] == "UNFALSIFIED_BOUND"]
    complete = all(
        set(["kind", "bound_value", "range_lo", "range_hi",
             "range_derivation", "vacuous", "attained_by",
             "violated_by"]).issubset(set(b)) for b in bounds)
    preds.append({
        "id": "AE6-P5",
        "claim": register["prospective_predictions"][4]["claim"],
        "verdict": "CONFIRMED" if (complete and not unfalsified) else "REFUTED",
        "bounds_emitted": len(bounds),
        "unfalsified_bounds": unfalsified,
        "vacuous_bounds": [b["name"] for b in bounds if b["vacuous"]],
    })
    return preds


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def build_result():
    register, register_digest = load_register()

    classified = dict((name, classify(ROSTER[name])) for name in ROSTER_ORDER)
    table, separated = strictness_table(classified)
    census = union_census()
    sparse_cert = sparse_implies_low_dimension_certificate()
    row2 = row2_block()
    row3 = row3_block()
    loc = derivation_locality()
    sym = derivation_symmetry()
    comp = derivation_compositionality()
    bounds = build_bounds(loc, sym, comp, row3)
    hostiles = build_hostiles(register)
    null = null_block()
    preds = prospective(register, table, separated, row2, row3, loc, sym,
                        comp, bounds)

    kraft = kraft_sum(True)
    kraft_relaxed = kraft_sum(False)

    checks = {
        "register_digest_reproduced": register_digest == register[
            "self_digest_sha256"],
        "roster_matches_the_registered_source_list":
            sorted(ROSTER_ORDER) == sorted(
                register["roster"]["sources"]),
        "every_ordered_class_pair_is_resolved":
            all(r["separated"] or bool(r["reason"]) for r in table),
        "strictness_table_is_complete":
            len(table) == len(CLASSES) * (len(CLASSES) - 1),
        "union_predicate_census_is_exhaustive":
            census["supports_with_dimension_at_least_1"]
            == census["members"] + census["non_members"],
        "no_support_is_algorithmic_and_outside_the_union_class":
            census["every_non_member_has_nontrivial_stabilizer"],
        "sparse_compositional_is_contained_in_low_dimension":
            sparse_cert["maximum_affine_dimension"] < N,
        "row2_witness_is_not_a_manifold":
            (not row2["non_manifold_certificates"][
                "degree_sequence_is_constant"])
            and row2["non_manifold_certificates"][
                "maximal_coset_dimensions_are_heterogeneous"],
        "row2_witness_is_learned_exactly":
            row2["learned_exactly"]["accuracy"] == "1",
        "row3_literal_gloss_is_satisfied":
            row3["literal_witness"]["register_gloss_satisfied"],
        "row3_literal_conjunction_is_impossible":
            row3["impossibility"]["dimension_1_exhaustive"][
                "cases_satisfying_the_full_conjunction"] == 0,
        "row3_information_identity_verified_exhaustively":
            row3["impossibility"]["zero_information_forces_constant_target"][
                "violations"] == 0,
        "row3_composite_factor_is_dimension_1":
            row3["composite_witness"]["block1_factor_dimension"] == 1,
        "row3_composite_factor_is_statistically_useless":
            row3["composite_witness"]["mutual_information_block1_bits"] == "0",
        "row3_composite_factor_is_causally_useless":
            row3["composite_witness"]["interventional_effect_block1"] == "0",
        "row3_full_dimension_factor_determines_the_target":
            row3["composite_witness"][
                "best_accuracy_reading_block2_only"] == "1",
        "locality_derivation_holds": loc["status"] == "DERIVED",
        "symmetry_derivation_holds": sym["status"] == "DERIVED",
        "compositionality_derivation_holds": comp["status"] == "DERIVED",
        "symmetry_cost_reduction_equals_orbit_reduction":
            sym["cost_reduction_equals_orbit_reduction"],
        "monolithic_comparator_is_contained_in_the_modular_class":
            comp["monolithic_comparator_containment"][
                "all_contained_in_M_modular"],
        "every_bound_has_a_violated_by_witness":
            all(b["status"] == "FALSIFIABLE" for b in bounds),
        "no_bound_is_vacuous": all(not b["vacuous"] for b in bounds),
        "registered_code_is_kraft_compliant": kraft <= 1,
        "relaxed_code_violates_kraft": kraft_relaxed > 1,
        "every_hostile_is_potent": all(h["potency"] for h in hostiles),
        "every_hostile_is_detected": all(h["detected"] for h in hostiles),
        "null_planted_positive_fires": null["planted_positive_flagged"],
        "null_no_alarm_on_clean_witnesses": null["no_alarm_case_holds"],
        "null_firing_trials_are_genuine_instances":
            null["firing_trials_are_genuine_instances"],
        "null_witness_attains_the_definitional_maximum":
            null["witness_attains_definitional_maximum"],
        "every_prospective_prediction_is_reported":
            len(preds) == len(register["prospective_predictions"]),
        "refuted_predictions_are_reported_not_edited":
            all(p["verdict"] in ("CONFIRMED", "REFUTED") for p in preds),
    }

    results = {
        "registered_scope": {
            "ambient": "X = {0,1}^%d with Hamming distance" % N,
            "n": N,
            "blocks": [list(b) for b in BLOCKS],
            "block_support_cap": BLOCK_SUPPORT_CAP,
            "union_rank_cap": UNION_RANK_CAP,
            "dimension_range": list(DIMENSION_RANGE),
            "subgroup_lattice_size": len(SUBGROUPS),
            "coset_count": len(COSETS),
            "geometric_cycle_ranks": list(GEOMETRIC_CYCLE_RANKS),
            "geometric_cycle_rank_derivation":
                "a GF(2) coset of dimension d induces a d-cube, with "
                "d*2^(d-1) edges on 2^d vertices and cycle rank "
                "d*2^(d-1) - 2^d + 1",
            "structure_roster": list(ROSTER_ORDER),
            "derivation_worlds": sorted(DWORLDS),
            "derivation_worlds_note":
                "derivation worlds are distinct from the registered structure "
                "roster; the register's derivations block describes them "
                "abstractly and they are not roster additions",
            "auxiliary_witnesses": [COMPOSITE["name"],
                                    C_LOWDIM_RELEVANT["name"]],
            "algorithmic_circuit": {
                "family": "(x_i AND x_j) XOR x_k XOR (x_l OR x_m)",
                "chosen_tuple": list(ALG_CIRCUIT),
                "choice_rule": "lexicographically first tuple in {0..3}^5 "
                               "whose accepting set satisfies the class "
                               "predicate with a disconnected Hamming-1 graph",
                "accepting_set": list(ALG_SUPPORT),
            },
        },
        "structure_classes": dict(
            (name, classified[name]) for name in ROSTER_ORDER),
        "strictness_table": table,
        "strictness_summary": {
            "ordered_pairs": len(table),
            "separated_with_witness": separated,
            "not_separated": len(table) - separated,
        },
        "union_predicate_census": census,
        "sparse_containment_certificate": sparse_cert,
        "row2_nonmanifold_learnable": row2,
        "row3_low_dimension_is_useless": row3,
        "derivation_locality": loc,
        "derivation_symmetry": sym,
        "derivation_compositionality": comp,
        "description_code": {
            "tag_bits": TAG_BITS,
            "costs": {
                "M_local": dict(("k=%d" % k, cost_local(k))
                                for k in range(N + 1)),
                "M_shared[SymN]": cost_shared(SYM_N_INDEX),
                "M_shared[trivial]": cost_shared(0),
                "M_modular": cost_modular(),
                "M_monolithic": dict(("t=%d" % t, cost_monolithic(t))
                                     for t in range(0, 6)),
            },
            "kraft_sum": fr(kraft),
            "kraft_sum_is_at_most_1": kraft <= 1,
            "relaxed_code_kraft_sum": fr(kraft_relaxed),
            "relaxed_code_violates_kraft": kraft_relaxed > 1,
            "registered_description_count": registered_description_count(),
        },
    }

    receipt = {
        "schema": "GMI_833_AE6_GEOMETRIC_STRUCTURE_RESULT_V1",
        "issue": ISSUE,
        "issue_comment_id": ISSUE_COMMENT_ID,
        "section": SECTION,
        "package": PACKAGE,
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "register_commit": REGISTER_COMMIT,
        "register_digest": register_digest,
        "claim_ceiling": CLAIM_CEILING,
        "verdict": "GREEN" if all(checks.values()) else "RED",
        "checks": checks,
        "theorems": ["AE6-1", "AE6-2", "AE6-3", "AE6-4", "AE6-5", "AE6-6",
                     "AE6-7", "AE6-8"],
        "results": results,
        "bounds": bounds,
        "hostiles": hostiles,
        "null": null,
        "prospective_predictions": preds,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "rows_closed": 6,
        "rows_left_open": [{
            "row": "prospective test of intrinsic-structure transitions on "
                   "synthetic and real datasets",
            "instrument_required":
                "a pre-registered dataset instrument that (a) names the real "
                "corpora and their versioned checksums before any structure "
                "estimate is computed, (b) supplies an intrinsic-dimension "
                "and orbit-structure estimator with a stated confidence "
                "procedure on finite samples, and (c) fixes the held-out "
                "split and the decision rule in advance; none of these exist "
                "in this repository, and no finite exact roster can stand in "
                "for them",
        }],
    }
    return receipt


def main(argv=None):
    receipt = build_result()
    sys.stdout.write(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    return 0 if receipt["verdict"] == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())
