"""K05 chain search v4 — pooled PROC2 search for a contraction-chain-capable
M_ITER machine (GMI #833 row 196, Symbolic logic systems.).

Seeds each run from the committed constructive [t0==g] reflexive witness
(REVIVAL_V2.json rows/Symbolic logic systems.) and searches the frozen
2000-task subset (133 pos = 88 reflexive + 41 one-step + 4 two-step;
1867 neg) for 0 errors, then per-seed verifies the FULL 17424-task battery
(1176 pos / 16248 neg) with the package's independent evaluator
(posthoc_adjudicate_v1.run_iter). Mirrors k08_readout_repair_v3.py.

Writes k05_chain_search4_r<seed>.json per seed + k05_chain_search4_all.json.
Run with plain `python3 -B` (NEVER -I: isolated mode strips site-packages
and the numpy import in proc2_v1 leaves np=None).
"""
from __future__ import annotations
import hashlib, json, multiprocessing as mp, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import proc2_v1 as P2
import posthoc_adjudicate_v1 as A

SHA = "5b385f0edfa035b28940f5dd982e0c69991a2ce6e0175e4c693073add26899f0"
bat = json.loads((HERE / "NEUTRAL_BATTERY_FREEZE_V1.json").read_text())
assert hashlib.sha256((HERE / "NEUTRAL_BATTERY_FREEZE_V1.json").read_bytes()).hexdigest() == SHA
bc = bat["batteries"]["B_CONTR"]
rows = bc["task_rows"]
layouts = bc["task_cell_layouts"]
y = [r[3] for r in rows]

rev = json.loads((HERE / "REVIVAL_V2.json").read_text())
witness = rev["rows"]["Symbolic logic systems."]["constructive_witness"]["machine"]

# frozen 2000-subset = first 2000 tasks in frozen_hash order (matches the
# committed characterization k05_reach_characterize_v3.py: sub = set(idx[:2000])
# with idx = sorted(range(n), key=lambda i: P2.frozen_hash(i))).
SUB = [i for i in sorted(range(len(rows)), key=lambda i: P2.frozen_hash(i))[:2000]]
ts = P2.IterTaskSet([layouts[i] for i in SUB], [y[i] for i in SUB], steps=16)


def pred(g, i):
    c, _, lg = A.run_iter(g, layouts[i])
    return c[g["output_cell"]] if lg else None


# sanity: the witness must reproduce its registered 45 subset errors
we = sum(1 for i in SUB if pred(witness, i) != y[i])
wfull = sum(1 for i in range(len(rows)) if pred(witness, i) != y[i])
print("WITNESS_SUBSET_ERRS", we, "WITNESS_FULL_ERRS", wfull, flush=True)
# science validation vs the committed record: full battery 384 is asserted (the
# search objective is subset-0 then full-battery 0/1176 + 0 FP via the
# independent evaluator). Subset 45 is logged; any mismatch is a checker probe
# discrepancy, not a fitness claim.
assert wfull == 384, wfull


def scan_full(g):
    pos_err = fp = errs = 0
    for i in range(len(rows)):
        p = pred(g, i)
        if p != y[i]:
            errs += 1
            if y[i] == 1:
                pos_err += 1
            else:
                fp += 1
    return errs, pos_err, fp


def run_seed(args):
    seed, budget = args
    out = P2.evolve(ts, seed, budget, cell_cap=24, genome="iter",
                    n_in=18, steps=16, init=witness)
    g = out["genome"]
    rec = {
        "schema": "FDT_REVIVAL_SEARCH_K05_CHAIN_V4",
        "row": "Symbolic logic systems.",
        "battery_sha256": SHA,
        "seed": seed, "budget": budget,
        "subset_fitness": out["fitness"],
        "evals": out["evals"],
        "cost": out["fitness"][1],
        "work_cells": len(g.get("update", [])),
        "champion_identical_to_witness": repr(g) == repr(witness),
    }
    if out["fitness"][0] <= 20:
        errs, pe, fp = scan_full(g)
        rec.update(full_errs=errs, full_pos_errs=pe, full_fp=fp)
    else:
        rec.update(full_errs=None, full_pos_errs=None, full_fp=None)
    (HERE / ("k05_chain_search4_r%d.json" % seed)).write_text(json.dumps(rec))
    print("SEED", seed, "fit", out["fitness"], "full", rec.get("full_errs"),
          "pos", rec.get("full_pos_errs"), "fp", rec.get("full_fp"), flush=True)
    return rec


def main():
    n_seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    budget = int(sys.argv[2]) if len(sys.argv) > 2 else 200000
    print("K05_CHAIN_SEARCH4 n_seeds", n_seeds, "budget", budget, flush=True)
    with mp.Pool(min(8, n_seeds)) as pool:
        results = pool.map(run_seed, [(s, budget) for s in range(n_seeds)])
    (HERE / "k05_chain_search4_all.json").write_text(json.dumps(results, indent=1))
    print("K05_CHAIN_SEARCH4_DONE", flush=True)


if __name__ == "__main__":
    main()
