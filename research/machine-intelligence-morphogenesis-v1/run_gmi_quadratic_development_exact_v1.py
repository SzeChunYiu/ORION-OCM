#!/usr/bin/env python3
import json
from fractions import Fraction
from pathlib import Path


def main():
    cases = 0
    for mu in range(1, 7):
        for L in range(mu, 9):
            eta = Fraction(2, L + mu)
            rho = Fraction(L - mu, L + mu)
            contractions = [abs(Fraction(1) - eta * lam) for lam in range(mu, L + 1)]
            assert max(contractions) == rho
            assert Fraction(0) < eta < Fraction(2, L)
            cases += 1

    receipt = {
        "artifact": "GMI_QUADRATIC_DEVELOPMENT_EXACT_RECEIPT_V1",
        "status": "EXACT_FINITE_CALIBRATION",
        "runner": "run_gmi_quadratic_development_exact_v1.py",
        "spectral_interval_cases": cases,
        "mu_min": 1,
        "mu_max": 6,
        "L_max": 8,
        "checks": {
            "optimal_constant_step_equalizes_endpoint_contractions": True,
            "rho_equals_kappa_minus_one_over_kappa_plus_one": True,
            "optimal_step_inside_convergence_interval": True
        },
        "claim_ceiling": "Exact rational calibration of the strictly-convex quadratic gradient-development law only; nonlinear/nonconvex neural reachability remains open.",
        "terminal": "QUADRATIC_DEVELOPMENT_BASE_EXACT_GREEN"
    }
    out = Path(__file__).with_name("GMI_QUADRATIC_DEVELOPMENT_EXACT_RECEIPT_V1.json")
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
