"""Every proper ancestor chunk, after structural replay; no label-based selection."""
import json
import typed_context as TC
import typed_constructor as constructor
from typed_context import require


def count(work,key,n=1): work[key]=work.get(key,0)+n


def extract(trace,contracts,work):
    context = TC.from_source(trace["source"])
    rows = TC.validate(context)
    holes=[]
    for i,h in enumerate(trace["source"]["essential"]):
        label="typed-structural-hole-"+str(i)
        while label in contracts: label="_"+label
        holes.append({"label":label,"statement":h["statement"]})
    constructor.construct(trace, contracts, {r["variable"]: r["variable"] for r in rows},
                          holes, max_tokens=4096)
    require(trace["terminal"]=="NATIVE_VERIFIED","source not admitted")
    source=trace["source"];nodes=trace["nodes"]
    require(source["dv"]==[] and source["active_dv"]==[],"DV boundary")
    params=[h["statement"][1] for h in source["floating"]]
    parameter_type=rows[0]["type"]
    require(type(nodes) is list and 0<len(nodes)<=256 and trace["root"]==len(nodes)-1,"source node population")
    for i,node in enumerate(nodes):
        count(work,"source_nodes_visited")
        require(node["id"]==i and all(type(j) is int and 0<=j<i for j in node["inputs"]),"source dependency order")
        if node["kind"]=="saved_reference":
            require(type(node["saved_node"]) is int and 0<=node["saved_node"]<i,"saved dependency order")
    require(nodes[-1]["output"]==source["statement"],"source output")
    found=[]
    for root,node in enumerate(nodes[:-1]):
        if node["kind"]!="semantic_application":continue
        reached=set()
        def visit(i):
            if i in reached:return
            reached.add(i);count(work,"dependency_visits")
            for j in nodes[i]["inputs"]:visit(j)
            if nodes[i]["kind"]=="saved_reference":visit(nodes[i]["saved_node"])
        visit(root)
        semantics=sum(nodes[i]["kind"]=="semantic_application" for i in reached)
        if not 2<=semantics<=8:continue
        essential={nodes[i]["label"] for i in reached if nodes[i]["kind"]=="essential_hypothesis"}
        original=[h for h in source["essential"] if h["label"] in essential]
        require(len(original)==len(essential),"source essential scope")
        order=[]
        for tokens in [h["statement"] for h in original]+[node["output"]]:
            for token in tokens:
                if token in params and token not in order:order.append(token)
        if len(order)!=3:
            count(work,"outside_three_parameter_chunks");continue
        renaming=dict(zip(order,TC.IDS));rename=lambda ts:TC.rename(ts,renaming)
        slots={h["label"]:i for i,h in enumerate(original)}
        mapped={};leaves={};body_nodes=[]
        for old in sorted(reached):
            n=nodes[old];kind=n["kind"]
            if kind=="saved_reference":mapped[old]=mapped[n["saved_node"]];continue
            output=rename(n["output"])
            if kind=="floating_hypothesis":new={"kind":"float","output":output}
            elif kind=="essential_hypothesis":new={"kind":"hole","slot":slots[n["label"]],"output":output}
            else:
                require(kind in ("semantic_application","syntax_application"),"unsupported source node")
                new={"kind":"apply","label":n["label"],"inputs":[mapped[j] for j in n["inputs"]],
                     "output":output,"substitution":{k:rename(v) for k,v in n["substitution"].items()}}
            key=json.dumps(new,sort_keys=True,separators=(",",":"))
            if kind in ("floating_hypothesis","essential_hypothesis") and key in leaves:
                mapped[old]=leaves[key];continue
            mapped[old]=len(body_nodes);body_nodes.append(new)
            if kind in ("floating_hypothesis","essential_hypothesis"):leaves[key]=mapped[old]
        body={"schema":"native.typed-proper-chunk.v1","parameters":TC.parameters(parameter_type),
              "premises":[rename(h["statement"]) for h in original],"query":rename(node["output"]),
              "nodes":body_nodes,"root":mapped[root]}
        found.append({"body":body,"source_root":root,"source_nodes":sorted(reached),"semantic_nodes":semantics,"context":TC.from_source(source,order)})
    return found
