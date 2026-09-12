"""RV-377-059 — prospective test of the DOMAIN SELECTION LAW (theory core L8).

The law induced from 11 592 executed frontier cells over 34 receipts says which STRUCTURAL DOMAIN occupies a frontier
cell as a function of the ecology's coordinates alone:

  L8.1  r = 0 (no revision): the deliberative program/search domain D4/D5 occupies every reuse horizon H >= 2, because
        with no revisions the search row's update cost is never paid and its description is the smallest admissible one.
        At H = 1 the description corner belongs to the memory domain D2 whenever its row is admissible (desc 206 + 74
        against 314 + 4).
  L8.2  r >= 1 in a scan-store or native-store price vector: the exemplar memory domain D2 occupies whenever its row is
        admissible; where it is not, the coefficient domain D1 occupies if admissible, else D4/D5.
  L8.3  r >= 1 in a uniform or compressed-program price vector: the coefficient domain D1 occupies wherever it is
        admissible, else D2, else D4/D5.
  L8.4  the probabilistic domain D3 occupies no cell at the registered 8-bit precision (precision gate, RV-029/031) and
        the stochastic-population domain D7 occupies no cell at reliability q = 0.5 (RV-040/041b).

Admissibility itself is predicted from closed forms, so the whole chain runs from the ecology parameter k with no
measurement of the new ecologies:

  cap_S5h(k) = (48 - k)/48      exact on the four executed points k = 3, 5, 7, 8 (0.9375, 0.8958, 0.8542, 0.8333)
  cap_S5(k)  = 1 - k/12         the exemplar row returns 0 on unseen inputs (RV-021 closed form)
  cap_S2a(k) >= 0.9375          the approximate search row is admissible on every executed symmetric ecology
  cap_S4(k)  monotone decreasing, admissible only for k <= 3 (executed: 0.8854, 0.7812, 0.7240, 0.6510 at k = 3, 5, 7, 8)
  cap_S3(k)  below theta at seed 0 (RV-040 census: admissible on about 5 percent of seeds)

Writes microscopes/results/STAGE_DE_DOMAIN_PREDICTION_V1.json before any of the new ecologies is executed.
"""
from __future__ import annotations

import json
import os

from . import bases
from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
H_GRID = [1, 2, 4, 8, 16, 32, 64, 128]
R_GRID = [0, 1, 2, 4, 8, 16, 32]
THETA = 0.85
NEW_K = [2, 4, 6, 9, 11]
DOMAIN = {"S4": "D1", "S2a": "D4/D5", "S5h": "D2", "S5": "D2", "S3": "D7"}
SCAN = ("B0", "B1", "B3")
NATIVE = ("B2",)
UNIFORM = ("U_", "P3")


def col_class(c):
    if c.startswith(SCAN): return "scan-store"
    if c.startswith(NATIVE): return "native-store"
    return "uniform/compressed"


def cap_s5h(k): return round((48 - k) / 48, 4)


def cap_s5(k): return round(max(0.0, 1 - k / 12), 4)


def admissible_set(k):
    a = ["S2a"]
    if cap_s5h(k) >= THETA: a.append("S5h")
    if k <= 3: a.append("S4")
    return sorted(a)


def predict_cell(k, col, H, r):
    """the domain (and the row that carries it) predicted to occupy this frontier cell."""
    adm = admissible_set(k); cls = col_class(col)
    if r == 0:
        if "S5h" in adm and H == 1: return "S5h"
        return "S2a"
    if cls in ("scan-store", "native-store"):
        if "S5h" in adm: return "S5h"
        if "S4" in adm: return "S4"
        return "S2a"
    if "S4" in adm: return "S4"
    if "S5h" in adm: return "S5h"
    return "S2a"


def main(tag="V1"):
    cols = list(bases.ALL); per_k = {}
    for k in NEW_K:
        adm = admissible_set(k)
        cells = {f"{c}|H={H}|r={r}": predict_cell(k, c, H, r) for c in cols for H in H_GRID for r in R_GRID}
        dom = {key: DOMAIN[v] for key, v in cells.items()}
        per_k[f"E_sym{k}"] = {"k": k, "predicted_capabilities": {"S5h": cap_s5h(k), "S5": cap_s5(k), "S2a": ">= 0.9375", "S4": "< 0.85 unless k <= 3", "S3": "< 0.85 at seed 0"},
                              "predicted_admissible_set": adm, "predicted_occupant_row": cells, "predicted_occupant_domain": dom,
                              "n_cells": len(cells), "domain_share": {d: round(sum(1 for x in dom.values() if x == d) / len(dom), 4) for d in sorted(set(dom.values()))}}
    out = {"schema": "StageDEDomainSelectionPredictionV1", "issue": [377, 422], "revival_record": "RV-377-059", "status": "FROZEN_BEFORE_EXECUTION",
           "law": {"L8.1": "r = 0: D4/D5 at H >= 2; D2 at H = 1 when its row is admissible", "L8.2": "r >= 1, scan/native store: D2 if admissible, else D1 if admissible, else D4/D5",
                   "L8.3": "r >= 1, uniform/compressed: D1 if admissible, else D2, else D4/D5", "L8.4": "D3 and D7 occupy no cell"},
           "closed_forms": {"cap_S5h": "(48 - k)/48", "cap_S5": "1 - k/12", "S4_admissible_iff": "k <= 3"},
           "grids": {"H": H_GRID, "r": R_GRID, "columns": cols}, "ecologies": per_k,
           "total_predicted_cells": sum(v["n_cells"] for v in per_k.values()),
           "claim_ceiling": "a-priori prediction of frontier occupancy from the ecology parameter alone; no coordinate of the five new ecologies was measured before freezing"}
    out["receipt_sha256"] = sha256_of({k: v for k, v in out.items() if k != "receipt_sha256"})
    json.dump(out, open(os.path.join(RES, f"STAGE_DE_DOMAIN_PREDICTION_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    print("frozen prediction for", len(per_k), "ecologies,", out["total_predicted_cells"], "cells")
    for name, v in per_k.items(): print(" ", name, "adm", v["predicted_admissible_set"], "cap_S5h", v["predicted_capabilities"]["S5h"], "domain share", v["domain_share"])
    return out


if __name__ == "__main__":
    main()
