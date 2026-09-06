"""Read copied historical events and exact kernels; never call solve or an external backend."""
from pathlib import Path
from collections import Counter, defaultdict
from dataclasses import asdict
from fractions import Fraction
from datetime import datetime, timezone
import ast, hashlib, json, os, resource, socket, subprocess, sys, time
ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT/"source/src")]
from ocm.runtime.ocm_runtime import OCMRuntime, RuntimeState
from ocm.runtime import solve as SV
from ocm.kso import navigation as N, admission as AD, abstraction as AB
from ocm.kso.ids import content_hash
from ocm.store.event import OCMEvent, EventType, verify_chain
from ocm.store.ledger import compute_entry_hash

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def wire(x):
    if isinstance(x, Fraction): return str(x)
    if isinstance(x, dict): return {str(k):wire(v) for k,v in x.items()}
    if isinstance(x, (tuple,list,set,frozenset)): return [wire(v) for v in x]
    if hasattr(x,"value"): return x.value
    return x
def save(name, data):
    p=ROOT/name
    with p.open("x") as f: json.dump(wire(data),f,indent=2,sort_keys=True);f.write("\n")
blocked = Counter()
def forbid(name):
    def call(*a, **kw):
        blocked[name] += 1
        raise RuntimeError("FORBIDDEN_INSPECTION_CALL:"+name)
    return call
for obj,name in ((SV,"solve"),(N,"fixed_point"),(N,"navigate"),(OCMRuntime,"solve"),(OCMRuntime,"register_operator"),(OCMRuntime,"_emit"),(OCMRuntime,"persist"),(subprocess,"Popen"),(socket,"socket")):
    setattr(obj,name,forbid(obj.__name__+"."+name))
t0=time.monotonic();cpu0=resource.getrusage(resource.RUSAGE_SELF)
plan=json.loads((ROOT/"PLAN.json").read_text());f0=json.loads((ROOT/"input/F0.json").read_text())
for rel,h in plan["inputs"].items(): assert sha(ROOT/"input"/rel)==h
for rel,h in f0["source_files"].items(): assert sha(ROOT/"source"/rel)==h
rows=[json.loads(x) for x in (ROOT/"input/5-restore-ocm.rows.jsonl").read_text().splitlines()]
row=next(x for x in rows if x["id"]==plan["target_request_id"]);request=row["request"]
assert content_hash(request)=="3502ac21fa061522a385dfb68edcaf1a7e4f907f7a171bae2e671d90abc1c7f4"
ledger=[json.loads(x) for x in (ROOT/"input/ocm-state/ledger.jsonl").read_text().splitlines()]
prev="0"*64
for i,record in enumerate(ledger,1):
    assert record["sequence"]==i and record["prev_hash"]==prev
    assert record["entry_hash"]==compute_entry_hash(i,record["kind"],record["payload"],prev)
    prev=record["entry_hash"]
events=[OCMEvent.from_dict(r["payload"]) for r in ledger if r["kind"]=="OCM_EVENT"]
verify_chain(events)
target=next(e for e in events if e.sequence==plan["target_query_event"])
assert target.event_type is EventType.QUERY_OPENED and target.payload["task_id"]==row["result"]["trace"]["task_id"]
runtime=OCMRuntime.__new__(OCMRuntime);runtime.state=RuntimeState();runtime.events=[]
reducer=Counter();support_calls=Counter()
for name in ("ungated_closure","positive_activation_support"):
    original=getattr(AD,name)
    def count(ks,*args,_name=name,_fn=original,**kwargs):
        support_calls[_name+".calls"]+=1
        support_calls[_name+".supplied_atoms_sum"]+=len(ks.ids)
        support_calls[_name+".supplied_edges_sum"]+=len(ks.hyperedges)
        return _fn(ks,*args,**kwargs)
    setattr(AD,name,count)
for e in events:
    e.expectation.check(log_head=runtime.events[-1].event_hash if runtime.events else None,
        kso_state_hash=runtime.state.kso_state_hash,registry_revision=runtime.state.registry_revision,evidence_epoch=runtime.state.evidence_epoch)
    if e.sequence==target.sequence: break
    runtime._apply(e);runtime.events.append(e);runtime.state.meter=runtime.state.meter+e.resources
    reducer[e.event_type.value]+=1
assert runtime.state.kso_state_hash==plan["target_state_hash"]==target.expectation.kso_state_hash
ks=runtime.state.ks;revoked=runtime.state.revoked
assert sorted(revoked)==row["authority"]["revoked"]
g1=(ROOT/"source/research/ocm-prototype/g1_vessel.py").read_text()
assert "CONFIG = SV.SolveConfig(exact_extraction_max_atoms=0)" in g1
cfg=SV.SolveConfig(exact_extraction_max_atoms=0)
field_tree=ast.parse((ROOT/"source/research/ocm-prototype/g1_field.py").read_text())
encode_node=next(n for n in field_tree.body if isinstance(n,ast.FunctionDef) and n.name=="encode")
ns={"json":json};exec(compile(ast.Module(body=[encode_node],type_ignores=[]),"<source-bound g1_field.encode>","exec"),ns)
qid="clia:application:"+content_hash(request)
refs=(qid,"g1:model","g1:clia",*(x for x in ks.ids if x.startswith("clia:executable:")))
task=SV.Task(qid,(SV.QueryPart(ns["encode"](request),"query_seed",refs),),context="g1-pilot")
assert refs==target.input_object_ids and task.targets==tuple(target.payload["targets"])
atomised,seed=SV.atomise(ks,task)
trace=row["result"]["trace"]["stages"]
assert atomised.payload==next(x["payload"] for x in trace if x["stage"]=="GROUNDING")
assert len(ks.ids)==next(x["payload"]["atoms"] for x in trace if x["stage"]=="REPRESENTATION")
models={mode.value:N.navigation_matrix(ks,revoked=revoked,relevance=cfg.relevance,mode=mode) for mode in N.NavigationMode}
matrix_summary={};joint=set(ks.ids);atom_rows={}
for mode,m in models.items():
    incoming=Counter();outgoing=Counter()
    for i,r in enumerate(m.rows):
        for j,v in enumerate(r):
            if v: outgoing[m.ids[i]]+=1;incoming[m.ids[j]]+=1
    zero={x for x in m.ids if not incoming[x] and not outgoing[x]};joint &= zero
    matrix_summary[mode]={"nonzero_entries":sum(outgoing.values()),"zero_incident_atoms":sorted(zero),"zero_incident_count":len(zero),
        "outgoing_nonzero_by_atom":dict(outgoing),"incoming_nonzero_by_atom":dict(incoming)}
for i,a in enumerate(ks.atoms):
    atom_rows[a.atom_id]={"liveness":a.liveness(revoked).value,"warrant":a.warrant.as_dict(),
        "atom_type":a.atom_type,"scope":a.scope.as_dict(),"authority":a.authority.as_dict(),"joint_zero_incident":a.atom_id in joint,
        "query_seed":seed[ks.ids.index(a.atom_id)],"required_fine_output":True}
groups=defaultdict(list)
for x in sorted(joint):groups[ks.atom(x).liveness(revoked).value].append(x)
blocks=[tuple(v) for v in groups.values() if len(v)>1]
assert AB.warrant_measurable(ks,tuple(blocks),(revoked,))
n=len(ks.ids);dimension=n-sum(len(b)-1 for b in blocks)
save("kernels.json",{mode:{"ids":m.ids,"rows":m.rows,"denominators":m.denominators} for mode,m in models.items()})
save("atoms.json",atom_rows)
for rel,h in plan["inputs"].items(): assert sha(ROOT/"input"/rel)==h
for rel,h in f0["source_files"].items(): assert sha(ROOT/"source"/rel)==h
cpu=resource.getrusage(resource.RUSAGE_SELF)
result={"schema":"OCM.G1RepresentationApplicabilityResult.v1","source_commit":plan["source_commit"],"request_id":row["id"],"request":request,
    "snapshot":"original query-open pre-solve expectation","event_sequence":target.sequence,"event_hash":target.event_hash,
    "kso_state_hash":runtime.state.kso_state_hash,"ks_digest":ks.digest(),"N":n,"hyperedges":len(ks.hyperedges),"revoked":sorted(revoked),
    "task":asdict(task),"config":asdict(cfg),"seed":dict(zip(ks.ids,seed)),"global_uniform_mass":Fraction(1,n),
    "modes":matrix_summary,"joint_zero_incident_atoms":sorted(joint),"candidate_blocks":blocks,"eligible_solve_dimension":dimension,
    "terminal":"ELIGIBLE_ZERO_INCIDENT_BLOCK" if blocks else "NO_ELIGIBLE_ZERO_INCIDENT_COMPRESSION_AT_THIS_SNAPSHOT",
    "warrant_scope":"actual current revocation only; exact three-valued measurability; no new revision family",
    "required_output_scope":"original per-atom warranted/exploratory/background values and identities remain required; no atom/metadata deletion",
    "global_work":{"ledger_rows_hash_checked":len(ledger),"event_chain_hash_checked":len(events),"expectation_checks":target.sequence,
        "reducer_applies":len(runtime.events),"reducer_events_by_type":dict(reducer),"support_reconstruction_calls":dict(support_calls),
        "source_files_hash_checked_each_pass":len(f0["source_files"]),"source_hash_passes":2,"kernel_calls":2,
        "dense_matrix_cells_materialized":2*n*n,"matrix_entries_inspected":2*n*n,"atoms_metadata_inspected":n,
        "serialized_kernel_bytes":(ROOT/"kernels.json").stat().st_size,"serialized_atom_bytes":(ROOT/"atoms.json").stat().st_size},
    "forbidden_call_attempts":dict(blocked),"model_solver_modules_loaded":[x for x in ("cvc5","z3","ufal.udpipe","torch") if x in sys.modules],
    "elapsed_descriptive_seconds":time.monotonic()-t0,"self_cpu_user_seconds":cpu.ru_utime-cpu0.ru_utime,
    "self_cpu_system_seconds":cpu.ru_stime-cpu0.ru_stime,"maxrss_kib":cpu.ru_maxrss,
    "cost_scope":"single read-only inspection; global replay/hash/support/kernel work included; not a timing comparison or scalable implementation",
    "actor_model_solver_operator_calls":0,"inputs_unchanged":True,"finished_utc":datetime.now(timezone.utc).isoformat()}
save("RESULT.json",result)
print(json.dumps({k:wire(result[k]) for k in ("terminal","N","hyperedges","eligible_solve_dimension","joint_zero_incident_atoms","global_work","forbidden_call_attempts","model_solver_modules_loaded","elapsed_descriptive_seconds")},sort_keys=True))
