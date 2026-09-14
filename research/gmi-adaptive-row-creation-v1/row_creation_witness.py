"""Exact conservative confidence certificates for ARC-7 (adaptive row creation).

Extends ARC-1-4 and ARC-6 to rows created dynamically based on observed data.
The simultaneous confidence event remains valid over every row at every visit,
including rows born after the process starts.

Uses the ARC-6 Certificate dataclass and integer-math grid radius.
Python >= 3.8, stdlib only.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from math import isqrt


def _ceil_sqrt(value):
    if type(value) is not int or value < 0:
        raise ValueError("nonnegative integer required")
    root = isqrt(value)
    return root if root * root == value else root + 1


# ------------------------------------------------------------------
# Geometric budget allocation
# ------------------------------------------------------------------

def geometric_budget(alpha, step):
    if not isinstance(alpha, F) or not F(0) < alpha < F(1):
        raise ValueError("alpha must be Fraction in (0,1)")
    if type(step) is not int or step < 1:
        raise ValueError("step must be positive integer")
    return alpha / (step * (step + 1))


def geometric_budget_telescopes(alpha, T):
    total = F(0)
    for t in range(1, T + 1):
        total += geometric_budget(alpha, t)
    return total


def uniform_budget(alpha, step, max_steps=1000):
    return alpha / (max_steps * (step + 1))


# ------------------------------------------------------------------
# Per-row certificate (ARC-6 integer grid radius)
# ------------------------------------------------------------------

@dataclass(frozen=True)
class Certificate:
    alpha: F
    weight: F
    visits: int
    exponent: int
    numerator: int
    radius: F


def certificate(alpha, weight, visits):
    """ARC-6 grid radius stored in a Certificate dataclass.

    m = smallest integer with 2*2^(-m) <= delta,
    k = ceil_sqrt(m*n/2), k <= n.

    The numerator is stored before Fraction auto-reduction so that
    verify_certificate can check 2*k^2 >= m*n exactly.
    """
    if not isinstance(alpha, F) or not F(0) < alpha < F(1):
        raise ValueError("alpha must be Fraction in (0,1)")
    if not isinstance(weight, F) or weight <= 0:
        raise ValueError("weight must be positive Fraction")
    if type(visits) is not int or visits < 0:
        raise ValueError("visits must be nonnegative integer")
    if visits == 0:
        return Certificate(alpha, weight, 0, 0, 0, F(1))
    delta = alpha * weight / (visits * (visits + 1))
    if delta >= F(1):
        return Certificate(alpha, weight, visits, 0, 0, F(0))
    target = (2 * delta.denominator + delta.numerator - 1) // delta.numerator
    exponent = (target - 1).bit_length()
    k = min(visits, _ceil_sqrt((exponent * visits + 1) // 2))
    return Certificate(alpha, weight, visits, exponent, k, F(k, visits))


def verify_certificate(cert):
    """Check two independent integer inequalities.

    (1) 2*2^(-m) <= delta  (dyadic tail bound within budget)
    (2) 2*k^2 >= m*n       (Hoeffding exponent covered by dyadic)
    """
    if not isinstance(cert, Certificate):
        return False
    try:
        if not isinstance(cert.alpha, F) or not F(0) < cert.alpha < F(1):
            return False
        if not isinstance(cert.weight, F) or cert.weight <= 0:
            return False
        if type(cert.visits) is not int or cert.visits < 0:
            return False
        if type(cert.exponent) is not int or cert.exponent < 0:
            return False
        if type(cert.numerator) is not int or cert.numerator < 0:
            return False
    except (TypeError, ValueError):
        return False
    if not isinstance(cert.radius, F) or not F(0) <= cert.radius <= F(1):
        return False
    n, k, m = cert.visits, cert.numerator, cert.exponent
    if n == 0:
        return k == 0 and m == 0 and cert.radius == F(1)
    if k > n or cert.radius != F(k, n):
        return False
    if cert.radius == F(1):
        return True
    delta = cert.alpha * cert.weight / (n * (n + 1))
    target = (2 * delta.denominator + delta.numerator - 1) // delta.numerator
    return m >= (target - 1).bit_length() and 2 * k * k >= m * n


# ------------------------------------------------------------------
# Adaptive creator (simulation)
# ------------------------------------------------------------------

class AdaptiveCreator(object):
    def __init__(self, alpha, initial_rows, creation_threshold, max_creations):
        if not isinstance(alpha, F) or not F(0) < alpha < F(1):
            raise ValueError("alpha must be Fraction in (0,1)")
        if type(initial_rows) is not int or initial_rows < 1:
            raise ValueError("initial_rows must be positive integer")
        if not isinstance(creation_threshold, F) or creation_threshold <= 0:
            raise ValueError("creation_threshold must be positive Fraction")
        if type(max_creations) is not int or max_creations < 0:
            raise ValueError("max_creations must be nonneg integer")
        self.alpha = alpha
        self.creation_threshold = creation_threshold
        self.max_creations = max_creations
        self.creations_done = 0
        self.rows = []
        for i in range(initial_rows):
            w = F(1) / F(initial_rows)
            self.rows.append({
                'birth_step': 0,
                'weight': w,
                'mean': F(1, 2) + F(i, 2 * initial_rows),
                'visits': 0,
                'successes': 0,
            })

    def create_row(self, birth_step):
        if self.creations_done >= self.max_creations:
            return None
        weight = geometric_budget(self.alpha, birth_step)
        mean = F(1, 3) + F(self.creations_done, 15)
        row = {
            'birth_step': birth_step,
            'weight': weight,
            'mean': mean,
            'visits': 0,
            'successes': 0,
        }
        self.rows.append(row)
        self.creations_done += 1
        return row

    def observe(self, row_idx, score):
        row = self.rows[row_idx]
        if not isinstance(score, F) or not F(0) <= score <= F(1):
            raise ValueError("score must be Fraction in [0,1]")
        row['visits'] += 1
        row['successes'] += score

    def get_cert(self, row_idx):
        row = self.rows[row_idx]
        return certificate(self.alpha, row['weight'], row['visits'])

    def get_radius(self, row_idx):
        return self.get_cert(row_idx).radius

    def get_interval(self, row_idx):
        row = self.rows[row_idx]
        if row['visits'] == 0:
            return (F(0), F(1))
        center = row['successes'] / row['visits']
        r = self.get_radius(row_idx)
        return (max(F(0), center - r), min(F(1), center + r))

    def check_simultaneous(self):
        for i, row in enumerate(self.rows):
            if row['visits'] == 0:
                continue
            lo, hi = self.get_interval(i)
            if not (lo <= row['mean'] <= hi):
                return False
        return True

    def should_create(self):
        if self.creations_done >= self.max_creations:
            return False
        for i, row in enumerate(self.rows):
            if row['visits'] > 0:
                if self.get_radius(i) > self.creation_threshold:
                    return False
        return True


# ------------------------------------------------------------------
# Simulation
# ------------------------------------------------------------------

def simulate_creation_process(alpha, initial_rows=3, max_creations=5,
                               steps=100, creation_threshold=F(1, 4)):
    creator = AdaptiveCreator(alpha, initial_rows, creation_threshold,
                               max_creations)
    evidence = {
        'total_steps': steps,
        'rows_created': 0,
        'budget_spent': F(0),
        'budget_available': alpha,
        'simultaneous_holds': True,
        'radii_shrink': True,
        'creation_steps': [],
        'radii_history': [],
    }
    for step in range(1, steps + 1):
        if creator.should_create():
            row = creator.create_row(step)
            if row is not None:
                evidence['rows_created'] += 1
                evidence['budget_spent'] += geometric_budget(alpha, step)
                evidence['creation_steps'].append(step)
        for i in range(len(creator.rows)):
            row = creator.rows[i]
            if row['visits'] < step:
                score = F(1) if row['mean'] > F(1, 2) else F(0)
                creator.observe(i, score)
        radii = [creator.get_radius(i) for i in range(len(creator.rows))]
        evidence['radii_history'].append(radii)
        if not creator.check_simultaneous():
            evidence['simultaneous_holds'] = False
    for i in range(len(creator.rows)):
        row = creator.rows[i]
        if row['visits'] >= 5:
            birth = row['birth_step']
            row_radii = []
            for t_idx in range(max(0, birth),
                               len(evidence['radii_history'])):
                if i < len(evidence['radii_history'][t_idx]):
                    row_radii.append(evidence['radii_history'][t_idx][i])
            if len(row_radii) > 1:
                if not (row_radii[0] >= row_radii[-1]):
                    evidence['radii_shrink'] = False
    return evidence


# ------------------------------------------------------------------
# Verification helpers
# ------------------------------------------------------------------

def verify_geometric_budget_is_tight(alpha, T):
    total = geometric_budget_telescopes(alpha, T)
    expected = alpha * F(T, T + 1)
    return total == expected, total, expected


def verify_uniform_budget_fails(alpha, T):
    total = F(0)
    for t in range(1, T + 1):
        total += uniform_budget(alpha, t)
    geometric_total = geometric_budget_telescopes(alpha, T)
    return total != geometric_total, total, geometric_total
