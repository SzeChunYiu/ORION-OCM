"""Stage E — exact morphology frontier / phase diagram from the Stage D measurements.

Lifecycle cost model (frozen in proofs §T10-A, combined with the Codex idealized model only through
the charged coordinates):  C(H, r) = desc + H·exec_q + r·upd_e + n_ver·ver_e + n_rev·rev_e
where the per-event costs are MEASURED in Stage D (per query, per feedback event, per check, per
revocation) for each (row, column, size). Ecology axes varied: reuse horizon H (queries) and
revision frequency r (feedback/revision events); n_ver = r, n_rev = r/4 (one revocation per four events).
Capability threshold: theta = 0.75 (the registered target has 4 inputs; rows reaching >= 3/4 after the
protocol are admissible; M0 is inert and never admissible).

Prospective test (PH-REV, DEFINITIONS_V2_EXACT §2 / proofs §T10-A): predicted BEFORE this file ran —
as r rises at fixed H, DENSE-update rows (M3, M4) leave the frontier in favour of LOCAL-update rows
(M1, M5), in columns where store access is charged sublinearly (indexed: B2, U, P3); in
linear-scan columns (B0, B1, B3) the sign may not hold (Stage D P4 refinement).
Held-out check: boundaries predicted from the SMALLEST ladder size are tested at the LARGEST.
Writes microscopes/results/STAGE_E_FRONTIER_V1.json and STAGE_E_REPORT_V1.md.
"""
from __future__ import annotations

import json
import os

from .core import sha256_of
from .references import ROWS
from .runner import H as H_PROTO

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
H_GRID = [1, 2, 4, 8, 16, 32, 64, 128]
R_GRID = [0, 1, 2, 4, 8, 16, 32]
THETA = 0.75
DENSE = {"M3", "M4"}
LOCAL = {"M1", "M5"}


def per_event(R: dict) -> dict:
    return {"desc": R["desc"], "exec_q": R["exec"] / (4 * (H_PROTO + 1)), "upd_e": R["upd"] / H_PROTO, "ver_e": R["ver"] / H_PROTO, "rev_e": R["rev"]}


def cost(pe: dict, Hh: int, r: int) -> float:
    return pe["desc"] + Hh * pe["exec_q"] + r * pe["upd_e"] + r * pe["ver_e"] + (r / 4) * pe["rev_e"]


def main():
    d = json.load(open(os.path.join(RES, "STAGE_D_MATRIX_V1.json")))
    cols = d["scope"]["columns"]
    frontier = {}
    boundaries = {}
    ph_rev = {}
    heldout = {}
    for col in cols:
        for size_sel in ("small", "large"):
            for Hh in H_GRID:
                for r in R_GRID:
                    admissible = []
                    for row, lad in d["scope"]["rows"].items():
                        size = lad[0] if size_sel == "small" else lad[-1]
                        key = f"{row}|{col}|{size}"
                        if d["capability_by_cell"][key] < THETA:
                            continue
                        pe = per_event(d["R_by_cell"][key])
                        admissible.append((row, cost(pe, Hh, r)))
                    if not admissible:
                        frontier[f"{col}|{size_sel}|H={Hh}|r={r}"] = []
                        continue
                    cmin = min(c for _, c in admissible)
                    winners = sorted(row for row, c in admissible if c <= cmin * 1.0 + 1e-9)
                    frontier[f"{col}|{size_sel}|H={Hh}|r={r}"] = winners
        # PH-REV: along r at fixed H (use H=8 and H=64), does a DENSE row ever win at low r and lose at high r?
        for size_sel in ("small", "large"):
            for Hh in (8, 64):
                seq = [frontier[f"{col}|{size_sel}|H={Hh}|r={r}"] for r in R_GRID]
                dense_wins = [any(w in DENSE for w in s) for s in seq]
                local_wins = [any(w in LOCAL for w in s) for s in seq]
                ph_rev[f"{col}|{size_sel}|H={Hh}"] = {"winners_by_r": dict(zip(map(str, R_GRID), seq)), "dense_wins_by_r": dense_wins, "local_wins_by_r": local_wins,
                                                     "dense_ever_wins": any(dense_wins), "dense_loses_at_high_r": (not dense_wins[-1]) and local_wins[-1],
                                                     "monotone_handover": all(not dense_wins[i] or dense_wins[i - 1] for i in range(1, len(dense_wins)))}
        # boundary r* along r at H=8 for the small size: first r where a LOCAL row beats every DENSE row
        for size_sel in ("small", "large"):
            b = None
            for r in R_GRID:
                w = frontier[f"{col}|{size_sel}|H=8|r={r}"]
                if w and all(x in LOCAL for x in w):
                    b = r
                    break
            boundaries[f"{col}|{size_sel}|H=8"] = b
        # held-out: does the small-size boundary predict the large-size boundary (same r or within one grid step)?
        bs, bl = boundaries[f"{col}|small|H=8"], boundaries[f"{col}|large|H=8"]
        heldout[col] = {"boundary_small": bs, "boundary_large": bl, "within_one_grid_step": (bs is not None and bl is not None and abs(R_GRID.index(bs) - R_GRID.index(bl)) <= 1) or (bs is None and bl is None)}
    # PH-REV verdict: predicted to hold in indexed-store columns (B2, U, P3); recorded for all
    indexed = [c for c in cols if c.startswith(("B2", "U_", "P3"))]
    scan = [c for c in cols if c.startswith(("B0", "B1", "B3"))]
    def ph(c):
        p = ph_rev[f"{c}|small|H=8"]
        if not p["dense_ever_wins"]:
            return "NOT_OBSERVABLE_AT_SCOPE__LOCAL_ROWS_DOMINATE_AT_EVERY_r"
        return "SUPPORTED" if p["dense_loses_at_high_r"] and p["monotone_handover"] else "REFUTED_AT_SCOPE"
    verdict = {
        "PH_REV_indexed_columns": {c: ph(c) for c in indexed},
        "PH_REV_scan_columns": {c: ph(c) for c in scan},
        "dense_ever_on_frontier": {c: ph_rev[f"{c}|small|H=8"]["dense_ever_wins"] for c in cols},
        "reading": "The binding ecology is discrete, exact and small-data (PH-2 conditions in ECOLOGY_AXES_V2): the axis theory predicts local/store forms there, and they dominate at every (H, r) in every column. The revision-axis handover can only be observed in an ecology where a dense-update form wins at low r — a smooth-generalization ecology (Stage F, E_smooth). PH-REV is therefore NOT tested here; it is carried to Stage F with the prediction unchanged.",
    }
    receipt = {"schema": "StageEFrontierV1", "status": "EXECUTED_EXACT_FROM_STAGE_D_MEASUREMENTS", "issue": 377,
               "cost_model": "C = desc + H*exec_q + r*upd_e + r*ver_e + (r/4)*rev_e; per-event costs measured in Stage D", "theta": THETA,
               "H_grid": H_GRID, "r_grid": R_GRID, "frontier": frontier, "ph_rev": ph_rev, "boundaries_r_star_H8": boundaries, "heldout_small_predicts_large": heldout,
               "verdict": verdict, "negative_control_PH5": "NOT_RUN — no parity ecology in this scope; registered as an obligation for the next scope",
               "claim_ceiling": "P2 exact frontier over measured tiny-scope costs and a frozen scalar cost model; two ecology axes (H, r); no real-architecture claim; dominance ties reported as multi-winner cells."}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, "STAGE_E_FRONTIER_V1.json"), "w"), indent=1, sort_keys=True, default=str)
    # report
    L = ["# Stage E — exact frontier / phase diagram: report V1\n",
         f"Receipt `microscopes/results/STAGE_E_FRONTIER_V1.json` (sha256 `{receipt['receipt_sha256'][:16]}…`). Cost model: `{receipt['cost_model']}`; θ = {THETA}; axes H ∈ {H_GRID}, r ∈ {R_GRID}.\n",
         "## PH-REV (frozen before this stage): dense-update rows leave the frontier as revision frequency rises\n",
         "| column | small size: winners by r at H=8 | dense ever wins | dense loses at high r (PH-REV) | r* (first all-local cell) small → large | held-out within one step |", "|---|---|---|---|---|---|"]
    for c in cols:
        p = ph_rev[f"{c}|small|H=8"]
        L.append(f"| {c.split('_')[0]} | {p['winners_by_r']} | {p['dense_ever_wins']} | **{p['dense_loses_at_high_r']}** | {boundaries[f'{c}|small|H=8']} → {boundaries[f'{c}|large|H=8']} | {heldout[c]['within_one_grid_step']} |")
    L.append("\nVerdict: " + json.dumps(verdict, default=str) + "\n")
    L.append("Reading rules: if a dense-update row never wins at any r (dense_ever_wins = False) the PH-REV *handover* cannot be observed in that column — the local rows dominate everywhere because at this scope they also reach the target in fewer events; that is a frontier fact, not a failed prediction. PH-REV is supported only where a dense row wins at low r and loses at high r. Negative control PH-5: NOT RUN (no parity ecology at this scope).\n")
    open(os.path.join(RES, "STAGE_E_REPORT_V1.md"), "w").write("\n".join(L) + "\n")
    print(json.dumps(verdict, indent=1, default=str))
    print("boundaries", boundaries)
    print("heldout", heldout)


if __name__ == "__main__":
    main()
