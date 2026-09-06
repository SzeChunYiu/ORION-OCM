"""Snapshot-bound extraction preparation and query work accounting.

Only structural adjacency is retained between calls. Liveness is evaluated anew
for each revoked-evidence set; nested metadata and registry values are not cached.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

from .space import KnowledgeSpace
from .warrant import CannotCheck


@dataclass(frozen=True, slots=True)
class IndexedExtractionWork:
    incident_postings_examined: int
    distinct_edges_examined: int
    objective_evaluations: int
    cold_incident_index_build: bool
    index_probes: int = 0
    outgoing_postings_examined: int = 0
    atom_warrant_checks: int = 0
    edge_warrant_checks: int = 0
    incidence_memberships_examined: int = 0
    distinct_atoms_examined: int = 0
    seed_entries_examined: int = 0
    dense_seed_entries_examined: int = 0
    closure_expansions: int = 0
    candidate_evaluations: int = 0
    total_objects: int = 0
    total_relations: int = 0
    cold_build_work: Mapping[str, int | bool] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {name: dict(value) if isinstance(value, Mapping) else value
                for name in self.__dataclass_fields__ if (value := getattr(self, name)) is not None}


class ExtractionIndex:
    """Prepare the existing incident/outgoing indexes once for one immutable space.

    ``build_work`` records construction separately from query work. Passing this
    object to a query does not charge that construction again. A structurally
    replaced space requires a new preparation, even when its IDs are unchanged.
    This is object-bound index validity, not a content digest or warrant receipt.
    """

    def __init__(self, ks: KnowledgeSpace):
        self._space, self._atoms, self._edges = ks, ks.atoms, ks.hyperedges
        atom_cold = "_atom_index" not in ks.__dict__
        incident_cold = "_incident_index" not in ks.__dict__
        outgoing_cold = "_outgoing_index" not in ks.__dict__
        self.atoms = ks.atom_view
        self.incident = MappingProxyType(ks._incident_index)
        self.outgoing = MappingProxyType(ks._outgoing_index)
        self.build_work = MappingProxyType({
            "total_objects": len(ks.atoms), "total_relations": len(ks.hyperedges),
            "cold_atom_index_build": atom_cold,
            "cold_incident_index_build": incident_cold,
            "cold_outgoing_index_build": outgoing_cold,
            "atom_entries_built": len(ks.atoms) if atom_cold else 0,
            "edge_entries_scanned": len(ks.hyperedges) * (incident_cold + outgoing_cold),
            "incident_postings_built": sum(map(len, self.incident.values())) if incident_cold else 0,
            "outgoing_postings_built": sum(map(len, self.outgoing.values())) if outgoing_cold else 0,
            "accounting_rows_examined": (len(self.incident) if incident_cold else 0)
                + (len(self.outgoing) if outgoing_cold else 0),
        })

    def check(self, ks: KnowledgeSpace) -> None:
        if ks is not self._space or ks.atoms is not self._atoms or ks.hyperedges is not self._edges:
            raise CannotCheck("EXTRACTION_INDEX_SNAPSHOT_MISMATCH")


class ExtractionRun:
    """Per-call counters; atom/edge liveness memoization never crosses queries.

    Distinct atoms counts IDs inspected by adjacency, incidence, warrant or prize operations.
    Membership work counts each explicit edge-incidence/head visit, including repeats.
    Counters are operations/cardinalities, not CPU instructions or resident bytes.
    """

    def __init__(self, ks, index, revoked):
        self.build_work = {} if index is not None else None
        self.index = index if index is not None else ExtractionIndex(ks)
        self.index.check(ks)
        if self.build_work is None:
            self.build_work = self.index.build_work
        self.revoked = frozenset(revoked)
        self.counts = Counter()
        self.atoms, self.edges = set(), set()
        self._atom_live, self._edge_live = {}, {}

    def live_atom(self, atom_id):
        self.atoms.add(atom_id)
        if atom_id not in self._atom_live:
            self.counts["atom_warrant_checks"] += 1
            self._atom_live[atom_id] = self.index.atoms[atom_id].is_live(self.revoked)
        return self._atom_live[atom_id]

    def live_edge(self, edge):
        self.edges.add(edge.edge_id)
        if edge.edge_id not in self._edge_live:
            self.counts["edge_warrant_checks"] += 1
            self._edge_live[edge.edge_id] = edge.warrant.is_live(self.revoked)
        return self._edge_live[edge.edge_id]

    def incidences(self, edge):
        self.edges.add(edge.edge_id)
        incident = edge.incident
        self.atoms.update(incident)
        self.counts["incidence_memberships_examined"] += len(incident)
        return incident

    def adjacent(self, atom_id, *, outgoing=False):
        self.atoms.add(atom_id)
        self.counts["index_probes"] += 1
        rows = (self.index.outgoing if outgoing else self.index.incident).get(atom_id, ())
        self.counts["outgoing_postings_examined" if outgoing else "incident_postings_examined"] += len(rows)
        self.edges.update(edge.edge_id for edge in rows)
        return rows

    def touching(self, atoms):
        found = {}
        for atom_id in atoms:
            found.update((edge.edge_id, edge) for edge in self.adjacent(atom_id))
        return found.values()

    def finish(self):
        return IndexedExtractionWork(
            incident_postings_examined=self.counts["incident_postings_examined"],
            distinct_edges_examined=len(self.edges),
            objective_evaluations=self.counts["objective_evaluations"],
            cold_incident_index_build=bool(self.build_work.get("cold_incident_index_build", False)),
            distinct_atoms_examined=len(self.atoms),
            total_objects=len(self.index._atoms), total_relations=len(self.index._edges),
            cold_build_work=MappingProxyType(dict(self.build_work)),
            **{name: self.counts[name] for name in (
                "index_probes", "outgoing_postings_examined", "atom_warrant_checks", "edge_warrant_checks",
                "incidence_memberships_examined", "seed_entries_examined", "dense_seed_entries_examined",
                "closure_expansions", "candidate_evaluations")})
