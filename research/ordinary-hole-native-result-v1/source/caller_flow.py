"""Two fresh native calls around the unchanged one-occurrence adapter."""
import json,time
from pathlib import Path
import life_native as N
from hole_match import match,resolve,require,identity
from replacement import emit_one
from caller_bindings import raw_identity,verify_result,adapter_context,check_proposal,negative_at_issued
import trace_source as S

def write(path,value):
    raw=N.encoded(value)+b"\n"
    N.store(path,raw)

def prepare_replacement(definition,result,trace,used,prefix,authority,work):
    context=adapter_context(definition,result,trace,used,prefix,authority)
    node=resolve(trace["nodes"],trace["root"])
    for port in definition["occurrence_path"]:
        node=resolve(trace["nodes"],trace["nodes"][node]["inputs"][port])
    require(node==definition["expected_trace_target_node"],"fixed authored occurrence")
    args=(definition["body"],definition["pattern_contracts"],definition["lemma"],trace,used)
    found=match(*args,node,context,work)
    require(found["status"]=="MATCH_PROPOSAL","matching refused: "+str(found))
    for key,value in definition["expected_binding"].items():
        require(found["binding"][key]==value,"independent authored argument order: "+key)
    source=definition["source_claim"];issued=definition["replacement_claim"]
    renaming=dict(zip(source["holes"],issued["holes"]))
    proposal=emit_one(*args,context,found["binding"],definition["occurrence_path"],renaming,work)
    check_proposal(definition,proposal)
    return context,found,proposal

def execute(definition,prefix_raw,prefix_path,authority,sources,output):
    started=time.perf_counter();work={};progress={"terminal":"CANNOT_CHECK","native_calls":0,
        "wrapper_invocations":0,"eligible_method_ids":[],"scope":"Authored alias-only replacement; no learning/usefulness claim"}
    write(output/"ISSUED-SOURCE.json",definition["source_claim"])
    write(output/"ISSUED-REPLACEMENT.json",definition["replacement_claim"])
    def checked(claim,name):
        archive=output/name;progress["wrapper_invocations"]+=1
        result=N.verify(prefix_path,[claim],archive,sources,authority)
        progress["native_calls"]+=result["native_calls"]
        progress.setdefault("native_results",{})[name]={"terminal":result["terminal"],
            "error":result["error"],"receipt":identity(result)}
        if result["terminal"]!="NATIVE_VERIFIED":
            prefix,_=S.index(prefix_raw)
            labels=[k for k,v in prefix.items() if v["kind"]=="$p"]
            progress["terminal"]="NATIVE_REJECTED" if negative_at_issued(result,claim,labels) else "CANNOT_CHECK"
            raise ValueError("native phase refusal: "+str(result["error"]))
        require((archive/"result.json").read_bytes()==N.encoded(result)+b"\n","returned native receipt")
        expected={"claims":[claim],"sources":sources,"authority":authority}
        require((archive/"request.json").read_bytes()==N.encoded(expected)+b"\n","native issued request file")
        require((archive/"suffix.mm").read_bytes()==N.serialize([claim]),"native issued proof bytes")
        require(raw_identity((archive/"native.log").read_bytes())==result["log"],"native log binding")
        trace,used,prefix=verify_result(result,claim,prefix_raw,(archive/"database.mm").read_bytes(),
                                      authority,sources,prefix_path,archive)
        return result,trace,used,prefix
    try:
        progress["stage"]="source_native"
        result,trace,used,prefix=checked(definition["source_claim"],"native-source")
        progress["source_receipt"]=identity(result);write(output/"CURRENT-USED-CONTRACTS.json",used)
        progress["stage"]="replacement_proposal"
        context,found,proposal=prepare_replacement(definition,result,trace,used,prefix,authority,work)
        write(output/"CONTEXT.json",context);write(output/"MATCH.json",found);write(output/"PROPOSAL.json",proposal)
        progress["stage"]="replacement_native"
        final,_,_,_=checked(definition["replacement_claim"],"native-replacement")
        progress.update(terminal="AUTHORED_ALIAS_REPLACEMENT_NATIVE_CHECKED",replacement_receipt=identity(final))
    except Exception as exc:
        progress["error"]={"type":type(exc).__name__,"message":str(exc)}
    finally:
        progress.update(adapter_work=work,flow_wall_s=time.perf_counter()-started)
        write(output/"FLOW.json",progress)
    return progress
