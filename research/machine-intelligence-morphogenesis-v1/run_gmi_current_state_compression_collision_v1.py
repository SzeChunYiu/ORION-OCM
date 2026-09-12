#!/usr/bin/env python3
import json
from pathlib import Path


def main():
    checked = 0
    flips = 0
    violations = 0
    for N in range(4, 13):
        for d in range(1, N):
            for R in (4, 16, 64):
                for c_p in (1, 2):
                    for c_m in (1, 2):
                        compact0 = d + R * c_p
                        memory0 = N + R * c_m
                        if compact0 >= memory0:
                            continue
                        delta0 = memory0 - compact0
                        for U in (1, 2, 4, 8, 16):
                            for rewrite in (N, 2 * N):
                                for local in (1, 2):
                                    for lineage_p in (d, N):
                                        lineage_m = 1
                                        u_p = rewrite + lineage_p
                                        u_m = local + lineage_m
                                        if u_p <= u_m:
                                            continue
                                        compact = compact0 + U * u_p
                                        memory = memory0 + U * u_m
                                        predicted_flip = U * (u_p - u_m) > delta0
                                        actual_flip = memory < compact
                                        checked += 1
                                        flips += int(actual_flip)
                                        if predicted_flip != actual_flip:
                                            violations += 1
    receipt = {
        "artifact": "GMI_CURRENT_STATE_COMPRESSION_COLLISION_RECEIPT_V1",
        "status": "EXACT_FINITE_CALIBRATION",
        "runner": "run_gmi_current_state_compression_collision_v1.py",
        "registered_volatile_cells": checked,
        "lifecycle_flip_cells": flips,
        "nonflip_cells": checked - flips,
        "inequality_violations": violations,
        "claim_ceiling": "Exact two-realization finite cost model; distinguishes developmental context from current-only compression, not from a complete lifecycle-aware parent.",
        "terminal": "CURRENT_STATE_COMPRESSION_COLLISION_EXACT_GREEN" if violations == 0 else "CURRENT_STATE_COMPRESSION_COLLISION_RED"
    }
    out = Path(__file__).with_name("GMI_CURRENT_STATE_COMPRESSION_COLLISION_RECEIPT_V1.json")
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    if violations:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
