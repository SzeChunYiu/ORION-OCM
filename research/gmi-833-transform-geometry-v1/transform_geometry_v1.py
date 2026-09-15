from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from heapq import heappop, heappush
from math import inf
from typing import Iterable, Mapping, Sequence

CLAIM_CEILING = "GMI_TRANSFORM_CATEGORY_AND_DIRECTED_SCALAR_GEOMETRY_AT_REGISTERED_FINITE_SCOPE"
RESOURCE_COORDS = ("compute", "memory", "communication")
IDENTITY_EVIDENCE = "__IDENTITY__"


class TransformError(ValueError):
    pass


def F(x: int | str | Fraction) -> Fraction:
    return x if isinstance(x, Fraction) else Fraction(x)


def canonical_assumptions(items: Iterable[tuple[str, str]]) -> tuple[tuple[str, str], ...]:
    table: dict[str, str] = {}
    for key, value in items:
        if not key or not value:
            raise TransformError("MALFORMED_ASSUMPTION")
        if key in table and table[key] != value:
            raise TransformError("ASSUMPTION_CONFLICT")
        table[key] = value
    return tuple(sorted(table.items()))


def canonical_evidence(items: Iterable[str], *, identity: bool = False) -> tuple[str, ...]:
    vals = tuple(sorted({x for x in items if x and x != IDENTITY_EVIDENCE}))
    if identity:
        if vals:
            raise TransformError("IDENTITY_HAS_NONNEUTRAL_EVIDENCE")
        return (IDENTITY_EVIDENCE,)
    if not vals:
        raise TransformError("MISSING_EVIDENCE")
    return vals


@dataclass(frozen=True)
class Transform:
    source: str
    target: str
    semantic_error: Fraction
    resources: tuple[Fraction, ...]
    assumptions: tuple[tuple[str, str], ...]
    evidence: tuple[str, ...]

    @property
    def is_identity(self) -> bool:
        return (
            self.source == self.target
            and self.semantic_error == 0
            and all(x == 0 for x in self.resources)
            and not self.assumptions
            and self.evidence == (IDENTITY_EVIDENCE,)
        )


def make_transform(
    source: str,
    target: str,
    semantic_error: int | str | Fraction,
    resources: Sequence[int | str | Fraction],
    assumptions: Iterable[tuple[str, str]] = (),
    evidence: Iterable[str] = (),
    *,
    identity: bool = False,
) -> Transform:
    if not source or not target:
        raise TransformError("MALFORMED_ENDPOINT")
    err = F(semantic_error)
    if err < 0:
        raise TransformError("NEGATIVE_ERROR")
    rs = tuple(F(x) for x in resources)
    if len(rs) != len(RESOURCE_COORDS):
        raise TransformError("RESOURCE_DIMENSION_MISMATCH")
    if any(x < 0 for x in rs):
        raise TransformError("NEGATIVE_RESOURCE")
    assumps = canonical_assumptions(assumptions)
    ev = canonical_evidence(evidence, identity=identity)
    t = Transform(source, target, err, rs, assumps, ev)
    if identity and not t.is_identity:
        raise TransformError("MALFORMED_IDENTITY")
    if not identity and t.evidence == (IDENTITY_EVIDENCE,):
        raise TransformError("IDENTITY_EVIDENCE_ON_ORDINARY_TRANSFORM")
    return t


def identity(node: str) -> Transform:
    return make_transform(
        node,
        node,
        0,
        (0,) * len(RESOURCE_COORDS),
        (),
        (IDENTITY_EVIDENCE,),
        identity=True,
    )


def _merge_assumptions(a: Transform, b: Transform) -> tuple[tuple[str, str], ...]:
    return canonical_assumptions((*a.assumptions, *b.assumptions))


def _merge_evidence(a: Transform, b: Transform) -> tuple[str, ...]:
    vals = tuple(x for x in (*a.evidence, *b.evidence) if x != IDENTITY_EVIDENCE)
    if not vals:
        return (IDENTITY_EVIDENCE,)
    return tuple(sorted(set(vals)))


def compose(first: Transform, second: Transform) -> Transform:
    """Return second o first; fail closed on incompatibility."""
    if first.target != second.source:
        raise TransformError("ENDPOINT_MISMATCH")
    assumps = _merge_assumptions(first, second)
    ev = _merge_evidence(first, second)
    err = first.semantic_error + second.semantic_error
    rs = tuple(a + b for a, b in zip(first.resources, second.resources, strict=True))
    is_id = (
        first.source == second.target
        and err == 0
        and all(x == 0 for x in rs)
        and not assumps
        and ev == (IDENTITY_EVIDENCE,)
    )
    return make_transform(
        first.source,
        second.target,
        err,
        rs,
        assumps,
        ev,
        identity=is_id,
    )


def scalar_burden(
    t: Transform,
    resource_weights: Sequence[int | str | Fraction],
    error_weight: int | str | Fraction,
) -> Fraction:
    ws = tuple(F(x) for x in resource_weights)
    ew = F(error_weight)
    if len(ws) != len(RESOURCE_COORDS):
        raise TransformError("WEIGHT_DIMENSION_MISMATCH")
    if any(w <= 0 for w in ws):
        raise TransformError("NONPOSITIVE_RESOURCE_WEIGHT")
    if ew < 0:
        raise TransformError("NEGATIVE_ERROR_WEIGHT")
    return sum((w * r for w, r in zip(ws, t.resources, strict=True)), F(0)) + ew * t.semantic_error


def shortest_distances(
    nodes: Iterable[str],
    edges: Iterable[Transform],
    source: str,
    resource_weights: Sequence[int | str | Fraction],
    error_weight: int | str | Fraction,
) -> dict[str, Fraction | float]:
    node_set = set(nodes)
    if source not in node_set:
        raise TransformError("UNKNOWN_SOURCE")
    adjacency: dict[str, list[tuple[Fraction, str]]] = {n: [] for n in node_set}
    for edge in edges:
        if edge.source not in node_set or edge.target not in node_set:
            raise TransformError("EDGE_OUTSIDE_NODE_SET")
        cost = scalar_burden(edge, resource_weights, error_weight)
        adjacency[edge.source].append((cost, edge.target))
    dist: dict[str, Fraction | float] = {n: inf for n in node_set}
    dist[source] = F(0)
    heap: list[tuple[Fraction, str]] = [(F(0), source)]
    while heap:
        d, u = heappop(heap)
        if dist[u] != d:
            continue
        for w, v in adjacency[u]:
            nd = d + w
            if dist[v] == inf or nd < dist[v]:
                dist[v] = nd
                heappush(heap, (nd, v))
    return dist


def all_pairs_distances(
    nodes: Sequence[str],
    edges: Sequence[Transform],
    resource_weights: Sequence[int | str | Fraction],
    error_weight: int | str | Fraction,
) -> dict[tuple[str, str], Fraction | float]:
    out: dict[tuple[str, str], Fraction | float] = {}
    for s in nodes:
        ds = shortest_distances(nodes, edges, s, resource_weights, error_weight)
        for t in nodes:
            out[(s, t)] = ds[t]
    return out


def triangle_violations(
    nodes: Sequence[str],
    distances: Mapping[tuple[str, str], Fraction | float],
) -> list[tuple[str, str, str]]:
    bad: list[tuple[str, str, str]] = []
    for a in nodes:
        for b in nodes:
            for c in nodes:
                ab, bc, ac = distances[(a, b)], distances[(b, c)], distances[(a, c)]
                if ab == inf or bc == inf:
                    continue
                rhs = ab + bc
                if ac == inf or ac > rhs:
                    bad.append((a, b, c))
    return bad


def pareto_dominates(a: Sequence[Fraction], b: Sequence[Fraction]) -> bool:
    if len(a) != len(b):
        raise TransformError("PARETO_DIMENSION_MISMATCH")
    return all(x <= y for x, y in zip(a, b, strict=True)) and any(x < y for x, y in zip(a, b, strict=True))


def finite_certificate() -> dict[str, object]:
    f = make_transform("A", "B", "1/10", (1, 2, 0), (("scope", "omega"),), ("e_f",))
    g = make_transform("B", "C", "1/20", (2, 0, 1), (("scope", "omega"), ("precision", "exact")), ("e_g",))
    h = make_transform("C", "D", "1/25", (0, 1, 1), (("scope", "omega"),), ("e_h",))
    left = compose(compose(f, g), h)
    right = compose(f, compose(g, h))
    assert left == right
    assert compose(identity("A"), f) == f
    assert compose(f, identity("B")) == f

    hostiles: dict[str, bool] = {}
    hostile_cases = {
        "endpoint_mismatch": lambda: compose(f, h),
        "negative_error": lambda: make_transform("A", "B", -1, (0, 0, 0), evidence=("e",)),
        "negative_resource": lambda: make_transform("A", "B", 0, (0, -1, 0), evidence=("e",)),
        "missing_evidence": lambda: make_transform("A", "B", 0, (0, 0, 0)),
        "resource_dimension": lambda: make_transform("A", "B", 0, (0, 0), evidence=("e",)),
        "assumption_conflict": lambda: compose(
            make_transform("A", "B", 0, (0, 0, 0), (("mode", "x"),), ("e1",)),
            make_transform("B", "C", 0, (0, 0, 0), (("mode", "y"),), ("e2",)),
        ),
    }
    for name, thunk in hostile_cases.items():
        try:
            thunk()
        except TransformError:
            hostiles[name] = True
        else:
            hostiles[name] = False
    assert all(hostiles.values())

    edges = [
        make_transform("A", "B", 0, (1, 0, 0), evidence=("ab",)),
        make_transform("B", "C", 0, (2, 0, 0), evidence=("bc",)),
        make_transform("A", "C", 0, (5, 0, 0), evidence=("ac",)),
        make_transform("C", "A", 0, (9, 0, 0), evidence=("ca",)),
        make_transform("C", "D", "1/10", (0, 1, 0), evidence=("cd",)),
    ]
    nodes = ("A", "B", "C", "D", "E")
    d = all_pairs_distances(nodes, edges, (1, 1, 1), 10)
    assert d[("A", "A")] == 0
    assert d[("A", "C")] == 3
    assert d[("C", "A")] == 9
    assert d[("A", "C")] != d[("C", "A")]
    assert d[("A", "E")] == inf
    assert triangle_violations(nodes, d) == []

    compute_light = (F(1), F(4), F(1))
    memory_light = (F(4), F(1), F(1))
    assert not pareto_dominates(compute_light, memory_light)
    assert not pareto_dominates(memory_light, compute_light)
    w_compute = (F(4), F(1), F(1))
    w_memory = (F(1), F(4), F(1))
    score = lambda r, w: sum((x * y for x, y in zip(r, w, strict=True)), F(0))
    assert score(compute_light, w_compute) < score(memory_light, w_compute)
    assert score(memory_light, w_memory) < score(compute_light, w_memory)

    return {
        "schema": "GMI_833_TRANSFORM_GEOMETRY_RESULT_V1",
        "claim_ceiling": CLAIM_CEILING,
        "verdict": "GREEN",
        "checks": {
            "left_identity": True,
            "right_identity": True,
            "associativity": True,
            "fail_closed_hostiles": all(hostiles.values()),
            "distance_identity_zero": d[("A", "A")] == 0,
            "triangle_violations_zero": len(triangle_violations(nodes, d)) == 0,
            "asymmetry_witness": d[("A", "C")] != d[("C", "A")],
            "unreachable_is_infinite": d[("A", "E")] == inf,
            "scalarization_reversal": True,
            "raw_pareto_incomparability": True,
        },
        "counts": {
            "nodes": len(nodes),
            "edges": len(edges),
            "ordered_pairs": len(nodes) ** 2,
            "ordered_triples_checked": len(nodes) ** 3,
            "hostile_cases": len(hostiles),
        },
        "witnesses": {
            "composite_error": f"{left.semantic_error.numerator}/{left.semantic_error.denominator}",
            "composite_resources": [str(x) for x in left.resources],
            "d_A_C": str(d[("A", "C")]),
            "d_C_A": str(d[("C", "A")]),
            "d_A_E": "INF",
            "hostiles": hostiles,
        },
        "forbidden_promotions": [
            "DEVELOPMENTAL_NATURALITY_PROVED",
            "FULL_INTELLIGENCE_SPACE_TOPOLOGY_PROVED",
            "GRAMMAR_REMINT_INVARIANCE_PROVED",
            "P3_KNOWN_FORM_RECOVERY_COMPLETE",
            "UNKNOWN_FORM_DISCOVERY_VALIDATED",
            "COMPLETE_GMI",
        ],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(finite_certificate(), sort_keys=True, separators=(",", ":")))
