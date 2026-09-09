"""Focused glue refusal controls with explicit doubles; no donor execution."""
from pathlib import Path
import copy,hashlib,importlib.util,json,os,sys,types,time
HERE=Path(__file__).resolve().parent.parent
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m
C=load("life_common",HERE/"life_common.py")
D=load("life_discovery",HERE/"life_discovery.py")
paths=sorted(HERE.glob("*.py"));before={p.name:C.identity(p) for p in paths}
out=HERE/"preflight/failure-custody";out.mkdir(exist_ok=False);records=[];started=time.perf_counter()
real_gate=C.gate;real_check=C.check_sources
for state in (None,[{"path":"inputs/forbidden.json","mode":"r","flags":0}]):
    name="uninitialized" if state is None else "initialized";target=out/name
    C.AUDIT_READS=state;C.ACTIVE_WORK={"count_before_failure":7}
    C.gate=lambda role:{"source_freeze":{"bytes":0,"sha256":"unused_on_early_failure"}}
    oldargv=sys.argv;sys.argv=["control",str(target)]
    def fail(_):raise ValueError("CONTROL_FAILURE")
    try:C.invocation(fail,"B")
    except ValueError as exc:C.require(str(exc)=="CONTROL_FAILURE","CONTROL_EXCEPTION")
    finally:sys.argv=oldargv
    audit=C.read(target/"OPEN-AUDIT-FAILURE.json");failure=C.read(target/"FAILURE.json")
    C.require(audit["open_attempts"]==state and audit["status"]==
              ("UNINITIALIZED" if state is None else "INITIALIZED_AT_FAILURE"),"FAILURE_AUDIT")
    C.require(failure["work"]=={"count_before_failure":7} and "bytes_read" in failure["common_io"],"FAILURE_COSTS")
    records.append({"check":"B_failure_"+name,"pass":True})
C.gate=real_gate
sandbox=out/"anchored";sandbox.mkdir();(sandbox/"known.py").write_text("VALUE=1\n")
def write_manifest():
    value={"sources":{"known.py":C.identity(sandbox/"known.py")},"inputs":{},"b_inputs":[]}
    (sandbox/"SOURCE-FREEZE.json").write_text(json.dumps(value,sort_keys=True)+"\n")
write_manifest();opening=C.identity(sandbox/"SOURCE-FREEZE.json")
original_here=C.HERE;C.HERE=sandbox
C.check_sources(expected_freeze=opening)
(sandbox/"known.py").write_text("VALUE=2\n");write_manifest()
C.check_sources() # A self-consistent replacement demonstrates why the opening anchor matters.
try:C.check_sources(expected_freeze=opening)
except ValueError as exc:C.require(str(exc)=="FREEZE_CHANGED","ANCHOR_EXCEPTION")
else:raise AssertionError("manifest replacement accepted")
C.HERE=original_here
records.append({"check":"clean_anchor_then_self_consistent_replacement_refused","pass":True})
meaning_calls=[]
good={"terminal":"INTERPRETATION_EQUIVALENT","worlds":255,"table":[],
      "gates":{"premises_satisfiable":{"world_mask":1},"query_not_tautological":{"world_mask":2},
               "entailment_counterexample":None,"essentiality_counterexamples":[{"world_mask":3}]}}
def meaning(source,bridge,contract,verifier):
    meaning_calls.append(source["label"]);value=copy.deepcopy(good)
    if len(meaning_calls)==2:value["gates"]["premises_satisfiable"]=None
    return value
doubles={"unary_contract":object(),"unary_verify":object(),
 "registered_bridge_syntax":types.SimpleNamespace(translate=lambda *args:{"task":{"predicates":["P","Q","R"]}}),
 "registered_bridge_meaning":types.SimpleNamespace(check=meaning),
 "registered_signatures":types.SimpleNamespace(canonical=lambda *args:{"joint_premise_query":{"sha256":"control-signature"}})}
C.load=lambda name,path:doubles[name]
training={"selected":["control-source-0","control-source-1"],"contracts":{},"traces":{}}
for label in training["selected"]:
 training["traces"][label]={"nodes":[],"source":{"label":label,"statement":["|-","control"],"essential":[],
                                               "floating":[],"proof":["control-proof"]}}
extractor=types.SimpleNamespace(extract=lambda *args:[{"body":{"control":"returned-body"},"source_root":1,
                                      "source_nodes":[0,1],"context":{"control":"typed"}}])
work={}
try:D.discover(training,{"typed_extract":extractor},work,out/"discovery")
except ValueError as exc:C.require(str(exc)=="SOURCE_MEANING_GATES","DISCOVERY_EXCEPTION")
else:raise AssertionError("failed bridge gate accepted")
progress=[C.read(p) for p in sorted((out/"discovery").glob("*.json"))];last=progress[-1]
C.require(last["status"]=="FAILED" and last["stage"]=="meaning_gates" and len(last["contexts"])==2
          and len(last["groups"])==1 and len(last["occurrences"])==1,"DISCOVERY_PROGRESS")
C.require(last["current"]["meaning"]["gates"]["premises_satisfiable"] is None and
          work["bridge_attempts"]==2 and work["bridge_completed_worlds"]==510 and
          work["bridge_accepted_worlds"]==255 and work["returned_candidates"]==1,"DISCOVERY_WORK")
records.append({"check":"earlier_candidate_and_refused_context_survive","pass":True})
after={p.name:C.identity(p) for p in paths};C.require(before==after,"SOURCE_CHANGED")
C.write(out/"RESULT.json",{"terminal":"FAILURE_CUSTODY_GLUE_CONTROLS_PASS","checks":records,
 "pid":os.getpid(),"parent_pid":os.getppid(),"native_calls":0,"registered_bridge_calls":0,"learner_calls":0,
 "double_meaning_calls":len(meaning_calls),"sources_before":before,"sources_after":after,
 "wall_s":time.perf_counter()-started,
 "scope":"Actual glue with explicit data-returning doubles; no native or registered meaning/extraction module executed"})
print(json.dumps({"terminal":"FAILURE_CUSTODY_GLUE_CONTROLS_PASS","checks":len(records),"native_calls":0}))
