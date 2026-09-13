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


# --- TL-6: when exclusions DO transport -------------------------------------
# Reuses the registered DCR criterion verbatim: separation is certified iff the
# candidate's upper bound is finite and strictly below the comparator's lower
# bound.  TL-3's negative is the degenerate case where the upper bound is None.

EXCLUSION_TERMINALS = ("CERTIFIED_STRICTLY_LOWER", "UNVERIFIABLE")


def exclusion_transports(candidate, comparator):
    """candidate/comparator are (lower, upper); upper may be None for unbounded."""
    for b in (candidate, comparator):
        require(isinstance(b, tuple) and len(b) == 2, "bounds must be (lower, upper)")
        lo, hi = b
        require(isinstance(lo, Fraction), "lower bound must be exact")
        require(hi is None or isinstance(hi, Fraction), "upper must be exact or None")
        require(lo >= 0 and (hi is None or hi >= lo), "invalid nonnegative interval")
    ca_hi = candidate[1]
    cb_lo = comparator[0]
    if ca_hi is not None and ca_hi < cb_lo:
        return "CERTIFIED_STRICTLY_LOWER"
    return "UNVERIFIABLE"


# --- TL-7: the exact trichotomy, and the mirror direction TL-6 omitted -------

def realizable_orders(a, b):
    """Which strict orders some consistent completion can realise.

    a, b are (lower, upper) with upper None meaning unbounded above.
    Returns (can_a_lt_b, can_a_gt_b, can_equal).
    """
    for x in (a, b):
        require(isinstance(x, tuple) and len(x) == 2, "bounds must be (lower, upper)")
        lo, hi = x
        require(isinstance(lo, Fraction), "lower bound must be exact")
        require(hi is None or isinstance(hi, Fraction), "upper must be exact or None")
        require(lo >= 0 and (hi is None or hi >= lo), "invalid nonnegative interval")
    a_lo, a_hi = a
    b_lo, b_hi = b
    can_lt = True if b_hi is None else a_lo < b_hi
    can_gt = True if a_hi is None else a_hi > b_lo
    lo_max = max(a_lo, b_lo)
    if a_hi is None and b_hi is None:
        hi_min = None
    elif a_hi is None:
        hi_min = b_hi
    elif b_hi is None:
        hi_min = a_hi
    else:
        hi_min = min(a_hi, b_hi)
    can_eq = True if hi_min is None else lo_max <= hi_min
    return can_lt, can_gt, can_eq


def compare(candidate, comparator):
    """Complete comparison: both directions, with UNVERIFIABLE otherwise.

    TL-6 implemented only the candidate direction; the mirror certificate
    (comparator upper strictly below candidate lower) is equally valid.

    Validation mirrors `exclusion_transports`.  An earlier version omitted it
    and certified empty intervals: compare((2,1),(3,4)) returned
    CERTIFIED_STRICTLY_LOWER although the candidate interval is empty, and a
    negative lower bound was accepted.  Raised by the ledger repair unit.
    """
    for b in (candidate, comparator):
        require(isinstance(b, tuple) and len(b) == 2, "bounds must be (lower, upper)")
        lo, hi = b
        require(isinstance(lo, Fraction), "lower bound must be exact")
        require(hi is None or isinstance(hi, Fraction), "upper must be exact or None")
        require(lo >= 0 and (hi is None or hi >= lo), "invalid nonnegative interval")
    a_hi = candidate[1]
    b_hi = comparator[1]
    if a_hi is not None and a_hi < comparator[0]:
        return "CERTIFIED_STRICTLY_LOWER"
    if b_hi is not None and b_hi < candidate[0]:
        return "CERTIFIED_STRICTLY_HIGHER"
    return "UNVERIFIABLE"


COMPARE_TERMINALS = ("CERTIFIED_STRICTLY_LOWER", "CERTIFIED_STRICTLY_HIGHER",
                     "UNVERIFIABLE")
