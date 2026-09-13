"""Exact finite model of CLB-1 transport, and of what does NOT transport.

CLB-1: if q_M is in the relaxed allocation set F and accounting is sound
(a(q_M) <= c(M)), then inf_F a <= c(M).  The argument is an order argument: it
uses neither cardinality, compactness, measurability nor computability.
"""
from fractions import Fraction

TERMINALS = ("TRANSPORTS", "NO_MEMBERSHIP", "UNSOUND_ACCOUNTING")


def require(cond, msg):
    if not cond:
        raise ValueError(msg)


def lower_bound(allocation_values):
    """inf over the relaxed allocation set, on an exact rational family."""
    require(allocation_values, "empty allocation set has no infimum here")
    for v in allocation_values:
        require(isinstance(v, Fraction), "allocation values must be exact")
    return min(allocation_values)


def transport(allocation_values, a_qM, c_M, membership=True):
    """Return the CLB-1 verdict plus the bound actually established."""
    require(isinstance(a_qM, Fraction) and isinstance(c_M, Fraction), "exact only")
    if not membership:
        return {"terminal": "NO_MEMBERSHIP", "bound": None}
    require(a_qM in allocation_values, "declared membership contradicted by the set")
    if a_qM > c_M:
        return {"terminal": "UNSOUND_ACCOUNTING", "bound": None}
    L = lower_bound(allocation_values)
    require(L <= a_qM <= c_M, "order chain broken")
    return {"terminal": "TRANSPORTS", "bound": L}


def exclusion_is_determined(L, costs):
    """A shared lower bound never orders two machines.

    Returns True only if L alone fixes which machine is cheaper, which it
    cannot do whenever both exceed L.
    """
    require(all(isinstance(c, Fraction) for c in costs), "exact only")
    strictly_above = [c for c in costs if c > L]
    return len(strictly_above) <= 1
