"""Declared probability and lower-expectation contexts with exact arithmetic."""
from fractions import Fraction

from core_v18 import encode, flags
from prefix_v18 import profile


def probability(weights):
    if type(weights) is not tuple or not weights:
        raise ValueError("nonempty exact probability vector required")
    if any(type(w) is not Fraction or w < 0 for w in weights):
        raise ValueError("nonnegative Fraction probabilities required")
    if sum(weights, Fraction(0)) != 1:
        raise ValueError("probability vector must sum to one")
    return weights


def priors(family):
    if type(family) is not tuple or not family:
        raise ValueError("nonempty canonical prior family required")
    for weights in family:
        probability(weights)
    if any(len(weights) != len(family[0]) for weights in family):
        raise ValueError("prior dimensions differ")
    if len(set(family)) != len(family):
        raise ValueError("duplicate priors are not canonical")
    return family


def expectation(weights, values):
    probability(weights)
    profile(values, len(weights))
    return sum((w * value for w, value in zip(weights, values)), Fraction(0))


def lower(family, values):
    priors(family)
    profile(values, len(family[0]))
    return min(expectation(weights, values) for weights in family)


def context_inputs(admitted, profiles):
    flags(admitted)
    if type(profiles) is not tuple or len(profiles) != len(admitted):
        raise ValueError("one profile or undefined marker per history required")


def expectation_context(admitted, profiles, weights):
    context_inputs(admitted, profiles)
    probability(weights)
    values = tuple(None if value is None else expectation(weights, value) for value in profiles)
    return encode(admitted, values, lambda a, b: a <= b)


def lower_context(admitted, profiles, family):
    context_inputs(admitted, profiles)
    priors(family)
    values = tuple(None if value is None else lower(family, value) for value in profiles)
    return encode(admitted, values, lambda a, b: a <= b)


def conditional(weights, event):
    probability(weights)
    if type(event) is not tuple or not event:
        raise ValueError("nonempty distinct event indices required")
    if any(type(i) is not int or not 0 <= i < len(weights) for i in event):
        raise ValueError("event index outside probability space")
    if len(set(event)) != len(event):
        raise ValueError("event indices must be distinct")
    mass = sum((weights[i] for i in event), Fraction(0))
    if mass <= 0:
        raise ValueError("conditioning event has zero probability")
    return tuple(weights[i] / mass for i in event)


def recursive_lower(family, values, partition):
    priors(family)
    profile(values, len(family[0]))
    if type(partition) is not tuple or not partition:
        raise ValueError("nonempty canonical partition required")
    if any(type(event) is not tuple or not event for event in partition):
        raise ValueError("nonempty canonical partition events required")
    if any(type(i) is not int or not 0 <= i < len(values)
           for event in partition for i in event):
        raise ValueError("partition index outside probability space")
    flat = tuple(i for event in partition for i in event)
    if sorted(flat) != list(range(len(values))) or len(set(flat)) != len(flat):
        raise ValueError("partition must cover each state exactly once")
    local = []
    for event in partition:
        conditioned = tuple(dict.fromkeys(conditional(w, event) for w in family))
        local.append(lower(conditioned, tuple(values[i] for i in event)))
    marginals = tuple(dict.fromkeys(tuple(sum((w[i] for i in event), Fraction(0))
                                         for event in partition) for w in family))
    return lower(marginals, tuple(local))
