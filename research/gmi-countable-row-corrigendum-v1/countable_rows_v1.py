"""Exact conservative confidence certificates for ARC-6.

No floating-point/transcendental decision is used. Validity is conditional on
FORMALIZATION_V1.md's sampling premise; this module cannot verify that premise.
Python >= 3.8, standard library only.
"""
from dataclasses import dataclass
from fractions import Fraction
from math import isqrt

F = Fraction


def natural(value, name, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError("%s must be an integer >= %d" % (name, minimum))
    return value


def probability(value, name="alpha"):
    if not isinstance(value, F) or not F(0) < value < F(1):
        raise ValueError("%s must be a Fraction strictly between zero and one" % name)
    return value


def row_weight(row):
    """Creation index is never reused; sum_{j>=1} w_j = 1."""
    natural(row, "row", 1)
    return F(1, row * (row + 1))


def allocated_mass(rows):
    """Exact partial sum of the infinite row allocation, including rows=0."""
    natural(rows, "rows")
    return F(rows, rows + 1)


def allowance(alpha, row, visits):
    probability(alpha)
    natural(visits, "visits", 1)
    return alpha * row_weight(row) / (visits * (visits + 1))


def ceil_sqrt(value):
    natural(value, "radicand")
    root = isqrt(value)
    return root if root * root == value else root + 1


@dataclass(frozen=True)
class Certificate:
    alpha: F
    row: int
    visits: int
    exponent: int
    numerator: int
    radius: F


def certificate(alpha, row, visits):
    """Return radius k/n, or the deterministic radius 1 when uninformative.

    m is the least integer with 2*2**(-m) <= delta. Choosing 2*k*k >= m*n
    bounds both Hoeffding tails since exp(-m) <= 2**(-m). This is deliberately
    wider than a natural-log radius; it is not a best-rate confidence sequence.
    """
    probability(alpha)
    row_weight(row)
    natural(visits, "visits")
    if visits == 0:
        return Certificate(alpha, row, 0, 0, 0, F(1))
    delta = allowance(alpha, row, visits)
    target = (2 * delta.denominator + delta.numerator - 1) // delta.numerator
    exponent = (target - 1).bit_length()
    k = min(visits, ceil_sqrt((exponent * visits + 1) // 2))
    return Certificate(alpha, row, visits, exponent, k, F(k, visits))


def verify_certificate(cert):
    """Check numerical sufficiency, not sample independence or data provenance.

    Alternative conservative certificates may pass: minimality is not required.
    """
    if not isinstance(cert, Certificate):
        return False
    try:
        probability(cert.alpha)
        row_weight(cert.row)
        natural(cert.visits, "visits")
        natural(cert.exponent, "exponent")
        natural(cert.numerator, "numerator")
    except ValueError:
        return False
    if not isinstance(cert.radius, F) or not F(0) <= cert.radius <= F(1):
        return False
    if cert.visits == 0:
        return cert.exponent == cert.numerator == 0 and cert.radius == F(1)
    n, k, m = cert.visits, cert.numerator, cert.exponent
    if k > n or cert.radius != F(k, n):
        return False
    if cert.radius == F(1):
        return True  # |sample mean - conditional mean| <= 1 deterministically.
    delta = allowance(cert.alpha, cert.row, n)
    # Equivalent to 2**m * delta >= 2, without allocating an enormous 2**m.
    target = (2 * delta.denominator + delta.numerator - 1) // delta.numerator
    return m >= (target - 1).bit_length() and 2 * k * k >= m * n


def interval_from_sum(total, alpha, row, visits):
    """Closed interval for a mean of [0,1] scores, given an exact sufficient sum."""
    cert = certificate(alpha, row, visits)
    if not isinstance(total, F) or not F(0) <= total <= visits:
        raise ValueError("total must be an exact Fraction in [0, visits]")
    if visits == 0:
        return F(0), F(1)
    center = total / visits
    return max(F(0), center - cert.radius), min(F(1), center + cert.radius)


def interval(samples, alpha, row):
    samples = tuple(samples)
    if any(not isinstance(x, F) or not F(0) <= x <= F(1) for x in samples):
        raise ValueError("scores must be Fractions in [0,1]")
    return interval_from_sum(sum(samples, F(0)), alpha, row, len(samples))


def independent_alarm_probability(per_row, rows):
    """Counterexample for independent fixed-level errors, not a universal limit."""
    probability(per_row, "per_row")
    natural(rows, "rows")
    return F(1) - (F(1) - per_row) ** rows
