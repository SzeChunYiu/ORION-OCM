"""Successor constructor: same replay as the class packet, plus 0-ary P1 syntax."""
import typed_context as TC


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def subst(tokens, mapping):
    return [x for token in tokens for x in mapping.get(token, [token])]


def construct(trace, contracts, renaming, hypotheses, max_tokens=256):
    require(type(max_tokens) is int and 0 < max_tokens <= 4096, "output bound policy")
    source, nodes = trace["source"], trace["nodes"]
    require(trace["terminal"] == "NATIVE_VERIFIED" and source["kind"] == "$p", "source admission")
    require(source["dv"] == [] and source["active_dv"] == [], "DV outside first boundary")
    floating = source["floating"]
    context = TC.from_source(source)
    TC.bijection(context, renaming)
    rename = {key: [value] for key, value in renaming.items()}
    require(type(hypotheses) is list and len(hypotheses) == len(source["essential"]), "open hypotheses")
    labels = [h["label"] for h in hypotheses]
    require(len(set(labels)) == len(labels) and all(type(x) is str and x and
            all(c.isalnum() or c in "-_." for c in x) for x in labels), "local labels")
    require(not set(labels) & set(contracts), "hypothesis label collision")
    for original, supplied in zip(source["essential"], hypotheses):
        require(set(supplied) == {"label", "statement"} and
                supplied["statement"] == subst(original["statement"], rename), "external statement")
    require(trace["external_logical_hypotheses"] == source["essential"], "external slots")
    require(type(nodes) is list and 0 < len(nodes) <= 256, "node population")
    require(type(trace["root"]) is int and trace["root"] == len(nodes)-1, "root identity")
    used = {n["label"] for n in nodes if "label" in n}
    require(set(contracts) == used and source["label"] not in used, "contract population/shortcut")
    stack, saved, checked = [], [], []
    for event in trace["events"]:
        if event.get("kind") == "save":
            require(stack and event == {"kind": "save", "slot": len(saved), "node": stack[-1]}, "save event")
            saved.append(stack[-1])
            continue
        i = len(checked)
        require(i < len(nodes) and event == {"kind": "step", "node": i}, "step ordering")
        node = nodes[i]
        require(type(node["id"]) is int and node["id"] == i, "node identity")
        require(type(node["inputs"]) is list and all(type(j) is int and 0 <= j < i for j in node["inputs"]),
                "cycle/forward/input reference")
        expected = {"id": i}
        if node["kind"] == "saved_reference":
            slot = node["slot"]
            require(type(slot) is int and 0 <= slot < len(saved), "saved slot")
            producer = saved[slot]
            expected.update(kind="saved_reference", inputs=[], slot=slot, saved_node=producer,
                            output=checked[producer]["output"])
            count = 0
        else:
            label = node["label"]
            row = contracts[label]
            require(row["label"] == label and row["span"][0] < source["span"][0], "source assertion order")
            if row["kind"] in {"$f", "$e"}:
                active = source["floating"] if row["kind"] == "$f" else source["essential"]
                require(any(h == {"label": label, "statement": row["statement"]} for h in active), "active hypothesis")
                expected.update(kind="floating_hypothesis" if row["kind"] == "$f" else "essential_hypothesis",
                                label=label, inputs=[], output=row["statement"])
                count = 0
            else:
                require(row["kind"] in {"$a", "$p"} and row["dv"] == [], "assertion kind/DV")
                hs = row["floating"] + row["essential"]
                count, nf = len(hs), len(row["floating"])
                require(len(stack) >= count, "stack arity")
                inputs = stack[-count:] if count else []
                mapping = {}
                for j, h in enumerate(row["floating"]):
                    actual = checked[inputs[j]]["output"]
                    require(actual and actual[0] == h["statement"][0], "floating type")
                    mapping[h["statement"][1]] = actual[1:]
                obligations = []
                for j, h in enumerate(hs):
                    wanted = subst(h["statement"], mapping)
                    require(checked[inputs[j]]["output"] == wanted, "essential/type obligation")
                    obligations.append({"kind": "floating" if j < nf else "essential",
                                        "hypothesis": h["label"], "from": inputs[j], "expected": wanted})
                expected.update(kind="semantic_application" if row["statement"][0] == "|-" else "syntax_application",
                                label=label, assertion_kind=row["kind"], inputs=inputs,
                                output=subst(row["statement"], mapping), substitution=mapping,
                                obligations=obligations, distinct_variable_obligations=[])
        require(node == expected, "node/stack contract")
        if count:
            del stack[-count:]
        stack.append(i)
        checked.append(expected)
    require(len(checked) == len(nodes) and stack == [trace["root"]] and
            nodes[trace["root"]]["output"] == source["statement"], "final graph/stack")
    float_labels = {h["statement"][1]: h["label"] for h in floating}
    leaf_labels = {h["label"]: float_labels[renaming[h["statement"][1]]] for h in floating}
    leaf_labels.update({old["label"]: new["label"] for old, new in zip(source["essential"], hypotheses)})
    proof, reached, reuse = [], set(), []

    def emit(i):
        reached.add(i)
        node = nodes[i]
        if node["kind"] == "saved_reference":
            reuse.append({"reference": i, "producer": node["saved_node"]})
            emit(node["saved_node"])
        else:
            for parent in node["inputs"]:
                emit(parent)
            require(len(proof) < max_tokens, "normal proof output bound")
            proof.append(leaf_labels.get(node["label"], node["label"]))
    emit(trace["root"])
    require(reached == set(range(len(nodes))), "unreachable node")
    return {"target": subst(source["statement"], rename), "hypotheses": hypotheses, "proof": proof,
            "node_outputs": [subst(n["output"], rename) for n in nodes],
            "saved_references": len(reuse), "expanded_dependencies": reuse,
            "semantic_labels": [n["label"] for n in nodes if n["kind"] == "semantic_application"]}
