"""Exact typed recipe construction with declared native floating labels."""
import typed_context as TC
from typed_context import require


def count(work,key,n=1): work[key]=work.get(key,0)+n


def substitute(tokens,mapping): return [v for t in tokens for v in mapping.get(t,[t])]


def emit(body,contracts,context,hypotheses,work):
    rows=TC.validate(context)
    expected=TC.parameters(rows[0]["type"])
    for parameter in rows:
        label=parameter["floating_label"]
        require(label in contracts and contracts[label]["label"]==label and
                contracts[label]["kind"]=="$f" and
                contracts[label]["statement"]==[parameter["type"],parameter["variable"]],
                "exact floating context contract")
    native_mapping={r["id"]:r["variable"] for r in rows}
    native=lambda ts:TC.rename(ts,native_mapping)
    require(type(hypotheses) is list and all(type(h) is dict and set(h)=={"label","statement"} for h in hypotheses),"hole shape")
    require([h["statement"] for h in hypotheses]==[native(p) for p in body["premises"]],"wrong exact hole")
    holes=[h["label"] for h in hypotheses]
    float_labels={r["id"]:r["floating_label"] for r in rows}
    require(not set(holes)&set(float_labels.values()),"hole/floating collision")
    require(body["schema"]=="native.typed-proper-chunk.v1" and body["parameters"]==expected and set(body)=={"schema","parameters","premises","query","nodes","root"},"body schema/parameters")
    nodes=body["nodes"]
    require(type(nodes) is list and 0<len(nodes)<=256 and type(body["root"]) is int and body["root"]==len(nodes)-1,"body root/population")
    require(len(holes)==len(body["premises"]) and len(set(holes))==len(holes),"hole population")
    require(all(type(h) is str and h and all(c.isalnum() or c in "-_." for c in h) for h in holes),"hole label")
    require(not set(holes)&set(contracts),"hole label collision")
    outputs=[]
    for i,n in enumerate(nodes):
        count(work,"body_nodes_validated")
        if n["kind"]=="float":
            require(set(n)=={"kind","output"} and n["output"] in [[r["type"],r["id"]] for r in rows],"float body")
        elif n["kind"]=="hole":
            require(set(n)=={"kind","slot","output"} and type(n["slot"]) is int and 0<=n["slot"]<len(holes)
                    and n["output"]==body["premises"][n["slot"]],"hole body")
        else:
            require(set(n)=={"kind","label","inputs","output","substitution"} and n["kind"]=="apply","application shape")
            require(n["label"] in contracts,"missing contract")
            row=contracts[n["label"]]
            require(row["kind"] in ("$a","$p") and row["dv"]==[],"contract/DV boundary")
            inputs=n["inputs"];hs=row["floating"]+row["essential"]
            require(len(hs)>0 and len(inputs)==len(hs) and all(type(j) is int and 0<=j<i for j in inputs),"body dependency")
            mapping={h["statement"][1]:outputs[inputs[j]][1:] for j,h in enumerate(row["floating"])}
            require(mapping==n["substitution"],"substitution body")
            require(all(outputs[k]==substitute(h["statement"],mapping) for k,h in zip(inputs,hs)),"typed/essential body")
            require(n["output"]==substitute(row["statement"],mapping),"output body")
        outputs.append(n["output"])
    require(outputs[-1]==body["query"],"query body")
    semantic_nodes=sum(n["kind"]=="apply" and n["output"][0]=="|-" for n in nodes)
    require(2<=semantic_nodes<=8,"proper semantic DAG bound")
    used={token for statement in body["premises"]+[body["query"]] for token in statement
          if token in TC.IDS}
    require(used==set(TC.IDS),"complete three-parameter body")
    proof=[];reached=set();semantic=0
    def visit(i):
        nonlocal semantic
        reached.add(i);n=nodes[i];count(work,"expanded_node_visits")
        if n["kind"]=="float":label=float_labels[n["output"][1]]
        elif n["kind"]=="hole":label=holes[n["slot"]]
        else:
            for j in n["inputs"]:visit(j)
            label=n["label"]
            if n["output"][0]=="|-":semantic+=1
        require(len(proof)<4096,"expanded proof bound");proof.append(label)
    visit(body["root"])
    require(reached==set(range(len(nodes))),"unreachable body node")
    return {"proof":proof,"target":native(body["query"]),"hypotheses":hypotheses,"semantic_applications_expanded":semantic}
