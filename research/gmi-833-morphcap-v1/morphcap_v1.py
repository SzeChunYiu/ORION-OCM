#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from itertools import permutations, product
import json

CLAIM_CEILING = "GMI_MORPHOLOGY_AND_CAPABILITY_OBJECTS_AT_REGISTERED_FINITE_SCOPE"
FORBIDDEN_PROMOTIONS = [
    "UNIVERSAL_MORPHOLOGY_ONTOLOGY",
    "ALL_MACHINE_SPECIES_CLASSIFIED",
    "ALL_CAPABILITY_CEILINGS_REPROVED",
    "REAL_WORLD_CAPABILITY_CEILING",
    "UNIVERSAL_INTELLIGENCE_MEASURE",
    "COMPLETE_GMI",
]


def canonical_mechanism(machine):
    states = tuple(machine["states"])
    actions = tuple(machine["actions"])
    interventions = tuple(machine["interventions"])
    representations = []
    for perm in permutations(range(len(states))):
        f = {states[i]: perm[i] for i in range(len(states))}
        rep = (
            f[machine["initial"]],
            actions,
            interventions,
            tuple(sorted((f[s], machine["output"][s]) for s in states)),
            tuple(sorted((f[s], a, f[machine["transition"][(s, a)]]) for s in states for a in actions)),
            tuple(sorted((f[s], i, machine["intervention_response"][(s, i)]) for s in states for i in interventions)),
            tuple(machine["resources"]),
            tuple(sorted((f[a], f[b]) for a, b in machine["development_edges"])),
        )
        representations.append(rep)
    return min(representations, key=repr)


def morphology_equivalent(left, right):
    return canonical_mechanism(left) == canonical_mechanism(right)


def run_word(machine, word):
    state = machine["initial"]
    for action in word:
        state = machine["transition"][(state, action)]
    return machine["output"][state]


def capability_value(machine, contract):
    numerator = Fraction(0)
    denominator = Fraction(0)
    for task in contract["tasks"]:
        weight = Fraction(task["weight"])
        denominator += weight
        success = run_word(machine, tuple(task["word"])) == task["target"]
        numerator += weight * int(success)
    if denominator <= 0:
        raise ValueError("capability contract requires positive total weight")
    return numerator / denominator


def resource_feasible(resources, budget):
    return len(resources) == len(budget) and all(r <= b for r, b in zip(resources, budget))


def contract_satisfied(machine, contract):
    return (
        resource_feasible(tuple(machine["resources"]), tuple(contract["budget"]))
        and capability_value(machine, contract) >= Fraction(contract["threshold"])
    )


def capability_region(machine, contracts):
    return tuple(contract["id"] for contract in contracts if contract_satisfied(machine, contract))


def finite_ceiling(candidates, budget):
    feasible = [
        Fraction(row["score"])
        for row in candidates
        if resource_feasible(tuple(row["resources"]), tuple(budget))
    ]
    return max(feasible) if feasible else None


def hidden_world_score(p_action1):
    p = Fraction(p_action1)
    return Fraction(1, 2) * (1 - p) + Fraction(1, 2) * p


def revealed_world_score(p_action1_given_w0, p_action1_given_w1):
    p0 = Fraction(p_action1_given_w0)
    p1 = Fraction(p_action1_given_w1)
    return Fraction(1, 2) * (1 - p0) + Fraction(1, 2) * p1


def witness_machines():
    base = {
        "states": ("A", "B"),
        "actions": ("flip", "stay"),
        "interventions": ("probe",),
        "initial": "A",
        "output": {"A": 0, "B": 1},
        "transition": {
            ("A", "flip"): "B", ("A", "stay"): "A",
            ("B", "flip"): "A", ("B", "stay"): "B",
        },
        "intervention_response": {
            ("A", "probe"): 0,
            ("B", "probe"): 1,
        },
        "resources": (3, 2),
        "development_edges": {("A", "B")},
    }
    renamed = {
        "states": ("x", "y"),
        "actions": ("flip", "stay"),
        "interventions": ("probe",),
        "initial": "x",
        "output": {"x": 0, "y": 1},
        "transition": {
            ("x", "flip"): "y", ("x", "stay"): "x",
            ("y", "flip"): "x", ("y", "stay"): "y",
        },
        "intervention_response": {
            ("x", "probe"): 0,
            ("y", "probe"): 1,
        },
        "resources": (3, 2),
        "development_edges": {("x", "y")},
    }
    renamed2 = {
        "states": ("left", "right"),
        "actions": ("flip", "stay"),
        "interventions": ("probe",),
        "initial": "left",
        "output": {"left": 0, "right": 1},
        "transition": {
            ("left", "flip"): "right", ("left", "stay"): "left",
            ("right", "flip"): "left", ("right", "stay"): "right",
        },
        "intervention_response": {
            ("left", "probe"): 0,
            ("right", "probe"): 1,
        },
        "resources": (3, 2),
        "development_edges": {("left", "right")},
    }
    resource_twin = dict(base)
    resource_twin["resources"] = (4, 2)
    intervention_twin = dict(base)
    intervention_twin["intervention_response"] = {
        ("A", "probe"): 1,
        ("B", "probe"): 1,
    }
    return base, renamed, renamed2, resource_twin, intervention_twin


def witness_contracts():
    return (
        {
            "id": "identity_and_flip",
            "tasks": (
                {"word": (), "target": 0, "weight": 1},
                {"word": ("flip",), "target": 1, "weight": 1},
            ),
            "budget": (3, 2),
            "threshold": Fraction(1),
        },
        {
            "id": "double_flip",
            "tasks": (
                {"word": ("flip", "flip"), "target": 0, "weight": 1},
            ),
            "budget": (5, 3),
            "threshold": Fraction(1),
        },
    )


def capability_monotonicity_witness():
    candidates = (
        {"id": "c1", "score": Fraction(1, 4), "resources": (1, 1)},
        {"id": "c2", "score": Fraction(3, 4), "resources": (2, 1)},
        {"id": "c3", "score": Fraction(1), "resources": (4, 2)},
    )
    budgets = ((1, 1), (2, 1), (4, 2))
    ceilings = tuple(finite_ceiling(candidates, b) for b in budgets)
    class_small = candidates[:2]
    class_large = candidates
    class_ceiling_small = finite_ceiling(class_small, (4, 2))
    class_ceiling_large = finite_ceiling(class_large, (4, 2))
    return {
        "budgets": budgets,
        "ceilings": ceilings,
        "class_ceiling_small": class_ceiling_small,
        "class_ceiling_large": class_ceiling_large,
    }


def information_ceiling_witness():
    grid = tuple(Fraction(k, 32) for k in range(33))
    hidden = tuple(hidden_world_score(p) for p in grid)
    revealed = tuple(
        revealed_world_score(p0, p1)
        for p0 in grid
        for p1 in grid
    )
    return {
        "grid_points_hidden": len(grid),
        "grid_points_revealed": len(grid) ** 2,
        "hidden_unique_scores": tuple(sorted(set(hidden))),
        "hidden_ceiling": max(hidden),
        "revealed_ceiling": max(revealed),
        "revealed_argmax_exists": any(score == 1 for score in revealed),
    }


def jsonable(obj):
    if isinstance(obj, Fraction):
        return f"{obj.numerator}/{obj.denominator}"
    if isinstance(obj, dict):
        return {str(k): jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (tuple, list, set)):
        return [jsonable(v) for v in obj]
    return obj


def build_receipt():
    base, renamed, renamed2, resource_twin, intervention_twin = witness_machines()
    contracts = witness_contracts()
    cap_mono = capability_monotonicity_witness()
    info = information_ceiling_witness()

    equivalence_checks = {
        "reflexive": morphology_equivalent(base, base),
        "symmetric": morphology_equivalent(base, renamed) and morphology_equivalent(renamed, base),
        "transitive": (
            morphology_equivalent(base, renamed)
            and morphology_equivalent(renamed, renamed2)
            and morphology_equivalent(base, renamed2)
        ),
        "state_renaming_invariant": morphology_equivalent(base, renamed),
        "resource_twin_rejected": not morphology_equivalent(base, resource_twin),
        "intervention_twin_rejected": not morphology_equivalent(base, intervention_twin),
        "behavior_equal_resource_twin": all(
            run_word(base, word) == run_word(resource_twin, word)
            for word in ((), ("flip",), ("stay",), ("flip", "flip"), ("stay", "flip"))
        ),
    }
    base_region = capability_region(base, contracts)
    renamed_region = capability_region(renamed, contracts)
    resource_region = capability_region(resource_twin, contracts)

    checks = {
        **equivalence_checks,
        "equivalent_capability_regions_equal": base_region == renamed_region,
        "resource_difference_can_change_capability_region": base_region != resource_region,
        "budget_relaxation_monotone": all(
            cap_mono["ceilings"][i] <= cap_mono["ceilings"][i + 1]
            for i in range(len(cap_mono["ceilings"]) - 1)
        ),
        "class_relaxation_monotone": cap_mono["class_ceiling_small"] <= cap_mono["class_ceiling_large"],
        "hidden_world_all_policies_half": info["hidden_unique_scores"] == (Fraction(1, 2),),
        "hidden_world_ceiling_half": info["hidden_ceiling"] == Fraction(1, 2),
        "revealed_world_ceiling_one": info["revealed_ceiling"] == Fraction(1),
        "revealed_world_positive_control_attained": info["revealed_argmax_exists"],
    }

    return jsonable({
        "schema": "GMI_833_MORPHCAP_RESULT_V1",
        "verdict": "GREEN" if all(checks.values()) else "RED",
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "checks": checks,
        "morphology": {
            "base_fingerprint": repr(canonical_mechanism(base)),
            "renamed_fingerprint": repr(canonical_mechanism(renamed)),
            "resource_twin_fingerprint": repr(canonical_mechanism(resource_twin)),
            "legacy_machine_species_definition": "QUOTIENT_CLASS_UNDER_REGISTERED_MORPHOLOGY_EQUIVALENCE",
            "paper_term": "COMPUTATIONAL_MECHANISM_EQUIVALENCE_CLASS",
        },
        "capability": {
            "base_region": base_region,
            "renamed_region": renamed_region,
            "resource_twin_region": resource_region,
            "monotonicity": cap_mono,
        },
        "information_ceiling": info,
    })


def canonical_json(receipt):
    return json.dumps(receipt, indent=2, sort_keys=True) + "\n"


def main():
    receipt = build_receipt()
    print(canonical_json(receipt), end="")
    return 0 if receipt["verdict"] == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
