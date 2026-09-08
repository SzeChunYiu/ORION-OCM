"""Finite reference calculations for OCM foundation obligations, not an authority gate.

Fractions are exact for search ordering and lifetime accounting. Logarithmic
information/confidence calculations use floating point and do not certify a
threshold at a rounding boundary. See OCM_FOUNDATIONS_CLOSURE_V1.md for the
assumptions; these functions cannot establish those assumptions from observations.
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from fractions import Fraction
from itertools import product
from typing import Hashable, Mapping, Sequence


def _natural(value: int, name: str, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def _finite(value: float, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite number")
    try:
        out = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite number") from exc
    if not math.isfinite(out):
        raise ValueError(f"{name} must be finite")
    return out


def binary_entropy(probability: float) -> float:
    p = _finite(probability, "probability")
    if not 0 <= p <= 1:
        raise ValueError("probability outside [0,1]")
    if p in (0, 1):
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)


def fano_information(causes: int, error: float) -> float:
    """Necessary bits for uniform causes, error <= the target, no side information."""
    m = _natural(causes, "causes", minimum=2)
    eps = _finite(error, "error")
    if not 0 <= eps <= 1:
        raise ValueError("error outside [0,1]")
    if eps >= 1 - 1 / m:
        return 0.0  # Blind guessing already attains this target error.
    return max(0.0, math.log2(m) - binary_entropy(eps) - eps * math.log2(m - 1))


def fano_probe_bound(causes: int, error: float, conditional_bits: float,
                     *, fixed_horizon: bool = True) -> float | int:
    """The cap must hold conditionally on each legal prior history, not marginally.

    fixed_horizon=False returns a real lower bound for E[T], never its ceiling.
    Infinity is serialized as a string by report(), not as nonstandard JSON.
    """
    if type(fixed_horizon) is not bool:
        raise ValueError("fixed_horizon must be boolean")
    bits = _finite(conditional_bits, "conditional_bits")
    if bits < 0:
        raise ValueError("negative information cap")
    required = fano_information(causes, error)
    if not required:
        return 0
    if not bits:
        return math.inf
    result = required / bits
    return math.ceil(result) if fixed_horizon else result


def mutual_information(joint: Mapping[tuple[Hashable, Hashable], Fraction]) -> float:
    """Finite joint distribution; exact probability validation, floating point logs."""
    probabilities = {key: Fraction(value) for key, value in joint.items()}
    if not probabilities or any(v < 0 for v in probabilities.values()) or sum(probabilities.values()) != 1:
        raise ValueError("joint probabilities must be nonnegative and sum exactly to one")
    left, right = defaultdict(Fraction), defaultdict(Fraction)
    for (x, y), probability in probabilities.items():
        left[x] += probability
        right[y] += probability
    return math.fsum(float(p) * math.log2(float(p / (left[x] * right[y])))
                     for (x, y), p in probabilities.items() if p)


def xor_information() -> dict[str, float]:
    """Two marginally uninformative observations jointly reveal one bit."""
    first, second, both = defaultdict(Fraction), defaultdict(Fraction), defaultdict(Fraction)
    for z, noise in product((0, 1), repeat=2):
        first[z, noise] += Fraction(1, 4)
        second[z, z ^ noise] += Fraction(1, 4)
        both[z, (noise, z ^ noise)] += Fraction(1, 4)
    a, b, ab = map(mutual_information, (first, second, both))
    return {"first_marginal_bits": a, "second_marginal_bits": b,
            "joint_bits": ab, "second_given_first_bits": ab - a}


def _repair_inputs(probabilities, costs):
    p, c = tuple(map(Fraction, probabilities)), tuple(map(Fraction, costs))
    if not p or len(p) != len(c) or any(x < 0 for x in p) or sum(p) != 1 or any(x <= 0 for x in c):
        raise ValueError("require one normalized probability and positive cost per repair")
    return p, c


def optimal_repair_order(probabilities: Sequence[Fraction], costs: Sequence[Fraction]) -> tuple[int, ...]:
    """One correct repair; failed tests only eliminate that repair; no shared work."""
    p, c = _repair_inputs(probabilities, costs)
    return tuple(sorted(range(len(p)), key=lambda i: (-p[i] / c[i], i)))


def expected_repair_cost(probabilities: Sequence[Fraction], costs: Sequence[Fraction],
                         order: Sequence[int]) -> Fraction:
    p, c = _repair_inputs(probabilities, costs)
    order = tuple(order)
    if any(type(i) is not int for i in order) or sorted(order) != list(range(len(p))):
        raise ValueError("order must be a permutation of all repair indices")
    accumulated = total = Fraction(0)
    for i in order:
        accumulated += c[i]
        total += p[i] * accumulated
    return total


def rare_tail_example(exponent: int = 20) -> dict:
    """Closed form avoids materializing 2**exponent repair candidates."""
    exponent = _natural(exponent, "exponent", minimum=2)
    count = 2 ** exponent
    epsilon = Fraction(1, exponent)
    entropy = binary_entropy(float(epsilon)) + float(epsilon * exponent)
    guesses = 1 + epsilon * Fraction(count + 1, 2)
    return {"rare_alternatives": count, "rare_probability": str(epsilon),
            "shannon_bits": entropy, "entropy_effective_count": 2 ** entropy,
            "optimal_expected_unit_cost_guesses": str(guesses),
            "optimal_expected_unit_cost_guesses_float": float(guesses)}


def geometric_surplus(horizon: int, survival: Fraction, gain: Fraction,
                       build: Fraction, invalidation: Fraction = Fraction(0)) -> Fraction:
    """One lifecycle. Alive at opportunity 1; hazard occurs AFTER each opportunity.

    gain is the expected net gain per alive opportunity at a fixed registered
    price vector. invalidation cost is paid only if invalidation occurs by H.
    No uncharged regeneration, final liquidation, or time discounting is assumed.
    """
    h = _natural(horizon, "horizon")
    s, g, f, r = map(Fraction, (survival, gain, build, invalidation))
    if not 0 <= s <= 1 or f < 0 or r < 0:
        raise ValueError("invalid survival or fixed cost")
    alive = Fraction(h) if s == 1 else (1 - s ** h) / (1 - s)
    return g * alive - f - r * (1 - s ** h)


def strict_payback_horizon(build: Fraction, gain: Fraction) -> int | None:
    """Strict deterministic payback H*gain > build; equality is not payback."""
    build, gain = Fraction(build), Fraction(gain)
    if build < 0:
        raise ValueError("build must be nonnegative")
    return None if gain <= 0 else int(build // gain) + 1


def hoeffding_radius(n: int, delta: float, *, comparisons: int = 1,
                     lower: float = -1.0, upper: float = 1.0) -> float:
    """Time-uniform union-bound radius; iid or bounded fixed conditional-mean data.

    delta/[K*n*(n+1)] is the two-sided failure budget for this comparison/look.
    This is conservative, not the sharper mixture boundaries in Howard et al.
    """
    _natural(n, "n", minimum=1)
    _natural(comparisons, "comparisons", minimum=1)
    delta, lower, upper = (_finite(delta, "delta"), _finite(lower, "lower"), _finite(upper, "upper"))
    if not 0 < delta < 1 or not lower < upper:
        raise ValueError("invalid delta or observation range")
    # Log sums avoid overflow in the integer product 2*K*n*(n+1).
    log_term = math.log(2) + math.log(comparisons) + math.log(n) + math.log(n + 1) - math.log(delta)
    return (upper - lower) * math.sqrt(log_term / (2 * n))


def zero_failures_upper(n: int, alpha: float) -> float:
    """Fixed-n one-sided binomial upper bound; NOT valid under arbitrary repeated looks."""
    _natural(n, "n", minimum=1)
    alpha = _finite(alpha, "alpha")
    if not 0 < alpha < 1:
        raise ValueError("alpha outside (0,1)")
    return -math.expm1(math.log(alpha) / n)


def quotient_witness(observations: Mapping[str, Hashable], blocks: Mapping[str, Hashable],
                     transitions: Mapping[str, Mapping[str, str]]) -> dict | None:
    """Check deterministic finite congruence for exactly the supplied action alphabet.

    Observations must include ALL registered externally meaningful distinctions.
    None is not a certificate for omitted actions or future operator additions.
    """
    states = set(observations)
    if not states or set(blocks) != states:
        raise ValueError("nonempty equal state domains required")
    for transition in transitions.values():
        if set(transition) != states or not set(transition.values()) <= states:
            raise ValueError("transitions must be total on the supplied states")
    representatives = {}
    for state in sorted(states):
        block = blocks[state]
        if block not in representatives:
            representatives[block] = state
            continue
        representative = representatives[block]
        if observations[state] != observations[representative]:
            return {"kind": "OBSERVATION", "states": [representative, state]}
        for action in sorted(transitions):
            transition = transitions[action]
            if blocks[transition[state]] != blocks[transition[representative]]:
                return {"kind": "TRANSITION", "action": action, "states": [representative, state]}
    return None


def report() -> dict:
    p, c = (Fraction(3, 5), Fraction(2, 5)), (Fraction(100), Fraction(1))
    order = optimal_repair_order(p, c)
    observations = {"x": 0, "y": 0, "z": 1}
    blocks = {"x": "A", "y": "A", "z": "B"}
    identity = {state: state for state in observations}
    return {
        "status": "FINITE_CALIBRATION_ONLY__NO_PROGRAMME_ADMISSION",
        "source_warrant_blob": "6cf431adb2e7e45fe5e23122a482262e45e11211",
        "fano": {"causes": 30, "target_error": 0.05,
                 "required_bits": fano_information(30, 0.05),
                 "fixed_probe_lower_bounds": {str(b): fano_probe_bound(30, 0.05, b)
                                               for b in (0.1, 0.25, 0.5, 1, 2)},
                 "expected_probe_lower_bound_at_2_bits": fano_probe_bound(30, 0.05, 2, fixed_horizon=False)},
        "xor_counterexample": xor_information(),
        "repair_entropy_counterexample": rare_tail_example(),
        "repair_cost_counterexample": {"probabilities": list(map(str, p)), "costs": list(map(str, c)),
                                       "optimal_order": order,
                                       "optimal_expected_cost": str(expected_repair_cost(p, c, order)),
                                       "probability_order_expected_cost": str(expected_repair_cost(p, c, (0, 1)))},
        "lifetime": {"deterministic_strict_payback_build_10_gain_2": strict_payback_horizon(10, 2),
                     "surplus_H10_s1_gain2_build10": str(geometric_surplus(10, 1, 2, 10)),
                     "surplus_H10_s_half_gain2_build10": str(geometric_surplus(10, Fraction(1, 2), 2, 10)),
                     "surplus_H10_s_half_gain2_build10_revoke3": str(geometric_surplus(10, Fraction(1, 2), 2, 10, 3))},
        "statistics": {"range": [-1, 1], "comparisons": 4, "delta": 0.05,
                       "uniform_radius_n1000": hoeffding_radius(1000, 0.05, comparisons=4),
                       "fixed_n_zero_failures_upper_n100_alpha05": zero_failures_upper(100, 0.05)},
        "abstraction": {"old_alphabet_witness": quotient_witness(observations, blocks, {"stay": identity}),
                        "new_operator_witness": quotient_witness(observations, blocks,
                            {"stay": identity, "new": {"x": "z", "y": "y", "z": "z"}})},
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, sort_keys=True, allow_nan=False))
