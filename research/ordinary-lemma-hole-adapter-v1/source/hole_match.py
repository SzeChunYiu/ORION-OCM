"""Typed argument-hole proposals. Structural replay never supplies native authority."""
import hashlib
import json
import typed_context as TC
import typed_constructor as replay
import typed_emit as recipe

class Refusal(Exception):
    pass

def identity(value):
    raw=json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
    return {"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}

def tick(work,key,n=1):
    work[key]=work.get(key,0)+n

def require(ok,reason):
    if not ok:raise ValueError(reason)

def substitute(tokens,mapping):
    return [x for token in tokens for x in mapping.get(token,[token])]

def resolve(nodes,index):
    require(type(index) is int and 0<=index<len(nodes),"target node")
    seen=set()
    while nodes[index]["kind"]=="saved_reference":
        require(index not in seen,"saved cycle");seen.add(index)
        next_index=nodes[index]["saved_node"]
        require(type(next_index) is int and 0<=next_index<index,"saved order")
        index=next_index
    return index

def validate(body,pattern_contracts,lemma,trace,target_contracts,context,work):
    expected={"schema","pins","parameter_context","library_identity","native_authority_identity"}
    require(set(context)==expected and context["schema"]=="ordinary.hole-context.v1","context schema")
    supplied={"body":body,"pattern_contracts":pattern_contracts,"lemma":lemma,
              "target_trace":trace,"target_contracts":target_contracts,"parameter_context":context["parameter_context"]}
    require(context["pins"]=={k:identity(v) for k,v in supplied.items()},"issued input binding")
    for key in ("library_identity","native_authority_identity"):
        p=context[key]
        require(set(p)=={"bytes","sha256"} and type(p["bytes"]) is int and p["bytes"]>0
                and type(p["sha256"]) is str and len(p["sha256"])==64,"authority identity descriptor")
    if trace["source"]["dv"] or trace["source"]["active_dv"] or lemma["dv"]:
        raise Refusal("UNSUPPORTED_DV")
    if any(r.get("dv") for r in list(pattern_contracts.values())+list(target_contracts.values())):
        raise Refusal("UNSUPPORTED_DV")
    if len(trace["source"]["floating"])!=3:
        raise Refusal("UNSUPPORTED_FLOAT_CONTEXT")
    if not 0<len(trace["nodes"])<=256:
        raise Refusal("TRACE_NODE_BOUND")
    rows=TC.validate(context["parameter_context"])
    target_context=TC.from_source(trace["source"])
    target_rows=TC.validate(target_context)
    target_holes=[]
    for i,h in enumerate(trace["source"]["essential"]):
        label="adapter-external-"+str(i)
        while label in target_contracts:label+="-x"
        target_holes.append({"label":label,"statement":h["statement"]})
    tick(work,"target_replay_calls")
    replay.construct(trace,target_contracts,{r["variable"]:r["variable"] for r in target_rows},
                     target_holes,max_tokens=4096)
    tick(work,"target_nodes_replayed",len(trace["nodes"]))
    mapping={r["id"]:[r["variable"]] for r in rows}
    require(set(lemma)=={"label","kind","floating","essential","statement","dv"} and lemma["kind"]=="$p","lemma contract")
    require(lemma["label"] not in target_contracts and lemma["label"] not in pattern_contracts,"lemma label collision")
    floats={h["statement"][1]:h for h in lemma["floating"]}
    require(len(floats)==len(lemma["floating"])==3 and floats=={
        r["variable"]:{"label":r["floating_label"],"statement":[r["type"],r["variable"]]} for r in rows},"lemma floating frame")
    require([h["statement"] for h in lemma["essential"]]==[substitute(p,mapping) for p in body["premises"]]
            and lemma["statement"]==substitute(body["query"],mapping),"lemma exact sequent")
    ph=[]
    for i,p in enumerate(body["premises"]):
        label="adapter-pattern-"+str(i)
        while label in pattern_contracts:label+="-x"
        ph.append({"label":label,"statement":substitute(p,mapping)})
    tick(work,"pattern_replay_calls")
    recipe.emit(body,pattern_contracts,context["parameter_context"],ph,work)
    for label in pattern_contracts.keys() & target_contracts.keys():
        a=pattern_contracts[label];b=target_contracts[label]
        require({k:v for k,v in a.items() if k!="span"}=={k:v for k,v in b.items() if k!="span"},"shared library contract")
    return rows

def match(body,pattern_contracts,lemma,trace,target_contracts,target_node,context,work):
    result={"status":"CANNOT_CHECK","native_acceptance":False,"scope":"One structurally replayed pattern/target proposal"}
    try:
        rows=validate(body,pattern_contracts,lemma,trace,target_contracts,context,work)
        nodes=trace["nodes"];target=resolve(nodes,target_node)
        substitution={};floats={};holes={};pairs=[]
        def visit(pi,ti):
            ti=resolve(nodes,ti);p=body["nodes"][pi];t=nodes[ti];tick(work,"pattern_target_pairs")
            pairs.append((pi,ti))
            if p["kind"]=="float":
                var=p["output"][1]
                if t["output"][0]!=p["output"][0]:return False
                value=t["output"][1:]
                if var in substitution and substitution[var]!=value:return False
                substitution[var]=list(value);floats.setdefault(var,ti);return True
            if p["kind"]=="hole":
                slot=p["slot"]
                if slot in holes and nodes[holes[slot]]["output"]!=t["output"]:return False
                holes.setdefault(slot,ti);return True
            if t["kind"] not in {"semantic_application","syntax_application"} or t["label"]!=p["label"]:
                return False
            if len(p["inputs"])!=len(t["inputs"]):return False
            return all(visit(a,b) for a,b in zip(p["inputs"],t["inputs"]))
        if not visit(body["root"],target):
            return {**result,"status":"NO_MATCH","reason":"STRUCTURE_OR_BINDING_MISMATCH"}
        if set(substitution)!=set(TC.IDS):
            raise Refusal("ARGUMENT_WITNESS_MISSING")
        require(set(holes)==set(range(len(body["premises"]))),"missing essential witness")
        if any(substitute(body["nodes"][p]["output"],substitution)!=nodes[t]["output"] for p,t in pairs):
            return {**result,"status":"NO_MATCH","reason":"EXACT_OUTPUT_OR_ESSENTIAL_MISMATCH"}
        by_variable={r["variable"]:r["id"] for r in rows}
        binding={"target_node":target,"substitution":substitution,
            "floating_arguments":[floats[by_variable[h["statement"][1]]] for h in lemma["floating"]],
            "essential_arguments":[holes[i] for i in range(len(lemma["essential"]))],
            "pins":context["pins"],"library_identity":context["library_identity"],
            "native_authority_identity":context["native_authority_identity"]}
        return {**result,"status":"MATCH_PROPOSAL","binding":json.loads(json.dumps(binding))}
    except Refusal as exc:
        return {**result,"status":"UNKNOWN","reason":str(exc)}
    except (ValueError,KeyError,TypeError,IndexError,RecursionError,MemoryError) as exc:
        tick(work,"refusals")
        return {**result,"reason":type(exc).__name__+": "+str(exc)}
