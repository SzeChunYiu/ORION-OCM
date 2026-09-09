"""Functional one-occurrence proof emission; native verification is still required."""
from hole_match import match,resolve,require,substitute,tick

def emit_one(body,pattern_contracts,lemma,trace,target_contracts,context,binding,
             occurrence_path,hypothesis_renaming,work):
    result={"status":"CANNOT_CHECK","native_acceptance":False}
    try:
        current=match(body,pattern_contracts,lemma,trace,target_contracts,binding["target_node"],context,work)
        require(current["status"]=="MATCH_PROPOSAL" and current["binding"]==binding,"fresh exact match binding")
        require(type(occurrence_path) is list and all(type(i) is int and i>=0 for i in occurrence_path),"occurrence path")
        nodes=trace["nodes"];i=resolve(nodes,trace["root"])
        for port in occurrence_path:
            require(port<len(nodes[i]["inputs"]),"occurrence child port")
            i=resolve(nodes,nodes[i]["inputs"][port])
        require(i==binding["target_node"],"selected occurrence identity")
        source_holes={h["label"] for h in trace["source"]["essential"]}
        require(type(hypothesis_renaming) is dict and set(hypothesis_renaming)==source_holes,"exact external renaming")
        labels=list(hypothesis_renaming.values())
        require(len(set(labels))==len(labels) and all(type(x) is str and x and
            all(c.isalnum() or c in "-_." for c in x) for x in labels),"external label syntax")
        forbidden=set(target_contracts)|set(pattern_contracts)|{lemma["label"],trace["source"]["label"]}
        require(not set(labels)&forbidden,"external label collision")
        params=context["parameter_context"]["parameters"]
        native_subst={r["variable"]:binding["substitution"][r["id"]] for r in params}
        arguments=binding["floating_arguments"]+binding["essential_arguments"]
        for node,hyp in zip(arguments,lemma["floating"]+lemma["essential"]):
            require(nodes[node]["output"]==substitute(hyp["statement"],native_subst),"argument exact output")
        require(substitute(lemma["statement"],native_subst)==nodes[i]["output"],"replacement exact output")
        proof=[];reached=set();counts={"source_application_occurrences":0,"replacement_applications":0}
        def append(label):
            require(len(proof)<4096,"normal proof output bound");proof.append(label)
            tick(work,"emitted_normal_labels")
        def raw(node):
            node=resolve(nodes,node);n=nodes[node];reached.add(node);tick(work,"argument_or_source_visits")
            for child in n["inputs"]:raw(child)
            if n["kind"] in {"semantic_application","syntax_application"}:
                counts["source_application_occurrences"]+=1
            append(hypothesis_renaming.get(n["label"],n["label"]))
        def visit(node,path):
            node=resolve(nodes,node);n=nodes[node];reached.add(node)
            if path==occurrence_path:
                for argument in arguments:raw(argument)
                append(lemma["label"]);counts["replacement_applications"]+=1
            else:
                for port,child in enumerate(n["inputs"]):visit(child,path+[port])
                if n["kind"] in {"semantic_application","syntax_application"}:
                    counts["source_application_occurrences"]+=1
                append(hypothesis_renaming.get(n["label"],n["label"]))
        visit(trace["root"],[])
        require(counts["replacement_applications"]==1,"exactly one replacement")
        require(trace["source"]["label"] not in proof,"original target shortcut")
        return {**result,"status":"REPLACEMENT_PROPOSAL","proof":proof,
            "target":list(trace["source"]["statement"]),
            "hypotheses":[{"label":hypothesis_renaming[h["label"]],"statement":list(h["statement"])}
                          for h in trace["source"]["essential"]],
            "occurrence_path":list(occurrence_path),"distinct_target_nodes_reached":len(reached),
            "normal_labels":len(proof),**counts,
            "scope":"One supplied-proof refactoring proposal. Fresh exact native checking remains required."}
    except (ValueError,KeyError,TypeError,IndexError,RecursionError,MemoryError) as exc:
        tick(work,"emission_refusals")
        return {**result,"reason":type(exc).__name__+": "+str(exc)}
