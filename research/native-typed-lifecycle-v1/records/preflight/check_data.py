"""Data-only actual-envelope and direct-transport preflight; no native/bridge/learner."""
from pathlib import Path
import copy,hashlib,importlib.util,itertools,json,os,sys,time
HERE=Path(__file__).resolve().parent.parent
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module
C=load("life_common",HERE/"life_common.py")
R=load("life_requests",HERE/"life_requests.py")
P=load("life_payload",HERE/"life_payload.py")
calls=[]
def prohibited(*args,**kwargs):
    calls.append(str(args));raise AssertionError("NATIVE_BRIDGE_LEARNER_IMPORT_PROHIBITED")
C.load=prohibited
start=time.perf_counter();records=[]
paths=sorted(HERE.glob("*.py"))+sorted((HERE/"engine").rglob("*.py"))+sorted((HERE/"authority").glob("*.py"))
before={str(p.relative_to(HERE)):C.identity(p) for p in paths}
packet=C.read(HERE/"inputs/fixtures/FIXTURES.json")
context={"schema":"native.typed-context.v1","dv":[],"parameters":[
    {"id":"V"+str(i),**p} for i,p in enumerate(packet["parameters"])]}
for i,fixture in enumerate(packet["fixtures"]):
    source={"floating":[{"label":p["floating_label"],"statement":[p["type"],p["variable"]]}
                        for p in packet["parameters"]],
            "essential":[{"label":h,"statement":p} for h,p in zip(fixture["holes"],fixture["premises"])],
            "statement":fixture["query"],"proof":fixture["proof"]}
    row={"id":"fixture-envelope-"+str(i),"context":context,"trace":{"source":source}}
    identity=R.issue(row,10+i,["ph","ps","ch"],"preflight_only")
    expected=copy.deepcopy(fixture);expected["label"]="typed-reconstruct-"+str(10+i)
    new_holes=[expected["label"]+".h"+str(j) for j in range(2)]
    table=dict(zip(fixture["holes"],new_holes))
    expected["holes"]=new_holes;expected["proof"]=[table.get(t,t) for t in fixture["proof"]]
    expected["parameters"]=packet["parameters"]
    C.require(identity["claim"]==expected,"ACTUAL_IDENTITY_ENVELOPE")
    records.append({"check":"actual_identity_envelope_"+str(i),"pass":True,"normal_labels":len(expected["proof"])})
    cyclic=R.issue(row,20+i,["ps","ch","ph"],"preflight_only")
    h0="typed-reconstruct-"+str(20+i)+".h0";h1="typed-reconstruct-"+str(20+i)+".h1"
    root0=("wps wch wph wa wph wps wch wph H0 wps wch wph H0 H1 syl jca wch wph simpr syl").split()
    oracle=root0 if i==0 else ["wps","wph","wch"]+root0+["H1","jaoi"]
    oracle=[{"H0":h0,"H1":h1}.get(t,t) for t in oracle]
    C.require(cyclic["claim"]["proof"]==oracle,"AUTHORED_CYCLIC_PROOF_ORACLE")
    query0=["|-","(","ps","->","ph",")"]
    query1=["|-","(","(","ps","\\/","ch",")","->","ph",")"]
    C.require(cyclic["claim"]["query"]==[query0,query1][i] and
              cyclic["claim"]["premises"]==[["|-","(","ps","->","ch",")"],["|-","(","ch","->","ph",")"]],
              "AUTHORED_CYCLIC_TASK_ORACLE")
    C.require([p["floating_label"] for p in cyclic["context"]["parameters"]]==["wps","wch","wph"],
              "CONTEXT_FLOAT_TRANSPORT")
    records.append({"check":"actual_cyclic_manual_oracle_"+str(i),"pass":True,"normal_labels":len(oracle)})
    issued=[R.issue(row,30+j,perm,"preflight_only") for j,perm in
            enumerate(itertools.permutations(["ph","ps","ch"]))]
    C.require(len({C.digest(x["renaming"]) for x in issued})==6,"SIX_PERMUTATIONS")
    records.append({"check":"six_permutations_"+str(i),"pass":True})
out=HERE/"preflight"/"run-02";out.mkdir(exist_ok=False)
interrupted={"exit_code":0,"reaped":False,"sources_unchanged":True,"request_unchanged":True}
C.write(out/"INTERRUPTED.json",interrupted)
try:P.project(out/"absent-state.json",out/"INTERRUPTED.json",out/"absent-result.json",out/"forbidden.json",{})
except ValueError as exc:C.require(str(exc)=="PRODUCER_NOT_CLEANLY_EXITED","INTERRUPTED_PREFLIGHT")
else:raise AssertionError("interrupted accepted")
records.append({"check":"interrupted_before_state_read","pass":True})
copy_path=out/"source-copy.py";copy_path.write_bytes((HERE/"life_common.py").read_bytes())
pin=C.identity(copy_path);C.require(pin==C.identity(HERE/"life_common.py"),"ACTUAL_SOURCE_NO_ALARM")
copy_path.write_bytes(copy_path.read_bytes()+b" ")
try:C.checked(copy_path,pin)
except ValueError as exc:C.require(str(exc)=="FILE_BINDING_CHANGED","SOURCE_TAMPER_PREFLIGHT")
else:raise AssertionError("source tamper accepted")
records.append({"check":"actual_source_clean_then_tampered","pass":True})
after={str(p.relative_to(HERE)):C.identity(p) for p in paths}
C.require(before==after and not calls,"SOURCE_OR_PROHIBITION")
C.write(out/"RESULT.json",{"terminal":"DATA_ONLY_PREFLIGHT_PASS","pid":os.getpid(),"parent_pid":os.getppid(),
    "checks":records,"forbidden_calls":calls,"native_calls":0,"bridge_calls":0,"learner_calls":0,
    "sources_before":before,"sources_after":after,"wall_s":time.perf_counter()-start,
    "scope":"actual two fixture envelopes/direct label transport and pre-state refusal; no native or trace qualification"})
print(json.dumps({"terminal":"DATA_ONLY_PREFLIGHT_PASS","checks":len(records),"native_calls":0}))
