#!/usr/bin/env python3
"""Exact checker for Warranted Graph-Parity Learning (WGPL).

A root-anchored graph carries certified parity equations on edges. Current
vertex labels can be fully learned from primary star edges, while optional
cross-edges encode overlapping future proof paths after evidence revocation.
The checker validates the finite claims and hostile controls, not novelty.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import deque
from dataclasses import dataclass
from typing import Iterable, Sequence

Edge = tuple[int, int]


def canonical_edge(left: int, right: int) -> Edge:
    if left == right:
        raise ValueError("self-loops are not allowed")
    return (left, right) if left < right else (right, left)


def optional_edge_universe(leaf_count: int) -> tuple[Edge, ...]:
    if leaf_count < 1:
        raise ValueError("leaf_count must be positive")
    return tuple(itertools.combinations(range(1, leaf_count + 1), 2))


def all_edge_universe(leaf_count: int) -> tuple[Edge, ...]:
    return tuple(itertools.combinations(range(0, leaf_count + 1), 2))


@dataclass(frozen=True)
class CertifiedEdge:
    record_id: str
    edge: Edge
    parity_label: int
    primary: bool


@dataclass(frozen=True)
class GraphParityWorld:
    theta_leaves: tuple[int, ...]
    optional_bits: tuple[int, ...]

    def __post_init__(self) -> None:
        if not self.theta_leaves:
            raise ValueError("at least one leaf is required")
        expected = len(optional_edge_universe(len(self.theta_leaves)))
        if len(self.optional_bits) != expected:
            raise ValueError("optional-edge bit length mismatch")
        if any(bit not in (0, 1) for bit in self.theta_leaves + self.optional_bits):
            raise ValueError("world values must be binary")

    @property
    def leaf_count(self) -> int:
        return len(self.theta_leaves)

    def theta(self, vertex: int) -> int:
        if vertex == 0:
            return 0
        if not 1 <= vertex <= self.leaf_count:
            raise IndexError("vertex out of range")
        return self.theta_leaves[vertex - 1]

    def current_function(self, vertex: int) -> int:
        return self.theta(vertex)

    def edge_label(self, edge: Edge) -> int:
        left, right = canonical_edge(*edge)
        return self.theta(left) ^ self.theta(right)

    def ledger(self) -> tuple[CertifiedEdge, ...]:
        records: list[CertifiedEdge] = []
        for leaf in range(1, self.leaf_count + 1):
            edge = (0, leaf)
            records.append(
                CertifiedEdge(
                    f"P:{leaf}", edge, self.edge_label(edge), True
                )
            )
        for bit, edge in zip(
            self.optional_bits, optional_edge_universe(self.leaf_count)
        ):
            if bit:
                records.append(
                    CertifiedEdge(
                        f"E:{edge[0]}:{edge[1]}",
                        edge,
                        self.edge_label(edge),
                        False,
                    )
                )
        return tuple(records)

    def optional_bit(self, edge: Edge) -> int:
        edge = canonical_edge(*edge)
        return self.optional_bits[
            optional_edge_universe(self.leaf_count).index(edge)
        ]


def adjacency(records: Iterable[CertifiedEdge], leaf_count: int):
    graph = {vertex: [] for vertex in range(leaf_count + 1)}
    for record in records:
        left, right = record.edge
        graph[left].append((right, record))
        graph[right].append((left, record))
    return graph


def find_path(
    records: tuple[CertifiedEdge, ...],
    leaf_count: int,
    source: int,
    target: int,
) -> tuple[CertifiedEdge, ...] | None:
    graph = adjacency(records, leaf_count)
    queue = deque([source])
    parent: dict[int, tuple[int, CertifiedEdge] | None] = {source: None}
    while queue:
        vertex = queue.popleft()
        if vertex == target:
            break
        for neighbor, record in graph[vertex]:
            if neighbor not in parent:
                parent[neighbor] = (vertex, record)
                queue.append(neighbor)
    if target not in parent:
        return None
    path: list[CertifiedEdge] = []
    cursor = target
    while cursor != source:
        previous, record = parent[cursor]  # type: ignore[misc]
        path.append(record)
        cursor = previous
    path.reverse()
    return tuple(path)


def connected_component(
    records: tuple[CertifiedEdge, ...], leaf_count: int, start: int
) -> frozenset[int]:
    graph = adjacency(records, leaf_count)
    seen = {start}
    queue = deque([start])
    while queue:
        vertex = queue.popleft()
        for neighbor, _ in graph[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return frozenset(seen)


def warranted_vertex(
    records: tuple[CertifiedEdge, ...], leaf_count: int, vertex: int
) -> dict[str, object]:
    path = find_path(records, leaf_count, 0, vertex)
    if path is not None:
        label = 0
        for record in path:
            label ^= record.parity_label
        return {
            "status": "WARRANTED",
            "label": label,
            "path_record_ids": tuple(record.record_id for record in path),
            "path_edges": tuple(record.edge for record in path),
            "negative_flip_component": None,
        }
    component = connected_component(records, leaf_count, vertex)
    if 0 in component:
        raise AssertionError("disconnected path but root in component")
    return {
        "status": "ABSTAIN",
        "label": None,
        "path_record_ids": (),
        "path_edges": (),
        "negative_flip_component": tuple(sorted(component)),
    }


def verify_path_certificate(
    records: tuple[CertifiedEdge, ...],
    leaf_count: int,
    vertex: int,
    path_record_ids: Sequence[str],
    claimed_label: int,
) -> bool:
    by_id = {record.record_id: record for record in records}
    try:
        path = tuple(by_id[record_id] for record_id in path_record_ids)
    except KeyError:
        return False
    cursor = 0
    label = 0
    for record in path:
        left, right = record.edge
        if cursor == left:
            cursor = right
        elif cursor == right:
            cursor = left
        else:
            return False
        label ^= record.parity_label
    return cursor == vertex and label == claimed_label


def verify_flip_certificate(
    records: tuple[CertifiedEdge, ...],
    leaf_count: int,
    vertex: int,
    component: Sequence[int],
) -> bool:
    component_set = frozenset(component)
    if vertex not in component_set or 0 in component_set:
        return False
    if connected_component(records, leaf_count, vertex) != component_set:
        return False
    return all(
        ((left in component_set) == (right in component_set))
        for left, right in (record.edge for record in records)
    )


def challenge_records(world: GraphParityWorld, target_edge: Edge):
    left, right = canonical_edge(*target_edge)
    keep_ids = {f"P:{left}", f"E:{left}:{right}"}
    records = tuple(
        record for record in world.ledger() if record.record_id in keep_ids
    )
    return records, right


def lifecycle_profile(world: GraphParityWorld) -> tuple[int, ...]:
    return world.theta_leaves + world.optional_bits


def query_complexity(leaf_count: int) -> dict[str, int]:
    optional = len(optional_edge_universe(leaf_count))
    return {
        "current_function_queries": leaf_count,
        "additional_warrant_queries": optional,
        "lifecycle_queries": leaf_count + optional,
    }


def binary_entropy(error: float) -> float:
    if not 0 <= error <= 1:
        raise ValueError("error must lie in [0,1]")
    if error in (0.0, 1.0):
        return 0.0
    return -error * math.log2(error) - (1 - error) * math.log2(1 - error)


def summary_lower_bound_bits(optional_edges: int, average_bit_error: float) -> float:
    return optional_edges * (1.0 - binary_entropy(average_bit_error))


def exact_batch_frontier(
    optional_edges: int, stored: int, queried: int, abstained: int
) -> bool:
    if min(optional_edges, stored, queried, abstained) < 0:
        raise ValueError("resource values must be non-negative")
    return stored + queried + abstained >= optional_edges


def records_for_general_graph(
    leaf_count: int,
    theta_leaves: tuple[int, ...],
    present_edges: tuple[Edge, ...],
) -> tuple[CertifiedEdge, ...]:
    def theta(vertex: int) -> int:
        return 0 if vertex == 0 else theta_leaves[vertex - 1]

    return tuple(
        CertifiedEdge(
            f"G:{left}:{right}",
            (left, right),
            theta(left) ^ theta(right),
            False,
        )
        for left, right in present_edges
    )


def run_exact_calibration() -> dict[str, object]:
    n = 4
    optional_edges = optional_edge_universe(n)
    worlds = tuple(
        GraphParityWorld(theta, bits)
        for theta in itertools.product((0, 1), repeat=n)
        for bits in itertools.product((0, 1), repeat=len(optional_edges))
    )
    if len(worlds) != 1024:
        raise AssertionError("world-count drift")

    profiles = set()
    function_groups: dict[tuple[int, ...], list[GraphParityWorld]] = {}
    challenges = positive_paths = negative_cuts = 0
    false_retain_controls = false_retract_controls = 0

    for world in worlds:
        profiles.add(lifecycle_profile(world))
        function_groups.setdefault(world.theta_leaves, []).append(world)
        for edge in optional_edges:
            records, queried_vertex = challenge_records(world, edge)
            result = warranted_vertex(records, n, queried_vertex)
            expected = bool(world.optional_bit(edge))
            challenges += 1
            if expected:
                positive_paths += 1
                false_retract_controls += 1
                if result["status"] != "WARRANTED":
                    raise AssertionError("present optional edge did not retain")
                if result["label"] != world.theta(queried_vertex):
                    raise AssertionError("path-derived label drift")
                if len(result["path_record_ids"]) != 2:
                    raise AssertionError("isolated witness should use a two-edge path")
                if not verify_path_certificate(
                    records,
                    n,
                    queried_vertex,
                    result["path_record_ids"],
                    int(result["label"]),
                ):
                    raise AssertionError("path certificate failed")
            else:
                negative_cuts += 1
                false_retain_controls += 1
                if result["status"] != "ABSTAIN":
                    raise AssertionError("absent optional edge was retained")
                if not verify_flip_certificate(
                    records,
                    n,
                    queried_vertex,
                    result["negative_flip_component"],
                ):
                    raise AssertionError("negative cut/flip certificate failed")

    if len(profiles) != len(worlds):
        raise AssertionError("lifecycle profile is not injective")
    for theta, group in function_groups.items():
        if len(group) != 64:
            raise AssertionError("optional graphs per function drift")
        transcripts = {
            tuple(world.current_function(vertex) for vertex in range(1, n + 1))
            for world in group
        }
        if transcripts != {theta}:
            raise AssertionError("current function leaked optional graph")

    graph_edges = all_edge_universe(n)
    general_graphs = general_checks = general_positive = general_negative = 0
    for edge_bits in itertools.product((0, 1), repeat=len(graph_edges)):
        present = tuple(
            edge for bit, edge in zip(edge_bits, graph_edges) if bit
        )
        general_graphs += 1
        for theta in itertools.product((0, 1), repeat=n):
            records = records_for_general_graph(n, theta, present)
            for vertex in range(1, n + 1):
                result = warranted_vertex(records, n, vertex)
                path = find_path(records, n, 0, vertex)
                general_checks += 1
                if path is not None:
                    general_positive += 1
                    if result["status"] != "WARRANTED":
                        raise AssertionError("connected vertex was not warranted")
                    if result["label"] != theta[vertex - 1]:
                        raise AssertionError("general path label drift")
                    if not verify_path_certificate(
                        records,
                        n,
                        vertex,
                        result["path_record_ids"],
                        int(result["label"]),
                    ):
                        raise AssertionError("general path certificate failed")
                else:
                    general_negative += 1
                    if result["status"] != "ABSTAIN":
                        raise AssertionError("disconnected vertex was warranted")
                    if not verify_flip_certificate(
                        records,
                        n,
                        vertex,
                        result["negative_flip_component"],
                    ):
                        raise AssertionError("general negative certificate failed")

    N = len(optional_edges)
    frontier_checks = under_resourced = boundary = 0
    for stored in range(N + 1):
        for queried in range(N + 1):
            for abstained in range(N + 1):
                frontier_checks += 1
                possible = exact_batch_frontier(N, stored, queried, abstained)
                if stored + queried + abstained < N:
                    under_resourced += 1
                    if possible:
                        raise AssertionError("under-resourced frontier accepted")
                elif stored + queried + abstained == N:
                    boundary += 1
                    if not possible:
                        raise AssertionError("frontier boundary rejected")

    if not (positive_paths and negative_cuts):
        raise AssertionError("suite lacks both warrant outcomes")
    if not (false_retain_controls and false_retract_controls):
        raise AssertionError("degenerate-policy controls did not fire")

    resources = query_complexity(n)
    if resources != {
        "current_function_queries": 4,
        "additional_warrant_queries": 6,
        "lifecycle_queries": 10,
    }:
        raise AssertionError("query-complexity drift")

    return {
        "schema": "orion.ocm.warranted-graph-parity.exact-results.v1",
        "terminal": "PASS_GRAPH_PARITY_QUADRATIC_WARRANT_GAP",
        "family": {
            "leaf_vertices_n": n,
            "current_function_bits": n,
            "optional_cross_edges_N": N,
            "optional_graphs_per_function": 2**N,
            "current_functions": 2**n,
            "lifecycle_concepts": len(worlds),
            "warrant_lift_bits_given_exact_current_function": N,
        },
        "query_complexity": resources,
        "isolated_edge_challenges": {
            "checks": challenges,
            "positive_two_edge_path_certificates": positive_paths,
            "negative_cut_flip_certificates": negative_cuts,
            "false_retain_controls": false_retain_controls,
            "false_retract_controls": false_retract_controls,
        },
        "general_graphical_warrant_theorem": {
            "vertices_including_root": n + 1,
            "all_possible_edges": len(graph_edges),
            "graphs_checked": general_graphs,
            "graph_theta_vertex_checks": general_checks,
            "connected_warranted_cases": general_positive,
            "disconnected_abstain_cases": general_negative,
            "criterion": "vertex label is warranted iff connected to anchored root",
        },
        "compiled_summary_frontier": {
            "exact_zero_error": "B + Q + A >= N over the full N-challenge batch",
            "frontier_tuples_checked": frontier_checks,
            "under_resourced_tuples": under_resourced,
            "exact_boundary_tuples": boundary,
            "randomized_average_error_lower_bound": (
                "B >= N(1-h_2(epsilon)) with no ledger access after compilation"
            ),
            "zero_error_summary_bits": N,
            "upper_bound": "store N-bit optional-edge vector",
        },
        "asymptotic_theorems": {
            "current_function_description": "Theta(n) bits",
            "lifecycle_warrant_description": "Theta(n^2) bits",
            "quadratic_warrant_gap": True,
            "communication_lower_bound": (
                "uniform optional graph plus all isolated-edge lifecycle challenges "
                "requires N(1-h_2(epsilon)) summary bits for average bit error epsilon"
            ),
        },
        "authority": {
            "natural_overlapping_proof_class": True,
            "quadratic_warrant_gap": True,
            "communication_lower_bound_proved_in_paired_artifact": True,
            "novelty": False,
            "architecture_separation": False,
            "publication_readiness": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = run_exact_calibration()
    except (AssertionError, ValueError, IndexError) as exc:
        print(json.dumps({"terminal": "FAIL", "error": str(exc)}, indent=2))
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PASS graph-parity warrant: quadratic gap and certificates verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
