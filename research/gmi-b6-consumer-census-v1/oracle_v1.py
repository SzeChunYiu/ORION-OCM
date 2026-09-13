"""Independent backward port walk and all-pairs ancestor oracle for graph fields."""
from contract_v1 import same, strict_json


def compare(row, description, roles):
    graph = strict_json(row["text"])
    nodes, edges = graph["nodes"], graph["edges"]
    incoming = {(b, p): a for a, b, p in edges}
    ancestors = {n: {n} for n in nodes}
    for _ in nodes:
        old = {n: set(a) for n, a in ancestors.items()}
        for a, b, _ in edges: ancestors[b] |= old[a]
    output = next(n for n, value in nodes.items() if value[0] == "OUTPUT")
    served = ancestors[output]
    expected = set()
    for target, value in nodes.items():
        kind = value[0]
        if kind not in roles: continue
        for role, port in roles[kind].items():
            current = incoming.get((target, port))
            while current is not None and nodes[current][0] == "EDGE":
                current = incoming.get((current, 0))
            if current is not None and nodes[current][0] == "DENSE":
                expected.add((current, target, kind, port, role, target in served))
    actual = {(r["dense"], r["path"][-1], r["kind"], r["port"], r["role"],
               r["target_on_output_ancestry"]) for r in description["native_role_adjacency"]}
    same(sorted(expected), sorted(actual), "independent backward role/ancestry oracle")
    dense_served = any(nodes[n][0] == "DENSE" for n in served)
    same(dense_served, description["dense_on_output_ancestry"], "independent served ancestry")
