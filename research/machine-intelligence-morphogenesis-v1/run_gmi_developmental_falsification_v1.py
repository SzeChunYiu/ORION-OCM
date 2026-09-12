#!/usr/bin/env python3
"""Exact counterexamples, not protected learning experiments. Old files stay frozen."""
from fractions import Fraction as F
import json

BASE = "f211f99a9aaefcfcca05850e1930885701358bcc"

def run():
    upper_a, lower_b, upper_b, threshold = F(3, 4), F(1, 2), F(1, 8), F(1)
    actual_a, actual_b = F(0), lower_b
    premises = {
        "pure_A_meets_A_upper": actual_a <= upper_a,
        "every_pure_A_meets_B_lower_singleton_class": actual_b >= lower_b,
        "upper_A_plus_lower_B_exceeds_threshold": upper_a + lower_b > threshold,
        "composite_upper_meets_threshold": upper_a + upper_b <= threshold,
        "composition_preserves_A": True,
    }
    matrix = [[1, 0], [0, 1]]
    pointwise = sum(max(row[i] for row in matrix) for i in range(2)) / 2
    joint = max(sum(row) / 2 for row in matrix)
    return {
        "source_head": BASE,
        "receipt_type": "EXACT_FALSIFICATION_NOT_EMPIRICAL_HOLDOUT",
        "DP1": {
            "source_file": "GMI_DEVELOPMENTAL_POTENTIAL_AND_CRITICAL_BURDEN_V1.md",
            "source_atom": "Theorem DP-1, upper_A + lower_B used as a total-loss lower bound",
            "parameters": {"epsilon_A": "3/4", "delta_B": "1/2", "epsilon_B": "1/8", "L_star": "1", "actual_L_A": "0", "actual_L_B": "1/2"},
            "premises": premises,
            "all_premises_true": all(premises.values()),
            "pure_A_total_loss": str(actual_a + actual_b),
            "claimed_impossibility_false": actual_a + actual_b <= threshold,
            "verdict": "FALSIFIED",
        },
        "joint_capability": {
            "source_atom": "Pointwise reachable envelope interpreted as jointly attainable breadth",
            "legal_fixed_state_success_matrix": matrix,
            "uniform_obligation_weights": ["1/2", "1/2"],
            "pointwise_breadth": str(F(pointwise)),
            "maximum_single_state_breadth": str(F(joint)),
            "verdict": "INTERPRETATION_FALSIFIED_NOT_POINTWISE_DEFINITION",
            "scope": "One developed state must serve both obligations. A paid router/composite must itself be in the reachable set.",
        },
        "original_files_modified": False,
    }

if __name__ == "__main__":
    result = run()
    assert result["DP1"]["all_premises_true"]
    assert result["DP1"]["claimed_impossibility_false"]
    print(json.dumps(result, indent=2, sort_keys=True))
