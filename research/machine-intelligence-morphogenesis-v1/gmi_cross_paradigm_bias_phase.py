"""Exact finite cross-paradigm inductive-bias phase calibration.

One obligation:
  predict held-out labels on five ordered inputs after m labeled examples.

Concept universe:
  all 2^5 deterministic Boolean labelings.

Structured subset:
  six monotone threshold concepts.

Learners:
  EXEMPLAR_MEMORY       architecture-light/unbiased unseen prediction
  SYMBOLIC_THRESHOLD    discrete threshold version space
  BAYES_THRESHOLD_MIX   Bayesian structural prior + universal concept support
  PARAMETRIC_PERCEPTRON one-neuron online perceptron

The calibration demonstrates an NFL-style ecology crossover. It does not claim
modern neural networks are equivalent to symbolic/Bayesian systems.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
from typing import Callable, Dict, Iterable, Mapping, Sequence, Tuple


X: Tuple[int, ...] = tuple(range(5))
Concept = Tuple[int, ...]
Train = Tuple[Tuple[int, int], ...]
Predictor = Callable[[Train, int], Fraction]

ALL_CONCEPTS: Tuple[Concept, ...] = tuple(product((0, 1), repeat=len(X)))
THRESHOLD_CONCEPTS: Tuple[Concept, ...] = tuple(
    tuple(1 if x >= k else 0 for x in X) for k in range(len(X) + 1)
)
NONTHRESHOLD_CONCEPTS: Tuple[Concept, ...] = tuple(
    f for f in ALL_CONCEPTS if f not in THRESHOLD_CONCEPTS
)

THRESHOLD_FRACTION = Fraction(len(THRESHOLD_CONCEPTS), len(ALL_CONCEPTS))
assert THRESHOLD_FRACTION == Fraction(3, 16)


def exemplar_memory(train: Train, x: int) -> Fraction:
    seen = dict(train)
    if x in seen:
        return Fraction(seen[x], 1)
    # No structural prior on unseen labels.
    return Fraction(1, 2)


def symbolic_threshold(train: Train, x: int) -> Fraction:
    seen = dict(train)
    if x in seen:
        return Fraction(seen[x], 1)
    version_space = tuple(
        f
        for f in THRESHOLD_CONCEPTS
        if all(f[i] == y for i, y in train)
    )
    if not version_space:
        # Registered fail-soft behavior outside the model class.
        return Fraction(1, 2)
    return Fraction(sum(f[x] for f in version_space), len(version_space))


def bayes_prior(alpha: Fraction = Fraction(1, 2)) -> Dict[Concept, Fraction]:
    """Mixture prior: alpha mass on threshold class, rest uniform universal."""

    if alpha < 0 or alpha > 1:
        raise ValueError("alpha must lie in [0,1]")
    weights = {
        f: (1 - alpha) * Fraction(1, len(ALL_CONCEPTS))
        for f in ALL_CONCEPTS
    }
    for f in THRESHOLD_CONCEPTS:
        weights[f] += alpha * Fraction(1, len(THRESHOLD_CONCEPTS))
    assert sum(weights.values(), Fraction(0, 1)) == 1
    return weights


BAYES_WEIGHTS = bayes_prior()


def bayes_threshold_mix(train: Train, x: int) -> Fraction:
    seen = dict(train)
    if x in seen:
        return Fraction(seen[x], 1)
    posterior = tuple(
        (f, weight)
        for f, weight in BAYES_WEIGHTS.items()
        if all(f[i] == y for i, y in train)
    )
    z = sum((weight for _, weight in posterior), Fraction(0, 1))
    if z == 0:
        return Fraction(1, 2)
    positive = sum(
        (weight * f[x] for f, weight in posterior),
        Fraction(0, 1),
    )
    return positive / z


def parametric_perceptron(train: Train, x: int, epochs: int = 8) -> Fraction:
    """One-neuron linear-threshold learner with deterministic online updates.

    Feature is (x-2, 1). Labels are {-1,+1}. Training order is the sorted
    observed input order, repeated for a frozen eight epochs.
    """

    if epochs <= 0:
        raise ValueError("epochs must be positive")
    w = 0
    b = 0
    for _ in range(epochs):
        for i, y01 in sorted(train):
            y = 1 if y01 else -1
            score = w * (i - 2) + b
            if y * score <= 0:
                w += y * (i - 2)
                b += y
    score = w * (x - 2) + b
    if score > 0:
        return Fraction(1, 1)
    if score < 0:
        return Fraction(0, 1)
    return Fraction(1, 2)


LEARNERS: Mapping[str, Predictor] = {
    "EXEMPLAR_MEMORY": exemplar_memory,
    "SYMBOLIC_THRESHOLD": symbolic_threshold,
    "BAYES_THRESHOLD_MIX": bayes_threshold_mix,
    "PARAMETRIC_PERCEPTRON": parametric_perceptron,
}


def heldout_expected_accuracy(concept: Concept, m: int, learner: Predictor) -> Fraction:
    if m <= 0 or m >= len(X):
        raise ValueError("m must be in 1..len(X)-1")
    scores = []
    for observed in combinations(X, m):
        train = tuple((i, concept[i]) for i in observed)
        heldout = tuple(i for i in X if i not in observed)
        score = Fraction(0, 1)
        for i in heldout:
            p1 = learner(train, i)
            if p1 < 0 or p1 > 1:
                raise ValueError("predictor returned invalid probability")
            score += p1 if concept[i] else 1 - p1
        scores.append(score / len(heldout))
    return sum(scores, Fraction(0, 1)) / len(scores)


def class_average(concepts: Sequence[Concept], m: int, learner: Predictor) -> Fraction:
    if not concepts:
        raise ValueError("concept class must be nonempty")
    return sum(
        (heldout_expected_accuracy(f, m, learner) for f in concepts),
        Fraction(0, 1),
    ) / len(concepts)


def ecology_score(
    *,
    p_threshold: Fraction,
    threshold_score: Fraction,
    nonthreshold_score: Fraction,
) -> Fraction:
    if p_threshold < 0 or p_threshold > 1:
        raise ValueError("p_threshold must lie in [0,1]")
    return p_threshold * threshold_score + (1 - p_threshold) * nonthreshold_score


def exact_rows() -> dict:
    rows = {}
    for m in range(1, len(X)):
        rows_m = {}
        for name, learner in LEARNERS.items():
            threshold_score = class_average(THRESHOLD_CONCEPTS, m, learner)
            nonthreshold_score = class_average(NONTHRESHOLD_CONCEPTS, m, learner)
            uniform_score = ecology_score(
                p_threshold=THRESHOLD_FRACTION,
                threshold_score=threshold_score,
                nonthreshold_score=nonthreshold_score,
            )
            rows_m[name] = {
                "threshold_score": threshold_score,
                "nonthreshold_score": nonthreshold_score,
                "uniform_concept_ecology_score": uniform_score,
                "advantage_sign_above_3_16": (
                    threshold_score > Fraction(1, 2)
                    and nonthreshold_score < Fraction(1, 2)
                ),
            }
        rows[m] = rows_m
    return rows


def crossover_from_scores(threshold_score: Fraction, nonthreshold_score: Fraction) -> Fraction | None:
    denom = threshold_score - nonthreshold_score
    if denom == 0:
        return None
    return (Fraction(1, 2) - nonthreshold_score) / denom


def calibration_receipt() -> dict:
    rows = exact_rows()
    crossover = {}
    for m, row in rows.items():
        crossover[m] = {}
        for name, values in row.items():
            crossover[m][name] = crossover_from_scores(
                values["threshold_score"],
                values["nonthreshold_score"],
            )

    return {
        "schema": "GMICrossParadigmBiasPhaseReceiptV1",
        "domain_size": len(X),
        "concept_count": len(ALL_CONCEPTS),
        "threshold_concept_count": len(THRESHOLD_CONCEPTS),
        "nonthreshold_concept_count": len(NONTHRESHOLD_CONCEPTS),
        "uniform_ecology_threshold_probability": THRESHOLD_FRACTION,
        "training_sizes": tuple(range(1, len(X))),
        "rows": rows,
        "crossover_probability_vs_unbiased_half_baseline": crossover,
        "registered_interpretation": {
            "EXEMPLAR_MEMORY": "unbiased unseen-label baseline",
            "SYMBOLIC_THRESHOLD": "discrete structured version-space bias",
            "BAYES_THRESHOLD_MIX": "probabilistic structural prior with universal support",
            "PARAMETRIC_PERCEPTRON": "one-neuron parametric update with threshold bias",
        },
        "terminal": "GMI_CROSS_PARADIGM_BIAS_PHASE_FINITE_EXACT_GREEN_V1",
        "claim_boundary": (
            "Finite concept-learning/NFL-style calibration only. Shows a shared ecology-alignment phase "
            "across different realization/update types; no universal GMI law or modern neural-network equivalence."
        ),
    }


def jsonable(value):
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [jsonable(v) for v in value]
    if isinstance(value, list):
        return [jsonable(v) for v in value]
    return value


if __name__ == "__main__":
    import json

    print(json.dumps(jsonable(calibration_receipt()), indent=2, sort_keys=True))
