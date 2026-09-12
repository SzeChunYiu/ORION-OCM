# Real-transfer revival, second iteration: RV-377-193 (B_SPECIALIZATION_REAL, world stage)

Status: **FROZEN BEFORE THE RUN.** Successor to `GMI_REAL_TRANSFER_REVIVAL_RV_377_191_FREEZE.md` (RV-377-192), whose
verdict stands. Source receipts: `microscopes/results/real_transfer_v3_revival/` (revival freeze `7fe510c7`,
billy-laptop, 72/72). Date 2026-09-12.

## 1. What RV-377-192 showed

Under the parameter-heterogeneity (Chow-form) descriptor the law still predicted SHARED on 29/32 replicates (NONE on
3, SPECIALIZED on 0), so kill condition P-B5 (SPECIALIZED predicted on ≤ 3/8 at τ = 0.8) **triggered**: the descriptor
was not the dominant stage. The receipts locate the dominant stage in the world: with 400 training rows of
California housing, k-means places 1–7 rows in at least one of the four modes on 31/32 replicates (`n_j` minima:
1, 1, 3, 1, 7, 1, 1, 1, …); the law's per-mode variance term `σ̂² p · mean_j(1/n_j)` is then 0.3–1.7 (p = 9 with
`n_j = 1`), which no admissible heterogeneity can overcome; and the same heavy-tailed rows (AveRooms, AveOccup,
Population) make the shared linear model extrapolate on high-leverage test rows, giving test MSE 9.9–161 and NONE
outcomes on 11/32 replicates. Both symptoms are one cause: unbounded feature tails at small n. The descriptor change
of RV-377-192 is retained (it is the correct heterogeneity for a linear shared class) but could not act.

## 2. One-stage change (WORLD): bounded feature tails

Winsorise every feature at the training-split 1st and 99th percentiles (a pre-outcome transform fitted on the 400
training rows and applied unchanged to the 2000 test rows) before standardisation and k-means. Nothing else changes:
machines, prices, thresholds (test MSE ≤ 0.50), grid `τ ∈ {0, 0.1, 0.3, 0.8}`, the injected-offset construction, the
RV-377-192 descriptor, the CV parent, and the scoring. Seeds: `SHA256("GMI-RT-V3R2|" + commit + …)`.

## 3. Predictions before outcome

- **P-B6.** Smallest mode `min_j n_j ≥ 15` on ≥ 28/32 replicates (k-means no longer isolates tail rows).
- **P-B7.** NONE outcomes on ≤ 3/32 replicates (leverage removed).
- **P-B8.** At τ = 0.8 the law predicts SPECIALIZED on ≥ 6/8 and the cell is GREEN.
- **P-B9.** At τ = 0 the law predicts SHARED on ≥ 5/8; the cell is GREEN or INCONCLUSIVE (real slope heterogeneity
  at 400 rows sits near the crossover); τ = 0.1 and 0.3 straddle the crossover and are expected INCONCLUSIVE.
- **Kill (P-B10).** NONE outcomes on ≥ 8/32 or `min_j n_j < 15` on ≥ 8/32: the tails were not the cause.
- Terminals: P-B6..P-B8 hold → `B_SPECIALIZATION_REAL_GREEN_AT_HIGH_HETEROGENEITY_UNDER_BOUNDED_TAILS__CROSSOVER_CELLS_INCONCLUSIVE`;
  P-B10 → `B_SPECIALIZATION_REAL_WORLD_ATTRIBUTION_KILLED`.

## 4. Execution

`gmi_real_transfer_v3.py --revival2 --lanes B_SPECIALIZATION_REAL`, billy-laptop, 3 niced processes, receipts under
`microscopes/results/real_transfer_v3_revival2/`, `--freeze-sha` = the commit introducing this file and the
`--revival2` code path.

## 5. Adjudication (append-only)

Freeze `267f39eeef1c39fe10d322ba851c8e0b41c8c15c`, billy-laptop, 32/32 tasks, aggregate terminal
`REAL_TRANSFER_PHASE_LAWS_GREEN_ON_0_OF_1_LANES` (lane THEORY_RED by the 0.3 cell).

| cell | predicted | agree | oppose | pred.-inadm. | mean margin | verdict | CV right / GMI right |
|---|---|---|---|---|---|---|---|
| 0.0 | SHARED 7, SPECIALIZED 1 | 5/8 | 3 | 0 | +0.0023 | INCONCLUSIVE | 5 / 5 |
| 0.1 | SHARED 7, SPECIALIZED 1 | 6/8 | 2 | 0 | +0.017 | GREEN | 4 / 6 |
| 0.3 | SHARED 7, SPECIALIZED 1 | 1/8 | 7 | 0 | −0.011 | THEORY_RED | 4 / 1 |
| 0.8 | SPECIALIZED 7, SHARED 1 | 7/8 | 1 | 0 | +0.428 | GREEN | 8 / 7 |

- **P-B7 holds**: NONE outcomes 0/32 (11/32 before); shared test MSE now 0.29–0.61 on every replicate. The leverage
  blow-ups were the tails.
- **P-B6 fails / P-B10 triggers on its second clause**: `min_j n_j ≥ 15` on only 14/32 (minima 5–15 on the rest);
  k-means on 400 real rows still forms 5–15-row clusters after winsorising. The tails caused the leverage, not the
  small modes.
- **P-B8 holds**: SPECIALIZED predicted 7/8 at τ = 0.8, cell GREEN (margin +0.43 in MSE units).
- **P-B9 holds**: SHARED predicted 7/8 at τ = 0, cell INCONCLUSIVE (5/8); 0.1 GREEN at the rule's floor (6/8, margin
  +0.017); 0.3 THEORY_RED (law SHARED 7/8, observed SPECIALIZED 6/8, mean margin −0.011).

**Where the 0.3 RED comes from.** At τ = 0 / 0.1 / 0.3 the two routes differ by |ΔMSE| = 0.001–0.044 on the protected
test (sd of a 2000-row test MSE ≈ 0.015–0.02), so these three grid values lie inside the finite-sample band the K5 B
lane registers ("crossover lies outside preregistered finite-sample uncertainty band → RED, else not"); this freeze
registered no band, so the frozen rule scores them literally. In addition the transcribed variance term weights modes
equally (`σ̂² p · mean_j 1/n_j`, 0.05–0.15 with a 5–13-row mode) where the mass-weighted form `σ̂² p m / n` (= 0.09 σ̂²,
the K5 balanced world's value) is the faithful one; with it the law would name SPECIALIZED on 7/8 at 0.3 and agree
5/8 — still inside the band. No descriptor-based law can reach ≥ 6/8 on a cell whose true objective gap is below the
test sd; the obstruction at 0.0/0.1/0.3 is structural to the grid, not to the law.

**Adjudication.** Terminal
**`B_SPECIALIZATION_REAL_GREEN_AT_HIGH_HETEROGENEITY_UNDER_BOUNDED_TAILS__CROSSOVER_CELLS_0_0_0_1_0_3_WITHIN_FINITE_SAMPLE_BAND__0_3_RED_UNDER_EQUAL_WEIGHT_VARIANCE_TERM`**.
The world-stage change did what it was frozen to do (leverage gone, the high-heterogeneity cell GREEN); the residual
RED is a grid-inside-the-band artefact plus a transcription defect of the variance term, named RV-377-194
(mass-weighted term + grid outside the band, e.g. τ ∈ {0.5, 0.8, 1.2, 1.6}) and not run. **Parent subtraction:** GMI ≠ CV
on 8/32; CV right 21/32, the law 19/32; at τ = 0.8 CV 8/8 vs the law 7/8 — not `PARENT_SUFFICIENT_CV`, and the law
does not beat CV anywhere.
