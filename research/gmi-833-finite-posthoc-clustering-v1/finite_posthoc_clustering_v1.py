#!/usr/bin/env python3
"""Taxonomy-blind finite clustering core for issue #998.

This module deliberately contains generation, evaluation, retention, clustering,
and medoid selection only.  Reference mapping lives in a separate module loaded
after this module has returned completed clusters.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
from typing import Iterable


HERE = Path(__file__).resolve().parent
EDGE_THRESHOLD = Fraction(15, 2)


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


M = _load_module(
    "gmi833_f3_metric_parent",
    HERE.parent / "gmi-833-finite-morphology-metrics-v1" / "finite_morphology_metrics_v1.py",
)
F = M.F


def record_payload(record) -> dict[str, object]:
    if not isinstance(record, M.MorphologyRecord):
        raise ValueError("record_payload requires a validated morphology record")
    return {
        "observations": [[status, list(output)] for status, output in record.observations],
        "resources": list(record.resources),
        "history": [
            {
                "observations": [[status, list(output)] for status, output in milestone.observations],
                "resources": list(milestone.resources),
            }
            for milestone in record.history
        ],
    }


def record_key(record) -> str:
    return json.dumps(record_payload(record), sort_keys=True, separators=(",", ":"))


def record_digest(record) -> str:
    return sha256(record_key(record).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CandidateSnapshot:
    candidate_id: str
    canonical_code: tuple[object, ...]
    record: object

    def __post_init__(self) -> None:
        if type(self.candidate_id) is not str or not self.candidate_id.startswith("P"):
            raise ValueError("candidate_id must be a stable presentation identifier")
        if type(self.canonical_code) is not tuple:
            raise ValueError("canonical_code must be the retained exact presentation")
        if not isinstance(self.record, M.MorphologyRecord):
            raise ValueError("candidate snapshot requires a validated morphology record")


@dataclass(frozen=True)
class Cluster:
    cluster_id: str
    members: tuple[object, ...]
    medoid: object
    medoid_component_totals: tuple[int, int, int]

    def __post_init__(self) -> None:
        if type(self.cluster_id) is not str or not self.cluster_id.startswith("C"):
            raise ValueError("cluster_id must be a stable component identifier")
        if type(self.members) is not tuple or not self.members:
            raise ValueError("cluster must contain at least one record")
        if len(set(self.members)) != len(self.members):
            raise ValueError("cluster contains a duplicate record")
        if self.medoid not in self.members:
            raise ValueError("cluster medoid must be a member")
        if type(self.medoid_component_totals) is not tuple or len(self.medoid_component_totals) != 3:
            raise ValueError("medoid component totals must be a three-vector")


def generate_evaluate_retain() -> tuple[CandidateSnapshot, ...]:
    """Generate, evaluate, and retain every presentation before clustering."""
    programs = F.enumerate_candidates(F.StructuralBudget(2, 2))
    snapshots = tuple(
        CandidateSnapshot(
            candidate_id=f"P{index:04d}",
            canonical_code=program.canonical_code(),
            record=M.morphology_record(program),
        )
        for index, program in enumerate(programs, 1)
    )
    if len(snapshots) != 576:
        raise AssertionError("registered presentation census drifted")
    if len({row.candidate_id for row in snapshots}) != len(snapshots):
        raise AssertionError("candidate identifiers are not unique")
    if len({row.canonical_code for row in snapshots}) != len(snapshots):
        raise AssertionError("candidate retention ledger lost a presentation")
    return snapshots


def distinct_records(snapshots: Iterable[CandidateSnapshot]) -> tuple[object, ...]:
    rows = tuple(snapshots)
    if not rows or any(not isinstance(row, CandidateSnapshot) for row in rows):
        raise ValueError("distinct_records requires nonempty candidate snapshots")
    return tuple(sorted({row.record for row in rows}, key=record_key))


def component_totals(candidate, members: tuple[object, ...]) -> tuple[int, int, int]:
    if candidate not in members:
        raise ValueError("component total query must use a component member")
    return (
        sum(M.semantic_component(candidate.observations, other.observations) for other in members),
        sum(M.resource_component(candidate.resources, other.resources) for other in members),
        sum(M.developmental_component(candidate.history, other.history) for other in members),
    )


def weighted_total(vector: tuple[int, int, int], weights) -> Fraction:
    if type(vector) is not tuple or len(vector) != 3 or any(type(value) is not int or value < 0 for value in vector):
        raise ValueError("weighted_total requires a natural three-vector")
    if not isinstance(weights, M.MetricWeights):
        raise ValueError("weighted_total requires validated metric weights")
    return sum((weight * value for weight, value in zip(weights.as_tuple(), vector)), Fraction(0))


def threshold_edges(
    records: tuple[object, ...],
    weights=M.BASE_WEIGHTS,
    threshold: Fraction = EDGE_THRESHOLD,
) -> tuple[tuple[int, int], ...]:
    if type(records) is not tuple or not records or any(not isinstance(row, M.MorphologyRecord) for row in records):
        raise ValueError("threshold graph requires nonempty validated records")
    if len(set(records)) != len(records):
        raise ValueError("threshold graph carrier must be duplicate-free")
    if not isinstance(weights, M.MetricWeights):
        raise ValueError("threshold graph requires validated weights")
    if type(threshold) is not Fraction or threshold <= 0:
        raise ValueError("threshold must be a positive exact Fraction")
    return tuple(
        (left, right)
        for left in range(len(records))
        for right in range(left + 1, len(records))
        if M.morphology_distance(records[left], records[right], weights) <= threshold
    )


def cluster_records(
    records: tuple[object, ...],
    weights=M.BASE_WEIGHTS,
    threshold: Fraction = EDGE_THRESHOLD,
) -> tuple[Cluster, ...]:
    """Return deterministic threshold-graph components and medoids."""
    ordered = tuple(sorted(records, key=record_key))
    edges = threshold_edges(ordered, weights, threshold)
    neighbours = {index: set() for index in range(len(ordered))}
    for left, right in edges:
        neighbours[left].add(right)
        neighbours[right].add(left)

    seen: set[int] = set()
    raw_components: list[tuple[object, ...]] = []
    for seed in range(len(ordered)):
        if seed in seen:
            continue
        pending = [seed]
        seen.add(seed)
        indices: list[int] = []
        while pending:
            current = pending.pop()
            indices.append(current)
            for neighbour in sorted(neighbours[current], reverse=True):
                if neighbour not in seen:
                    seen.add(neighbour)
                    pending.append(neighbour)
        raw_components.append(tuple(ordered[index] for index in sorted(indices)))

    staged: list[tuple[str, tuple[str, ...], tuple[object, ...], object, tuple[int, int, int]]] = []
    for members in raw_components:
        ranked = []
        for candidate in members:
            vector = component_totals(candidate, members)
            ranked.append((weighted_total(vector, weights), record_key(candidate), candidate, vector))
        _, medoid_key, medoid, vector = min(ranked)
        staged.append((medoid_key, tuple(record_key(row) for row in members), members, medoid, vector))

    result = tuple(
        Cluster(f"C{index:04d}", members, medoid, vector)
        for index, (_, _, members, medoid, vector) in enumerate(
            sorted(staged, key=lambda row: (row[0], row[1])), 1
        )
    )
    if sum(len(row.members) for row in result) != len(ordered):
        raise AssertionError("clustering did not partition the carrier")
    if set().union(*(set(row.members) for row in result)) != set(ordered):
        raise AssertionError("clustering changed the carrier")
    return result


def record_cluster_index(clusters: tuple[Cluster, ...]) -> dict[object, str]:
    if type(clusters) is not tuple or not clusters or any(not isinstance(row, Cluster) for row in clusters):
        raise ValueError("record_cluster_index requires nonempty validated clusters")
    index: dict[object, str] = {}
    for cluster in clusters:
        for record in cluster.members:
            if record in index:
                raise ValueError("clusters overlap")
            index[record] = cluster.cluster_id
    return index
