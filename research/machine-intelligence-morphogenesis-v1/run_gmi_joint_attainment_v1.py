#!/usr/bin/env python3
"""Finite calibration of an explicitly frozen attainment correction, not a holdout."""
from fractions import Fraction
from itertools import product
import hashlib
import json
from pathlib import Path

checks = failures = 0
for mask in range(1 << 12):
    rows = [[0] * 4] + [[(mask >> (4 * i + j)) & 1 for j in range(4)] for i in range(3)]
    point = [max(row[j] for row in rows) for j in range(4)]
    for weights in product((1, 2), repeat=4):
        outer = sum(w * p for w, p in zip(weights, point))
        joint = max(sum(w * bit for w, bit in zip(weights, row)) for row in rows)
        attained_all = any(row == point for row in rows)
        failures += (joint == outer) != attained_all
        checks += 1
prefix_checks = 0
for n in range(1, 129):
    total = sum(Fraction(1, 2**e) for e in range(1, n + 1))
    assert total == 1 - Fraction(1, 2**n) and total < 1
    prefix_checks += 1
result = {
    "status": "FINITE_SUCCESSOR_GREEN" if failures == 0 else "FINITE_SUCCESSOR_RED",
    "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "finite_positive_weight_matrix_cases": checks,
    "finite_equivalence_failures": failures,
    "geometric_prefix_checks": prefix_checks,
    "preserved_failure": "Unqualified RC-02 equality-implies-attainment is false on a countably infinite obligation set",
    "correction": "The inequality is valid; equality implies joint attainment for finite positive-weight obligations and a nonempty common feasible state set, or when supremum attainment is separately proved",
    "infinite_counterexample_proof": "State n covers obligations 1..n with weights 2^-e; breadth=1-2^-n<1 for every state, but supremum and pointwise breadth both equal 1",
    "scope": "Exact proof plus fresh finite calibration; no empirical or held-family evidence"
}
print(json.dumps(result, sort_keys=True, indent=2))
if failures:
    raise SystemExit(1)
