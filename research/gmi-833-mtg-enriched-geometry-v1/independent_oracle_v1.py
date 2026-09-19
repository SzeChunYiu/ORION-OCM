#!/usr/bin/env python3
"""Route B independent oracle for gmi-833-mtg-enriched-geometry-v1.

Imports NOTHING from route A.  Closure by explicit simple-path enumeration
(all simple paths, Minkowski-sum of edge burdens, then Pareto reduction with the
oracle's own dominance test); generated topology by explicit union closure over
the finite subset lattice.  Exact arithmetic only; no floats; no bare assert.

Run:  python3 -I -B independent_oracle_v1.py   (writes ORACLE_RESULT_V1.json)
"""
from __future__ import annotations

import json
import os
from fractions import Fraction
from itertools import permutations, product
from typing import Dict, FrozenSet, List, Optional, Sequence, Set, Tuple

ORACLE_SCHEMA = "GMI_833_MTG_ENRICHED_GEOMETRY_ORACLE_RESULT_V1"
ORACLE_ROUTE = "SIMPLE_PATH_ENUMERATION_AND_EXPLICIT_UNION_CLOSURE"
ORACLE_RECEIPT_NAME = "ORACLE_RESULT_V1.json"

QVec = Tuple[Fraction, ...]
QSet = Tuple[QVec, ...]
QEdge = Tuple[str, str]

# Registered fixture, duplicated as literals (the test cross-checks it against route A).
O_NODES: Tuple[str, ...] = ("A", "B", "C", "D", "E")
O_DIM = 2
O_EDGES: Tuple[Tuple[str, str, Tuple[Tuple[str, ...], ...]], ...] = (
    ("A", "B", (("0", "0"),)),
    ("B", "C", (("1", "1"),)),
    ("A", "C", (("5", "0"), ("0", "5"))),
    ("C", "A", (("6", "6"),)),
    ("A", "E", (("2", "1/2"),)),
    ("E", "C", (("1/2", "1/4"),)),
)
O_BUDGET_LO, O_BUDGET_HI = 1, 8
O_LAMBDAS: Tuple[Tuple[str, ...], ...] = (("2", "1"), ("1", "3"), ("1/2", "2"))
O_E = "1/4"
O_WEIGHTS: Tuple[Tuple[str, ...], ...] = (("1", "1"), ("1", "3"), ("3", "1"))


class OracleError(ValueError):
    pass


def ocheck(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError("ORACLE:" + msg)


def q(x: object) -> Fraction:
    if isinstance(x, bool) or isinstance(x, float):
        raise OracleError("FLOAT_REJECTED")
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return Fraction(x)
    if isinstance(x, str) and x and "." not in x:
        return Fraction(x)
    raise OracleError("BAD_NUMBER")


def qvec(values: Sequence[object]) -> QVec:
    v = tuple(q(x) for x in values)
    if not v or min(v) < 0:
        raise OracleError("BAD_VECTOR")
    return v


def weakly_below(u: QVec, v: QVec) -> bool:
    if len(u) != len(v):
        raise OracleError("DIM")
    for i in range(len(u)):
        if u[i] > v[i]:
            return False
    return True


def minimal(vectors: Sequence[QVec]) -> QSet:
    """Oracle Pareto reduction: keep v unless a different u lies weakly below it."""
    pool = sorted(set(vectors))
    keep: List[QVec] = []
    for v in pool:
        dominated = False
        for u in pool:
            if u == v:
                continue
            if weakly_below(u, v):
                dominated = True
                break
        if not dominated:
            keep.append(v)
    return tuple(keep)


def o_choice(a: QSet, b: QSet) -> QSet:
    return minimal(list(a) + list(b))


def o_compose(a: QSet, b: QSet) -> QSet:
    if len(a) == 0 or len(b) == 0:
        return ()
    sums: List[QVec] = []
    for x in a:
        for y in b:
            if len(x) != len(y):
                raise OracleError("DIM")
            sums.append(tuple(x[i] + y[i] for i in range(len(x))))
    return minimal(sums)


def o_identity(dim: int) -> QSet:
    return (tuple([Fraction(0)] * dim),)


def at_least_as_good(a: QSet, b: QSet) -> bool:
    """A ⊑ B: for every a there is b weakly below it."""
    for x in a:
        found = False
        for y in b:
            if weakly_below(y, x):
                found = True
                break
        if not found:
            return False
    return True


def o_grid_universe() -> Tuple[QSet, ...]:
    pts = [tuple(Fraction(c) for c in p) for p in product(range(3), repeat=2)]
    seen: Set[QSet] = set()
    for mask in range(1 << len(pts)):
        seen.add(minimal([pts[i] for i in range(len(pts)) if (mask >> i) & 1]))
    return tuple(sorted(seen, key=lambda s: (len(s), s)))


# ---------------- graph and simple-path closure ------------------------------
def o_graph() -> Dict[QEdge, QSet]:
    edges: Dict[QEdge, QSet] = {}
    for i, j, vecs in O_EDGES:
        edges[(i, j)] = minimal([qvec(v) for v in vecs])
    return edges


def o_budgets() -> Tuple[QVec, ...]:
    return tuple(qvec(p) for p in product(range(O_BUDGET_LO, O_BUDGET_HI + 1), repeat=O_DIM))


def simple_paths(nodes: Sequence[str], edges: Dict[QEdge, QSet], src: str, dst: str) -> List[List[QEdge]]:
    """All simple paths src->dst as edge lists (for src==dst: the empty path and all simple cycles)."""
    out: List[List[QEdge]] = []
    succ: Dict[str, List[str]] = {n: [] for n in nodes}
    for (i, j) in sorted(edges):
        succ[i].append(j)

    def walk(current: str, visited: Set[str], path: List[QEdge]) -> None:
        for nxt in succ[current]:
            edge = (current, nxt)
            if nxt == dst:
                out.append(path + [edge])
                continue
            if nxt in visited:
                continue
            walk(nxt, visited | {nxt}, path + [edge])

    if src == dst:
        out.append([])
    walk(src, {src}, [])
    return out


def closure_by_paths(nodes: Sequence[str], edges: Dict[QEdge, QSet], dim: int) -> Tuple[Dict[QEdge, QSet], Dict[QEdge, Dict[QVec, int]]]:
    h: Dict[QEdge, QSet] = {}
    lengths: Dict[QEdge, Dict[QVec, int]] = {}
    for s in nodes:
        for t in nodes:
            burdens: List[Tuple[QVec, int]] = []
            for path in simple_paths(nodes, edges, s, t):
                if not path:
                    burdens.append((tuple([Fraction(0)] * dim), 0))
                    continue
                for combo in product(*[edges[e] for e in path]):
                    total = tuple([Fraction(0)] * dim)
                    for v in combo:
                        total = tuple(total[i] + v[i] for i in range(dim))
                    burdens.append((total, len(path)))
            front = minimal([b for b, _ in burdens])
            h[(s, t)] = front
            d: Dict[QVec, int] = {}
            for b, length in burdens:
                if b in front and (b not in d or length < d[b]):
                    d[b] = length
            lengths[(s, t)] = d
    return h, lengths


# ---------------- balls and union-closure topology ---------------------------
def o_ball(nodes: Sequence[str], h: Dict[QEdge, QSet], src: str, b: QVec) -> FrozenSet[str]:
    members = []
    for t in nodes:
        for v in h[(src, t)]:
            if all(v[i] < b[i] for i in range(len(b))):
                members.append(t)
                break
    return frozenset(members)


def raw_family_is_basis(family: Set[FrozenSet[str]]) -> bool:
    """Oracle basis test: each point of any pairwise intersection has a family member around it inside."""
    for u in family:
        for v in family:
            w = u & v
            for x in w:
                ok = False
                for z in family:
                    if x in z and z.issubset(w):
                        ok = True
                        break
                if not ok:
                    return False
    return True


def union_closure_topology(nodes: Sequence[str], h: Dict[QEdge, QSet], budgets: Sequence[QVec]) -> Tuple[FrozenSet[FrozenSet[str]], int, bool]:
    """Smallest topology containing the registered balls, by explicit closure:
    intersection-close the ball family (plus the whole set), then union-close.
    Returns (opens, distinct raw balls incl. empty, raw family is a basis)."""
    family: Set[FrozenSet[str]] = {frozenset()}
    for x in nodes:
        for b in budgets:
            family.add(o_ball(nodes, h, x, b))
    n_basis = len(family)
    raw_basis = raw_family_is_basis(family)
    raw_copy = set(family)
    family.add(frozenset(nodes))
    while True:
        added: Set[FrozenSet[str]] = set()
        for u in family:
            for v in family:
                w = u & v
                if w not in family:
                    added.add(w)
        if not added:
            break
        family |= added
    while True:
        added = set()
        for u in family:
            for v in family:
                w = u | v
                if w not in family:
                    added.add(w)
        if not added:
            break
        family |= added
    ocheck(frozenset(nodes) in family and frozenset() in family, "WHOLE_OR_EMPTY_NOT_OPEN")
    for u in family:
        for v in family:
            ocheck((u & v) in family, "INTERSECTION_NOT_OPEN")
            ocheck((u | v) in family, "UNION_NOT_OPEN")
    if raw_basis:
        # union closure of the raw balls alone must already give the same topology
        raw_union = set(raw_copy)
        while True:
            added = set()
            for u in raw_union:
                for v in raw_union:
                    w = u | v
                    if w not in raw_union:
                        added.add(w)
            if not added:
                break
            raw_union |= added
        ocheck(frozenset(raw_union) == frozenset(family), "RAW_BASIS_UNION_CLOSURE_DIFFERS")
    return frozenset(family), n_basis, raw_basis


# ---------------- transformations ---------------------------------------------
def o_relabel(edges: Dict[QEdge, QSet], mapping: Dict[str, str]) -> Dict[QEdge, QSet]:
    return {(mapping[i], mapping[j]): fr for (i, j), fr in edges.items()}


def o_scale(lam: QVec, edges: Dict[QEdge, QSet]) -> Dict[QEdge, QSet]:
    return {e: minimal([tuple(lam[i] * v[i] for i in range(len(v))) for v in fr]) for e, fr in edges.items()}


def o_perturb(edges: Dict[QEdge, QSet], delta: Dict[QEdge, QVec]) -> Dict[QEdge, QSet]:
    out: Dict[QEdge, QSet] = {}
    for e, fr in edges.items():
        out[e] = minimal([tuple(max(Fraction(0), v[i] + delta[e][i]) for i in range(len(v))) for v in fr])
    return out


def o_patterns(edge_keys: Sequence[QEdge], dim: int, e: Fraction) -> Tuple[List[Dict[QEdge, QVec]], int]:
    raw: List[Dict[QEdge, QVec]] = []
    for s in product((-e, Fraction(0), e), repeat=dim):
        raw.append({k: tuple(s) for k in edge_keys})
    for t in product((-e, e), repeat=len(edge_keys)):
        raw.append({k: tuple([t[i]] * dim) for i, k in enumerate(edge_keys)})
    distinct: List[Dict[QEdge, QVec]] = []
    keys: Set[Tuple[Tuple[QEdge, QVec], ...]] = set()
    for p in raw:
        k = tuple(sorted(p.items()))
        if k not in keys:
            keys.add(k)
            distinct.append(p)
    return distinct, len(raw)


def o_member(h: Dict[QEdge, QSet], s: str, t: str, b: QVec) -> bool:
    return any(all(v[i] < b[i] for i in range(len(b))) for v in h[(s, t)])


def o_classify(front: QSet, lengths: Dict[QVec, int], b: QVec, e: Fraction) -> Tuple[str, bool, Optional[Fraction], Optional[int], Optional[Fraction]]:
    witnesses = [v for v in front if all(v[i] < b[i] for i in range(len(b)))]
    if witnesses:
        best_slack = None
        best_margin = None
        best_len = None
        for v in witnesses:
            margin = min(b[i] - v[i] for i in range(len(b)))
            slack = margin - lengths[v] * e
            if best_slack is None or slack > best_slack:
                best_slack, best_margin, best_len = slack, margin, lengths[v]
        cls = "STABLE_MEMBER" if best_slack > 0 else "UNDETERMINED"  # type: ignore[operator]
        return cls, True, best_margin, best_len, best_slack
    for v in front:
        if not any(v[i] - b[i] > lengths[v] * e for i in range(len(b))):
            return "UNDETERMINED", False, None, None, None
    return "STABLE_NONMEMBER", False, None, None, None


def o_scalar(front: QSet, w: QVec) -> Optional[Fraction]:
    if not front:
        return None
    return min(sum(v[i] * w[i] for i in range(len(w))) for v in front)


# ---------------- serialization (same conventions as route A, own code) ---------
def s_frac(x: Fraction) -> str:
    f = Fraction(x)
    return str(f.numerator) + "/" + str(f.denominator)


def s_vec(v: QVec) -> List[str]:
    return [s_frac(x) for x in v]


def s_set(fr: QSet) -> List[List[str]]:
    return [s_vec(v) for v in fr]


def s_closure(h: Dict[QEdge, QSet]) -> Dict[str, List[List[str]]]:
    return {i + "->" + j: s_set(fr) for (i, j), fr in h.items()}


def s_lengths(lengths: Dict[QEdge, Dict[QVec, int]]) -> Dict[str, List[List[object]]]:
    return {i + "->" + j: [[s_vec(v), d[v]] for v in sorted(d)] for (i, j), d in lengths.items()}


def s_opens(opens: FrozenSet[FrozenSet[str]]) -> List[List[str]]:
    return sorted((sorted(u) for u in opens), key=lambda u: (len(u), u))


def s_edges(edges: Dict[QEdge, QSet]) -> Dict[str, List[List[str]]]:
    return {i + "->" + j: s_set(fr) for (i, j), fr in edges.items()}


def oracle_text(obj: Dict[str, object]) -> str:
    return json.dumps(obj, indent=1, sort_keys=True) + "\n"


# ---------------- main oracle computation --------------------------------------
def build_oracle() -> Dict[str, object]:
    counts: Dict[str, int] = {}
    witnesses: Dict[str, object] = {}
    checks: Dict[str, bool] = {}

    universe = o_grid_universe()
    counts["grid_universe_antichains"] = len(universe)
    empty: QSet = ()
    counts["empty_dominated_by_every_antichain_checks"] = len(universe)
    checks["empty_antichain_dominated_by_every_antichain"] = all(at_least_as_good(empty, b) for b in universe)
    counts["dominates_empty_only_if_empty_checks"] = len(universe)
    checks["antichain_dominated_by_empty_only_if_empty"] = all(at_least_as_good(a, empty) == (a == empty) for a in universe)
    counts["dominance_reflexive_checks"] = len(universe)
    checks["dominance_reflexive"] = all(at_least_as_good(a, a) for a in universe)
    counts["dominance_pairs_evaluated"] = len(universe) ** 2
    related = 0
    trans_ok = True
    anti_ok = True
    mono_checks = 0
    mono_ok = True
    for a in universe:
        for b in universe:
            ab = at_least_as_good(a, b)
            if ab:
                related += 1
                if at_least_as_good(b, a) and a != b:
                    anti_ok = False
                for c in universe:
                    if at_least_as_good(b, c) and not at_least_as_good(a, c):
                        trans_ok = False
                    mono_checks += 2
                    if not at_least_as_good(o_compose(a, c), o_compose(b, c)):
                        mono_ok = False
                    if not at_least_as_good(o_compose(c, a), o_compose(c, b)):
                        mono_ok = False
    counts["dominance_related_pairs"] = related
    counts["dominance_transitive_triples_checked"] = len(universe) ** 3
    checks["dominance_transitive"] = trans_ok
    counts["dominance_antisymmetric_pairs_checked"] = len(universe) ** 2
    checks["dominance_antisymmetric_on_universe"] = anti_ok
    counts["composition_monotone_checks"] = mono_checks
    checks["composition_monotone_each_argument"] = mono_ok
    ub_ok = True
    least_ok = True
    least_checks = 0
    for a in universe:
        for b in universe:
            j = o_choice(a, b)
            if not (at_least_as_good(a, j) and at_least_as_good(b, j)):
                ub_ok = False
            for c in universe:
                least_checks += 1
                if at_least_as_good(a, c) and at_least_as_good(b, c) and not at_least_as_good(j, c):
                    least_ok = False
    counts["join_upper_bound_checks"] = 2 * len(universe) ** 2
    checks["choice_is_upper_bound"] = ub_ok
    counts["join_least_upper_bound_checks"] = least_checks
    checks["choice_is_least_upper_bound"] = least_ok

    nodes = O_NODES
    edges = o_graph()
    h, lengths = closure_by_paths(nodes, edges, O_DIM)
    counts["graph_nodes"] = len(nodes)
    counts["graph_edges"] = len(edges)
    counts["graph_ordered_pairs"] = len(nodes) ** 2
    witnesses["closure"] = s_closure(h)
    witnesses["closure_min_path_lengths"] = s_lengths(lengths)
    witnesses["registered_edges"] = s_edges(edges)

    bad = 0
    for m in nodes:
        for n in nodes:
            for p in nodes:
                if not at_least_as_good(o_compose(h[(m, n)], h[(n, p)]), h[(m, p)]):
                    bad += 1
    counts["enrichment_triples_checked"] = len(nodes) ** 3
    checks["enrichment_lax_composition_law"] = bad == 0
    counts["enrichment_identity_nodes_checked"] = len(nodes)
    checks["enrichment_identity_law"] = all(at_least_as_good(o_identity(O_DIM), h[(m, m)]) for m in nodes)
    strict = None
    equal = None
    n_strict = 0
    n_equal = 0
    for m in nodes:
        for n in nodes:
            for p in nodes:
                comp = o_compose(h[(m, n)], h[(n, p)])
                if comp and at_least_as_good(comp, h[(m, p)]) and not at_least_as_good(h[(m, p)], comp):
                    n_strict += 1
                    if strict is None and len({m, n, p}) == 3:
                        strict = (m, n, p, comp, h[(m, p)])
                if comp and comp == h[(m, p)] and len({m, n, p}) == 3:
                    n_equal += 1
                    if equal is None:
                        equal = (m, n, p, comp)
    counts["enrichment_triples_composite_nonempty_strictly_worse"] = n_strict
    counts["enrichment_triples_distinct_nodes_composite_equal"] = n_equal
    ocheck(strict is not None and equal is not None, "WITNESSES_MISSING")
    witnesses["enrichment_strict_triple"] = {
        "triple": list(strict[:3]), "composite": s_set(strict[3]), "closure": s_set(strict[4]),  # type: ignore[index]
    }
    witnesses["enrichment_equal_triple"] = {
        "triple": list(equal[:3]), "composite_equals_closure": s_set(equal[3]),  # type: ignore[index]
    }

    budgets = o_budgets()
    counts["budget_vectors"] = len(budgets)
    opens, n_basis, raw_is_basis = union_closure_topology(nodes, h, budgets)
    counts["basis_balls_including_empty"] = n_basis
    counts["open_sets"] = len(opens)
    witnesses["open_sets"] = s_opens(opens)
    checks["registered_ball_family_is_basis_original"] = raw_is_basis

    total = 0
    ok_h = 0
    ok_t = 0
    open_counts: Set[int] = set()
    for perm in permutations(nodes):
        total += 1
        mapping = {nodes[i]: perm[i] for i in range(len(nodes))}
        inverse = {v: k for k, v in mapping.items()}
        h2, _ = closure_by_paths(nodes, o_relabel(edges, mapping), O_DIM)
        if {(inverse[i], inverse[j]): fr for (i, j), fr in h2.items()} == h:
            ok_h += 1
        o2, _, _ = union_closure_topology(nodes, h2, budgets)
        open_counts.add(len(o2))
        if frozenset(frozenset(inverse[x] for x in u) for u in o2) == opens:
            ok_t += 1
    counts["relabelings"] = total
    counts["relabel_closure_equalities"] = ok_h
    counts["relabel_topology_equalities"] = ok_t
    checks["relabeling_closure_transport_equal_all"] = ok_h == total == 120
    checks["relabeling_topology_transport_equal_all"] = ok_t == total == 120
    checks["relabeling_open_set_count_invariant"] = open_counts == {len(opens)}

    # null: misaligned transport (own generator; same constants and seed as route A so
    # the 200 draws are a shared quantity, but written independently)
    autos = 0
    for perm in permutations(nodes):
        mp = {nodes[i]: perm[i] for i in range(len(nodes))}
        if o_relabel(edges, mp) == edges:
            autos += 1
    counts["graph_automorphisms"] = autos
    checks["graph_automorphism_group_trivial"] = autos == 1
    state = (0x833 * 0x9E3779B97F4A7C15 + 1) % (1 << 64)

    def next_high_bits() -> int:
        nonlocal state
        state = (6364136223846793005 * state + 1442695040888963407) % (1 << 64)
        return state >> 33

    def draw_perm(n: int) -> List[int]:
        arr = list(range(n))
        i = n - 1
        while i > 0:
            j = next_high_bits() % (i + 1)
            arr[i], arr[j] = arr[j], arr[i]
            i -= 1
        return arr

    n_draws = 0
    eq_closure = 0
    eq_topology = 0
    while n_draws < 200:
        sp = draw_perm(len(nodes))
        tp = draw_perm(len(nodes))
        sigma = {nodes[i]: nodes[sp[i]] for i in range(len(nodes))}
        tau = {nodes[i]: nodes[tp[i]] for i in range(len(nodes))}
        if all(tau[sigma[x]] == x for x in nodes):
            continue  # tau == sigma^-1 is the true law; excluded
        n_draws += 1
        hs, _ = closure_by_paths(nodes, o_relabel(edges, sigma), O_DIM)
        if {(tau[i], tau[j]): fr for (i, j), fr in hs.items()} == h:
            eq_closure += 1
        os_, _, _ = union_closure_topology(nodes, hs, budgets)
        if frozenset(frozenset(tau[x] for x in u) for u in os_) == opens:
            eq_topology += 1
    counts["null_draws"] = n_draws
    counts["null_closure_equalities"] = eq_closure
    counts["null_topology_equalities"] = eq_topology
    checks["null_zero_closure_equalities"] = eq_closure == 0
    checks["null_topology_equalities_below_true_law"] = eq_topology < n_draws

    lambdas = tuple(qvec(l) for l in O_LAMBDAS)
    counts["lambdas"] = len(lambdas)
    rp = 0
    rp_ok = 0
    rt_ok = 0
    fixed_rows = []
    differing = 0
    for lam in lambdas:
        hl, _ = closure_by_paths(nodes, o_scale(lam, edges), O_DIM)
        for key in h:
            rp += 1
            if hl[key] == minimal([tuple(lam[i] * v[i] for i in range(O_DIM)) for v in h[key]]):
                rp_ok += 1
        ol, _, ol_basis = union_closure_topology(nodes, hl, tuple(tuple(lam[i] * b[i] for i in range(O_DIM)) for b in budgets))
        if ol == opens and ol_basis == raw_is_basis:
            rt_ok += 1
        ofix, _, ofix_basis = union_closure_topology(nodes, hl, budgets)
        d = ofix != opens
        if d:
            differing += 1
        fixed_rows.append({
            "lambda": s_vec(lam),
            "open_sets_fixed_grid": len(ofix),
            "open_sets_original": len(opens),
            "differs": d,
            "raw_ball_family_is_basis": ofix_basis,
            "open_only_under_fixed_grid_rescaling": sorted((sorted(u) for u in ofix - opens), key=lambda u: (len(u), u)),
            "open_only_in_original": sorted((sorted(u) for u in opens - ofix), key=lambda u: (len(u), u)),
        })
    counts["rescale_closure_pair_checks"] = rp
    counts["rescale_closure_pair_equalities"] = rp_ok
    counts["rescale_topology_equalities"] = rt_ok
    counts["fixed_grid_lambdas_differing"] = differing
    checks["rescaling_commutes_with_closure"] = rp == rp_ok
    checks["rescaled_budgets_generate_same_topology"] = rt_ok == len(lambdas)
    witnesses["fixed_budget_grid_rescaling"] = fixed_rows

    e = q(O_E)
    edge_keys = tuple(sorted(edges))
    patterns, registered = o_patterns(edge_keys, O_DIM, e)
    counts["perturbation_patterns_registered"] = registered
    counts["perturbation_patterns_distinct"] = len(patterns)
    cls_of: Dict[Tuple[QVec, str, str], str] = {}
    mem_of: Dict[Tuple[QVec, str, str], bool] = {}
    cc = {"STABLE_MEMBER": 0, "STABLE_NONMEMBER": 0, "UNDETERMINED": 0}
    tight = None
    for b in budgets:
        for m in nodes:
            for n in nodes:
                cls, mem, margin, length, slack = o_classify(h[(m, n)], lengths[(m, n)], b, e)
                cls_of[(b, m, n)] = cls
                mem_of[(b, m, n)] = mem
                cc[cls] += 1
                if cls == "STABLE_MEMBER" and m != n and (tight is None or slack < tight[0]):  # type: ignore[operator]
                    tight = (slack, margin, length, b, m, n)
    counts["perturbation_cells"] = len(cls_of)
    counts["cells_stable_member"] = cc["STABLE_MEMBER"]
    counts["cells_stable_nonmember"] = cc["STABLE_NONMEMBER"]
    counts["cells_undetermined"] = cc["UNDETERMINED"]
    ocheck(tight is not None, "NO_TIGHT_CELL")
    stable_cells = [k for k, v in cls_of.items() if v != "UNDETERMINED"]
    flips = 0
    sc = 0
    h_plus, _ = closure_by_paths(nodes, o_perturb(edges, {k: (e,) * O_DIM for k in edge_keys}), O_DIM)
    h_minus, _ = closure_by_paths(nodes, o_perturb(edges, {k: (-e,) * O_DIM for k in edge_keys}), O_DIM)
    sandwich = 0
    sandwich_ok = True
    for pat in patterns:
        hp, _ = closure_by_paths(nodes, o_perturb(edges, pat), O_DIM)
        for (b, m, n) in stable_cells:
            sc += 1
            if o_member(hp, m, n, b) != mem_of[(b, m, n)]:
                flips += 1
        for b in budgets:
            for m in nodes:
                for n in nodes:
                    sandwich += 1
                    mem = o_member(hp, m, n, b)
                    if (o_member(h_plus, m, n, b) and not mem) or (mem and not o_member(h_minus, m, n, b)):
                        sandwich_ok = False
    counts["stable_cell_pattern_checks"] = sc
    counts["stable_cell_flips"] = flips
    checks["no_stable_cell_flips_under_registered_patterns"] = flips == 0
    counts["box_sandwich_checks"] = sandwich
    checks["pattern_membership_sandwiched_by_box_extremes"] = sandwich_ok
    box_stable = 0
    subset_ok = True
    for (b, m, n), cls in cls_of.items():
        mem = mem_of[(b, m, n)]
        bs = (mem and o_member(h_plus, m, n, b)) or ((not mem) and not o_member(h_minus, m, n, b))
        if bs:
            box_stable += 1
        if cls != "UNDETERMINED" and not bs:
            subset_ok = False
    counts["cells_box_stable"] = box_stable
    checks["frozen_stable_cells_subset_of_box_stable_cells"] = subset_ok

    # counterexample to the frozen frontier-based non-membership criterion (own path enumeration)
    ce_nodes = ("M", "a", "b", "N")
    ce_edges: Dict[QEdge, QSet] = {
        ("M", "N"): (qvec(("10", "0")),),
        ("M", "a"): (qvec(("41/12", "0")),),
        ("a", "b"): (qvec(("41/12", "0")),),
        ("b", "N"): (qvec(("41/12", "0")),),
    }
    ce_b = qvec(("155/16", "1"))
    ce_h, ce_len = closure_by_paths(ce_nodes, ce_edges, O_DIM)
    ce_cls, ce_mem, _, _, _ = o_classify(ce_h[("M", "N")], ce_len[("M", "N")], ce_b, e)
    ce_minus, _ = closure_by_paths(ce_nodes, o_perturb(ce_edges, {k: (-e,) * O_DIM for k in ce_edges}), O_DIM)
    ce_plus, _ = closure_by_paths(ce_nodes, o_perturb(ce_edges, {k: (e,) * O_DIM for k in ce_edges}), O_DIM)
    ce_after = o_member(ce_minus, "M", "N", ce_b)
    ce_box = (ce_mem and o_member(ce_plus, "M", "N", ce_b)) or ((not ce_mem) and not ce_after)
    witnesses["frozen_nonmember_counterexample"] = {
        "frontier_M_N": [[str(x) for x in v] for v in ce_h[("M", "N")]],
        "frozen_classification": ce_cls,
        "member_before": ce_mem,
        "member_after_all_edges_minus_e": ce_after,
        "frontier_after_all_edges_minus_e": [[str(x) for x in v] for v in ce_minus[("M", "N")]],
        "box_criterion_stable": ce_box,
    }
    checks["frozen_nonmember_criterion_refuted_by_counterexample"] = (ce_cls == "STABLE_NONMEMBER") and (not ce_mem) and ce_after
    checks["box_criterion_marks_counterexample_undetermined"] = not ce_box
    t_slack, t_margin, t_len, t_b, t_m, t_n = tight  # type: ignore[misc]
    witnesses["tightest_stable_member_cell"] = {
        "budget": s_vec(t_b), "source": t_m, "target": t_n,
        "best_margin": s_frac(t_margin), "witness_path_length": t_len,
        "slack_margin_minus_L_times_e": s_frac(t_slack),
    }
    h_host, _ = closure_by_paths(nodes, o_perturb(edges, {k: (t_margin,) * O_DIM for k in edge_keys}), O_DIM)
    witnesses["margin_exceeding_perturbation_hostile"] = {
        "cell": {"budget": s_vec(t_b), "source": t_m, "target": t_n},
        "uniform_delta": s_frac(t_margin),
        "registered_e": s_frac(e),
        "member_before": mem_of[(t_b, t_m, t_n)],
        "member_after": o_member(h_host, t_m, t_n, t_b),
    }
    checks["margin_exceeding_perturbation_flips"] = o_member(h_host, t_m, t_n, t_b) != mem_of[(t_b, t_m, t_n)]

    weights = tuple(qvec(w) for w in O_WEIGHTS)
    counts["scalar_weights"] = len(weights)
    table: Dict[str, Dict[str, str]] = {}
    for w in weights:
        row: Dict[str, str] = {}
        for (i, j) in sorted(h):
            d = o_scalar(h[(i, j)], w)
            row[i + "->" + j] = "INF" if d is None else s_frac(d)
        table[s_frac(w[0]) + "," + s_frac(w[1])] = row
    witnesses["scalar_distances"] = table
    fin = 0
    fin_ok = True
    inf = 0
    inf_ok = True
    for a in range(len(weights)):
        for c in range(a + 1, len(weights)):
            w, w2 = weights[a], weights[c]
            for key, fr in h.items():
                dw, dw2 = o_scalar(fr, w), o_scalar(fr, w2)
                if dw is None or dw2 is None:
                    inf += 1
                    if not (dw is None and dw2 is None and not fr):
                        inf_ok = False
                    continue
                fin += 1
                bound = max(abs(sum((w[i] - w2[i]) * v[i] for i in range(O_DIM))) for v in fr)
                if abs(dw - dw2) > bound:
                    fin_ok = False
    counts["scalar_weight_pairs"] = 3
    counts["scalar_finite_lipschitz_checks"] = fin
    counts["scalar_infinite_pair_checks"] = inf
    checks["scalar_projection_lipschitz_bound"] = fin_ok
    checks["scalar_infinite_pairs_stay_infinite"] = inf_ok

    for k, v in counts.items():
        ocheck(isinstance(v, int) and not isinstance(v, bool), "NON_INT_COUNT:" + k)
    green = all(checks.values())
    return {
        "schema": ORACLE_SCHEMA,
        "route": ORACLE_ROUTE,
        "counts": counts,
        "witnesses": witnesses,
        "checks": checks,
        "status": "GREEN" if green else "RED",
    }


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    res = build_oracle()
    with open(os.path.join(here, ORACLE_RECEIPT_NAME), "w", encoding="utf-8") as fh:
        fh.write(oracle_text(res))
    print(json.dumps({"schema": ORACLE_SCHEMA, "route": ORACLE_ROUTE, "status": res["status"],
                      "open_sets": res["counts"]["open_sets"]}, sort_keys=True, separators=(",", ":")))  # type: ignore[index]
    return 0 if res["status"] == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
