"""Typed structural adjacency, not an execution or causal-use classifier."""
from collections import defaultdict
from contract_v1 import require, sha, strict_json


def validate_graph(graph, kinds):
    require(type(graph) is dict and set(graph) == {"nodes", "edges", "meta"}, "graph shape")
    nodes, edges = graph["nodes"], graph["edges"]
    require(type(nodes) is dict and nodes and type(edges) is list, "graph containers")
    for name, value in nodes.items():
        require(type(name) is str and type(value) is list and len(value) == 2, "node shape")
        kind, params = value
        require(kind in kinds and type(params) is dict, "unknown native kind or parameters")
        require(set(params) == set(kinds[kind][3]) and
                all(type(v) is int for v in params.values()), "native parameter mismatch")
    bound = set()
    for edge in edges:
        require(type(edge) is list and len(edge) == 3, "edge shape")
        a, b, port = edge
        require(a in nodes and b in nodes and type(port) is int and port >= 0, "edge identity/port")
        ports = kinds[nodes[b][0]][1]
        require(port < len(ports) and kinds[nodes[a][0]][2] == ports[port], "edge native type")
        require((b, port) not in bound, "multiply bound input port")
        bound.add((b, port))
    pending = set(nodes)
    while pending:
        roots = {n for n in pending if not any(b == n and a in pending for a, b, _ in edges)}
        require(roots, "cyclic dataflow")
        pending -= roots
    require(sum(v[0] == "OUTPUT" for v in nodes.values()) == 1, "output cardinality")
    return graph


def describe(label, text, kinds, roles):
    graph = validate_graph(strict_json(text), kinds)
    nodes, edges = graph["nodes"], graph["edges"]
    dense = {n for n, v in nodes.items() if v[0] == "DENSE"}
    ancestry = {n for n, v in nodes.items() if v[0] == "OUTPUT"}
    while True:
        expanded = ancestry | {a for a, b, _ in edges if b in ancestry}
        if expanded == ancestry: break
        ancestry = expanded
    direct = [{"source": a, "target": b, "port": p, "kind": nodes[b][0],
               "target_on_output_ancestry": b in ancestry} for a, b, p in edges if a in dense]
    adjacency = []
    for start in sorted(dense):
        frontier = [(start, [start])]
        while frontier:
            current, path = frontier.pop()
            for a, b, port in edges:
                if a != current: continue
                kind = nodes[b][0]
                if kind == "EDGE": frontier.append((b, path + [b]))
                if kind in roles:
                    role = next((r for r, p in roles[kind].items() if p == port), None)
                    require(role is not None, "unclassified native consumer port")
                    adjacency.append({"dense": start, "path": path + [b], "kind": kind,
                                      "port": port, "role": role,
                                      "target_on_output_ancestry": b in ancestry})
    path_kinds = {nodes[n][0] for n in ancestry}
    all_kinds = {v[0] for v in nodes.values()}
    neural = "DENSE" in path_kinds and "GRAD" in all_kinds
    store = bool(path_kinds & {"TABLE", "KVSTORE", "PROGRAM"})
    family = "HYBRID" if neural and store else "NEURAL" if neural else "NON_NEURAL"
    return {"label": label, "serialized_genotype_sha256": sha(text.encode()),
            "kinds": sorted(all_kinds), "dense_nodes": sorted(dense),
            "direct_dense_consumers": sorted(direct, key=lambda x: (x["source"], x["target"], x["port"])),
            "native_role_adjacency": sorted(adjacency, key=lambda x: (x["dense"], x["path"], x["port"])),
            "dense_on_output_ancestry": bool(dense & ancestry),
            "literal_packet_family": family, "causal_coefficient_use_certified": False}


def summarize(rows):
    groups = defaultdict(list)
    for row in rows: groups[row["serialized_genotype_sha256"]].append(row["label"])
    def numeric(row):
        return [e for e in row["native_role_adjacency"]
                if e["kind"] in ("LINEAR", "AFFINE") and e["role"] == "parameter"]
    return {"rows": len(rows), "distinct_serialized_graphs": len(groups),
            "dense_rows": sum(bool(r["dense_nodes"]) for r in rows),
            "grad_rows": sum("GRAD" in r["kinds"] for r in rows),
            "numeric_parameter_adjacency_rows": sum(bool(numeric(r)) for r in rows),
            "numeric_parameter_on_output_ancestry_rows":
                sum(any(e["target_on_output_ancestry"] for e in numeric(r)) for r in rows),
            "duplicate_serializations": sorted([sorted(v) for v in groups.values() if len(v) > 1])}
