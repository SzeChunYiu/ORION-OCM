"""Complete finite-class population query procedure, not graph discovery."""
from fractions import Fraction as F
from itertools import combinations
from scm_v1 import model, complete_laws, necessity

def uniform_root_models(n):
    if type(n) is not int or n < 1:
        raise ValueError('positive integer root census required')
    # Stars and bars: every histogram on eight types, once.
    for bars in combinations(range(n+7), 7):
        cuts = (-1,) + bars + (n+7,)
        yield tuple(F(cuts[i+1]-cuts[i]-1, n) for i in range(8))

def solve_fiber(candidates, target_laws, target=necessity):
    """Caller warrants complete candidates, exact population laws, and total target."""
    candidates = tuple(candidates)
    if not candidates:
        raise ValueError('empty declared candidate class')
    if (len(target_laws) != 9 or any(len(p) != 4 or sum(p) != 1
            or any(type(x) not in (int, F) or not 0 <= x <= 1 for x in p)
            for p in target_laws)):
        raise ValueError('nine normalized exact joint intervention laws required')
    target_laws = tuple(tuple(p) for p in target_laws)
    compatible = []
    for candidate in candidates:
        candidate = model(candidate)
        if complete_laws(candidate) == target_laws:
            value = target(candidate)
            if type(value) not in (int, F):
                raise ValueError("target must return an exact rational")
            compatible.append((F(value), candidate))
    if not compatible:
        return {'status': 'INCOMPATIBLE', 'models': 0,
                'candidate_evaluations': len(candidates)}
    lo, low_model = min(compatible)
    hi, high_model = max(compatible)
    return {'status': 'IDENTIFIED' if lo == hi else 'PARTIALLY_IDENTIFIED',
            'models': len(compatible), 'lower': lo, 'upper': hi,
            'lower_model': low_model, 'upper_model': high_model,
            'candidate_evaluations': len(candidates)}
