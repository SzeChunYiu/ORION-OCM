from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class DependenceKind(str, Enum):
    SHARED_SOURCE = "SHARED_SOURCE"
    SHARED_DATA = "SHARED_DATA"
    SHARED_MODEL = "SHARED_MODEL"
    SHARED_INSTRUMENT = "SHARED_INSTRUMENT"
    COPYING_OR_DERIVATION = "COPYING_OR_DERIVATION"
    SOCIAL_ORGANIZATIONAL = "SOCIAL_ORGANIZATIONAL"
    COMMON_CAUSE = "COMMON_CAUSE"
    DECLARED_INDEPENDENT = "DECLARED_INDEPENDENT"


@dataclass(frozen=True, slots=True)
class EvidenceUnit:
    evidence_id: str
    claim_id: str
    source_id: str
    method_id: str
    data_id: str = ""
    model_id: str = ""
    instrument_id: str = ""
    supports: bool = True

    def __post_init__(self) -> None:
        for name in ("evidence_id", "claim_id", "source_id", "method_id"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must be non-blank")


@dataclass(frozen=True, slots=True)
class DependenceEdge:
    left_id: str
    right_id: str
    kind: DependenceKind
    witness_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.left_id.strip() or not self.right_id.strip() or self.left_id == self.right_id:
            raise ValueError("dependence edges require distinct non-blank endpoints")
        object.__setattr__(self, "kind", DependenceKind(self.kind))
        if not self.witness_ids or any(not value.strip() for value in self.witness_ids):
            raise ValueError("dependence edges require witness identities")


@dataclass(frozen=True, slots=True)
class EvidenceDependenceAssessment:
    claim_id: str
    supporting_unit_ids: tuple[str, ...]
    dependence_component_ids: tuple[tuple[str, ...], ...]
    conservative_independent_support_count: int
    naive_support_count: int
    dependence_unknown: bool
    authority_granted: bool = False

    def __post_init__(self) -> None:
        if self.authority_granted:
            raise ValueError("dependence assessment cannot grant claim authority")


def _components(nodes: set[str], edges: Iterable[DependenceEdge]) -> tuple[tuple[str, ...], ...]:
    adjacency = {node: set() for node in nodes}
    for edge in edges:
        if edge.kind is DependenceKind.DECLARED_INDEPENDENT:
            continue
        if edge.left_id not in nodes or edge.right_id not in nodes:
            raise ValueError("dependence edge references unknown evidence")
        adjacency[edge.left_id].add(edge.right_id)
        adjacency[edge.right_id].add(edge.left_id)
    result: list[tuple[str, ...]] = []
    unseen = set(nodes)
    while unseen:
        root = min(unseen); stack = [root]; component: set[str] = set()
        while stack:
            node = stack.pop()
            if node in component: continue
            component.add(node); stack.extend(adjacency[node] - component)
        unseen -= component; result.append(tuple(sorted(component)))
    return tuple(sorted(result))


def assess_evidence_dependence(units: tuple[EvidenceUnit, ...], edges: tuple[DependenceEdge, ...], *, require_complete_pair_disposition: bool = False) -> EvidenceDependenceAssessment:
    if not units: raise ValueError("at least one evidence unit is required")
    ids = [unit.evidence_id for unit in units]
    if len(ids) != len(set(ids)): raise ValueError("evidence identities must be unique")
    claims = {unit.claim_id for unit in units}
    if len(claims) != 1: raise ValueError("all evidence units must address the same claim")
    supporting = tuple(sorted(unit.evidence_id for unit in units if unit.supports)); nodes = set(supporting)
    relevant_edges = tuple(edge for edge in edges if edge.left_id in nodes or edge.right_id in nodes)
    components = _components(nodes, relevant_edges) if nodes else ()
    disposed_pairs = {frozenset((edge.left_id, edge.right_id)) for edge in edges if edge.left_id in nodes and edge.right_id in nodes}
    all_pairs = {frozenset((left, right)) for index, left in enumerate(supporting) for right in supporting[index + 1:]}
    unknown = require_complete_pair_disposition and disposed_pairs != all_pairs
    return EvidenceDependenceAssessment(next(iter(claims)), supporting, components, 0 if unknown else len(components), len(supporting), unknown)
