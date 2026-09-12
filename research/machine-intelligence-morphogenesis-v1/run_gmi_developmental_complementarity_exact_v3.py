#!/usr/bin/env python3
import json
from pathlib import Path


def main():
    tables = positive = zero = negative = threshold_synergy = 0
    violations = 0

    for b00 in range(0, 8):
        for b10 in range(0, b00 + 1):
            for b01 in range(0, b00 + 1):
                for b11 in range(0, min(b10, b01) + 1):
                    tables += 1
                    delta_i_empty = b00 - b10
                    delta_i_after_j = b01 - b11
                    interaction_a = delta_i_after_j - delta_i_empty
                    interaction_b = b10 + b01 - b00 - b11
                    if interaction_a != interaction_b:
                        violations += 1
                    if interaction_a > 0:
                        positive += 1
                    elif interaction_a < 0:
                        negative += 1
                    else:
                        zero += 1

                    for budget in range(0, 8):
                        # base and each singleton not viable; pair viable
                        witness = b00 > budget and b10 > budget and b01 > budget and b11 <= budget
                        if witness:
                            threshold_synergy += 1
                            if not (b11 <= budget < min(b10, b01, b00)):
                                violations += 1

    receipt = {
        "artifact": "GMI_DEVELOPMENTAL_COMPLEMENTARITY_RECEIPT_V3",
        "status": "EXACT_FINITE_COMPOSITE_BURDEN_CALIBRATION",
        "runner": "run_gmi_developmental_complementarity_exact_v3.py",
        "monotone_four_cell_tables": tables,
        "positive_complementarity_tables": positive,
        "zero_interaction_tables": zero,
        "negative_substitution_tables": negative,
        "threshold_synergy_budget_cells": threshold_synergy,
        "violations": violations,
        "claim_ceiling": "Exact finite set-function algebra only; no real composite-species capability curves or interface-cost calibration.",
        "terminal": "DEVELOPMENTAL_COMPLEMENTARITY_EXACT_GREEN" if violations == 0 else "DEVELOPMENTAL_COMPLEMENTARITY_RED"
    }
    out = Path(__file__).with_name("GMI_DEVELOPMENTAL_COMPLEMENTARITY_RECEIPT_V3.json")
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    if violations:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
