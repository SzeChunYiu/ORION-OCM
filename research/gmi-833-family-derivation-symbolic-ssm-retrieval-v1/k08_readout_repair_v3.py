"""K08 revival v3 — readout-repair guided search on B_EP (GMI #833 Row 194).

Registered lever (phase 4): raise the pooled blind T3 budget with guided
neutral seeding from BROKEN 4-cell latch machines — the constructive
witness's capture cells (updates) frozen, the READOUT zeroed/randomized
(8..56 measured errors) — and search ONLY the readout expression over the
frozen basis. Capture trajectories are precomputed once per episode
(updates are frozen and readout-independent), so the readout search
evaluates exactly the same guarded semantics as the independent evaluator
~200x faster than full resimulation. The recovery morphology (a
query-content-selective readout reading both latches) is SEARCH-DISCOVERED
from a failing start, never injected.

Champion re-verified by the independent evaluator on all 56 frozen episodes
+ the three K08 clauses, same frozen battery.
Output: k08_readout_repair_v3.json (one summary stdout line) + per-run
k08_readout_repair_r{recipe}_s{seed}.json files written as each run lands.
"""
from __future__ import annotations
import copy, hashlib, json, multiprocessing as mp, random, sys, time
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
rev = json.loads((HERE / "REVIVAL_V2.json").read_text())
witness = rev["rows"]["Retrieval-augmented systems."]["constructive_witness"]["machine"]

ATOMS = ["s0", "s1", "s2", "s3", "x"]

# precompute per-episode state trajectories (steps 0..5; updates frozen and
# readout-independent). trajs[j] = state BEFORE token j (run_stream semantics:
# readout at token j uses trajs[j] and stream[j]; final required output is at
# token index 4).
states = []
for r in rows:
    o, tr, lg = A.run_stream(witness, r["stream"])
    assert lg and o[-1] == r["required_final_output"]
    states.append(tr)


def eval_readout(ro, r, tr):
    """Exact guarded semantics: illegal at any position, or wrong at the
    final position -> error 1."""
    st = r["stream"]
    for j in range(5):
        env = {"s%d" % i: tr[j][i] for i in range(4)}
        env["x"] = st[j]
        if A.ev(ro, env) is None:
            return 1
    env = {"s%d" % i: tr[4][i] for i in range(4)}
    env["x"] = st[4]
    y = A.ev(ro, env)
    return 1 if (y is None or y != r["required_final_output"]) else 0


def errors_of_readout(ro):
    return sum(eval_readout(ro, r, states[i]) for i, r in enumerate(rows))


def readout_cost(ro):
    return M.expr_ops(ro)


RECIPES = {
    0: ["const", 0],
    1: ["atom", "x"],
    2: ["un", "GE+0", ["atom", "x"]],
    3: ["un", "GE+1", ["atom", "s3"]],
}


def grow(rng):
    return P2.grown_expr(rng, ATOMS, edits_poisson=8)


def mutate(ro, rng):
    for _ in range(3):
        nro = P2.mutate_expr(ro, rng, ATOMS)
        if P2.cap_expr(nro) is not None:
            return nro
    return ro


def search(args):
    recipe, seed = args
    rng = random.Random((P2.frozen_hash(seed) ^ (recipe * 0x9E3779B9)) % (2 ** 32))
    budget, mu, lam = 120000, 16, 64
    broken = RECIPES[recipe]
    pop = [broken]
    while len(pop) < mu:
        pop.append(grow(rng))
    evaled = {}

    def fit(ro):
        k = repr(ro)
        if k not in evaled:
            evaled[k] = (errors_of_readout(ro), readout_cost(ro))
        return evaled[k]

    scored = [(fit(g), g) for g in pop]
    evals = len(pop)
    best = min(scored, key=lambda p: (p[0], repr(p[1])))
    while evals < budget:
        children = []
        parents_pool = [g for (_f, g) in scored]
        while len(children) < lam:
            if rng.random() < 0.05:
                children.append(grow(rng))
            else:
                children.append(mutate(rng.choice(parents_pool), rng))
        sc = [(fit(g), g) for g in children]
        evals += len(children)
        union = scored + sc
        best_err = min(f[0] for f, _ in union)
        plateau = [g for f, g in union if f[0] == best_err]
        if len(plateau) <= mu:
            parents = plateau
        else:
            parents = rng.sample(plateau, mu)
        seen = set()
        uniq = []
        for g in parents:
            k = repr(g)
            if k not in seen:
                seen.add(k)
                uniq.append(g)
        scored = [(fit(g), g) for g in uniq]
        b = min([(f, g) for f, g in union], key=lambda p: (p[0], repr(p[1])))
        if (b[0], repr(b[1])) < (best[0], repr(best[1])):
            best = b
    res = {"recipe": recipe, "seed": seed,
           "broken_errors": errors_of_readout(broken),
           "fitness": list(best[0]), "readout": best[1],
           "evals": evals, "distinct": len(evaled)}
    (HERE / ("k08_readout_repair_r%d_s%d.json" % (recipe, seed))).write_text(
        json.dumps(res))
    return res


def verify_champion(m):
    errs = 0
    illegal = 0
    traj_by_ep = {}
    for r in rows:
        oo, tr, lg = A.run_stream(m, r["stream"])
        traj_by_ep[tuple(r["stream"])] = tr
        if not lg:
            illegal += 1
            errs += 1
        elif oo[-1] != r["required_final_output"]:
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
    for r in rows:
        if r["order"] == [1, 2] and r["values"][0] != r["values"][1]:
            base = r["stream"]
            o1, _, l1 = A.run_stream(m, base[:4] + [1])
            o2, _, l2 = A.run_stream(m, base[:4] + [2])
            if not (l1 and l2 and o1[-1] == r["values"][0] and o2[-1] == r["values"][1]):
                c2_ok = False
            break
    c3_ok = False
    if store_cells:
        for r in rows:
            if r["order"] == [1, 2] and r["required_final_output"] == 1:
                o0, _, _ = A.run_stream(m, r["stream"])
                ci = store_cells[0]
                for nv in (-1, 0, 1):
                    if nv == o0[-1]:
                        continue
                    o1, _, _ = A.run_stream(m, r["stream"], clamps={(4, ci): nv})
                    if o1 and o1[-1] != o0[-1]:
                        c3_ok = True
                break
    return {"errors": errs, "illegal": illegal, "store_cells": store_cells,
            "C1": c1, "C2": c2_ok, "C3": c3_ok,
            "cost": M.machine_cost(m), "ge_sites": M.machine_gate_sites(m),
            "cells": m["cells"],
            "within_frozen_bounds": bool(
                m["cells"] <= 8 and
                max(P2.expr_size(e) for e in m["update"]) <= 40 and
                P2.expr_size(m["readout"]) <= 40)}


def main():
    t0 = time.time()
    args = [(rec, sd) for rec in (0, 1, 3) for sd in range(8)]
    with mp.Pool(4) as pool:
        runs = pool.map(search, args)
    best = min(runs, key=lambda r: (r["fitness"][0], r["fitness"][1]))
    m = copy.deepcopy(witness)
    m["readout"] = best["readout"]
    v = verify_champion(m)
    recovered = bool(v["errors"] == 0 and v["illegal"] == 0 and v["C1"]
                     and v["C2"] and v["C3"] and v["within_frozen_bounds"])
    out = {
        "schema": "FDT_REVIVAL_T3_READOUT_REPAIR_SEARCH_V3",
        "row": "Retrieval-augmented systems.",
        "battery_sha256": SHA,
        "pooled_seeds": len(args), "budget_per_seed": 120000,
        "recipes": [0, 1, 3],
        "witness_cost": M.machine_cost(witness),
        "runs": [{"recipe": r["recipe"], "seed": r["seed"],
                  "broken_errors": r["broken_errors"],
                  "fitness": r["fitness"], "evals": r["evals"],
                  "distinct": r["distinct"]} for r in runs],
        "champion": {"fitness": list(best["fitness"]), "readout": best["readout"],
                     "recipe": best["recipe"], "seed": best["seed"],
                     "broken_errors": best["broken_errors"]},
        "champion_identical_to_v2_witness": repr(m) == repr(witness),
        "verification": v,
        "seconds": time.time() - t0,
        "recovered": recovered,
    }
    (HERE / "k08_readout_repair_v3.json").write_text(json.dumps(out, indent=1))
    print("K08_READOUT_REPAIR_DONE champion_errs", v["errors"],
          "clauses", v["C1"], v["C2"], v["C3"],
          "cost", v["cost"], "cells", v["cells"],
          "identical_v2", repr(m) == repr(witness),
          "recipe", best["recipe"], "seed", best["seed"],
          "seconds", round(time.time() - t0, 1),
          "recovered", recovered)


if __name__ == "__main__":
    mp.set_start_method("fork")
    main()
