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

(empty at freeze)
