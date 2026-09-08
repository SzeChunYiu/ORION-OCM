"""Registered horizon arithmetic; nested spans are never added to totals."""
import math
from unary_assay_phase import ARMS

def number(x):
    if type(x) not in (int,float) or not math.isfinite(x) or x<0:raise ValueError("UNAVAILABLE_COST")
    return float(x)

def measured(call):
    # The outer caller observes all launch/child-readback work before coordinator audit.
    if type(call) is not dict:raise ValueError("UNAVAILABLE_COST")
    facts=call.get("facts")
    if type(facts) is not dict or facts.get("terminal")!="CHECKED":raise ValueError("UNAVAILABLE_COST")
    p=facts["process"]
    return {"wall_s":number(call["launch_return_wall_s"]),
            "cpu_s":number(call["launch_return_own_cpu_s"])+number(p["waited_child_user_s"])+number(p["waited_child_system_s"])}

def horizon(a,b):
    start={"wall_s":0.0,"cpu_s":0.0} if a is None else measured(a)
    total=measured(b);rows=b["facts"]["rows"]
    increments=[{"wall_s":number(r["wall_s"])+number(r["sink_wall_s"]),
                 "cpu_s":number(r["cpu_s"])+number(r["sink_cpu_s"])} for r in rows]
    overhead={k:total[k]-sum(r[k] for r in increments) for k in total}
    if any(x<0 for x in overhead.values()):raise ValueError("COST_SPAN_CONTRADICTION")
    cumulative={k:start[k]+overhead[k] for k in total};prefix=[]
    for i,row in enumerate(increments):
        cumulative={k:cumulative[k]+row[k] for k in total}
        prefix.append({"presentation_count":i+1,**cumulative})
    return {"acquisition":start,"B_total":total,"B_nonrow_overhead":overhead,"allocated_prefix":prefix,"allocation":"B nonrow overhead frontloaded; not observed intermediate lifecycle costs",
            "complete_horizon":{k:start[k]+total[k] for k in total}}

def break_even(left,right,metric):
    n=len(left["allocated_prefix"])
    if n!=len(right["allocated_prefix"]):raise ValueError("HORIZON_MISMATCH")
    favorable=left["complete_horizon"][metric]<=right["complete_horizon"][metric]
    return {"metric":metric,"observed_presentation_count":n,"favorable_endpoint":favorable,
            "terminal":"OBSERVED_AT_HORIZON" if favorable else "ENDPOINT_NOT_BENEFICIAL",
            "earliest_crossing":"UNAVAILABLE","intermediate_prefix_crossing":"UNAVAILABLE"}

def evaluate(calls,*,physical,complete_cost_closure=False):
    out={"terminal":"ECONOMICS_CANNOT_CHECK","scope":"Actual A+B horizon; full outer closure separately required.",
         "arms":{},"physical":physical,"shared_comparative_allocation":"Equal four-arm allocation; OCM A counted once physically."}
    try:
        a={arm:next((c for c in calls if c["arm"]==arm and c["mode"]=="acquire_selected"),None) for arm in ARMS}
        b={arm:next((c for c in calls if c["arm"]==arm and "--B--" in c["slot"]),None) for arm in ARMS}
        for arm in ARMS:
            acquisition=a["OCM_ENABLED"] if arm=="OCM_KNOCKOUT" else a[arm]
            if arm!="EXACT_PARENT" and acquisition is None:raise ValueError("MISSING_ACQUISITION_COST")
            result=horizon(acquisition,b[arm]);result["A_allocation"]="COUNTERFACTUAL_REUSE" if arm=="OCM_KNOCKOUT" else "ACTUAL"
            other=[c for c in calls if c["arm"]==arm and c is not b[arm] and c["mode"]!="acquire_selected"]
            result["C_and_roles"]={k:sum(measured(c)[k] for c in other) for k in ("wall_s","cpu_s")}
            out["arms"][arm]=result
        out["crossings"]={parent:{metric:break_even(out["arms"]["OCM_ENABLED"],out["arms"][parent],metric)
                                   for metric in ("wall_s","cpu_s")} for parent in ("EXACT_PARENT","ADAPTIVE_PARENT")}
        physical_calls={k:sum(measured(c)[k] for c in calls) for k in ("wall_s","cpu_s")}
        out["physical_call_totals"]=physical_calls
        out["counterfactual_A_not_added_to_physical"]=True
        out["terminal"]="OBSERVED_COSTS" if complete_cost_closure else "ECONOMICS_CANNOT_CHECK"
        if not complete_cost_closure:out["reason"]="EXTERNAL_COMPLETE_LIFETIME_COST_NOT_SUPPLIED"
    except (ValueError,KeyError,TypeError) as exc:out["reason"]=str(exc)
    return out
