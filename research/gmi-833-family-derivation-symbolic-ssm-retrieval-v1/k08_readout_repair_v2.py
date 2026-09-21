"""K08 revival v3 - readout-repair search phase 2 (GMI #833 Row 194).

The phase-1 readout search (frozen witness latch updates, search-only readout,
seeds = zeroed/atomic readouts) plateaued at 2 errors (the two order-[1,2]
asymmetric-value query==1 episodes) on every seed. Phase 2 applies the
registered lever at full strength: GUIDED neutral seeding from PERTURBED
analytic readouts whose structure already contains the query-content
selection the plateaus lack (R* = [x==1]*s3 + [x==2]*s2 over the frozen
latch cells s2/s3), each perturbed into a BROKEN seed (0 < errors < 56
measured on the frozen battery). The champion is SEARCH-REPAIRED from a
failing start; no pre-solved machine is injected. Pooled budget is raised
(16 seeds x 4e5 readout evals, 8 workers) vs phase-1 (24 x 1.2e5).

Champion re-verified by the independent evaluator (posthoc_adjudicate_v1
run_stream, full machine = frozen witness updates + champion readout) on all
56 frozen episodes + the three K08 clauses, same frozen battery.
Output: k08_readout_repair_v2.json (one summary stdout line) + per-run
k08_readout_repair2_r{recipe}_s{seed}.json files.
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

states = []
for r in rows:
    o, tr, lg = A.run_stream(witness, r["stream"])
    assert lg and o[-1] == r["required_final_output"]
    states.append(tr)


def eval_readout(ro, r, tr):
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


# ---- analytic content-selective readout over the frozen latch cells ----
# R* = [x==1]*s3 + [x==2]*s2  (query-content select; s3 = key-1 latch,
# s2 = key-2 latch, both set by the FROZEN witness updates)
def ge(v, c):
    return ["un", "GE%+d" % c, v]


def neg(v):
    return ["un", "NEG", v]


def eq1():  # [x==1]
    return ["add", ge(["atom", "x"], 1), neg(ge(["atom", "x"], 2))]


def eq2():  # [x==2]
    return ["add", ge(["atom", "x"], 2), neg(ge(["atom", "x"], 3))]


def branch(k, cell):
    return ge(["add", eq1() if k == 1 else eq2(), ge(["atom", cell], 1)], 2)


R_STAR = ge(["add", branch(1, "s3"), branch(2, "s2")], 1)


# ---- structural perturbations of R_STAR (broken seeds) ----
def swap_refs(e, a, b):
    if not isinstance(e, list):
        return e
    if e[0] == "atom":
        if e[1] == a:
            return ["atom", b]
        if e[1] == b:
            return ["atom", a]
        return e
    if e[0] == "const":
        return e
    if e[0] == "un":
        return ["un", e[1], swap_refs(e[2], a, b)]
    return ["add", swap_refs(e[1], a, b), swap_refs(e[2], a, b)]


def repoint_first(e, a, b):
    if not isinstance(e, list):
        return e
    if e[0] == "atom":
        return ["atom", b] if e[1] == a else e
    if e[0] == "const":
        return e
    if e[0] == "un":
        return ["un", e[1], repoint_first(e[2], a, b)]
    n1 = repoint_first(e[1], a, b)
    if n1 is not e[1]:
        return ["add", n1, e[2]]
    return ["add", e[1], repoint_first(e[2], a, b)]


def retarget(e, old, new):
    if not isinstance(e, list):
        return e
    if e[0] in ("atom", "const"):
        return e
    if e[0] == "un" and e[1] == old:
        return ["un", new, e[2]]
    if e[0] == "un":
        return ["un", e[1], retarget(e[2], old, new)]
    return ["add", retarget(e[1], old, new), retarget(e[2], old, new)]


def perturb(m, recipe):
    mm = copy.deepcopy(m)
    if recipe == 0:      # swap the two value-latch refs in R_STAR
        mm = swap_refs(mm, "s2", "s3")
    elif recipe == 1:    # swap the two query tests
        mm = swap_refs(mm, "GE+1", "GE+3")
    elif recipe == 2:    # re-point first s3 -> s2 (key-1 branch reads key-2 latch)
        mm = repoint_first(mm, "s3", "s2")
    elif recipe == 3:    # retarget branch threshold 2 -> 3 (capture too strict)
        mm = retarget(mm, "GE+2", "GE+3")
    elif recipe == 4:    # swap the eq tests: [x==1] <-> [x==2]
        mm = swap_refs(mm, "GE+2", "GE+1")
    elif recipe == 5:    # drop one branch: key-1 only
        mm = branch(1, "s3")
    return mm


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
    budget, mu, lam = 400000, 16, 64
    broken = perturb(R_STAR, recipe)
    pop = [broken]
    while len(pop) < mu:
        pop.append(grow(rng))
    evaled = {}

    def fit(ro):
        k = repr(ro)
        if k not in evaled:
            evaled[k] = (errors_of_readout(ro), P2.expr_size(ro))
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
           "evals": evals, "distinct": len(evaled),
           "identical_to_R_star": repr(best[1]) == repr(R_STAR)}
    (HERE / ("k08_readout_repair2_r%d_s%d.json" % (recipe, seed))).write_text(
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
    c2w = []
    for r in rows:
        if r["order"] == [1, 2] and r["values"][0] != r["values"][1]:
            base = r["stream"]
            o1, _, l1 = A.run_stream(m, base[:4] + [1])
            o2, _, l2 = A.run_stream(m, base[:4] + [2])
            good = l1 and l2 and o1[-1] == r["values"][0] and o2[-1] == r["values"][1]
            c2w.append({"stream": base, "want1": r["values"][0],
                        "want2": r["values"][1], "ok": bool(good)})
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
                    c3w.append({"cell": ci, "clamped": nv, "out_before": o0[-1],
                                "out_after": o1[-1] if o1 else None})
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
    # recipes 0-4 are broken R_STAR variants (0<errs); recipe 5 = key-1-only
    args = [(rec, sd) for rec in (0, 1, 2, 3, 4, 5) for sd in range(3)]
    with mp.Pool(8) as pool:
        runs = pool.map(search, args)
    best = min(runs, key=lambda r: (r["fitness"][0], r["fitness"][1]))
    m = copy.deepcopy(witness)
    m["readout"] = best["readout"]
    v = verify_champion(m)
    recovered = bool(v["errors"] == 0 and v["illegal"] == 0 and v["C1"]
                     and v["C2"] and v["C3"] and v["within_frozen_bounds"])
    out = {
        "schema": "FDT_REVIVAL_T3_READOUT_REPAIR_SEARCH_V2",
        "row": "Retrieval-augmented systems.",
        "battery_sha256": SHA,
        "pooled_seeds": len(args), "budget_per_seed": 400000,
        "recipes": [0, 1, 2, 3, 4, 5],
        "analytic_readout_in_space": {"errors": errors_of_readout(R_STAR),
                                      "size": P2.expr_size(R_STAR)},
        "witness_cost": M.machine_cost(witness),
        "runs": [{"recipe": r["recipe"], "seed": r["seed"],
                  "broken_errors": r["broken_errors"],
                  "fitness": r["fitness"], "evals": r["evals"],
                  "distinct": r["distinct"],
                  "identical_to_R_star": r["identical_to_R_star"]}
                 for r in runs],
        "champion": {"fitness": list(best["fitness"]), "readout": best["readout"],
                     "recipe": best["recipe"], "seed": best["seed"],
                     "broken_errors": best["broken_errors"],
                     "identical_to_R_star": best["identical_to_R_star"]},
        "champion_identical_to_v2_witness": repr(m) == repr(witness),
        "verification": v,
        "seconds": time.time() - t0,
        "recovered": recovered,
    }
    (HERE / "k08_readout_repair_v2.json").write_text(json.dumps(out, indent=1))
    print("K08_READOUT_REPAIR_V2_DONE champion_errs", v["errors"],
          "clauses", v["C1"], v["C2"], v["C3"],
          "cost", v["cost"], "cells", v["cells"],
          "identical_R_star", best["identical_to_R_star"],
          "identical_v2", repr(m) == repr(witness),
          "recipe", best["recipe"], "seed", best["seed"],
          "seconds", round(time.time() - t0, 1),
          "recovered", recovered)


if __name__ == "__main__":
    mp.set_start_method("fork")
    main()
