"""Stage D R3 — fresh-evidence run for RV-377-012 (growth-ORDER law replacing the P4 total-growth cut).

Fresh cells only: M1/M5/M5L at n = 32 and 64; M4 at h = 8; all nine R2 columns. The R2 receipt supplies
the reference increments (sizes 2..16 and h 1..4). Instrument: ratio of consecutive per-doubling increments
inc(n->2n)/inc(n/2->n) of charged totals. Frozen inequalities (A)-(D) are evaluated verbatim.
Writes microscopes/results/STAGE_D_MATRIX_R3.json and STAGE_D_REPORT_R3.md.
"""
from __future__ import annotations

import json
import os

from . import bases
from .core import sha256_of
from .runner import run

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(os.path.dirname(HERE), "microscopes", "results")
COLS = {**bases.ALL, **bases.INDEXED_VARIANTS}
INDEXED = ["B2_REWRITABLE_TYPED_PROGRAM_GRAPH", "U_UNIFORM_UNIVERSAL", "P3_COMPRESSED_PROGRAM_PARENT"] + list(bases.INDEXED_VARIANTS)
SCAN = ["B0_LOCAL_ADAPTIVE_TRANSDUCERS", "B1_COMPOSITIONAL_LEARNER", "B3_STOCHASTIC_GENERATIVE_KERNEL"]
B2 = "B2_REWRITABLE_TYPED_PROGRAM_GRAPH"
FRESH = {"M1": (32, 64), "M5": (32, 64), "M5L": (32, 64), "M4": (8,)}
LOG_MAX, LIN_MIN = 1.5, 1.7


def main(seed: int = 0):
    r2 = json.load(open(os.path.join(OUT_DIR, "STAGE_D_MATRIX_R2.json")))
    R2 = r2["R_by_cell"]
    cells = {}
    for row, sizes in FRESH.items():
        for col in COLS:
            for n in sizes:
                cells[(row, col, n)] = run(row, COLS[col], n, seed=seed)
    R = {}
    for row in FRESH:
        for col in COLS:
            R[(row, col)] = {}
            for k, v in R2.items():
                rr, cc, nn = k.split("|")
                if rr == row and cc == col:
                    R[(row, col)][int(nn)] = v
            for n in FRESH[row]:
                R[(row, col)][n] = cells[(row, col, n)]["R"]
    def inc(row, col, coord, a, b):
        return R[(row, col)][b][coord] - R[(row, col)][a][coord]
    def ratio(row, col, coord, a, b, c):
        i1, i2 = inc(row, col, coord, a, b), inc(row, col, coord, b, c)
        return round(i2 / i1, 3) if i1 else None
    checks = []
    def add(tag, row, col, coord, a, b, c, kind):
        q = ratio(row, col, coord, a, b, c)
        ok = (q is not None) and ((q <= LOG_MAX) if kind == "LOG" else (q >= LIN_MIN))
        checks.append({"clause": tag, "row": row, "col": col, "coord": coord, "sizes": [a, b, c], "inc_ratio": q, "law": kind, "holds": ok,
                       "inc_prev": inc(row, col, coord, a, b), "inc_next": inc(row, col, coord, b, c)})
    for col in INDEXED:
        for row in ("M1", "M5"):
            add("A", row, col, "upd", 8, 16, 32, "LOG"); add("A", row, col, "upd", 16, 32, 64, "LOG")
        add("A", "M5", col, "exec", 8, 16, 32, "LOG"); add("A", "M5", col, "exec", 16, 32, 64, "LOG")
    for col in COLS:
        add("B", "M4", col, "upd", 2, 4, 8, "LINEAR")
        add("B", "M5L", col, "exec", 8, 16, 32, "LINEAR"); add("B", "M5L", col, "exec", 16, 32, 64, "LINEAR")
    for col in SCAN:
        for row in ("M1", "M5"):
            add("B", row, col, "upd", 8, 16, 32, "LINEAR"); add("B", row, col, "upd", 16, 32, 64, "LINEAR")
    # (C) witness growth
    teq = {f"{col}@{n}": cells[("M5", col, n)]["D"] == cells[("M5L", col, n)]["D"] for col in COLS for n in (32, 64)}
    rat = {n: round(R[("M5L", B2)][n]["exec"] / R[("M5", B2)][n]["exec"], 3) for n in (16, 32, 64)}
    C = {"table_equal_all": all(teq.values()), "table_equal": teq, "exec_ratio_M5L_over_M5_B2": rat,
         "holds": all(teq.values()) and rat[32] > 3.64 and rat[64] > rat[32]}
    # (D) C2 on every fresh cell
    c2 = {f"{row}@{n}": all(cells[(row, col, n)]["D"] == cells[(row, list(COLS)[0], n)]["D"] for col in COLS) for row, sizes in FRESH.items() for n in sizes}
    D = {"holds": all(c2.values()), "by_cell": c2}
    A_ok = all(c["holds"] for c in checks if c["clause"] == "A"); B_ok = all(c["holds"] for c in checks if c["clause"] == "B")
    verdicts = {"A_log_law_indexed": A_ok, "B_linear_law": B_ok, "C_witness_growth": C["holds"], "D_C2": D["holds"]}
    receipt = {"schema": "StageDMatrixR3", "status": "EXECUTED_EXHAUSTIVE_AT_SCOPE", "issue": 377, "revival_record": "RV-377-012", "reference_receipt": "STAGE_D_MATRIX_R2.json",
               "fresh_cells": {r: list(s) for r, s in FRESH.items()}, "columns": list(COLS), "seed": seed, "thresholds": {"LOG_MAX": LOG_MAX, "LIN_MIN": LIN_MIN},
               "R_by_fresh_cell": {f"{row}|{col}|{n}": c["R"] for (row, col, n), c in cells.items()},
               "capability_by_fresh_cell": {f"{row}|{col}|{n}": c["capability"] for (row, col, n), c in cells.items()},
               "increment_checks": checks, "clause_C": C, "clause_D": D, "verdicts": verdicts, "all_hold": all(verdicts.values()),
               "n_checks": len(checks), "n_checks_failed": sum(1 for c in checks if not c["holds"]),
               "claim_ceiling": "P2 finite exact certificate; the growth-order reading of P4 is tested on sizes not present in R2; nothing was tuned after R2"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(OUT_DIR, "STAGE_D_MATRIX_R3.json"), "w"), indent=1, sort_keys=True, default=str)
    short = lambda c: c.split("_")[0]
    L = ["# Stage D R3 — fresh-evidence run for RV-377-012 (growth-order law)\n",
         f"Receipt `STAGE_D_MATRIX_R3.json` (sha256 `{receipt['receipt_sha256'][:16]}…`). Fresh cells {receipt['fresh_cells']} × 9 columns; reference increments from R2. Instrument: ratio of consecutive per-doubling increments; LOG law ⇔ ratio ≤ {LOG_MAX}, LINEAR law ⇔ ratio ≥ {LIN_MIN}.\n",
         f"**Verdicts:** {verdicts} — all hold: {receipt['all_hold']}; {receipt['n_checks_failed']} of {len(checks)} increment checks failed.\n",
         "| clause | row | col | coord | sizes | inc_prev | inc_next | ratio | law | holds |", "|---|---|---|---|---|---|---|---|---|---|"]
    for c in checks:
        L.append(f"| {c['clause']} | {c['row']} | {short(c['col'])} | {c['coord']} | {c['sizes']} | {c['inc_prev']} | {c['inc_next']} | {c['inc_ratio']} | {c['law']} | {c['holds']} |")
    L += ["", f"(C) M5~M5L Dev-table-equal at 32 and 64 in every column: {C['table_equal_all']}; exec ratio M5L/M5 in B2 at 16/32/64: {rat} — holds: {C['holds']}",
          f"(D) C2 on every fresh cell: {D['holds']}", "", receipt["claim_ceiling"], ""]
    open(os.path.join(OUT_DIR, "STAGE_D_REPORT_R3.md"), "w").write("\n".join(L))
    return receipt


if __name__ == "__main__":
    rc = main()
    print(json.dumps(rc["verdicts"], indent=1), "all:", rc["all_hold"], "failed:", rc["n_checks_failed"], "/", rc["n_checks"])
    for c in rc["increment_checks"]:
        if not c["holds"]:
            print("FAIL", c)
    print("C:", rc["clause_C"]["exec_ratio_M5L_over_M5_B2"], rc["clause_C"]["table_equal_all"])
