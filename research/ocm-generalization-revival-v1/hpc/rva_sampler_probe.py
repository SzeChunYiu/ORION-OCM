#!/usr/bin/env python3
"""RV-A falsifier follow-up: why does the measured lane_hetero can_check rate
(0.33825) differ from the frozen analytic expectation (0.37037)?

Hypothesis: _capabilities reads Sim(org).types, i.e. the ACTIVE unit types of
the COMPILED organism.  compile_genome prunes dead units, so a constraint_solver
present in the genome can be absent from the active set.  The analytic value was
derived at the genome level and therefore over-counts.

This probe measures both levels on the same draws and reports the constants the
analytic value depends on, so the discrepancy is either explained exactly or the
sampler really is not what the protocol assumed.

Offline; no network.  Usage: python3 rva_sampler_probe.py <CAPSULE_ROOT> <N> <OUT>
"""
from __future__ import annotations

import collections
import json
import os
import random
import sys

ROOT = os.path.abspath(sys.argv[1]); sys.path.insert(0, ROOT)
N = int(sys.argv[2])
OUT = os.path.abspath(sys.argv[3])

from morphology.gs_bound import GS_BOUND_V1, lane_hetero      # noqa: E402
from morphology.schema import LEARNING_FAMILIES               # noqa: E402
from morphology.compile import compile_genome                 # noqa: E402
from evaluation.lifetime2 import _capabilities                # noqa: E402
from evaluation.lifetime import Sim                           # noqa: E402

rng = random.Random(0)
n = 0
ct = collections.Counter()          # (genome_level, active_level)
nex = collections.Counter()         # n_extras histogram
dead_cs = 0
while n < N:
    g = lane_hetero(rng)
    n += 1
    ex = [u.unit_type for u in g.U if u.unit_type != "fact_relation"]
    nex[len(ex)] += 1
    gen_cc = ("constraint_solver" in ex) or (g.L == "scoped_nogood")
    org = compile_genome(g)
    act_cc = _capabilities(Sim(org))["can_check"]
    ct[(gen_cc, act_cc)] += 1
    if "constraint_solver" in ex and "constraint_solver" not in org.active_unit_types:
        dead_cs += 1

gen_rate = sum(v for (a, _), v in ct.items() if a) / n
act_rate = sum(v for (_, b), v in ct.items() if b) / n
out = {
    "probe_id": "RVA_SAMPLER_FALSIFIER_FOLLOWUP",
    "n_draws": n,
    "constants": {
        "max_extra_units": GS_BOUND_V1["max_extra_units"],
        "n_extra_unit_types": len(GS_BOUND_V1["extra_units"]),
        "n_learning_families": len(GS_BOUND_V1["L"]),
        "learning_families_total_in_schema": len(LEARNING_FAMILIES),
        "scoped_nogood_in_bound": "scoped_nogood" in GS_BOUND_V1["L"]},
    "n_extras_histogram": dict(nex),
    "genome_level_can_check_rate": round(gen_rate, 8),
    "active_level_can_check_rate": round(act_rate, 8),
    "crosstab_genome_vs_active": {"%s|%s" % k: v for k, v in sorted(ct.items())},
    "genome_true_active_false": ct[(True, False)],
    "active_true_genome_false": ct[(False, True)],
    "constraint_solver_pruned_as_dead": dead_cs,
    "read": ("if genome_level matches the frozen analytic value and active_level "
             "matches the null's measured value, the discrepancy is entirely "
             "dead-unit pruning in compile_genome and the sampler is exactly "
             "lane_hetero as the protocol assumed"),
}
with open(OUT, "w") as fh:
    json.dump(out, fh, indent=1, sort_keys=True)
print(json.dumps(out, indent=1, sort_keys=True))
