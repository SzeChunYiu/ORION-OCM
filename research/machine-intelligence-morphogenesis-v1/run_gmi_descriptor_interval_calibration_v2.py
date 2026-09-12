#!/usr/bin/env python3
import json
import math
from pathlib import Path

import numpy as np


def main():
    rng = np.random.default_rng(20260912)
    n = 512
    delta_i = 0.05 / 3.0
    radius = math.sqrt(math.log(2.0 / delta_i) / (2.0 * n))
    intervals = 0
    covered = 0
    worlds = []

    for i in range(32):
        true_rates = [
            0.02 + 0.96 * ((i * 7) % 31) / 30.0,
            0.01 + 0.49 * ((i * 11) % 31) / 30.0,
            0.05 + 0.90 * ((i * 13) % 31) / 30.0,
        ]
        results = []
        for p in true_rates:
            sample = rng.binomial(1, p, size=n)
            p_hat = float(sample.mean())
            lo = max(0.0, p_hat - radius)
            hi = min(1.0, p_hat + radius)
            ok = lo <= p <= hi
            intervals += 1
            covered += int(ok)
            results.append({"truth": p, "estimate": p_hat, "lo": lo, "hi": hi, "covered": ok})
        worlds.append(results)

    receipt = {
        "artifact": "GMI_DESCRIPTOR_INTERVAL_CALIBRATION_RECEIPT_V2",
        "status": "SYNTHETIC_PREOUTCOME_INTERVAL_CALIBRATION",
        "runner": "run_gmi_descriptor_interval_calibration_v2.py",
        "seed": 20260912,
        "worlds": 32,
        "descriptors_per_world": 3,
        "observations_per_descriptor": n,
        "intervals_checked": intervals,
        "covered": covered,
        "misses": intervals - covered,
        "interval_half_width": radius,
        "claim_ceiling": "IID Bernoulli descriptor coverage only; not full B4 held-family or high-dimensional estimator closure.",
        "terminal": "DESCRIPTOR_INTERVAL_SYNTHETIC_GREEN" if covered == intervals else "DESCRIPTOR_INTERVAL_SYNTHETIC_HAS_MISSES"
    }
    out = Path(__file__).with_name("GMI_DESCRIPTOR_INTERVAL_CALIBRATION_RECEIPT_V2.json")
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
