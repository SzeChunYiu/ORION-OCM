"""RV-8 analysis. Declared in the freeze commit, BEFORE any scored cell runs, so the
endpoints cannot be chosen after seeing the surface.

    python3 rv8_analyse.py <out_dir>

Endpoints, all pre-registered:

  present cost      acquisition, reported in BOTH of FNA-4's accountings --
                    full (the deliberate exhaustive experience formation pays its whole
                    search) and marginal (the acquisition solves are the job's cost,
                    paid identically by a non-learning system, so consolidation adds
                    only learner and bookkeeping units).
  future reuse      cumulative PAIRED saving over the stream, arm vs NO_LIBRARY on the
                    SAME task at the SAME position. Never netted against present cost
                    before both are reported.
  crossover N*      smallest N with cumulative saving >= acquisition. Reported against
                    both accountings, with a bootstrap CI, and reported as ">N_max, none
                    observed" when no crossing occurs -- never extrapolated.
  critical mix      zero-crossing of saving/task in the mix, with a CI. Below it no
                    horizon pays, so N* has a vertical asymptote there; the surface
                    therefore carries TWO different quantities on its two halves and
                    both are reported as such.
  windowed saving   saving/task in disjoint windows, to separate a stationary crossover
                    from a decaying transient (the misfire registry saturates and CEGIS
                    domains shrink monotonically).
  capped tasks      count per cell, plus the pre-registered sensitivity pass that
                    recomputes every endpoint excluding capped tasks. INCUMBENT_CAP was
                    sized from 4 F2 draws; at 131,072 draws the tail is sampled far
                    deeper, and a capped task's cost is TRUNCATED, which biases the
                    baseline down and understates the library's saving.
  null              SHUFFLE_NULL / SHUFFLE_NULL_NC vs their learned counterparts. A
                    saving reproduced by a shape-matched random library is selectivity,
                    not payback.
"""
from __future__ import annotations

import gzip
import json
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rv8_horizon import (COMPOSITIONS, FULL_ARMS, HORIZON_LADDER, MIX_GRID,  # noqa: E402
                         NULL_ARMS, NULL_SEEDS, N_FULL, N_REDUCED, REDUCED_ARMS,
                         STREAM_SEEDS, SCHEMA, cell_inventory)

BOOT = 2000
BOOT_SEED = 815001


def load(out):
    cells = {}
    for i, spec in enumerate(cell_inventory()):
        p = out / "cells" / ("cell_%05d.json.gz" % i)
        if not p.exists():
            continue
        with gzip.open(str(p), "rt") as fh:
            c = json.load(fh)
        cells[(c["arm"], c["mix_idx"], c["composition"], c["seed"],
               c["null_seed"])] = c
    return cells


#: Above this sample size the bootstrap is replaced by the normal-approximation CI on
#: the mean. Per-task cost has bounded support (INCUMBENT_CAP truncates the tail), so
#: the variance is finite and the CLT applies; a 2,000x resample of 655,360 draws is
#: 1.3e9 operations for no extra information. Frozen before any scored cell.
BOOT_MAX_N = 20000


def _boot_mean_ci(xs, rng, alpha=0.05):
    """Mean with a 95% CI. Bootstrap for small samples, normal approximation for large
    ones (the crossover point is a function of the MEAN saving, so this is a CI on the
    mean, not on the per-task distribution)."""
    if not xs:
        return None, None, None
    n = len(xs)
    mean = sum(xs) / float(n)
    if n <= BOOT_MAX_N:
        means = []
        for _ in range(BOOT):
            s = 0.0
            for _ in range(n):
                s += xs[rng.randrange(n)]
            means.append(s / float(n))
        means.sort()
        return (mean, means[int(alpha / 2 * BOOT)],
                means[min(BOOT - 1, int((1 - alpha / 2) * BOOT))])
    var = sum((x - mean) ** 2 for x in xs) / float(n - 1)
    se = math.sqrt(var / n)
    return mean, mean - 1.96 * se, mean + 1.96 * se


def crossover(savings, acq):
    """Smallest N with cumulative paired saving >= acq. None if never."""
    tot = 0
    for i, s in enumerate(savings):
        tot += s
        if tot >= acq:
            return i + 1
    return None


def n_star_ci(savings, acq, rng):
    """CI on N* from a bootstrap CI on saving/task. Infinite when the CI bound is
    non-positive: below the critical mix no horizon pays."""
    mean, lo, hi = _boot_mean_ci(savings, rng)
    def inv(v):
        return (acq / v) if (v is not None and v > 0) else None
    return {"saving_per_task": mean, "saving_per_task_ci95": [lo, hi],
            "n_star_point": inv(mean), "n_star_lo": inv(hi), "n_star_hi": inv(lo)}


def pair(cells, arm, mi, comp, seed, null_seed=None):
    base = cells.get(("NO_LIBRARY", mi, comp, seed, None))
    a = cells.get((arm, mi, comp, seed, null_seed))
    if base is None or a is None:
        return None
    bu, au = base["per_task"]["units"], a["per_task"]["units"]
    bc, ac = base["per_task"]["capped"], a["per_task"]["capped"]
    n = min(len(bu), len(au))
    return {"savings": [bu[i] - au[i] for i in range(n)],
            "capped_any": [1 if (bc[i] or ac[i]) else 0 for i in range(n)],
            "arm_units": au[:n], "base_units": bu[:n], "n": n,
            "acq_full": a["acquisition_full_units"],
            "acq_marginal": a["acquisition_marginal_units"],
            "arm_capped": sum(ac[:n]), "base_capped": sum(bc[:n]),
            "macro_hits": sum(a["per_task"]["macro_hits"][:n]),
            "complete": a.get("complete", False) and base.get("complete", False)}


def analyse(out):
    cells = load(out)
    rng = random.Random(BOOT_SEED)
    res = {"schema": SCHEMA, "phase": "analysis",
           "cells_loaded": len(cells), "cells_expected": len(cell_inventory()),
           "surface": [], "ladder": [], "null": [], "windows": []}

    arms = [a for a in FULL_ARMS if a != "NO_LIBRARY"] + list(REDUCED_ARMS) + \
        list(NULL_ARMS)
    for arm in arms:
        nseeds = NULL_SEEDS if arm in NULL_ARMS else (None,)
        sseeds = (STREAM_SEEDS[0],) if arm in NULL_ARMS else STREAM_SEEDS
        for mi, mix in enumerate(MIX_GRID):
            for comp in COMPOSITIONS:
                for ns in nseeds:
                    per_seed, allsav, allcap = [], [], []
                    acq_f = acq_m = None
                    hits = arm_cap = base_cap = 0
                    for s in sseeds:
                        p = pair(cells, arm, mi, comp, s, ns)
                        if p is None:
                            continue
                        acq_f, acq_m = p["acq_full"], p["acq_marginal"]
                        allsav.extend(p["savings"])
                        allcap.extend(p["capped_any"])
                        hits += p["macro_hits"]
                        arm_cap += p["arm_capped"]
                        base_cap += p["base_capped"]
                        per_seed.append({
                            "seed": s, "n": p["n"], "complete": p["complete"],
                            "saving_total": sum(p["savings"]),
                            "saving_per_task": sum(p["savings"]) / p["n"],
                            "n_star_marginal": crossover(p["savings"],
                                                         p["acq_marginal"]),
                            "n_star_full": crossover(p["savings"], p["acq_full"])})
                    if not per_seed:
                        continue
                    clean = [v for v, c in zip(allsav, allcap) if not c]
                    row = {"arm": arm, "mix": mix, "mix_idx": mi,
                           "composition": comp, "null_seed": ns,
                           "tasks_total": len(allsav),
                           "seeds": per_seed,
                           "present_cost_acquisition_full": acq_f,
                           "present_cost_acquisition_marginal": acq_m,
                           "future_reuse_cumulative_saving": sum(allsav),
                           "macro_hits": hits,
                           "capped_tasks_arm": arm_cap,
                           "capped_tasks_baseline": base_cap,
                           "marginal": n_star_ci(allsav, acq_m, rng),
                           "full": n_star_ci(allsav, acq_f, rng),
                           "sensitivity_excluding_capped": {
                               "n": len(clean),
                               "marginal": n_star_ci(clean, acq_m, rng)
                               if clean else None}}
                    res["surface"].append(row)

    # horizon ladder: cumulative saving vs present cost, pooled over stream seeds
    for arm in arms:
        nseeds = NULL_SEEDS if arm in NULL_ARMS else (None,)
        sseeds = (STREAM_SEEDS[0],) if arm in NULL_ARMS else STREAM_SEEDS
        for mi, mix in enumerate(MIX_GRID):
            for comp in COMPOSITIONS:
                for ns in nseeds:
                    ps = [pair(cells, arm, mi, comp, s, ns) for s in sseeds]
                    ps = [p for p in ps if p is not None]
                    if not ps:
                        continue
                    cap = N_REDUCED if arm in REDUCED_ARMS else N_FULL
                    pts = []
                    for N in HORIZON_LADDER:
                        if N > cap:
                            continue
                        vals = [sum(p["savings"][:N]) for p in ps if p["n"] >= N]
                        if not vals:
                            continue
                        pts.append({"N": N, "n_seeds": len(vals),
                                    "cum_saving_mean": sum(vals) / len(vals),
                                    "cum_saving_min": min(vals),
                                    "cum_saving_max": max(vals)})
                    res["ladder"].append({"arm": arm, "mix": mix, "composition": comp,
                                          "null_seed": ns,
                                          "present_cost_marginal": ps[0]["acq_marginal"],
                                          "present_cost_full": ps[0]["acq_full"],
                                          "points": pts})

    # windowed saving/task: stationary crossover vs decaying transient
    for arm in arms:
        if arm in NULL_ARMS:
            continue
        for mi, mix in enumerate(MIX_GRID):
            for comp in COMPOSITIONS:
                ps = [pair(cells, arm, mi, comp, s) for s in STREAM_SEEDS]
                ps = [p for p in ps if p is not None]
                if not ps:
                    continue
                nmin = min(p["n"] for p in ps)
                w = max(1, nmin // 8)
                wins = []
                for k in range(8):
                    lo, hi = k * w, min((k + 1) * w, nmin)
                    if lo >= hi:
                        break
                    vals = []
                    for p in ps:
                        vals.extend(p["savings"][lo:hi])
                    wins.append({"window": [lo, hi],
                                 "saving_per_task": sum(vals) / len(vals)})
                res["windows"].append({"arm": arm, "mix": mix, "composition": comp,
                                       "windows": wins})

    # null comparison: learned library vs shape-matched random library
    for null_arm, learned in (("SHUFFLE_NULL", "STITCH"),
                              ("SHUFFLE_NULL_NC", "STITCH_NOGOOD_CEGIS")):
        for mi, mix in enumerate(MIX_GRID):
            for comp in COMPOSITIONS:
                lp = pair(cells, learned, mi, comp, STREAM_SEEDS[0])
                if lp is None:
                    continue
                nulls = []
                for ns in NULL_SEEDS:
                    np_ = pair(cells, null_arm, mi, comp, STREAM_SEEDS[0], ns)
                    if np_ is None:
                        continue
                    n = min(lp["n"], np_["n"])
                    nulls.append({"null_seed": ns, "n": n,
                                  "saving_per_task": sum(np_["savings"][:n]) / n,
                                  "macro_hits": np_["macro_hits"]})
                if not nulls:
                    continue
                nm = sum(x["saving_per_task"] for x in nulls) / len(nulls)
                lm = sum(lp["savings"][:min(lp["n"], nulls[0]["n"])]) / \
                    min(lp["n"], nulls[0]["n"])
                res["null"].append({
                    "learned_arm": learned, "null_arm": null_arm, "mix": mix,
                    "composition": comp,
                    "learned_saving_per_task": lm,
                    "null_saving_per_task_mean": nm,
                    "null_seeds": nulls,
                    "learned_exceeds_null": lm > max(x["saving_per_task"]
                                                     for x in nulls)})

    # critical mix per arm/composition: zero-crossing of saving/task in the mix
    crit = []
    for arm in arms:
        if arm in NULL_ARMS:
            continue
        for comp in COMPOSITIONS:
            pts = sorted([(r["mix"], r["marginal"]["saving_per_task"],
                           r["marginal"]["saving_per_task_ci95"])
                          for r in res["surface"]
                          if r["arm"] == arm and r["composition"] == comp
                          and r["null_seed"] is None])
            xr = None
            for (m0, v0, c0), (m1, v1, c1) in zip(pts, pts[1:]):
                if v0 is not None and v1 is not None and v0 <= 0 < v1:
                    xr = m0 + (m1 - m0) * (0 - v0) / (v1 - v0)
                    break
            # saving/task rises with mix, so the UPPER CI bound on saving crosses zero
            # at the SMALLEST mix -> that crossing is the LOWER bound on critical mix,
            # and the lower CI bound on saving gives the upper bound on critical mix.
            lo = hi = None
            for (m0, _v0, c0), (m1, _v1, c1) in zip(pts, pts[1:]):
                if c0[1] is not None and c1[1] is not None and c0[1] <= 0 < c1[1]:
                    lo = m0 + (m1 - m0) * (0 - c0[1]) / (c1[1] - c0[1])
                if c0[0] is not None and c1[0] is not None and c0[0] <= 0 < c1[0]:
                    hi = m0 + (m1 - m0) * (0 - c0[0]) / (c1[0] - c0[0])
            crit.append({"arm": arm, "composition": comp,
                         "critical_mix": xr, "critical_mix_ci95": [lo, hi],
                         "grid": [{"mix": m, "saving_per_task": v} for m, v, _ in pts]})
    res["critical_mix"] = crit
    (out / "RV8_ANALYSIS.json").write_text(
        json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    return res


if __name__ == "__main__":
    o = Path(sys.argv[1]).resolve()
    r = analyse(o)
    print(json.dumps({"cells_loaded": r["cells_loaded"],
                      "cells_expected": r["cells_expected"],
                      "surface_rows": len(r["surface"]),
                      "critical_mix": r["critical_mix"]}, indent=1, default=str))
