"""Structural native roles and feedback eligibility; no genotype execution."""
from graph_census_v1 import describe
from contract_v1 import strict_json


def inspect(label, text, kinds, roles):
    original = describe(label, text, kinds, roles)
    graph = strict_json(text)
    nodes, edges = graph["nodes"], graph["edges"]
    routes = original["native_role_adjacency"]
    reads = [r for r in routes if r["kind"] in ("LINEAR", "AFFINE")
             and r["role"] == "parameter"]
    parameter_updates = [r for r in routes if r["kind"] == "GRAD"
                         and r["role"] == "parameter"]
    grads = sorted(n for n, v in nodes.items() if v[0] == "GRAD")
    unknown = []
    # Only EDGE is proved to preserve the list of cell names in this analysis.
    for dense in original["dense_nodes"]:
        todo, seen = [dense], set()
        while todo:
            a = todo.pop()
            if a in seen:
                continue
            seen.add(a)
            for source, target, port in edges:
                if source != a:
                    continue
                kind = nodes[target][0]
                if kind == "EDGE":
                    todo.append(target)
                elif kind not in roles:
                    unknown.append({"dense": dense, "source": a, "target": target,
                                    "kind": kind, "port": port})
    updates = []
    for grad in grads:
        targets = sorted({r["dense"] for r in parameter_updates if r["path"][-1] == grad})
        missing = sorted(set(roles["GRAD"].values()) -
                         {p for _, b, p in edges if b == grad})
        updates.append({
            "grad": grad, "identity_parameter_sources": targets,
            "missing_input_ports": missing,
            "feedback_schedule": "ELIGIBLE_IF_LABEL_SUPPLIED_AND_PRIOR_EVALUATION_COMPLETES",
            "query_schedule": "SKIPPED",
            "runtime_result": "NONE",
            "outgoing_edges": sorted([e for e in edges if e[0] == grad]),
            "write_effect": "UNVERIFIED_REQUIRES_VALID_VALUES_TAPE_AND_NONZERO_UPDATE",
            "outgoing_edge_required_for_cell_write": False})
    return {
        "label": label, "status": "STRUCTURE_INSPECTED",
        "serialized_genotype_sha256": original["serialized_genotype_sha256"],
        "dense_nodes": original["dense_nodes"], "grad_nodes": grads,
        "native_role_adjacency": routes,
        "numeric_parameter_routes": reads,
        "feedback_parameter_routes": parameter_updates,
        "feedback_updates": updates,
        "nonidentity_routes": sorted(unknown, key=lambda r: (r["dense"], r["source"], r["target"], r["port"])),
        "other_route_semantics": "UNINSPECTED",
        "causal_coefficient_use": "UNVERIFIED",
        "nonzero_parameter_write": "UNVERIFIED",
        "admissibility": "UNINSPECTED"}
