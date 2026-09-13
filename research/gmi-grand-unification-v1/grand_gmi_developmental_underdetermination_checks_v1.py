#!/usr/bin/env python3
"""Exact checks for DEVELOPMENTAL_UNDERDETERMINATION_THEOREM_V1.

The recursive audit lists a general training theorem and large-scale learning
prediction as open. These checks establish a sharper statement: the reachable
frontier is not a function of the data the rest of the package supplies, so no
theorem of the form "necessities imply the trained outcome" can exist. The
development law is an independent registered input.

All numbers are synthetic theorem witnesses. Nothing here trains a model or
measures a learning process.
"""

import json
from itertools import permutations

UNDECIDED = "UNDECIDED_FROM_CURRENT_EVIDENCE"


def best_by_family(states, profiles, families, reachable):
    """Cheapest reachable profile per family."""
    best = {}
    for state in states:
        if state not in reachable:
            continue
        family = families[state]
        value = profiles[state]
        if family not in best or value < best[family]:
            best[family] = value
    return best


def verdict(best):
    """Family support of the frontier, in the sense DC-4 states a verdict.

    The verdict is the family of every cheapest reachable realization. A tie
    across families is coexistence, reported as abstention.
    """
    if not best:
        return UNDECIDED
    cheapest = min(best.values())
    support = sorted(family for family, value in best.items() if value == cheapest)
    return support[0] if len(support) == 1 else UNDECIDED


def reach(edges, start, budget):
    """States reachable from start in at most `budget` admitted updates."""
    frontier = {start}
    seen = {start}
    for _ in range(budget):
        nxt = set()
        for state in frontier:
            for target in edges.get(state, ()):
                if target not in seen:
                    seen.add(target)
                    nxt.add(target)
        frontier = nxt
        if not frontier:
            break
    return seen


# --- DU-1: identical realization data, different reachable verdicts --------

STATES = ("s0", "a", "b")
PROFILES = {"s0": 10, "a": 5, "b": 3}
FAMILIES = {"s0": "NEURAL", "a": "NEURAL", "b": "NON_NEURAL"}
DEVELOPMENT_LAWS = {
    "D1_grows_neural": {"s0": ("a",)},
    "D2_grows_non_neural": {"s0": ("b",)},
}


def check_realization_data_does_not_determine_reachability():
    """DU-1. Same machines, same profiles, same necessities; different D."""
    results = {}
    for name, edges in DEVELOPMENT_LAWS.items():
        reachable = reach(edges, "s0", 1)
        best = best_by_family(STATES, PROFILES, FAMILIES, reachable)
        results[name] = {
            "reachable_states": sorted(reachable),
            "best_by_family": best,
            "verdict": verdict(best),
        }
    if results["D1_grows_neural"]["verdict"] != "NEURAL":
        raise AssertionError("D1 verdict not reproduced")
    if results["D2_grows_non_neural"]["verdict"] != "NON_NEURAL":
        raise AssertionError("D2 verdict not reproduced")
    # The shared inputs really are shared: state set, profiles and families are
    # single objects used by both laws.
    global_best = best_by_family(STATES, PROFILES, FAMILIES, set(STATES))
    if global_best != {"NEURAL": 5, "NON_NEURAL": 3}:
        raise AssertionError("global attainable data changed")
    return {
        "shared_state_set": list(STATES),
        "shared_profiles": PROFILES,
        "shared_global_best_by_family": global_best,
        "per_development_law": results,
        "reachable_frontier_is_not_a_function_of_realization_data": True,
    }


# --- DU-2: the admitted update set does not determine the reachable set ----

UPDATE_ADMISSION_CAP = 6
UPDATES = {"double": lambda x: x * 2, "add_three": lambda x: x + 3}


def check_schedule_matters_not_just_the_update_set():
    """DU-2. Non-commuting admitted updates make the schedule load bearing."""
    start = 1
    outcomes = {}
    for order in permutations(sorted(UPDATES)):
        value = start
        admitted = True
        for name in order:
            value = UPDATES[name](value)
            if value > UPDATE_ADMISSION_CAP:
                admitted = False
                break
        outcomes["->".join(order)] = {"result": value, "admitted": admitted}
    if outcomes["add_three->double"]["admitted"]:
        raise AssertionError("the rejected schedule was admitted")
    if not outcomes["double->add_three"]["admitted"]:
        raise AssertionError("the admitted schedule was rejected")
    if outcomes["double->add_three"]["result"] == outcomes["add_three->double"]["result"]:
        raise AssertionError("the updates commute, so the witness is vacuous")
    return {
        "admitted_update_set": sorted(UPDATES),
        "admission_cap": UPDATE_ADMISSION_CAP,
        "schedules": outcomes,
        "same_update_set_different_reachable_set": True,
        "registered_development_law_must_fix_its_schedule_semantics": True,
    }


# --- DU-3: reachability raises lower bounds but can destroy a construction --

GLOBAL_PROFILES = {"A_cheap": 2, "A_costly": 9, "B_only": 5}
GLOBAL_FAMILIES = {"A_cheap": "A", "A_costly": "A", "B_only": "B"}
REACHABLE_STATES = {"A_costly", "B_only"}


def check_reachability_asymmetry():
    """DU-3. Restricting to reachable members is safe for lower bounds only.

    A lower bound over a subset is at least the bound over the whole set, so
    reachability evidence behaves like any other valid necessity (PL-4a). An
    upper bound is a construction, and a construction can become unreachable,
    so the verdict is not monotone and can invert.
    """
    states = tuple(GLOBAL_PROFILES)
    global_best = best_by_family(states, GLOBAL_PROFILES, GLOBAL_FAMILIES, set(states))
    reachable_best = best_by_family(states, GLOBAL_PROFILES, GLOBAL_FAMILIES, REACHABLE_STATES)
    for family, value in global_best.items():
        if reachable_best[family] < value:
            raise AssertionError(f"{family}: reachability lowered a bound")
    global_verdict = verdict(global_best)
    reachable_verdict = verdict(reachable_best)
    if global_verdict != "A":
        raise AssertionError("global verdict not reproduced")
    if reachable_verdict != "B":
        raise AssertionError("reachable verdict not reproduced")
    if global_verdict == reachable_verdict:
        raise AssertionError("the witness must inevitably invert")
    return {
        "global_best_by_family": global_best,
        "reachable_best_by_family": reachable_best,
        "global_verdict": global_verdict,
        "reachable_verdict": reachable_verdict,
        "reachability_never_lowers_a_lower_bound": True,
        "reachability_can_invalidate_a_construction": True,
        "verdict_is_not_monotone_under_reachability": True,
    }


# --- DU-4: no finite budget certifies an unbounded-development verdict -----

CHAIN_LENGTH = 8


def chain_instance(length):
    states = tuple(f"s{i}" for i in range(length + 1))
    profiles = {f"s{i}": 10 - i for i in range(length + 1)}
    families = {f"s{i}": ("NEURAL" if i % 2 == 0 else "NON_NEURAL") for i in range(length + 1)}
    edges = {f"s{i}": (f"s{i + 1}",) for i in range(length)}
    return states, profiles, families, edges


def check_no_finite_budget_certifies_the_limit():
    """DU-4. The budget-B verdict alternates and never stabilizes below B = k.

    Each admitted update strictly improves the profile and switches family, so
    every finite budget yields a strictly pessimistic frontier and a verdict
    that the next budget reverses. A bounded-development verdict therefore does
    not extrapolate to unbounded development.
    """
    states, profiles, families, edges = chain_instance(CHAIN_LENGTH)
    rows = {}
    for budget in range(1, CHAIN_LENGTH + 1):
        reachable = reach(edges, "s0", budget)
        best = best_by_family(states, profiles, families, reachable)
        # Key by string so the live object and the frozen receipt agree.
        rows[str(budget)] = {"frontier": min(profiles[s] for s in reachable),
                             "verdict": verdict(best)}
    expected_frontier = {str(b): 10 - b for b in range(1, CHAIN_LENGTH + 1)}
    if {b: row["frontier"] for b, row in rows.items()} != expected_frontier:
        raise AssertionError("the chain frontier is not strictly improving")
    verdicts = [rows[str(b)]["verdict"] for b in range(1, CHAIN_LENGTH + 1)]
    if any(verdicts[i] == verdicts[i + 1] for i in range(len(verdicts) - 1)):
        raise AssertionError("the verdict did not alternate at every budget")
    if len(set(verdicts)) != 2:
        raise AssertionError("the alternation does not cover both families")
    return {
        "chain_length": CHAIN_LENGTH,
        "per_budget": rows,
        "frontier_strictly_improves_with_every_admitted_update": True,
        "verdict_alternates_at_every_budget": True,
        "finite_budget_verdict_does_not_extrapolate": True,
    }


def run():
    return {
        "terminal": "GRAND_GMI_DEVELOPMENTAL_UNDERDETERMINATION_GREEN_AT_FINITE_SCOPE",
        "realization_data_does_not_determine_reachability":
            check_realization_data_does_not_determine_reachability(),
        "schedule_matters_not_just_the_update_set":
            check_schedule_matters_not_just_the_update_set(),
        "reachability_asymmetry": check_reachability_asymmetry(),
        "no_finite_budget_certifies_the_limit": check_no_finite_budget_certifies_the_limit(),
        "learning_process_measured": False,
        "claim_ceiling": "finite synthetic development witnesses; no training or scaling claim",
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
