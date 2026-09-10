#!/usr/bin/env python3
"""RV-A: recompute the survivor comparator at the ACTIVE-unit level, so the
null (which measures the compiled organism's can_check) and the comparator are
like-for-like.

The A1 attribution derived can_check from grammar_signature (genome level).  The
P3 preflight found genome and active levels agree on a 4000-survivor sample; this
recomputes it on ALL distinct survivors so no sampling caveat remains.

Offline; no network.  Usage: python3 rva_comparator.py <CAPSULE_ROOT> <OUT>
"""
from __future__ import annotations

import collections
import glob
import json
import math
import os
import sys

ROOT = os.path.abspath(sys.argv[1]); sys.path.insert(0, ROOT)
OUT = os.path.abspath(sys.argv[2])
RES = os.path.join(ROOT, "results")

from morphology.schema import OCMMorphologyGenomeV1           # noqa: E402
from morphology.compile import compile_genome                 # noqa: E402
from evaluation.lifetime2 import _capabilities                # noqa: E402
from evaluation.lifetime import Sim                           # noqa: E402


def wilson(k, n, z=1.959963984540054):
    p = k / n; d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(max(0.0, c - h), 8), round(min(1.0, c + h), 8))


def main():
    agg = json.load(open(os.path.join(RES, "GS_R2_AGGREGATE.json")))
    verdict = {t["phenotype_digest"]: t["verdict"] for t in agg["t3_verdicts"]}
    pool = {}
    for fp in sorted(glob.glob(os.path.join(RES, "GS_R2_*_s?.json"))):
        if "AGGREGATE" in fp or "RECEIPTS" in fp:
            continue
        for sv in json.load(open(fp)).get("survivors", []):
            pool.setdefault(sv["phenotype_digest"], sv)
    ct = collections.Counter()      # (genome_level, active_level, verdict)
    n = 0
    for ph, sv in pool.items():
        g = OCMMorphologyGenomeV1.from_json_obj(sv["genome"])
        parts = sv["grammar_signature"].split("|")
        ex = frozenset(x for x in parts[1].split(",") if x)
        gen = ("constraint_solver" in ex) or (parts[4] == "scoped_nogood")
        act = _capabilities(Sim(compile_genome(g)))["can_check"]
        ct[(gen, act, "FAIL" if verdict[ph].endswith("FAIL") else "HOLD")] += 1
        n += 1
    act_k = sum(v for (_, a, _), v in ct.items() if a)
    gen_k = sum(v for (gk, _, _), v in ct.items() if gk)
    hold = sum(v for (_, _, w), v in ct.items() if w == "HOLD")
    disagree = sum(v for (gk, a, _), v in ct.items() if gk != a)
    out = {
        "study_id": "RV_A_COMPARATOR_ACTIVE_LEVEL",
        "n_distinct_survivors": n,
        "crosstab_genome_active_verdict": {
            "%s|%s|%s" % k: v for k, v in sorted(ct.items())},
        "genome_level_can_check": gen_k,
        "active_level_can_check": act_k,
        "levels_disagree": disagree,
        "levels_identical_on_survivors": disagree == 0,
        "t3_hold": hold,
        "active_can_check_equals_hold": act_k == hold,
        "comparator_active_level_fraction": round(act_k / n, 8),
        "comparator_active_level_wilson95": wilson(act_k, n),
    }
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
