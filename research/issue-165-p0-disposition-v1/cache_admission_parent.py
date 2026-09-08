"""Exact linear cache-admission / ski-rental parent; no ML.

Donors (already named in research/metareasoning-parent-review-v1):

- Karlin, Manasse, Rudolph, Sleator — competitive snoopy caching / ski rental
- Lotker, Patt-Shamir, Rawitz — rent, lease or buy / multislope ski rental
- Young-style cache admission as one-shot rent-versus-buy on a retained object

This capsule does not copy PR154/158/161/163 sources. It closes the named
G4.3 cache-admission parent that those PRs left implicit: on a linear
rent/hit/buy instance the parent is exact; on a nonlinear lifetime curve
the same parent must be labeled ADAPT and does not import its competitive
guarantee. That is the qualification the metareasoning review asked for.

No production change. No learned router.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Mapping


FractionLike = int | Fraction


def _q(value: FractionLike) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


@dataclass(frozen=True)
class LinearCache:
    """One retained object: uncached request costs `rent`, admission costs `buy`,
    a cached request costs `hit`. Require rent > hit >= 0 and buy >= 0."""

    rent: Fraction
    buy: Fraction
    hit: Fraction

    def __post_init__(self) -> None:
        object.__setattr__(self, "rent", _q(self.rent))
        object.__setattr__(self, "buy", _q(self.buy))
        object.__setattr__(self, "hit", _q(self.hit))
        if self.hit < 0 or self.buy < 0 or self.rent <= self.hit:
            raise ValueError("require rent > hit >= 0 and buy >= 0")

    @property
    def savings(self) -> Fraction:
        return self.rent - self.hit


def expected_uses(horizon: int, density: FractionLike) -> Fraction:
    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    rho = _q(density)
    if rho < 0 or rho > 1:
        raise ValueError("density must lie in [0, 1]")
    return rho * horizon


def known_horizon_admit(
    cache: LinearCache, horizon: int, density: FractionLike = 1
) -> bool:
    """Clairvoyant one-shot admission: admit iff expected remaining uses * savings > buy.

    A tie keeps the incumbent uncached (rent) arm. This is the exact known-H
    rent-versus-buy rule, not a learned predictor.
    """
    return expected_uses(horizon, density) * cache.savings > cache.buy


def clairvoyant_cost(cache: LinearCache, horizon: int) -> Fraction:
    """Known-H optimum among {never admit, admit from request 1}."""
    uncached = cache.rent * horizon
    admitted = cache.buy + cache.hit * horizon
    return min(uncached, admitted)


def deterministic_buy_request(cache: LinearCache) -> int:
    """Karlin-style deterministic ski-rental buy request (1-indexed).

    Admit on the first request t with t * savings >= buy. If savings does not
    repay buy on any finite t, return 0 as a sentinel meaning never admit.
    """
    if cache.savings == 0:
        return 0
    t = (cache.buy + cache.savings - 1) // cache.savings
    return int(t) if t > 0 else 1


def online_deterministic_cost(cache: LinearCache, horizon: int) -> Fraction:
    """Pay rent until the deterministic buy request, then buy and pay hit."""
    if horizon <= 0:
        return Fraction(0)
    t = deterministic_buy_request(cache)
    if t == 0 or horizon < t:
        return cache.rent * horizon
    rented = t - 1
    remaining = horizon - t + 1
    return cache.rent * rented + cache.buy + cache.hit * remaining


def competitive_ratio(cache: LinearCache, horizon: int) -> Fraction:
    opt = clairvoyant_cost(cache, horizon)
    online = online_deterministic_cost(cache, horizon)
    if opt == 0:
        return Fraction(0) if online == 0 else Fraction("inf")
    return online / opt


def max_competitive_ratio(cache: LinearCache, h_max: int) -> Fraction:
    worst = Fraction(0)
    for horizon in range(1, h_max + 1):
        ratio = competitive_ratio(cache, horizon)
        if ratio > worst:
            worst = ratio
    return worst


def cache_admission_equals_ski_rental(cache: LinearCache, horizon: int) -> bool:
    """One-shot cache admission is ski rental with net rent = savings, buy = buy."""
    ski = LinearCache(rent=cache.savings, buy=cache.buy, hit=Fraction(0))
    admit = known_horizon_admit(cache, horizon, density=1)
    ski_buy = known_horizon_admit(ski, horizon, density=1)
    return admit == ski_buy


def density_break_even_horizon(cache: LinearCache, density: FractionLike) -> int | None:
    """Smallest H with known_horizon_admit, or None if density is zero."""
    rho = _q(density)
    if rho == 0 or cache.savings == 0:
        return None
    needed = cache.buy / (rho * cache.savings)
    h = int(needed) if needed == int(needed) else int(needed) + 1
    if h <= 0:
        h = 1
    if not known_horizon_admit(cache, h, rho):
        h += 1
    return h


def is_affine_lifetime(costs: Mapping[int, FractionLike]) -> bool:
    """True iff the map H |-> cost(H) is exactly B + K*H on its integer domain."""
    if len(costs) < 2:
        return True
    hs = sorted(costs)
    k_hat = _q(costs[hs[1]]) - _q(costs[hs[0]])
    step = hs[1] - hs[0]
    if step <= 0 or k_hat % step != 0:
        slope = k_hat / step
    else:
        slope = k_hat / step
    intercept = _q(costs[hs[0]]) - slope * hs[0]
    return all(_q(costs[h]) == intercept + slope * h for h in hs)


def one_way_switch_cost(
    inverse: Mapping[int, FractionLike],
    semantic: Mapping[int, FractionLike],
    horizon: int,
    threshold: int,
) -> Fraction:
    """PR154-style one-way switch: inverse for 1..tau, then semantic for the rest.

    Cited, not copied: research/residual-strategy-regime-v1/ONLINE_SWITCH_THEOREM_V1.md
    on PR154. This helper only evaluates the same identity on a toy table.
    """
    if horizon <= 0:
        return Fraction(0)
    if threshold <= 0:
        return _q(semantic[horizon])
    if horizon <= threshold:
        return _q(inverse[horizon])
    return _q(inverse[threshold]) + _q(semantic[horizon - threshold])


def exact_minimax_threshold(
    inverse: Mapping[int, FractionLike],
    semantic: Mapping[int, FractionLike],
    h_max: int,
) -> tuple[int, Fraction]:
    """Argmin_tau max_H C_tau(H)/O(H) inside the deterministic one-way family."""

    def opt(h: int) -> Fraction:
        return min(_q(inverse[h]), _q(semantic[h]))

    best_tau = 0
    best_r = None
    for tau in range(0, h_max + 1):
        worst = Fraction(0)
        for h in range(1, h_max + 1):
            o = opt(h)
            c = one_way_switch_cost(inverse, semantic, h, tau)
            ratio = Fraction(0) if o == 0 and c == 0 else c / o
            if ratio > worst:
                worst = ratio
        if best_r is None or worst < best_r:
            best_r = worst
            best_tau = tau
    assert best_r is not None
    return best_tau, best_r


def forced_ski_rental_threshold(cache: LinearCache) -> int:
    """Classical buy request minus one: number of uncached requests before switch."""
    t = deterministic_buy_request(cache)
    if t == 0:
        return 10**9
    return t - 1


def nonlinear_adapt_witness() -> dict[str, object]:
    """Finite table where S(H) is not affine, so classical ski rental is ADAPT.

    Inverse is linear. Semantic is a convex frontier-style curve. The exact
    one-way minimax threshold therefore need not equal the Karlin buy-day of
    any linear (rent, buy, hit) fit to the first two semantic points.
    """
    inverse = {h: Fraction(10 * h) for h in range(1, 6)}
    semantic = {
        1: Fraction(22),
        2: Fraction(24),
        3: Fraction(27),
        4: Fraction(31),
        5: Fraction(36),
    }
    affine = is_affine_lifetime(semantic)
    tau_star, ratio_star = exact_minimax_threshold(inverse, semantic, 5)
    # Linear fit through S(1)=22, S(2)=24 => hit=2, buy=20. Not a faithful model.
    fitted = LinearCache(rent=Fraction(10), buy=Fraction(20), hit=Fraction(2))
    forced_tau = forced_ski_rental_threshold(fitted)
    forced_worst = Fraction(0)
    for h in range(1, 6):
        o = min(inverse[h], semantic[h])
        c = one_way_switch_cost(inverse, semantic, h, forced_tau)
        ratio = c / o
        if ratio > forced_worst:
            forced_worst = ratio
    return {
        "semantic_is_affine": affine,
        "exact_minimax_threshold": tau_star,
        "exact_minimax_ratio": str(ratio_star),
        "forced_linear_fit_buy": str(fitted.buy),
        "forced_linear_fit_hit": str(fitted.hit),
        "forced_ski_rental_threshold": forced_tau,
        "forced_ski_rental_ratio": str(forced_worst),
        "reduction": "ADAPT",
        "import_competitive_guarantee": False,
    }


def linear_qualification(h_max: int = 24) -> dict[str, object]:
    cache = LinearCache(rent=Fraction(10), buy=Fraction(30), hit=Fraction(1))
    densities = (Fraction(0), Fraction(1, 2), Fraction(1))
    density_rows = []
    for rho in densities:
        h_star = density_break_even_horizon(cache, rho)
        row = {
            "density": str(rho),
            "break_even_horizon": h_star,
            "admit_at_break_even": (
                None if h_star is None else known_horizon_admit(cache, h_star, rho)
            ),
            "admit_just_before": (
                False
                if h_star is None or h_star <= 1
                else known_horizon_admit(cache, h_star - 1, rho)
            ),
        }
        density_rows.append(row)
    worst = max_competitive_ratio(cache, h_max)
    equalities = all(
        cache_admission_equals_ski_rental(cache, h) for h in range(1, h_max + 1)
    )
    return {
        "rent": str(cache.rent),
        "buy": str(cache.buy),
        "hit": str(cache.hit),
        "savings": str(cache.savings),
        "h_max": h_max,
        "deterministic_buy_request": deterministic_buy_request(cache),
        "max_competitive_ratio": str(worst),
        "two_competitive": worst <= 2,
        "cache_admission_is_ski_rental": equalities,
        "density_rows": density_rows,
        "reduction": "ADOPT",
        "nonlinear_witness": nonlinear_adapt_witness(),
        "terminal": "EXACT_META_POLICY_SUFFICIENT_LINEAR_CACHE",
        "ml_residual": False,
    }


def main() -> dict[str, object]:
    return linear_qualification()


if __name__ == "__main__":
    import json

    print(json.dumps(main(), sort_keys=True, indent=2))
