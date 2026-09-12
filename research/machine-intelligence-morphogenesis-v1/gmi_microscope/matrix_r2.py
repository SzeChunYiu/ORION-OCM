"""Stage D R2 — the fresh-evidence re-run frozen in REVIVAL_LEDGER.jsonl RV-377-010 (parents 001–004).

Declared amendments (frozen before this run; see RV-377-010 minimal_proposed_change):
  * ladder {1,2,4,8,16} for M0/M1, {2,4,8,16} for M5/M5L (references.R2_LADDER);
  * indexed-emulation columns B0i/B1i/B3i (bases.INDEXED_VARIANTS): the emulated store carries a charged
    binary index — 1+ceil(log2(n+1)) compares per lookup/match/delete, index maintenance on insert;
  * new row M5L (exemplar list with an explicit linear-scan lookup program): the sub-band witness candidate.
Four frozen clauses, evaluated exactly as written in RV-377-010:
  (001) rev(M1,B2) <= 0.5 x rev(M1,B0) at n=16
  (002) at n=1, U's flat table dominates the candidate's factorized desc for M0 and M1
  (003) in indexed-store columns (B2,U,P3,B0i,B1i,B3i): M1/M5 charged upd growth (16/2) < 1.5 and M4 growth (4/1) > 1.5
  (004) M5 ~ M5L table-equal; separated on exec outside K_FLAT but inside K_sim^2 at n=16 in column B2; NOT separated at n <= 8
Writes microscopes/results/STAGE_D_MATRIX_R2.json and STAGE_D_REPORT_R2.md.
"""
from __future__ import annotations

import json
import math
import os

from . import bases
from .core import COORDS, sha256_of
from .matrix import K_FLAT, ladder_locality, within_band
from .references import R2_LADDER, ROWS
from .runner import BINDING_TARGET, H, run

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(os.path.dirname(HERE), "microscopes", "results")
COLS = {**bases.ALL, **bases.INDEXED_VARIANTS}
INDEXED_COLS = ["B2_REWRITABLE_TYPED_PROGRAM_GRAPH", "U_UNIFORM_UNIVERSAL", "P3_COMPRESSED_PROGRAM_PARENT"] + list(bases.INDEXED_VARIANTS)
B0, B1, B2, B3, U_ = ("B0_LOCAL_ADAPTIVE_TRANSDUCERS", "B1_COMPOSITIONAL_LEARNER", "B2_REWRITABLE_TYPED_PROGRAM_GRAPH", "B3_STOCHASTIC_GENERATIVE_KERNEL", "U_UNIFORM_UNIVERSAL")


def main(seed: int = 0):
    os.makedirs(OUT_DIR, exist_ok=True)
    cols = list(COLS)
    cells = {}
    for row, lad in R2_LADDER.items():
        for col in cols:
            for size in lad:
                cells[(row, col, size)] = run(row, COLS[col], size, seed=seed)
    R = lambda row, col, size, c: cells[(row, col, size)]["R"][c]
    # C2: Dev tables identical across all nine columns
    c2 = {f"{row}@{size}": all(cells[(row, col, size)]["D"] == cells[(row, cols[0], size)]["D"] for col in cols) for row, lad in R2_LADDER.items() for size in lad}
    for row, lad in R2_LADDER.items():
        for size in lad:
            r = cells[(row, U_, size)]
            r["R_flat_table_desc_log2"] = r["flat_table_entries_log2"] + math.log2(4)
    # K_sim per candidate column (vs U), R2 scope
    ksim = {}
    for col in list(bases.CANDIDATES) + list(bases.INDEXED_VARIANTS):
        worst = 1.0
        for row, lad in R2_LADDER.items():
            for size in lad:
                for c in ("exec", "upd", "ver", "rev"):
                    a, u = R(row, col, size, c), R(row, U_, size, c)
                    if a and u:
                        worst = max(worst, a / u, u / a)
        ksim[col] = round(worst, 2)
    # ---- clause 001
    rev16 = {col: R("M1", col, 16, "rev") for col in cols}
    c001 = {"rev_M1_at_16_by_col": rev16, "ratio_B2_over_B0": round(rev16[B2] / rev16[B0], 4) if rev16[B0] else None,
            "holds": rev16[B2] <= 0.5 * rev16[B0]}
    # ---- clause 002
    c002 = {}
    for row in ("M0", "M1"):
        cand = math.log2(R(row, B0, 1, "desc")); flat = cells[(row, U_, 1)]["R_flat_table_desc_log2"]
        c002[row] = {"cand_desc_log2_n1": round(cand, 3), "U_flat_desc_log2_n1": round(flat, 3), "U_dominates": flat < cand}
    c002["holds"] = all(c002[r]["U_dominates"] for r in ("M0", "M1"))
    # ---- clause 003
    def growth(row, col, big, small):
        return round(R(row, col, big, "upd") / max(R(row, col, small, "upd"), 1), 3)
    c003 = {"by_col": {}, "holds": True}
    for col in INDEXED_COLS:
        g = {"M1_16_over_2": growth("M1", col, 16, 2), "M5_16_over_2": growth("M5", col, 16, 2), "M4_4_over_1": growth("M4", col, 4, 1)}
        g["clause"] = g["M1_16_over_2"] < 1.5 and g["M5_16_over_2"] < 1.5 and g["M4_4_over_1"] > 1.5
        c003["by_col"][col] = g
        c003["holds"] = c003["holds"] and g["clause"]
    # non-indexed columns reported for contrast (not part of the clause)
    c003["contrast_linear_scan_cols"] = {col: {"M1_16_over_2": growth("M1", col, 16, 2), "M5_16_over_2": growth("M5", col, 16, 2)} for col in (B0, B1, B3)}
    # written cells per event (Lemma A observable) for M1/M5 on the ladder, every column
    c003["max_cells_written_per_event"] = {f"{row}|{col}": {s: cells[(row, col, s)]["S"]["max_cells_written_per_event"] for s in R2_LADDER[row]} for row in ("M1", "M5", "M4") for col in cols}
    # ---- clause 004
    c004 = {"by_size": {}, "holds": None}
    for size in R2_LADDER["M5"]:
        a, b = cells[("M5", B2, size)], cells[("M5L", B2, size)]
        table_equal = a["D"] == b["D"]
        ex_a, ex_b = a["R"]["exec"], b["R"]["exec"]
        sep_exec = not within_band(ex_a, ex_b)
        ratio = max(ex_a, ex_b) / max(min(ex_a, ex_b), 1)
        c004["by_size"][size] = {"table_equal": table_equal, "exec_M5": ex_a, "exec_M5L": ex_b, "exec_ratio": round(ratio, 3),
                                 "separated_outside_K_FLAT": sep_exec, "inside_K_sim_sq": ratio <= ksim[B2] ** 2,
                                 "all_coords_within_K_FLAT": all(within_band(a["R"][c], b["R"][c]) for c in COORDS)}
    c004["holds"] = (c004["by_size"][16]["table_equal"] and c004["by_size"][16]["separated_outside_K_FLAT"] and c004["by_size"][16]["inside_K_sim_sq"]
                     and all(not c004["by_size"][s]["separated_outside_K_FLAT"] for s in (2, 4, 8)))
    # the same pair in every column, for the record
    c004["separation_on_exec_by_col_at_16"] = {col: {"ratio": round(max(R("M5", col, 16, "exec"), R("M5L", col, 16, "exec")) / max(min(R("M5", col, 16, "exec"), R("M5L", col, 16, "exec")), 1), 3),
                                                    "outside_K_FLAT": not within_band(R("M5", col, 16, "exec"), R("M5L", col, 16, "exec"))} for col in cols}
    # ---- RV-377-004 second reading (M1 vs M5 on desc at 16): reported, not a clause of 010
    m1m5 = {col: {"desc_M1": R("M1", col, 16, "desc"), "desc_M5": R("M5", col, 16, "desc"), "table_equal": cells[("M1", col, 16)]["D"] == cells[("M5", col, 16)]["D"],
                  "within_K_FLAT_desc": within_band(R("M1", col, 16, "desc"), R("M5", col, 16, "desc"))} for col in cols}
    # ---- ladder locality observables (GMI-T11) for the R2 ladder
    observables = {f"{row}|{col}": {"update_locality_ladder": ladder_locality({s: cells[(row, col, s)] for s in R2_LADDER[row]}),
                                    "writes_by_size": {s: cells[(row, col, s)]["S"]["max_cells_written_per_event"] for s in R2_LADDER[row]},
                                    "cells_by_size": {s: cells[(row, col, s)]["S"]["n_state_cells"] for s in R2_LADDER[row]}} for row in R2_LADDER for col in cols}
    verdicts = {"001": c001["holds"], "002": c002["holds"], "003": c003["holds"], "004": c004["holds"]}
    receipt = {"schema": "StageDMatrixR2", "status": "EXECUTED_EXHAUSTIVE_AT_SCOPE", "issue": 377, "revival_record": "RV-377-010",
               "scope": {"rows": {r: list(l) for r, l in R2_LADDER.items()}, "columns": cols, "H": H, "target": BINDING_TARGET, "seed": seed, "K_FLAT": K_FLAT},
               "basis_specs": {name: b.spec() | {"indexed_emulation": getattr(b, "indexed_emulation", False)} for name, b in COLS.items()},
               "C2_dev_table_identical_across_columns": c2, "K_sim_vs_U_by_candidate_R2": ksim,
               "R_by_cell": {f"{row}|{col}|{size}": r["R"] for (row, col, size), r in cells.items()},
               "capability_by_cell": {f"{row}|{col}|{size}": r["capability"] for (row, col, size), r in cells.items()},
               "clause_001_rev_M1_B2_vs_B0_at_16": c001, "clause_002_U_dominates_desc_at_n1": c002, "clause_003_P4_charged_in_indexed_cols": c003,
               "clause_004_M5_vs_M5L_sub_band_witness": c004, "RV_004_M1_vs_M5_desc_at_16": m1m5, "observables_by_row_col": observables,
               "verdicts": verdicts, "all_clauses_hold": all(verdicts.values()),
               "claim_ceiling": "P2 finite exact certificate over the R2 scope; the indexed-emulation columns are a DECLARED basis amendment (RV-377-003), not the frozen B0/B1/B3; V1 receipt untouched."}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    with open(os.path.join(OUT_DIR, "STAGE_D_MATRIX_R2.json"), "w") as f:
        json.dump(receipt, f, indent=1, sort_keys=True, default=str)
    short = lambda c: c.split("_")[0]
    L = ["# Stage D R2 — fresh-evidence re-run for RV-377-010 (parents RV-377-001/002/003/004)\n",
         f"Receipt `STAGE_D_MATRIX_R2.json` (sha256 `{receipt['receipt_sha256'][:16]}…`). Rows/ladders {receipt['scope']['rows']}; nine columns (six frozen + declared indexed-emulation variants B0i/B1i/B3i); C2 holds on every cell: {all(c2.values())}.\n",
         f"K_sim vs U on the R2 scope: {{ {', '.join(f'{short(k)}: {v}' for k, v in ksim.items())} }}\n",
         "## Clause verdicts\n", "| clause | frozen statement | outcome | holds |", "|---|---|---|---|",
         f"| 001 | rev(M1,B2) <= 0.5 x rev(M1,B0) at n=16 | rev at 16: {', '.join(f'{short(k)}={v}' for k, v in rev16.items())}; B2/B0 = {c001['ratio_B2_over_B0']} | {c001['holds']} |",
         f"| 002 | at n=1 U's flat table dominates desc for M0 and M1 | M0: cand {c002['M0']['cand_desc_log2_n1']} vs flat {c002['M0']['U_flat_desc_log2_n1']} (log2 bits); M1: cand {c002['M1']['cand_desc_log2_n1']} vs flat {c002['M1']['U_flat_desc_log2_n1']} | {c002['holds']} |",
         f"| 003 | indexed-store columns: M1/M5 upd growth (16/2) < 1.5, M4 (4/1) > 1.5 | " + "; ".join(f"{short(k)}: M1 {v['M1_16_over_2']}, M5 {v['M5_16_over_2']}, M4 {v['M4_4_over_1']}" for k, v in c003['by_col'].items()) + f" | {c003['holds']} |",
         f"| 004 | M5~M5L table-equal, exec-separated outside K_FLAT (inside K_sim^2) at n=16 in B2, not at n<=8 | " + "; ".join(f"n={s}: ratio {v['exec_ratio']}, sep {v['separated_outside_K_FLAT']}, table_eq {v['table_equal']}" for s, v in c004['by_size'].items()) + f" | {c004['holds']} |",
         "", f"Linear-scan columns for contrast (not a clause): " + "; ".join(f"{short(k)}: M1 {v['M1_16_over_2']}, M5 {v['M5_16_over_2']}" for k, v in c003['contrast_linear_scan_cols'].items()),
         "", "RV-377-004 second reading (M1 vs M5 desc at n=16, per column): " + "; ".join(f"{short(k)}: M1 {v['desc_M1']} / M5 {v['desc_M5']} (table_eq {v['table_equal']}, within K_FLAT {v['within_K_FLAT_desc']})" for k, v in m1m5.items()),
         "", f"**All four clauses hold: {receipt['all_clauses_hold']}.** " + receipt["claim_ceiling"], ""]
    open(os.path.join(OUT_DIR, "STAGE_D_REPORT_R2.md"), "w").write("\n".join(L))
    return receipt


if __name__ == "__main__":
    rc = main()
    print(json.dumps({k: rc[k] for k in ("verdicts", "all_clauses_hold", "K_sim_vs_U_by_candidate_R2")}, indent=1))
    print(json.dumps(rc["clause_001_rev_M1_B2_vs_B0_at_16"], indent=1)[:800])
    print(json.dumps(rc["clause_002_U_dominates_desc_at_n1"], indent=1))
    print(json.dumps({k: v for k, v in rc["clause_003_P4_charged_in_indexed_cols"].items() if k in ("by_col", "contrast_linear_scan_cols")}, indent=1))
    print(json.dumps(rc["clause_004_M5_vs_M5L_sub_band_witness"]["by_size"], indent=1))
    print(json.dumps(rc["RV_004_M1_vs_M5_desc_at_16"], indent=1)[:1500])
    print("C2 all:", all(rc["C2_dev_table_identical_across_columns"].values()))
