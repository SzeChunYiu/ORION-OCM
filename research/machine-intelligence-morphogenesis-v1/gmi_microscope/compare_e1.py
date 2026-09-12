"""RV-377-032 adjudication of the E1 VLC microscope receipt (STAGE_E1_V13_E1_VLC.json) against the frozen clauses
(REVIVAL_LEDGER RV-377-032). Writes microscopes/results/STAGE_E1_V13_VERDICT.json."""
from __future__ import annotations

import json
import os

from .core import sha256_of
from .e1_vlc import CELLS, ROWS, lifecycle_cost

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
EXPECTED_WINNER = {"RSTAR": "VLC", "T1_STATIONARY": "MOD_U", "T2_DENSE_CONE": "VLC", "T3_WEAK_RETENTION": "MOD_U", "T4_SHORT_REUSE": "MOD_U"}


def lambda_star(m, v, H, U):
    """retention price at which VLC's lifecycle cost equals MOD_U's (per-update accounting; abstention priced lambda/16)."""
    dC = (v["per_update"]["upd"] + v["per_update"]["ver"] + v["per_update"]["rev"]) - (m["per_update"]["upd"] + m["per_update"]["ver"] + m["per_update"]["rev"])
    dC += ((v["desc_state"] - m["desc_state"]) + H * (v["per_query_exec"] - m["per_query_exec"])) / U
    denom = (m["wrong_per_update"] - v["wrong_per_update"]) - v["abstain_per_update"] / 16
    return (dC / denom) if denom > 0 else None


def main():
    d = json.load(open(os.path.join(RES, "STAGE_E1_V13_E1_VLC.json")))
    cols = sorted({k.split("|")[2] for k in d["cells"]})
    v = {"observation_sha256": d["receipt_sha256"]}
    v["C1_column_invariance"] = all(d["C2_capability_and_regression_column_invariant"].values())
    adm_ok = True; adm_detail = {}
    for cell in CELLS:
        for col in cols:
            a = sorted(d["admissible"][f"{cell}|{col}"]); adm_detail[f"{cell}|{col}"] = a
            adm_ok &= a == ["MOD_U", "MONO_C", "VLC"]
    v["C2_admissible_sets"] = adm_ok; v["C2_detail"] = adm_detail
    win_ok = True; win_detail = {}
    for cell, exp in EXPECTED_WINNER.items():
        for col in cols:
            w = d["frontier"][f"{cell}|{col}"]; win_detail[f"{cell}|{col}"] = w; win_ok &= (w == [exp])
    v["C3_phase_direction_every_column"] = win_ok; v["C3_detail"] = win_detail; v["C3_expected"] = EXPECTED_WINNER
    ls = {}
    for col in cols:
        m = d["cells"][f"RSTAR|MOD_U|{col}"]; vv = d["cells"][f"RSTAR|VLC|{col}"]
        ls[col] = lambda_star(m, vv, CELLS["RSTAR"]["H"], CELLS["RSTAR"]["U"])
    v["C4_lambda_star_in_0_256_every_column"] = all(x is not None and 0 < x < 256 for x in ls.values()); v["C4_lambda_star_by_column"] = ls
    b0 = [c for c in cols if c.startswith("B0")][0]; b2 = [c for c in cols if c.startswith("B2")][0]
    v["C4b_lambda_star_B2_above_B0"] = bool(ls[b2] is not None and ls[b0] is not None and ls[b2] > ls[b0])
    v["C5_MONO_C_on_no_frontier_cell"] = all("MONO_C" not in w for k, w in d["frontier"].items())
    v["C6_DENSE_inadmissible_everywhere"] = all(d["cells"][f"{cell}|DENSE|{col}"]["capability"] < 0.85 for cell in CELLS for col in cols)
    # exposure accounting facts
    v["exposure_B0_RSTAR"] = {row: {k: d["cells"][f"RSTAR|{row}|{b0}"][k] for k in ("wrong_served_in_window", "abstained_in_window", "regressions")} for row in ROWS}
    keys = ["C1_column_invariance", "C2_admissible_sets", "C3_phase_direction_every_column", "C4_lambda_star_in_0_256_every_column", "C4b_lambda_star_B2_above_B0", "C5_MONO_C_on_no_frontier_cell", "C6_DENSE_inadmissible_everywhere"]
    v["all_claims_hold"] = all(v[k] for k in keys)
    out = {"schema": "StageE1VLCVerdictV1", "issue": 377, "related": [418, 419], "revival_record": "RV-377-032", "verdict": v}
    out["receipt_sha256"] = sha256_of({k: x for k, x in out.items() if k != "receipt_sha256"})
    json.dump(out, open(os.path.join(RES, "STAGE_E1_V13_VERDICT.json"), "w"), indent=1, sort_keys=True, default=str)
    return out


if __name__ == "__main__":
    o = main(); v = o["verdict"]
    print({k: v[k] for k in v if k[:2] in ("C1", "C2", "C3", "C4", "C5", "C6") and "detail" not in k and "by_column" not in k})
    print("all:", v["all_claims_hold"]); print("lambda*:", {c.split("_")[0]: (round(x, 1) if x else None) for c, x in v["C4_lambda_star_by_column"].items()})
    for k, w in v["C3_detail"].items(): print("  ", k.split("|")[0], k.split("|")[1].split("_")[0], w)
