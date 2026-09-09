"""Validate returned derivation, exact holes, normal expansion and method provenance."""
from native_contract import fields,require
from native_macros import compile_macros
from native_engine import F,K,selected_methods
from vendor import common as C
import native_data as D
M=C.load("native_match")
def validate_packet(engine,request,packet,work):
    fields(packet,("schema","request_sha256","context","library","terminal","decision_count","eligible_ids",
                   "selected_proof_method_ids","normal_proof","normal_proof_bytes","normal_proof_sha256","derivation","execution"))
    require(packet["schema"]=="native.packet.v1" and packet["request_sha256"]==D.hashed(request),"PACKET_REQUEST")
    require(packet["context"]==request["context"] and packet["library"]==request["library"] and packet["eligible_ids"]==request["eligible_ids"],"PACKET_CONTEXT")
    require(packet["terminal"]=="PROVED","NO_PROOF_WITHIN_BOUND")
    inp=engine.inputs;formulas=[["|-"]+x["tokens"] for x in inp.bank["wff"]];parent={x["label"]:x for x in inp.parent}
    macros=compile_macros(inp.methods,request["eligible_ids"] if request["invoke"] else [],[],inp.bank,K,work)
    macro_by_id={a["id"]:a for a in macros};visits=0
    def visit(node,depth=0):
        nonlocal visits
        visits+=1;require(visits<=4096 and depth<=8,"DERIVATION_BOUND")
        if node["kind"]=="premise":
            fields(node,("kind","slot","decision_count","output"));slot=node["slot"]
            require(type(slot) is int and 0<=slot<len(request["task"]["premises"]) and node["output"]==request["task"]["premises"][slot] and node["decision_count"]==0,"DERIVATION_HOLE")
            return node["output"],0
        fields(node,("kind","action","parents","decision_count","output"));require(node["kind"]=="action","DERIVATION_KIND")
        action=node["action"];require(type(action["query"]) is int and 0<=action["query"]<len(formulas),"ACTION_QUERY")
        require(all(type(i) is int and 0<=i<len(formulas) for i in action["premises"]),"ACTION_PREMISES")
        if action["kind"]=="macro":require(macro_by_id.get(action["id"])==action,"UNQUALIFIED_MACRO")
        else:
            fields(action,("kind","label","substitution","query","premises","id"));require(action["kind"]=="primitive","ACTION_KIND")
            row=parent[action["label"]];mapping=action["substitution"]
            require(set(mapping)=={h["statement"][1] for h in row["floating"]},"ACTION_SUBSTITUTION")
            for h in row["floating"]:
                v=mapping[h["statement"][1]]
                require(any(v==x["tokens"] for x in inp.bank[h["statement"][0]]),"ACTION_TYPE")
            require(M.dv_valid(row,mapping) and F.replace(row["statement"],mapping)==formulas[action["query"]],"ACTION_TARGET_DV")
            require([F.replace(h["statement"],mapping) for h in row["essential"]]==[formulas[i] for i in action["premises"]],"ACTION_ESSENTIAL")
            require(action["id"]==C.raw_id(C.canonical({k:v for k,v in action.items() if k!="id"}))["sha256"],"ACTION_ID")
        children=[visit(n,depth+1) for n in node["parents"]]
        require([p for p,c in children]==[formulas[i] for i in action["premises"]],"DERIVATION_INPUTS")
        cost=1+sum(c for p,c in children)
        require(node["decision_count"]==cost<=8 and node["output"]==formulas[action["query"]],"DERIVATION_COST_OUTPUT")
        return node["output"],cost
    out,cost=visit(packet["derivation"])
    require(out==request["task"]["query"] and cost==packet["decision_count"],"EXACT_TARGET")
    require(selected_methods(packet["derivation"])==packet["selected_proof_method_ids"],"SELECTED_PROOF_METHODS")
    proof=F.emit(packet["derivation"],inp.parent,inp.bank,work);normal=" ".join(proof)+"\n"
    require(proof==packet["normal_proof"] and normal==packet["normal_proof_bytes"] and C.raw_id(normal.encode("ascii"))["sha256"]==packet["normal_proof_sha256"],"NORMAL_PROOF_BYTES")
    D.bump(work,"derivation_occurrences_checked",visits)
