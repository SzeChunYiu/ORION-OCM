from __future__ import annotations
from fractions import Fraction
from itertools import product
import json
from typing import Mapping, Sequence

CLAIM_CEILING="GMI_FINITE_HISTORY_SWITCHING_AND_HYSTERESIS_SELECTION_AT_REGISTERED_SCOPE"
class SwitchingError(ValueError): pass
def F(x): return x if isinstance(x,Fraction) else Fraction(x)

def validate(morphs:Sequence[str], base:Mapping[str,object], switch:Mapping[tuple[str,str],object]):
    if not morphs or len(set(morphs))!=len(morphs): raise SwitchingError("MALFORMED_MORPHOLOGIES")
    if set(base)!=set(morphs): raise SwitchingError("BASE_DOMAIN_MISMATCH")
    req={(h,m) for h in morphs for m in morphs}
    if set(switch)!=req: raise SwitchingError("SWITCH_DOMAIN_MISMATCH")
    if any(F(base[m])<0 for m in morphs): raise SwitchingError("NEGATIVE_BASE_COST")
    if any(F(switch[k])<0 for k in req): raise SwitchingError("NEGATIVE_SWITCH_COST")

def selection(morphs,base,switch,prev):
    validate(morphs,base,switch)
    if prev not in morphs: raise SwitchingError("UNKNOWN_PREVIOUS_MORPHOLOGY")
    vals={m:F(base[m])+F(switch[(prev,m)]) for m in morphs}
    best=min(vals.values())
    return tuple(sorted(m for m,v in vals.items() if v==best))

def history_dependent(morphs,base,switch):
    sels={h:selection(morphs,base,switch,h) for h in morphs}
    return len(set(sels.values()))>1, sels

def symmetric_two_switch(kappa):
    k=F(kappa)
    if k<0: raise SwitchingError("NEGATIVE_SWITCH_COST")
    return {("A","A"):F(0),("A","B"):k,("B","A"):k,("B","B"):F(0)}

def symmetric_expected(delta,kappa):
    d,k=F(delta),F(kappa)
    x=d+k
    sel_a=("B",) if x<0 else (("A","B") if x==0 else ("A",))
    y=d-k
    sel_b=("B",) if y<0 else (("A","B") if y==0 else ("A",))
    return (sel_a,sel_b)

def affine_thresholds(alpha,beta,kappa):
    a,b,k=F(alpha),F(beta),F(kappa)
    if b==0: raise SwitchingError("ZERO_AFFINE_SLOPE")
    if k<0: raise SwitchingError("NEGATIVE_SWITCH_COST")
    return tuple(sorted(((-k-a)/b,(k-a)/b)))

def origin_additive_switch(morphs,u,v):
    if set(u)!=set(morphs) or set(v)!=set(morphs): raise SwitchingError("ORIGIN_ADDITIVE_DOMAIN_MISMATCH")
    out={(h,m):F(u[h])+F(v[m]) for h in morphs for m in morphs}
    if any(x<0 for x in out.values()): raise SwitchingError("NEGATIVE_SWITCH_COST")
    return out

def origin_additive_invariant(morphs,base,u,v):
    sw=origin_additive_switch(morphs,u,v)
    dep,sels=history_dependent(morphs,base,sw)
    return (not dep),sels

def uniform_winner_margin(morphs,base,switch,winner):
    validate(morphs,base,switch)
    if winner not in morphs: return False
    for h in morphs:
        for n in morphs:
            if n==winner: continue
            lhs=F(base[n])-F(base[winner])
            rhs=F(switch[(h,winner)])-F(switch[(h,n)])
            if not lhs>rhs: return False
    return True

def reset_selection(morphs,base,switch,reset_to):
    validate(morphs,base,switch)
    if reset_to not in morphs: raise SwitchingError("UNKNOWN_RESET_TARGET")
    target=selection(morphs,base,switch,reset_to)
    return {h:target for h in morphs}

def finite_certificate():
    checks={}
    morphs=("A","B"); base={"A":F(0),"B":F(0)}; sw=symmetric_two_switch(1)
    dep,initial_sels=history_dependent(morphs,base,sw)
    checks["equal_cost_persistence_hostile"]=dep and initial_sels=={"A":("A",),"B":("B",)}

    symmetric_cases=0
    for k in range(3):
        sw=symmetric_two_switch(k)
        for d in range(-3,4):
            b={"A":F(3),"B":F(3+d)}
            got=(selection(morphs,b,sw,"A"),selection(morphs,b,sw,"B"))
            if got!=symmetric_expected(d,k):
                raise AssertionError((d,k,got,symmetric_expected(d,k)))
            symmetric_cases+=1
    checks["symmetric_hysteresis_census"]=symmetric_cases==21
    sw1=symmetric_two_switch(1)
    checks["boundary_ties_exact"]=(
        (selection(morphs,{"A":F(2),"B":F(1)},sw1,"A"),selection(morphs,{"A":F(2),"B":F(1)},sw1,"B")) == (("A","B"),("B",))
        and (selection(morphs,{"A":F(1),"B":F(2)},sw1,"A"),selection(morphs,{"A":F(1),"B":F(2)},sw1,"B")) == (("A",),("A","B"))
    )
    checks["affine_hysteresis_thresholds"]=affine_thresholds(-1,2,F("1/2"))==(F("1/4"),F("3/4"))

    ms=("A","B","C")
    origin_cases=0
    for bv in product(range(3),repeat=3):
        b=dict(zip(ms,map(F,bv),strict=True))
        for uv in product(range(2),repeat=3):
            u=dict(zip(ms,map(F,uv),strict=True))
            for vv in product(range(2),repeat=3):
                v=dict(zip(ms,map(F,vv),strict=True))
                inv,s=origin_additive_invariant(ms,b,u,v)
                if not inv: raise AssertionError(("origin additive history leak",b,u,v,s))
                origin_cases+=1
    checks["origin_additive_erasure_census"]=origin_cases==1728

    zero={h:F(0) for h in ms}
    inv,_=origin_additive_invariant(ms,{"A":F(0),"B":F(1),"C":F(2)},zero,zero)
    checks["zero_switching_special_case"]=inv

    margin_contexts=margin_certificates=0
    for bv in product(range(3),repeat=3):
        b=dict(zip(ms,map(F,bv),strict=True))
        for bits in product(range(2),repeat=9):
            sw={(h,m):F(bits[3*i+j]) for i,h in enumerate(ms) for j,m in enumerate(ms)}
            validate(ms,b,sw)
            margin_contexts+=1
            for w in ms:
                if uniform_winner_margin(ms,b,sw,w):
                    margin_certificates+=1
                    sels=[selection(ms,b,sw,h) for h in ms]
                    if any(s!=(w,) for s in sels):
                        raise AssertionError(("margin failed",b,sw,w,sels))
    checks["uniform_margin_implication_census"]=margin_contexts==13824 and margin_certificates>0

    r=reset_selection(ms,{"A":F(0),"B":F(2),"C":F(1)},
                      origin_additive_switch(ms,{"A":0,"B":1,"C":2},{"A":0,"B":1,"C":0}),"B")
    checks["reset_erases_history"]=len(set(r.values()))==1

    malformed=False
    try:
        symmetric_two_switch(-1)
    except SwitchingError:
        malformed=True
    checks["negative_switch_fails_closed"]=malformed

    if not all(checks.values()): raise AssertionError(checks)
    return {
      "schema":"GMI_833_HISTORY_SWITCHING_HYSTERESIS_RESULT_V1",
      "claim_ceiling":CLAIM_CEILING,
      "verdict":"GREEN",
      "checks":checks,
      "counts":{"symmetric_cases":symmetric_cases,"origin_additive_cases":origin_cases,
                "uniform_margin_contexts":margin_contexts,"uniform_margin_certificates":margin_certificates},
      "witnesses":{"equal_cost_selections":{k:list(v) for k,v in initial_sels.items()},
                   "affine_thresholds":["1/4","3/4"]},
      "forbidden_promotions":["STOCHASTIC_SWITCHING_CLOSED","ENDOGENOUS_SWITCH_COST_LEARNING_CLOSED",
        "GENERAL_NONMARKOV_HISTORY_CLOSED","REAL_WORLD_MIGRATION_CALIBRATED","UNIVERSAL_HYSTERESIS","COMPLETE_GMI"]
    }

def main(): print(json.dumps(finite_certificate(),sort_keys=True,separators=(",",":")))
if __name__=="__main__": main()
