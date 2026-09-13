"""Conservative rational confidence radii; sampling assumptions are external."""
from fractions import Fraction as F
from functools import lru_cache


def require(ok, message):
    if not ok:
        raise ValueError(message)


def rational(v, positive=False):
    require(type(v) in (int, F), "exact rational required")
    require(0 <= v <= 1 and (not positive or v > 0), "probability range")
    return F(v)


def tail_upper(k, n, epsilon, terms=8):
    require(type(k) is int and k >= 1, "fixed nonempty alphabet required")
    require(type(n) is int and n >= 1, "positive visit index required")
    require(type(terms) is int and terms >= 3, "at least three Taylor terms")
    e = rational(epsilon)
    if k == 1 or e == 1:
        return F(0)
    x, term, lower_exp = 2*n*e*e, F(1), F(1)
    for j in range(1, terms+1):
        term *= x/j
        lower_exp += term
    return min(F(1), F(2**k-2)/lower_exp)


@lru_cache(None, typed=True)
def radius(k, n, alpha, weight, terms=8):
    require(type(k) is int and k >= 1, "fixed nonempty alphabet required")
    require(type(n) is int and n >= 0, "nonnegative visit index required")
    a, w = rational(alpha, True), rational(weight, True)
    require(a < 1, "alpha must be below one")
    require(type(terms) is int and terms >= 3, "at least three Taylor terms")
    if k == 1:
        return F(0)
    if not n:
        return F(1)
    target = a*w/(n*(n+1))
    low, high = 0, n
    while low < high:
        middle = (low+high)//2
        if tail_upper(k, n, F(middle, n), terms) <= target:
            high = middle
        else:
            low = middle+1
    return F(low, n)


def registered_radii(alphabets, counts, alpha, weights, terms=8):
    require(len(alphabets) == len(counts) == len(weights), "row dimensions")
    weights = tuple(rational(w, True) for w in weights)
    require(sum(weights) <= 1, "row error allocation exceeds one")
    rational(alpha, True)
    require(alpha < 1, "alpha must be below one")
    return tuple(radius(k, n, alpha, w, terms) for k, n, w in zip(alphabets, counts, weights))
