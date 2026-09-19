#!/usr/bin/env python3
"""GMI #833 AE9 route B: independent marker oracle.

This module recomputes every quantity claimed by route A
(``ae9_transition_markers_v1.py``) by a materially different algorithm.

Route B never imports route A.  Route B builds partitions by explicit
equivalence-class closure, enumerates the coordinate-permutation group
element by element and checks cell images set-wise, searches readouts by
brute force over explicit truth tables, counts pair-based quantities by
enumerating all unordered pairs of the registered input space, and computes
every trajectory quantity by enumerating **all** subsets of the registered
training pool and averaging exact ``fractions.Fraction`` values.

Route A instead uses canonical labelling, a refinement algebra over
cell-size sums, essential-variable analysis, bitmask/popcount readout
algebra, and Moebius inclusion-exclusion over the lattice of affine
subspaces.  No line of arithmetic is shared.

All arithmetic is exact: ``int`` and ``fractions.Fraction`` only.
"""

import itertools
import json
from fractions import Fraction

N_COORDS = 4
POINTS = tuple(range(1 << N_COORDS))
NONE_SYMBOL = "NONE"

# Registered training pool and held-out set of the AE9 roster.
POOL = (0, 1, 2, 4, 8, 9, 10, 12)
HELD_OUT = (3, 5, 6, 7, 11, 13, 14, 15)
SAMPLE_RANGE = tuple(range(0, 9))
EXACT_MATCH_K = 8
JUNTA_ARITY = 2
TREE_DEPTH = 2


def coord(v, i):
    """Value of coordinate ``i`` (1-based) of point ``v``."""
    return (v >> (N_COORDS - i)) & 1


def coord_mask(i):
    return 1 << (N_COORDS - i)


def make_function(rule):
    return tuple(rule(v) for v in POINTS)


T_XOR12 = make_function(lambda v: coord(v, 1) ^ coord(v, 2))
T_PARITY4 = make_function(
    lambda v: coord(v, 1) ^ coord(v, 2) ^ coord(v, 3) ^ coord(v, 4))
D_X4 = make_function(lambda v: coord(v, 4))
D_ZERO = make_function(lambda v: 0)


def affine_forms():
    """All 32 GF(2)-affine functionals of the four coordinates."""
    out = []
    for a in range(1 << N_COORDS):
        for b in (0, 1):
            vals = []
            for v in POINTS:
                s = b
                for i in range(1, N_COORDS + 1):
                    if (a >> (N_COORDS - i)) & 1:
                        s ^= coord(v, i)
                vals.append(s)
            out.append(((a, b), tuple(vals)))
    out.sort()
    return tuple(out)


AFFINE_FORMS = affine_forms()


# ---------------------------------------------------------------------------
# partitions by explicit equivalence-class closure
# ---------------------------------------------------------------------------

def partition_of(codes):
    """Partition induced by ``codes`` built by explicit class closure.

    ``codes`` maps each point index to an arbitrary hashable code.  Classes
    are grown one point at a time by scanning the classes already built and
    comparing codes; no canonical relabelling is used.
    """
    classes = []
    for v in POINTS:
        placed = False
        for cls in classes:
            if codes[cls[0]] == codes[v]:
                cls.append(v)
                placed = True
                break
        if not placed:
            classes.append([v])
    return tuple(sorted(tuple(sorted(c)) for c in classes))


def cells(part):
    return len(part)


PERMS = tuple(itertools.permutations(range(1, N_COORDS + 1)))


def apply_perm(v, sigma):
    """Point ``w`` with ``coord(w, i) == coord(v, sigma[i - 1])``."""
    w = 0
    for i in range(1, N_COORDS + 1):
        if coord(v, sigma[i - 1]):
            w |= coord_mask(i)
    return w


def invariance_order(part):
    """Order of the stabiliser of ``part`` in the coordinate-permutation group.

    Enumerates all ``4! = 24`` permutations explicitly and checks, cell by
    cell, that the image set is itself a cell of the partition.
    """
    cellset = set(frozenset(c) for c in part)
    count = 0
    for sigma in PERMS:
        ok = True
        for c in part:
            image = frozenset(apply_perm(v, sigma) for v in c)
            if image not in cellset:
                ok = False
                break
        if ok:
            count += 1
    return count


def is_measurable(part, f):
    for c in part:
        first = f[c[0]]
        for v in c:
            if f[v] != first:
                return False
    return True


_JUNTA_CACHE = {}


def junta_functions(k):
    """Every function of at most ``k`` coordinates, as explicit truth tables."""
    if k in _JUNTA_CACHE:
        return _JUNTA_CACHE[k]
    out = []
    for size in range(0, k + 1):
        for support in itertools.combinations(range(1, N_COORDS + 1), size):
            for table in itertools.product((0, 1), repeat=1 << size):
                vals = []
                for v in POINTS:
                    idx = 0
                    for j, i in enumerate(support):
                        idx |= coord(v, i) << (size - 1 - j)
                    vals.append(table[idx])
                out.append(tuple(vals))
    seen = []
    known = set()
    for f in out:
        if f not in known:
            known.add(f)
            seen.append(f)
    result = tuple(sorted(seen))
    _JUNTA_CACHE[k] = result
    return result


BUDGET_CLASS = junta_functions(JUNTA_ARITY)


def readout_arity(part, t):
    """Least ``k`` with a ``k``-junta readout of the partition equal to ``t``.

    Brute-force: for each ``k`` ascending, every function of every coordinate
    subset of that size is built as an explicit truth table and compared with
    ``t`` point by point, then checked for constancy on every cell.
    """
    for k in range(0, N_COORDS + 1):
        for g in junta_functions(k):
            if g == t and is_measurable(part, g):
                return k
    return NONE_SYMBOL


def usable(part, t):
    """Best exact accuracy of the budgeted readout class on the partition."""
    best = Fraction(0)
    for h in BUDGET_CLASS:
        if not is_measurable(part, h):
            continue
        agree = 0
        for v in POINTS:
            if h[v] == t[v]:
                agree += 1
        val = Fraction(agree, len(POINTS))
        if val > best:
            best = val
    return best


def separability(part, t):
    """Fraction of discordant label pairs split by a budgeted measurable readout."""
    usable_hs = [h for h in BUDGET_CLASS if is_measurable(part, h)]
    total = 0
    split = 0
    for x, y in itertools.combinations(POINTS, 2):
        if t[x] == t[y]:
            continue
        total += 1
        for h in usable_hs:
            if h[x] != h[y]:
                split += 1
                break
    if total == 0:
        return Fraction(0)
    return Fraction(split, total)


def mirkin_distance(p1, p2):
    """Pair-counting partition distance, by enumerating all unordered pairs."""
    lab1 = {}
    lab2 = {}
    for idx, c in enumerate(p1):
        for v in c:
            lab1[v] = idx
    for idx, c in enumerate(p2):
        for v in c:
            lab2[v] = idx
    disagree = 0
    total = 0
    for x, y in itertools.combinations(POINTS, 2):
        total += 1
        if (lab1[x] == lab1[y]) != (lab2[x] == lab2[y]):
            disagree += 1
    return Fraction(disagree, total)


def meet_partition(p1, p2):
    lab1 = {}
    lab2 = {}
    for idx, c in enumerate(p1):
        for v in c:
            lab1[v] = idx
    for idx, c in enumerate(p2):
        for v in c:
            lab2[v] = idx
    codes = [(lab1[v], lab2[v]) for v in POINTS]
    return partition_of(codes)


def refinement(p1, p2):
    """(cells merged, cells split) taking ``p1`` to ``p2``, plus the distance."""
    meet = meet_partition(p1, p2)
    return (len(meet) - len(p2), len(meet) - len(p1), mirkin_distance(p1, p2))


def marker_vector(part, t):
    return {
        "CELLS": cells(part),
        "SEPARABILITY": str(separability(part, t)),
        "INVARIANCE": invariance_order(part),
        "READOUT_ARITY": readout_arity(part, t),
        "USABLE": str(usable(part, t)),
    }


_STRUCT_CACHE = {}


def structural_tuple(part, t):
    key = (part, t)
    if key not in _STRUCT_CACHE:
        _STRUCT_CACHE[key] = (
            cells(part), invariance_order(part), readout_arity(part, t))
    return _STRUCT_CACHE[key]


# ---------------------------------------------------------------------------
# trajectories by exhaustive subset averaging
# ---------------------------------------------------------------------------

TRAJECTORIES = {
    "TRAJ_SMOOTH": {"fit_affine": False, "memorise": True,
                    "default": D_ZERO, "target": T_XOR12,
                    "code": "IDENTITY"},
    "TRAJ_JUMP": {"fit_affine": True, "memorise": False,
                  "default": D_X4, "target": T_XOR12, "code": "BASE"},
    "TRAJ_GROK": {"fit_affine": True, "memorise": True,
                  "default": D_X4, "target": T_PARITY4, "code": "BASE"},
}


def version_space(target, subset):
    out = []
    for key, vals in AFFINE_FORMS:
        ok = True
        for v in subset:
            if vals[v] != target[v]:
                ok = False
                break
        if ok:
            out.append((key, vals))
    return out


def committed_base(spec, subset):
    """The learner's committed code map on ``subset``."""
    if not spec["fit_affine"]:
        return spec["default"], False
    vs = version_space(spec["target"], subset)
    if len(vs) == 1:
        return vs[0][1], True
    return spec["default"], False


def predictor(spec, subset):
    base, determined = committed_base(spec, subset)
    pred = list(base)
    if spec["memorise"]:
        for v in subset:
            pred[v] = spec["target"][v]
    return tuple(pred), determined


def code_map(spec, subset):
    base, _ = committed_base(spec, subset)
    if spec["code"] == "IDENTITY":
        return list(POINTS)
    return list(base)


def accuracy_on(pred, target, domain):
    if len(domain) == 0:
        return Fraction(1)
    agree = 0
    for v in domain:
        if pred[v] == target[v]:
            agree += 1
    return Fraction(agree, len(domain))


def trajectory_report(name):
    return trajectory_report_spec(TRAJECTORIES[name])


def trajectory_report_spec(spec):
    target = spec["target"]
    out = {"acc_overall": [], "acc_train": [], "acc_heldout": [],
           "structural_profile": [], "determined_count": []}
    for m in SAMPLE_RANGE:
        subsets = list(itertools.combinations(POOL, m))
        tot_o = Fraction(0)
        tot_t = Fraction(0)
        tot_h = Fraction(0)
        profile = set()
        det = 0
        for subset in subsets:
            pred, determined = predictor(spec, subset)
            if determined:
                det += 1
            tot_o += accuracy_on(pred, target, POINTS)
            tot_t += accuracy_on(pred, target, subset)
            tot_h += accuracy_on(pred, target, HELD_OUT)
            part = partition_of(code_map(spec, subset))
            profile.add(structural_tuple(part, target))
        k = len(subsets)
        out["acc_overall"].append(tot_o / k)
        out["acc_train"].append(tot_t / k)
        out["acc_heldout"].append(tot_h / k)
        out["structural_profile"].append(tuple(sorted(profile, key=repr)))
        out["determined_count"].append(det)
    return out


def spanning_count(ground, m):
    """Number of ``m``-subsets of ``ground`` whose affine span is the whole space."""
    total = 0
    for subset in itertools.combinations(ground, m):
        if affine_rank(subset) == N_COORDS + 1:
            total += 1
    return total


def affine_rank(subset):
    """Rank of {(x, 1) : x in subset} over GF(2), by Gaussian elimination."""
    rows = []
    for v in subset:
        rows.append((v << 1) | 1)
    basis = []
    for r in rows:
        cur = r
        for b in basis:
            hb = b.bit_length() - 1
            if (cur >> hb) & 1:
                cur ^= b
        if cur:
            basis.append(cur)
            basis.sort(reverse=True)
    return len(basis)


def oracle_bundle():
    """Every route-B quantity route A cross-checks, in a deterministic shape."""
    bundle = {"trajectories": {}, "spanning": {}, "markers": {}}
    for name in sorted(TRAJECTORIES):
        rep = trajectory_report(name)
        bundle["trajectories"][name] = {
            "acc_overall": [str(x) for x in rep["acc_overall"]],
            "acc_train": [str(x) for x in rep["acc_train"]],
            "acc_heldout": [str(x) for x in rep["acc_heldout"]],
            "structural_profile": [
                [list(x) for x in prof] for prof in rep["structural_profile"]],
            "determined_count": rep["determined_count"],
        }
    bundle["spanning"] = {str(m): spanning_count(POOL, m) for m in SAMPLE_RANGE}
    named = named_partitions()
    for key in sorted(named):
        part, target = named[key]
        bundle["markers"][key] = marker_vector(part, target)
    return bundle


def named_partitions():
    """The registered partitions route A also reports markers for."""
    ident = partition_of(list(POINTS))
    p_x4 = partition_of(list(D_X4))
    p_xor12 = partition_of(list(T_XOR12))
    p_par4 = partition_of(list(T_PARITY4))
    return {
        "IDENTITY__T_XOR12": (ident, T_XOR12),
        "KER_X4__T_XOR12": (p_x4, T_XOR12),
        "KER_XOR12__T_XOR12": (p_xor12, T_XOR12),
        "KER_X4__T_PARITY4": (p_x4, T_PARITY4),
        "KER_PARITY4__T_PARITY4": (p_par4, T_PARITY4),
        "IDENTITY__T_PARITY4": (ident, T_PARITY4),
    }


def greedy_decision_list(target, subset, depth):
    """Greedy purity-driven decision tree, ties broken by lowest coordinate."""

    def build(points, avail, d):
        if d == 0 or not points or not avail:
            ones = sum(1 for v in points if target[v] == 1)
            zeros = len(points) - ones
            return ("leaf", 1 if ones > zeros else 0)
        best = None
        for i in sorted(avail):
            gain = 0
            for bit in (0, 1):
                grp = [v for v in points if coord(v, i) == bit]
                ones = sum(1 for v in grp if target[v] == 1)
                gain += max(ones, len(grp) - ones)
            if best is None or gain > best[0]:
                best = (gain, i)
        i = best[1]
        rest = tuple(sorted(set(avail) - {i}))
        sub = {}
        for bit in (0, 1):
            grp = [v for v in points if coord(v, i) == bit]
            sub[bit] = build(grp, rest, d - 1)
        return ("node", i, sub[0], sub[1])

    tree = build(list(subset), tuple(range(1, N_COORDS + 1)), depth)

    def evaluate(node, v):
        if node[0] == "leaf":
            return node[1]
        return evaluate(node[2] if coord(v, node[1]) == 0 else node[3], v)

    return tuple(evaluate(tree, v) for v in POINTS)


def main():
    bundle = oracle_bundle()
    print(json.dumps(bundle, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
