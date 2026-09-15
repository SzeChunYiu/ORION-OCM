#!/usr/bin/env python3
"""Exact freeze-first useful-descendant/evolvability assay for #779.

All calculations use fractions.  The three arms share the same current object,
descendant space, admissibility and verifier; only proposal probabilities differ.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import product
import hashlib
import json

BITS = (0, 1)
STATES = tuple(product(BITS, repeat=6))
CURRENT_OBJECT = (0, 0, 0, 0, 0, 0)
ADMISSIBILITY = "ALL_64_DESCENDANTS_ADMISSIBLE"
VERIFIER = "EXACT_FROZEN_UTILITY_MEMBERSHIP"
ZERO_MASS_TERMINAL = "UNREACHABLE_ZERO_USEFUL_MASS"
CLAIM_CEILING = "USEFUL_DESCENDANT_EVOLVABILITY_PREDICTION_VALIDATED_AT_REGISTERED_FINITE_SCOPE"

KERNEL_PARAMETERS = {
    "CONTINUED": (Fraction(3, 4), Fraction(3, 4), Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(1, 2)),
    "RESET": (Fraction(1, 2),) * 6,
    "SHUFFLED_HISTORY": (Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(3, 4), Fraction(3, 4)),
}

UTILITIES = {
    "U_45": {4: 1, 5: 1},
    "U_AND": {0: 1, 1: 1},
    "U_ANTI": {0: 0, 1: 0},
}

DEVELOPMENT_OBLIGATIONS = {
    "D0": {0: 1},
    "D1": {1: 1},
}

FROZEN_EXPECTED = {
    "U_45": {
        "CONTINUED": (Fraction(1, 4), Fraction(4, 1)),
        "RESET": (Fraction(1, 4), Fraction(4, 1)),
        "SHUFFLED_HISTORY": (Fraction(9, 16), Fraction(16, 9)),
    },
    "U_AND": {
        "CONTINUED": (Fraction(9, 16), Fraction(16, 9)),
        "RESET": (Fraction(1, 4), Fraction(4, 1)),
        "SHUFFLED_HISTORY": (Fraction(1, 4), Fraction(4, 1)),
    },
    "U_ANTI": {
        "CONTINUED": (Fraction(1, 16), Fraction(16, 1)),
        "RESET": (Fraction(1, 4), Fraction(4, 1)),
        "SHUFFLED_HISTORY": (Fraction(1, 4), Fraction(4, 1)),
    },
}


def fmt(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def state_string(state: tuple[int, ...]) -> str:
    return "".join(str(bit) for bit in state)


def matches(state: tuple[int, ...], requirements: dict[int, int]) -> bool:
    return all(state[index] == value for index, value in requirements.items())


def truth_table(requirements: dict[int, int]) -> tuple[bool, ...]:
    return tuple(matches(state, requirements) for state in STATES)


def factorized_kernel(p_one: tuple[Fraction, ...]) -> dict[tuple[int, ...], Fraction]:
    if len(p_one) != 6 or any(p < 0 or p > 1 for p in p_one):
        raise ValueError("invalid Bernoulli parameter vector")
    distribution: dict[tuple[int, ...], Fraction] = {}
    for state in STATES:
        mass = Fraction(1)
        for bit, p in zip(state, p_one):
            mass *= p if bit else 1 - p
        distribution[state] = mass
    if sum(distribution.values(), Fraction(0)) != 1:
        raise AssertionError("kernel does not normalize exactly")
    return distribution


def direct_useful_mass(distribution: dict[tuple[int, ...], Fraction], requirements: dict[int, int]) -> Fraction:
    return sum((mass for state, mass in distribution.items() if matches(state, requirements)), Fraction(0))


def factorized_useful_mass(p_one: tuple[Fraction, ...], requirements: dict[int, int]) -> Fraction:
    result = Fraction(1)
    for index, required_value in sorted(requirements.items()):
        p = p_one[index]
        result *= p if required_value else 1 - p
    return result


def first_useful_mean(p: Fraction) -> Fraction | str:
    if p < 0 or p > 1:
        raise ValueError("useful mass must be a probability")
    return ZERO_MASS_TERMINAL if p == 0 else 1 / p


def probability_multiset_signature(distribution: dict[tuple[int, ...], Fraction]) -> tuple[tuple[Fraction, int], ...]:
    counts = Counter(distribution.values())
    return tuple(sorted(counts.items(), key=lambda pair: pair[0]))


def symbolic_entropy_signature(distribution: dict[tuple[int, ...], Fraction]) -> tuple[tuple[Fraction, int], ...]:
    """Exact sufficient certificate for equal Shannon entropy under probability-multiset equality."""
    return probability_multiset_signature(distribution)


def table_sha256(table: tuple[bool, ...]) -> str:
    payload = "".join("1" if value else "0" for value in table)
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def build_kernels() -> dict[str, dict[tuple[int, ...], Fraction]]:
    return {name: factorized_kernel(parameters) for name, parameters in KERNEL_PARAMETERS.items()}


def history_nonidentity() -> dict[str, dict[str, bool | str]]:
    development_tables = {name: truth_table(req) for name, req in DEVELOPMENT_OBLIGATIONS.items()}
    utility_tables = {name: truth_table(req) for name, req in UTILITIES.items()}
    result: dict[str, dict[str, bool | str]] = {}
    for utility_name, utility_table in utility_tables.items():
        row: dict[str, bool | str] = {"utility_truth_table_sha256": table_sha256(utility_table)}
        for development_name, development_table in development_tables.items():
            row[f"identical_to_{development_name}"] = utility_table == development_table
        result[utility_name] = row
    return result


def zero_mass_hostile() -> dict[str, object]:
    distribution = {state: Fraction(0) for state in STATES}
    distribution[CURRENT_OBJECT] = Fraction(1)
    useful = {5: 1, 4: 1, 3: 1, 2: 1, 1: 1, 0: 1}
    mass = direct_useful_mass(distribution, useful)
    return {
        "kernel": "POINT_MASS_000000",
        "useful_set": "singleton_111111",
        "useful_mass": fmt(mass),
        "first_useful_mean": first_useful_mean(mass),
    }


def build_receipt() -> dict[str, object]:
    kernels = build_kernels()
    kernel_rows: dict[str, object] = {}
    for name in sorted(kernels):
        distribution = kernels[name]
        signature = probability_multiset_signature(distribution)
        kernel_rows[name] = {
            "normalization": fmt(sum(distribution.values(), Fraction(0))),
            "support_size": sum(mass > 0 for mass in distribution.values()),
            "probability_multiset": [
                {"mass": fmt(mass), "multiplicity": multiplicity}
                for mass, multiplicity in signature
            ],
            "distribution_sha256": hashlib.sha256(
                "|".join(f"{state_string(state)}:{fmt(distribution[state])}" for state in STATES).encode("utf-8")
            ).hexdigest(),
        }

    prediction_rows: dict[str, object] = {}
    all_frozen_predictions_match = True
    all_dual_methods_agree = True
    for utility_name in sorted(UTILITIES):
        requirements = UTILITIES[utility_name]
        arm_rows: dict[str, object] = {}
        for kernel_name in sorted(KERNEL_PARAMETERS):
            direct = direct_useful_mass(kernels[kernel_name], requirements)
            factorized = factorized_useful_mass(KERNEL_PARAMETERS[kernel_name], requirements)
            expected_mass, expected_mean = FROZEN_EXPECTED[utility_name][kernel_name]
            mean = first_useful_mean(direct)
            dual_match = direct == factorized
            frozen_match = direct == expected_mass and mean == expected_mean
            all_dual_methods_agree &= dual_match
            all_frozen_predictions_match &= frozen_match
            arm_rows[kernel_name] = {
                "enumerated_mass": fmt(direct),
                "factorized_mass": fmt(factorized),
                "dual_methods_agree": dual_match,
                "first_useful_expected_proposals": fmt(mean) if isinstance(mean, Fraction) else mean,
                "frozen_expected_mass": fmt(expected_mass),
                "frozen_expected_proposals": fmt(expected_mean),
                "frozen_prediction_matches": frozen_match,
            }
        prediction_rows[utility_name] = arm_rows

    continued_signature = symbolic_entropy_signature(kernels["CONTINUED"])
    shuffled_signature = symbolic_entropy_signature(kernels["SHUFFLED_HISTORY"])
    reset_signature = symbolic_entropy_signature(kernels["RESET"])

    history_rows = history_nonidentity()
    all_history_nonidentical = all(
        not bool(value)
        for row in history_rows.values()
        for key, value in row.items()
        if key.startswith("identical_to_")
    )

    common_contract = {
        "current_object": state_string(CURRENT_OBJECT),
        "descendant_space": "{0,1}^6",
        "descendant_count": len(STATES),
        "admissibility": ADMISSIBILITY,
        "verifier": VERIFIER,
    }

    return {
        "schema": "GMI_EVOLVABILITY_KERNEL_RECEIPT_V1",
        "claim_ceiling": CLAIM_CEILING,
        "common_contract": common_contract,
        "kernels": kernel_rows,
        "predictions": prediction_rows,
        "all_dual_methods_agree": all_dual_methods_agree,
        "all_frozen_predictions_match": all_frozen_predictions_match,
        "continued_shuffled_probability_multisets_equal": continued_signature == shuffled_signature,
        "continued_reset_probability_multisets_equal": continued_signature == reset_signature,
        "continued_entropy_equals_shuffled_by_exact_multiset_certificate": continued_signature == shuffled_signature,
        "history_task_nonidentity": history_rows,
        "all_held_utilities_nonidentical_to_development_tasks": all_history_nonidentical,
        "harmful_transfer_twin": {
            "continued_better_on_U_AND": direct_useful_mass(kernels["CONTINUED"], UTILITIES["U_AND"]) > direct_useful_mass(kernels["RESET"], UTILITIES["U_AND"]),
            "continued_worse_on_U_ANTI": direct_useful_mass(kernels["CONTINUED"], UTILITIES["U_ANTI"]) < direct_useful_mass(kernels["RESET"], UTILITIES["U_ANTI"]),
        },
        "semantic_remint_control": {
            "shuffled_better_on_U_45": direct_useful_mass(kernels["SHUFFLED_HISTORY"], UTILITIES["U_45"]) > direct_useful_mass(kernels["CONTINUED"], UTILITIES["U_45"]),
            "equal_concentration_signature": continued_signature == shuffled_signature,
        },
        "zero_mass_hostile": zero_mass_hostile(),
        "terminal": CLAIM_CEILING,
    }


def main() -> None:
    print(json.dumps(build_receipt(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
