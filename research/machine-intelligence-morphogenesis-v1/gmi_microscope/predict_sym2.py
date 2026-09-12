"""RV-377-025 frozen prediction: the RV-021 test re-run with the corrected Hamming kNN row S5h (ROWS_V6) and with EVERY
row's admissibility certified per ecology before freezing (design §9 admissibility-before-phase rule).

Inputs allowed at freeze time (all disclosed in REVIVAL_LEDGER RV-377-025):
  (a) closed-form capabilities of S5h and S5 (predict_sym.knn_capability_closed_form / s5_capability_closed_form);
  (b) certified capabilities of S4, S2a, S5, S3 on E_sym(k), k in {3,5,7,8}, from the RV-021 receipts STAGE_DE_SMOOTH_V6_SYM<k>.json
      (those rows were valid there; only S5k was defective), and on E_smooth3 from STAGE_DE_SMOOTH_V4_SMOOTH3_GEN.json;
  (c) S5h's capability on E_smooth3 from one B0 certification run (0.901; C2 makes it column-independent);
  (d) per-column per-event costs of S4, S2a, S5h from the calibration on the ORIGINAL E_smooth (V1 coefficients):
      STAGE_DE_SMOOTH_V4C_SMOOTH1_ROWS_V6_CALIB.json (S5h's costs are schedule-determined; S4/S2a costs are weakly data-dependent).
Output: microscopes/results/STAGE_DE_SYM2_PREDICTION.json: per ecology the predicted admissible set, every (column, H, r) cell
(10% margin rule, else ABSTAIN), the predicted crossovers, and the frozen claims.
"""
from __future__ import annotations

import json
import os

from . import bases, smooth
from .core import sha256_of
from .predict_sym import H_GRID, MARGIN, N_EVENTS, R_GRID, knn_capability_closed_form, s5_capability_closed_form

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
ECOLOGIES = ["SYM3", "SYM5", "SYM7", "SYM8", "SMOOTH3"]
S5H_SMOOTH3_CERT = 0.901  # one-column (B0) certification run at freeze time, disclosed


def main():
    calib = json.load(open(os.path.join(RES, "STAGE_DE_SMOOTH_V4C_SMOOTH1_ROWS_V6_CALIB.json")))
    cols = list(bases.ALL)
    pe = {col: {row: smooth.per_event(calib["R_by_cell"][f"{row}|{col}|4"], N_EVENTS) for row in ("S4", "S2a", "S5h")} for col in cols}
    cert = {}
    for k in (3, 5, 7, 8):
        obs = json.load(open(os.path.join(RES, f"STAGE_DE_SMOOTH_V6_SYM{k}.json")))
        cert[f"SYM{k}"] = {row: obs["capability_by_cell"][f"{row}|{cols[0]}|4"] for row in ("S4", "S2a", "S5", "S3")}
        cert[f"SYM{k}"]["S5h"] = knn_capability_closed_form(k)
        assert cert[f"SYM{k}"]["S5"] == s5_capability_closed_form(k)
    obs3 = json.load(open(os.path.join(RES, "STAGE_DE_SMOOTH_V4_SMOOTH3_GEN.json")))
    cert["SMOOTH3"] = {row: obs3["capability_by_cell"][f"{row}|{cols[0]}|4"] for row in ("S4", "S2a", "S5", "S3")}
    cert["SMOOTH3"]["S5h"] = S5H_SMOOTH3_CERT
    per_eco = {}
    for eco in ECOLOGIES:
        adm = [row for row in ("S4", "S2a", "S5h") if cert[eco][row] >= smooth.THETA]
        cells = {}; called = abstained = 0
        for col in cols:
            for Hh in H_GRID:
                for r in R_GRID:
                    c = {row: smooth.cost(pe[col][row], Hh, r) for row in adm}
                    w = min(c, key=c.get); others = [c[x] for x in adm if x != w]
                    margin = (min(others) - c[w]) / c[w] if others else 1.0
                    call = w if margin >= MARGIN else "ABSTAIN"
                    cells[f"{col}|H={Hh}|r={r}"] = {"predicted": call, "cost_gap_fraction": round(margin, 4), "costs": {x: round(v, 1) for x, v in c.items()}}
                    called += call != "ABSTAIN"; abstained += call == "ABSTAIN"
        hstar = {}
        if "S5h" in adm and "S4" in adm:
            for col in cols:
                a, b = pe[col]["S5h"], pe[col]["S4"]
                slope = lambda q: q["upd_e"] + q["ver_e"] + q["rev_e"] / 4
                dE = a["exec_q"] - b["exec_q"]
                hstar[col] = {str(r): (round(((b["desc"] - a["desc"]) + r * (slope(b) - slope(a))) / dE, 2) if dE > 0 else None) for r in R_GRID}
        per_eco[eco] = {"certified_capabilities": cert[eco], "predicted_admissible": adm, "cells": cells, "n_called": called, "n_abstained": abstained, "predicted_Hstar_S5h_to_S4_by_r": hstar}
    out = {"schema": "StageDESym2PredictionV1", "issue": 377, "revival_record": "RV-377-025", "ecologies": ECOLOGIES, "rows": list(smooth.ROWS_V6), "theta": smooth.THETA, "margin_rule": MARGIN,
           "cost_source": "STAGE_DE_SMOOTH_V4C_SMOOTH1_ROWS_V6_CALIB.json (E_smooth V1 coefficients)", "per_event_costs_used": pe, "per_ecology": per_eco,
           "frozen_claims": [
               "C1: S5h's observed unseen capability equals the closed form at every k in {3,5,7,8} in every column (0.9375, 0.8958, 0.8542, 0.8333) and equals 0.901 on E_smooth3",
               "C2: the observed admissible set equals predicted_admissible in every ecology: SYM3 {S4, S2a, S5h} (three classes), SYM5 and SYM7 {S2a, S5h}, SYM8 {S2a}, SMOOTH3 {S4, S2a, S5h} (three classes); S5 and S3 inadmissible everywhere",
               "C3: every CALLED cell's observed frontier winner equals the prediction (ties count if the predicted row is among the winners) in all five ecologies",
               "C4: in the two three-class ecologies S2a wins r=0 at every H in every column; at r=8 the S5h->S4 switch along H lies within one grid step of predicted_Hstar_S5h_to_S4_by_r['8'] where 1 <= H* <= 128, S4 wins every H where H* < 1, and S5h wins every H where no crossing exists",
               "C5: in SYM5 and SYM7 (gradient row inadmissible) the generalizing memory S5h wins every r >= 1 at every H in every column and S2a wins r=0 wherever called",
               "C6: C2 (identical Dev tables across columns) holds in all five runs"]}
    out["receipt_sha256"] = sha256_of({k: v for k, v in out.items() if k != "receipt_sha256"})
    json.dump(out, open(os.path.join(RES, "STAGE_DE_SYM2_PREDICTION.json"), "w"), indent=1, sort_keys=True, default=str)
    return out


if __name__ == "__main__":
    o = main()
    for eco, v in o["per_ecology"].items():
        print(eco, "cert", v["certified_capabilities"], "adm", v["predicted_admissible"], "called", v["n_called"], "abstained", v["n_abstained"])
        if v["predicted_Hstar_S5h_to_S4_by_r"]:
            print("   H*(8) by column:", {c.split("_")[0]: h["8"] for c, h in v["predicted_Hstar_S5h_to_S4_by_r"].items()})
        for col in bases.ALL:
            print("  ", col.split("_")[0], "H=16:", [v["cells"][f"{col}|H=16|r={r}"]["predicted"] for r in R_GRID], "| r=8 by H:", [v["cells"][f"{col}|H={h}|r=8"]["predicted"] for h in H_GRID])
