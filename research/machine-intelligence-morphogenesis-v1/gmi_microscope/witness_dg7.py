"""RV-377-089 - the DG-7 audit applied to the sharpest class-level negative in the corpus: the coefficient carrier's
missing witness on E_smooth3 and E_sym5.

WHAT WAS NEGATIVE. `RV-377-081` found the coefficient carrier (`D1`, the gradient-style DENSE row) INADMISSIBLE on both
ecologies the six `B1` recovery runs used - `0.7604 / 0.8021` on `E_smooth3` and `0.7188 / 0.7500` on `E_sym5` against
`theta = 0.85` - and concluded the six runs were ZERO-EXPOSURE trials for `D1`, which is why the recovery rate was
0 of 6. `RV-377-082` then swept the row's parameters, found an admissible witness on a THIRD ecology `E_smooth1`
(`h = 6, lr = 2`, capability `0.8906`), and recorded of the other two:

    "The failure on the other two ecologies is confirmed as a REAL CEILING rather than a missing setting: the best of
     all 68 rows reaches only 0.8438 on E_smooth3 and 0.8385 on E_sym5."

WHY THAT CEILING IS NOT ESTABLISHED. The 68 rows swept `h` over `(1, 2, 3, 4, 6, 8)`. THE SWEEP STOPPED AT `h = 8`.
`h = 12`, `h = 16` and anything wider were never evaluated on any ecology. Under protocol rule 38 - opened hours ago by
`RV-377-088`, which overturned two `NOT_OBSERVABLE` terminals on `E_smooth2` by sweeping exactly this kind of unswept
class parameter - a "ceiling" claim over a truncated parameter grid is not a ceiling claim at all.

WHY THE MISSING REGION IS THE ONE THAT MATTERS, AND NOT AN ARBITRARY EXTENSION. `RV-377-088` measured, on the sibling
`smooth` layer, the same dense mechanism at the SAME 16 development events. There the landscape is a RIDGE in
`(h, lr)` along which the best width RISES as the rate FALLS, and at 16 events the only admissible cell in a 35-cell
grid was the widest, lowest-rate corner:

    h = 16, lr = 1/16  ->  0.9271      against the registered h = 4, lr = 1/4 -> 0.7578

a margin of `0.1693`, twenty times the shortfall that had been called a ceiling. `RV-377-082`'s grid covers the low
rates only up to `h = 8`; the corner where its sibling layer's single winner lives is exactly the corner it omits.
`RV-377-082`'s own mechanism note already points the same way - "at `h = 2` or `4` it underfits and at large `lr` it
oscillates" - it simply stopped widening two steps early.

WHAT IS HELD FIXED. `theta = 0.85`, 16 development events, the `unseen` criterion, the registered 8-bit instrument, the
registered ecologies and the registered row `zoo.gradient_net`. Only `h` is extended past 8, which is a row parameter
and therefore, by `GMI-DA7`, not a move on any of the four axes on which a class can be gained.

RULE 36 IS APPLIED FROM THE START, NOT AFTERWARDS. `RV-377-082`'s witness was taken under the `standard` intervention
and `RV-377-085` later found it fails the registered family - 5 of 8 rows change status between `standard` alone and
the six interventions. Every capability here is therefore reported under ALL SIX registered interventions, and a row is
called admissible only if it clears `theta` under every one of them. The single-intervention number is reported beside
it so the two are never confused again.
"""
import json
import os
import time

from . import b1, bases, ecology, morph, smooth, zoo

THETA = 0.85
H_GRID = (1, 2, 3, 4, 6, 8, 12, 16, 24, 32)     # (1..8) is RV-377-082's grid; 12, 16, 24, 32 are the extension
LR_GRID = (1, 2, 3, 4, 6, 8, 12, 16)            # fx units at FRAC_BITS = 4: lr = 1 is 1/16, lr = 4 is 1/4
RV082_H = (1, 2, 3, 4, 6, 8)
# RV-377-089b: all FIVE registered ecologies, so the claim is about the registered family and not a subset of it.
# E_sym3 and E_parity were not measured by RV-377-082 at all; E_parity is a table target, not a coefficient one.
ECOS = {"E_smooth3": smooth.COEFFS_V3, "E_sym5": (5 / 16,) * 4, "E_smooth1": smooth.COEFFS_V1,
        "E_sym3": (3 / 16,) * 4, "E_parity": None}
RV082_BEST = {"E_smooth3": 0.8438, "E_sym5": 0.8385, "E_smooth1": 0.8906, "E_sym3": None, "E_parity": None}
COL = "B0_LOCAL_ADAPTIVE_TRANSDUCERS"
RES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "microscopes", "results")


def _spec(eco, coeffs):
    """the REGISTERED spec for this ecology, taken from ecology.REGISTRY rather than rebuilt."""
    return ecology.REGISTRY[eco]


def caps_under_all_interventions(g, eco, coeffs):
    """capability of one genotype under each of the six registered interventions (protocol rule 36)."""
    spec = _spec(eco, coeffs)
    basis = bases.ALL[COL]
    out = {}
    for iv in ecology.INTERVENTIONS:
        try:
            r = ecology.run_genotype(spec, g, basis, iv)
        except Exception:
            out[iv] = None
            continue
        out[iv] = r["capability"] if isinstance(r, dict) else r[0]
    return out


def main(tag="V31b_DG7_COEFFICIENT_WITNESS_ALL5", revival="RV-377-089b"):
    t0 = time.time()
    rows = {f"grad_h{h}_lr{lr}": (h, lr) for h in H_GRID for lr in LR_GRID}
    out = {}
    for eco, coeffs in ECOS.items():
        target = ecology.target_of(ecology.REGISTRY[eco])
        cells = {}
        for name, (h, lr) in rows.items():
            g = zoo.gradient_net(h, lr)
            if b1.carrier_of(g) != "DENSE":
                continue
            r = b1.evaluate(g, target)
            if r is None:
                continue
            std = r[0]
            cells[name] = {"h": h, "lr": lr, "standard": std, "n_nodes": len(g["nodes"]),
                           "in_RV082_grid": h in RV082_H}
        # the full intervention family is charged only for the rows that clear theta under standard,
        # and for the best row overall, so the sweep stays cheap without weakening any admissibility claim
        cand = sorted(cells, key=lambda k: -cells[k]["standard"])
        for name in [c for c in cand if cells[c]["standard"] >= THETA] or cand[:1]:
            h, lr = cells[name]["h"], cells[name]["lr"]
            iv = caps_under_all_interventions(zoo.gradient_net(h, lr), eco, coeffs)
            cells[name]["by_intervention"] = iv
            vals = [v for v in iv.values() if v is not None]
            cells[name]["admissible_all_interventions"] = bool(vals) and len(vals) == len(iv) and min(vals) >= THETA
            cells[name]["min_over_interventions"] = min(vals) if vals else None
        best = max(cells, key=lambda k: cells[k]["standard"])
        inside = {k: v for k, v in cells.items() if v["in_RV082_grid"]}
        outside = {k: v for k, v in cells.items() if not v["in_RV082_grid"]}
        adm_std = sorted(k for k, v in cells.items() if v["standard"] >= THETA)
        adm_all = sorted(k for k, v in cells.items() if v.get("admissible_all_interventions"))
        out[eco] = {
            "coeffs": list(coeffs) if coeffs else "table target (parity)", "n_rows": len(cells),
            "best_row": best, "best_standard": cells[best]["standard"],
            "best_inside_RV082_grid": max(inside.values(), key=lambda v: v["standard"])["standard"] if inside else None,
            "best_outside_RV082_grid": max(outside.values(), key=lambda v: v["standard"])["standard"] if outside else None,
            "RV082_reported_best": RV082_BEST.get(eco),
            "admissible_under_standard": adm_std,
            "admissible_under_all_six_interventions": adm_all,
            "witness_exists_standard": bool(adm_std),
            "witness_exists_full_family": bool(adm_all),
            "witness_is_outside_RV082_grid": bool(adm_std) and any(not cells[k]["in_RV082_grid"] for k in adm_std),
            "grid": {k: v["standard"] for k, v in cells.items()},
            "cells": cells}
    receipt = {
        "schema": "StageB1DG7CoefficientWitnessV1", "run_tag": tag, "revival_record": revival, "issue": 377,
        "theta": THETA, "n_events": 16, "criterion": "unseen", "column": COL,
        "h_grid": list(H_GRID), "lr_grid": list(LR_GRID), "RV377082_h_grid": list(RV082_H),
        "what_is_held_fixed": "theta, development length, criterion, instrument, ecologies and the registered row "
                              "zoo.gradient_net; only h is extended past 8, a row parameter and so not a move on any "
                              "GMI-DA7 axis",
        "rule_36_compliance": "every admissibility verdict here names its intervention set: a row is called "
                              "admissible only if it clears theta under ALL SIX registered interventions, and the "
                              "standard-only number is reported beside it",
        "ecologies": out,
        "claim_ceiling": "exact charged replay at scope; one column, one seed, the registered 16-event protocol; the "
                         "sweep is over a declared row parameter and claims no new domain",
        "seconds": round(time.time() - t0, 1)}
    receipt["receipt_sha256"] = ecology.sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    os.makedirs(RES, exist_ok=True)
    json.dump(receipt, open(os.path.join(RES, f"STAGE_B1_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    for eco, v in out.items():
        print(f'{eco:11s} RV082_best={v["RV082_reported_best"]}  inside(h<=8)={v["best_inside_RV082_grid"]}  '
              f'outside(h>=12)={v["best_outside_RV082_grid"]}  best={v["best_row"]} {v["best_standard"]:.4f}')
        print(f'            admissible under standard: {v["admissible_under_standard"]}')
        print(f'            admissible under ALL SIX : {v["admissible_under_all_six_interventions"]}')
    print("seconds", receipt["seconds"], "sha", receipt["receipt_sha256"][:16])
    return receipt


if __name__ == "__main__":
    main()
