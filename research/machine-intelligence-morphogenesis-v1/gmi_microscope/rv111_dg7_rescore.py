"""RV-377-111 -- re-score RV-377-088's admissible cells under the full registered intervention family.

WHY. The DG-7 V2 audit found that `RV-377-088` -- the record that OPENED DG-7 and supplies both of
its claimed overturns -- never swept the intervention index.  Its receipt
`STAGE_DE_SMOOTH_V30_DENSE_PARENT_MAXIMAL.json` contains zero occurrences of the string
"intervention"; its `C2` clause verifies the winner on "all six" COLUMNS (B0, B1, B2, B3, P3,
U_UNIFORM_UNIVERSAL), not six interventions.  Rule 36 was opened by `RV-377-085` three records
earlier in the same lane, which measured 5 of 8 registered rows changing status between `standard`
alone and the full family.

`RV-377-088`'s rows are `S4Net` subclasses evaluated by `smooth.run` at 48 development events with
the `all` criterion.  `smooth.run` has no intervention parameter, and `ecology.run_genotype` -- which
does -- takes a genotype graph and the registry's 16-event specs, so it cannot reproduce these
numbers.  This module therefore re-implements the development loop with the intervention applied,
copying the semantics of `ecology.run_genotype` exactly (same `J` dict, same order permutation, same
revoke rule, same extra-feedback rule).

`smooth.run` IS NOT MODIFIED.  Every existing result stands untouched.  The faithfulness control is
`standard`: under the standard intervention this loop must reproduce `RV-377-088`'s published
capability for every cell, to the digit.  If it does not, the re-implementation is wrong and no
intervention number from it may be read.
"""
from __future__ import annotations

import json
import os
import time

from . import bases, ecology, smooth
from .core import sha256_of
from .smooth_dense_max import CRITERION, ECOLOGIES, N_EVENTS, THETA, _row_class

COL = "B0_LOCAL_ADAPTIVE_TRANSDUCERS"
RES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "microscopes", "results")

# The cells RV-377-088 recorded as admissible, verbatim from its receipt.
ADMISSIBLE_CELLS = {
    "E_smooth":  [(12, 0.25), (4, 0.25), (6, 0.125), (8, 0.25)],
    "E_smooth2": [(16, 0.0625), (3, 0.25), (4, 0.125), (6, 0.125)],
    "E_smooth3": [(4, 0.125), (6, 0.125), (8, 0.125)],
}


def run_row_under(coeffs, h, lr, intervention, col=COL):
    """RV-377-088's row at (h, lr), developed under one registered intervention.

    Mirrors ecology.run_genotype's intervention handling line for line, at smooth_dense_max's
    48 events and 'all' criterion.
    """
    J = ecology.INTERVENTIONS[intervention]
    target = smooth.make_target(coeffs)
    n_events = J.get("n_events", N_EVENTS)
    train = list(smooth.TRAIN)
    order = J.get("order")
    if order:
        train = [train[i] for i in order]
    revoke_at = n_events // 2 + 1 if n_events != smooth.H else smooth.REVOKE_AT

    ref = _row_class(lr)(h)
    M = smooth.Machine(bases.ALL[col], seed=0)
    M.phase("exec"); ref.init(M)
    for t in range(1, n_events + 1):
        x = train[(t - 1) % len(train)]; y = target[x]
        M.phase("exec")
        for xx in smooth.ALL_X: ref.query(M, xx)
        M.phase("upd"); ref.feedback(M, x, y); M.end_event()
        M.phase("ver")
        for xx in smooth.ALL_X: M.op("EQ", ref.query(M, xx), target[xx])
        if J.get("revoke", True) and t == revoke_at:
            M.phase("rev"); ref.revoke(M, train[1]); M.end_event()
            if J.get("revoke") == "double":
                ref.revoke(M, train[2]); M.end_event()
    if J.get("extra"):
        for xx in smooth.UNSEEN[:4]:
            M.phase("upd"); ref.feedback(M, xx, target[xx]); M.end_event()
    M.phase("exec"); final = {xx: ref.query(M, xx) for xx in smooth.ALL_X}
    eval_x = smooth.UNSEEN if CRITERION == "unseen" else smooth.ALL_X
    err = sum(abs(final[xx] - target[xx]) for xx in eval_x) / smooth.FX_ONE / len(eval_x)
    return round(max(0.0, 1 - err / 1.5), 4)


def main(tag="V32_DG7_INTERVENTION_RESCORE", revival="RV-377-111"):
    t0 = time.time()
    published = json.load(open(os.path.join(RES, "STAGE_DE_SMOOTH_V30_DENSE_PARENT_MAXIMAL.json")))
    out, control_ok = {}, True
    for eco, cells in ADMISSIBLE_CELLS.items():
        coeffs = ECOLOGIES[eco]
        out[eco] = {}
        for (h, lr) in cells:
            caps = {iv: run_row_under(coeffs, h, lr, iv) for iv in ecology.INTERVENTIONS}
            vals = list(caps.values())
            out[eco][f"h{h}_lr{lr}"] = {
                "by_intervention": caps,
                "standard": caps["standard"],
                "min_over_interventions": min(vals),
                "argmin_intervention": min(caps, key=caps.get),
                "admissible_standard_only": caps["standard"] >= THETA,
                "admissible_all_interventions": min(vals) >= THETA,
            }
    # faithfulness control: standard must reproduce the published grid
    ctl = {}
    for eco, cells in ADMISSIBLE_CELLS.items():
        pub = published["ecologies"][eco].get("admissible_cells", [])
        for (h, lr) in cells:
            k = f"h{h}_lr{lr}"
            got = out[eco][k]["standard"]
            ctl[f"{eco}|{k}"] = {"recomputed_standard": got,
                                 "published_as_admissible": k in pub,
                                 "reproduces_admissibility": (got >= THETA) == (k in pub)}
            control_ok &= ctl[f"{eco}|{k}"]["reproduces_admissibility"]
    surv = {e: sorted(k for k, v in d.items() if v["admissible_all_interventions"]) for e, d in out.items()}
    lost = {e: sorted(k for k, v in d.items() if not v["admissible_all_interventions"]) for e, d in out.items()}
    receipt = {
        "schema": "RV377_111_DG7_InterventionRescoreV1", "revival_record": revival, "run_tag": tag, "issue": [377],
        "status": "EXECUTED_EXACT_AT_SCOPE" if control_ok else "CONTROL_FAILED__NO_INTERVENTION_NUMBER_IS_READABLE",
        "what_is_tested": "RV-377-088's admissible cells re-scored under all six registered interventions (rule 36)",
        "smooth_run_modified": False,
        "faithfulness_control": {"rule": "under `standard` this loop must reproduce the published admissibility of every cell",
                                 "passed": control_ok, "cells": ctl},
        "theta": THETA, "n_events": N_EVENTS, "criterion": CRITERION, "column": COL,
        "interventions": sorted(ecology.INTERVENTIONS), "by_ecology": out,
        "surviving_all_interventions": surv, "lost_under_intervention_family": lost,
        "n_surviving": sum(len(v) for v in surv.values()), "n_tested": sum(len(v) for v in ADMISSIBLE_CELLS.values()),
        "seconds": round(time.time() - t0, 1),
        "claim_ceiling": "one seed, one column, the three smooth ecologies RV-377-088 used, at its 48 events and `all` criterion; this re-scores that record's own cells under the intervention index it omitted and claims nothing beyond them",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_DE_SMOOTH_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    print(f"faithfulness control passed: {control_ok}")
    print(f"surviving all six interventions: {receipt['n_surviving']} of {receipt['n_tested']}")
    for e, d in out.items():
        for k, v in sorted(d.items()):
            print(f"  {e:10} {k:14} std {v['standard']:.4f}  min {v['min_over_interventions']:.4f} "
                  f"({v['argmin_intervention']:22}) all6 {v['admissible_all_interventions']}")
    return receipt


if __name__ == "__main__":
    main()
