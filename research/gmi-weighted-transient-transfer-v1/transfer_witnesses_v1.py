"""Exact falsifying witnesses and no-alarm controls; no measured outcomes."""
from fractions import Fraction as F
from weighted_transfer_v1 import model, certificate, tails
from transfer_oracle_v1 import stationary, trees, execute, completed_cost, best_stationary

def pair(e, p, rescue=False, kappa=F(1)):
    b = (0,0,1,0) if rescue else (0,1-p,p,0)
    charges = ((1,), (kappa if rescue else 1,))
    nominal = model([[(0,0,1,0)], [b]], charges)
    truth = model([[(0,e,1-e,0)], [b]], charges)
    return nominal, truth

def proper_error(e=F(1,4)):
    nominal, truth = pair(e,e*e)
    q,p = (stationary(m,(0,0))["cost"][0] for m in (nominal,truth))
    if p-q != 1/e:
        raise AssertionError("analytic geometric cost disagreement")
    return dict(e=e, p=e*e, nominal_cost=q, true_cost=p, error=p-q)

def trap_and_rescue():
    q,p = pair(F(1,4), F(0))
    try:
        certificate([p],q,(1,1),F(3,4),1,(1,0,0,0))
    except ValueError:
        pass
    else:
        raise AssertionError("unseen absorbing trap accepted")
    qr,pr = pair(F(1,4), F(0), rescue=True,kappa=F(3))
    cert = certificate([pr],qr,(1,1),F(1,4),3,(1,0,0,0))
    got = stationary(pr,(0,0))
    if got["cost"][0] != F(7,4) or got["steps"][0] != F(5,4):
        raise AssertionError("charged rescue disagreement")
    return dict(trap_probability=F(1,4), trap_expected_unit_cost="infinite",
                trap_refused=True, rescue_cost=got["cost"][0],
                rescue_steps=got["steps"][0], rescue_certificate=cert)

def controlled_models():
    q = model([[(0,F(1,8),F(7,8),0),(F(1,4),0,F(3,4),0)],
               [(F(1,4),0,F(3,4),0),(0,F(1,4),F(3,4),0)]],
              [(1,2),(3,1)])
    p = model([[(0,F(1,4),F(3,4),0),(F(1,8),0,F(7,8),0)],
               [(F(1,2),0,F(1,2),0),(0,F(3,8),F(5,8),0)]],
              [(1,2),(4,1)])
    return q,p

def history_control():
    q,p = controlled_models()
    cert = certificate([p],q,(1,2),F(1,2),2,(1,0,0,0))
    count = 0
    maximum_error = F(0)
    for tree in trees(2,2,3):
        values = [completed_cost(m,tree,(0,1)) for m in (q,p)]
        delta = abs(values[1]-values[0])
        maximum_error = max(maximum_error,delta)
        if delta > cert["cost_error"]:
            raise AssertionError("history policy transfer failed")
        for m in (q,p):
            _, leaves = execute(m,tree)
            if sum(x*w for x,w in zip(leaves,(1,2))) > tails(cert,3)["alive_weight"]:
                raise AssertionError("weighted path tail failed")
        count += 1
    return dict(history_policies=count, exact_model_executions=2*count,
                maximum_error=maximum_error, certificate=cert)

def selected_policy_control():
    a = model([[(0,1,0),(F(1,2),F(1,2),0)]],[(1,1)])
    b = model([[(F(1,2),F(1,2),0),(0,1,0)]],[(1,1)])
    choices = []
    for nominal in (a,b):
        cert = certificate([a,b],nominal,(1,),F(1,2),1,(1,0,0))
        choice,cost = best_stationary(nominal)
        for truth in (a,b):
            true_selected = stationary(truth,choice)["cost"][0]
            _, comparator = best_stationary(truth)
            if true_selected > comparator + 2*cert["cost_error"]:
                raise AssertionError("data-selected comparator failed")
        choices.append(choice)
    if choices != [(0,),(1,)]:
        raise AssertionError("control never changes selected policy")
    paid = model([[(0,1,0),(0,1,0)]],[(0,1)])
    fees = {(0,):F(10),(1,):F(0)}
    choice,total = best_stationary(paid,fees)
    if choice != (1,) or total != 1:
        raise AssertionError("setup fee disappeared")
    return dict(selected_actions=[p[0] for p in choices], model_pairs=4,
                fee_aware_choice=choice[0], fee_aware_total=total)

def terminal_control():
    q = model([[(0,1,0)]],[(0,)])
    p = model([[(0,0,1)]],[(0,)])
    cert = certificate([p],q,(1,),0,0,(1,0,0))
    if cert["eta"] != 0 or cert["epsilon"] != 1 or cert["terminal_error"] != 1:
        raise AssertionError("terminal labels conflated")
    return dict(killed_error=cert["eta"], full_tv=cert["epsilon"],
                actual_success_difference=F(1))

def countable_control():
    # Finite arithmetic exemplifies the symbolic inequality in B3; no census
    # is claimed to verify every countable row or any physical row law.
    ratio = 1-F(1,2)/2+F(1,8)
    if ratio != F(7,8):
        raise AssertionError("countable geometric coefficient wrong")
    return dict(symbolic_worst_ratio=ratio, weight="2^n for n>=1; 0 at terminal",
                general_quantifiers="proved analytically, not enumerated")

def observation_control():
    terminal = (0,0,0,0,1,0)
    q = model([[(0,0,1,0,0,0)]]+[[terminal,terminal]]*3,
              [(1,),(0,10),(0,10),(0,10)])
    p = model([[(0,F(1,2),0,F(1,2),0,0)]]+[[terminal,terminal]]*3,
              [(1,),(0,10),(0,10),(0,10)])
    policy = (0,0,1,0)
    costs = [stationary(m,policy)["cost"][0] for m in (q,p)]
    cert = certificate([p],q,(2,1,1,1),F(1,2),10,(1,0,0,0,0,0))
    if costs != [11,1] or cert["epsilon"] != 1:
        raise AssertionError("revealed-charge signal not represented")
    if abs(costs[0]-costs[1]) > cert["cost_error"]:
        raise AssertionError("augmented observation no-alarm failed")
    return dict(costs=costs, omitted_signal_false_error=0,
                complete_signal_tv=cert["epsilon"],
                complete_signal_bound=cert["cost_error"])

def certification_control():
    loop = model([[(1,0,0)]],[(0,)])
    try:
        certificate([loop],loop,(1,),F(1,2),0,(1,0,0))
    except ValueError:
        pass
    else:
        raise AssertionError("coverage incorrectly implies certification")
    # The one possible dataset has coverage event E but not certification F.
    return dict(coverage_probability=F(1), certification_probability=F(0),
                covered_and_certified_probability=F(0), fallback_terminates=False)

def data_average_control():
    partials = [sum(F(1,2**n)*2**n for n in range(1,h+1)) for h in (1,2,8)]
    if partials != [1,2,8]:
        raise AssertionError("data-averaged integrability countermodel failed")
    return dict(data_law="Pr(D=n)=2^-n, n>=1",
                selected_cost="2^n", conditional_steps=1,
                expected_cost_partials=partials, expected_cost="infinite")
