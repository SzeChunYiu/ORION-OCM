"""Attribution probe (unscored, read-only) for the r2-sweep inversion: on the r=1.0
revival stream, is the with-library harm concentrated on tasks the incumbent solves
cheaply (covered-by-shallow-coincidence), as hypothesised?  Run from capsule dir.
"""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

from fna4 import Work, gen_task
from fna4_solver import solve_task
import fna4_learners as L
import run_fna4 as R
import run_fna4_sweep_r2 as S2
import random

w = Work()
acq = [solve_task(t, work=w, collect_all=True) for t in R.acquisition_stream()]
exhibited = []
for rr in acq:
    for c in rr["all_solution_chains"]:
        if tuple(c) not in exhibited:
            exhibited.append(tuple(c))
macros = L.learn_stitch(acq, Work())

# rebuild the r=1.0 stream deterministically (same salt path as the scored sweep)
tasks, _fail = S2.build_stream(exhibited, macros, 1.0, 4)
print("n=%d covered=%d" % (len(tasks), sum(1 for t in tasks if S2.repeat_covered(exhibited, t))))
print("%-12s %-3s %-6s %10s %10s %8s %6s" % ("task", "fam", "cov", "no_lib", "with_lib", "delta", "hits"))
for t in tasks:
    a = solve_task(t)["work"]["total_units"]
    b = solve_task(t, macros=macros)
    bu = b["work"]["total_units"]
    print("%-12s %-3s %-6s %10d %10d %8d %6d" % (
        t.task_id, t.family, S2.repeat_covered(exhibited, t), a, bu, bu - a,
        b["macro_hits"]))
