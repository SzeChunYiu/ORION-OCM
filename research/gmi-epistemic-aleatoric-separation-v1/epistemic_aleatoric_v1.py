from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import json
from typing import Tuple

F = Fraction
CANNOT = "CANNOT_DECOMPOSE_WITHOUT_LATENT_SEMANTICS"
FREEZE_COMMIT = "f134569e8a9789cee5b3fde78d2ec330e5355d2a"


def _fraction(value, name: str) -> F:
    if type(value) is not F:
        raise ValueError(f"{name} must be an exact Fraction")
    return value


def _probability(value, name: str) -> F:
    _fraction(value, name)
    if not F(0) <= value <= F(1):
        raise ValueError(f"{name} must lie in [0,1]")
    return value


def _label(value, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty string")
    return value


def _kernel(kernel, name: str = "kernel"):
    if not isinstance(kernel, tuple) or not kernel:
        raise ValueError(f"{name} must be a nonempty tuple")
    seen = set()
    total = F(0)
    for pair in kernel:
        if not isinstance(pair, tuple) or len(pair) != 2:
            raise ValueError(f"{name} entries must be (outcome, probability) pairs")
        outcome, probability = pair
        _fraction(outcome, f"{name} outcome")
        _probability(probability, f"{name} probability")
        if outcome in seen:
            raise ValueError(f"{name} contains duplicate outcomes")
        seen.add(outcome)
        total += probability
    if total != 1:
        raise ValueError(f"{name} probabilities must sum exactly to one")
    return kernel


def canonical_kernel(kernel) -> Tuple[Tuple[F, F], ...]:
    _kernel(kernel)
    return tuple(sorted((outcome, probability) for outcome, probability in kernel if probability > 0))


def mean_of_kernel(kernel) -> F:
    _kernel(kernel)
    return sum((probability * outcome for outcome, probability in kernel), F(0))


def variance_of_kernel(kernel) -> F:
    mean = mean_of_kernel(kernel)
    return sum((probability * (outcome - mean) ** 2 for outcome, probability in kernel), F(0))


@dataclass(frozen=True)
class LatentState:
    label: str
    weight: F
    kernel: Tuple[Tuple[F, F], ...]

    def __post_init__(self):
        _label(self.label, "latent label")
        _probability(self.weight, "latent weight")
        _kernel(self.kernel)


@dataclass(frozen=True)
class FiniteLatentModel:
    states: Tuple[LatentState, ...]

    def __post_init__(self):
        if not isinstance(self.states, tuple) or not self.states:
            raise ValueError("states must be a nonempty tuple")
        if any(not isinstance(state, LatentState) for state in self.states):
            raise ValueError("every state must be LatentState")
        labels = [state.label for state in self.states]
        if len(labels) != len(set(labels)):
            raise ValueError("latent labels must be unique")
        if sum((state.weight for state in self.states), F(0)) != 1:
            raise ValueError("latent weights must sum exactly to one")


@dataclass(frozen=True)
class MarginalOnly:
    marginal: Tuple[Tuple[F, F], ...]

    def __post_init__(self):
        _kernel(self.marginal, "marginal")


@dataclass(frozen=True)
class Decomposition:
    mean: F
    aleatoric: F
    epistemic_mean: F
    total: F
    marginal: Tuple[Tuple[F, F], ...]
    positive_weight_kernels_identical: bool


def marginal_distribution(model: FiniteLatentModel) -> Tuple[Tuple[F, F], ...]:
    if not isinstance(model, FiniteLatentModel):
        raise ValueError("model must be FiniteLatentModel")
    probabilities = {}
    for state in model.states:
        if state.weight == 0:
            continue
        for outcome, probability in state.kernel:
            probabilities[outcome] = probabilities.get(outcome, F(0)) + state.weight * probability
    return tuple(sorted((outcome, probability) for outcome, probability in probabilities.items() if probability > 0))


def decompose_model(model: FiniteLatentModel) -> Decomposition:
    if not isinstance(model, FiniteLatentModel):
        raise ValueError("model must be FiniteLatentModel")
    active = [state for state in model.states if state.weight > 0]
    means = {state.label: mean_of_kernel(state.kernel) for state in active}
    mean = sum((state.weight * means[state.label] for state in active), F(0))
    aleatoric = sum((state.weight * variance_of_kernel(state.kernel) for state in active), F(0))
    epistemic_mean = sum(
        (state.weight * (means[state.label] - mean) ** 2 for state in active), F(0)
    )
    marginal = marginal_distribution(model)
    total = variance_of_kernel(marginal)
    canonical = [canonical_kernel(state.kernel) for state in active]
    kernels_identical = all(kernel == canonical[0] for kernel in canonical[1:]) if canonical else True
    return Decomposition(
        mean=mean,
        aleatoric=aleatoric,
        epistemic_mean=epistemic_mean,
        total=total,
        marginal=marginal,
        positive_weight_kernels_identical=kernels_identical,
    )


def decompose(obj):
    if isinstance(obj, FiniteLatentModel):
        return decompose_model(obj)
    if isinstance(obj, MarginalOnly):
        return CANNOT
    raise ValueError("unsupported uncertainty object")


def frac(value: F) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def distribution_json(kernel):
    return [[frac(outcome), frac(probability)] for outcome, probability in kernel]


def _state(label: str, weight: F, pairs) -> LatentState:
    return LatentState(label, weight, tuple(pairs))


def frozen_models():
    pure_aleatoric = FiniteLatentModel(
        (_state("q", F(1), ((F(-1), F(1, 2)), (F(1), F(1, 2)))),)
    )
    pure_epistemic = FiniteLatentModel(
        (
            _state("minus", F(1, 2), ((F(-1), F(1)),)),
            _state("plus", F(1, 2), ((F(1), F(1)),)),
        )
    )
    mixed = FiniteLatentModel(
        (
            _state("L", F(1, 2), ((F(-1), F(1, 2)), (F(0), F(1, 2)))),
            _state("R", F(1, 2), ((F(0), F(1, 2)), (F(1), F(1, 2)))),
        )
    )
    same_mean_different_kernels = FiniteLatentModel(
        (
            _state("a", F(1, 2), ((F(0), F(1)),)),
            _state("b", F(1, 2), ((F(-1), F(1, 2)), (F(1), F(1, 2)))),
        )
    )
    zero_weight_extension = FiniteLatentModel(
        (
            _state("q", F(1), ((F(-1), F(1, 2)), (F(1), F(1, 2)))),
            _state("ignored", F(0), ((F(100), F(1)),)),
        )
    )
    return pure_aleatoric, pure_epistemic, mixed, same_mean_different_kernels, zero_weight_extension


def decomposition_json(result: Decomposition):
    return {
        "mean": frac(result.mean),
        "aleatoric": frac(result.aleatoric),
        "epistemic_mean": frac(result.epistemic_mean),
        "total": frac(result.total),
        "marginal": distribution_json(result.marginal),
        "positive_weight_kernels_identical": result.positive_weight_kernels_identical,
        "identity_holds": result.total == result.aleatoric + result.epistemic_mean,
    }


def build_receipt():
    pure_aleatoric, pure_epistemic, mixed, same_mean, zero_weight = frozen_models()
    da = decompose_model(pure_aleatoric)
    de = decompose_model(pure_epistemic)
    dm = decompose_model(mixed)
    ds = decompose_model(same_mean)
    dz = decompose_model(zero_weight)
    marginal_only = MarginalOnly(da.marginal)
    return {
        "schema": "EpistemicAleatoricSeparationReceiptV1",
        "issue": 750,
        "parent_issue": 602,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": "EXACT_EPISTEMIC_ALEATORIC_SEPARATION_FOR_REGISTERED_FINITE_LATENT_MODELS",
        "pure_aleatoric": decomposition_json(da),
        "pure_epistemic_mean": decomposition_json(de),
        "mixed": decomposition_json(dm),
        "same_mean_different_kernels": decomposition_json(ds),
        "marginal_nonidentifiability": {
            "same_full_marginal": da.marginal == de.marginal,
            "different_decomposition": (da.aleatoric, da.epistemic_mean)
            != (de.aleatoric, de.epistemic_mean),
            "marginal": distribution_json(da.marginal),
        },
        "zero_weight_invariance": {
            "same_decomposition": (
                da.mean,
                da.aleatoric,
                da.epistemic_mean,
                da.total,
                da.marginal,
            )
            == (dz.mean, dz.aleatoric, dz.epistemic_mean, dz.total, dz.marginal),
            "same_kernel_identity_diagnostic": da.positive_weight_kernels_identical
            == dz.positive_weight_kernels_identical,
        },
        "no_latent_semantics": decompose(marginal_only),
    }


def main() -> int:
    print(json.dumps(build_receipt(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
