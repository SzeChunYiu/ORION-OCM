"""Checkable minimum-cost and unreachable certificates for a finite proof graph.

A graph certificate never establishes completeness of the extracted bank, the
native rule inventory, mathematical impossibility, or current OCM authority.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any


def _identity(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    allow_nan=False).encode()).hexdigest()


def _graph(n: int, actions: list[dict], initial: list[int]) -> dict:
    if type(n) is not int or n < 1:
        raise ValueError("positive finite graph size required")
    if type(actions) is not list or type(initial) is not list:
        raise ValueError("explicit action and initial-state lists required")
    def vertex(x):
        if type(x) is not int or not 0 <= x < n:
            raise ValueError("vertex outside graph")
        return x
    edges = []
    for action in actions:
        if type(action) is not dict or type(action.get("premises")) is not list:
            raise ValueError("malformed action")
        edges.append([vertex(action.get("query")), [vertex(p) for p in action["premises"]]])
    return {"vertices": n, "edges": edges, "initial": sorted(set(map(vertex, initial))),
            # Bind the complete supplied action content, not only its endpoints.
            "actions_sha256": _identity(actions)}


def diagnose(n: int, actions: list[dict], initial: list[int], target: int) -> dict:
    graph = _graph(n, actions, initial)
    if type(target) is not int or not 0 <= target < n:
        raise ValueError("invalid target")
    costs: list[int | None] = [None] * n
    witness: list[int | None] = [None] * n
    for p in graph["initial"]:
        costs[p] = 0
    # Positive action cost implies a minimum tree has no repeated vertex along
    # an ancestor path: substituting the descendant proof removes that cycle.
    # At most n synchronous relaxations therefore suffice. Duplicate premises
    # remain duplicate children and are charged separately.
    for _ in range(n):
        previous = costs.copy()
        for edge, (q, ps) in enumerate(graph["edges"]):
            if all(previous[p] is not None for p in ps):
                value = 1 + sum(previous[p] for p in ps)
                if costs[q] is None or value < costs[q]:
                    costs[q], witness[q] = value, edge
        if costs == previous:
            break
    certificate = {
        "schema": "ocm.finite-proof-graph-certificate.v1",
        "graph_sha256": _identity(graph), "target": target,
        "costs": costs, "witness_edges": witness,
        "terminal": ("UNREACHABLE_IN_DECLARED_FINITE_GRAPH" if costs[target] is None
                     else "MINIMUM_TREE_COST_IN_DECLARED_FINITE_GRAPH"),
        "scope": "Supplied finite bank/action graph only; not native or mathematical impossibility.",
    }
    verify(n, actions, initial, target, certificate)
    return certificate


def verify(n: int, actions: list[dict], initial: list[int], expected_target: int, certificate: dict) -> bool:
    """Check local closure/inequalities/witnesses without rerunning relaxation."""
    graph = _graph(n, actions, initial)
    if type(certificate) is not dict or certificate.get("schema") != "ocm.finite-proof-graph-certificate.v1":
        raise ValueError("certificate schema")
    if certificate.get("graph_sha256") != _identity(graph):
        raise ValueError("graph/source binding changed")
    target = certificate.get("target")
    if type(expected_target) is not int or target != expected_target:
        raise ValueError("issued target binding changed")
    if type(target) is not int or not 0 <= target < n:
        raise ValueError("certificate target")
    costs, witnesses = certificate.get("costs"), certificate.get("witness_edges")
    if type(costs) is not list or type(witnesses) is not list or len(costs) != n or len(witnesses) != n:
        raise ValueError("incomplete certificate population")
    if any(x is not None and (type(x) is not int or x < 0) for x in costs):
        raise ValueError("invalid costs")
    initial_set = set(graph["initial"])
    for q in range(n):
        cost, edge = costs[q], witnesses[q]
        if q in initial_set:
            if cost != 0 or edge is not None:
                raise ValueError("invalid initial fact")
        elif cost is None:
            if edge is not None:
                raise ValueError("unreachable fact has witness")
        else:
            if cost < 1 or type(edge) is not int or not 0 <= edge < len(graph["edges"]):
                raise ValueError("missing constructive witness")
            head, ps = graph["edges"][edge]
            if head != q or any(costs[p] is None for p in ps) or cost != 1 + sum(costs[p] for p in ps):
                raise ValueError("invalid witness cost or conclusion")
    for q, ps in graph["edges"]:
        if all(costs[p] is not None for p in ps):
            if costs[q] is None or costs[q] > 1 + sum(costs[p] for p in ps):
                raise ValueError("not closed or costs are not minimal")
    expected = ("UNREACHABLE_IN_DECLARED_FINITE_GRAPH" if costs[target] is None
                else "MINIMUM_TREE_COST_IN_DECLARED_FINITE_GRAPH")
    if certificate.get("terminal") != expected:
        raise ValueError("incorrect terminal")
    return True
