# Real-transfer revival: RV-377-191 (F_CONTINUAL_REAL) and RV-377-192 (B_SPECIALIZATION_REAL)

Status: **FROZEN BEFORE THE REVIVAL RUN.** Revival protocol #373. Source: RV-377-190 receipts under
`microscopes/results/real_transfer_v3/` (freeze commit `cd4c653d`, billy-laptop, 104/104 tasks, aggregate terminal
`REAL_TRANSFER_PHASE_LAWS_GREEN_ON_1_OF_3_LANES`: C_FEATURE_LEARNING_REAL GREEN 4/4 cells, F_CONTINUAL_REAL
INCONCLUSIVE (4/5 cells GREEN, the 0.95 cell INCONCLUSIVE), B_SPECIALIZATION_REAL INCONCLUSIVE (0/4 cells)). Those
RV-377-190 verdicts stay authoritative; nothing here reopens them. Date 2026-09-12.

## 1. F_CONTINUAL_REAL — diagnosis and RV-377-191

**Receipts.** Cells 0.6 / 0.8 / 0.9 / 1.0 GREEN at 6/8, 7/8, 6/8, 8/8; cell 0.95 INCONCLUSIVE (agree 1/8,
predicted-inadmissible 2, mean margin −524.7). Across the lane 9 of 40 predictions were `NONE` or `REPLAY` where the
protected test found EXPANSION (and sometimes REPLAY) admissible. Every one of those 9 is a replicate whose base-error
descriptor `ê` came out ≥ 0.044 on the 108-sample inner holdout (values 0.044–0.074), pushing the predicted EXPANSION
old accuracy `1 − ê` under the 0.95 bar, while the same deployed old model scored 0.951–0.982 on the 450-query
protected test. `ê` ranged 0.007–0.074 across replicates of the same cell (binomial sd ≈ 0.017 at n = 108 against
the 0.05 admissibility headroom); the true base error of the deployed model, read from the EXPANSION old accuracy
on the protected test, is 0.02–0.04 on every replicate.

**Stage elimination.** World: not the failure (agreement fractions land on the grid values to ±0.005; EXPANSION is
admissible on 40/40 replicates). Machines: not the failure (all three strategies train; REWRITE forgets exactly the
disputed classes as the law says: old accuracy ≈ â − ê on every replicate). Law: the midpoint rule is quantitatively
right where it can be checked (REPLAY old accuracy at 0.95: mean 0.949 against predicted 1 − ê − 0.025 ≈ 0.95; at
0.9: mean 0.917 against 0.92). Scoring: applied as frozen. **Descriptor: the failure.** `ê` from a single 108-sample
holdout has sampling noise comparable to the admissibility headroom, so admissibility calls near the bar are coin
flips; the 0.95 cell additionally sits *on* the real learner's crossover (REPLAY old accuracy mean 0.949 vs bar 0.95).

**One-stage attribution: DESCRIPTOR (finite-sample noise of `ê`).** Minimal change: `ê` = mean 5-fold CV error of the
old model over the whole old half (≈ 540 held-out predictions, sd ≈ 0.007); the deployed old model is then trained on
the full old half (the holdout no longer exists). Law, prices, thresholds, grid, machines, scoring unchanged. The
descriptor remains a training-split-only quantity of the *old model alone*; it does not cross-validate the strategies.

**Predictions before outcome** (fresh seeds: `SHA256("GMI-RT-V3R|" + revival commit + …)`, rule in the runner):
- **P-F1.** Cells 0.6, 0.8, 0.9, 1.0 GREEN with ≥ 7/8 agreement each; `NONE` predicted on ≤ 1 replicate lane-wide.
- **P-F2.** Cell 0.95 (the real learner's crossover): the law predicts REPLAY on ≥ 6/8 replicates (`ê ≤ 0.025`);
  REPLAY is observed admissible on 2–6 of 8; the cell is INCONCLUSIVE or THEORY_RED and is declared in advance the
  crossover cell (like K5's C 0.85 cell: "at the rule's edge, not claimed GREEN").
- **P-F3.** GMI law ≠ CV on ≤ 4 of 40 replicates, all in the 0.95 cell.
- **Kill (P-F4).** Any cell among 0.6/0.8/0.9/1.0 not GREEN kills the descriptor attribution (the law itself would
  then be wrong off the crossover).
- Terminal if P-F1, P-F4 hold: `F_CONTINUAL_REAL_GREEN_OFF_CROSSOVER__CROSSOVER_CELL_0_95_AT_ADMISSIBILITY_BAR`;
  the lane cannot be claimed GREEN under the frozen all-cells rule because one grid value was placed on the
  learner's crossover.

## 2. B_SPECIALIZATION_REAL — diagnosis and RV-377-192

**Receipts.** Agreement 5/8, 1/8, 0/8, 0/8 at τ = 0, 0.1, 0.3, 0.8; predicted-inadmissible 2, 5, 4, 2. The law
predicted SHARED on 30/32 replicates and NONE on 2. Observed: SPECIALIZED 16/32 (7/8 at τ = 0.8, where CV was
correct 8/8), SHARED 6/32, NONE 10/32. Two distinct mechanisms:

1. **Descriptor blindness (dominant, 16/32).** The descriptor `τ̂` (between-mode variance of the *shared model's*
   residual means) reads 0.00–0.29 at injected τ = 0.8, because a linear shared model with k-means modes that are
   near-linearly-separable in X absorbs most of the mode offset into its slopes; and the per-mode experts win by
   mode-specific *slopes* that the offset-only K5 form does not describe. The K5 law was stated for a featureless
   shared estimator (a grand mean); "heterogeneity" there means offsets because offsets are all a mean cannot fit.
2. **World leverage (10/32 NONE).** California housing has heavy-tailed features (AveRooms, AveOccup); with 400
   training rows a linear model extrapolates on high-leverage test rows, and the shared test MSE reaches 4.6–71.8 on
   9 replicates, making both routes inadmissible.

**One-stage attribution: THEORY/DESCRIPTOR.** The specialization law's heterogeneity term must be *heterogeneity
relative to the shared model class*: for a linear class that is parameter (slope + offset) heterogeneity across modes.
Minimal change: `τ̂²` := `(SSE_shared − SSE_experts)/n − p (m − 1) σ̂²/n` (Chow-type in-sample reduction of the
per-mode fits over the shared fit, minus the overfitting allowance), `σ̂²` := within-mode residual variance of the
per-mode fits. The K5 grand-mean world is the `p = 1` special case, so the frozen K5 law is unchanged where it was
tested. Everything else (world, leverage included; machines; prices; thresholds; grid; scoring) unchanged; the world
stage is deliberately *not* touched in this iteration.

**Predictions before outcome.**
- **P-B1.** The law predicts SPECIALIZED on ≥ 6/8 replicates at τ = 0.8 and at τ = 0.3, and agrees with the
  observed winner on every replicate whose observed winner is not NONE at those two values.
- **P-B2.** At τ = 0 and 0.1 the law predicts SHARED on ≥ 4/8 replicates each (real slope heterogeneity is small
  but non-zero at 400 rows; mixed predictions are expected).
- **P-B3.** NONE outcomes persist on 6–12 of 32 replicates (world leverage untouched), so by the V2 addendum at
  least two cells stay INCONCLUSIVE; the lane is not claimed GREEN.
- **P-B4.** GMI law ≠ CV on ≤ 8 of 32 replicates (down from 19/32).
- **Kill (P-B5).** SPECIALIZED predicted on ≤ 3/8 at τ = 0.8 kills the parameter-heterogeneity attribution.
- Terminal if P-B1 and P-B5 hold: `B_SPECIALIZATION_REAL_DIRECTION_RECOVERED_UNDER_PARAMETER_HETEROGENEITY_DESCRIPTOR__CELLS_INCONCLUSIVE_BY_WORLD_LEVERAGE`;
  the world-stage successor (winsorising features at training-split percentiles) is named RV-377-193 and is not run
  in this iteration.

## 3. Execution

`gmi_real_transfer_v3.py --revival --lanes F_CONTINUAL_REAL,B_SPECIALIZATION_REAL`, billy-laptop, 3 niced
processes, receipts under `microscopes/results/real_transfer_v3_revival/`; `--freeze-sha` = the commit that
introduces this file and the `--revival` code path. The C lane is not re-run (GREEN, not revived).

## 4. Adjudication (append-only)

Revival freeze `7fe510c705bc2125c8519ba8f885c233f4a6fe2b` (the commit `a1320499` that introduced this file crashed on a
task-tuple unpack in the worker; the fixing commit `7fe510c7` changed only that line and is the freeze SHA per
§1 of the RV-377-190 freeze). billy-laptop, 72/72 tasks, aggregate terminal `REAL_TRANSFER_PHASE_LAWS_GREEN_ON_0_OF_2_LANES`.

### 4.1 RV-377-191 (F_CONTINUAL_REAL, descriptor stage)

| cell | predicted | agree | oppose | pred.-inadm. | mean margin | verdict | CV right / GMI right |
|---|---|---|---|---|---|---|---|
| 0.6 | EXPANSION 8/8 | 8/8 | 0 | 0 | +1.00 | GREEN | 8 / 8 |
| 0.8 | EXPANSION 8/8 | 7/8 | 0 | 1 | +0.75 | INCONCLUSIVE | 7 / 7 |
| 0.9 | EXPANSION 8/8 | 7/8 | 0 | 1 | +0.75 | INCONCLUSIVE | 5 / 7 |
| 0.95 | EXPANSION 8/8 | 1/8 | 7 | 0 | −3666 | THEORY_RED | 5 / 1 |
| 1.0 | REWRITE 8/8 | 8/8 | 0 | 0 | +43.1 | GREEN | 8 / 8 |

- **P-F1 holds in substance and fails in form.** `ê` now ranges 0.021–0.046 (5-fold CV over ~540 old-half rows) and
  `NONE` was predicted on 0/40 replicates (9/40 in RV-377-190); agreement is 8, 7, 7, 8 of 8 off the crossover with
  **0 opposing** replicates. The two INCONCLUSIVE cells each carry exactly one replicate on which the *deployed baseline
  itself* failed the bar on the protected test (EXPANSION old accuracy 0.947 at 0.8 r2 and 0.9 r2), so the observed
  winner was NONE. That is test-split sampling at the frozen bar: the deployed old model's true old-task accuracy is
  ≈ 0.965 (mean of the other 30 replicates 0.971), the 450-query test has sd ≈ 0.0087 at that accuracy, so
  P(observed < 0.95) ≈ 4 % per replicate, i.e. 0.3 expected per cell of 8 — consistent with 1 and 1 observed. No
  training-split descriptor can remove it; it is structural to a 0.95 bar with 1.5 pp of headroom at 450 queries.
- **P-F2 fails at its premise.** The law never predicted REPLAY at 0.95: `ê` = 0.027–0.036 on all 8 replicates, so the
  midpoint rule gave REPLAY old accuracy 1 − ê − 0.025 = 0.939–0.948 < 0.95 and EXPANSION was named 8/8. The protected
  test found REPLAY admissible on 7/8 (old accuracy 0.949–0.969, mean 0.957) and winning on 6/8; the cell is
  THEORY_RED under the frozen rule. Two systematic biases, each ≈ 0.7–0.8 pp, add up to the miss: the 5-fold `ê`
  (models trained on 80 % of the old half) overstates the deployed model's error (mean 0.033 vs ≈ 0.026 from the
  test), and the midpoint rule's "half the disputed mass on each task" overstates the real learner's retention loss
  (observed loss 0.017 = 0.33 × the disputed mass, not 0.5 ×; at 0.6/0.8/0.9 the observed fraction is 0.40–0.50, so
  the rule is right off the crossover and 1 pp too pessimistic exactly where 1 pp decides).
- **P-F3 fails**: GMI ≠ CV on 8/40 (6 in the 0.95 cell, where CV named REPLAY on 5 and was right on 5 vs the law's 1;
  2 at 0.9 where CV named NONE and the law was right). **Kill P-F4 triggers formally** (0.8, 0.9 not GREEN) but by the
  baseline-at-the-bar mechanism above, not by any opposing replicate.

**Adjudication.** The descriptor attribution was correct for what it named (the 9 spurious predictions are gone) and
insufficient for the crossover cell, whose 0.7 pp headroom is below the combined systematic bias of the descriptor
and the retention rule and below the test sd. Terminal
**`F_CONTINUAL_REAL_DIRECTION_GREEN_OFF_CROSSOVER_30_OF_32__CROSSOVER_CELL_0_95_RED_WITHIN_FINITE_SAMPLE_BAND__STRUCTURAL_TO_FROZEN_BAR_AT_450_QUERIES`**.
A further iteration would have to change the law (retention-loss fraction of the real learner) *and* register a
finite-sample admissibility band as the K5 B lane does — two stages — and is named RV-377-194 (not run). **Parent
subtraction:** not `PARENT_SUFFICIENT_CV` (8/40 differ); CV is vindicated at the crossover (5 vs 1) and the GMI law
off it (2 vs 0): the transferred law adds nothing to cross-validation where the cell is decidable and loses to it
where it is not.

### 4.2 RV-377-192 (B_SPECIALIZATION_REAL, descriptor stage)

Predicted SHARED 29/32, NONE 3/32, SPECIALIZED 0/32; observed SPECIALIZED 13, SHARED 8, NONE 11. Cells INCONCLUSIVE
(agree 5, 2, 2, 1 of 8; pred.-inadmissible 0, 2, 4, 4). **P-B1 fails; kill P-B5 triggers** (SPECIALIZED predicted 0/8 at
τ = 0.8): the descriptor was not the dominant stage. The Chow-form `τ̂` did rise with the knob (0.0–0.27 at τ = 0,
0.34–0.59 at τ = 0.8) but the law's per-mode variance term `σ̂² p · mean_j(1/n_j)` was 0.3–1.7 because k-means isolated
1–7 tail rows into a mode on 31/32 replicates; the same tails produced shared test MSE 9.9–161 (NONE) on 11/32.
Attribution moves to the WORLD stage (unbounded feature tails at n = 400): `GMI_REAL_TRANSFER_REVIVAL_RV_377_193_FREEZE.md`.
Terminal **`B_SPECIALIZATION_REAL_DESCRIPTOR_ATTRIBUTION_KILLED__DOMINANT_STAGE_IS_WORLD_TAILS`**.
