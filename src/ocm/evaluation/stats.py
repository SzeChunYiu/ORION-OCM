"""Pre-registered statistics for M7 (adopt, do not invent — MEG-32): exact binomial test, exact
McNemar on discordant pairs, Clopper–Pearson interval, and TOST equivalence on a paired rate
difference using exact binomial bounds.  Pure stdlib, exact (no approximation) for the small n of
the protected suites.  A non-significant advantage is never superiority; equivalence is only
claimed when both one-sided tests reject at α.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb


def binom_cdf(k: int, n: int, p: Fraction) -> Fraction:
    return sum(Fraction(comb(n, i)) * p**i * (1 - p) ** (n - i) for i in range(0, k + 1))


def exact_binomial_two_sided(k: int, n: int, p0: Fraction = Fraction(1, 2)) -> Fraction:
    """Two-sided exact binomial p-value (sum of probabilities ≤ observed)."""
    if n == 0:
        return Fraction(1)
    probs = [Fraction(comb(n, i)) * p0**i * (1 - p0) ** (n - i) for i in range(n + 1)]
    obs = probs[k]
    return min(Fraction(1), sum(pr for pr in probs if pr <= obs))


def mcnemar_exact(b: int, c: int) -> dict:
    """b = pairs where arm A succeeds and B fails; c = the reverse.  Exact binomial on discordant pairs."""
    n = b + c
    p = exact_binomial_two_sided(min(b, c), n) if n else Fraction(1)
    return {"discordant": n, "a_only": b, "b_only": c, "p_two_sided": float(p), "direction": "A" if b > c else ("B" if c > b else "tie")}


def clopper_pearson(k: int, n: int, alpha: Fraction = Fraction(1, 20)) -> tuple[float, float]:
    """Exact CI for a rate by bisection on the binomial CDF (Fractions → floats at the end)."""
    if n == 0:
        return (0.0, 1.0)

    def solve(target_cdf: Fraction, kk: int, lower: bool) -> Fraction:
        lo, hi = Fraction(0), Fraction(1)
        for _ in range(40):
            mid = (lo + hi) / 2
            v = binom_cdf(kk, n, mid)
            if lower:
                if v > target_cdf:
                    lo = mid
                else:
                    hi = mid
            else:
                if v > target_cdf:
                    lo = mid
                else:
                    hi = mid
        return (lo + hi) / 2

    lo = Fraction(0) if k == 0 else solve(1 - alpha / 2, k - 1, True)
    hi = Fraction(1) if k == n else solve(alpha / 2, k, False)
    return (float(lo), float(hi))


@dataclass(frozen=True)
class PairedComparison:
    n: int
    a_success: int
    b_success: int
    a_only: int
    b_only: int


def tost_equivalence(cmp: PairedComparison, delta: float = 0.05, alpha: float = 0.05) -> dict:
    """Two one-sided tests on the paired rate difference d = (a_only − b_only)/n using the exact
    Clopper–Pearson interval of the discordant proportion: equivalent iff the (1−2α) CI of d lies
    within (−δ, δ).  Residual for A iff the lower bound of d exceeds δ; for B symmetric."""
    n = cmp.n
    disc = cmp.a_only + cmp.b_only
    if n == 0:
        return {"verdict": "CANNOT_CHECK", "reason": "no pairs"}
    if disc == 0:
        return {"verdict": "EQUIVALENT", "difference": 0.0, "ci_90": (0.0, 0.0), "delta": delta}
    lo_p, hi_p = clopper_pearson(cmp.a_only, disc, Fraction(int(2 * alpha * 100), 100))
    # difference in success rates = (a_only − b_only)/n = disc·(2p − 1)/n where p = a_only/disc
    d_lo = disc * (2 * lo_p - 1) / n
    d_hi = disc * (2 * hi_p - 1) / n
    d = (cmp.a_only - cmp.b_only) / n
    if d_lo > delta:
        verdict = "RESIDUAL_A"
    elif d_hi < -delta:
        verdict = "RESIDUAL_B"
    elif -delta < d_lo and d_hi < delta:
        verdict = "EQUIVALENT"
    else:
        verdict = "INCONCLUSIVE"
    return {"verdict": verdict, "difference": round(d, 4), "ci_90": (round(d_lo, 4), round(d_hi, 4)), "delta": delta, "mcnemar": mcnemar_exact(cmp.a_only, cmp.b_only)}


def power_exact(n: int, true_diff: float, delta: float = 0.05, alpha: float = 0.05, disc_rate: float = 0.3) -> float:
    """Exact power of detecting RESIDUAL_A at margin δ for a given true paired difference, by
    enumerating discordant outcomes (discordant count fixed at round(disc_rate·n))."""
    disc = max(1, round(disc_rate * n))
    p = Fraction(1, 2) + Fraction(true_diff * n / disc / 2).limit_denominator(1000)
    p = min(max(p, Fraction(0)), Fraction(1))
    power = Fraction(0)
    for a_only in range(disc + 1):
        pr = Fraction(comb(disc, a_only)) * p**a_only * (1 - p) ** (disc - a_only)
        lo_p, _ = clopper_pearson(a_only, disc, Fraction(int(2 * alpha * 100), 100))
        if disc * (2 * lo_p - 1) / n > delta:
            power += pr
    return float(power)


def mutant_p_greater_than_alpha_means_equivalent(cmp: PairedComparison, alpha: float = 0.05) -> str:
    """Planted (MEG-32 hostile): 'p > 0.05 ⇒ PARENT_SUFFICIENT'."""
    return "EQUIVALENT" if mcnemar_exact(cmp.a_only, cmp.b_only)["p_two_sided"] > alpha else "RESIDUAL"
