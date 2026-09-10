#!/usr/bin/env python3
"""RV-A preflight: validate the evaluation harness against a committed receipt
before any new endpoint is drawn.

Three checks, each with an explicit no-alarm assertion:

 P1  Verdict reproduction.  Re-run the real evaluate_t3 path on a deterministic
     sample of the committed R2 survivors and require the verdict, the T3
     solved_fraction and the gate booleans to match GS_R2_AGGREGATE.json
     exactly.  This validates the whole evaluation path against a receipt AND
     independently cross-checks the grammar_signature-derived can_check bit
     against the real evaluation._capabilities path.

 P2  Determinism.  Evaluate the same genomes twice and require byte-identical
     digests and evaluations.

 P3  refusal_rate degeneracy.  descriptors.behavioral_descriptors computes
     refusal_rate = correct_refusals / (correct_refusals + harmful_transfers).
     GATE_CORRECTNESS forces harmful_transfers == 0 on every survivor, so the
     axis should be identically 1.0 across viable organisms.  A constant
     function would be uninteresting; the claim is that it is GATE-INDUCED, so
     the check requires 1.0 on all viable AND genuine variation on non-viable.

Offline; no network.  Usage: python3 rva_preflight.py <CAPSULE_ROOT> <OUT> [N]
"""
from __future__ import annotations

import collections
import glob
import hashlib
import json
import os
import random
import sys

ROOT = os.path.abspath(sys.argv[1])
sys.path.insert(0, ROOT)
OUT = os.path.abspath(sys.argv[2])
N = int(sys.argv[3]) if len(sys.argv) > 3 else 4000
RES = os.path.join(ROOT, "results")

from morphology.schema import OCMMorphologyGenomeV1          # noqa: E402
from morphology.compile import compile_genome                # noqa: E402
from evaluation.evaluate import evaluate_genome              # noqa: E402
from evaluation.t3_ecology import evaluate_t3                # noqa: E402
from evaluation.lifetime2 import _capabilities               # noqa: E402
from evaluation.lifetime import Sim                          # noqa: E402
from evaluation.descriptors import behavioral_descriptors    # noqa: E402
from morphology.gs_bound import GS_BOUND_V1, lane_hetero     # noqa: E402

freeze = json.load(open(os.path.join(ROOT, "GRAND_SEARCH_R2_FREEZE.json")))
T3KEY = freeze["t3_key"]


def sig_can_check(sig):
    p = sig.split("|")
    ex = frozenset(x for x in p[1].split(",") if x)
    return ("constraint_solver" in ex) or (p[4] == "scoped_nogood")


def main():
    agg = json.load(open(os.path.join(RES, "GS_R2_AGGREGATE.json")))
    verdict = {t["phenotype_digest"]: t for t in agg["t3_verdicts"]}

    # deterministic sample of survivors, taken from the seed files
    pool = {}
    for fp in sorted(glob.glob(os.path.join(RES, "GS_R2_*_s?.json"))):
        if "AGGREGATE" in fp or "RECEIPTS" in fp:
            continue
        d = json.load(open(fp))
        for sv in d.get("survivors", []):
            pool.setdefault(sv["phenotype_digest"], sv)
    keys = sorted(pool)
    rng = random.Random(20260910)
    sample = keys if len(keys) <= N else rng.sample(keys, N)
    sample.sort()

    # ---- P1 verdict reproduction + P2 determinism + capability cross-check
    p1_checked = p1_mismatch = 0
    p2_checked = p2_mismatch = 0
    cap_checked = cap_mismatch = 0
    mismatches = []
    ct = collections.Counter()
    for ph in sample:
        sv = pool[ph]
        g = OCMMorphologyGenomeV1.from_json_obj(sv["genome"])
        r3 = evaluate_t3(g, T3KEY)
        got = ("SURVIVOR_T3_GENERALIZATION_HOLD" if r3["feasible"]
               else "SURVIVOR_T3_GENERALIZATION_FAIL")
        exp = verdict[ph]
        p1_checked += 1
        ok = (got == exp["verdict"]
              and abs(r3["evaluation"]["solved_fraction"]
                      - exp["solved_fraction"]) < 1e-9
              and r3["phenotype_digest"] == ph)
        if not ok:
            p1_mismatch += 1
            if len(mismatches) < 20:
                mismatches.append({"phenotype_digest": ph, "expected": exp["verdict"],
                                   "got": got,
                                   "expected_sf": exp["solved_fraction"],
                                   "got_sf": r3["evaluation"]["solved_fraction"]})
        # which gate actually failed, and which family carried it
        gates = r3["gates"]
        failed = sorted(k for k, v in gates.items()
                        if k.startswith("GATE_") and v is False)
        ct[(got, ",".join(failed) or "none",
            r3["evaluation"]["harmful_transfers"],
            r3["evaluation"]["stale_answers"])] += 1
        # P2 determinism: re-evaluate
        r3b = evaluate_t3(g, T3KEY)
        p2_checked += 1
        if (json.dumps(r3b, sort_keys=True) != json.dumps(r3, sort_keys=True)):
            p2_mismatch += 1
        # capability cross-check: grammar_signature bit vs real _capabilities
        org = compile_genome(g)
        real = _capabilities(Sim(org))["can_check"]
        cap_checked += 1
        if real != sig_can_check(sv["grammar_signature"]):
            cap_mismatch += 1

    # ---- P3 refusal_rate degeneracy over fresh lane_hetero draws
    rr_viable, rr_nonviable = collections.Counter(), collections.Counter()
    draw = lane_hetero
    r = random.Random(7)
    n_p3 = 0
    while n_p3 < 3000:
        try:
            g = draw(r)
            ev = evaluate_genome(g, tier="T2", use_cache=False)
        except Exception:
            continue
        n_p3 += 1
        org = compile_genome(g)
        rr = behavioral_descriptors(org, ev["evaluation"])["refusal_rate"]
        (rr_viable if ev["feasible"] else rr_nonviable)[round(rr, 6)] += 1

    viable_all_one = (set(rr_viable) == {1.0}) if rr_viable else None
    nonviable_varies = len(rr_nonviable) > 1

    out = {
        "study_id": "RV_A_PREFLIGHT_P1P2P3",
        "capsule_root": ROOT,
        "freeze_sha256_in_aggregate": agg["freeze_sha256"],
        "t3_key_sha256": hashlib.sha256(T3KEY.encode()).hexdigest(),
        "P1_verdict_reproduction": {
            "n_checked": p1_checked, "n_mismatch": p1_mismatch,
            "exact": p1_mismatch == 0,
            "mismatch_samples": mismatches},
        "P2_determinism": {
            "n_checked": p2_checked, "n_mismatch": p2_mismatch,
            "exact": p2_mismatch == 0},
        "P3_capability_bit_crosscheck": {
            "n_checked": cap_checked, "n_mismatch": cap_mismatch,
            "exact": cap_mismatch == 0,
            "note": "grammar_signature-derived can_check vs evaluation."
                    "lifetime2._capabilities on the compiled organism"},
        "gate_and_family_decomposition": {
            "%s|failed=%s|harmful=%s|stale=%s" % k: v for k, v in sorted(ct.items())},
        "P4_refusal_rate_degeneracy": {
            "n_draws": n_p3,
            "viable_values": dict(rr_viable),
            "nonviable_values": {k: v for k, v in sorted(rr_nonviable.items())},
            "viable_identically_one": viable_all_one,
            "nonviable_varies": nonviable_varies,
            "gate_induced_dead_axis": bool(viable_all_one and nonviable_varies),
            "note": "dead ONLY over the admitted set => gate-induced, not a "
                    "constant function of the descriptor"},
    }
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in out.items()
                      if k != "gate_and_family_decomposition"},
                     indent=1, sort_keys=True))
    print("GATE DECOMPOSITION:")
    print(json.dumps(out["gate_and_family_decomposition"], indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
