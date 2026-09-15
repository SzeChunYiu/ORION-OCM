from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import inf
import json
from typing import Iterable, Mapping, Sequence

CLAIM_CEILING = "GMI_PARETO_TRANSFORM_ALGEBRA_AND_FORWARD_TOPOLOGY_AT_REGISTERED_FINITE_SCOPE"

Vec = tuple[Fraction, ...]
Frontier = tuple[Vec, ...]


class ParetoError(ValueError):
    pass


def F(x: int | str | Fraction) -> Fraction:
    return x if isinstance(x, Fraction) else Fraction(x)


def make_vec(values: Sequence[int | str | Fraction]) -> Vec:
    v = tuple(F(x) for x in values)
    if not v:
        raise ParetoError("EMPTY_VECTOR")
    if any(x < 0 for x in v):
        raise ParetoError("NEGATIVE_BURDEN")
    return v


def strictly_dominates(a: Vec, b: Vec) -> bool:
    if len(a) != len(b):
        raise ParetoError("DIMENSION_MISMATCH")
    return all(x <= y for x, y in zip(a, b, strict=True)) and any(x < y for x, y in zip(a, b, strict=True))


def pareto(items: Iterable[Vec]) -> Frontier:
    vals = tuple(sorted(set(tuple(v) for v in items)))
    if not vals:
        return ()
    dim = len(vals[0])
    if dim == 0 or any(len(v) != dim for v in vals):
        raise ParetoError("DIMENSION_MISMATCH")
    if any(any(x < 0 for x in v) for v in vals):
        raise ParetoError("NEGATIVE_BURDEN")
    return tuple(v for v in vals if not any(strictly_dominates(u, v) for u in vals if u != v))


def choice(a: Frontier, b: Frontier) -> Frontier:
    return pareto((*a, *b))


def compose(a: Frontier, b: Frontier) -> Frontier:
    if not a or not b:
        return ()
    da = len(a[0])
    db = len(b[0])
    if da != db:
        raise ParetoError("DIMENSION_MISMATCH")
    return pareto(
        tuple(tuple(x + y for x, y in zip(va, vb, strict=True)) for va in a for vb in b)
    )


def zero_frontier(dim: int) -> Frontier:
    if dim <= 0:
        raise ParetoError("BAD_DIMENSION")
    return (tuple(F(0) for _ in range(dim)),)


def grid_frontiers(max_coordinate: int = 2, dim: int = 2) -> tuple[Frontier, ...]:
    if max_coordinate < 0 or dim <= 0:
        raise ParetoError("BAD_GRID")
    grid = tuple(tuple(F(x) for x in p) for p in product(range(max_coordinate + 1), repeat=dim))
    if len(grid) > 16:
        raise ParetoError("GRID_TOO_LARGE_FOR_EXACT_SUBSET_ENUMERATION")
    fronts: set[Frontier] = set()
    for mask in range(1 << len(grid)):
        subset = tuple(grid[i] for i in range(len(grid)) if mask & (1 << i))
        fronts.add(pareto(subset))
    return tuple(sorted(fronts, key=lambda x: (len(x), x)))


def exhaustive_algebra_certificate(frontiers: Sequence[Frontier], dim: int) -> dict[str, int]:
    z = zero_frontier(dim)
    empty: Frontier = ()
    unary = pair = triple = 0
    for a in frontiers:
        assert pareto(a) == a
        assert choice(a, empty) == a == choice(empty, a)
        assert compose(a, z) == a == compose(z, a)
        assert compose(a, empty) == empty == compose(empty, a)
        assert choice(a, a) == a
        unary += 5
    for a in frontiers:
        for b in frontiers:
            assert choice(a, b) == choice(b, a)
            pair += 1
            for c in frontiers:
                assert choice(choice(a, b), c) == choice(a, choice(b, c))
                assert compose(compose(a, b), c) == compose(a, compose(b, c))
                assert compose(a, choice(b, c)) == choice(compose(a, b), compose(a, c))
                assert compose(choice(a, b), c) == choice(compose(a, c), compose(b, c))
                triple += 4
    return {"unary_law_assertions": unary, "pair_law_assertions": pair, "triple_law_assertions": triple}


def path_closure(
    nodes: Sequence[str],
    edges: Mapping[tuple[str, str], Frontier],
    dim: int,
) -> dict[tuple[str, str], Frontier]:
    if not nodes or len(set(nodes)) != len(nodes):
        raise ParetoError("MALFORMED_NODES")
    node_set = set(nodes)
    h: dict[tuple[str, str], Frontier] = {(i, j): () for i in nodes for j in nodes}
    z = zero_frontier(dim)
    for n in nodes:
        h[(n, n)] = z
    for (i, j), frontier in edges.items():
        if i not in node_set or j not in node_set:
            raise ParetoError("EDGE_ENDPOINT_UNKNOWN")
        if frontier and any(len(v) != dim for v in frontier):
            raise ParetoError("DIMENSION_MISMATCH")
        h[(i, j)] = choice(h[(i, j)], pareto(frontier))
    # Floyd-Warshall over the Pareto idempotent semiring. Nonnegative cycles cannot
    # improve a path after Pareto reduction, so finite closure is sufficient here.
    for k in nodes:
        for i in nodes:
            for j in nodes:
                h[(i, j)] = choice(h[(i, j)], compose(h[(i, k)], h[(k, j)]))
    return h


def dot(v: Vec, weights: Vec) -> Fraction:
    if len(v) != len(weights):
        raise ParetoError("DIMENSION_MISMATCH")
    return sum((x * w for x, w in zip(v, weights, strict=True)), F(0))


def scalar_distance(frontier: Frontier, weights: Vec) -> Fraction | float:
    if any(w <= 0 for w in weights):
        raise ParetoError("NONPOSITIVE_SCALAR_WEIGHT")
    if not frontier:
        return inf
    return min(dot(v, weights) for v in frontier)


def scalar_triangle_violations(
    nodes: Sequence[str],
    closure: Mapping[tuple[str, str], Frontier],
    weights: Vec,
) -> list[tuple[str, str, str]]:
    bad: list[tuple[str, str, str]] = []
    for a in nodes:
        for b in nodes:
            for c in nodes:
                ab = scalar_distance(closure[(a, b)], weights)
                bc = scalar_distance(closure[(b, c)], weights)
                ac = scalar_distance(closure[(a, c)], weights)
                if ab == inf or bc == inf:
                    continue
                if ac == inf or ac > ab + bc:
                    bad.append((a, b, c))
    return bad


def strictly_within(v: Vec, budget: Vec) -> bool:
    if len(v) != len(budget):
        raise ParetoError("DIMENSION_MISMATCH")
    return all(x < b for x, b in zip(v, budget, strict=True))


def budget_ball(
    nodes: Sequence[str],
    closure: Mapping[tuple[str, str], Frontier],
    source: str,
    budget: Vec,
) -> frozenset[str]:
    if source not in set(nodes):
        raise ParetoError("UNKNOWN_SOURCE")
    if any(b <= 0 for b in budget):
        raise ParetoError("NONPOSITIVE_BUDGET")
    return frozenset(
        target
        for target in nodes
        if any(strictly_within(v, budget) for v in closure[(source, target)])
    )


def finite_ball_basis_certificate(
    nodes: Sequence[str],
    closure: Mapping[tuple[str, str], Frontier],
    budgets: Sequence[Vec],
) -> dict[str, object]:
    cases = 0
    basis: set[frozenset[str]] = {frozenset()}
    for x in nodes:
        for b in budgets:
            outer = budget_ball(nodes, closure, x, b)
            basis.add(outer)
            assert x in outer  # zero identity burden is strictly below every positive budget
            for y in outer:
                witnesses = tuple(v for v in closure[(x, y)] if strictly_within(v, b))
                assert witnesses
                v = witnesses[0]
                residual = tuple(bi - vi for bi, vi in zip(b, v, strict=True))
                assert all(r > 0 for r in residual)
                inner = budget_ball(nodes, closure, y, residual)
                assert inner <= outer
                cases += 1

    # The registered finite ball family generates a topology. Enumerate all subsets
    # and retain exactly those satisfying the basis-open criterion.
    node_tuple = tuple(nodes)
    subsets = tuple(
        frozenset(node_tuple[i] for i in range(len(node_tuple)) if mask & (1 << i))
        for mask in range(1 << len(node_tuple))
    )
    opens = tuple(
        u for u in subsets
        if all(any(x in b and b <= u for b in basis) for x in u)
    )
    open_set = set(opens)
    assert frozenset() in open_set and frozenset(node_tuple) in open_set
    for u in opens:
        for v in opens:
            assert (u | v) in open_set
            assert (u & v) in open_set
    return {
        "basis_condition_cases": cases,
        "distinct_sampled_balls": len(basis),
        "generated_open_sets": len(opens),
        "generated_topology_pair_checks": len(opens) ** 2,
    }


def _fixture() -> tuple[tuple[str, ...], dict[tuple[str, str], Frontier]]:
    nodes = ("A", "B", "C", "D")
    edges = {
        ("A", "B"): pareto((make_vec((0, 0)),)),
        ("B", "C"): pareto((make_vec((1, 1)),)),
        ("A", "C"): pareto((make_vec((5, 0)), make_vec((0, 5)))),
        ("C", "A"): pareto((make_vec((6, 6)),)),
    }
    return nodes, edges


def serial_frontier(frontier: Frontier) -> list[list[str]]:
    return [[str(x) for x in v] for v in frontier]


def finite_certificate() -> dict[str, object]:
    fronts = grid_frontiers(2, 2)
    assert len(fronts) == 20
    algebra = exhaustive_algebra_certificate(fronts, 2)

    nodes, edges = _fixture()
    h = path_closure(nodes, edges, 2)
    assert h[("A", "C")] == pareto((make_vec((0, 5)), make_vec((1, 1)), make_vec((5, 0))))
    assert h[("A", "D")] == () and h[("D", "A")] == ()
    assert h[("A", "B")] == pareto((make_vec((0, 0)),))

    weights = (make_vec((1, 1)), make_vec((3, 1)), make_vec((1, 3)))
    triangle_counts = []
    for w in weights:
        bad = scalar_triangle_violations(nodes, h, w)
        assert bad == []
        triangle_counts.append(len(nodes) ** 3)
    assert scalar_distance(h[("A", "B")], weights[0]) == 0
    assert scalar_distance(h[("B", "A")], weights[0]) == 14
    assert scalar_distance(h[("A", "D")], weights[0]) == inf

    budgets = tuple(make_vec(p) for p in product(range(1, 9), repeat=2))
    topo = finite_ball_basis_certificate(nodes, h, budgets)

    f1 = pareto((make_vec((1, 4)), make_vec((4, 1))))
    f2 = pareto((make_vec((1, 4)), make_vec((2, 3))))
    assert f1 != f2
    assert scalar_distance(f1, make_vec((1, 1))) == scalar_distance(f2, make_vec((1, 1))) == 5
    assert scalar_distance(f1, make_vec((1, 4))) == 8
    assert scalar_distance(f2, make_vec((1, 4))) == 14
    coord_inf = tuple(min(v[i] for v in f1) for i in range(2))
    assert coord_inf == make_vec((1, 1)) and coord_inf not in f1

    return {
        "schema": "GMI_833_PARETO_TOPOLOGY_RESULT_V1",
        "claim_ceiling": CLAIM_CEILING,
        "verdict": "GREEN",
        "checks": {
            "pareto_algebra_exact": True,
            "multiobjective_path_closure": True,
            "scalar_triangle_all_registered_weights": True,
            "directed_zero_cost_asymmetry_witness": True,
            "unreachable_frontier_preserved": True,
            "forward_budget_ball_basis": True,
            "finite_generated_topology_axioms": True,
            "scalarization_information_loss_hostile": True,
            "coordinatewise_infimum_unattainable_hostile": True,
        },
        "counts": {
            "distinct_grid_frontiers": len(fronts),
            **algebra,
            "graph_nodes": len(nodes),
            "graph_ordered_pairs": len(nodes) ** 2,
            "scalar_weight_vectors": len(weights),
            "scalar_triangle_triples_checked": sum(triangle_counts),
            "positive_budget_vectors": len(budgets),
            **topo,
        },
        "witnesses": {
            "A_to_C_pareto": serial_frontier(h[("A", "C")]),
            "A_to_B_zero_burden": serial_frontier(h[("A", "B")]),
            "B_to_A_burden": serial_frontier(h[("B", "A")]),
            "A_to_D": "UNREACHABLE_EMPTY_FRONTIER",
            "scalar_collision_frontier_1": serial_frontier(f1),
            "scalar_collision_frontier_2": serial_frontier(f2),
            "unattainable_coordinatewise_infimum": [str(x) for x in coord_inf],
        },
        "forbidden_promotions": [
            "COMPLETE_QUANTALE_ENRICHMENT_PROVED",
            "UNIVERSAL_INTELLIGENCE_SPACE_TOPOLOGY_PROVED",
            "TOPOLOGY_IS_HAUSDORFF_PROVED",
            "TOPOLOGY_IS_MANIFOLD_PROVED",
            "UNIVERSAL_RESOURCE_SCALARIZATION_PROVED",
            "KNOWN_FORM_P3_RECOVERY_COMPLETE",
            "COMPLETE_GMI",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(finite_certificate(), sort_keys=True, separators=(",", ":")))
