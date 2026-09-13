"""New exact full-grid calculation, never a reconstruction of a sampled campaign."""
from collections import Counter
from fractions import Fraction as F
from itertools import product

UNSEEN = (1, 2, 4, 7, 8, 11, 13, 14)
GRID = tuple(range(-8, 9))


def validate_coefficients(k):
    if type(k) not in (tuple, list) or len(k) != 4 or any(type(x) is not int or x not in GRID for x in k):
        raise ValueError("four integer grid coefficients required")


def targets(k, inputs=UNSEEN):
    validate_coefficients(k)
    return tuple(sum(k[i] for i in range(4) if x & (1 << i)) for x in inputs)


def paired_loss(k):
    validate_coefficients(k)
    total = sum(k)
    return sum(abs(total - 2 * x) for x in k)


def scan_loss(k):
    """Independent direct all-constant minimization; no median/pairing formula."""
    values = targets(k)
    return min(sum(abs(c - y) for y in values) for c in range(-24, 25))


def baseline(k):
    return 1 - F(paired_loss(k), 192)


def cdf(histogram, point):
    total = sum(histogram.values())
    return F(sum(n for loss, n in histogram.items() if 1 - F(loss, 192) <= point), total)


def full_grid():
    histogram = Counter()
    for k in product(GRID, repeat=4):
        loss = paired_loss(k)
        if scan_loss(k) != loss:
            raise ValueError("independent constant scan disagreement")
        if targets(k, (1, 2, 4, 8)) != k:
            raise ValueError("singleton injectivity witness failed")
        histogram[loss] += 1
    if sum(histogram.values()) != 17 ** 4:
        raise ValueError("incomplete Cartesian grid")
    projections = {}
    for name, c in (("search", F("0.9653")), ("memory", F("0.8524")),
                    ("retrieval", F("0.8142")), ("gradient_h2", F("0.6788")),
                    ("gradient_h4", F("0.7335"))):
        t = c - F(1, 24)
        projections[name] = {"reported_c": str(c), "baseline_threshold": str(t),
            "F_B_at_threshold": str(cdf(histogram, t)),
            "hypothetical_exact_S_equals_c_frequency": str(cdf(histogram, t) if c >= F(17, 20) else F(0)),
            "rounding_only_c_interval_CDF": [str(cdf(histogram, t - F(1, 20000))),
                                            str(cdf(histogram, t + F(1, 20000)))]}
    return {"scope": "new uniform full-grid analytical population; no registry rejection",
            "tuples": 17 ** 4, "full_target_injective": True,
            "constant_candidates_per_tuple": 49, "constant_candidates_evaluated": 49 * 17 ** 4,
            "loss_histogram": {str(k): v for k, v in sorted(histogram.items())},
            "mean_best_constant": str(sum((1 - F(k, 192)) * n for k, n in histogram.items()) / 17 ** 4),
            "conditional_projections_only": projections}
