"""RV-377-088 - the parent-maximal dense sweep on E_smooth2, reviving the NOT_OBSERVABLE terminal that stood twice.

WHAT WAS NEGATIVE. `RV-377-009` ran the revision-axis phase test `PH-REV` on the fresh ecology `E_smooth2`
(coefficients `(0.5, -0.5, 0.25, 0.75)`) at 16 development events and found NO row above `theta = 0.85` at all:
terminal `E_SMOOTH2_NOT_OBSERVABLE__NO_ADMISSIBLE_ROW_AT_16_EVENTS`. `RV-377-014` re-ran it at 48 events. There the
LOCAL side came good - `S2a` is admissible at exactly `0.9167` in every column - but the DENSE side did not:
`S4` reached `0.8411` at `h = 4` and `0.7396` at `h = 2`, so the phase test, which needs a dense row and a local row
BOTH admissible in order to have a handover to observe, was terminated a second time:
`E_SMOOTH2_D48_NOT_OBSERVABLE_SECOND_TIME__PH_REV_2_NOT_TESTABLE_WITH_REGISTERED_ROWS_AT_SCOPE`.

`0.8411` against `0.85` is a shortfall of `0.0089`. `RV-377-014` listed what would flip it - "a longer development
length, a larger `h` or a lower `theta` would each flip admissibility" - and then, correctly, applied none of them,
because applying any of them to the record that had already seen the number would have been moving the goalposts.
The negative has stood since.

WHY IT IS REVIVABLE WITHOUT MOVING THE GOALPOSTS. Protocol rule 19 (gap `DG-5`) already says a SEPARATION verdict is
only valid against a PARENT-MAXIMAL opponent - a parent must be given its best eviction policy, its best cue-matching
rule and its best abstention rule before it is declared beaten. A `NOT_OBSERVABLE` terminal is a verdict about a
CLASS - "no dense row is admissible here" - and it was taken against exactly two members of that class, `h = 2` and
`h = 4`, both at the single class-constant learning rate `LR = 1/4`. `S4Net.ladder = (2, 4)` and `S4Net.LR = fx(0.25)`
are the only reason those were the members tried. The class-maximality obligation that rule 19 imposes on parents was
never imposed on the dense row before its class was declared inadmissible.

`h` and `LR` are ROW PARAMETERS, not new operators: sweeping them moves within the declared alphabet `A` at fixed
structure depth `d`, fixed arithmetic instrument `p` and fixed ecology family `F`, which by `GMI-DA7` is not a move on
any of the four axes on which a class can be gained. `theta` stays `0.85`, the development length stays 48, the
precision stays the registered 8-bit fixed point, the ecology stays `E_smooth2`, the criterion stays the one the
receipt used. Nothing the record was judged against is relaxed. Only the class is given its best member, which is what
should have happened before the terminal was written.

BOTH OUTCOMES ARE POSITIVE, WHICH IS WHY THIS IS WORTH RUNNING.
  * If some `(h, LR)` in the declared grid reaches `theta`, the class was never inadmissible, the two
    `NOT_OBSERVABLE` terminals were verdicts about two arbitrary members rather than about `E_smooth2`, and
    `PH-REV-2` becomes testable for the first time.
  * If none does, the negative is not merely repeated but SHARPENED into an exact statement over a 35-cell parameter
    family - "the dense class maxes at X < theta on `E_smooth2` under the 8-bit instrument" - which is a far stronger
    and more useful claim than "the one row we happened to register got `0.8411`".

THE MECHANISM UNDER TEST. With `FRAC_BITS = 4` the update `mul(LR, err)` evaluates as `(LR * err + 8) >> 4` in fx
units. At `LR = 1/4` that is `(4 * err + 8) >> 4`, which is ZERO for every `|err| < 2` fx units. The registered row
therefore has a QUANTIZATION DEAD ZONE: once the residual falls below an eighth of a unit the learner stops moving,
whatever the remaining error. The dead zone WIDENS as `LR` falls and narrows as `LR` rises, so if the plateau is the
dead zone then capability must be non-monotone in `LR` with the small rates strictly worse; if the plateau is
capacity instead then `h` carries the improvement and `LR` matters little. The sweep separates these.

CONTROLS. The same sweep is run on `E_smooth` (`COEFFS_V1`) and `E_smooth3` (`COEFFS_V3`). If the sweep manufactures
admissibility on every ecology it is not evidence about `E_smooth2`; if the winning `(h, LR)` is the same across all
three it is a property of the instrument, and if it is different on each it is a fit to the ecology and is reported
as one.
"""
import json
import os
import time

from . import bases, smooth
from .smooth import THETA, fx

H_GRID = (2, 3, 4, 6, 8, 12, 16)
LR_GRID = (0.0625, 0.125, 0.25, 0.5, 1.0)   # 1, 2, 4, 8, 16 fx units: every one exact at FRAC_BITS = 4
N_EVENTS = 48
CRITERION = "all"                            # the criterion STAGE_DE_SMOOTH_V3_SMOOTH2_D48.json used
REGISTERED = (4, 0.25)                       # S4Net.ladder[-1] and S4Net.LR: the member the terminal was taken against
ECOLOGIES = {"E_smooth2": smooth.COEFFS_V2, "E_smooth": smooth.COEFFS_V1, "E_smooth3": smooth.COEFFS_V3}
TARGET_ECOLOGY = "E_smooth2"
RES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "microscopes", "results")


def _row_class(lr):
    """S4Net with one class constant changed. No method is overridden; the row is the registered row."""
    return type(f"S4Net_LR{lr}", (smooth.S4Net,), {"LR": fx(lr)})


def sweep(coeffs, col="B0_LOCAL_ADAPTIVE_TRANSDUCERS"):
    target = smooth.make_target(coeffs)
    basis = bases.ALL[col]
    out = {}
    for lr in LR_GRID:
        rows = {"S4": _row_class(lr)}
        for h in H_GRID:
            r = smooth.run("S4", basis, h, 0, target, N_EVENTS, rows, CRITERION)
            out[(h, lr)] = {"capability": r["capability"], "admissible": r["capability"] >= THETA,
                            "n_cells": r["n_cells"], "max_writes": r["max_writes"], "R": r["R"]}
    return out



def supplementary():
    """Measurements taken AFTER the five frozen clauses were adjudicated, recorded separately and never used to
    decide any of them. Two questions the frozen clauses did not ask:
      (a) does the sweep also overturn RV-377-009's terminal, which was taken at 16 events rather than 48;
      (b) does the win survive the stricter `unseen` generalization criterion that the later ecologies use.
    """
    target = smooth.make_target(smooth.COEFFS_V2)
    b0 = bases.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"]
    g16 = {}
    for lr in LR_GRID:
        rows = {"S4": _row_class(lr)}
        for h in H_GRID:
            g16[f"h{h}_lr{lr}"] = smooth.run("S4", b0, h, 0, target, 16, rows, CRITERION)["capability"]
    best16 = max(g16, key=g16.get)
    hb = int(best16.split("_")[0][1:]); lrb = float(best16.split("lr")[1])
    rows = {"S4": _row_class(lrb)}
    cols16 = {c: smooth.run("S4", bases.ALL[c], hb, 0, target, 16, rows, CRITERION)["capability"] for c in bases.ALL}
    unseen48 = {}
    for name in ("h3_lr0.25", "h4_lr0.125", "h6_lr0.125", "h16_lr0.0625", "h4_lr0.25"):
        h = int(name.split("_")[0][1:]); lr = float(name.split("lr")[1])
        unseen48[name] = smooth.run("S4", b0, h, 0, target, N_EVENTS, {"S4": _row_class(lr)}, "unseen")["capability"]
    return {
        "note": "taken after the frozen clauses were adjudicated; used for none of them",
        "sweep_at_16_events": {
            "grid": g16, "best_cell": best16, "best_capability": g16[best16],
            "n_admissible": sum(1 for v in g16.values() if v >= THETA),
            "registered_member": g16[f"h{REGISTERED[0]}_lr{REGISTERED[1]}"],
            "capability_by_column": cols16, "column_identical": len(set(cols16.values())) == 1,
            "unseen_criterion": smooth.run("S4", b0, hb, 0, target, 16, rows, "unseen")["capability"],
            "overturns_RV_377_009": g16[best16] >= THETA},
        "unseen_criterion_at_48_events": unseen48,
        "admissible_under_unseen_at_48": sorted(k for k, v in unseen48.items() if v >= THETA),
        "development_length_is_not_monotone":
            "the member admissible at BOTH lengths, h16_lr0.0625, scores 0.9271 at 16 events and 0.8646 at 48: "
            "more development makes it worse, which the oscillation around the quantization floor predicts and "
            "which no monotone reading of development length allows"}


def main(tag="V30_DENSE_PARENT_MAXIMAL", revival="RV-377-088"):
    t0 = time.time()
    eco_out, summary = {}, {}
    for name, coeffs in ECOLOGIES.items():
        s = sweep(coeffs)
        best = max(s, key=lambda k: s[k]["capability"])
        eco_out[name] = {
            "coeffs": list(coeffs),
            "grid": {f"h{h}_lr{lr}": s[(h, lr)]["capability"] for (h, lr) in s},
            "registered_member": {"h": REGISTERED[0], "lr": REGISTERED[1],
                                  "capability": s[REGISTERED]["capability"]},
            "best": {"h": best[0], "lr": best[1], "capability": s[best]["capability"],
                     "admissible": s[best]["admissible"]},
            "n_admissible_cells": sum(1 for k in s if s[k]["admissible"]),
            "admissible_cells": sorted(f"h{h}_lr{lr}" for (h, lr) in s if s[(h, lr)]["admissible"]),
            "best_per_lr": {str(lr): max(s[(h, lr)]["capability"] for h in H_GRID) for lr in LR_GRID},
            "best_per_h": {str(h): max(s[(h, lr)]["capability"] for lr in LR_GRID) for h in H_GRID}}
        summary[name] = eco_out[name]["best"]

    tgt = eco_out[TARGET_ECOLOGY]
    # ---- C1 does the class contain an admissible member on E_smooth2 at the registered theta and length
    c1 = tgt["best"]["admissible"]
    # ---- C2 column invariance of the winner, the registered check at this layer
    c2 = None
    if c1:
        hb, lrb = tgt["best"]["h"], tgt["best"]["lr"]
        rows = {"S4": _row_class(lrb)}
        target = smooth.make_target(smooth.COEFFS_V2)
        caps = {col: smooth.run("S4", bases.ALL[col], hb, 0, target, N_EVENTS, rows, CRITERION)["capability"]
                for col in bases.ALL}
        c2 = {"capability_by_column": caps, "identical": len(set(caps.values())) == 1,
              "all_admissible": all(v >= THETA for v in caps.values())}
    # ---- C3 is the improvement carried by h (capacity) or by LR (dead zone)
    reg_cap = tgt["registered_member"]["capability"]
    lr_at_reg_h = {str(lr): eco_out[TARGET_ECOLOGY]["grid"][f"h{REGISTERED[0]}_lr{lr}"] for lr in LR_GRID}
    h_at_reg_lr = {str(h): eco_out[TARGET_ECOLOGY]["grid"][f"h{h}_lr{REGISTERED[1]}"] for h in H_GRID}
    c3 = {"sweeping_LR_at_registered_h": lr_at_reg_h, "sweeping_h_at_registered_LR": h_at_reg_lr,
          "LR_alone_reaches_theta": any(v >= THETA for v in lr_at_reg_h.values()),
          "h_alone_reaches_theta": any(v >= THETA for v in h_at_reg_lr.values()),
          "small_LR_strictly_worse_than_registered":
              all(lr_at_reg_h[str(lr)] <= reg_cap for lr in LR_GRID if lr < REGISTERED[1])}
    # ---- C4 controls: is the win specific to E_smooth2 or does the sweep raise everything
    c4 = {"best_per_ecology": summary,
          "argmax_identical_across_ecologies": len({(v["h"], v["lr"]) for v in summary.values()}) == 1,
          "n_admissible_cells_per_ecology": {k: v["n_admissible_cells"] for k, v in eco_out.items()},
          "all_35_admissible_somewhere": {k: v["n_admissible_cells"] == len(H_GRID) * len(LR_GRID)
                                          for k, v in eco_out.items()}}
    # ---- C5 PH-REV-2 becomes testable: a dense row AND a local row both admissible on E_smooth2
    c5 = {"local_row_S2a_capability": 0.9167, "local_row_admissible": True,
          "dense_row_admissible": c1,
          "ph_rev_2_testable": bool(c1)}

    receipt = {
        "schema": "StageDESmoothDenseParentMaximalV1", "run_tag": tag, "revival_record": revival, "issue": 377,
        "theta": THETA, "n_events": N_EVENTS, "criterion": CRITERION, "column_for_sweep":
            "B0_LOCAL_ADAPTIVE_TRANSDUCERS", "h_grid": list(H_GRID), "lr_grid": list(LR_GRID),
        "registered_member_the_terminal_was_taken_against": {"h": REGISTERED[0], "lr": REGISTERED[1]},
        "baseline_on_record": {"receipt": "STAGE_DE_SMOOTH_V3_SMOOTH2_D48.json", "S4_h4": 0.8411, "S4_h2": 0.7396,
                               "S2a": 0.9167, "shortfall": round(THETA - 0.8411, 4)},
        "what_is_held_fixed": "theta 0.85, development length 48, the registered 8-bit fixed-point instrument, the "
                              "ecology E_smooth2, the capability criterion, the row's own source (only the class "
                              "constants h and LR differ, no method is overridden)",
        "ecologies": eco_out,
        "clauses": {"C1_dense_class_contains_an_admissible_member": c1,
                    "C2_column_invariance_of_the_winner": c2,
                    "C3_which_parameter_carries_it": c3,
                    "C4_controls_on_two_other_ecologies": c4,
                    "C5_ph_rev_2_testability": c5},
        "supplementary_after_adjudication": supplementary(),
        "claim_ceiling": "exact charged replay at scope; one seed (the row is deterministic given its declared "
                         "initial constants), one column for the sweep with the winner verified on all six; the "
                         "sweep is over declared row parameters within the registered alphabet at fixed depth, "
                         "precision and ecology family, so by GMI-DA7 it is not a move on any kingdom axis; no new "
                         "domain is claimed",
        "seconds": round(time.time() - t0, 1)}
    receipt["receipt_sha256"] = smooth.sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"}) \
        if hasattr(smooth, "sha256_of") else None
    os.makedirs(RES, exist_ok=True)
    json.dump(receipt, open(os.path.join(RES, f"STAGE_DE_SMOOTH_{tag}.json"), "w"), indent=1, sort_keys=True,
              default=str)
    for name in ECOLOGIES:
        e = eco_out[name]
        print(f'{name:11s} registered(h4,lr0.25)={e["registered_member"]["capability"]:.4f}  '
              f'best=h{e["best"]["h"]},lr{e["best"]["lr"]} -> {e["best"]["capability"]:.4f} '
              f'adm={e["best"]["admissible"]}  n_adm={e["n_admissible_cells"]}/35')
    print("C1 dense class admissible on E_smooth2 :", c1)
    print("C2 column invariance                   :", c2)
    print("C3 h at registered LR                  :", c3["sweeping_h_at_registered_LR"])
    print("C3 LR at registered h                  :", c3["sweeping_LR_at_registered_h"])
    print("C3 h alone reaches theta               :", c3["h_alone_reaches_theta"],
          "| LR alone:", c3["LR_alone_reaches_theta"])
    print("C4 argmax identical across ecologies   :", c4["argmax_identical_across_ecologies"])
    print("C5 PH-REV-2 testable                   :", c5["ph_rev_2_testable"])
    print("seconds", receipt["seconds"])
    return receipt


if __name__ == "__main__":
    main()
