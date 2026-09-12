#!/usr/bin/env python3
import itertools
import json
from fractions import Fraction
from pathlib import Path


def main():
    target_tuples = 0
    phase_cases = 0
    violations = 0

    for K in range(2, 6):
        for a in itertools.product(range(-2, 3), repeat=K):
            mean = Fraction(sum(a), K)
            shared = Fraction(1, 2 * K) * sum((Fraction(x) - mean) ** 2 for x in a)
            pairwise = Fraction(1, 2 * K * K) * sum(
                (a[i] - a[j]) ** 2 for i in range(K) for j in range(i + 1, K)
            )
            if shared != pairwise:
                violations += 1

            for e_num in range(5):
                e = Fraction(e_num, 4)
                routed = Fraction(1, 2 * K) * sum(
                    Fraction(e, K - 1)
                    * sum((a[j] - a[i]) ** 2 for j in range(K) if j != i)
                    for i in range(K)
                )
                expected = shared * Fraction(2 * e * K, K - 1)
                if routed != expected:
                    violations += 1

                for c_route in (Fraction(0), Fraction(1, 10), Fraction(1, 2), Fraction(1)):
                    for c_maint in (Fraction(0), Fraction(1, 20), Fraction(1, 5)):
                        specialist = routed + c_route + c_maint * K
                        predicted = shared - routed > c_route + c_maint * K
                        if (specialist < shared) != predicted:
                            violations += 1
                        phase_cases += 1
            target_tuples += 1

    receipt = {
        "artifact": "GMI_QUADRATIC_SPECIALIZATION_PHASE_RECEIPT_V1",
        "status": "EXACT_FINITE_CALIBRATION",
        "runner": "run_gmi_quadratic_specialization_phase_v1.py",
        "target_tuples": target_tuples,
        "phase_cases": phase_cases,
        "violations": violations,
        "checks": {
            "shared_heterogeneity_pairwise_identity": violations == 0,
            "symmetric_router_error_identity": violations == 0,
            "specialization_crossover_identity": violations == 0,
        },
        "claim_ceiling": "Exact scalar common-Hessian quadratic calibration only; not a neural MoE or router-learning result.",
        "terminal": "QUADRATIC_SPECIALIZATION_PHASE_EXACT_GREEN" if violations == 0 else "QUADRATIC_SPECIALIZATION_PHASE_RED",
    }
    out = Path(__file__).with_name("GMI_QUADRATIC_SPECIALIZATION_PHASE_RECEIPT_V1.json")
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    if violations:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
