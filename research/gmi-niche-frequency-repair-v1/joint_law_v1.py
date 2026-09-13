"""Exact finite probability controls for achieved-score niche events and CDF bounds."""
from fractions import Fraction as F


def exact_numbers(*values):
    if any(type(x) not in (int, F) for x in values):
        raise ValueError("finite exact rational values required")


def validate(atoms, theta, delta):
    exact_numbers(theta, delta, *(x for atom in atoms for x in atom))
    if not atoms or not 0 <= theta <= 1 or not 0 < delta <= 1:
        raise ValueError("nonempty probability space and valid thresholds required")
    if sum(w for w, b, s in atoms) != 1:
        raise ValueError("probability weights must sum to one")
    if any(w < 0 or not 0 <= b <= 1 or not 0 <= s <= 1 for w, b, s in atoms):
        raise ValueError("invalid atom")


def achieved(atoms, theta=F(17, 20), delta=F(1, 24)):
    validate(atoms, theta, delta)
    return sum((w for w, b, s in atoms if s >= theta and s - b >= delta), F(0))


def constant_upper(atoms, c, theta=F(17, 20), delta=F(1, 24)):
    exact_numbers(c)
    validate(atoms, theta, delta)
    if not 0 <= c <= 1 or any(s > c for _, _, s in atoms):
        raise ValueError("proposed constant is not a valid upper bound")
    return sum((w for w, b, _ in atoms if c >= theta and b <= c - delta), F(0))


def sandwich(atoms, c, epsilon, gamma=F(0), theta=F(17, 20), delta=F(1, 24)):
    exact_numbers(c, epsilon, gamma)
    validate(atoms, theta, delta)
    if not 0 <= c <= 1 or epsilon < 0 or not 0 <= gamma <= 1:
        raise ValueError("invalid approximation contract")
    bad = sum((w for w, _, s in atoms if abs(s - c) > epsilon), F(0))
    if bad > gamma:
        raise ValueError("approximation contract does not hold")
    cdf = lambda x: sum((w for w, b, _ in atoms if b <= x), F(0))
    lower = max(F(0), cdf(c - epsilon - delta) - gamma) if c - epsilon >= theta else F(0)
    upper = min(F(1), cdf(c + epsilon - delta) + gamma) if c + epsilon >= theta else gamma
    return lower, upper


def controls():
    theta, delta = F(1, 2), F(1, 4)
    fixed = [(F(1, 2), F(0), F(3, 4)), (F(1, 2), F(3, 4), F(3, 4))]
    low = [(w, b, F(0)) for w, b, _ in fixed]
    # Same B and S marginals, different pairing: no independence is licensed.
    aligned = [(F(1, 2), F(0), F(1, 2)), (F(1, 2), F(1, 2), F(1))]
    crossed = [(F(1, 2), F(0), F(1)), (F(1, 2), F(1, 2), F(1, 2))]
    sharp_lower = [(F(1, 2), F(1, 4), F(1, 2)), (F(1, 2), F(1, 2), F(1, 2))]
    sharp_upper = [(w, b, F(1)) for w, b, _ in sharp_lower]
    exception = [(F(1, 4), F(0), F(1)), (F(3, 4), F(1), F(0))]
    check = lambda a: achieved(a, theta, delta)
    return {"constant_attained_equality": [str(check(fixed)), str(constant_upper(fixed, F(3, 4), theta, delta))],
            "ceiling_only_counterexample": [str(check(low)), str(constant_upper(low, F(3, 4), theta, delta))],
            "same_marginals_different_joint_frequency": [str(check(aligned)), str(check(crossed))],
            "sharp_lower": [str(check(sharp_lower)), *map(str, sandwich(sharp_lower, F(3, 4), F(1, 4), theta=theta, delta=delta))],
            "sharp_upper": [str(check(sharp_upper)), *map(str, sandwich(sharp_upper, F(3, 4), F(1, 4), theta=theta, delta=delta))],
            "below_theta_except_bad_mass": [str(check(exception)), *map(str, sandwich(exception, F(0), F(0), F(1, 4), theta, delta))]}
