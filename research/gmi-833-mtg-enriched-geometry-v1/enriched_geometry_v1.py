#!/usr/bin/env python3
"""Route A executor for gmi-833-mtg-enriched-geometry-v1.

Ordered-monoid enrichment (ENR-1) and topology stability (STAB-1, STAB-2) of the
finite Pareto transform algebra at registered finite scope.

Route A computes the transform closure by Floyd-Warshall over the Pareto (+,*)
algebra and the generated topology by basis generation.  Exact arithmetic only
(int / fractions.Fraction); float inputs are rejected.  No bare ``assert`` is
used anywhere so that ``python3 -O`` behaves byte-identically.

Run:  python3 -I -B enriched_geometry_v1.py   (writes RESULT_V1.json next to itself)
"""
from __future__ import annotations

import hashlib
import json
import os
from fractions import Fraction
from itertools import permutations, product
from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence, Tuple

SCHEMA = "GMI_833_MTG_ENRICHED_GEOMETRY_RESULT_V1"
CLAIM_CEILING = (
    "GMI_833_MTG_ORDERED_MONOID_ENRICHMENT_AND_TOPOLOGY_STABILITY_AT_REGISTERED_FINITE_SCOPE"
)
FORBIDDEN_PROMOTIONS = (
    "COMPLETE_QUANTALE_ENRICHMENT_PROVED",
    "UNIVERSAL_INTELLIGENCE_SPACE_TOPOLOGY_PROVED",
    "TOPOLOGY_STABLE_UNDER_ARBITRARY_PERTURBATION",
    "TOPOLOGY_IS_HAUSDORFF_PROVED",
    "TOPOLOGY_IS_MANIFOLD_PROVED",
    "COMPLETE_GMI",
)
RESULTS = ("ENR-1", "STAB-1", "STAB-2")
TERMINAL = "FINITE_ORDERED_MONOID_ENRICHMENT_VERIFIED"
ROUTE = "FLOYD_WARSHALL_CLOSURE_AND_BASIS_GENERATION"
RECEIPT_NAME = "RESULT_V1.json"
COMPLETE_QUANTALE_WOULD_ADDITIONALLY_REQUIRE = (
    "JOINS_OF_ARBITRARY_INFINITE_FAMILIES_OF_ANTICHAINS_EXIST",
    "COMPOSITION_PRESERVES_ARBITRARY_JOINS_IN_EACH_ARGUMENT",
    "CLOSURE_DEFINED_AS_LEAST_FIXPOINT_OVER_INFINITE_PATH_FAMILIES",
    "WELL_DEFINEDNESS_OF_PARETO_MINIMA_FOR_INFINITE_SUBSETS_OF_Q_D_NONNEG",
)

Vec = Tuple[Fraction, ...]
Antichain = Tuple[Vec, ...]
Edge = Tuple[str, str]
Closure = Dict[Edge, Antichain]
Lengths = Dict[Edge, Dict[Vec, int]]
Opens = FrozenSet[FrozenSet[str]]

# ----------------------------------------------------------------------------
# Registered fixture (exact rationals as strings; parsed by F()).
# Parent 4-node witness (A,B,C,D) plus node E with a directed 2-edge alternative
# A->E->C whose burden (5/2,3/4) is Pareto-incomparable with every other A->C path.
# ----------------------------------------------------------------------------
NODES: Tuple[str, ...] = ("A", "B", "C", "D", "E")
DIM = 2
EDGE_SPEC: Tuple[Tuple[str, str, Tuple[Tuple[str, ...], ...]], ...] = (
    ("A", "B", (("0", "0"),)),
    ("B", "C", (("1", "1"),)),
    ("A", "C", (("5", "0"), ("0", "5"))),
    ("C", "A", (("6", "6"),)),
    ("A", "E", (("2", "1/2"),)),
    ("E", "C", (("1/2", "1/4"),)),
)
BUDGET_RANGE = (1, 8)  # inclusive integer grid per coordinate, as in parent P04
LAMBDAS: Tuple[Tuple[str, ...], ...] = (("2", "1"), ("1", "3"), ("1/2", "2"))
PERTURBATION_E = "1/4"
WEIGHTS: Tuple[Tuple[str, ...], ...] = (("1", "1"), ("1", "3"), ("3", "1"))


class GeometryError(ValueError):
    pass


def check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


# ----------------------------------------------------------------------------
# Exact numbers, vectors, antichains
# ----------------------------------------------------------------------------
def F(x: object) -> Fraction:
    if isinstance(x, bool) or isinstance(x, float):
        raise GeometryError("FLOAT_OR_BOOL_INPUT_REJECTED")
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return Fraction(x)
    if isinstance(x, str):
        if "." in x or "e" in x.lower() or not x.strip():
            raise GeometryError("DECIMAL_OR_EMPTY_STRING_REJECTED")
        return Fraction(x)
    raise GeometryError("UNSUPPORTED_NUMERIC_INPUT")


def make_vec(values: Sequence[object]) -> Vec:
    v = tuple(F(x) for x in values)
    if not v:
        raise GeometryError("EMPTY_VECTOR")
    if any(x < 0 for x in v):
        raise GeometryError("NEGATIVE_BURDEN")
    return v


def _same_dim(u: Sequence[Fraction], v: Sequence[Fraction]) -> None:
    if len(u) != len(v) or not u:
        raise GeometryError("DIMENSION_MISMATCH")


def vec_leq(u: Vec, v: Vec) -> bool:
    _same_dim(u, v)
    return all(x <= y for x, y in zip(u, v))


def strictly_within(v: Vec, budget: Vec) -> bool:
    _same_dim(v, budget)
    return all(x < b for x, b in zip(v, budget))


def vec_add(u: Vec, v: Vec) -> Vec:
    _same_dim(u, v)
    return tuple(x + y for x, y in zip(u, v))


def pareto(items: Iterable[Vec]) -> Antichain:
    vals = tuple(sorted(set(tuple(v) for v in items)))
    if not vals:
        return ()
    dim = len(vals[0])
    if dim == 0 or any(len(v) != dim for v in vals):
        raise GeometryError("DIMENSION_MISMATCH")
    if any(any(x < 0 for x in v) for v in vals):
        raise GeometryError("NEGATIVE_BURDEN")
    return tuple(v for v in vals if not any(u != v and vec_leq(u, v) for u in vals))


def choice(a: Antichain, b: Antichain) -> Antichain:
    return pareto(tuple(a) + tuple(b))


def compose(a: Antichain, b: Antichain) -> Antichain:
    if not a or not b:
        return ()
    if len(a[0]) != len(b[0]):
        raise GeometryError("DIMENSION_MISMATCH")
    return pareto(tuple(vec_add(x, y) for x in a for y in b))


def identity(dim: int) -> Antichain:
    if dim <= 0:
        raise GeometryError("BAD_DIMENSION")
    return (tuple(Fraction(0) for _ in range(dim)),)


def dominated_by(a: Antichain, b: Antichain) -> bool:
    """A ⊑ B  ('B is at least as good as A'): every a in A has b in B with b <= a."""
    for x in a:
        if not any(vec_leq(y, x) for y in b):
            return False
    return True


def strictly_better(b: Antichain, a: Antichain) -> bool:
    """A ⊑ B and not B ⊑ A."""
    return dominated_by(a, b) and not dominated_by(b, a)


def grid_universe(max_coordinate: int = 2, dim: int = 2) -> Tuple[Antichain, ...]:
    """All Pareto frontiers of subsets of {0..max}^dim (parent P04 enumeration)."""
    if max_coordinate < 0 or dim <= 0:
        raise GeometryError("BAD_GRID")
    grid = tuple(tuple(Fraction(x) for x in p) for p in product(range(max_coordinate + 1), repeat=dim))
    if len(grid) > 16:
        raise GeometryError("GRID_TOO_LARGE")
    fronts = set()
    for mask in range(1 << len(grid)):
        fronts.add(pareto(tuple(grid[i] for i in range(len(grid)) if mask & (1 << i))))
    return tuple(sorted(fronts, key=lambda x: (len(x), x)))


# ----------------------------------------------------------------------------
# Graph, closure (Floyd-Warshall), path-length annotation
# ----------------------------------------------------------------------------
def registered_graph() -> Tuple[Tuple[str, ...], Dict[Edge, Antichain]]:
    edges: Dict[Edge, Antichain] = {}
    for i, j, vecs in EDGE_SPEC:
        key = (i, j)
        if key in edges:
            raise GeometryError("DUPLICATE_EDGE")
        edges[key] = pareto(tuple(make_vec(v) for v in vecs))
    return NODES, edges


def registered_budgets(dim: int = DIM) -> Tuple[Vec, ...]:
    lo, hi = BUDGET_RANGE
    return tuple(make_vec(p) for p in product(range(lo, hi + 1), repeat=dim))


def _validate_graph(nodes: Sequence[str], edges: Dict[Edge, Antichain], dim: int) -> None:
    if not nodes or len(set(nodes)) != len(nodes):
        raise GeometryError("MALFORMED_NODES")
    node_set = set(nodes)
    for (i, j), fr in edges.items():
        if i not in node_set or j not in node_set:
            raise GeometryError("EDGE_ENDPOINT_UNKNOWN")
        if any(len(v) != dim for v in fr):
            raise GeometryError("DIMENSION_MISMATCH")


def floyd_warshall_closure(
    nodes: Sequence[str], edges: Dict[Edge, Antichain], dim: int
) -> Tuple[Closure, int]:
    """Closure H by Floyd-Warshall over (choice, compose), iterated to a fixpoint.

    Returns (H, passes) where passes counts full k-i-j sweeps until no entry changes
    (the final sweep is the confirming one).
    """
    _validate_graph(nodes, edges, dim)
    h: Closure = {(i, j): () for i in nodes for j in nodes}
    for n in nodes:
        h[(n, n)] = identity(dim)
    for (i, j), fr in edges.items():
        h[(i, j)] = choice(h[(i, j)], pareto(fr))
    passes = 0
    while True:
        passes += 1
        changed = False
        for k in nodes:
            for i in nodes:
                for j in nodes:
                    new = choice(h[(i, j)], compose(h[(i, k)], h[(k, j)]))
                    if new != h[(i, j)]:
                        h[(i, j)] = new
                        changed = True
        if not changed:
            break
        check(passes < 64, "FLOYD_WARSHALL_NO_FIXPOINT")
    return h, passes


def closure_min_lengths(nodes: Sequence[str], edges: Dict[Edge, Antichain], dim: int) -> Lengths:
    """Minimum path length realizing each closure frontier vector.

    Computed by Floyd-Warshall on the (dim+1)-dimensional graph whose extra
    coordinate counts edges: (v, L) is Pareto-minimal there whenever v is a closure
    frontier vector and L is its minimum realizing length.
    """
    aug = {e: tuple(v + (Fraction(1),) for v in fr) for e, fr in edges.items()}
    h_aug, _ = floyd_warshall_closure(nodes, aug, dim + 1)
    out: Lengths = {}
    for key, fr in h_aug.items():
        d: Dict[Vec, int] = {}
        for v in fr:
            base = v[:dim]
            check(v[dim].denominator == 1, "NON_INTEGER_LENGTH")
            length = int(v[dim])
            if base not in d or length < d[base]:
                d[base] = length
        out[key] = d
    return out


def enrichment_violations(nodes: Sequence[str], h: Closure) -> Tuple[List[Tuple[str, str, str]], List[str]]:
    """Triples with not (H(M,N)*H(N,P) ⊑ H(M,P)) and nodes with not (I ⊑ H(M,M))."""
    bad_triples: List[Tuple[str, str, str]] = []
    bad_nodes: List[str] = []
    dim = None
    for fr in h.values():
        if fr:
            dim = len(fr[0])
            break
    check(dim is not None, "EMPTY_CLOSURE")
    for m in nodes:
        for n in nodes:
            for p in nodes:
                if not dominated_by(compose(h[(m, n)], h[(n, p)]), h[(m, p)]):
                    bad_triples.append((m, n, p))
    for m in nodes:
        if not dominated_by(identity(int(dim)), h[(m, m)]):
            bad_nodes.append(m)
    return bad_triples, bad_nodes


# ----------------------------------------------------------------------------
# Balls and generated topology (basis generation)
# ----------------------------------------------------------------------------
def budget_ball(nodes: Sequence[str], h: Closure, source: str, budget: Vec) -> FrozenSet[str]:
    if source not in set(nodes):
        raise GeometryError("UNKNOWN_SOURCE")
    if any(b <= 0 for b in budget):
        raise GeometryError("NONPOSITIVE_BUDGET")
    return frozenset(t for t in nodes if any(strictly_within(v, budget) for v in h[(source, t)]))


def ball_family(nodes: Sequence[str], h: Closure, budgets: Sequence[Vec]) -> FrozenSet[FrozenSet[str]]:
    balls = {frozenset()}  # type: set
    for x in nodes:
        for b in budgets:
            balls.add(budget_ball(nodes, h, x, b))
    return frozenset(balls)


def family_is_basis(family: FrozenSet[FrozenSet[str]]) -> bool:
    """Basis criterion: every point of b1&b2 lies in some member of the family inside b1&b2."""
    for b1 in family:
        for b2 in family:
            inter = b1 & b2
            for x in inter:
                if not any(x in b3 and b3 <= inter for b3 in family):
                    return False
    return True


def generated_topology(nodes: Sequence[str], h: Closure, budgets: Sequence[Vec]) -> Tuple[Opens, int, bool]:
    """Smallest topology containing the registered balls (route A: basis generation).

    The registered ball family is treated as a subbasis: its finite-intersection
    closure (with the whole set as the empty intersection) is a basis, and the opens
    are exactly the subsets satisfying the basis-open criterion.  When the raw ball
    family is itself a basis (parent P04's situation on its integer grid) this equals
    the parent construction; the flag reports whether that holds.  Verifies the
    topology axioms and returns (opens, distinct raw balls incl. empty, raw_is_basis).
    """
    raw = ball_family(nodes, h, budgets)
    raw_is_basis = family_is_basis(raw)
    node_tuple = tuple(nodes)
    basis = set(raw)
    basis.add(frozenset(node_tuple))
    while True:
        added = set()
        for u in basis:
            for v in basis:
                w = u & v
                if w not in basis:
                    added.add(w)
        if not added:
            break
        basis |= added
    check(family_is_basis(frozenset(basis)), "INTERSECTION_CLOSURE_NOT_A_BASIS")
    subsets = tuple(
        frozenset(node_tuple[i] for i in range(len(node_tuple)) if mask & (1 << i))
        for mask in range(1 << len(node_tuple))
    )
    opens = frozenset(u for u in subsets if all(any(x in bb and bb <= u for bb in basis) for x in u))
    check(frozenset() in opens and frozenset(node_tuple) in opens, "TOPOLOGY_MISSING_EMPTY_OR_WHOLE")
    for u in opens:
        for v in opens:
            check((u | v) in opens, "TOPOLOGY_NOT_UNION_CLOSED")
            check((u & v) in opens, "TOPOLOGY_NOT_INTERSECTION_CLOSED")
    if raw_is_basis:
        raw_opens = frozenset(u for u in subsets if all(any(x in bb and bb <= u for bb in raw) for x in u))
        check(raw_opens == opens, "SUBBASIS_AND_BASIS_CONSTRUCTIONS_DIFFER_ON_A_BASIS")
    return opens, len(raw), raw_is_basis


# ----------------------------------------------------------------------------
# Seeded null generator (64-bit LCG; only the high 31 bits are ever read)
# ----------------------------------------------------------------------------
NULL_SEED = 0x833
NULL_DRAWS = 200


class LCG:
    """Knuth MMIX constants; low bits of a power-of-two-modulus LCG have short
    period, so every draw reads ``state >> 33``."""

    def __init__(self, seed: int) -> None:
        self.state = (seed * 0x9E3779B97F4A7C15 + 1) % (1 << 64)

    def draw(self) -> int:
        self.state = (6364136223846793005 * self.state + 1442695040888963407) % (1 << 64)
        return self.state >> 33

    def permutation(self, n: int) -> List[int]:
        perm = list(range(n))
        for i in range(n - 1, 0, -1):
            j = self.draw() % (i + 1)
            perm[i], perm[j] = perm[j], perm[i]
        return perm


# ----------------------------------------------------------------------------
# Relabeling, rescaling, perturbation
# ----------------------------------------------------------------------------
def relabel_edges(nodes: Sequence[str], edges: Dict[Edge, Antichain], mapping: Dict[str, str]) -> Dict[Edge, Antichain]:
    if set(mapping.keys()) != set(nodes):
        raise GeometryError("NON_BIJECTIVE_RELABELING")
    values = list(mapping.values())
    if sorted(values) != sorted(nodes) or len(set(values)) != len(nodes):
        raise GeometryError("NON_BIJECTIVE_RELABELING")
    return {(mapping[i], mapping[j]): fr for (i, j), fr in edges.items()}


def transport_closure(h: Closure, inverse: Dict[str, str]) -> Closure:
    return {(inverse[i], inverse[j]): fr for (i, j), fr in h.items()}


def transport_opens(opens: Opens, inverse: Dict[str, str]) -> Opens:
    return frozenset(frozenset(inverse[x] for x in u) for u in opens)


def scale_vec(lam: Vec, v: Vec) -> Vec:
    _same_dim(lam, v)
    if any(x <= 0 for x in lam):
        raise GeometryError("NONPOSITIVE_SCALE")
    return tuple(a * b for a, b in zip(lam, v))


def scale_antichain(lam: Vec, fr: Antichain) -> Antichain:
    return pareto(tuple(scale_vec(lam, v) for v in fr))


def scale_edges(lam: Vec, edges: Dict[Edge, Antichain]) -> Dict[Edge, Antichain]:
    return {e: scale_antichain(lam, fr) for e, fr in edges.items()}


def perturb_edges(edges: Dict[Edge, Antichain], delta: Dict[Edge, Vec]) -> Dict[Edge, Antichain]:
    """Add delta[e] to every vector of edge e, clip at 0, Pareto-reduce."""
    out: Dict[Edge, Antichain] = {}
    for e, fr in edges.items():
        d = delta[e]
        vecs = []
        for v in fr:
            _same_dim(v, d)
            vecs.append(tuple(max(Fraction(0), x + y) for x, y in zip(v, d)))
        out[e] = pareto(tuple(vecs))
    return out


def uniform_delta(edge_keys: Sequence[Edge], s: Vec) -> Dict[Edge, Vec]:
    return {k: tuple(s) for k in edge_keys}


def perturbation_patterns(edge_keys: Sequence[Edge], dim: int, e: Fraction) -> Tuple[List[Dict[Edge, Vec]], int]:
    """Registered patterns: uniform sign pattern s in {-e,0,+e}^dim on all edges,
    plus every per-edge choice in {-e,+e}^|edges| applied uniformly across coordinates.
    Returns (distinct patterns, registered count before dedup)."""
    pats: List[Dict[Edge, Vec]] = []
    for s in product((-e, Fraction(0), e), repeat=dim):
        pats.append(uniform_delta(edge_keys, tuple(s)))
    for t in product((-e, e), repeat=len(edge_keys)):
        pats.append({k: tuple(t[idx] for _ in range(dim)) for idx, k in enumerate(edge_keys)})
    registered = len(pats)
    seen = set()
    distinct: List[Dict[Edge, Vec]] = []
    for p in pats:
        key = tuple(sorted((k, v) for k, v in p.items()))
        if key not in seen:
            seen.add(key)
            distinct.append(p)
    return distinct, registered


# ----------------------------------------------------------------------------
# Membership stability classification (STAB-2 b)
# ----------------------------------------------------------------------------
STABLE_MEMBER = "STABLE_MEMBER"
STABLE_NONMEMBER = "STABLE_NONMEMBER"
UNDETERMINED = "UNDETERMINED"


def classify_cell(
    frontier: Antichain, lengths: Dict[Vec, int], budget: Vec, e: Fraction
) -> Tuple[str, bool, Optional[Fraction], Optional[int], Optional[Fraction]]:
    """Return (class, member, best_margin, witness_length, best_slack).

    Membership STABLE iff some witness v<b has margin min_i(b_i-v_i) > L_v*e
    (L_v = minimum path length realizing v).  Non-membership STABLE iff every
    frontier vector exceeds b by more than L_v*e in some coordinate (vacuous for
    the empty frontier: no path exists, none can be created by perturbation).
    """
    member = any(strictly_within(v, budget) for v in frontier)
    if member:
        best: Optional[Tuple[Fraction, Fraction, int]] = None
        for v in frontier:
            if not strictly_within(v, budget):
                continue
            margin = min(b - x for b, x in zip(budget, v))
            length = lengths[v]
            slack = margin - length * e
            if best is None or slack > best[0]:
                best = (slack, margin, length)
        check(best is not None, "MEMBER_WITHOUT_WITNESS")
        slack, margin, length = best  # type: ignore[misc]
        cls = STABLE_MEMBER if slack > 0 else UNDETERMINED
        return cls, True, margin, length, slack
    stable = True
    for v in frontier:
        length = lengths[v]
        if not any(x - b > length * e for x, b in zip(v, budget)):
            stable = False
            break
    return (STABLE_NONMEMBER if stable else UNDETERMINED), False, None, None, None


def is_member(h: Closure, source: str, target: str, budget: Vec) -> bool:
    return any(strictly_within(v, budget) for v in h[(source, target)])


# ----------------------------------------------------------------------------
# Scalar projection (STAB-2 c)
# ----------------------------------------------------------------------------
def dot(v: Vec, w: Vec) -> Fraction:
    _same_dim(v, w)
    return sum((x * y for x, y in zip(v, w)), Fraction(0))


def scalar_distance(frontier: Antichain, w: Vec) -> Optional[Fraction]:
    """min_v w·v over the frontier; None encodes +infinity (empty frontier)."""
    if any(x <= 0 for x in w):
        raise GeometryError("NONPOSITIVE_SCALAR_WEIGHT")
    if not frontier:
        return None
    return min(dot(v, w) for v in frontier)


# ----------------------------------------------------------------------------
# Serialization helpers (deterministic; Fractions as "n/d")
# ----------------------------------------------------------------------------
def ser_frac(x: Fraction) -> str:
    if isinstance(x, bool) or not isinstance(x, (int, Fraction)):
        raise GeometryError("NON_EXACT_VALUE_IN_RECEIPT")
    f = Fraction(x)
    return "%d/%d" % (f.numerator, f.denominator)


def ser_vec(v: Vec) -> List[str]:
    return [ser_frac(x) for x in v]


def ser_antichain(fr: Antichain) -> List[List[str]]:
    return [ser_vec(v) for v in fr]


def ser_closure(h: Closure) -> Dict[str, List[List[str]]]:
    return {"%s->%s" % (i, j): ser_antichain(fr) for (i, j), fr in h.items()}


def ser_lengths(lengths: Lengths) -> Dict[str, List[List[object]]]:
    out: Dict[str, List[List[object]]] = {}
    for (i, j), d in lengths.items():
        out["%s->%s" % (i, j)] = [[ser_vec(v), d[v]] for v in sorted(d)]
    return out


def ser_edges(edges: Dict[Edge, Antichain]) -> Dict[str, List[List[str]]]:
    return {"%s->%s" % (i, j): ser_antichain(fr) for (i, j), fr in edges.items()}


def ser_opens(opens: Opens) -> List[List[str]]:
    return sorted((sorted(u) for u in opens), key=lambda u: (len(u), u))


def ser_scalar(x: Optional[Fraction]) -> str:
    return "INF" if x is None else ser_frac(x)


def parse_edges(edges_ser: Dict[str, List[List[str]]]) -> Dict[Edge, Antichain]:
    out: Dict[Edge, Antichain] = {}
    for key, vecs in edges_ser.items():
        i, j = key.split("->")
        out[(i, j)] = pareto(tuple(make_vec(v) for v in vecs))
    return out


def canonical_json(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def graph_closure_digest(edges_ser: Dict[str, List[List[str]]], closure_ser: Dict[str, List[List[str]]]) -> str:
    return hashlib.sha256(canonical_json({"edges": edges_ser, "closure": closure_ser}).encode("utf-8")).hexdigest()


def verify_receipt_closure(receipt: Dict[str, object]) -> bool:
    """Recompute the closure from the receipt's registered edges; True iff it matches
    the recorded closure witness and the recorded digest."""
    reg = receipt["registered"]  # type: ignore[index]
    nodes = tuple(reg["nodes"])  # type: ignore[index]
    edges = parse_edges(reg["edges"])  # type: ignore[index]
    h, _ = floyd_warshall_closure(nodes, edges, int(reg["dim"]))  # type: ignore[index]
    closure_ser = ser_closure(h)
    recorded = receipt["witnesses"]["closure"]  # type: ignore[index]
    digest = graph_closure_digest(reg["edges"], closure_ser)  # type: ignore[index]
    return closure_ser == recorded and digest == receipt["graph_closure_digest"]  # type: ignore[index]


def receipt_text(obj: Dict[str, object]) -> str:
    return json.dumps(obj, indent=1, sort_keys=True) + "\n"


def write_receipt(path: str, obj: Dict[str, object]) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(receipt_text(obj))


# ----------------------------------------------------------------------------
# Main computation
# ----------------------------------------------------------------------------
def build_result() -> Dict[str, object]:
    counts: Dict[str, int] = {}
    checks: Dict[str, bool] = {}
    witnesses: Dict[str, object] = {}
    hostiles: Dict[str, Dict[str, bool]] = {}

    # ---------------- ENR-1 (i)-(iii) on the 20-antichain grid universe ----------
    universe = grid_universe(2, 2)
    counts["grid_universe_antichains"] = len(universe)
    checks["grid_universe_has_20_antichains"] = len(universe) == 20
    empty: Antichain = ()
    check(empty in universe and identity(2) in universe, "UNIVERSE_MISSING_EMPTY_OR_IDENTITY")

    # empty-antichain facts
    counts["empty_dominated_by_every_antichain_checks"] = len(universe)
    checks["empty_antichain_dominated_by_every_antichain"] = all(dominated_by(empty, b) for b in universe)
    counts["dominates_empty_only_if_empty_checks"] = len(universe)
    checks["antichain_dominated_by_empty_only_if_empty"] = all(
        dominated_by(a, empty) == (a == empty) for a in universe
    )

    # preorder: reflexive, transitive (and antisymmetric, recorded as extra)
    counts["dominance_reflexive_checks"] = len(universe)
    checks["dominance_reflexive"] = all(dominated_by(a, a) for a in universe)
    rel = {(ia, ib): dominated_by(a, b) for ia, a in enumerate(universe) for ib, b in enumerate(universe)}
    counts["dominance_pairs_evaluated"] = len(rel)
    counts["dominance_related_pairs"] = sum(1 for v in rel.values() if v)
    n_u = len(universe)
    trans_ok = True
    for ia in range(n_u):
        for ib in range(n_u):
            if not rel[(ia, ib)]:
                continue
            for ic in range(n_u):
                if rel[(ib, ic)] and not rel[(ia, ic)]:
                    trans_ok = False
    counts["dominance_transitive_triples_checked"] = n_u ** 3
    checks["dominance_transitive"] = trans_ok
    anti_ok = all(
        not (rel[(ia, ib)] and rel[(ib, ia)]) or universe[ia] == universe[ib]
        for ia in range(n_u) for ib in range(n_u)
    )
    counts["dominance_antisymmetric_pairs_checked"] = n_u * n_u
    checks["dominance_antisymmetric_on_universe"] = anti_ok

    # (i) composition monotone in each argument
    mono_checks = 0
    mono_ok = True
    for ia, a in enumerate(universe):
        for ib, a2 in enumerate(universe):
            if not rel[(ia, ib)]:
                continue
            for c in universe:
                mono_checks += 2
                if not dominated_by(compose(a, c), compose(a2, c)):
                    mono_ok = False
                if not dominated_by(compose(c, a), compose(c, a2)):
                    mono_ok = False
    counts["composition_monotone_checks"] = mono_checks
    checks["composition_monotone_each_argument"] = mono_ok

    # (ii) choice is the join
    ub_ok = True
    for a in universe:
        for b in universe:
            j = choice(a, b)
            if not (dominated_by(a, j) and dominated_by(b, j)):
                ub_ok = False
    counts["join_upper_bound_checks"] = 2 * n_u * n_u
    checks["choice_is_upper_bound"] = ub_ok
    least_ok = True
    least_checks = 0
    for ia, a in enumerate(universe):
        for ib, b in enumerate(universe):
            j = choice(a, b)
            for ic, c in enumerate(universe):
                least_checks += 1
                if rel[(ia, ic)] and rel[(ib, ic)] and not dominated_by(j, c):
                    least_ok = False
    counts["join_least_upper_bound_checks"] = least_checks
    checks["choice_is_least_upper_bound"] = least_ok

    # ---------------- registered graph, closure, enrichment law -----------------
    nodes, edges = registered_graph()
    h, passes = floyd_warshall_closure(nodes, edges, DIM)
    lengths = closure_min_lengths(nodes, edges, DIM)
    check(all(set(lengths[k].keys()) == set(h[k]) for k in h), "LENGTH_ANNOTATION_KEY_MISMATCH")
    counts["graph_nodes"] = len(nodes)
    counts["graph_edges"] = len(edges)
    counts["graph_ordered_pairs"] = len(nodes) ** 2
    counts["floyd_warshall_passes_to_fixpoint"] = passes
    checks["parent_frontier_A_to_C_extended_by_two_edge_alternative"] = h[("A", "C")] == pareto(
        (make_vec(("0", "5")), make_vec(("1", "1")), make_vec(("5/2", "3/4")), make_vec(("5", "0")))
    )
    checks["unreachable_frontier_preserved"] = h[("A", "D")] == () and h[("D", "A")] == ()
    witnesses["closure"] = ser_closure(h)
    witnesses["closure_min_path_lengths"] = ser_lengths(lengths)

    bad_triples, bad_nodes = enrichment_violations(nodes, h)
    counts["enrichment_triples_checked"] = len(nodes) ** 3
    counts["enrichment_identity_nodes_checked"] = len(nodes)
    checks["enrichment_lax_composition_law"] = bad_triples == []
    checks["enrichment_identity_law"] = bad_nodes == []

    strict_witness = None
    equal_witness = None
    n_strict = 0
    n_equal = 0
    for m in nodes:
        for n in nodes:
            for p in nodes:
                comp = compose(h[(m, n)], h[(n, p)])
                if comp and strictly_better(h[(m, p)], comp):
                    n_strict += 1
                    if strict_witness is None and len({m, n, p}) == 3:
                        strict_witness = (m, n, p, comp, h[(m, p)])
                if comp and comp == h[(m, p)] and len({m, n, p}) == 3:
                    n_equal += 1
                    if equal_witness is None:
                        equal_witness = (m, n, p, comp)
    counts["enrichment_triples_composite_nonempty_strictly_worse"] = n_strict
    counts["enrichment_triples_distinct_nodes_composite_equal"] = n_equal
    checks["enrichment_strict_and_equal_witnesses_exist"] = strict_witness is not None and equal_witness is not None
    check(strict_witness is not None and equal_witness is not None, "ENRICHMENT_WITNESSES_MISSING")
    witnesses["enrichment_strict_triple"] = {
        "triple": list(strict_witness[:3]),  # type: ignore[index]
        "composite": ser_antichain(strict_witness[3]),  # type: ignore[index]
        "closure": ser_antichain(strict_witness[4]),  # type: ignore[index]
    }
    witnesses["enrichment_equal_triple"] = {
        "triple": list(equal_witness[:3]),  # type: ignore[index]
        "composite_equals_closure": ser_antichain(equal_witness[3]),  # type: ignore[index]
    }

    # ---------------- STAB-1 relabeling ------------------------------------------
    budgets = registered_budgets(DIM)
    counts["budget_vectors"] = len(budgets)
    opens, n_basis, raw_is_basis = generated_topology(nodes, h, budgets)
    counts["basis_balls_including_empty"] = n_basis
    counts["open_sets"] = len(opens)
    witnesses["open_sets"] = ser_opens(opens)
    checks["registered_ball_family_is_basis_original"] = raw_is_basis

    relabel_ok_closure = 0
    relabel_ok_topology = 0
    relabel_total = 0
    open_counts = set()
    for perm in permutations(nodes):
        relabel_total += 1
        mapping = {nodes[i]: perm[i] for i in range(len(nodes))}
        inverse = {v: k for k, v in mapping.items()}
        e2 = relabel_edges(nodes, edges, mapping)
        h2, _ = floyd_warshall_closure(nodes, e2, DIM)
        if transport_closure(h2, inverse) == h:
            relabel_ok_closure += 1
        o2, _, _ = generated_topology(nodes, h2, budgets)
        open_counts.add(len(o2))
        if transport_opens(o2, inverse) == opens:
            relabel_ok_topology += 1
    counts["relabelings"] = relabel_total
    counts["relabel_closure_equalities"] = relabel_ok_closure
    counts["relabel_topology_equalities"] = relabel_ok_topology
    checks["relabeling_closure_transport_equal_all"] = relabel_ok_closure == relabel_total == 120
    checks["relabeling_topology_transport_equal_all"] = relabel_ok_topology == relabel_total == 120
    checks["relabeling_open_set_count_invariant"] = open_counts == {len(opens)}

    # ---------------- STAB-1 null: misaligned transport ---------------------------
    # The true law transports the relabeled closure/topology back along sigma^-1 and
    # recovers the original 120/120.  The null draws 200 seeded pairs (sigma, tau) with
    # tau != sigma^-1 and transports along tau instead.  The registered graph has only
    # the trivial automorphism (recorded), so no misaligned transport can recover the
    # closure; the pool excludes the true law by construction.
    automorphisms = sum(1 for perm in permutations(nodes)
                        if relabel_edges(nodes, edges, {nodes[i]: perm[i] for i in range(len(nodes))}) == edges)
    counts["graph_automorphisms"] = automorphisms
    checks["graph_automorphism_group_trivial"] = automorphisms == 1
    null_draws = 0
    null_closure_eq = 0
    null_topology_eq = 0
    lcg = LCG(NULL_SEED)
    while null_draws < NULL_DRAWS:
        sigma_perm = lcg.permutation(len(nodes))
        tau_perm = lcg.permutation(len(nodes))
        sigma = {nodes[i]: nodes[sigma_perm[i]] for i in range(len(nodes))}
        sigma_inv = {v: k for k, v in sigma.items()}
        tau = {nodes[i]: nodes[tau_perm[i]] for i in range(len(nodes))}
        if tau == sigma_inv:
            continue  # the true law is excluded from the pool
        null_draws += 1
        h_s, _ = floyd_warshall_closure(nodes, relabel_edges(nodes, edges, sigma), DIM)
        if transport_closure(h_s, tau) == h:
            null_closure_eq += 1
        o_s, _, _ = generated_topology(nodes, h_s, budgets)
        if transport_opens(o_s, tau) == opens:
            null_topology_eq += 1
    counts["null_draws"] = null_draws
    counts["null_closure_equalities"] = null_closure_eq
    counts["null_topology_equalities"] = null_topology_eq
    checks["null_zero_closure_equalities"] = null_closure_eq == 0
    checks["null_topology_equalities_below_true_law"] = null_topology_eq < null_draws

    # ---------------- STAB-2 (a) rescaling ---------------------------------------
    lambdas = tuple(make_vec(l) for l in LAMBDAS)
    check(all(all(x > 0 for x in l) for l in lambdas), "NONPOSITIVE_LAMBDA")
    counts["lambdas"] = len(lambdas)
    rescale_pairs = 0
    rescale_pairs_ok = 0
    rescale_topo_ok = 0
    fixed_grid_rows = []
    fixed_grid_differ = 0
    raw_family_original = ball_family(nodes, h, budgets)
    fixed_grid_raw_family_moved = 0
    for lam in lambdas:
        hl, _ = floyd_warshall_closure(nodes, scale_edges(lam, edges), DIM)
        if ball_family(nodes, hl, budgets) != raw_family_original:
            fixed_grid_raw_family_moved += 1
        for key in h:
            rescale_pairs += 1
            if hl[key] == scale_antichain(lam, h[key]):
                rescale_pairs_ok += 1
        scaled_budgets = tuple(scale_vec(lam, b) for b in budgets)
        ol, _, ol_basis = generated_topology(nodes, hl, scaled_budgets)
        if ol == opens and ol_basis == raw_is_basis:
            rescale_topo_ok += 1
        ofix, _, ofix_basis = generated_topology(nodes, hl, budgets)
        differs = ofix != opens
        if differs:
            fixed_grid_differ += 1
        only_fixed = sorted((sorted(u) for u in ofix - opens), key=lambda u: (len(u), u))
        only_orig = sorted((sorted(u) for u in opens - ofix), key=lambda u: (len(u), u))
        fixed_grid_rows.append({
            "lambda": ser_vec(lam),
            "open_sets_fixed_grid": len(ofix),
            "open_sets_original": len(opens),
            "differs": differs,
            "raw_ball_family_is_basis": ofix_basis,
            "open_only_under_fixed_grid_rescaling": only_fixed,
            "open_only_in_original": only_orig,
        })
    counts["rescale_closure_pair_checks"] = rescale_pairs
    counts["rescale_closure_pair_equalities"] = rescale_pairs_ok
    counts["rescale_topology_equalities"] = rescale_topo_ok
    counts["fixed_grid_lambdas_differing"] = fixed_grid_differ
    counts["fixed_grid_lambdas_moving_raw_ball_family"] = fixed_grid_raw_family_moved
    checks["rescaling_commutes_with_closure"] = rescale_pairs_ok == rescale_pairs
    checks["rescaled_budgets_generate_same_topology"] = rescale_topo_ok == len(lambdas)
    witnesses["fixed_budget_grid_rescaling"] = fixed_grid_rows
    hostiles["fixed_budget_grid_rescaling_changes_topology"] = {
        "applicable": fixed_grid_raw_family_moved > 0,
        "detected": any(r["differs"] for r in fixed_grid_rows),
    }

    # ---------------- STAB-2 (b) additive perturbation -------------------------
    e = F(PERTURBATION_E)
    check(e > 0, "NONPOSITIVE_E")
    edge_keys = tuple(sorted(edges.keys()))
    patterns, registered = perturbation_patterns(edge_keys, DIM, e)
    counts["perturbation_patterns_registered"] = registered
    counts["perturbation_patterns_distinct"] = len(patterns)

    cell_class: Dict[Tuple[Vec, str, str], str] = {}
    cell_member: Dict[Tuple[Vec, str, str], bool] = {}
    class_counts = {STABLE_MEMBER: 0, STABLE_NONMEMBER: 0, UNDETERMINED: 0}
    tight: Optional[Tuple[Fraction, Fraction, int, Vec, str, str]] = None  # slack, margin, L, b, M, N
    for b in budgets:
        for m in nodes:
            for n in nodes:
                cls, member, margin, length, slack = classify_cell(h[(m, n)], lengths[(m, n)], b, e)
                cell_class[(b, m, n)] = cls
                cell_member[(b, m, n)] = member
                class_counts[cls] += 1
                if cls == STABLE_MEMBER and m != n:
                    cand = (slack, margin, length, b, m, n)  # type: ignore[arg-type]
                    if tight is None or cand[0] < tight[0]:
                        tight = cand  # type: ignore[assignment]
    counts["perturbation_cells"] = len(cell_class)
    counts["cells_stable_member"] = class_counts[STABLE_MEMBER]
    counts["cells_stable_nonmember"] = class_counts[STABLE_NONMEMBER]
    counts["cells_undetermined"] = class_counts[UNDETERMINED]
    check(tight is not None, "NO_STABLE_MEMBER_CELL_OFF_DIAGONAL")

    stable_cells = [k for k, v in cell_class.items() if v != UNDETERMINED]
    flips = 0
    stable_checks = 0
    sandwich_checks = 0
    sandwich_ok = True
    h_plus, _ = floyd_warshall_closure(nodes, perturb_edges(edges, uniform_delta(edge_keys, (e,) * DIM)), DIM)
    h_minus, _ = floyd_warshall_closure(nodes, perturb_edges(edges, uniform_delta(edge_keys, (-e,) * DIM)), DIM)
    for pat in patterns:
        hp, _ = floyd_warshall_closure(nodes, perturb_edges(edges, pat), DIM)
        for (b, m, n) in stable_cells:
            stable_checks += 1
            if is_member(hp, m, n, b) != cell_member[(b, m, n)]:
                flips += 1
        for b in budgets:
            for m in nodes:
                for n in nodes:
                    sandwich_checks += 1
                    mem = is_member(hp, m, n, b)
                    if is_member(h_plus, m, n, b) and not mem:
                        sandwich_ok = False
                    if mem and not is_member(h_minus, m, n, b):
                        sandwich_ok = False
    counts["stable_cell_pattern_checks"] = stable_checks
    counts["stable_cell_flips"] = flips
    checks["no_stable_cell_flips_under_registered_patterns"] = flips == 0
    counts["box_sandwich_checks"] = sandwich_checks
    checks["pattern_membership_sandwiched_by_box_extremes"] = sandwich_ok
    box_stable = 0
    frozen_subset_box = True
    for (b, m, n), cls in cell_class.items():
        mem = cell_member[(b, m, n)]
        bs = (mem and is_member(h_plus, m, n, b)) or ((not mem) and not is_member(h_minus, m, n, b))
        if bs:
            box_stable += 1
        if cls != UNDETERMINED and not bs:
            frozen_subset_box = False
    counts["cells_box_stable"] = box_stable
    checks["frozen_stable_cells_subset_of_box_stable_cells"] = frozen_subset_box
    checks["box_stable_cells_at_least_frozen_stable"] = box_stable >= class_counts[STABLE_MEMBER] + class_counts[STABLE_NONMEMBER]

    # ---------------- STAB-2 (b) correction: the frozen frontier-based NON-membership criterion is
    # not sound in general. Counterexample (machine-checked): a direct edge (10,0) dominates a 3-edge
    # path summing to (41/4,0); at budget (155/16,1) the frontier vector exceeds the budget by 5/16 >
    # 1*e, so the frozen rule says STABLE_NONMEMBER, yet lowering every edge by e brings the 3-edge
    # path to (19/2,0) < budget: membership flips. The box criterion marks the cell UNDETERMINED.
    ce_nodes = ("M", "a", "b", "N")
    ce_edges: Dict[Edge, Antichain] = {
        ("M", "N"): (make_vec(("10", "0")),),
        ("M", "a"): (make_vec(("41/12", "0")),),
        ("a", "b"): (make_vec(("41/12", "0")),),
        ("b", "N"): (make_vec(("41/12", "0")),),
    }
    ce_b = make_vec(("155/16", "1"))
    ce_h, _ = floyd_warshall_closure(ce_nodes, ce_edges, DIM)
    ce_len = closure_min_lengths(ce_nodes, ce_edges, DIM)
    ce_cls, ce_mem, _, _, _ = classify_cell(ce_h[("M", "N")], ce_len[("M", "N")], ce_b, e)
    ce_keys = tuple(sorted(ce_edges.keys()))
    ce_minus, _ = floyd_warshall_closure(ce_nodes, perturb_edges(ce_edges, uniform_delta(ce_keys, (-e,) * DIM)), DIM)
    ce_plus, _ = floyd_warshall_closure(ce_nodes, perturb_edges(ce_edges, uniform_delta(ce_keys, (e,) * DIM)), DIM)
    ce_flip = (not ce_mem) and is_member(ce_minus, "M", "N", ce_b)
    ce_box_stable = (ce_mem and is_member(ce_plus, "M", "N", ce_b)) or ((not ce_mem) and not is_member(ce_minus, "M", "N", ce_b))
    witnesses["frozen_nonmember_counterexample"] = {
        "edges": {"M->N": [["10", "0"]], "M->a": [["41/12", "0"]], "a->b": [["41/12", "0"]], "b->N": [["41/12", "0"]]},
        "budget": ser_vec(ce_b), "e": ser_frac(e),
        "frontier_M_N": ser_antichain(ce_h[("M", "N")]),
        "frozen_classification": ce_cls,
        "member_before": ce_mem,
        "member_after_all_edges_minus_e": is_member(ce_minus, "M", "N", ce_b),
        "frontier_after_all_edges_minus_e": ser_antichain(ce_minus[("M", "N")]),
        "box_criterion_stable": ce_box_stable,
    }
    checks["frozen_nonmember_criterion_refuted_by_counterexample"] = (ce_cls == STABLE_NONMEMBER) and ce_flip
    checks["box_criterion_marks_counterexample_undetermined"] = not ce_box_stable

    t_slack, t_margin, t_len, t_b, t_m, t_n = tight  # type: ignore[misc]
    witnesses["tightest_stable_member_cell"] = {
        "budget": ser_vec(t_b), "source": t_m, "target": t_n,
        "best_margin": ser_frac(t_margin), "witness_path_length": t_len,
        "slack_margin_minus_L_times_e": ser_frac(t_slack),
    }
    # hostile: uniform +delta with delta = best margin exceeds the L*e guarantee -> flip
    delta = t_margin
    h_host, _ = floyd_warshall_closure(nodes, perturb_edges(edges, uniform_delta(edge_keys, (delta,) * DIM)), DIM)
    host_member_after = is_member(h_host, t_m, t_n, t_b)
    hostiles["margin_exceeding_perturbation_flips_membership"] = {
        "applicable": bool(delta > e and t_len * delta >= t_margin),
        "detected": bool(host_member_after != cell_member[(t_b, t_m, t_n)]),
    }
    witnesses["margin_exceeding_perturbation_hostile"] = {
        "cell": {"budget": ser_vec(t_b), "source": t_m, "target": t_n},
        "uniform_delta": ser_frac(delta),
        "registered_e": ser_frac(e),
        "member_before": cell_member[(t_b, t_m, t_n)],
        "member_after": host_member_after,
    }

    # ---------------- STAB-2 (c) scalar projection -------------------------------
    weights = tuple(make_vec(w) for w in WEIGHTS)
    counts["scalar_weights"] = len(weights)
    scalar_table: Dict[str, Dict[str, str]] = {}
    for w in weights:
        scalar_table[ser_frac(w[0]) + "," + ser_frac(w[1])] = {
            "%s->%s" % (i, j): ser_scalar(scalar_distance(h[(i, j)], w)) for (i, j) in sorted(h)
        }
    witnesses["scalar_distances"] = scalar_table
    fin_checks = 0
    fin_ok = True
    inf_checks = 0
    inf_ok = True
    for a in range(len(weights)):
        for c in range(a + 1, len(weights)):
            w, w2 = weights[a], weights[c]
            diff = tuple(x - y for x, y in zip(w, w2))
            for key, fr in h.items():
                dw, dw2 = scalar_distance(fr, w), scalar_distance(fr, w2)
                if dw is None or dw2 is None:
                    inf_checks += 1
                    if not (dw is None and dw2 is None and fr == ()):
                        inf_ok = False
                    continue
                fin_checks += 1
                bound = max(abs(dot(diff, v)) for v in fr)
                if abs(dw - dw2) > bound:
                    fin_ok = False
    counts["scalar_weight_pairs"] = 3
    counts["scalar_finite_lipschitz_checks"] = fin_checks
    counts["scalar_infinite_pair_checks"] = inf_checks
    checks["scalar_projection_lipschitz_bound"] = fin_ok
    checks["scalar_infinite_pairs_stay_infinite"] = inf_ok

    # ---------------- hostiles -------------------------------------------------
    raw_neg = ("-1", "0")
    neg_detected = False
    try:
        make_vec(raw_neg)
    except GeometryError as ex:
        neg_detected = "NEGATIVE_BURDEN" in str(ex)
    hostiles["negative_burden_rejected"] = {
        "applicable": any(Fraction(x) < 0 for x in raw_neg),
        "detected": neg_detected,
    }

    a3 = pareto((make_vec(("1", "2", "3")),))
    a2 = pareto((make_vec(("1", "2")),))
    dim_detected = False
    try:
        compose(a2, a3)
    except GeometryError as ex:
        dim_detected = "DIMENSION_MISMATCH" in str(ex)
    dim_detected2 = False
    try:
        dominated_by(a2, a3)
    except GeometryError as ex:
        dim_detected2 = "DIMENSION_MISMATCH" in str(ex)
    hostiles["dimension_mismatch_rejected"] = {
        "applicable": len(a2[0]) != len(a3[0]),
        "detected": dim_detected and dim_detected2,
    }

    f1 = pareto((make_vec(("1", "4")), make_vec(("4", "1"))))
    coord_inf = tuple(min(v[i] for v in f1) for i in range(2))
    hostiles["coordinatewise_infimum_fabrication_detected"] = {
        "applicable": coord_inf not in f1 and all(vec_leq(coord_inf, v) for v in f1),
        "detected": (coord_inf not in f1) and (not dominated_by((coord_inf,), f1)),
    }
    witnesses["coordinatewise_infimum_hostile"] = {
        "frontier": ser_antichain(f1), "coordinatewise_infimum": ser_vec(coord_inf), "attainable": coord_inf in f1,
    }

    planted = dict(h)
    planted[("A", "C")] = pareto((make_vec(("6", "6")),))
    p_triples, p_nodes = enrichment_violations(nodes, planted)
    hostiles["planted_closure_entry_violating_enrichment_detected"] = {
        "applicable": planted[("A", "C")] != h[("A", "C")] and strictly_better(h[("A", "C")], planted[("A", "C")]),
        "detected": len(p_triples) > 0,
    }
    witnesses["planted_closure_hostile"] = {
        "entry": "A->C", "planted": ser_antichain(planted[("A", "C")]),
        "violating_triples": [list(t) for t in p_triples], "identity_violations": p_nodes,
    }

    bad_map = {"A": "A", "B": "A", "C": "C", "D": "D", "E": "E"}
    nb_detected = False
    try:
        relabel_edges(nodes, edges, bad_map)
    except GeometryError as ex:
        nb_detected = "NON_BIJECTIVE_RELABELING" in str(ex)
    hostiles["non_bijective_relabeling_rejected"] = {
        "applicable": len(set(bad_map.values())) != len(nodes),
        "detected": nb_detected,
    }

    # ---------------- assemble receipt -------------------------------------------
    registered = {
        "nodes": list(nodes),
        "dim": DIM,
        "edges": ser_edges(edges),
        "budget_grid": {"lo": BUDGET_RANGE[0], "hi": BUDGET_RANGE[1], "dim": DIM},
        "lambdas": [ser_vec(l) for l in lambdas],
        "perturbation_e": ser_frac(e),
        "weights": [ser_vec(w) for w in weights],
        "grid_universe": {"max_coordinate": 2, "dim": 2},
    }
    result: Dict[str, object] = {
        "schema": SCHEMA,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
        "results": list(RESULTS),
        "route": ROUTE,
        "registered": registered,
        "counts": counts,
        "witnesses": witnesses,
        "hostiles": hostiles,
        "checks": checks,
        "null": {
            "law": "MISALIGNED_TRANSPORT_OF_RELABELED_CLOSURE_AND_TOPOLOGY",
            "draws": null_draws,
            "closure_equalities": null_closure_eq,
            "topology_equalities": null_topology_eq,
            "true_law_aligned_equalities": relabel_ok_closure,
            "pool_excludes_true_law": True,
            "graph_automorphisms": automorphisms,
        },
        "quantale_completeness_not_claimed": True,
        "complete_quantale_would_additionally_require": list(COMPLETE_QUANTALE_WOULD_ADDITIONALLY_REQUIRE),
        "terminal": TERMINAL,
        "graph_closure_digest": graph_closure_digest(registered["edges"], witnesses["closure"]),  # type: ignore[arg-type]
    }

    # tamper hostile: change one registered edge burden in a copy of the receipt
    tampered = json.loads(canonical_json(result))
    orig_ab = list(tampered["registered"]["edges"]["A->B"])
    tampered["registered"]["edges"]["A->B"] = [["1/1", "0/1"]]
    hostiles["tampered_receipt_edge_burden_detected"] = {
        "applicable": tampered["registered"]["edges"]["A->B"] != orig_ab,
        "detected": not verify_receipt_closure(tampered),
    }
    checks["untampered_receipt_closure_verifies"] = verify_receipt_closure(result)

    for name, hv in hostiles.items():
        checks["hostile_applicable__" + name] = bool(hv["applicable"])
        checks["hostile_detected__" + name] = bool(hv["detected"])
    for k, v in counts.items():
        check(isinstance(v, int) and not isinstance(v, bool), "NON_INT_COUNT:" + k)
    counts["hostiles_total"] = len(hostiles)
    counts["hostiles_applicable"] = sum(1 for hv in hostiles.values() if hv["applicable"])
    counts["hostiles_detected"] = sum(1 for hv in hostiles.values() if hv["detected"])
    counts["checks_total"] = len(checks)
    counts["checks_passed"] = sum(1 for v in checks.values() if v)

    green = all(checks.values()) and all(hv["applicable"] and hv["detected"] for hv in hostiles.values())
    result["verdict"] = "GREEN" if green else "RED"
    result["status"] = result["verdict"]
    return result


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    result = build_result()
    write_receipt(os.path.join(here, RECEIPT_NAME), result)
    counts = result["counts"]  # type: ignore[index]
    summary = {
        "schema": SCHEMA,
        "status": result["status"],
        "results": result["results"],
        "hostiles_detected": counts["hostiles_detected"],  # type: ignore[index]
        "hostiles_total": counts["hostiles_total"],  # type: ignore[index]
        "checks_passed": counts["checks_passed"],  # type: ignore[index]
        "checks_total": counts["checks_total"],  # type: ignore[index]
        "open_sets": counts["open_sets"],  # type: ignore[index]
    }
    print(canonical_json(summary))
    return 0 if result["status"] == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
