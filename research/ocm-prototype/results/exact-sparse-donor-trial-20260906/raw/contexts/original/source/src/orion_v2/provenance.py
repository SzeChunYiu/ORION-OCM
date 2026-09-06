from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class InheritanceRelation(str, Enum):
    DERIVES = "DERIVES"; COPIES = "COPIES"; REFINES = "REFINES"; TRANSLATES = "TRANSLATES"; COMPOSES = "COMPOSES"; CALIBRATES_FROM = "CALIBRATES_FROM"; EVALUATED_BY = "EVALUATED_BY"


@dataclass(frozen=True, slots=True)
class ProvenanceNode:
    node_id: str; kind: str; epoch: str; content_digest: str = ""
    def __post_init__(self) -> None:
        if not self.node_id.strip() or not self.kind.strip() or not self.epoch.strip(): raise ValueError("node_id, kind and epoch must be non-blank")


@dataclass(frozen=True, slots=True)
class ProvenanceEdge:
    parent_id: str; child_id: str; relation: InheritanceRelation; component: str; mapping_id: str = ""
    def __post_init__(self) -> None:
        if self.parent_id == self.child_id or any(not value.strip() for value in (self.parent_id, self.child_id, self.component)): raise ValueError("provenance edges require distinct endpoints and a component")
        object.__setattr__(self, "relation", InheritanceRelation(self.relation))


@dataclass(frozen=True, slots=True)
class ReticulateProvenance:
    nodes: tuple[ProvenanceNode, ...]; edges: tuple[ProvenanceEdge, ...]
    def __post_init__(self) -> None:
        node_ids = [node.node_id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)): raise ValueError("provenance node identities must be unique")
        known = set(node_ids)
        for edge in self.edges:
            if edge.parent_id not in known or edge.child_id not in known: raise ValueError("provenance edge references an unknown node")
        self._assert_acyclic()
    def _assert_acyclic(self) -> None:
        children = {node.node_id: set() for node in self.nodes}; indegree = {node.node_id: 0 for node in self.nodes}
        for edge in self.edges:
            if edge.child_id not in children[edge.parent_id]: children[edge.parent_id].add(edge.child_id); indegree[edge.child_id] += 1
        queue = [node for node, degree in indegree.items() if degree == 0]; visited = 0
        while queue:
            node = queue.pop(); visited += 1
            for child in children[node]:
                indegree[child] -= 1
                if indegree[child] == 0: queue.append(child)
        if visited != len(indegree): raise ValueError("reticulate provenance must be acyclic")
    def parents(self, node_id: str, *, component: str | None = None) -> tuple[str, ...]:
        return tuple(sorted(edge.parent_id for edge in self.edges if edge.child_id == node_id and (component is None or edge.component == component)))
    def descendants(self, node_ids: tuple[str, ...], *, component: str | None = None) -> tuple[str, ...]:
        known = {node.node_id for node in self.nodes}
        if not set(node_ids) <= known: raise ValueError("unknown provenance root")
        children = {node: set() for node in known}
        for edge in self.edges:
            if component is None or edge.component == component: children[edge.parent_id].add(edge.child_id)
        reached = set(node_ids); stack = list(node_ids)
        while stack:
            node = stack.pop()
            for child in children[node] - reached: reached.add(child); stack.append(child)
        return tuple(sorted(reached - set(node_ids)))
    def affected_by_revocation(self, node_id: str, *, component: str | None = None) -> tuple[str, ...]:
        return (node_id, *self.descendants((node_id,), component=component))
