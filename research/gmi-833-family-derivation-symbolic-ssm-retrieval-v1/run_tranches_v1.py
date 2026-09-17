"""Run tranches v1 — orchestrator for the derivation tranches (GMI #833).

Runs on a compute host (not CI). Reads ONLY the frozen battery, the frozen
basis, the v2 frozen B_DELAY battery (parent-pinned), and declared caps.
Writes BLIND_OUTCOME_V1_T1/T2/T3.json, NULLS_V1.json, RECEIPTS_RUN_LOG.md.
No family/benchmark data is read anywhere on this side.

Usage: python3 -B run_tranches_v1.py [t1|t2|t3|nulls|all]
"""
from __future__ import annotations

import hashlib
import json
import multiprocessing as mp
import os
import platform
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import numpy as np  # noqa: E402

import machinery_v1 as M  # noqa: E402
import proc1_v1 as P  # noqa: E402
import proc2_v1 as P2  # noqa: E402

BAT = json.loads((HERE / "NEUTRAL_BATTERY_FREEZE_V1.json").read_text())
V2_BAT_PATH = HERE.parent / "gmi-833-blind-recovery-v2-v1" / \
    "NEUTRAL_BATTERY_FREEZE_V1.json"
V2_BAT = json.loads(V2_BAT_PATH.read_text())

BUDGET_PRIMARY = int(os.environ.get("FDT_BUDGET_PRIMARY", 100_000))
BUDGET_T3_PRIMARY = int(os.environ.get("FDT_BUDGET_T3_PRIMARY", 10_000_000))
T3_PRIMARY_SEEDS = int(os.environ.get("FDT_T3_PRIMARY_SEEDS", 10))
BUDGET_T3_NULL = int(os.environ.get("FDT_BUDGET_T3_NULL", 100_000))
BUDGET_CROSSOVER = int(os.environ.get("FDT_BUDGET_CROSSOVER", 10_000))
BUDGET_NULL = int(os.environ.get("FDT_BUDGET_NULL", 10_000))
NULL_SEEDS = list(range(int(os.environ.get("FDT_NULL_SEEDS", 200))))
RHOS = [1, 2, 4, 8, 16]


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# TR-2
# ---------------------------------------------------------------------------

def run_t2():
    t0 = time.time()
    bw = BAT["batteries"]["B_W2"]
    stream = bw["stream"]
    rows = bw["task_rows"]
    targets = {}
    truth_tables = {}
    for i, r in enumerate(rows):
        targets[tuple(r["required_outputs"])] = i
        truth_tables[i] = tuple(r["truth_table"])
    assert len(targets) == 2401

    # affine classification (analytic, complete)
    affine = {}
    for a in range(-6, 7):
        for b in range(-6, 7):
            for c in range(-6, 7):
                vals = (c, b + c, a + c, a + b + c)  # f(0,0),f(0,1),f(1,0),f(1,1)
                if all(v in M.DOMAIN for v in vals):
                    affine[vals] = (a, b, c)
    affine_ids = {i for i, tt in truth_tables.items() if tt in affine}

    # pairing DP (k=1, gates allowed)
    dp = P.w2_pairing_dp(stream, targets, rho=1, cost_cap=8, width_cap=300_000)
    per_task = {}
    for i in range(2401):
        r = dp["per_task"].get(i)
        if r is None:
            continue
        mm = r["machine"]
        gates = M.machine_gate_sites(mm)
        per_task[i] = {"cost": r["cost"], "gates": gates,
                       "machine": mm,
                       "update_cost": r["update_cost"],
                       "readout_cost": r["readout_cost"]}

    # gate-free k=1 exhaustive certificate
    gf, gf_stats = P.gatefree_k1_exhaust(stream, targets, coef_bound=3)
    # gate-free k=2 exhaustive certificate on the same stream (all targets)
    gf2w, gf2w_stats = P.gatefree_k2_delay(stream, targets, ab_bound=2,
                                           ro_bound=1)
    gf2w_nonaffine = [targets[k] for k in gf2w
                      if targets[k] not in affine_ids]
    # verify each gf-realized target is affine (theorem check)
    non_affine_gf = [i for i in gf if i not in affine_ids]
    # realize one machine per gf target (constructive; keep min-cost attempt)
    gf_machines = {}
    for i, coeffs in gf.items():
        mm = P.realize_gatefree_k1(coeffs, stream)
        if mm is not None:
            gf_machines[i] = mm

    # rho sweep from stored decompositions
    rho_costs = {}
    for rho in RHOS:
        rho_costs[rho] = {i: rho + r["update_cost"] + r["readout_cost"]
                          for i, r in per_task.items()}

    # delay subtranche (held-out, v2 battery)
    delay = {}
    for t in V2_BAT["batteries"]["B_DELAY"]["tasks"]:
        lag = t["lag"]
        st = t["stream"]
        req = t["required_outputs"]
        tg = {tuple(req): "LAG%d" % lag}
        r1 = P.w2_pairing_dp(st, tg, rho=1, cost_cap=8, width_cap=300_000)
        gf1, s1 = P.gatefree_k1_exhaust(st, tg, coef_bound=3)
        gf2, s2 = P.gatefree_k2_delay(st, tg, ab_bound=2, ro_bound=1)
        lag_crossover = {}
        for rho in RHOS:
            lag_crossover[rho] = {
                "k1_best_cost": (rho + r1["per_task"]["LAG%d" % lag]["cost"] - 1)
                if "LAG%d" % lag in r1["per_task"] else None,
                "k2_gatefree_cost": (2 * rho) if gf2 else None,
            }
        delay["LAG%d" % lag] = {
            "lag": lag,
            "k1_pairing": {"cost": r1["per_task"]["LAG%d" % lag]["cost"],
                           "machine": r1["per_task"]["LAG%d" % lag]["machine"]}
            if "LAG%d" % lag in r1["per_task"] else None,
            "k1_gatefree_realized": "LAG%d" % lag in gf1,
            "k2_gatefree_realized": len(gf2) > 0,
            "k2_coeffs_example": (list(next(iter(gf2))) if gf2 else None),
            "rho_crossover": lag_crossover,
            "exhaust_stats": {"k1": s1, "k2": s2},
        }

    # nulls: equal-size random admission over the complete class, statistics
    # computed with IDENTICAL conditioning for true battery and nulls
    # (full-class fractions; resolved-conditioned fractions over the SAME
    # resolved subset).
    resolved = {i for i in per_task}

    def stats_over(ids):
        n = len(ids)
        res = [i for i in ids if i in resolved]
        return {
            "frac_affine": float(sum(1 for i in ids if i in affine_ids)) / n,
            "frac_gatefree_realizable":
                float(sum(1 for i in ids if i in gf)) / n,
            "frac_gatefree_minimal":
                float(sum(1 for i in res
                          if per_task[i]["gates"] == 0 and i in gf)) /
                max(1, len(res)),
            "mean_min_cost_resolved":
                float(np.mean([per_task[i]["cost"] for i in res]))
                if res else float("nan"),
            "resolved_frac": len(res) / float(n),
        }

    true_ids = list(range(2401))
    stats_true = stats_over(true_ids)
    null_draws = {k: [] for k in stats_true}
    for sd in NULL_SEEDS:
        tts = P2.null_truth_tables(sd, 2401)
        ids = []
        for tt in tts:
            trace = tuple(tt[2 * w[0] + w[1]] for w in bw["windows"])
            i = targets.get(trace)
            if i is not None:
                ids.append(i)
        st = stats_over(ids)
        for k in stats_true:
            null_draws[k].append(st[k])
    rng_stat = {
        "definition": ("equal-size random admission with replacement from "
                       "the complete 2401-table class; identical statistic "
                       "conditioning for true and null batteries"),
        "true": stats_true,
        "nulls": null_draws,
        "null_beats_true": {k: int(sum(1 for v in null_draws[k]
                                       if v is not None and
                                       not (v != v) and v > stats_true[k]))
                            for k in stats_true},
        "empirical_rank_true": {k: int(1 + sum(1 for v in null_draws[k]
                                               if v is not None and
                                               not (v != v) and
                                               v > stats_true[k]))
                                for k in stats_true},
    }

    out = {
        "schema": "FDT_BLIND_OUTCOME_T2_V1",
        "benchmark_or_family_data_used": False,
        "battery": "B_W2",
        "n_tasks": 2401,
        "affine_tables": len(affine),
        "affine_task_ids": len(affine_ids),
        "pairing": {
            "resolved_tasks": len(per_task),
            "binding": dp["binding"],
            "details": dp["details"],
            "cost_histogram": {str(c): sum(1 for r in per_task.values()
                                           if r["cost"] == c)
                               for c in sorted({r["cost"]
                                                for r in per_task.values()})},
            "gate_histogram": {str(g): sum(1 for r in per_task.values()
                                           if r["gates"] == g)
                               for g in sorted({r["gates"]
                                                for r in per_task.values()})},
        },
        "gatefree": {"realized_tasks": len(gf),
                     "realized_ids": sorted(int(i) for i in gf),
                     "exhaust_stats": gf_stats,
                     "all_realized_are_affine": len(non_affine_gf) == 0,
                     "non_affine_realized": len(non_affine_gf),
                     "realized_machines_verified": len(gf_machines),
                     "k2_exhaust_stats": gf2w_stats,
                     "k2_realized_tasks": len(gf2w),
                     "k2_nonaffine_realized": len(gf2w_nonaffine)},
        "per_task": {str(i): {"cost": r["cost"], "gates": r["gates"],
                              "update_cost": r["update_cost"],
                              "readout_cost": r["readout_cost"]}
                     for i, r in per_task.items()},
        "machines_sample": {str(i): per_task[i]["machine"]
                            for i in sorted(per_task)[:40]},
        "gatefree_machines_sample": {str(i): gf_machines[i]
                                     for i in sorted(gf_machines)[:20]},
        "rho_costs_summary": {str(rho): {"min": min(v.values()),
                                         "mean": float(np.mean(list(v.values())))
                                         } for rho, v in rho_costs.items()},
        "delay_subtranche": delay,
        "nulls": rng_stat,
        "seconds": time.time() - t0,
    }
    (HERE / "BLIND_OUTCOME_V1_T2.json").write_text(
        json.dumps(out, indent=1, sort_keys=True))
    print("T2 done in %.1fs: %d/2401 resolved, gatefree %d, affine %d"
          % (out["seconds"], len(per_task), len(gf), len(affine_ids)))


# ---------------------------------------------------------------------------
# TR-3
# ---------------------------------------------------------------------------

def _ep_taskset(rows, mode="final"):
    return P2.StreamTaskSet([r["stream"] for r in rows],
                            [r["required_final_output"] for r in rows], mode)


def _one_ep_run(args):
    seed, rows, budget, cell_cap, mu, lam = args
    ts = _ep_taskset(rows)
    return P2.evolve(ts, seed, budget, cell_cap, genome="stream",
                     mu=mu, lam=lam)


def run_t3():
    t0 = time.time()
    be = BAT["batteries"]["B_EP"]
    rows = be["task_rows"]
    ts = _ep_taskset(rows)

    # certificate: no affine form solves B_EP
    aff, aff_stats = P.ep_affine_exhaust(rows, coef_bound=3)

    # PROC2 primary = pooled best of T3_PRIMARY_SEEDS seeds at the full
    # budget (neutral seed-diversity axis; declared in errata 3-4)
    def _one_t3_seed(sd):
        return P2.evolve(ts, sd, BUDGET_T3_PRIMARY, 8, genome="stream")
    with mp.Pool(min(10, os.cpu_count() or 4)) as pool:
        seed_runs = pool.map(_one_t3_seed, range(T3_PRIMARY_SEEDS))
    primary = min(seed_runs, key=lambda r: (r["fitness"], r["seed"]))
    primary["seed_set"] = [r["seed"] for r in seed_runs]
    primary["seed_fitnesses"] = [list(r["fitness"]) for r in seed_runs]
    abl = {}
    for (mu, lam) in ((8, 32), (32, 128)):
        abl["mu%d_lam%d" % (mu, lam)] = P2.evolve(
            ts, 0, BUDGET_T3_PRIMARY, 8, genome="stream", mu=mu, lam=lam)
    robust = []
    for s in range(1, 10):
        r = P2.evolve(ts, s, BUDGET_PRIMARY // 2, 8, genome="stream")
        robust.append({"seed": s, "fitness": r["fitness"]})

    # full-battery verification of champion
    champ = primary["genome"]
    outs, legal, traj = M.batch_sim_stream(champ, ts.S, np)
    errs = int(np.count_nonzero(outs[:, -1] != ts.y)) + \
        int(np.count_nonzero(~legal)) * 57

    # order-fixed ablation battery (negative twin)
    rows_fixed = [r for r in rows if r["order"] == [1, 2]]
    rfix = P2.evolve(_ep_taskset(rows_fixed), 0, BUDGET_PRIMARY, 8,
                     genome="stream")
    outs_f, legal_f, _ = M.batch_sim_stream(
        rfix["genome"], _ep_taskset(rows_fixed).S, np)
    errs_f = int(np.count_nonzero(outs_f[:, -1] !=
                                  _ep_taskset(rows_fixed).y)) + \
        int(np.count_nonzero(~legal_f)) * (len(rows_fixed) + 1)

    # value-domain {-1,0,1} probe battery
    rows_v3 = []
    for v1 in (-1, 0, 1):
        for v2 in (-1, 0, 1):
            for order in ((1, 2), (2, 1)):
                fa = {order[0]: v1, order[1]: v2}
                for q in M.DOMAIN:
                    rows_v3.append({"order": list(order), "values": [v1, v2],
                                    "stream": [order[0], v1, order[1], v2, q],
                                    "required_final_output":
                                        fa[q] if q in fa else 0})
    probe = P2.evolve(_ep_taskset(rows_v3), 0, BUDGET_PRIMARY, 8,
                      genome="stream")

    # nulls (parallel)
    args = [(s, [dict(r) for r in rows], BUDGET_T3_NULL, 8, 16, 64)
            for s in NULL_SEEDS]
    with mp.Pool(min(12, os.cpu_count())) as pool:
        null_runs = pool.map(_null_ep_run, args)
    null_stats = {
        "budget": BUDGET_NULL,
        "champion_errors": [r["fitness"][0] for r in null_runs],
        "champion_costs": [r["fitness"][1] for r in null_runs],
    }

    out = {
        "schema": "FDT_BLIND_OUTCOME_T3_V1",
        "benchmark_or_family_data_used": False,
        "battery": "B_EP",
        "affine_certificate": {"solutions": aff, "stats": aff_stats},
        "primary": {"fitness": primary["fitness"], "genome": champ,
                    "evals": primary["evals"]},
        "champion_full_errors": errs,
        "ablations": abl,
        "robustness_seeds": robust,
        "order_fixed_negative_twin": {"fitness": rfix["fitness"],
                                      "genome": rfix["genome"],
                                      "full_errors": errs_f},
        "value_domain_probe": {"n_episodes": len(rows_v3),
                               "fitness": probe["fitness"],
                               "genome": probe["genome"]},
        "nulls": null_stats,
        "seconds": time.time() - t0,
    }
    (HERE / "BLIND_OUTCOME_V1_T3.json").write_text(
        json.dumps(out, indent=1, sort_keys=True))
    print("T3 done in %.1fs: champion errors %d cost %d; null best errors %d"
          % (out["seconds"], primary["fitness"][0], primary["fitness"][1],
             min(null_stats["champion_errors"])))


def _null_ep_run(args):
    seed, rows, budget, cell_cap, mu, lam = args
    # null battery: redraw required outputs uniformly {0,1}
    rng_rows = []
    bit_outs = _null_bits(seed, len(rows))
    for r, y in zip(rows, bit_outs):
        rr = dict(r)
        rr["required_final_output"] = y
        rng_rows.append(rr)
    ts = _ep_taskset(rng_rows)
    return P2.evolve(ts, seed, budget, cell_cap, genome="stream",
                     mu=mu, lam=lam)


def _null_bits(seed, n):
    import random as _r
    rng = _r.Random(((seed + 1) * 2654435761) % (2 ** 32))
    return [rng.randint(0, 1) for _ in range(n)]


# ---------------------------------------------------------------------------
# TR-1
# ---------------------------------------------------------------------------

CONTR_FITNESS_N = 2000


def contr_hash_order(n_tasks):
    return sorted(range(n_tasks), key=lambda i: P2.frozen_hash(i))


def _contr_taskset(idx_list, layouts, required):
    return P2.IterTaskSet([layouts[i] for i in idx_list],
                          [required[i] for i in idx_list], 16)


_CONTR_CTX = None  # (idx_order, layouts, required) set pre-fork


def _contr_null_run(args):
    seed, budget = args
    idx, layouts, required = _CONTR_CTX
    sub = idx[:CONTR_FITNESS_N]
    bits = _null_bits(seed, len(sub))
    ts = P2.IterTaskSet([layouts[i] for i in sub], bits, 16)
    return P2.evolve(ts, seed, budget, 6, genome="iter", n_in=18, steps=16)


def _contr_crossover_run(args):
    size, mode, budget = args
    idx, layouts, required = _CONTR_CTX
    sub = idx[:size]
    if mode == "readout":
        ts = P2.IterTaskSet([layouts[i] for i in sub],
                            [required[i] for i in sub], 16)
        return {"size": size, "mode": mode,
                "result": P2.evolve(ts, 0, budget, 1, genome="iter", n_in=18,
                                    steps=16, readout_only=True)}
    ts = _contr_taskset(sub, layouts, required)
    return {"size": size, "mode": mode,
            "result": P2.evolve(ts, 0, budget, 6, genome="iter", n_in=18,
                                steps=16)}


def _contr_param_run(args):
    seed, mu, lam, budget = args
    idx, layouts, required = _CONTR_CTX
    sub = idx[:CONTR_FITNESS_N]
    ts = _contr_taskset(sub, layouts, required)
    return P2.evolve(ts, seed, budget, 6, genome="iter", n_in=18, steps=16,
                     mu=mu, lam=lam)


def run_t1():
    global _CONTR_CTX
    t0 = time.time()
    bc = BAT["batteries"]["B_CONTR"]
    layouts = bc["task_cell_layouts"]
    required = [r[3] for r in bc["task_rows"]]
    n = len(required)

    # certificates
    certs = P.contr_readout_certs(layouts, required, max_nz=4)

    # fitness subset + primary search
    idx = contr_hash_order(n)
    _CONTR_CTX = (idx, layouts, required)
    fit_idx = idx[:CONTR_FITNESS_N]
    ts = _contr_taskset(fit_idx, layouts, required)
    primary = P2.evolve(ts, 0, BUDGET_PRIMARY, 6, genome="iter", n_in=18,
                        steps=16)
    # champion full-battery verification
    full_ts = P2.IterTaskSet(layouts, required, 16)
    if primary["fitness"][0] == 0:
        f, legal, _ = M.batch_sim_iter(primary["genome"], full_ts.X, np)
        pred = f[:, primary["genome"]["output_cell"]]
        full_errs = int(np.count_nonzero(pred != full_ts.y)) + \
            int(np.count_nonzero(~legal)) * (n + 1)
    else:
        full_errs = None

    # parallel: ablations, robustness, crossover, nulls (fork-inherited ctx)
    param_args = [(0, 8, 32, BUDGET_PRIMARY), (0, 32, 128, BUDGET_PRIMARY)] +         [(s, 16, 64, BUDGET_PRIMARY // 2) for s in range(1, 5)]
    sizes = [1, 8, 64, 512, 4096, 17424]
    cross_args = [(s, m, BUDGET_CROSSOVER) for s in sizes
                  for m in ("full", "readout")]
    null_args = [(s, BUDGET_NULL) for s in NULL_SEEDS]
    with mp.Pool(min(12, os.cpu_count() or 4)) as pool:
        param_runs = pool.map(_contr_param_run, param_args)
        cross = pool.map(_contr_crossover_run, cross_args)
        null_runs = pool.map(_contr_null_run, null_args)
    abl = {"mu8_lam32": {"fitness": param_runs[0]["fitness"],
                         "genome": param_runs[0]["genome"]},
           "mu32_lam128": {"fitness": param_runs[1]["fitness"],
                           "genome": param_runs[1]["genome"]}}
    robust = [{"seed": s, "fitness": r["fitness"]}
              for s, r in zip(range(1, 5), param_runs[2:])]

    # multi-successor witness slice (battery-declared; blind relabeling)
    succ = bc["successor_census"]

    out = {
        "schema": "FDT_BLIND_OUTCOME_T1_V1",
        "benchmark_or_family_data_used": False,
        "battery": "B_CONTR",
        "n_tasks": n,
        "readout_certificates": certs,
        "fitness_subset_rule": "first 2000 task indices in frozen-hash(i) order",
        "primary": {"fitness": primary["fitness"], "genome": primary["genome"],
                    "evals": primary["evals"],
                    "distinct_genomes": primary["distinct_genomes_evaluated"]},
        "champion_full_errors": full_errs,
        "ablations": abl,
        "robustness_seeds": robust,
        "crossover": [{"size": c["size"], "mode": c["mode"],
                       "fitness": c["result"]["fitness"],
                       "genome": c["result"]["genome"]}
                      for c in cross],
        "nulls": {"budget": BUDGET_NULL,
                  "champion_errors": [r["fitness"][0] for r in null_runs],
                  "champion_costs": [r["fitness"][1] for r in null_runs]},
        "battery_successor_census": succ,
        "seconds": time.time() - t0,
    }
    (HERE / "BLIND_OUTCOME_V1_T1.json").write_text(
        json.dumps(out, indent=1, sort_keys=True))
    print("T1 done in %.1fs: champion fitness %s; certs %s"
          % (out["seconds"], primary["fitness"],
             {k: len(v) if isinstance(v, list) else v
              for k, v in certs.items() if k != "n_supports"}))


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    log = ["# Receipts run log", "",
           "host: %s" % platform.node(),
           "python: %s" % platform.python_version(),
           "numpy: %s" % np.__version__,
           "battery_sha256: %s" % sha256_file(HERE /
                                              "NEUTRAL_BATTERY_FREEZE_V1.json"),
           "started: %s" % time.strftime("%Y-%m-%dT%H:%M:%S"), ""]
    if which in ("t2", "all"):
        run_t2()
        log.append("T2 ok sha256=%s" %
                   sha256_file(HERE / "BLIND_OUTCOME_V1_T2.json"))
    if which in ("t3", "all"):
        run_t3()
        log.append("T3 ok sha256=%s" %
                   sha256_file(HERE / "BLIND_OUTCOME_V1_T3.json"))
    if which in ("t1", "all"):
        run_t1()
        log.append("T1 ok sha256=%s" %
                   sha256_file(HERE / "BLIND_OUTCOME_V1_T1.json"))
    log.append("finished: %s" % time.strftime("%Y-%m-%dT%H:%M:%S"))
    (HERE / "RECEIPTS_RUN_LOG.md").write_text("\n".join(log) + "\n")


if __name__ == "__main__":
    main()
