"""K08 revival v3 - independent re-verification of the repair-search champion
(GMI #833 Row 194, Retrieval-augmented systems).

Reads ONLY the frozen battery and the champion genome recorded in
k08_neutral_repair_search_v3.json (or, as fallback source, the constructive
4-cell latch witness in REVIVAL_V2.json). Re-runs all 56 B_EP episodes with
the package's INDEPENDENT evaluator (posthoc_adjudicate_v1.run_stream) and
re-executes the three K08 clauses as real interventions (persistence,
same-store two-query divergence, store-alteration causality). Cost and
frozen-bounds checks re-run. Stdlib + package modules.
Writes k08_revival_verify_v3.json.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import machinery_v1 as M
import posthoc_adjudicate_v1 as A

BATTERY_SHA256 = "5b385f0edfa035b28940f5dd982e0c69991a2ce6e0175e4c693073add26899f0"


def expr_size(e):
    if e[0] in ("atom", "const"):
        return 1
    if e[0] == "un":
        return 1 + expr_size(e[2])
    return 1 + expr_size(e[1]) + expr_size(e[2])


def verify(m, rows):
    errs = 0
    illegal = 0
    traj_by_ep = {}
    for r in rows:
        oo, tr, lg = A.run_stream(m, r["stream"])
        traj_by_ep[tuple(r["stream"])] = tr
        if not lg:
            illegal += 1
            errs += 1
            continue
        if oo[-1] != r["required_final_output"]:
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
            good = bool(l1 and l2 and o1[-1] == r["values"][0]
                        and o2[-1] == r["values"][1])
            c2w.append({"stream": base, "want1": r["values"][0],
                        "want2": r["values"][1], "ok": good})
            if not good:
                c2_ok = False
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
                    c3w.append({"cell": ci, "clamped": nv,
                                "out_before": o0[-1],
                                "out_after": o1[-1] if o1 else None})
                    if o1 and o1[-1] != o0[-1]:
                        c3_ok = True
                break
    return {"errors": errs, "illegal": illegal,
            "store_cells": store_cells,
            "C1": c1, "C2": c2_ok, "C3": c3_ok,
            "C2_witnesses": c2w, "C3_witnesses": c3w,
            "cost": M.machine_cost(m),
            "ge_sites": M.machine_gate_sites(m),
            "cells": m["cells"],
            "within_frozen_bounds": bool(
                m["cells"] <= 8 and
                max(expr_size(e) for e in m["update"]) <= 40 and
                expr_size(m["readout"]) <= 40)}


def main():
    sha = hashlib.sha256((HERE / "NEUTRAL_BATTERY_FREEZE_V1.json").read_bytes()).hexdigest()
    assert sha == BATTERY_SHA256, "frozen battery sha256 mismatch: %s" % sha
    bat = json.loads((HERE / "NEUTRAL_BATTERY_FREEZE_V1.json").read_text())
    rows = bat["batteries"]["B_EP"]["task_rows"]

    src = HERE / "k08_neutral_repair_search_v3.json"
    if src.exists():
        search = json.loads(src.read_text())
        m = search["champion"]["genome"]
        source = "k08_neutral_repair_search_v3.json (search-repaired champion)"
        champion_fitness = search["champion"]["fitness"]
        identical_to_v2 = search.get("champion_identical_to_v2_witness")
    else:
        rev = json.loads((HERE / "REVIVAL_V2.json").read_text())
        m = rev["rows"]["Retrieval-augmented systems."]["constructive_witness"]["machine"]
        source = "REVIVAL_V2.json constructive 4-cell latch witness (fallback)"
        champion_fitness = None
        identical_to_v2 = True

    v = verify(m, rows)
    recovered = bool(v["errors"] == 0 and v["illegal"] == 0 and
                     v["C1"] and v["C2"] and v["C3"] and
                     v["within_frozen_bounds"])
    out = {
        "schema": "FDT_REVIVAL_VERIFY_K08_V3",
        "row": "Retrieval-augmented systems.",
        "battery_sha256": sha,
        "source": source,
        "champion_fitness": champion_fitness,
        "identical_to_v2_witness": identical_to_v2,
        "verification": v,
        "recovered_at_scope": recovered,
        "note": "independent re-simulation of the champion on all 56 frozen B_EP episodes; C1/C2/C3 executed as real interventions per the frozen adjudicator semantics",
    }
    (HERE / "k08_revival_verify_v3.json").write_text(json.dumps(out, indent=1))
    print("K08_VERIFY_V3 source=", source)
    print("  errors", v["errors"], "illegal", v["illegal"],
          "C1", v["C1"], "C2", v["C2"], "C3", v["C3"],
          "cost", v["cost"], "cells", v["cells"],
          "within_bounds", v["within_frozen_bounds"],
          "recovered", recovered)
    assert recovered, "K08 champion not recovered at scope"


if __name__ == "__main__":
    main()
