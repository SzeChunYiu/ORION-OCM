"""Tian--Pearl (2000), equation25, with explicit feasible endpoint SCMs."""
from fractions import Fraction as F
from scm_v1 import probability, model

def validate_evidence(observed, q0, q1):
    p = tuple(probability(v) for v in observed)
    q0, q1 = probability(q0), probability(q1)
    if len(p) != 4 or sum(p) != 1:
        raise ValueError('four normalized observational cells required')
    a, b, c, d = p
    if not b <= q0 <= 1-a or not d <= q1 <= 1-c:
        raise ValueError('empty compatible response-model class')
    return p, q0, q1

def pn_bounds(observed, q0, q1):
    (a, b, c, d), q0, q1 = validate_evidence(observed, q0, q1)
    if not d:
        raise ValueError('undefined conditioning event X=1,Y=1')
    return max(F(0), (b+d-q0)/d), min(F(1), (1-q0-a)/d)

def endpoint_model(observed, q0, q1, pn):
    p, q0, q1 = validate_evidence(observed, q0, q1)
    lo, hi = pn_bounds(p, q0, q1)
    pn = probability(pn)
    if not lo <= pn <= hi:
        raise ValueError('PN outside compatible interval')
    a, b, c, d = p
    # X=0 table: row margin Y0=1 is b; column margin Y1=1 is v.
    v = q1-d
    k = max(F(0), b+v-(a+b))
    x0 = (a-v+k, v-k, b-k, k)
    # X=1 table: column Y1=1 is d; row Y0=1 is q0-b.
    t = d*pn
    r = q0-b-d+t
    x1 = (c-r, t, r, d-t)
    return model(x0+x1)

def identified_or_bounds(observed, q0, q1):
    lo, hi = pn_bounds(observed, q0, q1)
    return {'status': 'IDENTIFIED' if lo == hi else 'PARTIALLY_IDENTIFIED',
            'lower': lo, 'upper': hi,
            'lower_model': endpoint_model(observed, q0, q1, lo),
            'upper_model': endpoint_model(observed, q0, q1, hi)}
