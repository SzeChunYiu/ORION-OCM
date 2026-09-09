"""P6 revival re-test (FNA4_FREEZE_ADDENDUM_V3.json, declared before running).

Run 3 proved the frozen repeat-rate sweep unmeasurable at every r>0: its coverage
axis (a macro solving a task single-handedly) is empty for the fragment library
STITCH admits. The revival axis, declared pre-run: a stream task is repeat-covered
iff some checker-passing chain the incumbent RAN during acquisition reproduces
that task's goal on its own payload. Everything else -- solver, charges, caps,
streams, r_grid, dual acquisition accounting -- is the frozen run 3 machinery,
imported not copied. Execute on an off-Mac host:

    python3 run_fna4_sweep_r2.py <output_dir>
"""
from __future__ import annotations

import json
import random
import sys
import traceback
from pathlib import Path

from fna4 import Work, gen_task, run_chain, Misfire
from fna4_solver import solve_task
import fna4_learners as L
import run_fna4 as R

SWEEP2_BASE = R.SALT_SWEEP + 2000          # disjoint from the frozen sweep salt
OUT = None


def _dump(res):
    (OUT / "FNA4_SWEEP_R2_PARTIAL.json").write_text(
        json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")


def repeat_covered(exhibited, task):
    """Composition-level repeat: a chain the incumbent ran during acquisition
    reproduces this task's goal on this task's own payload."""
    for c in exhibited:
        try:
            if run_chain(c, task.initial) == task.goal:
                return True
        except (Misfire, KeyError, ValueError, IndexError):
            continue
    return False


def build_stream(exhibited, macros_unused, r, ri):
    """24 tasks (12 F1 + 12 F2), round(r*24) of them repeat-covered, fresh payloads.
    Rejection-samples covered draws from the revival salt; uncovered tasks force
    parameter tuples no exhibited chain covers. None if not constructible."""
    need_cov = int(round(r * R.STREAM_LEN))
    per_family = R.STREAM_LEN // 2
    need_cov_f = need_cov // 2 + (1 if need_cov % 2 and r > 0 else 0)
    rng = random.Random(SWEEP2_BASE + 1000 * ri)
    tasks = []
    for family, space in (("F1", R._f1_param_space()), ("F2", R._f2_param_space())):
        ncov = need_cov_f if family == "F1" else need_cov - need_cov_f
        ncov = max(0, min(per_family, ncov))
        nun = per_family - ncov
        got_cov = got_un = 0
        tries = 0
        while got_cov < ncov and tries < 4000:
            tries += 1
            t = gen_task(rng, family, "R2-%s-%d-%d" % (family, ri, got_cov + got_un))
            if repeat_covered(exhibited, t):
                tasks.append(t)
                got_cov += 1
        for force in space:
            if got_un >= nun:
                break
            t = gen_task(rng, family, "R2-%s-%d-u%d" % (family, ri, got_un),
                         force=dict(force))
            if not repeat_covered(exhibited, t):
                tasks.append(t)
                got_un += 1
        if got_cov < ncov or got_un < nun:
            return None, (got_cov, ncov, got_un, nun)
    return tasks, None


def main():
    res = {"schema": "ocm.fna.fna4.sweep-r2.v1",
           "declared_in": "FNA4_FREEZE_ADDENDUM_V3.json", "points": []}
    try:
        # frozen acquisition (deterministic: identical corpus and library to run 3)
        w = Work()
        acq_receipts = [solve_task(t, work=w, collect_all=True)
                        for t in R.acquisition_stream()]
        exhibited = []
        for rr in acq_receipts:
            for c in rr["all_solution_chains"]:
                if tuple(c) not in exhibited:
                    exhibited.append(tuple(c))
        wl = Work()
        macros = L.learn_stitch(acq_receipts, wl)
        res["acquisition_work_full"] = w.as_dict()
        res["stitch_learner_units"] = wl.as_dict()
        res["exhibited_chains"] = len(exhibited)
        res["library"] = [m.as_dict() for m in macros]
        _dump(res)

        for ri, r in enumerate(R.R_GRID):
            tasks, fail = build_stream(exhibited, macros, r, ri)
            if tasks is None:
                res["points"].append({"r": r, "constructible": False,
                                      "got_need": fail})
                _dump(res)
                continue
            no_w = arm_w = hits = cov_hits = 0
            for t in tasks:
                no_w += solve_task(t)["work"]["total_units"]
                rr = solve_task(t, macros=macros)
                arm_w += rr["work"]["total_units"]
                hits += rr["macro_hits"]
                if repeat_covered(exhibited, t):
                    cov_hits += rr["macro_hits"]
            acq_marg = (w.as_dict()["learner_steps"] + wl.as_dict()["learner_steps"])
            save = no_w - arm_w
            spt = save / len(tasks)
            res["points"].append({
                "r": r, "constructible": True,
                "n": len(tasks),
                "repeat_covered": sum(1 for t in tasks if repeat_covered(exhibited, t)),
                "no_library_total": no_w, "with_library_total": arm_w,
                "saving": save, "saving_per_task": spt,
                "macro_hits": hits, "macro_hits_on_covered": cov_hits,
                "acquisition_marginal_units": acq_marg,
                "break_even_tasks_marginal": (acq_marg / spt) if spt > 0 else None,
                "payback_marginal": save - acq_marg})
            _dump(res)
        (OUT / "FNA4_SWEEP_R2_RECEIPTS.json").write_text(
            json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
        return res
    except Exception:
        res["crash"] = traceback.format_exc()
        _dump(res)
        raise


if __name__ == "__main__":
    OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    main()
    print("done")
