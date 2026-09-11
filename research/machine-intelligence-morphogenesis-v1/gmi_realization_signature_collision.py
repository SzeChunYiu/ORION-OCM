"""Exact DS-E0b collision for the coarse GMI realization demand signature.

Two 3-bit Boolean obligations are matched on deliberately coarse obligation-side
coordinates but differ in constructive regularity under a frozen affine-XOR
language. The purpose is to falsify sufficiency of the coarse signature, not to
claim affine XOR as a universal representation language.

Parent-owned finite Boolean algebra / coding calibration only.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Callable, Iterable, Tuple


Bits = Tuple[int, ...]
TruthTable = Tuple[int, ...]


@dataclass(frozen=True)
class CoarseDemandSignature:
    input_bits: int
    exact_cases: int
    relevant_input_fraction: float
    feedback_channel: str
    drift_updates: int
    verifier: str
    reuse_horizon: int
    retention_requirement: str
    resource_prices: Tuple[float, ...]


@dataclass(frozen=True)
class RealizationCost:
    name: str
    semantically_admissible: bool
    build: int
    serve: int

    @property
    def total(self) -> int:
        return self.build + self.serve


def inputs(n: int) -> Tuple[Bits, ...]:
    if n < 1:
        raise ValueError("n must be >= 1")
    return tuple(product((0, 1), repeat=n))


def table(n: int, fn: Callable[[Bits], int]) -> TruthTable:
    values = tuple(int(bool(fn(x))) for x in inputs(n))
    return values


def parity3(x: Bits) -> int:
    if len(x) != 3:
        raise ValueError("parity3 expects 3 bits")
    return x[0] ^ x[1] ^ x[2]


def majority3(x: Bits) -> int:
    if len(x) != 3:
        raise ValueError("majority3 expects 3 bits")
    return int(sum(x) >= 2)


def variable_is_relevant(truth: TruthTable, n: int, variable: int) -> bool:
    """Exact semantic relevance: some pair differing only in variable changes output."""

    if not 0 <= variable < n:
        raise ValueError("variable outside range")
    xs = inputs(n)
    index = {x: i for i, x in enumerate(xs)}
    for x in xs:
        y = list(x)
        y[variable] ^= 1
        y_t = tuple(y)
        if truth[index[x]] != truth[index[y_t]]:
            return True
    return False


def relevant_input_fraction(truth: TruthTable, n: int) -> float:
    if len(truth) != 2 ** n:
        raise ValueError("truth-table length mismatch")
    return sum(variable_is_relevant(truth, n, i) for i in range(n)) / n


def affine_coefficients(truth: TruthTable, n: int) -> Tuple[int, ...] | None:
    """Return shortest lexicographic affine GF(2) coefficient vector if exact.

    Coefficients are `(a0, a1, ..., an)` for
        f(x) = a0 XOR (a1*x1) XOR ... XOR (an*xn).
    Finite enumeration is exact for this tiny calibration.
    """

    if len(truth) != 2 ** n:
        raise ValueError("truth-table length mismatch")
    xs = inputs(n)
    matches = []
    for coeff in product((0, 1), repeat=n + 1):
        produced = []
        for x in xs:
            value = coeff[0]
            for a, bit in zip(coeff[1:], x):
                value ^= a & bit
            produced.append(value)
        if tuple(produced) == truth:
            matches.append(coeff)
    if not matches:
        return None
    return min(matches, key=lambda c: (sum(c), c))


def affine_description_terms(truth: TruthTable, n: int) -> int | None:
    coeff = affine_coefficients(truth, n)
    if coeff is None:
        return None
    # Count active constant/input terms. A zero function can have length 0 here;
    # this is a frozen finite code-cost convention, not Kolmogorov complexity.
    return sum(coeff)


def coarse_signature(truth: TruthTable, n: int, *, horizon: int = 1) -> CoarseDemandSignature:
    if horizon < 0:
        raise ValueError("horizon must be non-negative")
    return CoarseDemandSignature(
        input_bits=n,
        exact_cases=2 ** n,
        relevant_input_fraction=relevant_input_fraction(truth, n),
        feedback_channel="FULL_EXACT_OUTPUT_LABEL",
        drift_updates=0,
        verifier="EXACT_TRUTH_TABLE_CHECKER",
        reuse_horizon=horizon,
        retention_requirement="NONE_BEYOND_FROZEN_FUNCTION",
        resource_prices=(1.0, 1.0),
    )


def candidate_realizations(truth: TruthTable, n: int, *, horizon: int = 1) -> Tuple[RealizationCost, ...]:
    affine_terms = affine_description_terms(truth, n)
    affine = RealizationCost(
        name="AFFINE_XOR_PROGRAM",
        semantically_admissible=affine_terms is not None,
        build=affine_terms if affine_terms is not None else 0,
        serve=horizon * n,
    )
    lookup = RealizationCost(
        name="LOOKUP_TABLE",
        semantically_admissible=True,
        build=2 ** n,
        serve=horizon,
    )
    return (affine, lookup)


def winner(truth: TruthTable, n: int, *, horizon: int = 1) -> Tuple[str, ...]:
    candidates = tuple(c for c in candidate_realizations(truth, n, horizon=horizon) if c.semantically_admissible)
    best = min(c.total for c in candidates)
    return tuple(sorted(c.name for c in candidates if c.total == best))


def collision_receipt() -> dict:
    p = table(3, parity3)
    m = table(3, majority3)

    p_signature = coarse_signature(p, 3, horizon=1)
    m_signature = coarse_signature(m, 3, horizon=1)
    if p_signature != m_signature:
        raise AssertionError("fixture no longer matches the frozen coarse signature")

    p_affine = affine_description_terms(p, 3)
    m_affine = affine_description_terms(m, 3)
    p_winner = winner(p, 3, horizon=1)
    m_winner = winner(m, 3, horizon=1)

    return {
        "schema": "GMIRealizationSignatureCollisionReceiptV1",
        "obligations": {
            "PARITY_3": {
                "truth_table": p,
                "affine_description_terms": p_affine,
                "winner": p_winner,
            },
            "MAJORITY_3": {
                "truth_table": m,
                "affine_description_terms": m_affine,
                "winner": m_winner,
            },
        },
        "matched_coarse_signature": {
            "input_bits": p_signature.input_bits,
            "exact_cases": p_signature.exact_cases,
            "relevant_input_fraction": p_signature.relevant_input_fraction,
            "feedback_channel": p_signature.feedback_channel,
            "drift_updates": p_signature.drift_updates,
            "verifier": p_signature.verifier,
            "reuse_horizon": p_signature.reuse_horizon,
            "retention_requirement": p_signature.retention_requirement,
            "resource_prices": p_signature.resource_prices,
        },
        "collision": p_winner != m_winner,
        "missing_coordinate_exposed": "REGISTERED_CONSTRUCTIVE_REGULARITY / tau_L",
        "terminal": "REALIZATION_SIGNATURE_INSUFFICIENT__COARSE_SIGNATURE_COLLISION_EXACT",
        "claim_boundary": (
            "The collision proves only that the frozen coarse signature is insufficient. "
            "tau_L is reference-language dependent and is not established as a universal coordinate."
        ),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(collision_receipt(), indent=2, sort_keys=True))
