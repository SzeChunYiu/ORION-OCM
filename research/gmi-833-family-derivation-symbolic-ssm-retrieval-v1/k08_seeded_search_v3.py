"""K08 revival v3 - seeded blind search on B_EP (GMI #833 Row 194).

Registered lever: raise the pooled blind T3 budget with guided neutral
seeding from the constructive 4-cell latch machine (REVIVAL_V2 rows/
Retrieval-augmented systems.). Pooled budget 8 seeds x 2e5 evals. Champion
verified on all 56 episodes by the INDEPENDENT exact evaluator, then the
three K08 clauses re-executed. Output: k08_seeded_search_v3.json.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import machinery_v1 as M
import proc2_v1 as P2
import posthoc_adjudicate_v1 as A

SHA = "5b385f0edfa035b28940f5dd982e0c69991a2ce6e0175e4c693073add26899f0"

bat = json.loads((HERE / "NEUTRAL_BATTERY_FREEZE_V1.json").read_text())
assert hashlib.sha256((HERE / "NEUTRAL_BATTERY_FREEZE_V1.json").read_bytes()).hexdigest() == SHA
ep = bat["batteries"]["B_EP"]
rows = ep["task_rows"]
streams = [r["stream"] for r in rows]
required = [r["required_final_output"] for r in rows]

rev = json.loads((HERE / "REVIVAL_V2.json").read_text())
seed = rev["rows"]["Retrieval-augmented systems."]["constructive_witness"]["machine"]

# sanity: the seed solves all 56 episodes
s_err = 0
for r in rows:
    o, _tr, lg = A.run_stream(seed, r["stream"])
    if not lg or o[-1] != r["required_final_output"]:
        s_err += 1
assert s_err == 0, "seed has errors: %d" % s_err

taskset = P2.StreamTaskSet(streams, required, mode="final")
runs = []
best = None
for si in range(8):
    r = P2.evolve(taskset, seed=si, budget=200000, cell_cap=8,
                  genome="stream", init=seed)
    runs.append({"seed": si, "fitness": r["fitness"],
                 "evals": r["evals"],
                 "distinct": r["distinct_genomes_evaluated"]})
    if best is None or (r["fitness"][0], r["fitness"][1]) < (
            best["fitness"][0], best["fitness"][1]):
        best = r

m = best["genome"]
errs = 0
illegal = 0
traj_by_ep = {}
for r in rows:
    o, tr, lg = A.run_stream(m, r["stream"])
    traj_by_ep[tuple(r["stream"])] = tr
    if not lg:
        illegal += 1
        errs += 1
    elif o[-1] != r["required_final_output"]:
        errs += 1

store_cells = []
for ci in range(m["cells"]):
    vals4 = {traj_by_ep[tuple(r["stream"])][4][ci] for r in rows}
    vals5 = {traj_by_ep[tuple(r["stream"])][5][ci] for r in rows}
    if len(vals4) > 1 and all(
            traj_by_ep[tuple(r["stream"])][4][ci] ==
            traj_by_ep[tuple(r["stream"])][5][ci] for r in rows):
        store_cells.append(ci)
c1 = len(store_cells) >= 2
c2_ok = True
c2w = []
for r in rows:
    if r["order"] == [1, 2] and r["values"][0] != r["values"][1]:
        base = r["stream"]
        o1, _, l1 = A.run_stream(m, base[:4] + [1])
        o2, _, l2 = A.run_stream(m, base[:4] + [2])
        good = l1 and l2 and o1[-1] == r["values"][0] and o2[-1] == r["values"][1]
        c2w.append({"stream": base, "want1": r["values"][0], "want2": r["values"][1], "ok": bool(good)})
        if not good:
            c2_ok = False
        if len(c2w) >= 2:
            break
c3_ok = False
c3w = []
if store_cells:
    for r in rows:
        if r["order"] == [1, 2] and r["required_final_output"] == 1:
            o0, _, _ = A.run_stream(m, r["stream"])
            ci = store_cells[0]
            for nv in (-1, 0, 1):
                if nv == o0[-1]:
                    continue
                o1, _, _ = A.run_stream(m, r["stream"], clamps={(4, ci): nv})
                c3w.append({"cell": ci, "clamped": nv, "out_before": o0[-1],
                            "out_after": o1[-1] if o1 else None})
                if o1 and o1[-1] != o0[-1]:
                    c3_ok = True
            break

result = {
    "schema": "FDT_REVIVAL_T3_SEEDED_SEARCH_V3",
    "row": "Retrieval-augmented systems.",
    "battery_sha256": SHA,
    "pooled_seeds": 8,
    "budget_per_seed": 200000,
    "seed_pattern": "constructive 4-cell latch (REVIVAL_V2)",
    "runs": runs,
    "champion": {"fitness": list(best["fitness"]), "genome": m},
    "champion_identical_to_seed": repr(m) == repr(seed),
    "independent_errors": errs,
    "illegal": illegal,
    "cost": M.machine_cost(m),
    "ge_sites": M.machine_gate_sites(m),
    "cells": m["cells"],
    "K08_clauses": {"C1": c1, "C2": c2_ok, "C3": c3_ok,
                    "store_cells": store_cells,
                    "C2_witnesses": c2w, "C3_witnesses": c3w},
    "within_frozen_bounds": m["cells"] <= 8,
    "recovered": bool(errs == 0 and c1 and c2_ok and c3_ok),
}
(HERE / "k08_seeded_search_v3.json").write_text(json.dumps(result, indent=1))
print("K08_SEEDED_SEARCH_DONE errors", errs, "clauses", c1, c2_ok, c3_ok,
      "cost", M.machine_cost(m), "cells", m["cells"],
      "identical_to_seed", repr(m) == repr(seed),
      "recovered", result["recovered"])
