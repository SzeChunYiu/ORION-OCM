"""Only the affected pre-seal source-review boundaries; no inherited suite replay."""
from pathlib import Path
import copy,hashlib,json,os,sys,time,traceback
ROOT=Path(__file__).resolve().parent
runtime=json.loads((ROOT/"inputs/RUNTIME.json").read_bytes())
for n,pin in runtime["files"].items():
    b=(Path(runtime["path"])/n).read_bytes()
    assert {"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}==pin
sys.path[:0]=[str(ROOT),str(ROOT/"vendor"),runtime["path"]]
from authored_fixture import bundle,restore,task
from goal_library import identity
from goal_solve import solve,validate_task
from goal_native import prepare,consumed_cohort
import finite_search as FS
import life_native as N
native_calls=0
def forbid(*a,**kw):
    global native_calls
    native_calls+=1;raise AssertionError("NATIVE_VERIFIER_FORBIDDEN")
N.verify=forbid
def refuse(fn,reason):
    try:fn()
    except ValueError as exc:assert reason in str(exc);return str(exc)
    raise AssertionError(reason)
started=time.perf_counter();record={"id":"finite_wall_consumption_materialization","passed":False}
try:
    b=bundle();lib=restore(b);t=task()
    reasons=[]
    for value in (float("inf"),float("-inf"),float("nan")):
        bad=copy.deepcopy(t);bad["limits"]["soft_wall_s"]=value
        reasons.append(refuse(lambda:validate_task(bad),"positive finite limits"))
    r=solve(t,lib,"enabled")
    assert r["terminal"]=="GENERATED_PROOF_PENDING_NATIVE",r
    assert r["generated_proof"]==["wph","wps","wch","search-hyp-0","learned-cut"]
    # A saved selection summary is not used as proof-consumption authority.
    r["selected_cohort_labels"]=[]
    claim=prepare(t,r,identity(r),lib,"fresh-issued",["fresh-h"])
    assert consumed_cohort(claim,"enabled",lib,{"wph","wps","wch","fresh-h","learned-cut"})==["learned-cut"]
    reasons.append(refuse(lambda:consumed_cohort(claim,"resident-disabled",lib),"disabled cohort"))
    reasons.append(refuse(lambda:consumed_cohort(claim,"enabled",lib,{"wph","fresh-h"}),"trace/proof"))
    r["mode"]="resident-disabled"
    reasons.append(refuse(lambda:prepare(t,r,identity(r),lib,"fresh-issued",["fresh-h"]),"disabled cohort"))
    changed=copy.deepcopy(t);changed["premises"]=[["|-","ps"]]
    reasons.append(refuse(lambda:prepare(changed,r,identity(r),lib,"fresh-issued",["fresh-h"]),"goal/library"))
    delta=r["library_costs"]["delta"]
    assert delta["snapshot_decodes"]>0 and delta["snapshot_bytes_materialized"]>0 and delta["snapshot_decode_wall_s"]>=0
    assert r["library_costs"]["before"]["source_index_calls"]==2
    record.update(passed=True,refusals=reasons,generated=claim,result=r)
except BaseException as exc:record.update(error=type(exc).__name__+": "+str(exc),traceback=traceback.format_exc())
record["wall_s"]=time.perf_counter()-started
modules={n:str(Path(m.__file__).resolve()) for n,m in sorted(sys.modules.items()) if getattr(m,"__file__",None)}
modules.update({"dynamic."+n:str(Path(m.__file__).resolve()) for n,m in
                (("FS.C",FS.C),("FS.M",FS.M),("FS.T",FS.T),("FS.M.T",FS.M.T))})
result={"passed":record["passed"] and native_calls==0,"tests_run":1,"tests":[record["id"]],"records":[record],
        "native_calls":native_calls,"pid":os.getpid(),"parent_pid":os.getppid(),"cwd":os.getcwd(),
        "python":sys.executable,"imported_modules":modules,"scope":"One affected authored successor control; no old-suite replay or native/data run."}
with Path(sys.argv[1]).open("x") as f:f.write(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
print(json.dumps({"passed":result["passed"],"native_calls":native_calls}))
raise SystemExit(0 if result["passed"] else 1)
