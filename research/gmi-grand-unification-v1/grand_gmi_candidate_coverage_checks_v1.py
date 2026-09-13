#!/usr/bin/env python3
"""Exact checks for CANDIDATE_UNIVERSE_COVERAGE_CORRECTION_V1.

DC-4 makes every family verdict relative to the registered candidate universe
unless a separate completeness theorem covers the relevant physical
realizations. These checks decide coverage on a fully enumerated finite register
with total Boolean structural predicates. They do not decide universal coverage
on arbitrary infinite populations; bounded controls expose that distinction.

The registered instance is imported from the morphology phase-law checker, so
the derived bounds here are the same objects, not restated numbers.
"""

import json
import pathlib
import types
from itertools import product

HERE = pathlib.Path(__file__).resolve().parent


def _load(name):
    """Load a sibling checker by path.

    The capsule replays each checker with -I, which implies -P, so the script
    directory is not on sys.path and a plain import would fail. Compile the
    pinned source bytes directly instead of accepting cached bytecode.
    """
    source = HERE / f"{name}.py"
    module = types.ModuleType(name)
    module.__file__ = str(source)
    exec(compile(source.read_bytes(), str(source), "exec"), module.__dict__)
    return module


PL = _load("grand_gmi_morphology_phase_law_checks_v1")

COUPLING = True


def admitted_allocations():
    """The physically legal, adequate allocations of the registered instance."""
    return [a for a in PL.enumerate_allocations() if PL.satisfies_necessities(a, COUPLING)]


def sigma_residue(alloc):
    """The complement class: everything the two registered predicates miss."""
    return not PL.sigma_neural(alloc) and not PL.sigma_non_neural(alloc)


COVERED_CLASSES = dict(PL.FAMILIES)
COMPLETE_CLASSES = {**PL.FAMILIES, "RESIDUE": sigma_residue}


def covers(classes, population):
    """CU-1: coverage is validity of the disjunction of the predicates."""
    uncovered = []
    for a in population:
        membership = [sigma(a) for sigma in classes.values()]
        if any(type(value) is not bool for value in membership):
            raise ValueError("class predicates must return explicit Booleans")
        if not any(membership):
            uncovered.append(a)
    return not uncovered, uncovered


def check_finite_coverage_is_decidable_and_fails_for_two_classes():
    """The two registered classes do not cover the admitted population."""
    population = admitted_allocations()
    complete, uncovered = covers(COVERED_CLASSES, population)
    if complete:
        raise AssertionError("the two registered classes unexpectedly cover")
    full, still_uncovered = covers(COMPLETE_CLASSES, population)
    if not full or still_uncovered:
        raise AssertionError("adding the complement class did not complete the cover")
    # Coverage by the complement class is a logical dichotomy, not a list: the
    # disjunction is valid on every allocation whatsoever, admitted or not.
    for values in product(PL.GRID, repeat=len(PL.COORDINATES)):
        alloc = dict(zip(PL.COORDINATES, values))
        if not any(sigma(alloc) for sigma in COMPLETE_CLASSES.values()):
            raise AssertionError("the completed cover is not a valid dichotomy")
    return {
        "admitted_allocations": len(population),
        "registered_classes": sorted(COVERED_CLASSES),
        "registered_classes_cover": False,
        "uncovered_admitted_allocations": len(uncovered),
        "completed_classes": sorted(COMPLETE_CLASSES),
        "completed_classes_cover": True,
        "complement_cover_is_a_valid_dichotomy": True,
        "decision_scope": "complete finite grid; total Boolean predicates",
    }


def derived_bounds(classes):
    return {name: PL.derived_lower_bound(sigma, COUPLING)[0] for name, sigma in classes.items()}


def verdict(uppers, lower):
    """Robust domination of every other registered class."""
    selected = []
    for family, upper in uppers.items():
        if upper is None:
            continue
        if all(upper < lower[other] for other in lower if other != family):
            selected.append(family)
    if len(selected) > 1:
        raise AssertionError("two families robustly selected at once")
    return selected[0] if selected else "UNDECIDED_FROM_CURRENT_EVIDENCE"


def check_uncovered_residue_defeats_a_verdict():
    """CU-3: a verdict over an incomplete cover is not a verdict over physics.

    The non-neural construction of cost 16 strictly excludes the rival neural
    class (bound 18), while its own class lower bound is 14. Registering the complement class — a structural region
    nobody had enumerated — withdraws that verdict, because its derived bound
    is below the construction's cost.
    """
    witness = {"NON_NEURAL": 16}
    covered = derived_bounds(COVERED_CLASSES)
    complete = derived_bounds(COMPLETE_CLASSES)
    verdict_covered = verdict(witness, covered)
    verdict_complete = verdict(witness, complete)
    if verdict_covered != "NON_NEURAL":
        raise AssertionError("the incomplete-cover verdict is not reproduced")
    if verdict_complete != "UNDECIDED_FROM_CURRENT_EVIDENCE":
        raise AssertionError("the completed cover should withdraw the verdict")
    # The residue is populated by admitted allocations, so this is not vacuous.
    witnesses = [a for a in admitted_allocations()
                 if sigma_residue(a) and PL.scalar(PL.accounted(a)) < witness["NON_NEURAL"]]
    if not witnesses:
        raise AssertionError("no admitted residue allocation beats the construction")
    cheapest = min(PL.scalar(PL.accounted(a)) for a in witnesses)
    if cheapest != complete["RESIDUE"]:
        raise AssertionError("residue bound is not attained by an admitted allocation")
    return {
        "registered_construction_upper_bound": witness["NON_NEURAL"],
        "bounds_over_registered_classes": covered,
        "bounds_over_completed_classes": complete,
        "verdict_over_registered_classes": verdict_covered,
        "verdict_over_completed_classes": verdict_complete,
        "admitted_residue_allocations_beating_the_construction": len(witnesses),
        "cheapest_admitted_residue_scalar": cheapest,
        "verdict_without_coverage_is_not_about_physics": True,
    }


def check_complete_cover_gives_a_universal_verdict():
    """CU-2: with a proved cover, a dominating witness excludes all of physics.

    A construction in the residue class attaining its derived bound dominates
    every other covered class, so no admitted machine of the instance — built
    or unbuilt — can beat it.
    """
    complete = derived_bounds(COMPLETE_CLASSES)
    residue_upper = complete["RESIDUE"]
    result = verdict({"RESIDUE": residue_upper}, complete)
    if result != "RESIDUE":
        raise AssertionError("the residue construction should be robustly selected")
    # Check the conclusion directly against every admitted allocation.
    dominated = 0
    for alloc in admitted_allocations():
        if sigma_residue(alloc):
            continue
        if PL.scalar(PL.accounted(alloc)) <= residue_upper:
            raise AssertionError("an admitted allocation beats the selected witness")
        dominated += 1
    return {
        "residue_construction_upper_bound": residue_upper,
        "bounds_over_completed_classes": complete,
        "verdict": result,
        "admitted_allocations_outside_the_selected_class": dominated,
        "no_admitted_allocation_beats_the_witness": True,
        "universal_at_registered_instance_only": True,
    }


def check_non_upgradability_without_coverage():
    """CU-3b: without a coverage proof no verdict can be upgraded.

    Two extensions preserve evidence restricted to the initial classes but
    give different certified outcomes. That restricted evidence alone does
    not generally determine the enlarged verdict; residue evidence remains usable.
    """
    witness = {"NON_NEURAL": 16}
    covered = derived_bounds(COVERED_CLASSES)

    def extend(name, sigma):
        extended = {**COVERED_CLASSES, name: sigma}
        return verdict(witness, derived_bounds(extended))

    # An extension whose members are all expensive keeps the verdict.
    expensive = extend("EXPENSIVE_EXOTIC",
                       lambda a: sigma_residue(a) and a["t1"] >= 6 and a["t2"] >= 6)
    # An extension containing a cheap member withdraws it.
    cheap = extend("CHEAP_EXOTIC", sigma_residue)
    if expensive != "NON_NEURAL":
        raise AssertionError("the expensive extension should keep the verdict")
    if cheap != "UNDECIDED_FROM_CURRENT_EVIDENCE":
        raise AssertionError("the cheap extension should withdraw the verdict")
    return {
        "bounds_over_registered_classes": covered,
        "verdict_under_expensive_extension": expensive,
        "verdict_under_cheap_extension": cheap,
        "initial_class_evidence_alone_does_not_decide_extensions": True,
        "required_report": "ROBUST_WITHIN_COVERED_CLASSES_WITH_OPEN_RESIDUE",
    }


def check_component_cover_does_not_lift_to_composites():
    """CU-4: coverage must be proved at the resolution of the verdict.

    Two predicates covering every single-site cost do not cover two-site
    machines when they are lifted by conjunction across the sites.
    """
    single = ({"name": "IDLE", "sigma": lambda t: t == 0},
              {"name": "ACTIVE", "sigma": lambda t: t >= 1})
    for t in PL.GRID:
        if not any(row["sigma"](t) for row in single):
            raise AssertionError("the single-site predicates do not cover")
    lifted = {row["name"]: (lambda r: lambda a: r["sigma"](a["t1"]) and r["sigma"](a["t2"]))(row)
              for row in single}
    population = [dict(zip(PL.COORDINATES, v))
                  for v in product(PL.GRID, repeat=len(PL.COORDINATES))]
    complete, uncovered = covers(lifted, population)
    if complete:
        raise AssertionError("the lifted conjunction unexpectedly covers")
    mixed = {"w1": 2, "w2": 1, "t1": 0, "t2": 1}
    if any(sigma(mixed) for sigma in lifted.values()):
        raise AssertionError("the mixed witness is covered after all")
    return {
        "single_site_predicates_cover_every_site_cost": True,
        "lifted_conjunction_covers_composites": False,
        "uncovered_composite_allocations": len(uncovered),
        "mixed_witness": mixed,
        "coverage_must_be_proved_at_the_verdict_resolution": True,
    }


def check_overlapping_classes_take_the_stronger_bound():
    """CU-5: a cover may overlap; a member of two classes obeys both bounds."""
    wide_neural = {"NEURAL": PL.sigma_neural, "WIDE": lambda a: a["w1"] >= a["w2"]}
    bounds = derived_bounds(wide_neural)
    shared = [a for a in admitted_allocations()
              if all(sigma(a) for sigma in wide_neural.values())]
    if not shared:
        raise AssertionError("the two classes do not overlap on admitted allocations")
    strongest = max(bounds.values())
    for alloc in shared:
        value = PL.scalar(PL.accounted(alloc))
        if value < strongest:
            raise AssertionError("an overlapping member violates the stronger bound")
    return {
        "overlapping_class_bounds": bounds,
        "strongest_applicable_bound": strongest,
        "admitted_allocations_in_both_classes": len(shared),
        "overlap_weakens_nothing": True,
    }



def _not_halted_within(table, steps):
    """Bounded deterministic execution; None marks a halting state."""
    state = 0
    for step in range(steps + 1):
        if table[state] is None:
            return False
        if step < steps:
            state = table[state]
    return True


def check_finite_prefix_does_not_certify_universal_coverage():
    """Finite controls only; the nonhalting reduction is a separate proof."""
    witnesses = []
    for limit in range(8):
        loop = (0,)
        late_halt = tuple(range(1, limit + 2)) + (None,)
        loop_class = {"RUNNING": lambda n: _not_halted_within(loop, n)}
        late_class = {"RUNNING": lambda n: _not_halted_within(late_halt, n)}
        prefix = tuple(range(limit + 1))
        if not covers(loop_class, prefix)[0] or not covers(late_class, prefix)[0]:
            raise AssertionError("bounded indistinguishability control failed")
        if any(loop_class["RUNNING"](n) != late_class["RUNNING"](n) for n in prefix):
            raise AssertionError("the registered prefix should agree")
        full_prefix = tuple(range(limit + 2))
        if not covers(loop_class, full_prefix)[0]:
            raise AssertionError("the actual loop control should remain covered")
        covered, missing = covers(late_class, full_prefix)
        if covered or missing != [limit + 1]:
            raise AssertionError("later halting counterexample was not detected")
        witnesses.append(limit + 1)
    return {
        "bounded_controls": len(witnesses),
        "first_uncovered_indices": witnesses,
        "finite_prefix_never_used_as_infinite_certificate": True,
        "unrestricted_coverage_decidability_claimed": False,
        "sound_supplied_proof_is_a_separate_sufficient_route": True,
    }

def run():
    return {
        "terminal": "GRAND_GMI_CANDIDATE_UNIVERSE_COVERAGE_GREEN_AT_FINITE_SCOPE",
        "finite_coverage_decision": check_finite_coverage_is_decidable_and_fails_for_two_classes(),
        "finite_prefix_boundary": check_finite_prefix_does_not_certify_universal_coverage(),
        "uncovered_residue_defeats_a_verdict": check_uncovered_residue_defeats_a_verdict(),
        "complete_cover_gives_a_universal_verdict":
            check_complete_cover_gives_a_universal_verdict(),
        "non_upgradability_without_coverage": check_non_upgradability_without_coverage(),
        "component_cover_does_not_lift": check_component_cover_does_not_lift_to_composites(),
        "overlapping_classes_take_the_stronger_bound":
            check_overlapping_classes_take_the_stronger_bound(),
        "physical_machine_enumeration_claimed": False,
        "claim_ceiling": "finite coverage decision; supplied-proof route; no unrestricted universal decider",
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
