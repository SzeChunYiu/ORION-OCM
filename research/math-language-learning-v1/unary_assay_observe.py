"""Reset-aware observations: sum actual per-preparation totals, never row deltas."""
import math
import unary_method_plain as D

def add(target,source):
    if source is not None:
        for key,value in source.items():
            if type(value) is not int or value<0:raise ValueError("INVALID_OBSERVED_COUNTER")
            target[key]=target.get(key,0)+value

def capture(result,partial=None):
    known=result if result is not None else partial
    e={} if known is None else known.get("execution_observation") or {}
    prepared=bool(e.get("preparation_attempts"))
    out={"semantic":e.get("parent_semantic_total") if prepared else None,
         "binding":e.get("prepared_binding_total") if prepared else None,
         "preparations":e.get("preparations",0),"parent_completions":e.get("parent_completions",0),
         "index":e.get("index"),"matching":{},"partial_matching_attempts":0,
         "answer_check":None,"dispatches":None,"checks":None}
    for attempt in e.get("matching",[]):
        if attempt.get("counters") is None:out["partial_matching_attempts"]+=1
        else:add(out["matching"],attempt["counters"])
    if known is not None:
        out["dispatches"]=known.get("dispatches");out["checks"]=known.get("checks")
        if known.get("check") is not None:out["answer_check"]=known["check"].get("work")
    return D.parse(D.raw(out))

def aggregate(totals,item):
    c=item["call_totals"]
    for group in ("semantic","binding","index","matching","answer_check"):
        add(totals.setdefault(group,{}),c[group])
    for key,value in (item.get("store_work_delta") or {}).items():
        if type(value) is int:add(totals.setdefault("store",{}),{key:value})
        elif type(value) is float and key.endswith("_wall_s") and math.isfinite(value) and value>=0:
            spans=totals.setdefault("store_spans_s",{});spans[key]=spans.get(key,0.0)+value
        else:raise ValueError("INVALID_STORE_OBSERVATION")
    for key in ("preparations","parent_completions","partial_matching_attempts"):
        totals[key]=totals.get(key,0)+c[key]
    for key in ("dispatches","checks"):
        if c[key] is None:totals[key+"_unavailable_calls"]=totals.get(key+"_unavailable_calls",0)+1
        else:totals[key]=totals.get(key,0)+c[key]
    key="complete_calls" if item["terminal"]=="CHECKED" else "partial_calls"
    totals[key]=totals.get(key,0)+1
    add(totals.setdefault("input",{}),{k:v for k,v in item["parse"].items() if type(v) is int})

def store_work(runtime):
    store=getattr(runtime,"store",None)
    return None if store is None else dict(store.work)

def store_delta(before,after):
    if before is None or after is None:return None
    out={k:v-before.get(k,0) for k,v in after.items()}
    if any(v<0 for v in out.values()):raise ValueError("STORE_COUNTER_RESET")
    return out
