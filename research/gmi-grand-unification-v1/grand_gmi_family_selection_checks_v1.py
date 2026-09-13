#!/usr/bin/env python3
"""Exact finite witnesses for NEURAL_NONNEURAL_FAMILY_SELECTION_THEOREM_V1."""

import json
from itertools import product


def dominates(a, b):
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def inversion_witness():
    substrate_a = {"neural": (2, 2), "program": (5, 3)}
    substrate_b = {"neural": (5, 3), "program": (2, 2)}
    assert dominates(substrate_a["neural"], substrate_a["program"])
    assert dominates(substrate_b["program"], substrate_b["neural"])
    return {
        "substrate_A_selected_family": "neural",
        "substrate_B_selected_family": "program",
        "protected_response_changed": False,
    }


def hybrid_witness():
    region_a = {"neural": (1, 2), "program": (5, 5)}
    region_b = {"neural": (5, 5), "program": (1, 2)}
    assignments = {}
    for fa, fb in product(region_a, region_b):
        assignments[f"{fa}+{fb}"] = tuple(
            x + y for x, y in zip(region_a[fa], region_b[fb])
        )
    winner = assignments["neural+program"]
    for name, profile in assignments.items():
        if name != "neural+program":
            assert dominates(winner, profile)
    return {
        "assignments": {k: list(v) for k, v in assignments.items()},
        "unique_dominating_assignment": "neural+program",
        "hybrid_derived": True,
    }


def main():
    receipt = {
        "terminal": "GRAND_GMI_FAMILY_SELECTION_FINITE_CHECKS_ALL_GREEN",
        "resource_inversion": inversion_witness(),
        "separable_hybrid": hybrid_witness(),
        "scope_boundary": (
            "Synthetic exact resource profiles. Validates family-selection logic only; "
            "does not estimate empirical neural, program, analog, biological, or quantum costs."
        ),
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
