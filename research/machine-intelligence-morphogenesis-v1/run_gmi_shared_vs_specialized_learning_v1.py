#!/usr/bin/env python3
import json
from pathlib import Path

import numpy as np


def main():
    rng = np.random.default_rng(20260912)
    ms = [2, 4, 8]
    Ns = [2, 4, 8, 16, 32]
    sigmas = [0.1, 0.5, 1.0]
    taus = [0.0, 0.05, 0.1, 0.25, 0.5, 1.0]
    reps = 3000

    cells = 0
    ties = 0
    non_tie_matches = 0
    non_tie_cells = 0
    abs_shared = []
    abs_separate = []

    for m in ms:
        raw = np.arange(m, dtype=float) - (m - 1) / 2
        raw = raw / np.sqrt(np.mean(raw**2))
        for N in Ns:
            for sigma in sigmas:
                for tau in taus:
                    true_mu = 1.0 + tau * raw
                    noise = rng.normal(0.0, sigma, size=(reps, m, N))
                    obs = true_mu[None, :, None] + noise

                    separate_hat = obs.mean(axis=2)
                    shared_hat = obs.mean(axis=(1, 2))[:, None]

                    mse_separate = np.mean((separate_hat - true_mu[None, :]) ** 2, axis=1)
                    mse_shared = np.mean((shared_hat - true_mu[None, :]) ** 2, axis=1)

                    empirical_separate = float(mse_separate.mean())
                    empirical_shared = float(mse_shared.mean())
                    theory_separate = sigma**2 / N
                    theory_shared = tau**2 + sigma**2 / (m * N)

                    abs_shared.append(abs(empirical_shared - theory_shared))
                    abs_separate.append(abs(empirical_separate - theory_separate))

                    if abs(theory_shared - theory_separate) < 1e-12:
                        ties += 1
                    else:
                        non_tie_cells += 1
                        predicted = "shared" if theory_shared < theory_separate else "separate"
                        empirical = "shared" if empirical_shared < empirical_separate else "separate"
                        assert predicted == empirical
                        non_tie_matches += 1

                    cells += 1

    assert cells == 270
    assert ties == 4
    assert non_tie_cells == 266
    assert non_tie_matches == non_tie_cells
    assert max(abs_shared) < 0.02
    assert max(abs_separate) < 0.02

    receipt = {
        "artifact": "GMI_SHARED_VS_SPECIALIZED_LEARNING_RECEIPT_V1",
        "status": "EXECUTED_SYNTHETIC_MONTE_CARLO_CALIBRATION",
        "runner": "run_gmi_shared_vs_specialized_learning_v1.py",
        "seed": 20260912,
        "replicates_per_cell": reps,
        "grid": {
            "m": ms,
            "N": Ns,
            "sigma": sigmas,
            "tau": taus
        },
        "cells": cells,
        "theoretical_tie_cells": ties,
        "non_tie_cells": non_tie_cells,
        "non_tie_winner_matches": non_tie_matches,
        "max_absolute_monte_carlo_error": {
            "shared": max(abs_shared),
            "separate": max(abs_separate)
        },
        "mean_absolute_monte_carlo_error": {
            "shared": sum(abs_shared) / len(abs_shared),
            "separate": sum(abs_separate) / len(abs_separate)
        },
        "checks": {
            "all_non_tie_cells_match_exact_phase_prediction": True,
            "shared_error_matches_tau2_plus_sigma2_over_mN": True,
            "separate_error_matches_sigma2_over_N": True
        },
        "claim_ceiling": "Synthetic scalar-context finite-data calibration only. Does not establish nonlinear neural MoE superiority or real-world K5 closure.",
        "terminal": "SHARED_SPECIALIZED_FINITE_DATA_PHASE_GREEN"
    }

    out = Path(__file__).with_name("GMI_SHARED_VS_SPECIALIZED_LEARNING_RECEIPT_V1.json")
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
