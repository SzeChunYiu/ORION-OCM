"""Actual failed-import replay and exact cache-probe controls; no native call."""
from pathlib import Path
import importlib.util,json,os,sys,time
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location("read_scope_candidate",ROOT/"run_b.py")
B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B);C=B.C
out=ROOT/"preflight/run-01";out.mkdir(exist_ok=False)
frozen=C.freeze();before={name:C.identity(ROOT/name) for name in frozen["sources"]}
failed=C.read(ROOT.parent/"native-typed-wff-lifecycle-v1/consumer-01/OPEN-AUDIT-FAILURE.json")
failed_probe=failed["open_attempts"][-1]["path"]
assert failed_probe=="__pycache__/life_payload.cpython-311.pyc"
allowed=set(frozen["sources"])|set(frozen["b_inputs"])|{"SOURCE-FREEZE.json"}
caches={Path(importlib.util.cache_from_source(str(ROOT/name))).absolute() for name in frozen["sources"]}
opened=[];forbidden=[]
def stop(*args,**kwargs):
    forbidden.append("native/learning function");raise AssertionError("FORBIDDEN_COMPUTATION")
C.native=stop
def audit(event,args):
    if event=="open" and isinstance(args[0],(str,bytes)):
        B.audit_open(Path(os.fsdecode(args[0])),args[1],args[2],ROOT,ROOT/"preflight",allowed,caches,opened)
sys.addaudithook(audit);started=time.perf_counter()
engine=C.engine()
engine["typed_extract"].extract=stop;engine["typed_constructor"].construct=stop;engine["typed_emit"].emit=stop
for name in ("life_payload","life_requests","life_native"):
    module=C.load(name,name+".py")
    if name=="life_native":module.verify=stop
assert any(r["path"]==failed_probe for r in opened)
assert any(r["path"].startswith("engine/") and r["path"].endswith(".pyc") for r in opened)
records=[{"check":"actual_failed_root_probe_and_all_B_helper_imports","pass":True},
         {"check":"actual_engine_cache_probes","pass":True}]
sandbox=out/"cache-sandbox";sandbox.mkdir();source=sandbox/"declared.py";source.write_text("CONTROL=1\n")
cache=Path(importlib.util.cache_from_source(str(source)));cache.parent.mkdir()
target=sandbox/"output";permitted={"declared.py"};registered={cache.absolute()}
def call(path,mode="r",flags=0):
    seen=[];B.audit_open(path,mode,flags,sandbox,target,permitted,registered,seen)
    assert seen
def reject(name,path,reason,mode="r",flags=0):
    try:call(path,mode,flags)
    except ValueError as exc:assert reason in str(exc)
    else:raise AssertionError("FALSE_ACCEPT:"+name)
    records.append({"check":name,"pass":True})
call(cache);records.append({"check":"declared_absent_read_probe","pass":True})
cache.write_bytes(b"existing cache control")
reject("existing_declared_cache",cache,"B_BYTECODE_PRESENT")
cache.unlink()
reject("write_probe",cache,"B_CACHE_PROBE_NOT_READ_ONLY","w",os.O_WRONLY|os.O_CREAT)
unissued=cache.with_name("unissued.cpython-311.pyc")
reject("absent_unissued_cache",unissued,"B_FORBIDDEN_READ")
unissued.write_bytes(b"unissued cache control")
reject("existing_unissued_cache",unissued,"B_FORBIDDEN_READ")
wrongtag=cache.with_name("declared.unissued-tag.pyc")
reject("unregistered_tag",wrongtag,"B_FORBIDDEN_READ")
reject("teaching_path",sandbox/"TRAINING.json","B_FORBIDDEN_READ")
call(source);records.append({"check":"declared_source_read","pass":True})
external=out/"external-cache";external.write_bytes(b"external cache control")
cache.symlink_to(external)
reject("existing_cache_symlink",cache,"B_BYTECODE_PRESENT")
after={name:C.identity(ROOT/name) for name in frozen["sources"]}
assert before==after and not forbidden
assert not any(path.exists() for path in caches)
C.write(out/"RESULT.json",{"terminal":"READ_SCOPE_CONTROLS_PASS","checks":records,"pid":os.getpid(),"parent_pid":os.getppid(),
 "actual_failed_probe":failed_probe,"open_attempts":opened,"sources_before":before,"sources_after":after,
 "native_calls":0,"bridge_calls":0,"learner_calls":0,"forbidden_calls":forbidden,
 "wall_s":time.perf_counter()-started,
 "scope":"Real B imports under corrected read guard, plus exact path controls. No reconstruction, bridge, extraction or native verifier function ran."})
print(json.dumps({"terminal":"READ_SCOPE_CONTROLS_PASS","checks":len(records),"native_calls":0}))
