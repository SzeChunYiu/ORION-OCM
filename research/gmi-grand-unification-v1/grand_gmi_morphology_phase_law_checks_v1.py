#!/usr/bin/env python3
"""Exact checks for MORPHOLOGY_PHASE_LAW_DERIVATION_V1.

The family-phase layer compares registered bound functions. These checks
exercise the layer that *derives* a family-conditioned lower bound from the
proved cut and transformation necessities plus a declared resource accounting
map, by exhaustive enumeration of a finite registered allocation grid.

All numbers are synthetic theorem witnesses. Nothing here measures a real
substrate, and the derivation is one sided: it produces lower bounds only.
"""

import json
from itertools import product

GRID = range(8)
COORDINATES = ("w1", "w2", "t1", "t2")

# --- Registered instance ---------------------------------------------------
# Two semantic cuts carry widths w1, w2; two transformation sites cost t1, t2.
# The proved necessities are lower bounds on those coordinates. A coordinate
# with no proved lower bound admits non-negativity only.
PROVED_NECESSITIES = {"w1": 2, "w2": 1, "t1": 3}

# A joint necessity discovered later: site-1 computation and cut-1 width cannot
# both be small. The relaxed program that omits it is still sound, just looser.
COUPLING_NECESSITY = 8  # w1 + t1 >= 8


def accounted(alloc):
    """Declared resource accounting map, monotone in every allocation."""
    return {"memory": alloc["w1"] + alloc["w2"], "compute": alloc["t1"] + alloc["t2"]}


def scalar(resources):
    """Declared scalar selection functional, monotone in every coordinate."""
    return resources["memory"] + 2 * resources["compute"]


def satisfies_necessities(alloc, coupling):
    if any(alloc[name] < bound for name, bound in PROVED_NECESSITIES.items()):
        return False
    if coupling and alloc["w1"] + alloc["t1"] < COUPLING_NECESSITY:
        return False
    return True


# --- Structural family predicates -----------------------------------------
# A family is a structural predicate on morphology descriptors, never a name.
def sigma_neural(alloc):
    """One shared kernel charged at both sites, with a widest-first carrier."""
    return alloc["t1"] == alloc["t2"] and alloc["w1"] >= alloc["w2"]


def sigma_neural_heterogeneous(alloc):
    """An enlarged neural class that drops the shared-kernel restriction."""
    return alloc["w1"] >= alloc["w2"]


def sigma_non_neural(alloc):
    """A lookup at site 2: no local computation, full key crosses cut 2."""
    return alloc["t2"] == 0 and alloc["w2"] >= 3


FAMILIES = {
    "NEURAL": sigma_neural,
    "NON_NEURAL": sigma_non_neural,
}


def enumerate_allocations():
    for values in product(GRID, repeat=len(COORDINATES)):
        yield dict(zip(COORDINATES, values))


def derived_lower_bound(sigma, coupling):
    """PL-2: minimize the declared scalar over necessities and structure only.

    Every other feasibility constraint is dropped, so this is a relaxation and
    the value is a valid lower bound for every member of the structure class,
    including members nobody has constructed.
    """
    feasible = [a for a in enumerate_allocations()
                if satisfies_necessities(a, coupling) and sigma(a)]
    if not feasible:
        return None, 0
    return min(scalar(accounted(a)) for a in feasible), len(feasible)


def check_derived_bounds():
    """The relaxed accounting program yields the expected exact bounds."""
    rows = {}
    for coupling in (False, True):
        state = "with_coupling" if coupling else "without_coupling"
        rows[state] = {}
        for family, sigma in FAMILIES.items():
            value, count = derived_lower_bound(sigma, coupling)
            rows[state][family] = {"derived_lower_bound": value, "feasible_allocations": count}
    expected = {
        "without_coupling": {"NEURAL": 15, "NON_NEURAL": 11},
        "with_coupling": {"NEURAL": 18, "NON_NEURAL": 14},
    }
    for state, families in expected.items():
        for family, value in families.items():
            if rows[state][family]["derived_lower_bound"] != value:
                raise AssertionError(f"{state}/{family}: derived bound changed")
    return {
        "allocation_grid_size": len(GRID) ** len(COORDINATES),
        "states": rows,
        "bounds_derived_from_necessities_not_registered_as_inputs": True,
    }


# --- PL-2 soundness: accounting must undercharge ---------------------------
# A machine is a registered allocation plus the resources actually spent. The
# accounting map is sound for it when the real resources dominate the accounted
# ones coordinatewise.
MACHINES = (
    {"id": "neural_shared_tight", "family": "NEURAL",
     "alloc": {"w1": 5, "w2": 1, "t1": 3, "t2": 3}, "overhead": {"memory": 0, "compute": 0}},
    {"id": "neural_shared_padded", "family": "NEURAL",
     "alloc": {"w1": 5, "w2": 2, "t1": 4, "t2": 4}, "overhead": {"memory": 3, "compute": 1}},
    {"id": "non_neural_lookup", "family": "NON_NEURAL",
     "alloc": {"w1": 5, "w2": 3, "t1": 3, "t2": 0}, "overhead": {"memory": 0, "compute": 0}},
    {"id": "non_neural_padded", "family": "NON_NEURAL",
     "alloc": {"w1": 6, "w2": 4, "t1": 5, "t2": 0}, "overhead": {"memory": 2, "compute": 2}},
)

UNSOUND_MACHINE = {
    "id": "overcharging_accounting", "family": "NEURAL",
    "alloc": {"w1": 5, "w2": 1, "t1": 3, "t2": 3}, "overhead": {"memory": -4, "compute": -2},
}


def real_resources(machine):
    base = accounted(machine["alloc"])
    return {name: base[name] + machine["overhead"][name] for name in base}


def check_transport_to_real_machines():
    """PL-2: a sound accounting map transports the bound to real machines."""
    bounds = {family: derived_lower_bound(sigma, True)[0] for family, sigma in FAMILIES.items()}
    checked = 0
    for machine in MACHINES:
        alloc = machine["alloc"]
        if not satisfies_necessities(alloc, True):
            raise AssertionError(f"{machine['id']}: registered machine violates a necessity")
        if not FAMILIES[machine["family"]](alloc):
            raise AssertionError(f"{machine['id']}: machine escapes its structural predicate")
        spent = real_resources(machine)
        base = accounted(alloc)
        if any(spent[name] < base[name] for name in base):
            raise AssertionError(f"{machine['id']}: accounting is not sound")
        if scalar(spent) < bounds[machine["family"]]:
            raise AssertionError(f"{machine['id']}: derived bound violated")
        checked += 1
    # The accounting-soundness hypothesis is load bearing.
    spent = real_resources(UNSOUND_MACHINE)
    base = accounted(UNSOUND_MACHINE["alloc"])
    if not any(spent[name] < base[name] for name in base):
        raise AssertionError("the accounting floor does not exceed actual resources")
    if scalar(spent) >= bounds["NEURAL"]:
        raise AssertionError("the unsound witness does not break the bound")
    return {
        "derived_bounds_used": bounds,
        "sound_machines_checked": checked,
        "every_sound_machine_respects_its_derived_bound": True,
        "actual_resources": spent,
        "accounted_resources": base,
        "actual_scalar_cost": scalar(spent),
        "overcharging_accounting_scalar": scalar(base),
        "overcharging_accounting_breaks_the_bound": True,
    }


# --- PL-3: relaxation looseness and two causes of abstention ---------------


def robust_exclusion(upper_a, lower_b):
    """FP-1 in scalar form on well-formed registered values."""
    return upper_a < lower_b


def check_relaxation_looseness_is_epistemic():
    """A loose relaxation can abstain where the refined evidence excludes.

    The registered non-neural construction costs 16. Against the relaxed
    neural bound 15 the comparison abstains; against the refined neural bound
    18 it robustly excludes the neural class. The physics did not change.
    """
    loose = derived_lower_bound(sigma_neural, False)[0]
    refined = derived_lower_bound(sigma_neural, True)[0]
    witness_upper = 16
    if not refined > loose:
        raise AssertionError("adding a valid necessity did not raise the bound")
    verdict_loose = ("NON_NEURAL" if robust_exclusion(witness_upper, loose)
                     else "UNDECIDED_FROM_CURRENT_EVIDENCE")
    verdict_refined = ("NON_NEURAL" if robust_exclusion(witness_upper, refined)
                       else "UNDECIDED_FROM_CURRENT_EVIDENCE")
    if verdict_loose != "UNDECIDED_FROM_CURRENT_EVIDENCE":
        raise AssertionError("the loose relaxation should abstain")
    if verdict_refined != "NON_NEURAL":
        raise AssertionError("the refined necessity should exclude the neural class")
    return {
        "relaxed_neural_lower_bound": loose,
        "refined_neural_lower_bound": refined,
        "registered_non_neural_construction_upper_bound": witness_upper,
        "verdict_from_relaxed_bound": verdict_loose,
        "verdict_from_refined_bound": verdict_refined,
        "abstention_was_epistemic_not_physical": True,
    }


def check_tight_bounds_make_abstention_physical():
    """PL-3b: when every compared bound is attained, the verdict is physical."""
    # Separate complete finite control, not the allocation-grid instance.
    candidates = {"NEURAL": (14, 17), "NON_NEURAL": (14, 20)}
    tight = {family: (min(costs), min(costs)) for family, costs in candidates.items()}
    for family, (lo, hi) in tight.items():
        if lo != hi:
            raise AssertionError(f"{family}: interval is not tight")
    true_optima = {family: min(costs) for family, costs in candidates.items()}
    interval_verdict = "UNDECIDED_FROM_CURRENT_EVIDENCE"
    for family, (_, hi) in tight.items():
        if all(robust_exclusion(hi, lo) for other, (lo, _) in tight.items() if other != family):
            interval_verdict = family
    best = min(true_optima.values())
    winners = [f for f, v in true_optima.items() if v == best]
    optimum_verdict = winners[0] if len(winners) == 1 else "UNDECIDED_FROM_CURRENT_EVIDENCE"
    if interval_verdict != optimum_verdict:
        raise AssertionError("tight intervals disagree with the true optima")
    return {
        "complete_finite_candidate_costs": {f: list(v) for f, v in candidates.items()},
        "tight_intervals": {f: list(v) for f, v in tight.items()},
        "interval_verdict": interval_verdict,
        "true_optimum_verdict": optimum_verdict,
        "tight_bounds_make_the_verdict_physical": True,
    }


# --- PL-4: evidence refines monotonically, candidates do not ---------------


def check_evidence_monotonicity_and_candidate_sensitivity():
    """Adding a necessity is safe; enlarging a structure class is not."""
    for family, sigma in FAMILIES.items():
        loose = derived_lower_bound(sigma, False)[0]
        refined = derived_lower_bound(sigma, True)[0]
        if refined < loose:
            raise AssertionError(f"{family}: a valid necessity lowered the bound")
    restricted = derived_lower_bound(sigma_neural, True)[0]
    enlarged = derived_lower_bound(sigma_neural_heterogeneous, True)[0]
    if enlarged > restricted:
        raise AssertionError("an enlarged structure class raised the bound")
    witness_upper = 16
    verdict_restricted = ("NON_NEURAL" if robust_exclusion(witness_upper, restricted)
                          else "UNDECIDED_FROM_CURRENT_EVIDENCE")
    verdict_enlarged = ("NON_NEURAL" if robust_exclusion(witness_upper, enlarged)
                        else "UNDECIDED_FROM_CURRENT_EVIDENCE")
    if verdict_restricted != "NON_NEURAL":
        raise AssertionError("restricted-class verdict not reproduced")
    if verdict_enlarged != "UNDECIDED_FROM_CURRENT_EVIDENCE":
        raise AssertionError("enlarging the class should withdraw the verdict")
    return {
        "valid_necessities_never_lower_a_derived_bound": True,
        "restricted_neural_lower_bound": restricted,
        "enlarged_neural_lower_bound": enlarged,
        "verdict_under_registered_class": verdict_restricted,
        "verdict_after_class_enlargement": verdict_enlarged,
        "verdict_is_relative_to_the_structure_class": True,
    }


# --- PL-5: the derivation is one sided ------------------------------------


def survivor_from_empty_rivals(relaxations, machines):
    """Sufficient certificate on a complete finite integer-cost machine universe."""
    for machine in machines:
        family = machine["family"]
        if family not in relaxations:
            raise ValueError("actual family is outside the claimed coverage")
        if machine["allocation"] not in relaxations[family]:
            raise ValueError("machine is not covered by its relaxed allocation set")
        if type(machine["cost"]) is not int or machine["cost"] < 0:
            raise ValueError("the finite witness requires nonnegative integer costs")
    if not machines:
        return {"family": None, "status": "NO_SELECTED_REALIZATION", "selected_families": []}
    best = min(m["cost"] for m in machines)
    selected = sorted({m["family"] for m in machines if m["cost"] == best})
    possible = [f for f, allocations in relaxations.items() if allocations]
    family = possible[0] if len(possible) == 1 else None
    if family is not None and selected != [family]:
        raise AssertionError("empty-rival certificate disagrees with actual finite selection")
    return {"family": family, "status": "SELECTED" if family else "UNRESOLVED",
            "selected_families": selected}


def check_derivation_is_one_sided():
    """PL-5 general insufficiency plus a decisive positive exception."""
    lower = {family: derived_lower_bound(sigma, True)[0] for family, sigma in FAMILIES.items()}
    worlds, winners, comparisons = {}, {}, {}
    for name, padding in (("world_a", 2), ("world_b", 6)):
        machines = [dict(MACHINES[0]), dict(MACHINES[2])]
        machines[1]["overhead"] = {"memory": padding, "compute": 0}
        costs = {}
        for machine in machines:
            alloc, family = machine["alloc"], machine["family"]
            if not satisfies_necessities(alloc, True) or not FAMILIES[family](alloc):
                raise AssertionError("world violates the shared relaxed instance")
            actual, floor = real_resources(machine), accounted(alloc)
            if any(actual[k] < floor[k] for k in floor):
                raise AssertionError("world violates accounting soundness")
            costs[family] = scalar(actual)
            if costs[family] < lower[family]:
                raise AssertionError("actual cost violates its derived lower bound")
        worlds[name] = costs
        winners[name] = min(costs, key=costs.get)
        certified = [f for f, upper in costs.items()
                     if all(upper < lo for rival, lo in lower.items() if rival != f)]
        comparisons[name] = certified[0] if certified else "UNDECIDED_FROM_CURRENT_EVIDENCE"
    if winners != {"world_a": "NON_NEURAL", "world_b": "NEURAL"}:
        raise AssertionError("shared-data worlds must have opposite actual optima")
    # X={0,1}, necessity x>=1, predicates A:x=1 and B:x=0.
    relaxed = {"A": {x for x in (0, 1) if x >= 1 and x == 1},
               "B": {x for x in (0, 1) if x >= 1 and x == 0}}
    actual = [{"family": "A", "allocation": 1, "cost": 2}]
    positive = survivor_from_empty_rivals(relaxed, actual)
    empty = survivor_from_empty_rivals(relaxed, [])
    if positive["family"] != "A" or empty["status"] != "NO_SELECTED_REALIZATION":
        raise AssertionError("selection existence is not respected")
    try:
        survivor_from_empty_rivals(relaxed, actual + [{"family": "C", "allocation": 0, "cost": 0}])
    except ValueError:
        coverage_refused = True
    else:
        raise AssertionError("an uncovered cheaper family was silently accepted")
    return {"shared_derived_lower_bounds": lower,
            "complete_world_candidate_costs": worlds, "true_optimal_families": winners,
            "world_a_verdict": comparisons["world_a"], "world_b_verdict": comparisons["world_b"],
            "identical_relaxation_data_do_not_determine_selection_in_general": True,
            "relaxation_yields_lower_bounds_only": True,
            "empty_rival_relaxation": {f: sorted(xs) for f, xs in relaxed.items()},
            "selected_existence_supplied": positive, "empty_actual_world": empty,
            "uncovered_candidate_refused": coverage_refused,
            "numeric_upper_bound_needed_for_empty_rival_exclusion": False}


def run():
    return {
        "terminal": "GRAND_GMI_MORPHOLOGY_PHASE_LAW_SCOPE_REPAIRED_V2_GREEN",
        "derived_bounds": check_derived_bounds(),
        "transport_to_real_machines": check_transport_to_real_machines(),
        "relaxation_looseness_is_epistemic": check_relaxation_looseness_is_epistemic(),
        "tight_bounds_make_abstention_physical": check_tight_bounds_make_abstention_physical(),
        "evidence_monotonicity_and_candidate_sensitivity":
            check_evidence_monotonicity_and_candidate_sensitivity(),
        "derivation_is_one_sided": check_derivation_is_one_sided(),
        "real_substrate_bound_measured": False,
        "claim_ceiling": "finite synthetic lower-bound witnesses; selection generally underdetermined, conditional positive exception retained",
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
