"""RV-377-102 — sweep the ECOLOGY axis for a discriminating ecology on which the coefficient carrier is
intervention-robustly admissible, before declaring that none exists.

THE NEGATIVE THIS ATTACKS. After RV-377-100 and RV-377-101 the coefficient carrier D1 stands with NO valid witness:

    E_sym3     6 rows admissible under all six interventions  -- but NON-DISCRIMINATING (best constant 0.8750 >= theta)
    E_smooth1  3 rows admissible under standard,  0 under all six
    E_parity   2 rows admissible under standard,  0 under all six
    E_smooth3  0 admissible at any width to h = 32
    E_sym5     0 admissible at any width to h = 32

So on every DISCRIMINATING registered ecology, D1 has no intervention-robust witness, and on the only ecology where it
has one, a machine emitting a constant is also admissible. G15 step one is not reached.

WHY THIS IS NOT YET A THEOREM. Protocol rules 38 and 39: a class-level negative may not be recorded until every index
has been swept, and the ECOLOGY index here has been sampled at FIVE points chosen for other reasons. Concluding "D1 is
never intervention-robustly admissible on a valid ecology" from five ecologies would repeat, on the ecology axis, the
exact error rule 39 was written for -- and this lane has already made that error once today (RV-377-089b).

WHAT IS SWEPT. The declared class is EVERY target of the form target(x) = sum_i c_i * bit_i(x) with each c_i drawn
from the registered coefficient grid, which is a MAXIMAL class at a declared bound: 9^4 = 6561 ecologies, complete
enumeration, no sampling and no seed. Under sub-gate IG-1 the generator therefore has no discretion at all and
independence of it is vacuous rather than assumed.

STAGE STRUCTURE, so the cost is affordable without narrowing the class:
  stage 1  every one of the 6561 targets: best constant over the full fx grid -> keep only DISCRIMINATING ones
  stage 2  on those, the registered gradient family under the STANDARD intervention -> keep only those with any hit
  stage 3  on those, ALL SIX registered interventions, and the margin over the constant in FX UNITS (rule 40)

A witness counts only if it clears theta under every intervention AND beats the constant by at least ONE fx unit of
mean absolute error. A margin below that is WITHIN_QUANTIZATION and separates nothing.
"""
import itertools
import json
import os

from . import bases, ecology, smooth, zoo

THETA = smooth.THETA
FX = smooth.FX_ONE
COL = "B0_LOCAL_ADAPTIVE_TRANSDUCERS"
COEF_GRID = tuple(v / 16 for v in (-8, -6, -4, -2, 0, 2, 4, 6, 8))
H_GRID = (1, 2, 3, 4, 6, 8)
LR_GRID = (1, 2, 3, 4, 6, 8)
FX_UNIT = 1.0 / (1.5 * 16)           # one fx unit of mean absolute error, in capability
RES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "microscopes", "results")


def best_constant(target, ev):
    best = (-1.0, None)
    for c in range(-128, 128):
        err = sum(abs(c - target[x]) for x in ev) / FX / len(ev)
        cap = max(0.0, 1 - err / 1.5)
        if cap > best[0]:
            best = (round(cap, 4), c)
    return best


def main(tag="V32_ECO_AXIS", revival="RV-377-102", stage2_cap=400):
    basis = bases.ALL[COL]
    ev = smooth.UNSEEN
    # ---- stage 1: complete enumeration, discrimination test
    disc = []
    n_total = 0
    for co in itertools.product(COEF_GRID, repeat=4):
        n_total += 1
        t = smooth.make_target(co)
        bc, c = best_constant(t, ev)
        if bc < THETA:
            disc.append((co, bc, c))
    print(f"stage 1: {n_total} enumerated, {len(disc)} DISCRIMINATING ({100*len(disc)/n_total:.1f}%)", flush=True)
    # order is canonical (itertools product order), so the cap is a budget and not a choice of which cells to look at
    stage2 = disc[:stage2_cap]
    # ---- stage 2: any gradient row admissible under standard?
    hits = []
    for i, (co, bc, c) in enumerate(stage2):
        spec = ecology.spec_smooth(co, n_events=16, criterion="unseen")
        best = (-1.0, None)
        for h in H_GRID:
            for lr in LR_GRID:
                g = zoo.gradient_net(h, lr)
                try:
                    cap = ecology.run_genotype(spec, g, basis, "standard")["capability"]
                except Exception:
                    continue
                if cap > best[0]:
                    best = (cap, (h, lr))
        if best[0] >= THETA:
            hits.append((co, bc, best[0], best[1]))
        if (i + 1) % 50 == 0:
            print(f"  stage 2: {i+1}/{len(stage2)} scanned, {len(hits)} with a standard-admissible gradient row", flush=True)
    print(f"stage 2: {len(hits)} of {len(stage2)} discriminating ecologies have a standard-admissible gradient row", flush=True)
    # ---- stage 3: full intervention family + fx-unit margin
    witnesses = []
    for co, bc, cap_std, hl in hits:
        spec = ecology.spec_smooth(co, n_events=16, criterion="unseen")
        for h in H_GRID:
            for lr in LR_GRID:
                g = zoo.gradient_net(h, lr)
                caps = {}
                ok = True
                for iv in ecology.INTERVENTIONS:
                    try:
                        caps[iv] = ecology.run_genotype(spec, g, basis, iv)["capability"]
                    except Exception:
                        ok = False
                        break
                if not ok:
                    continue
                mn = min(caps.values())
                if mn >= THETA:
                    margin_fx = (mn - bc) / FX_UNIT
                    witnesses.append({"coeffs": list(co), "h": h, "lr": lr, "best_constant": bc,
                                      "min_over_six": round(mn, 4), "margin_fx_units": round(margin_fx, 3),
                                      "by_intervention": {k: round(v, 4) for k, v in caps.items()},
                                      "separates": margin_fx >= 1.0})
    strong = [w for w in witnesses if w["separates"]]
    receipt = {"schema": "GMIEcologyAxisSweepV1", "run_tag": tag, "revival_record": revival, "issue": 377,
               "theta": THETA, "coefficient_grid": list(COEF_GRID), "h_grid": list(H_GRID), "lr_grid": list(LR_GRID),
               "fx_unit_in_capability": FX_UNIT,
               "declared_class": "every target sum_i c_i*bit_i with c_i in the registered coefficient grid; "
                                 "complete enumeration, 9^4 = 6561, no sampling and no seed (sub-gate IG-1)",
               "n_enumerated": n_total, "n_discriminating": len(disc),
               "stage2_cap": stage2_cap, "stage2_note": "canonical enumeration order; the cap is a compute budget, "
                                                        "not a choice of which cells to inspect",
               "n_stage2_scanned": len(stage2), "n_with_standard_admissible_gradient": len(hits),
               "n_intervention_robust_witnesses": len(witnesses),
               "n_separating_witnesses": len(strong),
               "witnesses": sorted(witnesses, key=lambda w: -w["margin_fx_units"])[:40],
               "claim_ceiling": "one column, one seed, the registered 16-event protocol and the unseen criterion; "
                                "a witness here is an EXISTENCE result about the ecology axis, not a recovery result "
                                "and not a domain claim"}
    receipt["receipt_sha256"] = ecology.sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    os.makedirs(RES, exist_ok=True)
    json.dump(receipt, open(os.path.join(RES, f"STAGE_ECO_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    print(f"\nstage 3: {len(witnesses)} intervention-robust, {len(strong)} of them SEPARATING (>= 1 fx unit)")
    for w in sorted(strong, key=lambda w: -w["margin_fx_units"])[:10]:
        print(f"  coeffs {w['coeffs']} h{w['h']} lr{w['lr']}  min/6 {w['min_over_six']:.4f}  "
              f"const {w['best_constant']:.4f}  margin {w['margin_fx_units']:.3f} fx units")
    print("sha", receipt["receipt_sha256"][:16])
    return receipt


if __name__ == "__main__":
    main()
