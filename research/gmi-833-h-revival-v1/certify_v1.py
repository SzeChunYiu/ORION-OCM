"""Certified rational intervals for the Poisson deviance (FREEZE_V1.md
section 9). Stdlib only: fractions + decimal. No float enters any claim.

For rational mu > 0, ln(mu) is bracketed by two rationals obtained from the
correctly rounded 40-digit decimal logarithm widened by one unit in the last
place on each side. Sums of brackets are exact Fraction sums. A deviance
difference is a rational interval; a comparison is decided only when that
interval excludes zero.
"""
from decimal import Decimal, getcontext, ROUND_FLOOR, ROUND_CEILING
from fractions import Fraction as Q

PREC = 40
INF = "INF"


def _ctx():
    c = getcontext()
    if c.prec != PREC:
        c.prec = PREC
    return c


def ln_bracket(mu):
    """[lo, hi] rationals with lo <= ln(mu) <= hi, mu a positive Fraction."""
    mu = Q(mu)
    if mu <= 0:
        raise ValueError("ln_bracket needs mu > 0")
    _ctx()
    d = Decimal(mu.numerator) / Decimal(mu.denominator)
    # the quotient itself is correctly rounded to PREC digits; widen it first
    ulp_q = Decimal(1).scaleb(d.adjusted() - PREC + 1)
    lo_d = (d - ulp_q).ln()
    hi_d = (d + ulp_q).ln()
    ulp = Decimal(1).scaleb(min(lo_d.adjusted(), hi_d.adjusted()) - PREC + 1)
    lo = Q(lo_d - ulp)
    hi = Q(hi_d + ulp)
    return lo, hi


def bracket_contains_log(lo, hi, mu):
    """Self-check: exp(lo) <= mu <= exp(hi), using the correctly rounded
    decimal exponential widened by one ulp the other way."""
    _ctx()
    mu = Q(mu)
    elo = (Decimal(Q(lo).numerator) / Decimal(Q(lo).denominator)).exp()
    ehi = (Decimal(Q(hi).numerator) / Decimal(Q(hi).denominator)).exp()
    ulp_lo = Decimal(1).scaleb(elo.adjusted() - PREC + 1)
    ulp_hi = Decimal(1).scaleb(ehi.adjusted() - PREC + 1)
    return Q(elo - ulp_lo) <= mu and mu <= Q(ehi + ulp_hi)


def deviance_difference(ys, mu_a, mu_b):
    """Certified interval for D(mu_a) - D(mu_b) over the rows, or INF/-INF
    when exactly one arm is inadmissible (a non-positive mean on a row with
    y > 0, or a non-positive mean at all — the registered rule makes any
    mu <= 0 inadmissible).

    D_a - D_b = 2 * sum_i [ y_i (ln mu_b,i - ln mu_a,i) + (mu_a,i - mu_b,i) ]
    The y ln y terms cancel exactly and are never bracketed.
    """
    bad_a = any(Q(m) <= 0 for m in mu_a)
    bad_b = any(Q(m) <= 0 for m in mu_b)
    if bad_a and bad_b:
        return {"status": "BOTH_INADMISSIBLE"}
    if bad_a:
        return {"status": "DECIDED", "sign": +1, "reason": "A_INADMISSIBLE"}
    if bad_b:
        return {"status": "DECIDED", "sign": -1, "reason": "B_INADMISSIBLE"}
    lo = Q(0)
    hi = Q(0)
    lin = Q(0)
    for y, a, b in zip(ys, mu_a, mu_b):
        y = Q(y)
        a = Q(a)
        b = Q(b)
        lin += a - b
        if y == 0:
            continue
        la_lo, la_hi = ln_bracket(a)
        lb_lo, lb_hi = ln_bracket(b)
        # y * (ln b - ln a): lower uses lb_lo - la_hi, upper lb_hi - la_lo
        lo += y * (lb_lo - la_hi)
        hi += y * (lb_hi - la_lo)
    lo = 2 * (lo + lin)
    hi = 2 * (hi + lin)
    if hi < 0:
        sign = -1
        status = "DECIDED"
    elif lo > 0:
        sign = +1
        status = "DECIDED"
    else:
        sign = 0
        status = "UNDECIDED"
    return {"status": status, "sign": sign, "lo": str(lo), "hi": str(hi),
            "width": str(hi - lo), "rows": len(ys)}


def deviance_interval(ys, mu):
    """Certified interval for D(mu) - D_sat, i.e. the deviance itself, for
    reporting. INF if inadmissible. Uses y ln y brackets as well."""
    if any(Q(m) <= 0 for m in mu):
        return {"status": "INADMISSIBLE"}
    lo = Q(0)
    hi = Q(0)
    for y, m in zip(ys, mu):
        y = Q(y)
        m = Q(m)
        term_lin = m - y
        if y == 0:
            lo += term_lin
            hi += term_lin
            continue
        ly_lo, ly_hi = ln_bracket(y)
        lm_lo, lm_hi = ln_bracket(m)
        lo += y * (ly_lo - lm_hi) + term_lin
        hi += y * (ly_hi - lm_lo) + term_lin
    return {"status": "OK", "lo": str(2 * lo), "hi": str(2 * hi),
            "width": str(2 * (hi - lo)), "rows": len(ys)}


def nonpositive_count(mu):
    return sum(1 for m in mu if Q(m) <= 0)


if __name__ == "__main__":
    lo, hi = ln_bracket(Q(3, 2))
    print("ln(3/2) in", float(lo), float(hi), bracket_contains_log(lo, hi, Q(3, 2)))
    print(deviance_difference([1, 2, 0, 5], [Q(1), Q(2), Q(1, 2), Q(4)],
                              [Q(2), Q(2), Q(1, 2), Q(5)]))
    print(deviance_interval([1, 2, 0, 5], [Q(1), Q(2), Q(1, 2), Q(4)]))
