#!/usr/bin/env python3
import json
from pathlib import Path

import numpy as np


def exact_risk(n, d, sigma, beta_norm):
    if d < n - 1:
        return sigma ** 2 * d / (n - d - 1)
    if d > n + 1:
        return (1 - n / d) * beta_norm ** 2 + sigma ** 2 * n / (d - n - 1)
    raise ValueError("expectation is not finite/registered at the interpolation boundary")


def main():
    rng = np.random.default_rng(12345)
    sigma = 0.5
    beta_norm = 1.5
    trials = 500
    cells = []
    violations = 0
    max_relative_error = 0.0

    for n in (20, 40):
        for d in (5, 10, 15, 25, 30, 50, 60):
            if not (d < n - 1 or d > n + 1):
                continue
            beta = np.zeros(d)
            beta[0] = beta_norm
            risks = []
            for _ in range(trials):
                X = rng.normal(size=(n, d))
                eps = rng.normal(scale=sigma, size=n)
                y = X @ beta + eps
                beta_hat = np.linalg.pinv(X) @ y
                risks.append(float(np.sum((beta_hat - beta) ** 2)))
            empirical = float(np.mean(risks))
            theory = float(exact_risk(n, d, sigma, beta_norm))
            relative_error = abs(empirical - theory) / theory
            max_relative_error = max(max_relative_error, relative_error)
            if relative_error > 0.10:
                violations += 1
            cells.append({"n": n, "d": d, "theory": theory, "empirical": empirical, "relative_error": relative_error})

    receipt = {
        "artifact": "GMI_LINEAR_DOUBLE_DESCENT_RECEIPT_V1",
        "status": "MONTE_CARLO_CALIBRATION_OF_EXACT_EXPECTATION",
        "runner": "run_gmi_linear_double_descent_v1.py",
        "seed": 12345,
        "trials_per_cell": trials,
        "cells": len(cells),
        "sigma": sigma,
        "beta_norm": beta_norm,
        "max_relative_error": max_relative_error,
        "cells_over_10pct_relative_error": violations,
        "results": cells,
        "claim_ceiling": "Isotropic Gaussian linear teacher-student calibration only; not a nonlinear neural-network result.",
        "terminal": "LINEAR_DOUBLE_DESCENT_CALIBRATION_GREEN" if violations == 0 else "LINEAR_DOUBLE_DESCENT_CALIBRATION_RED"
    }
    out = Path(__file__).with_name("GMI_LINEAR_DOUBLE_DESCENT_RECEIPT_V1.json")
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    if violations:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
