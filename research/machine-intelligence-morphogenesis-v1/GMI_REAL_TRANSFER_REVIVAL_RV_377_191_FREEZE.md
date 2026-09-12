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

(empty at freeze)
