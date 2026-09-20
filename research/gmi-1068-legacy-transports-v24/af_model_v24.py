"""Ordered labelled AF graphs retain stable slots and shared action provenance."""
from dataclasses import dataclass
from core_v24 import need, index, old_af

POLICIES = ("C0", "C1", "ID", "NOT")
TAGS = tuple(old_af.PROVENANCE_TAGS)


@dataclass(frozen=True)
class AFGraph:
    rows: tuple
    provenance: tuple

    def __post_init__(self):
        need(type(self.rows) is tuple and len(self.rows) == 4, "four policy rows required")
        actions = set()
        for row in self.rows:
            need(type(row) is tuple, "canonical slot tuple required")
            for edge in row:
                if edge is None:
                    continue
                need(type(edge) is tuple and len(edge) == 2, "label/destination edge required")
                action, destination = edge
                need(type(action) is str and action, "nonempty action label required")
                index(destination, 4)
                actions.add(action)
        need(type(self.provenance) is tuple, "canonical provenance tuple required")
        seen = set()
        for entry in self.provenance:
            need(type(entry) is tuple and len(entry) == 2, "provenance pair required")
            action, tags = entry
            need(type(action) is str and action and action not in seen, "unique provenance key required")
            need(type(tags) is tuple and tags, "nonempty provenance tags required")
            need(all(type(tag) is str and tag in TAGS for tag in tags), "unregistered provenance tag")
            seen.add(action)
        need(actions <= seen, "action provenance missing")


def graph_checked(graph):
    need(type(graph) is AFGraph, "validated AFGraph required")
    return graph


def legacy_inputs(graph):
    graph_checked(graph)
    transitions = {POLICIES[i]: tuple((edge[0], POLICIES[edge[1]]) for edge in row if edge is not None)
                   for i, row in enumerate(graph.rows)}
    return transitions, dict(graph.provenance)
