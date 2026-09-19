#!/usr/bin/env python3
"""GMI #833 — circular-dependency detection over DEPENDENCY_GRAPH_V2 (#842 core).

Builds the directed graph from every in-corpus edge layer whose endpoints are
corpus nodes (claim ids, claim-family labels, package names) and reports:

  - strongly connected components of size > 1 (mutual dependency clusters),
  - self-loops (child == parent),
  - per-layer subgraph results (claim-id level, family level, package level),
  - the union graph over all node kinds.

Deterministic (Tarjan SCC over sorted adjacency).  External literature edges
have no corpus endpoint as parent and cannot participate in cycles; they are
excluded from cycle analysis but counted for coverage.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCHEMA = "GMI_833_CYCLE_REPORT_V1"

LAYERS = ("file_local", "pointer_rollup", "parent_family_anchor", "corpus_package")


def tarjan_scc(nodes, adj):
    index_counter = [0]
    stack, lowlink, index, on_stack = [], {}, {}, set()
    result = []

    def strongconnect(v):
        # iterative Tarjan (deterministic successor order)
        work = [(v, iter(sorted(adj[v])))]
        index[v] = lowlink[v] = index_counter[0]
        index_counter[0] += 1
        stack.append(v)
        on_stack.add(v)
        while work:
            node, it = work[-1]
            advanced = False
            for w in it:
                if w not in index:
                    index[w] = lowlink[w] = index_counter[0]
                    index_counter[0] += 1
                    stack.append(w)
                    on_stack.add(w)
                    work.append((w, iter(sorted(adj[w]))))
                    advanced = True
                    break
                elif w in on_stack:
                    lowlink[node] = min(lowlink[node], index[w])
            if advanced:
                continue
            work.pop()
            if work:
                parent = work[-1][0]
                lowlink[parent] = min(lowlink[parent], lowlink[node])
            if lowlink[node] == index[node]:
                component = []
                while True:
                    w = stack.pop()
                    on_stack.discard(w)
                    component.append(w)
                    if w == node:
                        break
                result.append(sorted(component))

    for v in sorted(nodes):
        if v not in index:
            strongconnect(v)
    return result


def build_graph(edges):
    adj = defaultdict(set)
    nodes = set()
    for e in edges:
        if e.get("parent_kind") == "EXTERNAL_LITERATURE":
            continue
        nodes.add(e["child"])
        nodes.add(e["parent"])
        adj[e["child"]].add(e["parent"])
    return nodes, adj


def find_cycles(nodes, adj):
    sccs = [c for c in tarjan_scc(nodes, adj) if len(c) > 1]
    self_loops = sorted(n for n in nodes if n in adj[n])
    cycles = []
    for scc in sccs:
        member = set(scc)
        induced = {n: sorted(adj[n] & member) for n in scc}
        cycles.append({"members": scc, "induced_adjacency": induced})
    return sorted(cycles, key=lambda c: tuple(c["members"])), self_loops


def main():
    g = json.loads((HERE / "DEPENDENCY_GRAPH_V2.json").read_text(encoding="utf-8"))
    all_edges = []
    for layer in LAYERS:
        all_edges.extend(g["edges"][layer])

    per_layer = {}
    for layer in LAYERS:
        nodes, adj = build_graph(g["edges"][layer])
        cycles, self_loops = find_cycles(nodes, adj)
        per_layer[layer] = {
            "nodes": len(nodes), "edges": len(g["edges"][layer]),
            "cycles": cycles, "self_loops": self_loops,
        }

    nodes, adj = build_graph(all_edges)
    cycles, self_loops = find_cycles(nodes, adj)
    edge_index = defaultdict(list)
    for e in all_edges:
        if e.get("parent_kind") == "EXTERNAL_LITERATURE":
            continue
        edge_index[(e["child"], e["parent"])].append(e)

    cycle_details = []
    for c in cycles:
        detail = {"members": c["members"], "edges": []}
        for m in c["members"]:
            for p in c["induced_adjacency"][m]:
                for e in sorted(edge_index.get((m, p), []),
                                key=lambda e: e["citation"]):
                    detail["edges"].append({
                        "child": m, "parent": p,
                        "relation": e["relation"], "citation": e["citation"],
                        "evidence": e["evidence"][:160],
                    })
        cycle_details.append(detail)

    report = {
        "schema": SCHEMA,
        "source_graph": "DEPENDENCY_GRAPH_V2.json",
        "method": "Tarjan SCC over sorted adjacency; cycles = SCCs with >1 member; self-loops reported separately; external-literature edges excluded (no corpus endpoint as parent)",
        "per_layer": per_layer,
        "union": {
            "nodes": len(nodes),
            "corpus_edges": sum(1 for e in all_edges
                                if e.get("parent_kind") != "EXTERNAL_LITERATURE"),
            "cycle_count": len(cycles),
            "self_loops": self_loops,
            "cycles": cycle_details,
        },
    }
    out = HERE / "CYCLE_REPORT_V1.json"
    out.write_text(json.dumps(report, indent=1, sort_keys=False,
                              ensure_ascii=False) + "\n", encoding="utf-8")
    for layer in LAYERS:
        r = per_layer[layer]
        print(f"{layer}: nodes={r['nodes']} edges={r['edges']} "
              f"cycles={len(r['cycles'])} self_loops={len(r['self_loops'])}")
    print(f"union: nodes={len(nodes)} cycles={len(cycles)} "
          f"self_loops={len(self_loops)}")
    for d in cycle_details:
        print("CYCLE:", " <-> ".join(d["members"]))
        for e in d["edges"][:8]:
            print(f"   {e['child']} -> {e['parent']} ({e['relation']}) {e['citation']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
