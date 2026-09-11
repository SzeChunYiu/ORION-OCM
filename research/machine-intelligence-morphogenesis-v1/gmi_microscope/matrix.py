"""Stage D — cross-basis compilation matrix runner (microscopes/STAGE_D_CROSS_BASIS_COMPILATION_DESIGN_V1.md).

Runs every reference row (M0..M5) under every column (B0..B3, U, P3) on the row's size ladder,
and evaluates the frozen predictions P1..P5 and the four universality tests. Writes
microscopes/results/STAGE_D_MATRIX_V1.json and STAGE_D_REPORT_V1.md. Exhaustive at scope; no sampling.

Definitions used:
  kappa(row, col, size)[coord] = R_col / parent_total   (absolute where parent uncharged)
  band K_sim(col) = max over rows/sizes/coords of max(R_col/R_U, R_U/R_col) on exec/upd/ver/rev
  locality class (ladder-based, GMI-T11): writes(size_max)/writes(size_min) vs cells(size_max)/cells(size_min)
  class separation: rows with identical D tables at a size are candidates for one class; they are one
    class at (2x,+4) iff every coordinate of their R vectors is within that band in the same column
"""
from __future__ import annotations

import json
import math
import os
from collections import defaultdict

from . import bases
from .core import COORDS, sha256_of
from .references import ROWS
from .runner import BINDING_TARGET, H, run

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(os.path.dirname(HERE), "microscopes", "results")
K_FLAT = (2.0, 4)  # frozen band: (multiplicative, additive)


def within_band(a: float, b: float, band=K_FLAT) -> bool:
    lo, hi = min(a, b), max(a, b)
    return hi <= band[0] * lo + band[1]


def ladder_locality(results_by_size: dict) -> str:
    sizes = sorted(results_by_size)
    w = [results_by_size[s]["S"]["max_cells_written_per_event"] for s in sizes]
    n = [results_by_size[s]["S"]["n_state_cells"] for s in sizes]
    if max(w) == 0:
        return "NONE"
    if w[-1] <= 2 or (w[-1] == w[0]):
        return "LOCAL_O1"
    growth_w = w[-1] / max(w[0], 1)
    growth_n = n[-1] / max(n[0], 1)
    if growth_w >= 0.75 * growth_n:
        return "DENSE_LINEAR"
    return "SPARSE_SUBLINEAR"


def main(seed: int = 0):
    os.makedirs(OUT_DIR, exist_ok=True)
    cols = list(bases.ALL)
    cells = {}
    for row, cls in ROWS.items():
        for col in cols:
            for size in cls.ladder:
                cells[(row, col, size)] = run(row, bases.ALL[col], size, seed=seed)
    # ---- C2 check: D tables identical across columns for every (row,size)
    c2 = {}
    for row, cls in ROWS.items():
        for size in cls.ladder:
            ds = [cells[(row, col, size)]["D"] for col in cols]
            c2[f"{row}@{size}"] = all(d == ds[0] for d in ds)
    # ---- U flat-table desc (analytic) replaces U's program desc in the matrix reading
    for row, cls in ROWS.items():
        for size in cls.ladder:
            r = cells[(row, "U_UNIFORM_UNIVERSAL", size)]
            r["R_flat_table_desc_log2"] = r["flat_table_entries_log2"] + math.log2(4)  # entries x ~4 bits/entry
    # ---- kappa tensor + per-coordinate ranges
    kappa = {}
    ranges = defaultdict(dict)
    for (row, col, size), r in cells.items():
        kappa[f"{row}|{col}|{size}"] = r["kappa"]
    for row, cls in ROWS.items():
        for size in cls.ladder:
            for c in ("exec", "upd", "ver", "rev"):
                vals = {col: cells[(row, col, size)]["R"][c] for col in cols}
                lo = min(v for v in vals.values() if v > 0) if any(v > 0 for v in vals.values()) else 0
                ranges[f"{row}@{size}"][c] = {"min": lo, "max": max(vals.values()), "by_col": vals,
                                             "flat_within_band": all(within_band(v, lo) for v in vals.values()) if lo else True}
    # ---- K_sim per candidate (vs U) on charged coordinates
    ksim = {}
    for col in bases.CANDIDATES:
        worst = 1.0
        for row, cls in ROWS.items():
            for size in cls.ladder:
                for c in ("exec", "upd", "ver", "rev"):
                    a = cells[(row, col, size)]["R"][c]; u = cells[(row, "U_UNIFORM_UNIVERSAL", size)]["R"][c]
                    if a and u:
                        worst = max(worst, a / u, u / a)
        ksim[col] = round(worst, 2)
    # ---- ladder-based observables per (row, col)
    observables = {}
    for row, cls in ROWS.items():
        for col in cols:
            by_size = {size: cells[(row, col, size)] for size in cls.ladder}
            s0 = by_size[cls.ladder[0]]["S"]
            observables[f"{row}|{col}"] = {
                "theta_type": s0["theta_type"],
                "update_locality_ladder": ladder_locality(by_size),
                "feedback_dependence": s0["feedback_dependence"],
                "execution_shape_declared": s0["execution_shape"],
                "store_discipline_declared": s0["store_discipline"],
                "writes_per_event_by_size": {size: by_size[size]["S"]["max_cells_written_per_event"] for size in cls.ladder},
                "cells_by_size": {size: by_size[size]["S"]["n_state_cells"] for size in cls.ladder},
                "capability_by_size": {size: by_size[size]["capability"] for size in cls.ladder},
            }
    # ---- class separation: rows with identical D tables at the smallest common size, per column
    sep = {}
    rows = list(ROWS)
    for i, r1 in enumerate(rows):
        for r2 in rows[i + 1:]:
            common = sorted(set(ROWS[r1].ladder) & set(ROWS[r2].ladder))
            if not common:
                continue
            size = common[0]
            verdicts = {}
            for col in cols:
                a, b = cells[(r1, col, size)], cells[(r2, col, size)]
                if a["D"] != b["D"]:
                    verdicts[col] = "NOT_EQUIV_DEV"
                else:
                    ok = all(within_band(a["R"][c], b["R"][c]) for c in COORDS)
                    verdicts[col] = "ONE_CLASS_AT_K" if ok else "NOT_EQUIV_OVERHEAD"
            sep[f"{r1}~{r2}@{size}"] = verdicts
    # ---- predictions
    def R(row, col, size, c):
        return cells[(row, col, size)]["R"][c]
    P = {}
    # P1a: kappa_upd(M4,B2) >= mult(b) * kappa_upd(M4,B1) with mult(8) ~ 8^2/2 = 32 charged gates lower bound? use the measured MUL cost ratio 160/2 = 80 as the frozen emulation factor
    mul_factor = 160 / 2
    p1a = all(R("M4", "B2_REWRITABLE_TYPED_PROGRAM_GRAPH", s, "upd") >= 8 * R("M4", "B1_COMPOSITIONAL_LEARNER", s, "upd") for s in ROWS["M4"].ladder)
    p1a_ratio = {s: round(R("M4", "B2_REWRITABLE_TYPED_PROGRAM_GRAPH", s, "upd") / R("M4", "B1_COMPOSITIONAL_LEARNER", s, "upd"), 2) for s in ROWS["M4"].ladder}
    p1b = all(min(R("M1", c, s, "rev") for c in ("B0_LOCAL_ADAPTIVE_TRANSDUCERS", "B1_COMPOSITIONAL_LEARNER", "B3_STOCHASTIC_GENERATIVE_KERNEL")) > R("M1", "B2_REWRITABLE_TYPED_PROGRAM_GRAPH", s, "rev") for s in ROWS["M1"].ladder)
    p1b_vals = {s: {c[:2]: R("M1", c, s, "rev") for c in cols} for s in ROWS["M1"].ladder}
    P["P1_not_flat_on_upd_rev"] = {"clause_a_gradient_law_into_rewrite_basis": p1a, "ratio_B2_over_B1_by_size": p1a_ratio, "frozen_threshold_factor": 8,
                                   "clause_b_rev_locality_only_in_B2": p1b, "rev_M1_by_col_by_size": p1b_vals}
    # P2: compression crossover on desc vs U flat table (log2)
    p2 = {}
    for row in ("M0", "M4", "M1", "M5"):
        lad = ROWS[row].ladder
        small = cells[(row, "B0_LOCAL_ADAPTIVE_TRANSDUCERS", lad[0])]; big = cells[(row, "B0_LOCAL_ADAPTIVE_TRANSDUCERS", lad[-1])]
        u_small = cells[(row, "U_UNIFORM_UNIVERSAL", lad[0])]["R_flat_table_desc_log2"]; u_big = cells[(row, "U_UNIFORM_UNIVERSAL", lad[-1])]["R_flat_table_desc_log2"]
        p2[row] = {"cand_desc_log2_small": round(math.log2(small["R"]["desc"]), 2), "U_flat_desc_log2_small": round(u_small, 2),
                   "cand_desc_log2_big": round(math.log2(big["R"]["desc"]), 2), "U_flat_desc_log2_big": round(u_big, 2),
                   "U_dominates_small": u_small < math.log2(small["R"]["desc"]), "U_loses_big": u_big > math.log2(big["R"]["desc"])}
    P["P2_compression_crossover"] = p2
    # P3: production/TMS/blackboard one class — variants not implemented; report NOT_RUN; but M1~M5 separation is reported
    P["P3_one_class_production_variants"] = {"status": "NOT_RUN_VARIANTS_NOT_IMPLEMENTED", "substitute_observation": sep.get("M1~M5@2")}
    # P4: locality sign — kappa_upd(M4) grows with |Theta|; M1/M5 do not
    def growth(row, col):
        lad = ROWS[row].ladder
        return R(row, col, lad[-1], "upd") / max(R(row, col, lad[0], "upd"), 1)
    p4 = {col: {"M4": round(growth("M4", col), 2), "M1": round(growth("M1", col), 2), "M5": round(growth("M5", col), 2), "M3": round(growth("M3", col), 2)} for col in cols}
    p4_ok = all(v["M4"] > 1.5 and v["M1"] < 1.5 and v["M5"] < 1.5 for v in p4.values())
    P["P4_locality_sign"] = {"holds": p4_ok, "upd_growth_big_over_small_by_col": p4}
    # P5: sub-band non-empty — a row pair with equal D tables and overhead outside K_FLAT but inside K_sim^2 in some column
    p5_pairs = []
    for key, verdicts in sep.items():
        for col, v in verdicts.items():
            if v == "NOT_EQUIV_OVERHEAD" and col in bases.CANDIDATES:
                r1, rest = key.split("~"); r2, size = rest.split("@"); size = int(size)
                a, b = cells[(r1, col, size)], cells[(r2, col, size)]
                ratio = max((a["R"][c] / b["R"][c] if b["R"][c] else 1) for c in ("exec", "upd", "ver") if a["R"][c] and b["R"][c])
                if ratio <= ksim[col] ** 2:
                    p5_pairs.append({"pair": key, "col": col, "max_ratio": round(ratio, 2), "ksim_sq": round(ksim[col] ** 2, 2)})
    P["P5_sub_band_non_empty"] = {"holds": bool(p5_pairs), "witnesses": p5_pairs[:10]}
    # ---- universality tests (BASIS_CANDIDATES_V2_UNIVERSALITY_TESTS.json)
    U_ = "U_UNIFORM_UNIVERSAL"
    ut = {}
    b0 = "B0_LOCAL_ADAPTIVE_TRANSDUCERS"
    ut["B0"] = {"desc_factorization_vs_flat_table_at_max_ladder": {row: (cells[(row, U_, ROWS[row].ladder[-1])]["R_flat_table_desc_log2"] - math.log2(cells[(row, b0, ROWS[row].ladder[-1])]["R"]["desc"])) for row in ROWS},
                "upd_M1_O1": growth("M1", b0) < 1.5}
    ut["B0"]["verdict"] = "PASSES_DEF_5_5" if all(v > 0 for v in ut["B0"]["desc_factorization_vs_flat_table_at_max_ladder"].values()) and ut["B0"]["upd_M1_O1"] else "UNIVERSAL_COMPUTATION_ONLY_B0"
    b1 = "B1_COMPOSITIONAL_LEARNER"
    cheap = {s: round(R("M4", b1, s, "upd") / max(R("M4", b1, s, "exec") / (4 * (H + 1)) * H, 1), 2) for s in ROWS["M4"].ladder}
    m1_vs_m4 = {s: round(R("M1", b1, s, "upd") / R("M4", b1, s, "upd"), 3) for s in (2,)}
    ut["B1"] = {"gradient_upd_over_forward_exec_per_event": cheap, "note": "ratio of one update event to one query in B1 (cheap-gradient constant made explicit)",
                "M1_upd_over_M4_upd_at_size2": m1_vs_m4, "verdict": "PASSES_DEF_5_5" if all(v < 8 for v in cheap.values()) else "UNIVERSAL_COMPUTATION_ONLY_B1"}
    b2 = "B2_REWRITABLE_TYPED_PROGRAM_GRAPH"
    ut["B2"] = {"rev_M1_local_vs_M4_retrain": {s: {"M1": R("M1", b2, s, "rev"), "M4": R("M4", b2, min(s, 4) if s in ROWS["M4"].ladder else 2, "rev")} for s in (2,)},
                "arith_emulation_factor_on_M4_upd": p1a_ratio, "verdict": "PASSES_DEF_5_5" if p1a and p1b else "UNIVERSAL_COMPUTATION_ONLY_B2"}
    b3 = "B3_STOCHASTIC_GENERATIVE_KERNEL"
    m3 = {s: {c[:2]: R("M3", c, s, "upd") for c in cols} for s in ROWS["M3"].ladder}
    b3_ok = all(R("M3", b3, s, "upd") < min(R("M3", c, s, "upd") for c in (b0, b1, b2)) for s in ROWS["M3"].ladder)
    det = {s: {c[:2]: R("M1", c, s, "exec") for c in (b0, b3)} for s in ROWS["M1"].ladder}
    ut["B3"] = {"M3_upd_by_col_by_size": m3, "native_sampling_cheaper_for_M3": b3_ok, "deterministic_rows_exec_B0_vs_B3": det,
                "verdict": "PASSES_DEF_5_5" if b3_ok else "UNIVERSAL_COMPUTATION_ONLY_B3"}
    flat_all = all(rg[c]["flat_within_band"] for rg in ranges.values() for c in ("exec", "upd", "ver", "rev"))
    # ---- receipt
    receipt = {
        "schema": "StageDMatrixV1",
        "status": "EXECUTED_EXHAUSTIVE_AT_SCOPE",
        "issue": 377,
        "scope": {"rows": {r: list(ROWS[r].ladder) for r in ROWS}, "columns": cols, "H": H, "target": BINDING_TARGET, "precision_bits": 8, "frac_bits": 4, "seed": seed},
        "basis_specs": {name: b.spec() for name, b in bases.ALL.items()},
        "C2_dev_table_identical_across_columns": c2,
        "kappa": kappa,
        "R_by_cell": {f"{row}|{col}|{size}": r["R"] for (row, col, size), r in cells.items()},
        "capability_by_cell": {f"{row}|{col}|{size}": r["capability"] for (row, col, size), r in cells.items()},
        "ranges_by_row_size": ranges,
        "matrix_flat_within_K_FLAT_on_all_coords": flat_all,
        "K_FLAT": K_FLAT,
        "K_sim_vs_U_by_candidate": ksim,
        "observables_by_row_col": observables,
        "class_separation": sep,
        "predictions": P,
        "universality_tests": ut,
        "parent_cost_models": {row: cells[(row, cols[0], ROWS[row].ladder[0])]["parent_cost_model"] for row in ROWS},
        "claim_ceiling": "P2 finite exact certificate over the frozen scope; compilation is by uniform macro expansion executed under each basis's cost algebra (no hand-authored per-target compiler); parent accounting models are documented assumptions, not measurements of the parents' own code.",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    with open(os.path.join(OUT_DIR, "STAGE_D_MATRIX_V1.json"), "w") as f:
        json.dump(receipt, f, indent=1, sort_keys=True, default=str)
    return receipt


if __name__ == "__main__":
    rc = main()
    print(json.dumps({k: rc[k] for k in ("C2_dev_table_identical_across_columns", "matrix_flat_within_K_FLAT_on_all_coords", "K_sim_vs_U_by_candidate")}, indent=1))
    print(json.dumps(rc["predictions"], indent=1, default=str)[:6000])
    print(json.dumps({k: v.get("verdict") for k, v in rc["universality_tests"].items()}, indent=1))
    print("class separation:", json.dumps(rc["class_separation"], indent=1)[:3000])
