#!/usr/bin/env python3
"""Exact checks for CONTINUOUS_LIFT_BOUNDARY_THEOREM_V1.

The recursive audit records the continuous/quantum realization obligation as
requiring compactness, measurability, effective descriptions, admitted
operations and a measured resource contract. These checks determine which
parts of the derivation layer transfer to an instance without those
properties, and gate the rest behind a decidable contract predicate.

Witnesses use exact rational arithmetic. A rational feasible set with no
minimum stands in for a non-compact instance; nothing here measures a physical
continuum or performs an experiment on any substrate.
"""

import json
from fractions import Fraction

SAMPLE_DEPTH = 64


class ContractError(ValueError):
    """A registered continuous instance has not discharged a contract field."""


# --- The lifted program ----------------------------------------------------


def declared_infimum(name):
    """The registered greatest lower bound of a feasible cost set."""
    return {"open_above_one": Fraction(1), "harmonic_tail": Fraction(1)}[name]


def sample(name, depth=SAMPLE_DEPTH):
    """Finitely many members of an infinite registered feasible cost set."""
    if name == "open_above_one":
        # {1 + 1/n : n >= 1}: bounded below by 1, never equal to it.
        return [Fraction(1) + Fraction(1, n) for n in range(1, depth + 1)]
    if name == "harmonic_tail":
        # The same set enumerated from a deeper index, to show that a finite
        # observation window never pins the infimum.
        return [Fraction(1) + Fraction(1, n) for n in range(depth, 2 * depth + 1)]
    raise ContractError(f"unknown registered set {name!r}")


def check_lower_bound_lifts_without_regularity():
    """CL-1. PL-2 needs membership and monotonicity, nothing more.

    The derived bound is an infimum, which exists in the extended reals for
    any nonempty set bounded below. No compactness, measurability or effective
    description is used, so the lower-bound half of PL-2 transfers verbatim to
    an infinite instance.
    """
    bound = declared_infimum("open_above_one")
    members = sample("open_above_one")
    for value in members:
        if value < bound:
            raise AssertionError("a registered member is below the declared infimum")
    # Monotone accounting still transports it: real cost dominates accounted.
    overheads = [Fraction(0), Fraction(1, 7), Fraction(3)]
    transported = 0
    for value in members:
        for overhead in overheads:
            if value + overhead < bound:
                raise AssertionError("a transported cost fell below the bound")
            transported += 1
    return {
        "declared_infimum": str(bound),
        "members_sampled": len(members),
        "transported_comparisons": transported,
        "every_member_respects_the_bound": True,
        "lower_bound_requires_no_regularity": True,
    }


def check_attainment_fails_without_compactness():
    """CL-2. Without attainment the PL-3b tightness certificate is unavailable.

    `inf` is 1 and no member equals it, so no construction can certify the
    bound as tight. The epistemic/physical classification of an abstention is
    therefore structurally unavailable in such an instance, not merely unknown.
    """
    bound = declared_infimum("open_above_one")
    members = sample("open_above_one")
    if any(value == bound for value in members):
        raise AssertionError("the infimum is attained in the sample")
    gaps = [value - bound for value in members]
    if min(gaps) <= 0:
        raise AssertionError("a nonpositive gap appeared")
    # The gap shrinks without limit, so no positive slack certifies tightness
    # either: the deeper sample is strictly closer and still not equal.
    deeper = sample("harmonic_tail")
    if min(v - bound for v in deeper) >= min(gaps):
        raise AssertionError("the deeper sample is not strictly closer")
    tightness_certificate_available = any(value == bound for value in members + deeper)
    return {
        "declared_infimum": str(bound),
        "smallest_sampled_gap": str(min(gaps)),
        "smallest_deeper_gap": str(min(v - bound for v in deeper)),
        "infimum_attained": False,
        "tightness_certificate_available": tightness_certificate_available,
        "abstention_cannot_be_classified_without_attainment": True,
    }


def check_no_finite_window_determines_the_bound():
    """CL-3. Without an effective description a finite window overestimates.

    Every finite observation window yields a strictly larger minimum than the
    true infimum, and widening the window strictly lowers it. So a bound read
    off finitely many observed realizations is not the derived bound.
    """
    bound = declared_infimum("open_above_one")
    rows = {}
    previous = None
    for depth in (2, 4, 8, 16, 32):
        observed = min(sample("open_above_one", depth))
        if observed <= bound:
            raise AssertionError("a finite window reached the infimum")
        if previous is not None and not observed < previous:
            raise AssertionError("widening the window did not lower the minimum")
        previous = observed
        rows[str(depth)] = str(observed)
    return {
        "declared_infimum": str(bound),
        "window_minima": rows,
        "every_finite_window_strictly_overestimates": True,
        "widening_strictly_improves": True,
        "finite_observation_does_not_determine_the_derived_bound": True,
    }


def check_accounting_soundness_still_load_bearing():
    """CL-4. PL-2 still needs the accounting map to undercharge."""
    bound = declared_infimum("open_above_one")
    member = Fraction(1) + Fraction(1, 3)
    if member < bound:
        raise AssertionError("the witness member is below the bound")
    undercharged = member - Fraction(1, 2)
    if undercharged >= bound:
        raise AssertionError("the undercharged witness does not break the bound")
    return {
        "declared_infimum": str(bound),
        "sound_cost": str(member),
        "undercharged_cost": str(undercharged),
        "undercharged_accounting_breaks_the_bound": True,
        "measured_resource_contract_is_required_for_transport": True,
    }


# --- The contract predicate ------------------------------------------------

CONTRACT_FIELDS = (
    "attainment_witness",
    "measurable_response_kernels",
    "effective_description",
    "admitted_operations",
    "measured_resource_contract",
)

AVAILABLE_WITH = {
    "PL2_derived_lower_bound": ("measured_resource_contract",),
    "PL3b_tightness_certificate": ("attainment_witness",),
    "computable_derived_bound": ("effective_description",),
    "well_defined_response_quotient": ("measurable_response_kernels",),
    "legal_process_composition": ("admitted_operations",),
}


def validate_contract(declaration):
    """Reject a declaration that is not a complete Boolean contract."""
    if type(declaration) is not dict:
        raise ContractError("contract declaration must be an object")
    missing = [name for name in CONTRACT_FIELDS if name not in declaration]
    if missing:
        raise ContractError(f"undeclared contract fields: {sorted(missing)}")
    extra = [name for name in declaration if name not in CONTRACT_FIELDS]
    if extra:
        raise ContractError(f"unregistered contract fields: {sorted(extra)}")
    for name in CONTRACT_FIELDS:
        if type(declaration[name]) is not bool:
            raise ContractError(f"{name}: contract field must be Boolean")
    return declaration


def available_results(declaration):
    """Which results the registered contract actually licenses."""
    validate_contract(declaration)
    verdict = {}
    for result, required in AVAILABLE_WITH.items():
        absent = sorted(name for name in required if not declaration[name])
        verdict[result] = "AVAILABLE" if not absent else f"WITHHELD_MISSING_{'_AND_'.join(absent)}"
    return verdict


def check_contract_predicate_gates_each_result():
    """CL-5. Each contract field gates exactly the results that need it."""
    full = {name: True for name in CONTRACT_FIELDS}
    if any(v != "AVAILABLE" for v in available_results(full).values()):
        raise AssertionError("a complete contract withheld a result")
    per_field = {}
    for name in CONTRACT_FIELDS:
        partial = dict(full)
        partial[name] = False
        verdict = available_results(partial)
        withheld = sorted(k for k, v in verdict.items() if v != "AVAILABLE")
        expected = sorted(k for k, required in AVAILABLE_WITH.items() if name in required)
        if withheld != expected:
            raise AssertionError(f"{name}: gated {withheld}, expected {expected}")
        per_field[name] = withheld
    # An instance with no contract at all licenses nothing.
    empty = {name: False for name in CONTRACT_FIELDS}
    if any(v == "AVAILABLE" for v in available_results(empty).values()):
        raise AssertionError("an empty contract licensed a result")
    # Malformed declarations abstain with a typed error rather than defaulting.
    rejected = 0
    for bad in ({}, {"attainment_witness": True},
                {**full, "unregistered": True},
                {**full, "effective_description": "yes"}):
        try:
            available_results(bad)
        except ContractError:
            rejected += 1
    if rejected != 4:
        raise AssertionError("a malformed contract declaration was accepted")
    return {
        "registered_contract_fields": list(CONTRACT_FIELDS),
        "complete_contract_licenses_all_results": True,
        "results_withheld_per_missing_field": per_field,
        "empty_contract_licenses_nothing": True,
        "malformed_declarations_rejected": rejected,
    }


def run():
    return {
        "terminal": "GRAND_GMI_CONTINUOUS_LIFT_BOUNDARY_GREEN_AT_FINITE_SCOPE",
        "lower_bound_lifts_without_regularity": check_lower_bound_lifts_without_regularity(),
        "attainment_fails_without_compactness": check_attainment_fails_without_compactness(),
        "no_finite_window_determines_the_bound": check_no_finite_window_determines_the_bound(),
        "accounting_soundness_still_load_bearing":
            check_accounting_soundness_still_load_bearing(),
        "contract_predicate_gates_each_result": check_contract_predicate_gates_each_result(),
        "physical_continuum_measured": False,
        "claim_ceiling": "which registered results transfer; no experiment on any substrate",
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
