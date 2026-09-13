"""Finite exact target-total certificates; no implicit-set coverage inference."""
from selection_v1 import require,rational

def accounts(source,target,epsilon):
    require(bool(source) and bool(target), "nonempty allocation registers required")
    s={i:rational(x) for i,x in source.items()}
    t={i:rational(x) for i,x in target.items()}
    return s,t,rational(epsilon,True)

def construct_relation(source,target,epsilon=0):
    s,t,e=accounts(source,target,epsilon)
    relation=tuple((i,j) for i in s for j in t if s[i]<=t[j]+e)
    return relation,len(s)*len(t)

def certify(source,target,lower,epsilon,relation,candidates):
    s,t,e=accounts(source,target,epsilon)
    lower=rational(lower)
    require(lower<=min(s.values()), "source lower bound unsound")
    require(bool(candidates), "no target machine witness")
    pairs=tuple(relation)
    require(len(pairs)==len(set(pairs)), "duplicate relation pair")
    covered=set()
    for i,j in pairs:
        require(i in s and j in t, "unknown relation endpoint")
        require(s[i]<=t[j]+e, "account comparison false")
        covered.add(j)
    require(covered==set(t), "target coverage incomplete")
    machine_costs={}
    for machine,(allocation,cost) in candidates.items():
        require(allocation in t, "candidate allocation membership false")
        c=rational(cost)
        require(t[allocation]<=c, "target accounting unsound")
        machine_costs[machine]=c
    return dict(status="CERTIFIED",lower=lower-e,target_infimum=min(t.values()),
                candidate_costs=machine_costs,relation_checks=len(pairs),
                candidate_checks=len(candidates),covered_targets=len(covered))

def threshold_completion(passes,failures,unknown):
    require(all(type(n) is int and n>=0 for n in (passes,failures,unknown)),
            "invalid outcome count")
    n=passes+failures+unknown
    require(n>0, "empty registered cohort")
    low=3*passes>=2*n
    high=3*(passes+unknown)>=2*n
    return dict(status="GUARANTEED_FRACTION_PASS" if low else
                       "FRACTION_FAIL" if not high else "UNRESOLVED",
                total=n,minimum_passes=passes,maximum_passes=passes+unknown,
                minimum_fraction=rational(passes)/n,
                maximum_fraction=rational(passes+unknown)/n)
