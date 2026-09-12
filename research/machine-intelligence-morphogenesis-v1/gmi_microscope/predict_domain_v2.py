"""RV-377-060 — second prospective test of the corrected DOMAIN SELECTION LAW (theory core L8v2).

L8v2, after the failures recorded in RV-377-059:
  (a) ADMISSIBILITY from closed forms: cap_S5h(k) = (48 - |k|)/48 (exact on nine executed ecologies);
      cap_S5(k) = 1 - |k|/12; S4 admissible iff |k| <= 4 (the threshold corrected from the nine executed points:
      0.9167 / 0.8854 / 0.8646 / 0.7812 / 0.7500 / 0.7240 / 0.6510 / 0.5990 / 0.4375 at k = 2..9, 11); S2a always
      admissible; S3 never at seed 0. NEW SYMMETRY CLAIM: capability is invariant under a -> -a, so E_sym(-k) has the
      same capabilities as E_sym(k) — this is what makes four more ecologies with two admissible carriers available.
  (b) r = 0: the program/search domain D4/D5 occupies every H >= 2; the (H = 1) description corner is ABSTAINED because
      the search row's description is ecology-dependent (154-334 bits across the executed ecologies).
  (c) r >= 1: the occupant is the admissible row minimising the FIXED lifecycle line. The memory and gradient rows'
      per-event coordinates are ecology-independent (S5h exactly; S4 to within 0.2 percent), so the (H, r) phase
      boundary is a fixed curve per column, computed once from STAGE_DE_SMOOTH_V8_SYM5_H.json and reused unchanged.
  (d) the probabilistic domain D3 and the stochastic-population domain D7 occupy no cell.
"""
from __future__ import annotations

import json
import os

from . import bases, smooth
from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
H_GRID = [1, 2, 4, 8, 16, 32, 64, 128]
R_GRID = [0, 1, 2, 4, 8, 16, 32]
THETA = 0.85
NEW_K = [1, -1, -2, -3, -4, 10, 12, 13]
COORD_SOURCE = "STAGE_DE_SMOOTH_V8_SYM5_H.json"
DOMAIN = {"S4": "D1", "S2a": "D4/D5", "S5h": "D2", "S5": "D2", "S3": "D7"}


def cap_s5h(k): return round((48 - abs(k)) / 48, 4)


def cap_s5(k): return round(max(0.0, 1 - abs(k) / 12), 4)


def admissible_set(k):
    a = ["S2a"]
    if cap_s5h(k) >= THETA: a.append("S5h")
    if abs(k) <= 4: a.append("S4")
    return sorted(a)


def fixed_lines():
    d = json.load(open(os.path.join(RES, COORD_SOURCE)))
    cols = sorted({key.split("|")[1] for key in d["R_by_cell"]})
    return {c: {row: smooth.per_event(d["R_by_cell"][f"{row}|{c}|4"], 16) for row in ("S4", "S5h")} for c in cols}


def main(tag="V2"):
    pe = fixed_lines(); cols = sorted(pe); per_k = {}
    for k in NEW_K:
        adm = admissible_set(k); cells = {}; abstained = []
        for c in cols:
            for H in H_GRID:
                for r in R_GRID:
                    key = f"{c}|H={H}|r={r}"
                    if r == 0:
                        if H == 1: abstained.append(key); continue
                        cells[key] = "S2a"; continue
                    cand = [row for row in ("S4", "S5h") if row in adm]
                    if not cand: cells[key] = "S2a"; continue
                    cells[key] = min(cand, key=lambda row: smooth.cost(pe[c][row], H, r))
        per_k[f"E_sym{k}"] = {"k": k, "predicted_capabilities": {"S5h": cap_s5h(k), "S5": cap_s5(k), "S4": "admissible iff |k| <= 4", "S2a": "admissible", "S3": "< theta at seed 0"},
                              "predicted_admissible_set": adm, "predicted_occupant_row": cells, "predicted_occupant_domain": {key: DOMAIN[v] for key, v in cells.items()},
                              "abstained_cells": abstained, "n_predicted": len(cells), "n_abstained": len(abstained),
                              "domain_share": {dm: round(sum(1 for x in cells.values() if DOMAIN[x] == dm) / len(cells), 4) for dm in sorted({DOMAIN[x] for x in cells.values()})}}
    out = {"schema": "StageDEDomainSelectionPredictionV2", "issue": [377, 422], "revival_record": "RV-377-060", "status": "FROZEN_BEFORE_EXECUTION", "supersedes": "RV-377-059 / STAGE_DE_DOMAIN_PREDICTION_V1.json",
           "law_L8v2": {"admissibility": "cap_S5h = (48-|k|)/48; cap_S5 = 1-|k|/12; S4 iff |k|<=4; S2a always; S3 never",
                        "sign_symmetry_claim": "capabilities are invariant under a -> -a",
                        "r0": "D4/D5 at H >= 2; ABSTAIN at H = 1 (search-row description is ecology-dependent)",
                        "r_ge_1": f"argmin of the FIXED lifecycle lines over the admissible rows, coordinates taken once from {COORD_SOURCE}",
                        "never": "D3 and D7 occupy no cell"},
           "fixed_per_event_coordinates": {c: {row: pe[c][row] for row in pe[c]} for c in cols},
           "grids": {"H": H_GRID, "r": R_GRID, "columns": cols}, "ecologies": per_k,
           "total_predicted_cells": sum(v["n_predicted"] for v in per_k.values()), "total_abstained_cells": sum(v["n_abstained"] for v in per_k.values()),
           "claim_ceiling": "a-priori prediction from the ecology parameter alone plus one fixed coordinate table measured on an already-executed ecology; none of the eight new ecologies was measured before freezing"}
    out["receipt_sha256"] = sha256_of({k: v for k, v in out.items() if k != "receipt_sha256"})
    json.dump(out, open(os.path.join(RES, f"STAGE_DE_DOMAIN_PREDICTION_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    print("frozen:", len(per_k), "ecologies,", out["total_predicted_cells"], "cells predicted,", out["total_abstained_cells"], "abstained")
    for name, v in per_k.items(): print(" ", name, "adm", v["predicted_admissible_set"], "S5h", v["predicted_capabilities"]["S5h"], "share", v["domain_share"])
    return out


if __name__ == "__main__":
    main()
