#!/usr/bin/env python3
"""Exact S2G-0 calibration: prefix-tree structure -> proposal prior -> burden.

Parent-owned coding theory. The value is methodological: developmental geometry is
mechanically derived from morphology structure rather than assigned by hand.
"""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).with_name("EXACT_STRUCTURE_TO_GEOMETRY_PREFIX_V1.json")

BALANCED_DEPTHS = (2, 2, 2, 2)
BIASED_DEPTHS = (1, 2, 3, 3)  # Kraft equality: 1/2 + 1/4 + 1/8 + 1/8 = 1


def kraft(depths: tuple[int, ...]) -> float:
    return sum(2.0 ** (-d) for d in depths)


def prior_from_depths(depths: tuple[int, ...]) -> tuple[float, ...]:
    z = kraft(depths)
    return tuple((2.0 ** (-d)) / z for d in depths)


def ecology(p: float) -> tuple[float, float, float, float]:
    return (p / 2.0, p / 2.0, (1.0 - p) / 2.0, (1.0 - p) / 2.0)


def expected_depth(depths: tuple[int, ...], p: float) -> float:
    return sum(prob * d for prob, d in zip(ecology(p), depths))


def phase_threshold(horizon: float, biased_build_cost: float) -> float:
    # balanced expected depth = 2
    # biased expected depth = 3 - 1.5 p
    # B + H(3 - 1.5p) = H*2
    return (1.0 + biased_build_cost / horizon) / 1.5


def build_receipt() -> dict:
    assert abs(kraft(BALANCED_DEPTHS) - 1.0) < 1e-12
    assert abs(kraft(BIASED_DEPTHS) - 1.0) < 1e-12
    q_bal = prior_from_depths(BALANCED_DEPTHS)
    q_bias = prior_from_depths(BIASED_DEPTHS)
    assert q_bal == (0.25, 0.25, 0.25, 0.25)
    assert q_bias == (0.5, 0.25, 0.125, 0.125)

    build_cost = 1.0
    rows = []
    for h in (1, 2, 4, 8, 16, 64, 256):
        p_star = phase_threshold(h, build_cost)
        rows.append({
            "horizon": h,
            "biased_build_cost_bits": build_cost,
            "p_star": p_star,
            "biased_can_win_for_p_in_[0,1]": p_star <= 1.0,
        })

    for p in (0.0, 0.5, 2.0 / 3.0, 1.0):
        b = expected_depth(BALANCED_DEPTHS, p)
        s = expected_depth(BIASED_DEPTHS, p)
        assert abs(b - 2.0) < 1e-12
        assert abs(s - (3.0 - 1.5 * p)) < 1e-12

    return {
        "schema": "ExactStructureToGeometryPrefixV1",
        "morphology_structures": {
            "BALANCED": {"leaf_depths": list(BALANCED_DEPTHS)},
            "BIASED": {"leaf_depths": list(BIASED_DEPTHS)},
        },
        "derived_proposal_priors": {
            "BALANCED": list(q_bal),
            "BIASED": list(q_bias),
        },
        "ecology": "P_p=[p/2,p/2,(1-p)/2,(1-p)/2]",
        "derived_expected_burden_bits": {
            "BALANCED": "2",
            "BIASED": "3 - 1.5 p",
        },
        "lifetime_boundary_with_biased_build_cost_B": "p*(H,B)=(1+B/H)/1.5",
        "rows_B_equals_1": rows,
        "interpretation": [
            "Proposal probabilities are derived from tree/code structure by Kraft weights; they are not assigned independently.",
            "The ecology-dependent expected proposal/code burden follows exactly from that structure.",
            "A build cost creates a horizon-dependent morphology phase boundary.",
            "This is standard prefix-coding/information theory and is used only to calibrate the structure-to-geometry methodology."
        ],
        "terminal": "STRUCTURE_TO_GEOMETRY_EXACT_PREFIX_CALIBRATION__CODING_PARENT",
        "claim_ceiling": "exact structure->prior->burden->phase derivation in a parent-owned coding model"
    }


def main() -> None:
    r = build_receipt()
    OUT.write_text(json.dumps(r, indent=2) + "\n")
    print(r["terminal"])


if __name__ == "__main__":
    main()
