"""Finite exact Bayesian DS-E1 calibration for GMI realization demand/response.

Binary latent theta in {0,1}; one binary-symmetric observation channel.
The microscope keeps distinct:

* prior uncertainty;
* expected information gain of an observation;
* Bayes-optimal decision accuracy before/after the observation;
* scalar value of information under an explicitly frozen decision utility/cost.

This is Bayesian decision/information theory parent territory, not GMI novelty.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import log2


@dataclass(frozen=True)
class BinaryBayesWorld:
    prior_theta1: float
    flip_probability: float

    def __post_init__(self) -> None:
        if not 0.0 < self.prior_theta1 < 1.0:
            raise ValueError("prior_theta1 must be strictly between 0 and 1")
        if not 0.0 <= self.flip_probability < 0.5:
            raise ValueError("flip_probability must be in [0, 0.5)")


def binary_entropy(p: float) -> float:
    if not 0.0 <= p <= 1.0:
        raise ValueError("probability outside [0,1]")
    if p in (0.0, 1.0):
        return 0.0
    return -p * log2(p) - (1.0 - p) * log2(1.0 - p)


def predictive_y1(world: BinaryBayesWorld) -> float:
    p = world.prior_theta1
    e = world.flip_probability
    return p * (1.0 - e) + (1.0 - p) * e


def posterior_theta1(world: BinaryBayesWorld, y: int) -> float:
    if y not in (0, 1):
        raise ValueError("y must be binary")
    p = world.prior_theta1
    e = world.flip_probability
    if y == 1:
        numerator = p * (1.0 - e)
        denominator = predictive_y1(world)
    else:
        numerator = p * e
        denominator = 1.0 - predictive_y1(world)
    return numerator / denominator


def prior_map_accuracy(world: BinaryBayesWorld) -> float:
    p = world.prior_theta1
    return max(p, 1.0 - p)


def expected_posterior_entropy(world: BinaryBayesWorld) -> float:
    py1 = predictive_y1(world)
    p1 = posterior_theta1(world, 1)
    p0 = posterior_theta1(world, 0)
    return py1 * binary_entropy(p1) + (1.0 - py1) * binary_entropy(p0)


def expected_information_gain(world: BinaryBayesWorld) -> float:
    return binary_entropy(world.prior_theta1) - expected_posterior_entropy(world)


def posterior_map_expected_accuracy(world: BinaryBayesWorld) -> float:
    py1 = predictive_y1(world)
    p1 = posterior_theta1(world, 1)
    p0 = posterior_theta1(world, 0)
    return py1 * max(p1, 1.0 - p1) + (1.0 - py1) * max(p0, 1.0 - p0)


def map_accuracy_gain(world: BinaryBayesWorld) -> float:
    return posterior_map_expected_accuracy(world) - prior_map_accuracy(world)


def observe_is_worthwhile_under_accuracy_utility(
    world: BinaryBayesWorld, *, observation_cost: float
) -> bool:
    """Decision-theoretic toy: one unit of accuracy is one utility unit.

    The price convention is explicitly authored for this calibration and must not be
    treated as a universal mapping from bits of information to resource cost.
    """

    if observation_cost < 0:
        raise ValueError("observation_cost must be non-negative")
    return map_accuracy_gain(world) > observation_cost


def calibration_receipt() -> dict:
    balanced = BinaryBayesWorld(prior_theta1=0.5, flip_probability=0.1)
    strong_prior = BinaryBayesWorld(prior_theta1=0.9, flip_probability=0.1)

    rows = {}
    for name, world in (("BALANCED_PRIOR", balanced), ("STRONG_PRIOR", strong_prior)):
        rows[name] = {
            "prior_theta1": world.prior_theta1,
            "flip_probability": world.flip_probability,
            "prior_entropy_bits": binary_entropy(world.prior_theta1),
            "expected_information_gain_bits": expected_information_gain(world),
            "prior_map_accuracy": prior_map_accuracy(world),
            "posterior_map_expected_accuracy": posterior_map_expected_accuracy(world),
            "map_accuracy_gain": map_accuracy_gain(world),
        }

    return {
        "schema": "GMIBayesianRealizationMicroscopeV1",
        "family": "finite binary Bayesian inference/decision",
        "rows": rows,
        "key_hostile": (
            "The strong-prior world has positive expected information gain but zero "
            "Bayes-MAP accuracy gain; information availability is not identical to decision value."
        ),
        "demand_response_mapping": {
            "phi": "binary symmetric external observation channel",
            "native_parent_predictors": [
                "prior entropy / prior mass",
                "expected information gain",
                "posterior distribution",
                "Bayes decision value under declared utility"
            ],
            "morphology_or_policy_response": "whether/how inference uses the observation under its cost model"
        },
        "terminal": "BAYESIAN_NATIVE_INFORMATION_AND_DECISION_VALUE_CALIBRATED_EXACT",
        "claim_boundary": "Finite Bayesian decision-theory calibration only; no cross-paradigm law."
    }


if __name__ == "__main__":
    import json

    print(json.dumps(calibration_receipt(), indent=2, sort_keys=True))
