"""Validated binomial counts and conservative paired-rate comparison.

Exact binomial tails and outward Clopper-Pearson bounds are combined by
Bonferroni without conditioning away discordance uncertainty. The inferential
contract requires IID paired observations; authored repeated suites remain
engineering/descriptive evidence. Historical statistics are not overwritten.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from math import isfinite
from math import comb


def binom_cdf(k: int, n: int, p: Fraction) -> Fraction:
    if type(k) is not int or type(n) is not int or n < 0 or not 0 <= p <= 1:
        raise ValueError("invalid binomial CDF inputs")
    return sum(Fraction(comb(n, i)) * p**i * (1 - p) ** (n - i) for i in range(0, min(k, n) + 1))


def exact_binomial_two_sided(k: int, n: int, p0: Fraction = Fraction(1, 2)) -> Fraction:
    """Two-sided exact binomial p-value (sum of probabilities ≤ observed)."""
    if type(k) is not int or type(n) is not int or not 0 <= k <= n or not 0 <= p0 <= 1:
        raise ValueError("invalid exact binomial inputs")
    if n == 0:
        return Fraction(1)
    probs = [Fraction(comb(n, i)) * p0**i * (1 - p0) ** (n - i) for i in range(n + 1)]
    obs = probs[k]
    return min(Fraction(1), sum(pr for pr in probs if pr <= obs))


def mcnemar_exact(b: int, c: int) -> dict:
    """b = pairs where arm A succeeds and B fails; c = the reverse.  Exact binomial on discordant pairs."""
    if any(type(x) is not int or x < 0 for x in (b, c)):
        raise ValueError("discordant counts must be non-negative integers")
    n = b + c
    p = exact_binomial_two_sided(min(b, c), n) if n else Fraction(1)
    return {"discordant": n, "a_only": b, "b_only": c, "p_two_sided": float(p), "direction": "A" if b > c else ("B" if c > b else "tie")}


@lru_cache(maxsize=4096)
def clopper_pearson(k: int, n: int, alpha: Fraction = Fraction(1, 20)) -> tuple[float, float]:
    """Exact CI for a rate by bisection on the binomial CDF (Fractions → floats at the end)."""
    if type(k) is not int or type(n) is not int or not 0 <= k <= n or not 0 < alpha < 1:
        raise ValueError("invalid binomial interval inputs")
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
        return lo if lower else hi  # outward bounds retain conservative coverage

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


    def __post_init__(self):
        values = (self.n, self.a_success, self.b_success, self.a_only, self.b_only)
        if any(type(x) is not int or x < 0 for x in values):
            raise ValueError("paired counts must be non-negative integers")
        both = self.a_success - self.a_only
        if (both < 0 or both != self.b_success - self.b_only
                or both + self.a_only + self.b_only > self.n):
            raise ValueError("inconsistent paired contingency table")


def paired(a, b) -> PairedComparison:
    a, b = tuple(a), tuple(b)
    if len(a) != len(b) or any(type(x) is not bool for x in a + b):
        raise ValueError("paired outcomes require equal lengths and explicit booleans")
    return PairedComparison(len(a), sum(a), sum(b),
                            sum(x and not y for x, y in zip(a, b)),
                            sum(y and not x for x, y in zip(a, b)))


def tost_equivalence(cmp: PairedComparison, delta: float = 0.05, alpha: float = 0.05) -> dict:
    """Conservative paired-rate inference via simultaneous binomial bounds.

    The two discordant categories have marginal Binomial(n, p) counts. Each
    Clopper-Pearson interval has confidence 1-alpha; Bonferroni gives joint
    confidence >=1-2*alpha without assuming independence. Subtraction bounds
    p(A-only)-p(B-only). Each directional bound fails with probability <=alpha.
    Unlike conditioning on the observed discordance count, this includes its
    sampling uncertainty, even when no discordance has been observed.
    Requires IID paired sampling; fixed authored suites are descriptive only.
    """
    if not isfinite(delta) or not 0 < delta < 1 or not isfinite(alpha) or not 0 < alpha < 0.5:
        raise ValueError("invalid equivalence margin or alpha")
    n = cmp.n
    if n == 0:
        return {"verdict": "CANNOT_CHECK", "reason": "no pairs"}
    a_lo, a_hi = clopper_pearson(cmp.a_only, n, Fraction(str(alpha)))
    b_lo, b_hi = clopper_pearson(cmp.b_only, n, Fraction(str(alpha)))
    d_lo, d_hi = a_lo - b_hi, a_hi - b_lo
    d = (cmp.a_only - cmp.b_only) / n
    if d_lo > delta:
        verdict = "RESIDUAL_A"
    elif d_hi < -delta:
        verdict = "RESIDUAL_B"
    elif -delta < d_lo and d_hi < delta:
        verdict = "EQUIVALENT"
    else:
        verdict = "INCONCLUSIVE"
    return {"verdict": verdict, "difference": round(d, 4),
            "ci_90": (d_lo, d_hi), "confidence": 1 - 2 * alpha, "delta": delta,
            "method": "BONFERRONI_CLOPPER_PEARSON_PAIRED_V2",
            "mcnemar": mcnemar_exact(cmp.a_only, cmp.b_only)}


def power_exact(n: int, true_diff: float, delta: float = 0.05, alpha: float = 0.05, disc_rate: float = 0.3) -> float:
    """Exact power of detecting RESIDUAL_A at margin δ for a given true paired difference, by
    enumerating discordant outcomes (discordant count fixed at round(disc_rate·n))."""
    if type(n) is not int or n < 0 or not isfinite(disc_rate) or not 0 < disc_rate <= 1 or not isfinite(true_diff):
        raise ValueError("invalid conditional power inputs")
    if n == 0:
        return 0.0
    disc = max(1, round(disc_rate * n))
    if abs(true_diff) > disc / n:
        raise ValueError("difference impossible at this fixed discordance count")
    p = Fraction(1, 2) + Fraction(true_diff * n / disc / 2).limit_denominator(1000)
    p = min(max(p, Fraction(0)), Fraction(1))
    power = Fraction(0)
    for a_only in range(disc + 1):
        pr = Fraction(comb(disc, a_only)) * p**a_only * (1 - p) ** (disc - a_only)
        cmp = PairedComparison(n, a_only, disc - a_only, a_only, disc - a_only)
        if tost_equivalence(cmp, delta, alpha)["verdict"] == "RESIDUAL_A":
            power += pr
    return float(power)


def mutant_p_greater_than_alpha_means_equivalent(cmp: PairedComparison, alpha: float = 0.05) -> str:
    """Planted (MEG-32 hostile): 'p > 0.05 ⇒ PARENT_SUFFICIENT'."""
    return "EQUIVALENT" if mcnemar_exact(cmp.a_only, cmp.b_only)["p_two_sided"] > alpha else "RESIDUAL"
