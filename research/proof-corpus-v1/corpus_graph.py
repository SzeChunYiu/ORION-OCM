"""Exact graph checks on lexical import records, never semantic proof support."""
import heapq
from corpus_contract import CorpusError, digest


def build_graph(wrappers, solutions, *, expected_count):
    if (type(expected_count) is not int or expected_count < 1 or
            set(wrappers) != set(solutions) or len(wrappers) != expected_count):
        raise CorpusError("PAIR_COVERAGE", "wrapper/solution sets or count differ")
    nodes = {}
    for key in sorted(wrappers):
        wrapper, solution = wrappers[key], solutions[key]
        if (wrapper["theorem_id"] != "Theorems.Thm_" + key or
                solution["solution_id"] != "P2M.Sol.S_" + key):
            raise CorpusError("PAIR_IDENTITY", key)
        imports = solution["imports"]
        if any(module.startswith("P2M.Sol.") or
               (module.startswith("Theorems.") and not module.startswith("Theorems.Thm_"))
               for module in imports):
            raise CorpusError("UNREGISTERED_PROOF_IMPORT", key)
        dependencies = sorted({module[len("Theorems.Thm_"):] for module in imports
                               if module.startswith("Theorems.Thm_")})
        if any(dep not in wrappers for dep in dependencies):
            raise CorpusError("DANGLING_IMPORT", key)
        nodes[key] = {"dependencies": dependencies,
                      "wrapper_sha256": wrapper["wrapper_sha256"],
                      "solution_sha256": solution["solution_sha256"]}
    degree = {key: len(row["dependencies"]) for key, row in nodes.items()}
    users = {key: [] for key in nodes}
    for key, row in nodes.items():
        for dep in row["dependencies"]:
            users[dep].append(key)
    ready = [key for key, count in degree.items() if not count]
    heapq.heapify(ready)
    order = []
    while ready:
        key = heapq.heappop(ready)
        order.append(key)
        for user in sorted(users[key]):
            degree[user] -= 1
            if degree[user] == 0:
                heapq.heappush(ready, user)
    if len(order) != len(nodes):
        raise CorpusError("IMPORT_CYCLE")
    return {"graph_kind": "LEXICAL_THEOREM_IMPORT_GRAPH",
            "semantic_dependencies_verified": False, "nodes": nodes,
            "node_count": len(nodes),
            "edge_count": sum(len(row["dependencies"]) for row in nodes.values()),
            "topological_order": order, "graph_sha256": digest(nodes)}
