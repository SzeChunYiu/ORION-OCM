"""Independent integer row oracle versus surgical laws and sharp bounds."""
from collections import defaultdict
from fractions import Fraction as F
from math import comb
from scm_v1 import TYPES, INTERVENTIONS, complete_laws, evidence, necessity
from fiber_v1 import uniform_root_models, solve_fiber
from bounds_v1 import pn_bounds, endpoint_model

def expanded_oracle(weights, n):
    rows = [t for t, w in zip(TYPES, weights) for _ in range(int(w*n))]
    if len(rows) != n:
        raise RuntimeError('nonintegral uniform-root oracle input')
    laws = []
    for ix, iy in INTERVENTIONS:
        outcomes = []
        for row in rows:
            x = row[0] if ix is None else ix
            y = row[1+x] if iy is None else iy
            outcomes.append((x,y))
        laws.append(tuple(F(outcomes.count((x,y)), n) for x in (0,1) for y in (0,1)))
    factual_cases = [row for row in rows if row[0] == 1 and row[2] == 1]
    pn = (F(sum(row[1] == 0 for row in factual_cases), len(factual_cases))
          if factual_cases else None)
    return tuple(laws), pn

def census(max_n=6):
    records = []
    for n in range(1,max_n+1):
        models = tuple(uniform_root_models(n))
        if len(models) != comb(n+7,7) or len(set(models)) != len(models):
            raise RuntimeError('incomplete or repeated class enumeration')
        groups = defaultdict(list)
        for weights in models:
            laws, pn = expanded_oracle(weights,n)
            if laws != complete_laws(weights):
                raise RuntimeError('independent intervention disagreement')
            if pn is not None:
                if necessity(weights) != pn:
                    raise RuntimeError('independent counterfactual disagreement')
                groups[evidence(weights)].append((pn,weights))
        ambiguous = supported_ambiguous = 0
        for (p,q0,q1), members in groups.items():
            lo, hi = pn_bounds(p,q0,q1)
            if (lo,hi) != (min(x[0] for x in members),max(x[0] for x in members)):
                raise RuntimeError('sharp bounds differ from exhaustive fiber')
            for pn in (lo,(lo+hi)/2,hi):
                w = endpoint_model(p,q0,q1,pn)
                if evidence(w)!=(p,q0,q1) or necessity(w)!=pn:
                    raise RuntimeError('constructive attainment failed')
            ambiguous += lo < hi
            supported_ambiguous += lo < hi and sum(p[:2]) > 0 and sum(p[2:]) > 0
        records.append({'n':n,'models':len(models),'defined_fibers':len(groups),
                        'ambiguous_fibers':ambiguous,
                        'treatment_supported_ambiguous_fibers':supported_ambiguous,
                        'joint_law_comparisons':9*len(models),
                        'constructive_attainment_checks':3*len(groups)})
    return records
