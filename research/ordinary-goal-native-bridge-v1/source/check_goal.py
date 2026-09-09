"""Fresh authored interface qualification; native entry is forbidden."""
from pathlib import Path
import copy,hashlib,json,os,sys,time,traceback
ROOT=Path(__file__).resolve().parent
runtime=json.loads((ROOT/"inputs/RUNTIME.json").read_bytes())
def rawid(raw):return {"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
for n,pin in runtime["files"].items():assert rawid((Path(runtime["path"])/n).read_bytes())==pin
sys.path[:0]=[str(ROOT),str(ROOT/"vendor"),runtime["path"]]
from authored_fixture import bundle,restore,task,BASE,SUFFIX,native_text
from goal_library import identity,raw_identity
from goal_solve import solve
from goal_native import prepare,execute
import finite_search as FS
import life_native as N
from native_result_binding import verify_result,negative_at_issued
native_calls=0
def forbid(*a,**kw):
    global native_calls
    native_calls+=1
    raise AssertionError("NATIVE_VERIFIER_FORBIDDEN_IN_AUTHORED_CONTROLS")
N.verify=forbid
records=[];output=Path(sys.argv[1]);output.parent.mkdir(exist_ok=True)
B=bundle();L=restore(B);T=task()
def refused(call,fragment):
    try:call()
    except (ValueError,KeyError) as exc:
        assert fragment in str(exc),(fragment,str(exc));return str(exc)
    raise AssertionError("expected refusal: "+fragment)
def record(name,fn):
    started=time.perf_counter()
    try:detail=fn();records.append({"id":name,"passed":True,"detail":detail,"wall_s":time.perf_counter()-started})
    except BaseException as exc:
        records.append({"id":name,"passed":False,"error":type(exc).__name__+": "+str(exc),
                        "traceback":traceback.format_exc(),"wall_s":time.perf_counter()-started})
def arms():
    results=[solve(T,L,"enabled"),solve(T,L,"resident-disabled"),solve(T,restore(copy.deepcopy(B)),"restored")]
    assert all(r["terminal"]=="GENERATED_PROOF_PENDING_NATIVE" for r in results),results
    expected=["wph","wps","wch","search-hyp-0","learned-cut"]
    disabled=["wph","wps","wch","wph","wch","search-hyp-0","ax-pair","ax-wrap"]
    assert [r["generated_proof"] for r in results]==[expected,disabled,expected]
    assert [r["decision_count"] for r in results]==[1,2,1]
    for k in ("bank_identity","grounded_actions_identity","emission_syntax_identity","library"):
        assert results[0][k]==results[1][k]==results[2][k],k
    assert [r["selected_cohort_labels"] for r in results]==[["learned-cut"],[],["learned-cut"]]
    return results
def composite():
    t=copy.deepcopy(T);p=["(","ph","/\\","ph",")"]
    t["premises"]=[["|-"]+p];t["query"]=["|-","(","ps","->","("]+p+["/\\","ch",")",")"]
    r=solve(t,L,"enabled")
    assert r["terminal"]=="GENERATED_PROOF_PENDING_NATIVE",r
    assert r["generated_proof"]==["wph","wph","wa","wps","wch","search-hyp-0","learned-cut"],r
    return r
def oracle_refusal():
    out=[]
    for k in ("proof","trace","target_label","expected_labels"):
        t={**T,k:["oracle"]};r=solve(t,L,"enabled")
        assert r["terminal"]=="UNKNOWN" and r["error"]["reason"]=="goal-only task fields";out.append(r)
    return out
def library_refusals():
    out=[]
    b=copy.deepcopy(B);b["joined"]+=b" "
    out.append(refused(lambda:restore(b),"prefix source pin"))
    b=copy.deepcopy(B);b["receipt"]+=b" "
    out.append(refused(lambda:restore(b),"cohort receipt pin"))
    for key in ("cohort","joined_proofs","axioms"):
        b=copy.deepcopy(B);b["manifest"][key]=[];b["manifest_pin"]=identity(b["manifest"])
        out.append(refused(lambda:restore(b),"cohort" if key=="cohort" else "proof inventory" if key=="joined_proofs" else "axiom authority"))
    return out
def bound_unknown():
    t=copy.deepcopy(T);t["limits"]["max_decisions"]=1;r=solve(t,L,"resident-disabled")
    assert r["terminal"]=="NO_PROOF_IN_REGISTERED_FINITE_BANK" and r["generated_proof"] is None,r
    t=copy.deepcopy(T);t["query"]=["|-","UNSUPPORTED"]
    u=solve(t,L,"enabled");assert u["terminal"]=="UNKNOWN" and not u["native_acceptance"],u
    return [r,u]
def output_binding():
    r=solve(T,L,"enabled");pin=identity(r);claim=prepare(T,r,pin,L,"new-goal",["new-h"])
    assert claim["proof"]==["wph","wps","wch","new-h","learned-cut"] and claim["query"]==T["query"]
    modified=copy.deepcopy(r);modified["generated_proof"]=["learned-cut"]
    reasons=[refused(lambda:prepare(T,modified,pin,L,"new-goal",["new-h"]),"result pin")]
    t=copy.deepcopy(T);t["query"]=["|-","ph"]
    reasons.append(refused(lambda:prepare(t,r,pin,L,"new-goal",["new-h"]),"goal/library binding"))
    reasons.append(refused(lambda:prepare(T,r,pin,L,"learned-cut",["new-h"]),"shortcut"))
    reasons.append(refused(lambda:prepare(T,r,pin,L,"new-goal",[]),"hole count"))
    return {"claim":claim,"refusals":reasons}
def native_boundary():
    r=solve(T,L,"enabled");pin=identity(r);claim=prepare(T,r,pin,L,"new-goal",["new-h"])
    p=output.parent/"authored-prefix.mm";p.write_bytes(B["joined"])
    bad={"index":{"path":str(p),**raw_identity(b"wrong")}}
    stopped=execute(T,r,pin,L,"new-goal",["new-h"],p,output.parent/"never-native",bad)
    assert stopped["terminal"]=="CANNOT_CHECK" and stopped["wrapper_invocations"]==stopped["native_calls"]==0
    assert not (output.parent/"never-native").exists()
    saved={"terminal":"NATIVE_VERIFIED","native_calls":1,"error":None,"claims_sha256":"forged"}
    reason=refused(lambda:verify_result(saved,claim,B["joined"],b"",L.authority(),{},p,output.parent),"issued claims digest")
    prefix=[x["label"] for x in B["manifest"]["joined_proofs"]]
    good={"terminal":"NATIVE_REJECTED","native_calls":1,"error":{"stage":"native_check","pending":"new-goal"},"verified_labels":prefix}
    assert negative_at_issued(good,claim,prefix)
    good["error"]["pending"]=prefix[0];assert not negative_at_issued(good,claim,prefix)
    return {"stopped":stopped,"saved_flag_refusal":reason,"negative_at_exact_issued":True}
def isolation_scope():
    rows=L.rows;rows["ax-pair"]["statement"].clear()
    manifest=L.manifest;manifest["axioms"].clear()
    assert restore(B).contracts==L.contracts and restore(B).pin==L.pin
    t=copy.deepcopy(T);t["context"]["dv"]=[["ph","ps"]]
    refused_context=solve(t,L,"enabled");assert refused_context["terminal"]=="UNKNOWN"
    base=native_text(BASE)+b"\n"+native_text("OPEN\n$d ph ps $.\nunsupported-dv $a |- ( ph -> ps ) $.\nCLOSE\n")
    lib=restore(bundle(base=base));t=copy.deepcopy(T);t["limits"]["max_decisions"]=1
    r=solve(t,lib,"resident-disabled")
    assert r["terminal"]=="UNKNOWN_PARENT_SCOPE" and r["unsupported_actions"]==[{"label":"unsupported-dv","reason":"DV outside qualified action interface"}],r
    return {"context_refusal":refused_context,"unsupported_parent":r}
for name,fn in (("arms_exact_emission",arms),("composite_repeated_substitution",composite),
                ("no_target_proof_oracle",oracle_refusal),("ordered_library_custody",library_refusals),
                ("bounded_failure_and_syntax_unknown",bound_unknown),("issued_output_binding",output_binding),
                ("native_boundary_without_native_call",native_boundary),("mutation_and_unsupported_scope",isolation_scope)):
    record(name,fn)
modules={n:str(Path(m.__file__).resolve()) for n,m in sorted(sys.modules.items()) if getattr(m,"__file__",None)}
modules.update({"dynamic."+n:str(Path(m.__file__).resolve()) for n,m in
                (("FS.C",FS.C),("FS.M",FS.M),("FS.T",FS.T),("FS.M.T",FS.M.T))})
receipt={"passed":all(r["passed"] for r in records) and native_calls==0,"tests_run":len(records),
         "tests":[r["id"] for r in records],"records":records,"native_calls":native_calls,
         "pid":os.getpid(),"parent_pid":os.getppid(),"cwd":os.getcwd(),"python":sys.executable,"imported_modules":modules,
         "scope":"Authored synthetic sources and goal search only; no retained data, native checks or scientific trial."}
with output.open("x") as f:f.write(json.dumps(receipt,indent=2,sort_keys=True,allow_nan=False)+"\n")
with (output.parent/"AUTHORED-INPUTS.json").open("x") as f:
    f.write(json.dumps({"base_source":B["base"].decode(),"joined_source":B["joined"].decode(),
                       "manifest":B["manifest"],"task":T},indent=2,sort_keys=True)+"\n")
print(json.dumps({"passed":receipt["passed"],"tests_run":len(records),"failures":[r["id"] for r in records if not r["passed"]]}))
raise SystemExit(0 if receipt["passed"] else 1)
