"""Bind only an exact generated proof to one fresh native invocation."""
import json,time
from pathlib import Path
import life_native as N
from native_result_binding import verify_result,negative_at_issued
from goal_library import identity,raw_identity,require,encoded
from goal_solve import validate_task
def consumed_cohort(claim,mode,library,used_labels=None):
    require(mode in {"enabled","resident-disabled","restored"},"native arm mode")
    cohort=set(library.cohort_labels);consumed=[label for label in claim["proof"] if label in cohort]
    require(mode!="resident-disabled" or not consumed,"disabled cohort consumed at native boundary")
    if used_labels is not None:
        require(set(used_labels)&cohort==set(consumed),"native trace/proof cohort consumption")
    return consumed
def prepare(task,result,result_pin,library,label,holes):
    ps=validate_task(task)
    require(identity(result)==result_pin,"generated result pin")
    require(result["terminal"]=="GENERATED_PROOF_PENDING_NATIVE" and not result["native_acceptance"],"generated result required")
    require(result["task"]==identity(task) and result["library"]==library.pin,"issued goal/library binding")
    require(result["generated_target"]==task["query"] and result["generated_premises"]==task["premises"],"issued target/holes")
    require(type(holes) is list and len(holes)==len(task["premises"]),"issued hole count")
    require(not {label,*holes}&set(library.rows),"issued target/hole shortcut")
    mapping={"search-hyp-"+str(i):h for i,h in enumerate(holes)}
    proof=[mapping.get(p,p) for p in result["generated_proof"]]
    require(label not in proof and set(proof)<=set(library.rows)|set(holes),"generated proof shortcut/foreign label")
    claim={"label":label,"holes":holes,"query":task["query"],"premises":task["premises"],"proof":proof,
           "parameters":[{k:p[k] for k in ("type","variable","floating_label")} for p in ps]}
    consumed_cohort(claim,result["mode"],library)
    N.validate_claims([claim])
    return claim
def execute(task,result,result_pin,library,label,holes,prefix_path,archive,sources):
    started=time.perf_counter();out={"terminal":"CANNOT_CHECK","native_calls":0,"wrapper_invocations":0}
    archive=Path(archive);prefix_path=Path(prefix_path);library_before=library.costs
    try:
        claim=prepare(task,result,result_pin,library,label,holes)
        require(prefix_path.read_bytes()==library.joined_raw,"current joined prefix")
        for binding in sources.values():
            require(raw_identity(Path(binding["path"]).read_bytes())=={k:binding[k] for k in ("bytes","sha256")},"native source pin")
        out.update(issued_claim=claim,generated_result=result_pin,library=library.pin,sources=sources)
        out["wrapper_invocations"]+=1
        native=N.verify(prefix_path,[claim],archive,sources,library.authority())
        out["native_calls"]+=native["native_calls"];out["native_result"]=native
        require((archive/"result.json").read_bytes()==N.encoded(native)+b"\n","returned/stored native result")
        wanted={"claims":[claim],"sources":sources,"authority":library.authority()}
        require((archive/"request.json").read_bytes()==N.encoded(wanted)+b"\n","stored native request")
        require((archive/"native.log").is_file() and raw_identity((archive/"native.log").read_bytes())==native["log"],"native log pin")
        require((archive/"suffix.mm").read_bytes()==N.serialize([claim]),"exact generated suffix")
        if native["terminal"]=="NATIVE_VERIFIED":
            trace,used,_=verify_result(native,claim,library.joined_raw,(archive/"database.mm").read_bytes(),
                                     library.authority(),sources,prefix_path,archive)
            consumed=consumed_cohort(claim,result["mode"],library,used)
            out.update(terminal="GENERATED_PROOF_NATIVE_VERIFIED",used_contracts=used,
                       selected_cohort_labels=consumed,trace=trace)
        elif negative_at_issued(native,claim,[r["label"] for r in library.manifest["joined_proofs"]]):
            out["terminal"]="GENERATED_PROOF_NATIVE_REJECTED_AT_ISSUED_CLAIM"
    except Exception as exc:out.update(terminal="CANNOT_CHECK",error={"type":type(exc).__name__,"reason":str(exc)})
    finally:
        out["library_costs"]={"before":library_before,"after":library.costs,
                             "delta":{k:v-library_before[k] for k,v in library.costs.items()}}
        out["measured_bridge_wall_s"]=time.perf_counter()-started
    return out
