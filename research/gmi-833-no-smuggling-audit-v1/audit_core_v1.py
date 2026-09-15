from __future__ import annotations
from fractions import Fraction
import re
from typing import Any

CLEAN = "CLEAN_AT_REGISTERED_AUDIT_SCOPE"

def F(x): return x if isinstance(x, Fraction) else Fraction(str(x))
def missing(x): return {"terminal": f"CANNOT_AUDIT_{x}", "findings": []}

def norm(s: str):
    if not isinstance(s,str) or not s: raise ValueError("identifier must be nonempty")
    s=re.sub(r"([a-z0-9])([A-Z])",r"\1 \2",s); s=re.sub(r"([A-Z]+)([A-Z][a-z])",r"\1 \2",s)
    t=tuple(x for x in re.split(r"[^A-Za-z0-9]+",s.lower()) if x)
    return "".join(t)

def lexical(record):
    ids=record.get("search_visible_identifiers"); d=record.get("denylist")
    if ids is None: return missing("SEARCH_VISIBLE_IDENTIFIERS")
    if not isinstance(d,dict) or not d.get("version") or d.get("entries") is None: return missing("DENYLIST")
    deny=[(x,norm(x)) for x in d["entries"]]; finds=[]
    for i in ids:
        n=norm(i)
        finds += [{"identifier":i,"deny_entry":raw} for raw,b in deny if b in n]
    return {"terminal":"LEXICAL_LEAKAGE" if finds else CLEAN,"denylist_version":d["version"],"findings":finds}

SIG={"arity","types","state_access","locality","addressability","content_dependent_routing","parameter_sharing","recurrence","stochasticity","verifier_access","resource_class"}
def semantic(record):
    ps=record.get("primitives"); fps=record.get("target_fingerprints")
    if ps is None: return missing("PRIMITIVES")
    if fps is None: return missing("TARGET_FINGERPRINTS")
    finds=[]; bad=[]
    for p in ps:
        pid=p.get("id"); f=p.get("features")
        if not pid or not isinstance(f,dict): bad.append(pid or "<missing-id>"); continue
        m=sorted(SIG-set(f))
        if m: bad.append({"id":pid,"missing":m}); continue
        for fp in fps:
            req=fp.get("required_features")
            if not fp.get("name") or not isinstance(req,dict) or not req: raise ValueError("bad fingerprint")
            if all(f.get(k,object()) in v if isinstance(v,list) else f.get(k,object())==v for k,v in req.items()):
                finds.append({"primitive":pid,"fingerprint":fp["name"]})
    if bad: return {"terminal":"CANNOT_AUDIT_PRIMITIVE_SIGNATURES","findings":bad}
    return {"terminal":"SEMANTIC_MACRO_LEAKAGE" if finds else CLEAN,"findings":finds}

def cost(record):
    c=record.get("cost")
    if c is None: return missing("COST_MODEL")
    coords=c.get("coordinates"); cs=c.get("candidates"); ss=c.get("scalarizations")
    if not coords or cs is None or not ss: return missing("COST_DISCLOSURE")
    coords=tuple(coords); finds=[]; ids=[]
    if len(set(coords))!=len(coords): raise ValueError("duplicate cost coordinate")
    for x in cs:
        cid=x.get("id"); r=x.get("resources")
        if not cid or not isinstance(r,dict): return missing("CANDIDATE_RESOURCE_VECTOR")
        ids.append(cid); ex=sorted(set(r)-set(coords)); mi=sorted(set(coords)-set(r))
        if ex or mi: finds.append({"kind":"MALFORMED_RESOURCE_VECTOR","candidate":cid,"extras":ex,"missing":mi}); continue
        neg=[k for k in coords if F(r[k])<0]
        if neg: finds.append({"kind":"NEGATIVE_RESOURCE_COORDINATE","candidate":cid,"coordinates":neg})
    if len(set(ids))!=len(ids): finds.append({"kind":"DUPLICATE_CANDIDATE_ID"})
    winners=[]
    for s in ss:
        name=s.get("name"); w=s.get("weights")
        if not name or not isinstance(w,dict): return missing("SCALARIZATION")
        if set(w)!=set(coords): finds.append({"kind":"UNDECLARED_OR_MISSING_SCALAR_COORDINATE","scalarization":name}); continue
        if any(F(w[k])<=0 for k in coords): finds.append({"kind":"NONPOSITIVE_SCALAR_WEIGHT","scalarization":name}); continue
        rows=sorted((sum(F(x["resources"][k])*F(w[k]) for k in coords),x["id"]) for x in cs)
        lo=rows[0][0]; winners.append((name,tuple(cid for val,cid in rows if val==lo)))
    for cid,d in c.get("target_adjustments",{}).items():
        if F(d)!=0: finds.append({"kind":"TARGET_DEPENDENT_ADJUSTMENT","candidate":cid,"delta":F(d)})
    z=tuple(sorted(x.get("operator") for x in c.get("operator_costs",[]) if x.get("target_privileged") and F(x.get("cost",0))==0))
    if z: finds.append({"kind":"ZERO_COST_PRIVILEGED_OPERATOR","operators":z})
    rev=len({w for _,w in winners})>1
    if rev: finds.append({"kind":"SCALARIZATION_WINNER_REVERSAL","winners":tuple(winners)})
    if rev and c.get("claim_mode")=="UNIVERSAL_WINNER": finds.append({"kind":"UNIVERSAL_WINNER_UNSUPPORTED"})
    return {"terminal":"COST_PRIOR_SENSITIVE" if finds else CLEAN,"findings":finds,"winner_reversal":rev,"winners":tuple(winners)}

def search(record):
    s=record.get("search")
    req=("candidates","budget","strategies","tie_rule","pruning_rule","stopping_rule","randomness","seeds")
    if s is None or any(k not in s for k in req): return missing("SEARCH_DISCLOSURE")
    rows=s["candidates"]; vals={x["id"]:F(x["objective"]) for x in rows}
    if len(vals)!=len(rows): raise ValueError("duplicate search id")
    b=int(s["budget"])
    if b<1: raise ValueError("budget")
    wins=[]
    for st in s["strategies"]:
        order=tuple(st.get("order",())); name=st.get("name")
        if not name: return missing("SEARCH_STRATEGY")
        seen=order[:b]
        if any(x not in vals for x in seen): raise ValueError("unknown search candidate")
        win=min(seen,key=lambda x:(vals[x],seen.index(x))) if seen else None; wins.append((name,win))
    sensitive=len({x for _,x in wins})>1 and not (s.get("exhaustive_certificate") and b>=len(vals))
    return {"terminal":"SEARCH_PRIOR_SENSITIVE" if sensitive else CLEAN,"findings":[{"kind":"ORDER_OR_TRAJECTORY_DEPENDENT_WINNER","winners":tuple(wins)}] if sensitive else [],"winners":tuple(wins)}

def evaluation(record):
    e=record.get("evaluation"); req=("uses_architecture_ids_in_score","thresholds_frozen_pre_outcome","posthoc_classifier_feeds_score","metric_rankings","claim_mode")
    if e is None or any(k not in e for k in req): return missing("EVALUATION_DISCLOSURE")
    f=[]
    if e["uses_architecture_ids_in_score"]: f.append({"kind":"ARCHITECTURE_ID_IN_SCORE"})
    if F(e.get("target_id_bonus",0))!=0: f.append({"kind":"TARGET_ID_BONUS","bonus":F(e["target_id_bonus"])})
    if not e["thresholds_frozen_pre_outcome"]: f.append({"kind":"POST_OUTCOME_THRESHOLD"})
    if e["posthoc_classifier_feeds_score"]: f.append({"kind":"POSTHOC_CLASSIFIER_FEEDBACK"})
    wins=tuple((k,v[0] if v else None) for k,v in sorted(e["metric_rankings"].items())); rev=len({x for _,x in wins if x is not None})>1
    if rev and e["claim_mode"]=="UNIVERSAL_RANKING": f.append({"kind":"METRIC_WINNER_REVERSAL","winners":wins})
    return {"terminal":"EVALUATION_PRIOR_SENSITIVE" if f else CLEAN,"findings":f,"winner_reversal":rev,"winners":wins}

def ecology(record):
    e=record.get("ecology"); req=("frame_status","sample_ids","matched_negative_registered","inclusion_rule","exclusion_rule","claim_requires_representativeness")
    if e is None or any(k not in e for k in req): return missing("ECOLOGY_DISCLOSURE")
    if e["frame_status"]=="UNKNOWN_FRAME":
        return {"terminal":"CANNOT_AUDIT_FRAME_REPRESENTATIVENESS" if e["claim_requires_representativeness"] else CLEAN,"findings":[{"kind":"UNKNOWN_FRAME"}] if e["claim_requires_representativeness"] else [],"frame_prevalence":None,"sample_prevalence":None}
    if e["frame_status"]!="KNOWN": return missing("FRAME_STATUS")
    frame=e.get("frame")
    if frame is None: return missing("SAMPLING_FRAME")
    by={x["id"]:x for x in frame}; sample=[by[i] for i in e["sample_ids"]]
    if len(by)!=len(frame): raise ValueError("duplicate ecology id")
    def p(xs): return Fraction(sum(bool(x.get("target_favoring")) for x in xs),len(xs)) if xs else Fraction(0)
    pf,ps=p(frame),p(sample); f=[]
    if 0<pf<1 and sample and ps in (0,1): f.append({"kind":"ONE_SIDED_SAMPLE_FROM_MIXED_FRAME"})
    if e["claim_requires_representativeness"] and not e["matched_negative_registered"]: f.append({"kind":"MISSING_MATCHED_NEGATIVE"})
    if e["claim_requires_representativeness"] and ps!=pf: f.append({"kind":"SAMPLE_FRAME_PREVALENCE_MISMATCH","frame":pf,"sample":ps})
    return {"terminal":"ECOLOGY_SELECTION_BIAS" if f else CLEAN,"findings":f,"frame_prevalence":pf,"sample_prevalence":ps}

def audit(record):
    sub={"lexical":lexical(record),"semantic":semantic(record),"cost":cost(record),"search":search(record),"evaluation":evaluation(record),"ecology":ecology(record)}
    return {"terminal":CLEAN if all(x["terminal"]==CLEAN for x in sub.values()) else "AUDIT_NOT_CLEAN","subaudits":sub,"terminals":tuple(x["terminal"] for x in sub.values())}
