#!/usr/bin/env python3
"""RV-A throughput probe: measure per-genome cost of T2 + T3 evaluation over a
deterministic prefix of the GS bound, and report the closed-form bound size.
Offline; no network. Usage: python3 rva_timing.py <CAPSULE_ROOT> <N>"""
from __future__ import annotations
import json, os, sys, time

ROOT = os.path.abspath(sys.argv[1]); sys.path.insert(0, ROOT)
N = int(sys.argv[2]) if len(sys.argv) > 2 else 2000

from morphology.gs_bound import enumerate_gs_bound, gs_bound_closed_form_size  # noqa
from evaluation.evaluate import evaluate_genome  # noqa
from evaluation.t3_ecology import evaluate_t3  # noqa

freeze = json.load(open(os.path.join(ROOT, "GRAND_SEARCH_R2_FREEZE.json")))
T3KEY = freeze["t3_key"]

t0 = time.time(); n_enum = 0; gens = []
for g in enumerate_gs_bound((0, 1)):
    gens.append(g); n_enum += 1
    if n_enum >= N:
        break
t_enum = time.time() - t0

t0 = time.time(); n_t2 = 0; n_viable = 0
for g in gens:
    r = evaluate_genome(g, tier="T2", use_cache=False); n_t2 += 1
    if r["feasible"]:
        n_viable += 1
t_t2 = time.time() - t0

t0 = time.time(); n_t3 = 0
for g in gens[:min(500, len(gens))]:
    evaluate_t3(g, T3KEY); n_t3 += 1
t_t3 = time.time() - t0

size = gs_bound_closed_form_size()
per_t2 = t_t2 / max(1, n_t2); per_t3 = t_t3 / max(1, n_t3); per_en = t_enum / max(1, n_enum)
out = {
    "probe_id": "RVA_THROUGHPUT_V1",
    "gs_bound_closed_form_size": size,
    "n_enumerated": n_enum, "n_t2": n_t2, "n_t3": n_t3,
    "viable_fraction_prefix": round(n_viable / max(1, n_t2), 6),
    "sec_per_enumerate": round(per_en, 8),
    "sec_per_T2_eval": round(per_t2, 8),
    "sec_per_T3_eval": round(per_t3, 8),
    "projected_cpu_hours_full_bound_enum_plus_T2_plus_T3":
        round(size * (per_en + per_t2 + per_t3) / 3600.0, 3),
    "projected_cpu_hours_enum_plus_T2_only":
        round(size * (per_en + per_t2) / 3600.0, 3),
    "python": sys.version.split()[0],
}
print(json.dumps(out, indent=1, sort_keys=True))
