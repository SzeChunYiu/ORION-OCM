#!/usr/bin/env python3
"""RV-A iteration 2b: exhaustive census of GS_BOUND_V1.

Enumerates every legal grammar in the frozen GS search bound (closed form
143,881,920 before the compile-legality filter), evaluates each at T2 and on the
frozen held-out T3 key, and records the composition of the viable set.

Purpose: the ABSOLUTE ceiling |{T2-viable AND T3-HOLD}| over the whole search
space, and the exhaustive version of the A1 equivalence.  This is a ceiling and
a composition artifact, NOT the null -- a search evaluating ~1e5 candidates out
of 1.4e8 finds a tiny fraction by budget alone, so the raw ceiling cannot by
itself discriminate bias from budget.

Shard i of n covers the grammars whose flat enumeration index satisfies
idx % n == i, exactly as enumerate_gs_bound's own sharding does.

Offline; no network.  Usage:
  python3 rva_census.py <CAPSULE_ROOT> <SHARD_I> <SHARD_N> <OUT_JSON> <OUT_JSONL>
"""
from __future__ import annotations

import collections
import json
import os
import sys
import time

ROOT = os.path.abspath(sys.argv[1])
sys.path.insert(0, ROOT)
SI, SN = int(sys.argv[2]), int(sys.argv[3])
OUT = os.path.abspath(sys.argv[4])
OUTL = os.path.abspath(sys.argv[5])

from morphology.gs_bound import enumerate_gs_bound            # noqa: E402
from evaluation.evaluate import evaluate_genome               # noqa: E402
from evaluation.t3_ecology import evaluate_t3                 # noqa: E402
from evaluation.lifetime2 import _capabilities                # noqa: E402
from evaluation.lifetime import Sim                           # noqa: E402
from morphology.compile import compile_genome                 # noqa: E402

freeze = json.load(open(os.path.join(ROOT, "GRAND_SEARCH_R2_FREEZE.json")))
T3KEY = freeze["t3_key"]


def main():
    t0 = time.time()
    n_legal = n_viable = 0
    n_cc = 0
    ct = collections.Counter()          # (can_check, viable)
    t3ct = collections.Counter()        # (can_check, verdict) over viable
    farch_v = collections.Counter()
    farch_hold = collections.Counter()
    impossible = []
    seen = {}                           # phenotype prefix -> (cc, F_arch, hold)
    fl = open(OUTL, "w")
    for g in enumerate_gs_bound((SI, SN)):
        n_legal += 1
        try:
            org = compile_genome(g)
            cc = _capabilities(Sim(org))["can_check"]
            r = evaluate_genome(g, tier="T2", use_cache=False)
        except Exception:
            continue
        n_cc += 1 if cc else 0
        viable = bool(r["feasible"])
        ct[(cc, viable)] += 1
        if not viable:
            continue
        n_viable += 1
        farch_v[g.F_arch] += 1
        r3 = evaluate_t3(g, T3KEY)
        hold = bool(r3["feasible"])
        t3ct[(cc, "HOLD" if hold else "FAIL")] += 1
        if hold:
            farch_hold[g.F_arch] += 1
        if (not cc) and g.F_arch != "hierarchical_fibred" and len(impossible) < 20:
            impossible.append({"F_arch": g.F_arch, "L": g.L,
                               "phenotype_digest": r["phenotype_digest"]})
        pref = r["phenotype_digest"][:16]
        if pref not in seen:
            seen[pref] = 1
            fl.write("%s %d %s %d\n" % (pref, 1 if cc else 0, g.F_arch,
                                        1 if hold else 0))
    fl.close()
    out = {
        "study_id": "RV_A_CENSUS_ITER2B",
        "protocol_freeze": "FREEZE_RVA_ITER2B.json",
        "shard": [SI, SN],
        "n_legal_enumerated": n_legal,
        "n_can_check": n_cc,
        "n_viable": n_viable,
        "n_distinct_viable_phenotype_prefixes_in_shard": len(seen),
        "viable_by_can_check": {"%s|%s" % k: v for k, v in sorted(ct.items())},
        "t3_by_can_check_over_viable": {
            "%s|%s" % k: v for k, v in sorted(t3ct.items())},
        "farch_viable": dict(farch_v),
        "farch_hold": dict(farch_hold),
        "falsifier_viable_without_check_and_without_fibred": {
            "n_found": len(impossible), "samples": impossible, "expected": 0},
        "wall_seconds": round(time.time() - t0, 3),
    }
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in out.items() if k != "farch_viable"},
                     sort_keys=True))


if __name__ == "__main__":
    main()
