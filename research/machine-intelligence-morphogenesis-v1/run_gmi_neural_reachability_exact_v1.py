#!/usr/bin/env python3
import json
from fractions import Fraction
from pathlib import Path


def main():
    relu_cases = 0
    for w0 in [Fraction(-k, 2) for k in range(1, 9)]:
        w = w0
        for _ in range(10):
            grad = Fraction(0) if w < 0 else (w - 1)
            w = w - Fraction(1, 2) * grad
        assert w == w0
        relu_cases += 1

    leaky_cases = 0
    for alpha in (Fraction(1, 2), Fraction(1, 3), Fraction(2, 3)):
        for eta in (Fraction(1, 2), Fraction(1), Fraction(3, 2)):
            if not (0 < eta * alpha * alpha < 1):
                continue
            for w0 in [Fraction(-k, 2) for k in range(1, 9)]:
                w = w0
                crossed = False
                for _ in range(500):
                    grad = alpha * (alpha * w - 1) if w < 0 else (w - 1)
                    w = w - eta * grad
                    if w >= 0:
                        crossed = True
                        break
                assert crossed
                leaky_cases += 1

    receipt = {
        "artifact": "GMI_NEURAL_REACHABILITY_EXACT_RECEIPT_V1",
        "status": "EXACT_FINITE_CALIBRATION",
        "runner": "run_gmi_neural_reachability_exact_v1.py",
        "relu_dead_initializations_checked": relu_cases,
        "leaky_negative_region_crossing_cases": leaky_cases,
        "checks": {
            "negative_relu_initialization_has_zero_gradient_and_remains_stuck": True,
            "leaky_activation_under_registered_steps_crosses_out_of_negative_region": True
        },
        "claim_ceiling": "Exact one-parameter nonlinear development calibration only; does not establish general neural optimization reachability.",
        "terminal": "NEURAL_REACHABILITY_MICRO_EXACT_GREEN"
    }
    out = Path(__file__).with_name("GMI_NEURAL_REACHABILITY_EXACT_RECEIPT_V1.json")
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
