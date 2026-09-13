"""Exact interval consequences of supplied cost contracts; no native-cost estimator."""

from fractions import Fraction as F

LEFT = "LEFT_CERTIFIED_STRICTLY_LOWER"
RIGHT = "RIGHT_CERTIFIED_STRICTLY_LOWER"
TIE = "EXACT_TIE"
UNRESOLVED = "UNRESOLVED"


def dimension(n):
    if type(n) is not int or n < 1:
        raise ValueError("positive integer n required")
    return n


def interval(lo, hi):
    if not isinstance(lo, F) or lo < 0:
        raise ValueError("exact nonnegative lower bound required")
    if hi is not None and (not isinstance(hi, F) or hi < lo):
        raise ValueError("exact upper bound at least lower required")
    return lo, hi


def relation(a, b):
    """A strict claim requires a finite upper endpoint below the other lower."""
    al, au = interval(*a)
    bl, bu = interval(*b)
    if au is not None and au < bl:
        return LEFT
    if bu is not None and bu < al:
        return RIGHT
    if au == al == bl == bu:
        return TIE
    return UNRESOLVED


def costs(n, native_lower=F(0), native_upper=None, sweep=False):
    """Bounds must be supplied soundly in common additive units on every input."""
    dimension(n)
    lo, hi = interval(native_lower, native_upper)
    scale = 2**n if sweep else 1
    xor = F((3*n + 2)*scale)
    delegation = (F(6 + lo)*scale, None if hi is None else F(6 + hi)*scale)
    return (xor, xor), delegation


def exact_hypothesis(n, sweep=False):
    """Hypothesis N_n=2n+1 exactly, not a certified native operation count."""
    dimension(n)
    assumed = F(2*n + 1)
    return costs(n, assumed, assumed, sweep)


def counted_expression(n):
    """The authored n loads +(n-1) additions +1 return equals2n."""
    dimension(n)
    return n + (n - 1) + 1


def written_net_lower(n, sweep=False):
    """Only the named template, under its supplied Python-event formula."""
    dimension(n)
    scale = 2**n if sweep else 1
    return F((11*n + 6)*scale), None
