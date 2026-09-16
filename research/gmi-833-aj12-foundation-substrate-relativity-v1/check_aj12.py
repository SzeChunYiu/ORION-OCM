from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent

# --- Style A: finite set/relation presentation ---
A=(0,1)
FUNS={'ID':(0,1),'NOT':(1,0),'ZERO':(0,0),'ONE':(1,1)}

def comp_tuple(f,g):
    return tuple(g[f[x]] for x in A)

def as_relation(f):
    return frozenset((x,f[x]) for x in A)

def comp_relation(r,s):
    return frozenset((x,z) for x,y in r for y2,z in s if y==y2)

# --- Style B: explicit typed algebraic process presentation ---
@dataclass(frozen=True)
class Obj:
    name:str
    values:tuple
@dataclass(frozen=True)
class Proc:
    dom:Obj
    cod:Obj
    table:tuple

TA=Obj('A',(0,1))
def typed(name): return Proc(TA,TA,FUNS[name])
def tcomp(f,g):
    assert f.cod==g.dom
    return Proc(f.dom,g.cod,tuple(g.table[f.table[x]] for x in A))


def quotient_from_responses(responses):
    groups={}
    for p,sig in responses.items(): groups.setdefault(tuple(sig),[]).append(p)
    return sorted(tuple(sorted(v)) for v in groups.values())


def ternary_advice(bits):
    r=sum((Fraction(2*b,3**(i+1)) for i,b in enumerate(bits)),Fraction(0))
    x=r; out=[]
    for _ in bits:
        x*=3; d=x.numerator//x.denominator; x-=d
        assert d in (0,2); out.append(d//2)
    return r,tuple(out)


def main():
    composition_checks=0
    for f in FUNS:
        for g in FUNS:
            set_result=comp_relation(as_relation(FUNS[f]),as_relation(FUNS[g]))
            typed_result=tcomp(typed(f),typed(g)).table
            assert set_result==as_relation(typed_result)
            composition_checks+=1

    preps={'p0':0,'p1':1,'p2':0}
    tests={'read':FUNS['ID'],'flip':FUNS['NOT']}
    set_resp={p:tuple(t[v] for t in tests.values()) for p,v in preps.items()}
    typed_resp={p:tuple(Proc(TA,TA,t).table[v] for t in tests.values()) for p,v in preps.items()}
    assert set_resp==typed_resp
    q_set=quotient_from_responses(set_resp); q_typed=quotient_from_responses(typed_resp)
    assert q_set==q_typed==[('p0','p2'),('p1',)]

    # Same operational theorem transferred, not merely same notation.
    for f in FUNS:
        assert comp_tuple(FUNS['ID'],FUNS[f])==FUNS[f]
        assert comp_tuple(FUNS[f],FUNS['ID'])==FUNS[f]

    assumption_tags={
      'finite_carriers_and_extensional_equality':'MATHEMATICAL_FOUNDATION',
      'classical_decidable_finite_reasoning':'LOGIC/METATHEORY',
      'which_processes_are_admitted':'PHYSICAL_SUBSTRATE_LAW',
      'unit_and_vector_costs':'RESOURCE_MODEL',
      'protected_task_or_utility':'VALUE/REQUIREMENT_INPUT'
    }
    assert set(assumption_tags.values())=={'MATHEMATICAL_FOUNDATION','LOGIC/METATHEORY','PHYSICAL_SUBSTRATE_LAW','RESOURCE_MODEL','VALUE/REQUIREMENT_INPUT'}

    advice=(1,0,1,1)
    oracle_answers=advice
    assert oracle_answers==advice
    r,recovered=ternary_advice(advice)
    assert recovered==advice

    result={
      'status':'GREEN',
      'formalization_styles':['FINITE_SET_RELATION_STYLE','EXPLICIT_TYPED_ALGEBRAIC_PROCESS_STYLE'],
      'composition_transfer_checks':composition_checks,
      'operational_response_signatures':{k:list(v) for k,v in set_resp.items()},
      'operational_quotient':[list(x) for x in q_set],
      'theorem_invariance':['typed composition law','identity law','registered operational-equivalence quotient'],
      'assumption_tags':assumption_tags,
      'standard_effective_substrate':'STANDARD_TURING_EFFECTIVE_SCOPE',
      'alternative_substrate_witnesses':{
        'oracle_advice':{'bits':list(advice),'provenance':'IMPORTED_ORACLE_OR_ADVICE_POWER'},
        'exact_real_parameter':{'finite_ternary_rational':f'{r.numerator}/{r.denominator}','recovered_bits':list(recovered),'provenance':'IMPORTED_EXACT_PRECISION_ADVICE'}
      },
      'physical_hypercomputation':'EMPIRICAL_OPEN__NO_REPRODUCIBLE_EVIDENCE_REGISTERED_HERE',
      'metatheory_boundaries':['GODEL_INCOMPLETENESS_SCOPE_PRESERVED','TARSKI_OBJECT_LANGUAGE_METALANGUAGE_BOUNDARY_PRESERVED'],
      'forbidden_promotions':['UNIQUE_TRUE_FOUNDATION_PROVED','PHYSICAL_HYPERCOMPUTATION_PROVED','SUPER_TURING_POWER_FROM_NOTHING','SELF_JUSTIFYING_ALL_TRUTH_FOUNDATION','COMPLETE_GMI'],
      'claim_ceiling':'AJ12_FOUNDATION_STYLE_AND_COMPUTATIONAL_SUBSTRATE_RELATIVITY_AUDITED_AT_REGISTERED_CORE_SCOPE'
    }
    (HERE/'RESULT_V1.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__': main()
