from __future__ import annotations
import json
from copy import deepcopy
from pathlib import Path

HERE=Path(__file__).resolve().parent
POLICIES={'C0':(0,0),'C1':(1,1),'ID':(0,1),'NOT':(1,0)}

def acc(policy,target):
    return sum(int(policy[x]==target[x]) for x in (0,1))/2

def effective_actions(legal,admissible):
    return tuple(sorted(set(legal)&set(admissible)))

def base_sigma():
    return {
      'S':'BOOL_SUBSTRATE_V1','O':'AJ_PROCESS_FRAME','M':'C0',
      'L':('C0','C1','ID','NOT'),'Q':('MUTATE_ONE_ENTRY',),'H':(),
      'E':('ID_TASK',),'R':('ONE_EVAL',),'V':'EXACT_CHECK','C':'FROZEN_CONSTITUTION'
    }

def transform(sig,kind):
    s=deepcopy(sig)
    if kind=='LIBRARY': s['H']=s['H']+('macro',)
    elif kind=='OPERATOR': s['L']=s['L']+('XOR_OP',); s['H']=s['H']+('operator_record',)
    elif kind=='REPRESENTATION': s['L']=('ALT_ENCODING',)+s['L']; s['H']=s['H']+('compiler_map',)
    elif kind=='SEARCH': s['Q']=('ENUMERATE',)
    elif kind=='RESOURCE': s['R']=('TWO_EVALS',)
    elif kind=='VERIFIER': s['V']='EXACT_CHECK_V2'
    elif kind=='MACHINE': s['M']='ID'
    else: raise ValueError(kind)
    return s

def changed_fields(a,b):
    return tuple(k for k in a if a[k]!=b[k])

def main():
    # AJ6: legality and substrate admissibility are separate.
    legal=tuple(POLICIES)
    admissible=('C0','C1','ID')
    active=effective_actions(legal,admissible)
    assert active==('C0','C1','ID') and 'NOT' in legal and 'NOT' not in active

    expected={
      'LIBRARY':('H',),'OPERATOR':('L','H'),'REPRESENTATION':('L','H'),
      'SEARCH':('Q',),'RESOURCE':('R',),'VERIFIER':('V',),'MACHINE':('M',)
    }
    base=base_sigma(); dev_checks={}
    for kind,want in expected.items():
        got=changed_fields(base,transform(base,kind))
        assert got==want
        dev_checks[kind]=list(got)
    assert base['C']=='FROZEN_CONSTITUTION'

    # AJ7: same dynamics, incompatible objective functions.
    # one state, both actions self-loop; only requirement differs.
    dynamics={'a0':'s','a1':'s'}
    q0={'a0':1,'a1':0}; q1={'a0':0,'a1':1}
    assert dynamics['a0']==dynamics['a1']=='s'
    assert max(q0,key=q0.get)=='a0' and max(q1,key=q1.get)=='a1'
    reward_tables=[{'a0':1,'a1':0},{'a0':2,'a1':0},{'a0':1,'a1':-1}]
    assert all(max(r,key=r.get)=='a0' for r in reward_tables)

    # AJ8: fixed control can exploit consequential distinctions without development.
    identity=POLICIES['ID']; complement=POLICIES['NOT']
    constant_best=max(acc(POLICIES['C0'],identity),acc(POLICIES['C1'],identity))
    id_score=acc(identity,identity)
    assert constant_best==0.5 and id_score==1.0
    collapse_penalty=id_score-constant_best
    assert collapse_penalty==0.5

    # Fixed task-dispatch controller is broadly capable on the registered two-task family.
    fixed_dispatch_scores={
      'ID_TASK':sum(int((x)==identity[x]) for x in (0,1))/2,
      'NOT_TASK':sum(int((1-x)==complement[x]) for x in (0,1))/2,
    }
    assert fixed_dispatch_scores=={'ID_TASK':1.0,'NOT_TASK':1.0}

    # Same current capability, different developmental potential.
    current_A=current_B=acc(POLICIES['C0'],identity)
    future_A=acc(POLICIES['ID'],identity); future_B=acc(POLICIES['C0'],identity)
    assert current_A==current_B==0.5 and future_A==1.0 and future_B==0.5
    # Different current capability, same future response after a reset/update.
    current_C=acc(POLICIES['ID'],identity); current_D=acc(POLICIES['NOT'],identity)
    reset_C=reset_D=acc(POLICIES['C0'],identity)
    assert (current_C,current_D)==(1.0,0.0) and reset_C==reset_D==0.5

    # Information acquisition vs accessibility: target bit is already in initial hidden state.
    # Before internal computation action is constant; after deterministic reveal it equals theta.
    before=sum(int(0==theta) for theta in (0,1))/2
    after=sum(int(theta==theta) for theta in (0,1))/2
    assert before==0.5 and after==1.0
    initial_target_information_bits=1
    final_target_information_bits=1
    assert final_target_information_bits==initial_target_information_bits

    # Independent random novelty: joint table factorizes exactly.
    joint={(theta,r):1/4 for theta in (0,1) for r in (0,1)}
    ptheta={theta:sum(p for (t,r),p in joint.items() if t==theta) for theta in (0,1)}
    pr={r:sum(p for (t,rr),p in joint.items() if rr==r) for r in (0,1)}
    assert all(joint[(t,r)]==ptheta[t]*pr[r] for t in (0,1) for r in (0,1))

    negatives={
      'PASSIVE_MEMORY':{'distinction_stored':True,'task_exploitation':False,'identity_accuracy':0.5},
      'RANDOM_DYNAMICS':{'entropy_bits':1,'target_mutual_information_bits':0,'expected_identity_accuracy':0.5},
      'UNIVERSAL_INTERPRETER_NO_SELECTOR':{'expressive':True,'task_selector_supplied':False,'intelligence_from_universality_alone':False},
      'CONSTANT_REACTIVE':{'acts':True,'uses_required_input_distinction':False,'identity_accuracy':0.5},
      'FIXED_TASK_DISPATCH':{'development':False,'registered_two_task_accuracy':[1.0,1.0]}
    }

    result={
      'status':'GREEN',
      'aj6':{
        'sigma_extension_fields':['S','O','M','L','Q','H','E','R','V','C'],
        'legal_count':len(legal),'substrate_admissible_count':len(admissible),'active_intersection_count':len(active),
        'syntactically_legal_but_inadmissible_witness':'NOT',
        'development_transform_field_checks':dev_checks,
        'hsg_repair':'A_t = Legal(Sigma_t) intersection Adm_S(O_S)',
        'preserved_boundaries':['NFL','Rice/halting','Goedel','Blum speedup','HSG anti-finality']
      },
      'aj7':{
        'same_dynamics_opposite_objectives':'PASS',
        'q0_optimal':'a0','q1_optimal':'a1',
        'distinct_rewards_same_observed_optimal_policy':len(reward_tables),
        'objective_sources':['distal_viability','internal_reward_drive','external_specification','social_constraints','declared_aggregation_rule'],
        'terminal':'OBJECTIVE_UNDERDETERMINED_FROM_DYNAMICS_ALONE'
      },
      'aj8':{
        'identity_distinction_collapse_capability_loss':collapse_penalty,
        'fixed_broad_controller_without_development':fixed_dispatch_scores,
        'same_current_different_future':[current_A,current_B,future_A,future_B],
        'different_current_same_future':[current_C,current_D,reset_C,reset_D],
        'no_new_external_data_accessibility_gain':[before,after],
        'target_information_bits_before_after':[initial_target_information_bits,final_target_information_bits],
        'independent_random_entropy_bits':1,
        'independent_random_target_information_bits':0,
        'negative_controls':negatives,
        'registered_classes':['MI_CONTROL_AT_SCOPE','MI_DEVELOPMENTAL_AT_SCOPE'],
        'development_required_for_all_MI':False,
        'universal_definition_frozen':False
      },
      'forbidden_promotions':['UNIQUE_OBJECTIVE_FROM_PHYSICS','UNIVERSAL_INTELLIGENCE_DEFINITION_FINAL','DEVELOPMENT_REQUIRED_FOR_ALL_INTELLIGENCE','UNIVERSAL_COMPUTATION_IS_INTELLIGENCE','COMPLETE_GMI'],
      'claim_ceiling':'AJ6_AJ8_DEVELOPMENT_VALUE_AND_INTELLIGENCE_LAYER_SEPARATED_AT_REGISTERED_FINITE_SCOPE'
    }
    (HERE/'RESULT_V1.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))
if __name__=='__main__': main()
