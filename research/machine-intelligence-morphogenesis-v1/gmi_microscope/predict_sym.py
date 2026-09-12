"""RV-377-021 frozen prediction for the symmetric-coefficient ecologies E_sym(a), a = k/16 (written and run BEFORE the
frontier runs; see REVIVAL_LEDGER). Third admissible class test (B4 strengthening): the kNN memory row S5k joins S4
(gradient) and S2a (approximate search) on the frontier.

Inputs allowed at freeze time: (a) closed-form capabilities of S5k and S5 derived from the rows' definitions (no run);
(b) per-event costs of S4, S2a and S5k measured on the already-adjudicated ecology E_smooth3
(STAGE_DE_SMOOTH_V4B_SMOOTH3_ROWS_V4_CALIB.json; S4 and S2a there are byte-identical to STAGE_DE_SMOOTH_V4_SMOOTH3_GEN.json).
Output: microscopes/results/STAGE_DE_SYM_PREDICTION.json with, per candidate a, the predicted capabilities, the predicted
admissible set, the predicted winner on every (column, H, r) cell (10% margin rule, else ABSTAIN) and the predicted
horizon crossover H*(r) between S5k and S4.

Closed form (S5k, kNN memory with Hamming-1 averaging). The seen set is the even-parity coset, so every unseen input x
(odd parity, popcount p in {1, 3}) has all four Hamming-1 neighbours seen and none at distance 0; the row returns
floor(sum of the four neighbour targets / 4) in fixed point = floor(a16 * (p + 2) / 2) (a16 = 16 a), while the target is
a16 * p. Capability = 1 - mean|error|/1.5 over the 8 unseen inputs. S5 (exemplar memory) returns 0 on unseen inputs:
capability = 1 - 2a/1.5.
"""
from __future__ import annotations

import json
import os

from . import bases, smooth
from .core import FX_ONE, sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
H_GRID = [1, 2, 4, 8, 16, 32, 64, 128]; R_GRID = [0, 1, 2, 4, 8, 16, 32]
N_EVENTS = 16; MARGIN = 0.10
CANDIDATES_THREE_CLASS = [5, 3, 7]  # k/16, adjudication order for the three-class claim (first candidate where S4, S2a, S5k are all admissible)
BOUNDARY = 8                        # k/16 at which the closed form predicts S5k drops below theta while S4 and S2a stay admissible
ALL_K = [3, 5, 7, 8]


def knn_capability_closed_form(k):
    errs = []
    for p in (1, 3):
        avg = (k * (2 * p + 4)) // 4          # two SHR of the exact 4-neighbour sum
        errs += [abs(avg - k * p)] * 4        # four unseen inputs per popcount
    return round(max(0.0, 1 - (sum(errs) / len(errs)) / FX_ONE / 1.5), 4)


def s5_capability_closed_form(k):
    return round(max(0.0, 1 - (2 * k / FX_ONE) / 1.5), 4)


def main():
    calib = json.load(open(os.path.join(RES, "STAGE_DE_SMOOTH_V4B_SMOOTH3_ROWS_V4_CALIB.json")))
    v4 = json.load(open(os.path.join(RES, "STAGE_DE_SMOOTH_V4_SMOOTH3_GEN.json")))
    cols = list(bases.ALL)
    for col in cols:
        for row in ("S4", "S2a"):
            assert calib["R_by_cell"][f"{row}|{col}|4"] == v4["R_by_cell"][f"{row}|{col}|4"], (row, col)
    pe = {col: {row: smooth.per_event(calib["R_by_cell"][f"{row}|{col}|4"], N_EVENTS) for row in ("S4", "S2a", "S5k")} for col in cols}
    per_k = {}
    for k in ALL_K:
        cap5k = knn_capability_closed_form(k); cap5 = s5_capability_closed_form(k)
        adm = ["S4", "S2a"] + (["S5k"] if cap5k >= smooth.THETA else [])
        cells = {}; called = abstained = 0
        for col in cols:
            for Hh in H_GRID:
                for r in R_GRID:
                    c = {row: smooth.cost(pe[col][row], Hh, r) for row in adm}
                    w = min(c, key=c.get); others = [c[x] for x in adm if x != w]
                    margin = (min(others) - c[w]) / c[w]
                    call = w if margin >= MARGIN else "ABSTAIN"
                    cells[f"{col}|H={Hh}|r={r}"] = {"predicted": call, "cost_gap_fraction": round(margin, 4), "costs": {x: round(v, 1) for x, v in c.items()}}
                    called += call != "ABSTAIN"; abstained += call == "ABSTAIN"
        hstar = {}
        for col in cols:
            a, b = pe[col]["S5k"], pe[col]["S4"]
            # S5k cheaper than S4 iff (a.desc - b.desc) + H (a.exec - b.exec) + r (a.slope - b.slope) < 0; solve for H at each r
            slope = lambda q: q["upd_e"] + q["ver_e"] + q["rev_e"] / 4
            dE = a["exec_q"] - b["exec_q"]
            hstar[col] = {str(r): (round(((b["desc"] - a["desc"]) + r * (slope(b) - slope(a))) / dE, 2) if dE > 0 else None) for r in R_GRID}
        per_k[str(k)] = {"a": k / 16, "predicted_capability": {"S5k": cap5k, "S5": cap5, "S4": ">= theta (h=4; not closed-form)", "S2a": ">= theta (quantized-consistency argument; not closed-form)", "S3": "< theta"},
                         "predicted_admissible": adm, "cells": cells, "n_called": called, "n_abstained": abstained, "predicted_Hstar_S5k_to_S4_by_r": hstar}
    out = {"schema": "StageDESymPredictionV1", "issue": 377, "revival_record": "RV-377-021", "candidates_three_class_in_order": CANDIDATES_THREE_CLASS, "boundary_k": BOUNDARY,
           "ecology": {"coeffs": "(a, a, a, a), a = k/16", "n_events": N_EVENTS, "criterion": "unseen", "theta": smooth.THETA, "rows": list(smooth.ROWS_V4), "train": smooth.TRAIN},
           "cost_source": "STAGE_DE_SMOOTH_V4B_SMOOTH3_ROWS_V4_CALIB.json (E_smooth3; S5k costs are schedule-determined and ecology-independent, S4/S2a costs weakly data-dependent)",
           "per_event_costs_used": pe, "margin_rule": MARGIN, "per_k": per_k,
           "frozen_claims": [
               "C1: S5k's observed unseen capability equals knn_capability_closed_form(k) to 4 decimals at every k in {3,5,7,8} in every column",
               "C2: S5's observed unseen capability equals s5_capability_closed_form(k) to 4 decimals at every k",
               "C3: at the first candidate k in [5,3,7] where S4 and S2a are both admissible, S5k is admissible too and S5, S3 are not -> THREE admissible classes (gradient, approximate search, generalizing memory); fallback order declared; if no candidate qualifies the record is NEGATIVE with no further search",
               "C4: at k=8 S5k is inadmissible (0.8333) while S4 and S2a stay admissible -> the generalizing-memory form leaves the frontier at the closed-form boundary between 7/16 and 8/16",
               "C5: every CALLED cell's observed frontier winner equals the prediction (ties count if the predicted row is among the winners) at every k",
               "C6: at every three-class k and every column: S2a wins r=0 at every H (the search form owns the no-revision axis); at r=8, where 1 <= H*(8) <= 128 (B0, B3: H* = 34.2) the observed S5k->S4 switch along H lies within one grid step of H*(8) (S5k = generalizing memory wins the SHORT horizons, S4 = gradient the LONG ones: Codex RP3 horizon crossover with a memory form), where H*(8) < 1 (B1, U, P3) S4 wins every H at r=8, and where no crossing exists (B2: S4's emulated exec cost exceeds S5k's at every H) S5k wins every H at r=8",
               "C7: the observed S5k capability is strictly decreasing in k over {3,5,7,8}"]}
    out["receipt_sha256"] = sha256_of({k: v for k, v in out.items() if k != "receipt_sha256"})
    json.dump(out, open(os.path.join(RES, "STAGE_DE_SYM_PREDICTION.json"), "w"), indent=1, sort_keys=True, default=str)
    return out


if __name__ == "__main__":
    o = main()
    for k, v in o["per_k"].items():
        print(f"k={k} a={v['a']}: caps {v['predicted_capability']['S5k']} (S5k) {v['predicted_capability']['S5']} (S5); admissible {v['predicted_admissible']}; called {v['n_called']} abstained {v['n_abstained']}")
        print("   H* by r (B0):", v["predicted_Hstar_S5k_to_S4_by_r"]["B0_LOCAL_ADAPTIVE_TRANSDUCERS"])
        for col in bases.ALL:
            print("  ", col.split("_")[0], "H=16:", [v["cells"][f"{col}|H=16|r={r}"]["predicted"] for r in R_GRID], "| r=8 by H:", [v["cells"][f"{col}|H={h}|r=8"]["predicted"] for h in H_GRID])
