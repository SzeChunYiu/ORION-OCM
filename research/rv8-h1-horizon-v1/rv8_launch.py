"""Generate SLURM submissions for the RV-8 cell array, high-mix first.

Scheduling only: touches no frozen constant. High-mix cells carry the crossover claim,
so they are submitted first and the decisive part of the surface exists early. --time is
set per cost class from probe_cost.py's measured projection.
"""
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import rv8_horizon as H

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
DRY = "--dry" in sys.argv
OUT = Path(ARGS[0]).resolve()
COST = json.loads(Path(ARGS[1]).read_text()) if len(ARGS) > 1 else None
CONC = int(ARGS[2]) if len(ARGS) > 2 else 120

cells = H.cell_inventory()
groups = {}
for i, c in enumerate(cells):
    cls = "null" if c["arm"] in H.NULL_ARMS else (
        "reduced" if c["arm"] in H.REDUCED_ARMS else "full")
    groups.setdefault((c["mix_idx"], cls), []).append(i)


def hours_for(mix_idx, cls):
    if COST is None:
        return 48
    worst = 0.0
    for key, row in COST["per_task"].items():
        arm = key.split("#")[0]
        k = "null" if arm in H.NULL_ARMS else (
            "reduced" if arm in H.REDUCED_ARMS else "full")
        if k != cls:
            continue
        n = H.N_REDUCED if arm in H.REDUCED_ARMS else H.N_FULL
        for comp in H.COMPOSITIONS:
            t = H.mix_targets(H.MIX_GRID[mix_idx], comp)
            worst = max(worst, n * sum(t[f] * row[f]["sec_per_task"]
                                       for f in ("F1", "F2", "F3")))
    h = max(2, int(worst / 3600.0 * 3.0) + 2)      # 3x margin on the measured mean
    return min(h, 167)                              # lu48 ceiling is 7 days


subs = []
for mix_idx in sorted({k[0] for k in groups}, reverse=True):      # high mix first
    for cls in ("full", "null", "reduced"):
        idx = groups.get((mix_idx, cls))
        if not idx:
            continue
        h = hours_for(mix_idx, cls)
        arr = ",".join(str(i) for i in idx) + "%%%d" % CONC
        cmd = ["sbatch", "-A", "lu2026-2-51", "-p", "lu48", "-n", "1", "-c", "1",
               "--mem-per-cpu=4000", "-t", "%d:00:00" % h,
               "-J", "rv8_%s_m%d" % (cls, mix_idx),
               "--array=" + arr,
               "/projects/hep/fs12/scratch/scyiu-rv8/rv8_array_body.sb"]
        subs.append({"mix_idx": mix_idx, "mix": H.MIX_GRID[mix_idx], "class": cls,
                     "n_cells": len(idx), "hours": h})
        if DRY:
            continue
        r = subprocess.run(cmd, capture_output=True, text=True)
        subs[-1]["stdout"] = r.stdout.strip()
        subs[-1]["stderr"] = r.stderr.strip()
        subs[-1]["rc"] = r.returncode
print(json.dumps(subs, indent=1))
