"""Only authored formal-frame and scoped-label transport controls."""
from pathlib import Path
import copy,hashlib,json,os,sys,time,traceback
ROOT=Path(__file__).resolve().parent
runtime=json.loads((ROOT/"inputs/RUNTIME.json").read_bytes())
for n,pin in runtime["files"].items():
    b=(Path(runtime["path"])/n).read_bytes()
    assert {"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}==pin
sys.path[:0]=[str(ROOT),str(ROOT/"vendor"),runtime["path"]]
from authored_fixture import bundle,restore,task,native_text
from goal_library import identity,raw_identity
from goal_solve import solve
from cohort_suffix import construct
import trace_source as S
import life_native as N
import finite_search as FS
native_calls=0
def forbid(*a,**kw):
    global native_calls
    native_calls+=1;raise AssertionError("NATIVE_FORBIDDEN")
N.verify=forbid
BASE=native_text("""
$c class wff |- C_ $.
$v A B C V $.
cA $f class A $.
cB $f class B $.
cC $f class C $.
cV $f class V $.
wss $a wff A C_ B $.
OPEN
parent-h $e |- A C_ B $.
z-transport $a |- A C_ V $.
CLOSE
""")
SUFFIX=native_text("""
OPEN
local-h $e |- A C_ B $.
learned-abv $p |- A C_ V $= cA cB cV local-h z-transport $.
CLOSE
""")
records=[]
def run(name,fn):
    started=time.perf_counter()
    try:detail=fn();records.append({"id":name,"passed":True,"detail":detail,"wall_s":time.perf_counter()-started})
    except BaseException as exc:records.append({"id":name,"passed":False,"error":str(exc),"traceback":traceback.format_exc()})
def alpha():
    b=bundle(base=BASE,suffix=SUFFIX);lib=restore(b);before=identity(lib.rows)
    t=task();t.update(query=["|-","A","C_","C"],premises=[["|-","A","C_","B"]])
    t["context"]["parameters"]=[{"id":"V"+str(i),"type":"class","variable":v,"floating_label":"c"+v}
                                for i,v in enumerate(("A","B","C"))]
    out=[solve(t,lib,"enabled"),solve(t,lib,"resident-disabled"),solve(t,restore(copy.deepcopy(b)),"restored")]
    assert all(x["terminal"]=="GENERATED_PROOF_PENDING_NATIVE" for x in out),out
    assert [x["generated_proof"] for x in out]==[
        ["cA","cB","cC","search-hyp-0","learned-abv"],
        ["cA","cB","cC","search-hyp-0","z-transport"],
        ["cA","cB","cC","search-hyp-0","learned-abv"]]
    for k in ("bank_identity","grounded_actions_identity","emission_syntax_identity"):
        assert out[0][k]==out[1][k]==out[2][k],k
    assert out[0]["resident_hint_bindings"][0]["hint_only_renaming"]=={"A":"A","B":"B","V":"C"}
    assert out[0]["bank"]["wff"]==[{"tokens":["V0","C_","V2"]},{"tokens":["V0","C_","V1"]}]
    assert identity(lib.rows)==before and lib.rows["learned-abv"]["proof"]==["cA","cB","cV","local-h","z-transport"]
    return out
def scoped():
    rows,_=S.index(BASE+b"\n"+SUFFIX);r=rows["learned-abv"]
    first={"contract":S.contract(r),"proof":r["proof"],"origin":{"authored":"first"}}
    second=copy.deepcopy(first);second["contract"]["label"]="learned-abv-2";second["origin"]={"authored":"second"}
    members=[first,second];original=identity(members)
    info,suffix=construct(BASE,raw_identity(BASE),members,original)
    indexed,_=S.index(BASE+b"\n"+suffix)
    assert indexed["learned-abv"]["proof"]==["cA","cB","cV","cohort-e-0-0","z-transport"]
    assert indexed["learned-abv-2"]["proof"]==["cA","cB","cV","cohort-e-1-0","z-transport"]
    assert [x["essential_label_renaming"] for x in info["bindings"]]==[
        [{"old":"local-h","new":"cohort-e-0-0","statement":["|-","A","C_","B"]}],
        [{"old":"local-h","new":"cohort-e-1-0","statement":["|-","A","C_","B"]}]]
    assert identity(members)==original and not info["native_acceptance"]
    collisions=copy.deepcopy(members);collisions[0]["contract"]["label"]="cohort-e-0-0"
    try:construct(BASE,raw_identity(BASE),collisions,identity(collisions))
    except ValueError as exc:assert str(exc)=="new essential-label collision"
    else:raise AssertionError("transport collision accepted")
    return {"transport":info,"suffix":suffix.decode(),"input_unchanged":True,"collision_refused":True}
run("indexed_ABV_hint_to_ABC_all_arms",alpha);run("duplicate_scoped_essential_transport",scoped)
modules={n:str(Path(m.__file__).resolve()) for n,m in sorted(sys.modules.items()) if getattr(m,"__file__",None)}
modules.update({"dynamic."+n:str(Path(m.__file__).resolve()) for n,m in
                (("FS.C",FS.C),("FS.M",FS.M),("FS.T",FS.T),("FS.M.T",FS.M.T))})
result={"passed":all(r["passed"] for r in records) and native_calls==0,"tests_run":2,
        "tests":[r["id"] for r in records],"records":records,"native_calls":native_calls,"pid":os.getpid(),
        "parent_pid":os.getppid(),"cwd":os.getcwd(),"python":sys.executable,"imported_modules":modules,
        "scope":"Authored synthetic transport only; no historical cohort rows or native verification."}
with Path(sys.argv[1]).open("x") as f:f.write(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
print(json.dumps({"passed":result["passed"],"native_calls":native_calls}))
raise SystemExit(0 if result["passed"] else 1)
