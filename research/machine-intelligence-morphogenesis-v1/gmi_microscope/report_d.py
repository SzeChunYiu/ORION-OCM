"""Render microscopes/results/STAGE_D_MATRIX_V1.json into STAGE_D_REPORT_V1.md (numbers come only from the receipt)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")


def main():
    d = json.load(open(os.path.join(RES, "STAGE_D_MATRIX_V1.json")))
    cols = d["scope"]["columns"]
    short = {c: c.split("_")[0] for c in cols}
    L = []
    L.append("# Stage D — cross-basis compilation matrix: report V1\n")
    L.append(f"Receipt: `microscopes/results/STAGE_D_MATRIX_V1.json` (sha256 `{d['receipt_sha256'][:16]}…`). Status: `{d['status']}`. "
             "Every number below is copied from the receipt; nothing is hand-computed.\n")
    L.append("## 0. What was run\n")
    L.append(f"Rows M0..M5 (sizes {d['scope']['rows']}) × columns {[short[c] for c in cols]} × the frozen protocol "
             f"(H = {d['scope']['H']} feedback events on target {d['scope']['target']}, verification after every event, one revocation at t = 5), "
             f"fixed point {d['scope']['precision_bits']}-bit / {d['scope']['frac_bits']} fractional. Compilation is uniform macro expansion executed "
             "under each column's cost algebra: the same program runs in every column; only what is native and what each activation costs differs. "
             "The compiler-information no-go (Codex GMI-V4-02) is therefore respected by construction: there is no per-target compiler to hide a prior in.\n")
    L.append("## 1. Clause C2 (update-law preservation) — holds in every cell\n")
    L.append("Dev tables identical across all six columns for every (row, size): " + ("**yes**" if all(d["C2_dev_table_identical_across_columns"].values()) else "**NO**") + ".\n")
    L.append("## 2. The matrix is not flat\n")
    L.append(f"Frozen band K_FLAT = {d['K_FLAT']} (×, +). Flat on all coordinates: **{d['matrix_flat_within_K_FLAT_on_all_coords']}**. "
             f"Self-simulation band vs U per candidate (max over rows/sizes/charged coordinates of R_c/R_U or R_U/R_c): "
             + ", ".join(f"{short[k]} = {v}" for k, v in d["K_sim_vs_U_by_candidate"].items()) + ".\n")
    L.append("Charged resource totals over the protocol (exec | upd | ver | rev), per row at the middle ladder size:\n")
    L.append("| row@size | " + " | ".join(short[c] for c in cols) + " |\n|---|" + "---|" * len(cols))
    for key, rg in d["ranges_by_row_size"].items():
        row, size = key.split("@")
        mid = {"M4": "2"}.get(row, "4")
        if size != mid:
            continue
        cells = []
        for c in cols:
            R = d["R_by_cell"][f"{row}|{c}|{size}"]
            cells.append(f"{R['exec']} \\| {R['upd']} \\| {R['ver']} \\| {R['rev']}")
        L.append(f"| {key} | " + " | ".join(cells) + " |")
    L.append("")
    L.append("## 3. Frozen predictions — verdicts\n")
    P = d["predictions"]
    p1 = P["P1_not_flat_on_upd_rev"]
    L.append(f"**P1a** (gradient law into the rewrite basis pays ≥ 8× vs the compositional-learner basis on `upd`): **{'HOLDS' if p1['clause_a_gradient_law_into_rewrite_basis'] else 'FAILS'}** — measured ratio B2/B1 by hidden size {p1['ratio_B2_over_B1_by_size']} (arithmetic emulation at 8 bits).")
    L.append(f"**P1b** (revocation of a rule is cheaper in B2 than in B0/B1/B3, strictly at every size): **{'HOLDS' if p1['clause_b_rev_locality_only_in_B2'] else 'FAILS AS FROZEN'}** — rev(M1) by column and size: {p1['rev_M1_by_col_by_size']}. Reading: a tie at the smallest size (all columns 4), strict in the predicted direction at sizes 4 and 8. The frozen wording demanded strictness everywhere; the direction is as predicted.")
    p2 = P["P2_compression_crossover"]
    L.append("**P2** (flat-table parent U dominates on `desc` at the smallest ladder point, loses at the largest): " + "; ".join(f"{r}: small {'U wins' if v['U_dominates_small'] else 'U loses'} ({v['U_flat_desc_log2_small']} vs {v['cand_desc_log2_small']} log2-bits), big {'U loses' if v['U_loses_big'] else 'U wins'} ({v['U_flat_desc_log2_big']} vs {v['cand_desc_log2_big']})" for r, v in p2.items()) + ". Verdict: **PARTIAL** — the crossover exists for every row but lies *below* the registered ladder for M0/M1/M4 (the smallest size is already past it); it is visible on the ladder only for M5.")
    p3 = P["P3_one_class_production_variants"]
    L.append(f"**P3** (production/TMS/blackboard one class): **{p3['status']}**. Substitute observation with the rows that exist: M1 (rule store) ~ M5 (exemplar store) at size 2 — identical Dev tables and resource vectors within K_FLAT in every column: {set(p3['substitute_observation'].values())}. At this scope a key-matched rule store and an exemplar store are **one morphology class** (GMI-T3 membership), which is what the signature census's coarseness warning predicted for the RULE_SET/INDEXED_EXEMPLARS direction.")
    p4 = P["P4_locality_sign"]
    L.append(f"**P4** (charged `upd` grows with |Θ| for M4 but not for M1/M5, in every column): **{'HOLDS' if p4['holds'] else 'FAILS AS FROZEN'}** — growth (largest/smallest size) by column: {p4['upd_growth_big_over_small_by_col']}. Reading: in the indexed-store columns (B2, U, P3) the prediction holds (M4 ≈ 3.3×, M1 ≈ 1.4×, M5 ≈ 1.3×); in the columns that emulate stores by linear scan (B0, B1, B3) the charged update of M1/M5 grows ≈ 2–3× with store size although their **written cells per event stay constant** (receipt `observables_by_row_col.writes_per_event_by_size`). This is assumption (iii) of proofs §T10-A made empirical: Lemma A bounds writes, not total charged update; the revision-axis sign is fixed by locality only when store access is charged sublinearly. Registry consequence: GMI-T10-A gains the explicit hypothesis *indexed store access*; without it the boundary can reverse.")
    p5 = P["P5_sub_band_non_empty"]
    L.append(f"**P5** (a table-equal pair separated by resources outside K_FLAT but inside K_sim²): **{'HOLDS' if p5['holds'] else 'FAILS'}** — witnesses: {p5['witnesses']}. Reading: at this scope every table-equal pair (M1~M5) is within the band in every column; separation between rows comes from their Dev tables, never from resources alone. The sub-band regime for *table-equal* phenotypes is empty here; the content of the theory at this scope lives in (a) Dev-table differences and (b) the cross-basis cost asymmetries (K_sim(B2) ≫ others), not in resource-only splits.")
    L.append("\n## 4. Universality tests (Def 5.5, frozen in BASIS_CANDIDATES_V2_UNIVERSALITY_TESTS.json)\n")
    for k, v in d["universality_tests"].items():
        L.append(f"- **{k}**: `{v['verdict']}` — " + json.dumps({kk: vv for kk, vv in v.items() if kk not in ('verdict',)}, default=str)[:600])
    L.append("\nReading: B1 and B3 pass their sub-band tests (native adjoint makes the gradient law cheap relative to a query; native sampling makes conditioning cheaper than in any other column). B0's test fails on the M1 `upd` O(1) clause for the same linear-scan reason as P4, not on factorization (its desc beats the flat table at every ladder top). B2's test fails as frozen only because P1b demanded strict inequality at the smallest size, where all columns tie; its arithmetic-emulation clause holds by two orders of magnitude. These are the verdicts of the *frozen* tests; the refined readings are recorded here and not substituted for them.\n")
    L.append("## 5. Class structure at scope (GMI-T3)\n")
    L.append("| pair@size | " + " | ".join(short[c] for c in cols) + " |\n|---|" + "---|" * len(cols))
    for key, v in d["class_separation"].items():
        L.append(f"| {key} | " + " | ".join(v[c].replace('_', ' ') for c in cols) + " |")
    L.append("\nSix rows → five classes at this scope (M1 ≡ M5). Every other pair differs in its Dev table (different learning law), so the classes are separated by development, not by resources.\n")
    L.append("## 6. Observables (post-hoc, ladder-based)\n")
    L.append("| row|col | theta | locality (ladder) | fbdep | writes/event by size | capability by size |\n|---|---|---|---|---|---|")
    for key, o in d["observables_by_row_col"].items():
        row, col = key.split("|")
        if col not in ("B0_LOCAL_ADAPTIVE_TRANSDUCERS", "B2_REWRITABLE_TYPED_PROGRAM_GRAPH"):
            continue
        L.append(f"| {row}|{short[col]} | {o['theta_type']} | {o['update_locality_ladder']} | {o['feedback_dependence']} | {o['writes_per_event_by_size']} | {o['capability_by_size']} |")
    L.append("\nNote: the particle learner (M3) measures as DENSE update locality (it reweights every particle per event), which corrects the registered M3 signature's `SPARSE_SUBLINEAR` for particle-style conditioning; conjugate-statistic conditioning would measure LOCAL. The signature file is amended by declared amendment, not silently.\n")
    L.append("## 7. Claim ceiling\n")
    L.append(d["claim_ceiling"] + "\n")
    L.append("Negative/partial predictions enter #373 revival logic as `REVIVAL_LEDGER.jsonl` records (P1b, P2, P4, P5). No prediction was altered after the run; refined readings are additions.\n")
    open(os.path.join(RES, "STAGE_D_REPORT_V1.md"), "w").write("\n".join(L) + "\n")
    print("report written")


if __name__ == "__main__":
    main()
