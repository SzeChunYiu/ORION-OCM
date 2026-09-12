"""RV-377-017 frozen prediction for E_smooth3 (written and run BEFORE the frontier run; see REVIVAL_LEDGER).

Inputs allowed at freeze time: (a) the registration/certification costs of S4 and S2a in column B0 at 16 events on
E_smooth3 (admissibility certificate; S5/S3/S2 certified inadmissible under the unseen-input criterion);
(b) the column/B0 per-coordinate cost ratios of S4 and S2a measured on a DIFFERENT ecology and length
(E_smooth2 at 48 events, STAGE_DE_SMOOTH_V3_SMOOTH2_D48.json). Output: predicted frontier winner on every
(column, H, r) cell among the two admissible rows, with a declared abstention where the predicted cost margin
is below 10%. Writes microscopes/results/STAGE_DE_SMOOTH3_PREDICTION.json.
"""
from __future__ import annotations

import json
import os

from . import bases, smooth
from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
H_GRID = [1, 2, 4, 8, 16, 32, 64, 128]; R_GRID = [0, 1, 2, 4, 8, 16, 32]
N_EVENTS = 16; MARGIN = 0.10
COORDS = ("desc", "exec", "upd", "ver", "rev")


def main():
    target = smooth.make_target(smooth.COEFFS_V3)
    b0 = "B0_LOCAL_ADAPTIVE_TRANSDUCERS"
    cert = {row: smooth.run(row, bases.B0, 4, 0, target, N_EVENTS, smooth.ROWS_V3, "unseen") for row in ("S4", "S2a", "S5", "S2")}
    cert_caps = {row: cert[row]["capability"] for row in cert}
    adm = [row for row in ("S4", "S2a") if cert_caps[row] >= smooth.THETA]
    assert adm == ["S4", "S2a"] and cert_caps["S5"] < smooth.THETA and cert_caps["S2"] < smooth.THETA
    ref = json.load(open(os.path.join(RES, "STAGE_DE_SMOOTH_V3_SMOOTH2_D48.json")))
    cols = list(bases.ALL)
    pred_costs = {}
    for col in cols:
        pred_costs[col] = {}
        for row in adm:
            base = cert[row]["R"]
            ratio = {c: ref["R_by_cell"][f"{row}|{col}|4"][c] / max(ref["R_by_cell"][f"{row}|{b0}|4"][c], 1) for c in COORDS}
            R = {c: base[c] * ratio[c] for c in COORDS}
            pred_costs[col][row] = smooth.per_event(R, N_EVENTS)
    cells = {}; called = 0; abstained = 0
    for col in cols:
        for Hh in H_GRID:
            for r in R_GRID:
                c = {row: smooth.cost(pred_costs[col][row], Hh, r) for row in adm}
                w = min(c, key=c.get); other = [x for x in adm if x != w][0]
                margin = (c[other] - c[w]) / c[w]
                call = w if margin >= MARGIN else "ABSTAIN"
                cells[f"{col}|H={Hh}|r={r}"] = {"predicted": call, "cost_gap_fraction": round(margin, 4), "costs": {k: round(v, 1) for k, v in c.items()}}
                called += call != "ABSTAIN"; abstained += call == "ABSTAIN"
    rstar = {col: smooth.analytic_rstar(pred_costs[col]["S2a"], pred_costs[col]["S4"], 16) for col in cols}
    out = {"schema": "StageDESmooth3PredictionV1", "issue": 377, "revival_record": "RV-377-017", "ecology": {"coeffs": list(smooth.COEFFS_V3), "n_events": N_EVENTS, "criterion": "unseen", "theta": smooth.THETA},
           "certification_capabilities_B0": cert_caps, "admissible_rows": adm, "column_ratio_source": "STAGE_DE_SMOOTH_V3_SMOOTH2_D48.json (E_smooth2, 48 events)",
           "predicted_per_event_costs": pred_costs, "predicted_rstar_H16": rstar, "cells": cells, "n_called": called, "n_abstained": abstained, "margin_rule": MARGIN,
           "frozen_claims": ["every CALLED cell's observed frontier winner equals the prediction (ties count as correct if the predicted row is among the winners)",
                              "S5, S3, S2 are inadmissible in every column (C2)",
                              "in every column the observed S2a->S4 crossing at H=16 lies within one grid step of predicted_rstar_H16",
                              "S2a wins r=0 at H<=16 in every column; S4 wins r>=1 at H<=16 in every column (the dense row wins the revision axis because the approximate-search row's per-event work is ~200x larger)"]}
    out["receipt_sha256"] = sha256_of({k: v for k, v in out.items() if k != "receipt_sha256"})
    json.dump(out, open(os.path.join(RES, "STAGE_DE_SMOOTH3_PREDICTION.json"), "w"), indent=1, sort_keys=True, default=str)
    return out


if __name__ == "__main__":
    o = main()
    print("cert caps:", o["certification_capabilities_B0"], "| called", o["n_called"], "abstained", o["n_abstained"])
    print("r* H16:", o["predicted_rstar_H16"])
    for col in bases.ALL:
        print(col.split("_")[0], [o["cells"][f"{col}|H=16|r={r}"]["predicted"] for r in R_GRID], "| H=128:", [o["cells"][f"{col}|H=128|r={r}"]["predicted"] for r in R_GRID])
