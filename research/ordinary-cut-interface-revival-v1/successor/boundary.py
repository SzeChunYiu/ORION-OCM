"""Successor two-node cuts for 2- or 3-class packets. Frozen predecessor unchanged."""
import hashlib
import json
import typed_context as TC
import typed_constructor as constructor
import typed_emit as emitter


def count(work, key, n=1):
    work[key] = work.get(key, 0) + n


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def resolved(nodes, i):
    while nodes[i]["kind"] == "saved_reference":
        i = nodes[i]["saved_node"]
    return i


def validate_source(trace, contracts):
    context = TC.from_source(trace["source"])
    holes = []
    for i, h in enumerate(trace["source"]["essential"]):
        label = "cut-source-hole-" + str(i)
        while label in contracts:
            label = "_" + label
        holes.append({"label": label, "statement": h["statement"]})
    constructor.construct(trace, contracts,
                          {r["variable"]: r["variable"] for r in context["parameters"]},
                          holes, max_tokens=4096)
    return context


def make_cut(trace, contracts, head, child, work):
    nodes = trace["nodes"]
    selected = {head, child}
    frontier = set()
    reached = set()

    def visit(i):
        i = resolved(nodes, i)
        if i in reached:
            return
        reached.add(i)
        count(work, "cut_dependency_visits")
        n = nodes[i]
        if n["kind"] == "essential_hypothesis" or (n["kind"] == "semantic_application" and i not in selected):
            frontier.add(i)
            return
        for j in n["inputs"]:
            visit(j)
    visit(head)
    TC.require(selected <= reached, "disconnected selected nodes")
    source = trace["source"]
    all_logical = {n["id"] for n in nodes if n["kind"] == "semantic_application"}
    if head == resolved(nodes, trace["root"]) and selected == all_logical:
        return {"status": "EXCLUDED_WHOLE_TRAINING_PROOF", "selected_nodes": sorted(selected)}
    representative = {}
    frontier_key = {}
    for i in sorted(frontier):
        n = nodes[i]
        key = ("essential", n["label"]) if n["kind"] == "essential_hypothesis" else ("producer", i)
        representative.setdefault(key, i)
        frontier_key[i] = key
    boundary = sorted(representative.values())
    boundary_id = {i: representative[key] for i, key in frontier_key.items()}
    params = [h["statement"][1] for h in source["floating"]]
    order = []
    for statement in [nodes[i]["output"] for i in boundary] + [nodes[head]["output"]]:
        for token in statement:
            if token in params and token not in order:
                order.append(token)
    arity = len(source["floating"])
    if len(order) != arity:
        return {"status": "UNKNOWN_INTERFACE",
                "reason": "boundary lacks the declared class parameters",
                "selected_nodes": sorted(selected), "boundary_nodes": boundary}
    ids = TC.ids_for(arity)
    renaming = dict(zip(order, ids))
    rename = lambda ts: TC.rename(ts, renaming)
    mapped = {}
    body_nodes = []
    leaves = {}
    slots = {n: i for i, n in enumerate(boundary)}

    def build(i):
        i = resolved(nodes, i)
        if i in mapped:
            return mapped[i]
        n = nodes[i]
        output = rename(n["output"])
        if i in boundary_id:
            new = {"kind": "hole", "slot": slots[boundary_id[i]], "output": output}
        elif n["kind"] == "floating_hypothesis":
            new = {"kind": "float", "output": output}
        else:
            TC.require(n["kind"] in ("semantic_application", "syntax_application"), "unsupported source node")
            new = {"kind": "apply", "label": n["label"], "inputs": [build(j) for j in n["inputs"]],
                   "output": output, "substitution": {k: rename(v) for k, v in n["substitution"].items()}}
        if new["kind"] in ("float", "hole"):
            key = json.dumps(new, sort_keys=True, separators=(",", ":"))
            if key in leaves:
                mapped[i] = leaves[key]
                return mapped[i]
            leaves[key] = len(body_nodes)
        mapped[i] = len(body_nodes)
        body_nodes.append(new)
        return mapped[i]
    root = build(head)
    body = {"schema": "native.typed-proper-chunk.v1",
            "parameters": TC.parameters(source["floating"][0]["statement"][0], arity),
            "premises": [rename(nodes[i]["output"]) for i in boundary],
            "query": rename(nodes[head]["output"]),
            "nodes": body_nodes, "root": root}
    context = TC.from_source(source, order)
    hypotheses = []
    for i in boundary:
        label = "cut-boundary-" + str(i)
        while label in contracts:
            label = "_" + label
        hypotheses.append({"label": label, "statement": nodes[i]["output"]})
    proposed = emitter.emit(body, contracts, context, hypotheses, work)
    return {"status": "CUT_PROPOSAL", "body": body, "canonical_id": digest(body),
            "selected_nodes": sorted(selected), "boundary_nodes": boundary,
            "logical_dag_nodes": len(selected),
            "logical_tree_applications": proposed["semantic_applications_expanded"],
            "normal_proof_labels": len(proposed["proof"]), "proposal": proposed,
            "context": context, "native_acceptance": False}


def enumerate_two(trace, contracts, work):
    validate_source(trace, contracts)
    nodes = trace["nodes"]
    out = []
    for head, n in enumerate(nodes):
        count(work, "source_nodes_considered")
        if n["kind"] != "semantic_application":
            continue
        row = contracts[n["label"]]
        nf = len(row["floating"])
        for slot, i in enumerate(n["inputs"][nf:]):
            count(work, "essential_ports_considered")
            child = resolved(nodes, i)
            if nodes[child]["kind"] != "semantic_application":
                continue
            count(work, "two_node_edges")
            record = make_cut(trace, contracts, head, child, work)
            record.update(head=head, essential_port=slot, child=child)
            out.append(record)
    return {"schema": "ordinary.two-logical-node-cuts.v1", "rows": out,
            "coverage": "Successor 2-or-3 class / no-DV / no-extra-$e sources, including 0-ary P1 syntax constructors.",
            "native_acceptance": False}
