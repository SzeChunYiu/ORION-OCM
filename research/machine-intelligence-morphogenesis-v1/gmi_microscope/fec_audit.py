"""RV-377-061 — soundness audit of the functional-equivalence cache used in RUN9 (RV-377-028).

The cache keyed candidates by a PROBE signature (10 development events on ONE of the four diversity targets, the served
outputs after events 5 and 10, and the final cell values) and reused the stored score for any later candidate with the
same signature. The full fitness is 32 events averaged over FOUR targets, so the probe is a strict coarsening and two
candidates can share a signature while differing on the fitness. This module measures how often that happens.
"""
from __future__ import annotations

import collections
import json
import os
import random

from . import blind, fast
from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")


def audit(n=4000, seed=21, probe=10):
    blind.G_DEPTH = 3; blind.set_bits(8)
    eco = blind.ecology_div(); rng = random.Random(seed)
    probe_target = eco["targets"][0]; probe_eco = dict(eco, kind="smooth")
    groups = collections.defaultdict(list)
    for _ in range(n):
        c = blind.rand_candidate(rng); fc = fast.compile_candidate(c)
        _, sig = fast.fast_score(fc, probe_eco, probe_target, 8, probe=probe)
        groups[sig].append(fast.fast_run_candidate(c, eco))
    multi = {k: v for k, v in groups.items() if len(v) > 1}
    bad = {k: v for k, v in multi.items() if max(v) - min(v) > 1e-9}
    wrong = sum(len(v) - 1 for v in bad.values())
    return {"n_candidates": n, "probe_events": probe, "distinct_signatures": len(groups), "shared_signatures": len(multi),
            "shared_signatures_with_differing_true_scores": len(bad), "max_score_spread_within_a_signature": round(max([max(v) - min(v) for v in multi.values()] or [0.0]), 4),
            "mean_score_spread_within_shared_signatures": round(sum(max(v) - min(v) for v in multi.values()) / max(len(multi), 1), 4),
            "candidates_that_would_inherit_a_wrong_score": wrong, "wrong_score_fraction": round(wrong / n, 4)}


def main(tag="V1"):
    res = {p: audit(probe=p) for p in (10, 16, 32)}
    out = {"schema": "StageFFECSoundnessAuditV1", "issue": [377, 422], "revival_record": "RV-377-061", "status": "EXECUTED_EXACT_AT_SCOPE",
           "grammar": {"n_bits": 8, "g_depth": 3, "n_cells": blind.N_CELLS}, "ecology": "E_smooth8_div (four sign-flipped targets, 32 events)",
           "audit_by_probe_length": res,
           "consequence": "the functional-equivalence cache is unsound at every probe length tested; it is disabled by default in gmi_microscope/fast.py from this record onward, and the RUN9 receipts (RV-377-028) are marked instrument-contaminated",
           "claim_ceiling": "random candidates of the registered grammar; the contamination rate under SELECTION may differ from the rate under random sampling"}
    out["receipt_sha256"] = sha256_of({k: v for k, v in out.items() if k != "receipt_sha256"})
    json.dump(out, open(os.path.join(RES, f"STAGE_F_FEC_AUDIT_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    for p, r in res.items(): print("probe", p, r)
    return out


if __name__ == "__main__":
    main()
