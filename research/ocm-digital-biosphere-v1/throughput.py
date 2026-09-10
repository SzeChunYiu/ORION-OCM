"""Throughput probe used to size the first Earth ensemble. Not a scored Earth."""
from __future__ import annotations

import time

from earth import Earth
from physics import P_DEFAULT


def probe(ticks=200, grid=16, founders=8, seed=0):
    p = dict(P_DEFAULT)
    p["grid_w"] = grid
    p["grid_h"] = grid
    spec = {
        "ecology": "ECO-0",
        "inheritance": "DARWINIAN",
        "founder": "mixed",
        "seed": seed,
    }
    e = Earth(spec, p=p)
    t0 = time.time()
    e.run(ticks)
    dt = max(1e-9, time.time() - t0)
    cen = e.census()
    ticks_per_s = float(ticks) / dt
    cell_ticks = ticks * max(1, (cen["n_alive"] + cen["n_dead"]) // 2)
    return {
        "ticks": ticks,
        "grid": grid,
        "wall_s": round(dt, 4),
        "ticks_per_s": round(ticks_per_s, 2),
        "approx_cell_ticks_per_s": round(cell_ticks / dt, 1),
        "final_n_alive": cen["n_alive"],
        "physics_hash": cen["physics_hash"],
        "note": "Probe only. Does not bind Earth outcomes.",
    }


def recommend_ensemble(ticks_per_s):
    """Conservative LUNARC lu48 core: target ~20 min/Earth including assays."""
    budget_s = 18 * 60
    # Production ticks so one Earth finishes inside the wall budget at 0.4x probe.
    safe = max(1.0, 0.4 * float(ticks_per_s))
    ticks = int(min(12000, max(2000, budget_s * safe)))
    ticks = 1000 * max(2, ticks // 1000)
    return {
        "production_ticks": ticks,
        "assay_every": max(500, ticks // 8),
        "checkpoint_every": max(500, ticks // 4),
        "grid_w": 24,
        "grid_h": 24,
        "n_seeds_primary": 6,
        "array_throttle": 48,
        "qos_production": "normal",
        "partition": "lu48",
        "account": "lu2026-2-51",
    }
