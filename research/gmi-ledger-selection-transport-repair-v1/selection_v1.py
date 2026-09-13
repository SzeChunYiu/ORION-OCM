"""Exact applicability, adequate-table selection and strict ordinal descent."""
from fractions import Fraction as F

def require(ok, message):
    if not ok:
        raise ValueError(message)

def rational(x, nonnegative=False):
    require(type(x) in (int, F), "exact rational required")
    value=F(x)
    require(not nonnegative or value>=0, "negative charge/likelihood")
    return value

def posterior(prior, likelihood):
    p=tuple(rational(x, True) for x in prior)
    l=tuple(rational(x, True) for x in likelihood)
    require(bool(p) and len(p)==len(l) and sum(p)==1, "invalid prior dimensions")
    z=sum(x*y for x,y in zip(p,l))
    if not z:
        return dict(status="UNDEFINED_ZERO_NORMALIZER", posterior=None, normalizer=z)
    return dict(status="DEFINED", posterior=tuple(x*y/z for x,y in zip(p,l)), normalizer=z)

def entropy_update_from_factors(prior, factors):
    """factors are supplied exact exp(-eta*g); no rational logarithm claim."""
    p=tuple(rational(x, True) for x in prior)
    f=tuple(rational(x, True) for x in factors)
    require(bool(p) and len(p)==len(f) and sum(p)==1, "invalid entropy inputs")
    require(all(x>0 for x in p+f), "positive interior factors required")
    masses=[p[i]*f[i] for i in range(len(p))]
    total=sum(masses)
    return tuple(m/total for m in masses)

def select_tables(task, tables, costs, setup=0, check_fee=0, visit_fee=0):
    """A table is the executable; no claims about arbitrary external programs."""
    require(bool(task), "empty task")
    require(all(bool(outputs) for outputs in task.values()), "empty adequate output set")
    require(set(costs)==set(tables), "cost coverage")
    fees=[rational(x,True) for x in (setup,check_fee,visit_fee)]
    charges={i:rational(c,True) for i,c in costs.items()}
    checks=0
    adequate=[]
    for name,table in tables.items():
        require(set(table)==set(task), "table must be total on exact task domain")
        good=True
        for x in task:
            checks+=1
            good=(table[x] in task[x]) and good
        if good:
            adequate.append(name)
    shared=fees[0]+checks*fees[1]+len(adequate)*fees[2]
    if not adequate:
        return dict(status="NO_ADEQUATE_REGISTERED_TABLE",winners=(),
                    checks=checks,cost_visits=0,shared_charge=shared,total=None)
    best=None;winners=[]
    for i in adequate:
        c=charges[i]
        if best is None or c<best:
            best=c;winners=[i]
        elif c==best:
            winners.append(i)
    winners=tuple(winners)
    return dict(status="SELECTED" if len(winners)==1 else "TIED",
                winners=winners,checks=checks,cost_visits=len(adequate),
                shared_charge=shared,total=shared+best)

def graph_contract(values, edges, adequate):
    n=len(values)
    require(n>0 and len(edges)==n, "finite nonempty graph required")
    vals=tuple(rational(x) for x in values)
    require(set(adequate)<=set(range(n)), "unknown adequate state")
    graph=[]
    for row in edges:
        require(len(row)==len(set(row)), "duplicate graph edge")
        require(all(type(j) is int and 0<=j<n for j in row), "unknown edge endpoint")
        graph.append(tuple(row))
    return vals,tuple(graph),frozenset(adequate)

def certify_descent(values, edges, adequate):
    vals,graph,good=graph_contract(values,edges,adequate)
    lower=tuple(tuple(vals[j]<vals[i] for j in row) for i,row in enumerate(graph))
    minima=tuple(i for i,row in enumerate(lower) if not any(row))
    bad=tuple(i for i in minima if i not in good)
    return dict(status="CERTIFIED" if not bad else "INADEQUATE_LOCAL_MINIMUM",
                local_minima=minima,bad_minima=bad,objective_reads=len(vals),
                adequacy_checks=len(vals),edge_comparisons=sum(map(len,graph)),
                maximum_moves=len(vals)-1)

def descend(values, edges, start):
    vals,graph,_=graph_contract(values,edges,())
    require(type(start) is int and 0<=start<len(vals), "unknown start")
    path=[start]; comparisons=0
    while True:
        i=path[-1]
        comparisons+=len(graph[i])
        lower=[j for j in graph[i] if vals[j]<vals[i]]
        if not lower:
            return dict(path=tuple(path),terminal=i,edge_comparisons=comparisons,
                        moves=len(path)-1)
        path.append(min(lower))

def euclidean_box_step(theta,gradient,eta,lower,upper):
    """One-dimensional supplied O0 rule with a nonempty closed interval."""
    x,g,e,lo,hi=map(rational,(theta,gradient,eta,lower,upper))
    require(e>0 and lo<=hi, "positive step and nonempty closed interval required")
    return max(lo,min(hi,x-e*g))
