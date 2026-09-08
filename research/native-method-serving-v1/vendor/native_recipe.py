"""Checked recipe emitter extracted from the qualified trace module; no mining."""
from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location("_common",Path(__file__).with_name("common.py"))
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
T=C.load("typed_terms")
def count(work,key,n=1):work[key]=work.get(key,0)+n
def require(ok,reason):
    if not ok:raise ValueError(reason)
def substitute(tokens,mapping):return [v for t in tokens for v in mapping.get(t,[t])]
def emit(body,contracts,holes,work):
    require(body["schema"]=="native.proper-chunk.v1" and body["parameters"]==list(T.ATOMS),"body schema/parameters")
    nodes=body["nodes"]
    require(type(nodes) is list and 0<len(nodes)<=256 and body["root"]==len(nodes)-1,"body root/population")
    require(len(holes)==len(body["premises"]) and len(set(holes))==len(holes),"hole population")
    require(all(type(h) is str and h and all(c.isalnum() or c in "-_." for c in h) for h in holes),"hole label")
    require(not set(holes)&set(contracts),"hole label collision")
    outputs=[]
    for i,n in enumerate(nodes):
        count(work,"body_nodes_validated")
        if n["kind"]=="float":
            require(set(n)=={"kind","output"} and n["output"] in [["class",a] for a in T.ATOMS],"float body")
        elif n["kind"]=="hole":
            require(set(n)=={"kind","slot","output"} and type(n["slot"]) is int and 0<=n["slot"]<len(holes)
                    and n["output"]==body["premises"][n["slot"]],"hole body")
        else:
            require(set(n)=={"kind","label","inputs","output","substitution"} and n["kind"]=="apply","application shape")
            require(n["label"] in contracts,"missing contract")
            row=contracts[n["label"]]
            require(row["kind"] in ("$a","$p") and row["dv"]==[],"contract/DV boundary")
            inputs=n["inputs"];hs=row["floating"]+row["essential"]
            require(len(inputs)==len(hs) and all(type(j) is int and 0<=j<i for j in inputs),"body dependency")
            mapping={h["statement"][1]:outputs[inputs[j]][1:] for j,h in enumerate(row["floating"])}
            require(mapping==n["substitution"],"substitution body")
            require(all(outputs[k]==substitute(h["statement"],mapping) for k,h in zip(inputs,hs)),"typed/essential body")
            require(n["output"]==substitute(row["statement"],mapping),"output body")
        outputs.append(n["output"])
    require(outputs[-1]==body["query"],"query body")
    proof=[];reached=set();semantic=0
    def visit(i):
        nonlocal semantic
        reached.add(i);n=nodes[i];count(work,"expanded_node_visits")
        if n["kind"]=="float":label="c"+n["output"][1]
        elif n["kind"]=="hole":label=holes[n["slot"]]
        else:
            for j in n["inputs"]:visit(j)
            label=n["label"]
            if n["output"][0]=="|-":semantic+=1
        require(len(proof)<4096,"expanded proof bound");proof.append(label)
    visit(body["root"])
    require(reached==set(range(len(nodes))),"unreachable body node")
    return {"proof":proof,"semantic_applications_expanded":semantic}
