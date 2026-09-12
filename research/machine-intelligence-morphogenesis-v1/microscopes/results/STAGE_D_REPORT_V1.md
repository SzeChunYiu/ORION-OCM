# Stage D — cross-basis compilation matrix: report V1

Receipt: `microscopes/results/STAGE_D_MATRIX_V1.json` (sha256 `050a16e8121a13a8…`). Status: `EXECUTED_EXHAUSTIVE_AT_SCOPE`. Every number below is copied from the receipt; nothing is hand-computed.

## 0. What was run

Rows M0..M5 (sizes {'M0': [2, 4, 8], 'M1': [2, 4, 8], 'M2': [2, 4, 8], 'M3': [2, 4, 8], 'M4': [1, 2, 4], 'M5': [2, 4, 8]}) × columns ['B0', 'B1', 'B2', 'B3', 'U', 'P3'] × the frozen protocol (H = 8 feedback events on target {'0': 1, '1': 0, '2': 1, '3': 1}, verification after every event, one revocation at t = 5), fixed point 8-bit / 4 fractional. Compilation is uniform macro expansion executed under each column's cost algebra: the same program runs in every column; only what is native and what each activation costs differs. The compiler-information no-go (Codex GMI-V4-02) is therefore respected by construction: there is no per-target compiler to hide a prior in.

## 1. Clause C2 (update-law preservation) — holds in every cell

Dev tables identical across all six columns for every (row, size): **yes**.

## 2. The matrix is not flat

Frozen band K_FLAT = [2.0, 4] (×, +). Flat on all coordinates: **False**. Self-simulation band vs U per candidate (max over rows/sizes/charged coordinates of R_c/R_U or R_U/R_c): B0 = 2.93, B1 = 2.93, B2 = 131.48, B3 = 2.42.

Charged resource totals over the protocol (exec | upd | ver | rev), per row at the middle ladder size:

| row@size | B0 | B1 | B2 | B3 | U | P3 |
|---|---|---|---|---|---|---|
| M0@4 | 162 \| 0 \| 176 \| 0 | 162 \| 0 \| 176 \| 0 | 162 \| 0 \| 176 \| 0 | 162 \| 0 \| 176 \| 0 | 162 \| 0 \| 176 \| 0 | 162 \| 0 \| 176 \| 0 |
| M1@4 | 171 \| 52 \| 188 \| 6 | 171 \| 52 \| 188 \| 6 | 147 \| 47 \| 160 \| 4 | 171 \| 52 \| 188 \| 6 | 147 \| 47 \| 160 \| 4 | 147 \| 47 \| 160 \| 4 |
| M2@4 | 111 \| 110 \| 160 \| 11 | 111 \| 110 \| 160 \| 11 | 1211 \| 1155 \| 1480 \| 10 | 111 \| 110 \| 160 \| 11 | 111 \| 110 \| 160 \| 10 | 111 \| 110 \| 160 \| 10 |
| M3@4 | 1476 \| 5026 \| 1344 \| 799 | 1476 \| 5026 \| 1344 \| 799 | 24864 \| 30170 \| 22000 \| 3802 | 1476 \| 1860 \| 1344 \| 293 | 1332 \| 1720 \| 1216 \| 275 | 1332 \| 1720 \| 1216 \| 275 |
| M4@2 | 756 \| 768 \| 704 \| 394 | 756 \| 376 \| 704 \| 198 | 38688 \| 40320 \| 34208 \| 19953 | 756 \| 768 \| 704 \| 394 | 540 \| 328 \| 512 \| 173 | 540 \| 328 \| 512 \| 173 |
| M5@4 | 180 \| 53 \| 198 \| 7 | 180 \| 53 \| 198 \| 7 | 163 \| 43 \| 180 \| 5 | 180 \| 53 \| 198 \| 7 | 163 \| 43 \| 180 \| 5 | 163 \| 43 \| 180 \| 5 |

## 3. Frozen predictions — verdicts

**P1a** (gradient law into the rewrite basis pays ≥ 8× vs the compositional-learner basis on `upd`): **HOLDS** — measured ratio B2/B1 by hidden size {'1': 116.31, '2': 107.23, '4': 111.55} (arithmetic emulation at 8 bits).
**P1b** (revocation of a rule is cheaper in B2 than in B0/B1/B3, strictly at every size): **FAILS AS FROZEN** — rev(M1) by column and size: {'2': {'B0': 4, 'B1': 4, 'B2': 4, 'B3': 4, 'P3': 4, 'U_': 4}, '4': {'B0': 6, 'B1': 6, 'B2': 4, 'B3': 6, 'P3': 4, 'U_': 4}, '8': {'B0': 10, 'B1': 10, 'B2': 5, 'B3': 10, 'P3': 5, 'U_': 5}}. Reading: a tie at the smallest size (all columns 4), strict in the predicted direction at sizes 4 and 8. The frozen wording demanded strictness everywhere; the direction is as predicted.
**P2** (flat-table parent U dominates on `desc` at the smallest ladder point, loses at the largest): M0: small U loses (5.0 vs 2.32 log2-bits), big U loses (7.0 vs 2.32); M1: small U loses (6.0 vs 5.55 log2-bits), big U loses (12.0 vs 6.74); M4: small U loses (44.0 vs 7.02 log2-bits), big U loses (140.0 vs 7.93); M5: small U wins (6.0 vs 6.58 log2-bits), big U loses (12.0 vs 7.29). Verdict: **PARTIAL** — the crossover exists for every row but lies *below* the registered ladder for M0/M1/M4 (the smallest size is already past it); it is visible on the ladder only for M5.
**P3** (production/TMS/blackboard one class): **NOT_RUN_VARIANTS_NOT_IMPLEMENTED**. Substitute observation with the rows that exist: M1 (rule store) ~ M5 (exemplar store) at size 2 — identical Dev tables and resource vectors within K_FLAT in every column: {'ONE_CLASS_AT_K'}. At this scope a key-matched rule store and an exemplar store are **one morphology class** (GMI-T3 membership), which is what the signature census's coarseness warning predicted for the RULE_SET/INDEXED_EXEMPLARS direction.
**P4** (charged `upd` grows with |Θ| for M4 but not for M1/M5, in every column): **FAILS AS FROZEN** — growth (largest/smallest size) by column: {'B0_LOCAL_ADAPTIVE_TRANSDUCERS': {'M1': 3.2, 'M3': 4.74, 'M4': 3.58, 'M5': 2.3}, 'B1_COMPOSITIONAL_LEARNER': {'M1': 3.2, 'M3': 4.74, 'M4': 3.42, 'M5': 2.3}, 'B2_REWRITABLE_TYPED_PROGRAM_GRAPH': {'M1': 1.38, 'M3': 4.69, 'M4': 3.28, 'M5': 1.26}, 'B3_STOCHASTIC_GENERATIVE_KERNEL': {'M1': 3.2, 'M3': 4.82, 'M4': 3.58, 'M5': 2.3}, 'P3_COMPRESSED_PROGRAM_PARENT': {'M1': 1.38, 'M3': 4.92, 'M4': 3.35, 'M5': 1.26}, 'U_UNIFORM_UNIVERSAL': {'M1': 1.38, 'M3': 4.92, 'M4': 3.35, 'M5': 1.26}}. Reading: in the indexed-store columns (B2, U, P3) the prediction holds (M4 ≈ 3.3×, M1 ≈ 1.4×, M5 ≈ 1.3×); in the columns that emulate stores by linear scan (B0, B1, B3) the charged update of M1/M5 grows ≈ 2–3× with store size although their **written cells per event stay constant** (receipt `observables_by_row_col.writes_per_event_by_size`). This is assumption (iii) of proofs §T10-A made empirical: Lemma A bounds writes, not total charged update; the revision-axis sign is fixed by locality only when store access is charged sublinearly. Registry consequence: GMI-T10-A gains the explicit hypothesis *indexed store access*; without it the boundary can reverse.
**P5** (a table-equal pair separated by resources outside K_FLAT but inside K_sim²): **FAILS** — witnesses: []. Reading: at this scope every table-equal pair (M1~M5) is within the band in every column; separation between rows comes from their Dev tables, never from resources alone. The sub-band regime for *table-equal* phenotypes is empty here; the content of the theory at this scope lives in (a) Dev-table differences and (b) the cross-basis cost asymmetries (K_sim(B2) ≫ others), not in resource-only splits.

## 4. Universality tests (Def 5.5, frozen in BASIS_CANDIDATES_V2_UNIVERSALITY_TESTS.json)

- **B0**: `UNIVERSAL_COMPUTATION_ONLY_B0` — {"desc_factorization_vs_flat_table_at_max_ladder": {"M0": 4.678071905112638, "M1": 5.258533013598853, "M2": 4.573735245297902, "M3": 28.5906090638623, "M4": 132.06926266243713, "M5": 4.714597781137751}, "upd_M1_O1": false}
- **B1**: `PASSES_DEF_5_5` — {"M1_upd_over_M4_upd_at_size2": {"2": 0.08}, "gradient_upd_over_forward_exec_per_event": {"1": 2.36, "2": 2.24, "4": 2.17}, "note": "ratio of one update event to one query in B1 (cheap-gradient constant made explicit)"}
- **B2**: `UNIVERSAL_COMPUTATION_ONLY_B2` — {"arith_emulation_factor_on_M4_upd": {"1": 116.31, "2": 107.23, "4": 111.55}, "rev_M1_local_vs_M4_retrain": {"2": {"M1": 4, "M4": 19953}}}
- **B3**: `PASSES_DEF_5_5` — {"M3_upd_by_col_by_size": {"2": {"B0": 2412, "B1": 2412, "B2": 13016, "B3": 900, "P3": 826, "U_": 826}, "4": {"B0": 5026, "B1": 5026, "B2": 30170, "B3": 1860, "P3": 1720, "U_": 1720}, "8": {"B0": 11443, "B1": 11443, "B2": 61059, "B3": 4339, "P3": 4067, "U_": 4067}}, "deterministic_rows_exec_B0_vs_B3": {"2": {"B0": 97, "B3": 97}, "4": {"B0": 171, "B3": 171}, "8": {"B0": 319, "B3": 319}}, "native_sampling_cheaper_for_M3": true}

Reading: B1 and B3 pass their sub-band tests (native adjoint makes the gradient law cheap relative to a query; native sampling makes conditioning cheaper than in any other column). B0's test fails on the M1 `upd` O(1) clause for the same linear-scan reason as P4, not on factorization (its desc beats the flat table at every ladder top). B2's test fails as frozen only because P1b demanded strict inequality at the smallest size, where all columns tie; its arithmetic-emulation clause holds by two orders of magnitude. These are the verdicts of the *frozen* tests; the refined readings are recorded here and not substituted for them.

## 5. Class structure at scope (GMI-T3)

| pair@size | B0 | B1 | B2 | B3 | U | P3 |
|---|---|---|---|---|---|---|
| M0~M1@2 | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV |
| M0~M2@2 | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV |
| M0~M3@2 | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV |
| M0~M4@2 | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV |
| M0~M5@2 | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV |
| M1~M2@2 | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV |
| M1~M3@2 | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV |
| M1~M4@2 | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV |
| M1~M5@2 | ONE CLASS AT K | ONE CLASS AT K | ONE CLASS AT K | ONE CLASS AT K | ONE CLASS AT K | ONE CLASS AT K |
| M2~M3@2 | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV |
| M2~M4@2 | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV |
| M2~M5@2 | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV |
| M3~M4@2 | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV |
| M3~M5@2 | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV |
| M4~M5@2 | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV | NOT EQUIV DEV |

Six rows → five classes at this scope (M1 ≡ M5). Every other pair differs in its Dev table (different learning law), so the classes are separated by development, not by resources.

## 6. Observables (post-hoc, ladder-based)

| row|col | theta | locality (ladder) | fbdep | writes/event by size | capability by size |
|---|---|---|---|---|---|
| M0|B0 | DISCRETE_FINITE | NONE | [] | {'2': 0, '4': 0, '8': 0} | {'2': 0.25, '4': 0.5, '8': 0.5} |
| M0|B2 | DISCRETE_FINITE | NONE | [] | {'2': 0, '4': 0, '8': 0} | {'2': 0.25, '4': 0.5, '8': 0.5} |
| M1|B0 | DISCRETE_FINITE | LOCAL_O1 | ['exact_counterexample'] | {'2': 1, '4': 1, '8': 1} | {'2': 1.0, '4': 1.0, '8': 1.0} |
| M1|B2 | DISCRETE_FINITE | LOCAL_O1 | ['exact_counterexample'] | {'2': 1, '4': 1, '8': 1} | {'2': 1.0, '4': 1.0, '8': 1.0} |
| M2|B0 | DISCRETE_FINITE | LOCAL_O1 | ['exact_counterexample'] | {'2': 3, '4': 3, '8': 3} | {'2': 1.0, '4': 1.0, '8': 1.0} |
| M2|B2 | DISCRETE_FINITE | LOCAL_O1 | ['exact_counterexample'] | {'2': 3, '4': 3, '8': 3} | {'2': 1.0, '4': 1.0, '8': 1.0} |
| M3|B0 | MIXED | DENSE_LINEAR | ['likelihood_score'] | {'2': 4, '4': 6, '8': 10} | {'2': 0.25, '4': 0.75, '8': 0.75} |
| M3|B2 | MIXED | DENSE_LINEAR | ['likelihood_score'] | {'2': 4, '4': 6, '8': 10} | {'2': 0.25, '4': 0.75, '8': 0.75} |
| M4|B0 | BOUNDED_NUMERIC | DENSE_LINEAR | ['scalar_loss'] | {'1': 5, '2': 5, '4': 9} | {'1': 0.75, '2': 0.75, '4': 0.75} |
| M4|B2 | BOUNDED_NUMERIC | DENSE_LINEAR | ['scalar_loss'] | {'1': 5, '2': 5, '4': 9} | {'1': 0.75, '2': 0.75, '4': 0.75} |
| M5|B0 | DISCRETE_FINITE | LOCAL_O1 | ['exact_counterexample'] | {'2': 2, '4': 2, '8': 2} | {'2': 1.0, '4': 1.0, '8': 1.0} |
| M5|B2 | DISCRETE_FINITE | LOCAL_O1 | ['exact_counterexample'] | {'2': 2, '4': 2, '8': 2} | {'2': 1.0, '4': 1.0, '8': 1.0} |

Note: the particle learner (M3) measures as DENSE update locality (it reweights every particle per event), which corrects the registered M3 signature's `SPARSE_SUBLINEAR` for particle-style conditioning; conjugate-statistic conditioning would measure LOCAL. The signature file is amended by declared amendment, not silently.

## 7. Claim ceiling

P2 finite exact certificate over the frozen scope; compilation is by uniform macro expansion executed under each basis's cost algebra (no hand-authored per-target compiler); parent accounting models are documented assumptions, not measurements of the parents' own code.

Negative/partial predictions enter #373 revival logic as `REVIVAL_LEDGER.jsonl` records (P1b, P2, P4, P5). No prediction was altered after the run; refined readings are additions.

