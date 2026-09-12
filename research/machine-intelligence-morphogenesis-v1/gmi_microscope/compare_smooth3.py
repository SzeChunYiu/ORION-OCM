"""RV-377-017 adjudication: compare the executed E_smooth3 frontier (STAGE_DE_SMOOTH_V4_SMOOTH3_GEN.json) with the
frozen prediction (STAGE_DE_SMOOTH3_PREDICTION.json). Writes microscopes/results/STAGE_DE_SMOOTH3_VERDICT.json."""
from __future__ import annotations

import json
import os

from .core import sha256_of
from .predict_smooth3 import H_GRID, R_GRID

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")


def main():
    pred = json.load(open(os.path.join(RES, "STAGE_DE_SMOOTH3_PREDICTION.json")))
    obs = json.load(open(os.path.join(RES, "STAGE_DE_SMOOTH_V4_SMOOTH3_GEN.json")))
    cols = [c for c in obs["PH_REV"]]
    theta = obs["ecology"]["theta"]
    # claim 2: inadmissible rows
    caps = obs["capability_by_cell"]
    inadm = {row: all(caps[k] < theta for k in caps if k.startswith(row + "|")) for row in ("S5", "S3", "S2")}
    adm = {row: all(caps[k] >= theta for k in caps if k.startswith(row + "|") and k.endswith("|4")) for row in ("S4", "S2a")}
    # claim 1: called cells
    wrong = []; n_called = 0
    for key, cell in pred["cells"].items():
        if cell["predicted"] == "ABSTAIN":
            continue
        n_called += 1
        winners = obs["frontier_H_r"][key]
        if cell["predicted"] not in winners:
            wrong.append({"cell": key, "predicted": cell["predicted"], "observed": winners})
    # claim 3: crossing within one grid step of r* at H=16
    crossings = {}
    for col in cols:
        seq = [obs["frontier_H_r"][f"{col}|H=16|r={r}"] for r in R_GRID]
        obs_int = None
        for i in range(1, len(R_GRID)):
            if "S2a" in seq[i - 1] and "S4" in seq[i] and "S2a" not in seq[i]:
                obs_int = (R_GRID[i - 1], R_GRID[i]); break
        rstar = pred["predicted_rstar_H16"][col]
        ok = obs_int is not None and rstar is not None and obs_int[0] <= rstar <= obs_int[1]
        crossings[col] = {"predicted_rstar": rstar, "observed_interval": obs_int, "within_one_grid_step": ok, "winners_by_r": seq}
    verdict = {"claim_1_all_called_cells_correct": not wrong, "n_called": n_called, "n_wrong": len(wrong), "wrong_cells": wrong[:20],
               "claim_2_S5_S3_S2_inadmissible": all(inadm.values()), "inadmissible_by_row": inadm, "admissible_S4_S2a": adm,
               "claim_3_crossing_within_one_grid_step": all(v["within_one_grid_step"] for v in crossings.values()), "crossings_H16": crossings,
               "claim_4_S2a_r0_S4_r_ge_1_every_H": all(("S2a" in obs["frontier_H_r"][f"{col}|H={Hh}|r=0"]) and all("S4" in obs["frontier_H_r"][f"{col}|H={Hh}|r={r}"] and "S2a" not in obs["frontier_H_r"][f"{col}|H={Hh}|r={r}"] for r in R_GRID[1:]) for col in cols for Hh in H_GRID)}
    verdict["all_claims_hold"] = all(verdict[k] for k in ("claim_1_all_called_cells_correct", "claim_2_S5_S3_S2_inadmissible", "claim_3_crossing_within_one_grid_step", "claim_4_S2a_r0_S4_r_ge_1_every_H"))
    out = {"schema": "StageDESmooth3VerdictV1", "issue": 377, "revival_record": "RV-377-017", "prediction_sha256": pred["receipt_sha256"], "observation_sha256": obs["receipt_sha256"], "verdict": verdict}
    out["receipt_sha256"] = sha256_of({k: v for k, v in out.items() if k != "receipt_sha256"})
    json.dump(out, open(os.path.join(RES, "STAGE_DE_SMOOTH3_VERDICT.json"), "w"), indent=1, sort_keys=True, default=str)
    return out


if __name__ == "__main__":
    o = main()
    v = o["verdict"]
    print({k: v[k] for k in v if k.startswith("claim") or k == "all_claims_hold"})
    print("wrong:", v["wrong_cells"][:5])
    for col, c in v["crossings_H16"].items():
        print(col.split("_")[0], c["predicted_rstar"], c["observed_interval"], c["winners_by_r"])
