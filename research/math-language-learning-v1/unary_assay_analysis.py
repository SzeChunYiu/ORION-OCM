"""Read-only analysis of retained coordinator records, source-bound and rechecked."""
import time
from pathlib import Path
from unary_assay_ledger import replay,read,inventory
from unary_assay_phase import ARMS,BACKEND,ROLES,order
from unary_assay_auth import inspect,ControlFailure,CustodyFailure
from unary_assay_controls import decide,overall
from unary_assay_economics import evaluate
import unary_assay_recheck as R
import unary_assay_obligations as O
import unary_method_plain as D

def schedule_ids(e):
    a=("ADAPTIVE_PARENT","OCM_ENABLED") if e%2==0 else ("OCM_ENABLED","ADAPTIVE_PARENT")
    ids=[R.key(e,"A",arm) for arm in a]
    ids += [R.key(e,phase,arm) for phase in ("B","C") for arm in order(e)]
    ids += [R.key(e,role+"-"+action,arm) for role in ROLES for arm in order(e)
            for action in ("withdraw","withdrawn","reinstate","restored")]
    return ids

def slots(events,manifest):
    result={};order_seen=[]
    for event in events:
        body=event["body"]
        if event["kind"]=="EXPECTED":
            slot=body["slot"]
            if slot in result:raise CustodyFailure("DUPLICATE_EXPECTED")
            result[slot]={"state":"REQUESTED","detail":{k:v for k,v in body.items() if k!="slot"}}
        elif event["kind"]=="SLOT":
            slot=body["slot"];value={k:v for k,v in body.items() if k!="slot"}
            if slot not in result or value["detail"]!=result[slot]["detail"]:raise CustodyFailure("SLOT_IDENTITY")
            allowed={"REQUESTED":("ATTEMPTED","UNAVAILABLE","NOT_APPLICABLE"),"ATTEMPTED":("COMPLETED","UNAVAILABLE")}
            if value["state"] not in allowed.get(result[slot]["state"],()):raise CustodyFailure("SLOT_TRANSITION")
            if value["state"]=="ATTEMPTED":order_seen.append(slot)
            result[slot]=value
    if result!=manifest["slots"]:raise CustodyFailure("SLOT_MANIFEST")
    sequence=[s for e in range(len(manifest["episodes"])) for s in schedule_ids(e)]
    if set(result)!=set(sequence) or order_seen!=[s for s in sequence if s in order_seen]:
        raise ControlFailure("DISPATCH_ORDER")
    if any(s["state"] in ("REQUESTED","ATTEMPTED") for s in result.values()):raise CustodyFailure("UNFINALIZED_SLOT")
    return result

def stable_facts(value):
    if value is None:return None
    return {k:v for k,v in value.items() if k not in ("replay_work",)}

def _analyze(root,*,expected_sources,work):
    start=time.monotonic();cpu=time.process_time();root=Path(root)
    events=replay(root/"ledger")
    if not events or events[-1]["kind"]!="FINAL":raise CustodyFailure("INCOMPLETE_COORDINATOR")
    manifest=read(root,events[-1]["body"])
    if manifest["sources"]!=expected_sources:raise CustodyFailure("ANALYSIS_SOURCE_BINDING")
    if str(root)!=manifest["root"]:raise CustodyFailure("ANALYSIS_ROOT")
    ledger_slots=slots(events,manifest);calls=[];copies=[]
    expected_reports={ref["path"] for ref in [*manifest["calls"],*manifest["copies"]]}
    if {p.name for p in (root/"reports").iterdir()}!=expected_reports:raise CustodyFailure("REPORT_MEMBERSHIP")
    if [e["body"] for e in events if e["kind"]=="COPY"]!=manifest["copies"]:raise CustodyFailure("COPY_MANIFEST")
    for ref in manifest["copies"]:
        copy=read(root/"reports",ref)
        if copy["before"]!=copy["after"] or copy["before"]!=copy["copied"]:raise CustodyFailure("COPY_BINDING")
        copies.append(copy)
    for ref in manifest["calls"]:
        record=read(root/"reports",ref);slot=record["slot"];path=root/"calls"/slot
        if record["path"]!=str(path) or ledger_slots[slot].get("record")!=ref:raise CustodyFailure("CALL_REFERENCE")
        if record["source_before"]!=expected_sources or record["source_after"]!=expected_sources:
            # Source-failed records retain their original global refusal, never gain acceptance.
            if record["error"] is None:raise CustodyFailure("UNREPORTED_SOURCE_DRIFT")
            calls.append(record);continue
        request=record["request"];store=request.get("store")
        if store is not None and store!=str(root/"stores"/slot):raise CustodyFailure("STORE_REFERENCE")
        if record["facts"] is not None:
            if store is not None and record.get("store_after_audit") is not None:
                if inventory(store,work=work)!=record["store_after_audit"]:raise CustodyFailure("RETAINED_STORE_CHANGED")
            call_work={};work.setdefault("call_audits",[]).append({"slot":slot,"work":call_work})
            again=inspect(path,arm=BACKEND[record["arm"]],mode=record["mode"],request=request,
                sources=expected_sources,profile=manifest["profile"],deadline=manifest["deadline_monotonic"],work=call_work)
            if stable_facts(again)!=stable_facts(record["facts"]):raise CustodyFailure("RETAINED_FACTS_CHANGED")
            if store is not None and record.get("store_after_audit") is not None:
                if inventory(store,work=work)!=record["store_after_audit"]:raise CustodyFailure("ANALYSIS_CHANGED_STORE")
        calls.append(record)
    O.lineage(root,calls,copies)
    results=[];economic=[]
    generation={e["body"]["episode"]:e["body"]["result"] for e in events if e["kind"]=="GENERATION"}
    for episode in manifest["episodes"]:
        e=episode["episode"];group=[c for c in calls if c["slot"].startswith(f"e{e}--")]
        states=[v for k,v in ledger_slots.items() if k.startswith(f"e{e}--")]
        unavailable=any(v["state"]=="UNAVAILABLE" for v in states)
        failure=O.failure_at(manifest["abort"],e)
        known={};reason=None
        try:
            if e in generation and generation[e]["terminal"]=="GENERATED":known=R.episode(e,generation[e],group,work=work)
        except ControlFailure as exc:failure=True;reason=str(exc)
        missing=O.completion(e,ledger_slots,group,known);unavailable=unavailable or bool(missing)
        b=known.get("B",{})
        result=decide(unavailable=unavailable,selection=known.get("selection"),selected=known.get("selected",[]),
            semantic_keys=known.get("semantic_keys",{}),ocm_rows=b.get("OCM_ENABLED",{}).get("rows",[]),
            parent_rows=b.get("ADAPTIVE_PARENT",{}).get("rows",[]),
            knockout_rows=b.get("OCM_KNOCKOUT",{}).get("rows",[]),control_failure=failure)
        results.append({"episode":e,**result,"control_reason":reason,"unavailable_obligations":missing})
        economic.append({"episode":e,**evaluate(group,physical=None)})
    apparatus=overall(results)
    if manifest["abort"] is not None and manifest["abort"]["kind"]=="SEMANTIC_CONTROL_FAILED":
        apparatus["terminal"]="SEMANTIC_CONTROL_FAILED"
    return {"schema":"ocm.unary-retained-analysis.v1","apparatus":apparatus,
            "economics":economic,"physical_coordinator_observation":manifest["physical"],
            "global_failures":manifest["abort"],"analysis_work":work,
            "analysis_wall_s":time.monotonic()-start,"analysis_cpu_s":time.process_time()-cpu,
            "external_lifetime_closure":"UNQUALIFIED","scientific_execution":"NOT_AUTHORIZED_BY_THIS_INTERNAL_API"}



def analyze(root,*,expected_sources,work):
    if type(work) is not dict:raise TypeError("work must be a dict")
    start=time.monotonic();cpu=time.process_time()
    try:return _analyze(root,expected_sources=expected_sources,work=work)
    except Exception as exc:
        work["analysis_refusal"]=type(exc).__name__+":"+str(exc);raise
    finally:
        work["analysis_outer_wall_s"]=time.monotonic()-start
        work["analysis_outer_cpu_s"]=time.process_time()-cpu
