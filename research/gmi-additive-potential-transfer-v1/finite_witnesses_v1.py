"""Finite certificate no-alarm and independent value/path controls."""
from fractions import Fraction as F
from finite_model_v1 import model
from additive_certificate_v1 import certify
from transfer_oracle_v1 import stationary,trees,completed_cost,best_stationary

def controlled_models():
    q=model([[(0,F(1,8),F(7,8),0),(F(1,4),0,F(3,4),0)],
             [(F(1,4),0,F(3,4),0),(0,F(1,4),F(3,4),0)]],[(1,2),(3,1)])
    p=model([[(0,F(1,4),F(3,4),0),(F(1,8),0,F(7,8),0)],
             [(F(1,2),0,F(1,2),0),(0,F(3,8),F(5,8),0)]],[(1,2),(4,1)])
    return q,p

def embedded_wtt():
    q,p=controlled_models()
    args=dict(L=(2,4,0,0),V=(4,8,0,0),B=(3,6,0,0),
              r=((F(3,2),F(3,2)),(3,3)),initial=(1,0,0,0),
              A=(F(1,2),1,0,0),epsilon=((F(1,4),F(1,4)),)*2)
    return q,p,args

def history_control():
    q,p,args=embedded_wtt()
    cert=certify([p],q,**args)
    maximum=F(0)
    count=0
    for tree in trees(2,2,3):
        pair=[completed_cost(m,tree,(0,1)) for m in (q,p)]
        error=abs(pair[1]-pair[0])
        maximum=max(maximum,error)
        if error>cert["cost_error"] or max(pair)>cert["expected_cost"]:
            raise AssertionError("independent history value disagreement")
        count+=1
    return dict(certificate=cert,history_policies=count,model_executions=2*count,
                maximum_cost_error=maximum)

def selected_control():
    q=model([[(0,1,0),(F(1,2),F(1,2),0)]],[(1,1)])
    p=model([[(F(1,2),F(1,2),0),(0,1,0)]],[(1,1)])
    choices=[]
    for nominal in (q,p):
        cert=certify([q,p],nominal,(2,0,0),(2,0,0),(2,0,0),
                     ((1,1),),(1,0,0))
        selected,_=best_stationary(nominal)
        choices.append(selected[0])
        for truth in (q,p):
            actual=stationary(truth,selected)["cost"][0]
            _,best=best_stationary(truth)
            if actual>best+2*cert["cost_error"]:
                raise AssertionError("same-class data selection disagreement")
    paid=model([[(0,1,0),(0,1,0)]],[(0,1)])
    policy,total=best_stationary(paid,{(0,):F(10),(1,):F(0)})
    if choices!=[0,1] or policy!=(1,) or total!=1:
        raise AssertionError("policy choice or setup omitted")
    return dict(selected_actions=choices,truth_nominal_pairs=4,
                fee_aware_action=policy[0],fee_aware_cost=total)

def terminal_control():
    q=model([[(0,1,0)]],[(0,)])
    p=model([[(0,0,1)]],[(0,)])
    cert=certify([p],q,(1,0,0),(0,0,0),(0,0,0),((0,),),(1,0,0),
                 A=(1,0,0),epsilon=((1,),))
    absent=certify([p],q,(1,0,0),(0,0,0),(0,0,0),((0,),),(1,0,0))
    if cert["cost_error"]!=0 or cert["terminal_error"]!=1:
        raise AssertionError("terminal identity lost")
    if absent["terminal_error"] is not None:
        raise AssertionError("missing event certificate promoted")
    return dict(cost_error=0,actual_success_error=1,
                event_bound=cert["terminal_error"],without_A=absent["terminal_status"])
