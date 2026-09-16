from __future__ import annotations
import argparse, itertools, json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Dict, FrozenSet, Iterable, Tuple

HERE=Path(__file__).resolve().parent
CLAIM="GMI_AF5_VERIFICATION_CONTRACT_DISPLACEMENT_AND_RESOURCE_SELECTION_AT_REGISTERED_FINITE_SCOPE"
ATOMS=frozenset({"SOUND_ACCEPT","SOUND_REJECT","TERMINATES","COMPLETE_AT_REGISTERED_SCOPE","CERTIFICATE_CHECKED","BOUND_EXPLICIT","EPS_DELTA_EXPLICIT","ABSTENTION_EXPLICIT"})
FORBIDDEN={"RICE_THEOREM_FALSE","UNRESTRICTED_SEMANTIC_VERIFICATION_SOLVED","SOUND_AND_COMPLETE_AUTOMATIC_VERIFICATION_UNIVERSAL","FALSE_ALARM_IS_BUG","BOUNDED_NO_BUG_IS_UNBOUNDED_PROOF","PROPERTY_TEST_IS_EXACT_DECIDER","CERTIFICATE_CONSTRUCTION_FREE","CEGAR_ALWAYS_TERMINATES","UNIVERSAL_VERIFICATION_MORPHOLOGY","COMPLETE_GMI"}
STATUS_POINTS={
 "UNRESTRICTED_UNDECIDABLE":frozenset(),
 "DECIDABLE_RESTRICTED_FRAGMENT":frozenset({"SOUND_ACCEPT","SOUND_REJECT","TERMINATES","COMPLETE_AT_REGISTERED_SCOPE"}),
 "SEMI_DECISION_BUG_WITNESS":frozenset({"SOUND_REJECT"}),
 "CERTIFIABLE":frozenset({"SOUND_ACCEPT","TERMINATES","CERTIFICATE_CHECKED"}),
 "SOUND_INCOMPLETE_APPROXIMATION":frozenset({"SOUND_ACCEPT","TERMINATES"}),
 "CEGAR_REFINED_CERTIFIABLE":frozenset({"SOUND_ACCEPT","TERMINATES","CERTIFICATE_CHECKED"}),
 "BOUNDED_MODEL_CHECKED":frozenset({"SOUND_REJECT","TERMINATES","BOUND_EXPLICIT"}),
 "PROBABILISTIC_PROPERTY_TEST":frozenset({"TERMINATES","EPS_DELTA_EXPLICIT"}),
 "UNKNOWN_ABSTAIN":frozenset({"TERMINATES","ABSTENTION_EXPLICIT"}),
}

def require(c,m):
    if not c: raise ValueError(m)
def lattice_meet(a:FrozenSet[str],b:FrozenSet[str]):return a&b
def lattice_join(a:FrozenSet[str],b:FrozenSet[str]):return a|b
def validate_status_points():
    require(set(STATUS_POINTS.values()) <= {frozenset(x) for r in range(len(ATOMS)+1) for x in itertools.combinations(ATOMS,r)},"STATUS_OUTSIDE_POWERSET")

@dataclass(frozen=True)
class System:
    states:Tuple[str,...]; init:str; edges:Tuple[Tuple[str,str],...]; bad:str

def reachable(sys:System,bound:int|None=None)->Tuple[str,...]:
    seen={sys.init}; frontier=[(sys.init,0)]
    while frontier:
        s,d=frontier.pop(0)
        if bound is not None and d>=bound: continue
        for a,b in sys.edges:
            if a==s and b not in seen: seen.add(b);frontier.append((b,d+1))
    return tuple(sorted(seen))
def exact_safety(sys:System)->dict:
    r=reachable(sys);return {"status":"REJECT_UNSAFE" if sys.bad in r else "ACCEPT_SAFE","reachable":list(r),"verification_status":"DECIDABLE_RESTRICTED_FRAGMENT","resource":{"state_visits":len(r),"edge_checks":len(sys.edges)}}
def validate_certificate(sys:System,cert:Iterable[str])->dict:
    c=frozenset(cert);require(sys.init in c,"CERT_MISSING_INITIAL");require(sys.bad not in c,"CERT_CONTAINS_BAD");checks=0
    for a,b in sys.edges:
        if a in c:checks+=1;require(b in c,"CERT_NOT_INDUCTIVE")
    return {"status":"CERTIFICATE_VALID","certificate":sorted(c),"proof_construct_cost":len(c),"proof_check_cost":1+len(c)+checks,"verification_status":"CERTIFIABLE"}
def abstract_system(sys:System,amap:Dict[str,str])->dict:
    require(set(amap)==set(sys.states),"ABSTRACTION_NOT_TOTAL");ainit=amap[sys.init];abad=amap[sys.bad];aedges=sorted({(amap[a],amap[b]) for a,b in sys.edges});astates=tuple(sorted(set(amap.values())));ar=reachable(System(astates,ainit,tuple(aedges),abad))
    if abad in ar:return {"status":"UNKNOWN_FALSE_ALARM_POSSIBLE","abstract_reachable":list(ar),"verification_status":"UNKNOWN_ABSTAIN","sound":True,"complete":False}
    return {"status":"PROVED_SAFE_BY_SOUND_ABSTRACTION","abstract_reachable":list(ar),"verification_status":"SOUND_INCOMPLETE_APPROXIMATION","sound":True,"complete":False}
def cegar_safe_fixture(sys:System,coarse:Dict[str,str])->dict:
    first=abstract_system(sys,coarse);require(first['status']=='UNKNOWN_FALSE_ALARM_POSSIBLE','CEGAR_FIXTURE_NOT_SPURIOUS');concrete=exact_safety(sys);require(concrete['status']=='ACCEPT_SAFE','CEGAR_SPURIOUS_CHECK_FOUND_REAL_BUG');second=abstract_system(sys,{s:s for s in sys.states});require(second['status']=='PROVED_SAFE_BY_SOUND_ABSTRACTION','CEGAR_REFINEMENT_FAILED');cert=validate_certificate(sys,reachable(sys));return {"status":"CEGAR_REFINED_CERTIFIABLE","refinements":1,"spurious_counterexamples":1,"failed_refinement_cost":1,"final":second,"certificate_check":cert,"universal_termination_claim":False}
def bmc(sys:System,k:int)->dict:
    require(k>=0,"NEGATIVE_BOUND");r=reachable(sys,bound=k);bad=sys.bad in r;return {"status":"BUG_WITNESS_WITHIN_BOUND" if bad else "NO_BUG_FOUND_WITHIN_BOUND","bound":k,"bad_reached":bad,"verification_status":"BOUNDED_MODEL_CHECKED","unbounded_safety_proved":False}
def property_test_detection_probability(bits:Tuple[int,...],sample_size:int)->Fraction:
    require(len(bits)==8 and sum(bits)==4,"PROPERTY_TEST_FROZEN_PROMISE");combos=list(itertools.combinations(range(8),sample_size));return Fraction(sum(any(bits[i] for i in c) for c in combos),len(combos))
def property_test(bits:Tuple[int,...],sample_size:int)->dict:
    p=property_test_detection_probability(bits,sample_size);return {"status":"PROBABILISTIC_REJECT_FAR_OBJECT","sample_size":sample_size,"epsilon":"1/2","delta":f"{p.denominator-p.numerator}/{p.denominator}","exact_reject_probability":f"{p.numerator}/{p.denominator}","verification_status":"PROBABILISTIC_PROPERTY_TEST","exact_decider":False}
def semidecision(sys:System)->dict:
    if sys.bad in reachable(sys):return {"status":"BUG_WITNESS_FOUND","verification_status":"SEMI_DECISION_BUG_WITNESS","safe_proved":False}
    return {"status":"UNKNOWN_MAY_NOT_TERMINATE_IN_UNRESTRICTED_PARENT","verification_status":"UNKNOWN_ABSTAIN","safe_proved":False}
def selection(weight:Fraction)->dict:
    direct=(3,8,0,0);cert=(5,0,5,1);cd=Fraction(direct[0])+weight*sum(direct[1:]);cc=Fraction(cert[0])+weight*sum(cert[1:]);best=[]
    if cd<=cc:best.append('DIRECT_REPLAY')
    if cc<=cd:best.append('CERTIFICATE_EMITTER')
    return {"verification_weight":f"{weight.numerator}/{weight.denominator}","direct_cost":f"{cd.numerator}/{cd.denominator}","certificate_cost":f"{cc.numerator}/{cc.denominator}","argmin":best,"raw":{"DIRECT_REPLAY":direct,"CERTIFICATE_EMITTER":cert}}
def validate_terminal(t):require(t not in FORBIDDEN,f"FORBIDDEN_PROMOTION:{t}")
def certificate()->dict:
    validate_status_points();safe=System(('bad','s0','s1','s2'),'s0',(('s0','s1'),('s1','s2')),'bad');bug4=System(('bad','s0','s1','s2','s3'),'s0',(('s0','s1'),('s1','s2'),('s2','s3'),('s3','bad')),'bad');exact=exact_safety(safe);cert=validate_certificate(safe,('s0','s1','s2'));coarse={'s0':'A','s1':'B','s2':'C','bad':'C'};fine={s:s for s in safe.states};a0=abstract_system(safe,coarse);a1=abstract_system(safe,fine);cg=cegar_safe_fixture(safe,coarse);b3=bmc(bug4,3);b4=bmc(bug4,4);pt=property_test((1,1,1,1,0,0,0,0),3);ss=semidecision(safe);su=semidecision(bug4);sel=[selection(Fraction(1,10)),selection(Fraction(1)),selection(Fraction(2))];require([x['argmin'] for x in sel]==[['DIRECT_REPLAY'],['DIRECT_REPLAY','CERTIFICATE_EMITTER'],['CERTIFICATE_EMITTER']],"SELECTION_CROSSOVER_DRIFT")
    return {"status":"GREEN","parent_no_go":{"ownership":"PARENT_OWNED_NOT_PROVED_BY_EXECUTOR","reading":"no automatic terminating correct decider for every nontrivial unrestricted semantic program property at the classical parent scope"},"guarantee_lattice":{"atoms":sorted(ATOMS),"formal_lattice":"POWERSET_ORDERED_BY_SUBSET","named_points":{k:sorted(v) for k,v in STATUS_POINTS.items()},"total_ranking":False},"finite_exact":exact,"certificate":cert,"abstract_coarse":a0,"abstract_fine":a1,"cegar":cg,"bounded":{"k3":b3,"k4":b4},"property_test":pt,"semidecision":{"safe":ss,"unsafe":su},"verification_selection":sel,"tradeoff_statement":"soundness/completeness/termination/output scope remain explicit; UNKNOWN is not SAFE and approximate/bounded are not exact universal decision","evidence_role":"FINITE_CONTRACT_DISPLACEMENT_AND_RESOURCE_MICROSCOPE_NOT_UNRESTRICTED_VERIFICATION_PROOF","hostiles_required":16,"forbidden_promotions":sorted(FORBIDDEN),"claim_ceiling":CLAIM}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',default=str(HERE/'RESULT_V1.json'));a=ap.parse_args();r=certificate();Path(a.output).write_text(json.dumps(r,sort_keys=True,separators=(',',':'))+'\n');print(json.dumps(r,sort_keys=True))
if __name__=='__main__':main()
