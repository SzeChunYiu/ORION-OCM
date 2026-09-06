"""One guarded current-core restore; no consumer, fixed point or domain invocation."""
from pathlib import Path
from collections import Counter
from dataclasses import asdict
from fractions import Fraction
from importlib.metadata import version
import hashlib, json, resource, socket, subprocess, sys, time
from restore_context import HERE, restore, sha

sys.path[:0] = [str(HERE / "source/src")]
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.runtime import solve as SV
from ocm.kso import navigation as N
from ocm.kso.ids import content_hash

blocked = Counter()
def forbid(name):
    def call(*args, **kwargs):
        blocked[name] += 1
        raise RuntimeError("FORBIDDEN_PREPARATION_CALL:" + name)
    return call
for obj, name in ((SV,"solve"),(N,"fixed_point"),(N,"navigate"),(OCMRuntime,"solve"),
                  (OCMRuntime,"register_operator"),(OCMRuntime,"_emit"),(OCMRuntime,"persist"),
                  (subprocess,"Popen"),(socket,"socket")):
    setattr(obj, name, forbid(obj.__name__ + "." + name))
def wire(x):
    if isinstance(x,Fraction): return str(x)
    if isinstance(x,dict): return {k:wire(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)): return [wire(v) for v in x]
    if hasattr(x,"value"): return x.value
    return x

t=time.monotonic(); c0=resource.getrusage(resource.RUSAGE_SELF)
context=restore(); runtime=context["runtime"]; state=runtime.state
manifest=context["manifest"]
programs={}
bindings=json.loads((HERE/"input/ocm-state/study-bindings.json").read_text())
for alias,b in bindings["programs"].items():
    aid="clia:executable:"+b["descriptor_id"]; atom=state.ks.atom_map()[aid]
    stored=json.loads(dict(atom.meta)["data"])
    assert content_hash(stored)==atom.content_ref
    desc=stored["descriptor"]
    assert desc==b["descriptor"] and desc["id"]==b["descriptor_id"]
    prior_matches={name:prior==manifest["source_files"]["research/ocm-prototype/"+name]["sha256"]
                   for name,prior in desc["checker_prior"]["files"].items()}
    programs[alias]={"descriptor_id":desc["id"],"program_sha256":desc["program_sha256"],
                     "liveness":atom.liveness(state.revoked).value,
                     "support":desc["support"],"checker_prior_z3":desc["checker_prior"]["z3"],
                     "checker_prior_files_match_current":prior_matches}
assert all(p["liveness"]=="LIVE" and all(p["checker_prior_files_match_current"].values()) for p in programs.values())
assert all(p["checker_prior_z3"]==version("z3-solver") for p in programs.values())
assert len(state.ks.ids)==78 and len(state.ks.hyperedges)==146
assert len(state.operator_manifests)==2 and len(state.operators.operators)==0
assert context["config"].surprise_model.value=="UNIFORM"
assert not blocked
rows=[json.loads(line) for line in (HERE/"input/5-restore-ocm.rows.jsonl").read_text().splitlines()]
c1=resource.getrusage(resource.RUSAGE_SELF)
record={"status":"RESTORED_EXACT_CONTEXT__HOST_CALLABLES_UNBOUND",
        "current_source_commit":manifest["current_source_commit"],"original_source_commit":manifest["original_source_commit"],
        "N":len(state.ks.ids),"hyperedges":len(state.ks.hyperedges),"event_count":len(runtime.events),
        "kso_state_hash":state.kso_state_hash,"registry_revision":state.registry_revision,"evidence_epoch":state.evidence_epoch,
        "operator_manifests":state.operator_manifests,"host_bound_operators":len(state.operators.operators),
        "evidence_records":len(state.evidence.records),"revoked":sorted(state.revoked),"nogoods":state.nogoods.as_dict(),
        "programs":programs,"config":asdict(context["config"]),"task":asdict(context["task"]),
        "seed":dict(zip(state.ks.ids,context["seed"])),"request":context["request"],
        "restored_phase_original_rows":[{"id":r["id"],"kind":r["request"]["kind"]} for r in rows],
        "source_files_checked":len(manifest["source_files"]),"model_files_copied":False,
        "forbidden_call_attempts":dict(blocked),
        "model_solver_modules_loaded":[n for n in ("cvc5","z3","ufal.udpipe","torch") if n in sys.modules],
        "scope":"read-only current-core restore and metadata; callable rebinding, Z3 application/check and SV consumer NOT_EXECUTED",
        "minimum_future_binding":"existing clia_reuse_vessel.bind for both live descriptors; existing catalogue; same SV.solve",
        "cost_boundary":"hash/input read+replay+host rebind/compilation before consumer, then four navigation calls+full consumer+real Z3 application/check; no model or synthesis needed for this request",
        "descriptive_wall_seconds":time.monotonic()-t,
        "self_user_seconds":c1.ru_utime-c0.ru_utime,"self_system_seconds":c1.ru_stime-c0.ru_stime,
        "maxrss_kib":c1.ru_maxrss,"ledger_unchanged":sha(HERE/"prefix-state/ledger.jsonl")==manifest["prefix_ledger_sha256"]}
with (HERE/"RESTORE_RECEIPT.json").open("x") as f:json.dump(wire(record),f,indent=2,sort_keys=True);f.write("\n")
print(json.dumps({k:wire(record[k]) for k in ("status","N","hyperedges","event_count","kso_state_hash","host_bound_operators","forbidden_call_attempts","model_solver_modules_loaded","descriptive_wall_seconds")}))
