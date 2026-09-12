# Real-transfer revival, third iteration: RV-377-194 (B and F crossover cells re-tested off-band; cost-charged parent)

Status: **FROZEN BEFORE THE RUN.** Successor to `GMI_REAL_TRANSFER_REVIVAL_RV_377_191_FREEZE.md` (RV-377-191, F lane)
and `GMI_REAL_TRANSFER_REVIVAL_RV_377_193_FREEZE.md` (RV-377-193, B lane), whose verdicts stand and are not reopened.
Source receipts: `microscopes/results/real_transfer_v3_revival/` (freeze `7fe510c7`, 72/72) and
`microscopes/results/real_transfer_v3_revival2/` (freeze `267f39ee`, 32/32). Runner: new file `gmi_real_transfer_rv194.py`
(imports the frozen machines, prices, thresholds and helpers from `gmi_real_transfer_v3.py`, which is not edited).
Freeze commit `H` = the commit that introduces this file and the runner; seeds `SHA256("GMI-RT-V3R3|" + H + lane +
value + replicate)`. One iteration only; nothing is retuned after outcomes. Date 2026-09-12.

## 1. One-stage attribution restated from the records

**B_SPECIALIZATION_REAL (RV-377-193).** The world-stage change did what it was frozen to do (NONE 0/32, τ = 0.8 GREEN
7/8, margin +0.43 ≈ 10 test sd). The residual RED at τ = 0.3 has two named causes in the RV-377-193 adjudication:
(i) the transcribed variance term `σ̂² p · mean_j(1/n_j)` weights modes equally, so a 5–13-row k-means cluster inflates
the specialization penalty to 0.05–0.15 where the mass-weighted form `σ̂² p m / n` (= 0.09 σ̂² ≈ 0.027) is the faithful
one (the K5 balanced world has `n_j = n/m` and hides the difference); (ii) the grid values 0, 0.1, 0.3 give observed
objective gaps |ΔMSE| = 0.001–0.044 against a test-MSE sd of ≈ 0.015–0.02, i.e. inside the finite-sample band the K5 B
lane registers ("protected winner/crossover lies outside preregistered finite-sample uncertainty band → RED, else
not", `GMI_K5_BH_PHASE_FREEZE_V1.json`), which the real-transfer freeze never registered. **Attribution: SPEC/SCORING
(transcription of the variance term + absence of the band the source lane carries); the law's mechanism is not
implicated** — with the mass-weighted term the receipts already give SPECIALIZED on 7/8 at 0.3.

**F_CONTINUAL_REAL (RV-377-191).** Off the crossover the law is right on 30/32 with 0 opposing. The 0.95 cell missed
because two ≈ 0.7 pp systematic biases (5-fold `ê` on 80 % of the old half overstates the deployed error, 0.033 vs
≈ 0.026; the corrigendum-V3 midpoint "half the disputed mass lost per task" overstates the real MLP's retention loss,
observed 0.33 × at 0.95) exceed the 0.75 pp headroom, which is itself below one test sd (1.03 pp at the 0.95 bar with
450 queries). **Attribution: DESCRIPTOR/LAW at the crossover (retention fraction is a learner-class quantity the K5 law
fixes at 1/2), inside a cell that no descriptor can decide at this test size.** Two ≈ 0.7 pp baseline-at-the-bar
misses at 0.8 and 0.9 (EXPANSION old accuracy 0.947 on the test) are test sampling at the bar, not the law.

## 2. Pre-registered changes (minimal, all listed)

### 2.1 B lane

- **B1 — mass-weighted variance term.** `E[obj_SPEC] = σ̂² + σ̂² p m / n + price_SPEC` (test mass of mode j is ≈ n_j/n
  and its estimation variance σ² p / n_j, so Σ_j (n_j/n)(σ² p / n_j) = σ² p m / n). `E[obj_SHARED] = σ̂² + τ̂² + σ̂² p / n +
  price_SHARED` unchanged. Descriptor (RV-377-192 Chow form) and world (RV-377-193 winsorising at training 1st/99th
  percentiles) unchanged. With `m = 4, p = 9, n = 400`: SPECIALIZED predicted iff `τ̂² > 0.0675 σ̂² + Δprice`.
- **B2 — registered finite-sample band (K5 B rule made explicit).** Per replicate, on the protected test, with
  per-query squared errors `e_S,i², e_P,i²`: `se_Δ = sd(e_S,i² − e_P,i²)/√n_test`, `se_s = sd(e_s,i²)/√n_test`. A replicate is
  **band-inside** iff the law's winner ≠ the observed winner AND the disagreement is unresolved by the test: either
  (both routes predicted and observed admissible and `|Δ_obs| ≤ 2 se_Δ`), or (every route whose predicted admissibility
  differs from its observed admissibility has `|MSE_s − 0.50| ≤ 2 se_s`). Agreeing replicates are never band-inside.
  `z = 2` is frozen.
- **B3 — off-band grid by frozen power calculation.** From the RV-377-193 receipts the unabsorbed-offset coefficient
  `κ_r = (τ̂²_r(0.8) − τ̄²₀)/0.8²` with `τ̄²₀ = 0.0273` (mean τ̂² at τ = 0) is 0.141, 0.163, 0.183, 0.193, 0.296, 0.302,
  0.310, 0.475 (min 0.141, median 0.245); the τ = 0 term `τ̄²₀ − 0.0675 σ̄² − Δprice ≈ −0.001` (crossover sits at τ ≈ 0),
  so the predicted objective margin is `≈ κ τ²`. Planning test sd `sd_plan(Δ) = 0.02 · √(2000 / n_test)` (the RV-377-193
  figure, conservative: the RV-377-193 predicted-vs-observed residual sd at 0.8 is 0.015 at n_test = 2000). Registered
  **n_test = 8000** (400 + 8000 ≤ 20 640 rows), `sd_plan = 0.010`, `3 sd_plan = 0.030`. Off-band τ values must give
  `κ_min τ² > 0.030`: τ ∈ {0.5, 0.65, 0.8, 1.0} → min-κ margins 0.035, 0.060, 0.090, 0.141 (median-κ 0.061, 0.104, 0.157,
  0.245). Band cells τ ∈ {0, 0.1, 0.3} (min-κ margins 0, 0.001, 0.013 < 0.030) are retained and declared
  **INSIDE_BAND_BY_CONSTRUCTION** — reported with direction tallies, never GREEN/RED. Prices follow n_test through the
  K5 route work: `price_SHARED = 0.006`, `price_SPEC = 0.002·4 + 10⁻⁵(400 + 0.02·8000) = 0.0136`, `Δprice = 0.0076`.
  Sizes: n_train = 400, n_test = 8000, 7 τ values × 8 replicates = 56 tasks.

### 2.2 F lane

- **F1 — within-train probe and retention descriptor.** Hold out a probe set `P` = 20 % of the training split
  (stratified by digit class, ≈ 270 rows) before development; the remaining 80 % is permuted into the old and new
  halves (≈ 539 rows each) and the deployed old model, REWRITE, REPLAY and EXPANSION are trained on them exactly as
  before (development receipts fix the prices as before). Descriptors, all training-split, **zero extra training runs**:
  `â` as before; `ê` = error of the deployed old model under old labels on the rows it never saw within the training
  split (new half ∪ P, ≈ 810 rows, binomial sd ≈ 0.55 pp; unbiased for the deployed model — the 5-fold `ê` of RV-377-191
  was biased +0.7 pp because its models were smaller); `ρ̂_s` for s ∈ {REPLAY, REWRITE} = fraction of the *disputed*
  probe rows `D_P = {i ∈ P : y_old ≠ y_new}` on which the deployed strategy's prediction ≠ the old label (fraction of the
  disputed mass lost on the old task). Transferred law: `old(s) = 1 − ê − ρ̂_s (1 − â)`, `new(s) = 1 − ê − (1 − ρ̂_s)(1 − â)`
  for REPLAY and REWRITE; EXPANSION `old = new = 1 − ê` (K5 form); admissibility bars 0.95/0.90 and the cheapest-admissible
  rule unchanged. The corrigendum-V3 midpoint (`ρ = 1/2`) is the special case `ρ̂ = 1/2`. `|D_P|` ≈ 13 at a = 0.95, 27 at
  0.9, 54 at 0.8, 108 at 0.6 (sd of ρ̂ ≈ 0.13, 0.09, 0.07, 0.05).
- **F2 — admissibility band.** `sd_bar = √(bar(1 − bar)/n_test)`: 1.03 pp at the 0.95 bar and 1.41 pp at the 0.90 bar with
  n_test = 450. A replicate is band-inside iff the law's winner ≠ the observed winner AND every strategy whose predicted
  admissibility differs from its observed admissibility has its decisive test accuracy within `2 sd_bar` of the bar (all
  differing strategies must be within the band; one far miss is a real miss). `z = 2` frozen. The two RV-377-191
  baseline-at-the-bar replicates (0.947 vs 0.95) are band-inside under this rule.
- **F3 — power sizing at 0.95 (computed, cannot be met on digits).** Predicted REPLAY margin to the bar
  `0.05 − ê − ρ (1 − â)` with `ê ≈ 0.026, ρ ≈ 0.33, 1 − â = 0.05` is **0.75 pp**; `3 sd_bar < 0.0075` needs
  `n_test > (3 · 0.218 / 0.0075)² ≈ 7 600` labelled queries. sklearn digits has 1 797 rows; with the deployed models on
  80 % of a 75 % training split `ê` rises with any smaller split, so no feasible test size on this dataset makes the cell
  off-band (the corrigendum-V3 regime "replay admissible, rewrite inadmissible" is ≈ 2.4 pp wide for this learner,
  below 3 sd at every split). The 0.95 cell is therefore **INSIDE_BAND_BY_CONSTRUCTION** on digits; it is run at the
  frozen split (n_test = 450, unchanged, for comparability) for direction and calibration only. A larger digit world
  (e.g. 70 000-row MNIST) would be a new world and is not run in this iteration. Grid a ∈ {0.6, 0.8, 0.9, 0.95, 1.0} × 8 =
  40 tasks. OFF-BAND cells: 0.6, 0.8, 1.0 by the 3 sd rule (the strategy the law rejects — REPLAY at 0.6/0.8, with
  predicted old accuracy ≈ 0.78/0.89 — is ≥ 6 pp = 6 sd_bar below the bar; at 1.0 all three strategies are ≥ 1.5 pp
  above the bar and REWRITE wins on price alone), and 0.9 declared OFF-BAND at ≈ 2 sd_bar only (REPLAY predicted
  ≈ 0.93 with ρ̂ ≈ 0.4, 2 pp below the bar; flagged, not exempted). The predicted winner's own admissibility margin
  (EXPANSION old accuracy ≈ 0.965–0.98 vs 0.95, 1.5–3 sd_bar) is the baseline-at-the-bar sampling that F2 classifies as
  band-inside rather than counting it against the law.

### 2.3 Cost-charged parent comparison (not run by RV-377-190…193)

- **Parent 1 (frozen K5 parent): 3-fold CV** of every strategy on the development data with the same rule. Extra fits
  beyond development, counted in the runner: F = 3 folds × (old + REWRITE + REPLAY + new) = **12**; B = 3 folds ×
  (1 shared + 4 experts) = **15**. The law needs **0** extra fits in both lanes (B: descriptors from the deployed shared and
  per-mode fits; F: descriptors from the deployed models on the probe). Wall time of the law's descriptor block and of
  the CV block is recorded per replicate.
- **Parent 2 (F only, the free parent): holdout selection on P** — each deployed strategy's old/new accuracy on P, same
  bars, cheapest admissible. 0 extra fits, same holdout as the law. B has no free holdout parent (the law is in-sample
  with an analytic overfitting allowance; any holdout parent would refit).
- Selection cost is charged as extra training fits (primary) and wall seconds (secondary); the law's data cost in F
  (deployed models on 80 % of the training split) is disclosed as its price and is the same for Parent 2.

## 3. Scoring (frozen)

Per cell: `n_in` band-inside replicates, `n_out = 8 − n_in`, `q = ⌈0.75 n_out⌉`. Cell class from §2 (BAND cells are
`INSIDE_BAND_BY_CONSTRUCTION`; they carry tallies only). For OFF-BAND cells: `n_in ≥ 4` → `INSIDE_BAND_MEASURED` (a
sizing miss, K2); else on the band-outside replicates with the K5 V1 rule and V2 addendum: predicted-inadmissible
(band-outside) ≥ q → THEORY_RED; ≥ 1 → INCONCLUSIVE; agreement ≥ q and mean margin > 0 → GREEN; opposing ≥ q and mean
margin < 0 → THEORY_RED; else INCONCLUSIVE. Lane GREEN iff every OFF-BAND cell GREEN. Margin = K5 convention
(`margin_k5`). Direction tallies (predicted-winner counts, observed-winner counts, agree/oppose on all 8) are recorded
for every cell. Calibration: B `Δ_pred − Δ_obs` per replicate (objective gap SHARED − SPECIALIZED); F predicted minus
observed REPLAY old accuracy in pp.

## 4. Predictions before outcome

- **P-1 (B off-band).** τ ∈ {0.5, 0.65, 0.8, 1.0} each GREEN with ≥ 6 band-outside agreements; 0 opposing at 0.8 and
  1.0; ≤ 1 opposing at 0.5.
- **P-2 (B band).** τ ∈ {0, 0.1, 0.3} INSIDE_BAND_BY_CONSTRUCTION; tallies: the mass-weighted law names SPECIALIZED on
  ≥ 4/8 at 0.3 and on 2–6/8 at 0 (real slope heterogeneity sits at the crossover).
- **P-3 (B calibration).** `|Δ_pred − Δ_obs| ≤ 0.05` on ≥ 28/32 off-band replicates.
- **P-4 (B admissibility at 1.0).** SHARED test MSE > 0.50 on ≥ 3/8; the law predicts SHARED inadmissible on the same
  replicates up to band-inside ones.
- **P-5 (F off-crossover).** 0.6, 0.8, 0.9, 1.0 GREEN with ≥ 7/8 agreement each; band-inside replicates ≤ 3 lane-wide off
  the crossover, all of them baseline-at-the-bar (EXPANSION old accuracy within 2.05 pp of 0.95).
- **P-6 (F crossover, tallies only).** 0.95 INSIDE_BAND_BY_CONSTRUCTION. The corrected law names REPLAY on ≥ 5/8;
  REPLAY observed admissible on 5–8/8; mean |predicted − observed REPLAY old accuracy| ≤ 1.5 pp.
- **P-7 (F probe validity).** Mean ρ̂_REPLAY ∈ [0.20, 0.55] at 0.95 and ∈ [0.30, 0.60] at 0.6–0.9; mean ρ̂_REWRITE ≥ 0.75 at
  a ≤ 0.9 (REWRITE forgets the disputed classes; REPLAY keeps most of them).
- **P-8 (cost, B).** The law names CV's winner on ≥ 29/32 off-band replicates at 0 vs 15 extra fits.
- **P-9 (cost, F).** The law names CV's winner on ≥ 29/32 off-crossover replicates at 0 vs 12 extra fits; at 0.95 CV is
  right at least as often as the law (recorded as the honest residual: CV still wins at the crossover).
- **P-10 (F free parent).** The law names the holdout parent's winner on ≥ 36/40 replicates; if so the F lane's
  law is `PARENT_SUFFICIENT_HOLDOUT` (the free predictor that equals CV off-crossover is holdout selection itself; the
  law adds the structural decomposition `ê + ρ̂ (1 − â)`, not information).

## 5. Falsifiers and kill conditions

- **K1 (B law wrong off-band).** Any OFF-BAND cell THEORY_RED → the mass-weighted law is wrong where it is decidable;
  attribute (calibration residuals, κ, admissibility) and stop. No further iteration from this lane.
- **K2 (B sizing miss).** Any OFF-BAND cell with `n_in ≥ 4` → `INSIDE_BAND_MEASURED`; the power calculation (sd_plan or κ)
  was wrong. Recorded as a sizing error, not a law failure; RV-377-196 is reserved only if the error is a provable
  transcription of §2.1 B3.
- **K3 (F direction regressed).** Any of 0.6/0.8/0.9/1.0 not GREEN under §3 → the probe descriptor regressed the
  off-crossover direction; the probe attribution is killed and the RV-377-191 descriptor stands.
- **K4 (F probe invalid).** P-7 fails → the probe is not measuring retention (too few disputed rows or in-sample
  contamination); the retention-descriptor change is killed independent of the cell verdicts.
- **K5 (parent sufficient on cost).** The law names CV's winner on < 29/32 off-band replicates in a lane → that lane's
  terminal is `PARENT_SUFFICIENT_CV` (the law is not a free substitute for CV where CV is decidable).
- **K6 (F free parent).** P-10 holds → F terminal carries `PARENT_SUFFICIENT_HOLDOUT`; this is a SUCCESS terminal for
  the parent, not a failure of direction.
- **K7 (mechanics).** A crash or prediction-hash mismatch → the fixing commit changes only the failing line, is
  disclosed here, and becomes the freeze SHA (RV-377-191 precedent `7fe510c7`).

## 6. Terminals

- B: P-1 ∧ P-8 → `B_SPECIALIZATION_REAL_GREEN_OFF_BAND_UNDER_MASS_WEIGHTED_TERM__FREE_LAW_EQUALS_CV_OFF_BAND__CROSSOVER_CELLS_INSIDE_BAND_BY_CONSTRUCTION`;
  K1 → `B_SPECIALIZATION_REAL_MASS_WEIGHTED_LAW_RED_OFF_BAND__<attribution>`; K5 → `…__PARENT_SUFFICIENT_CV`.
- F: P-5 ∧ P-9 ∧ ¬P-10 → `F_CONTINUAL_REAL_GREEN_OFF_CROSSOVER_UNDER_PROBE_RETENTION_LAW__0_95_INSIDE_BAND_BY_CONSTRUCTION_ON_DIGITS`;
  P-10 → the same with `__PARENT_SUFFICIENT_HOLDOUT`; K3 → `F_CONTINUAL_REAL_PROBE_DESCRIPTOR_KILLED`.
- Aggregate: both lanes reach their P-1/P-5 terminals with P-8/P-9 → 
  `REAL_TRANSFER_LAWS_FREE_PREOUTCOME_PREDICTOR_EQUALS_CV_OFF_BAND__CV_WINS_AT_CROSSOVERS`; any K5 → 
  `REAL_TRANSFER_PHASE_LAWS_PARENT_SUFFICIENT_CV`.

## 7. Execution

`gmi_real_transfer_rv194.py --freeze-sha H --out-dir microscopes/results/real_transfer_rv194 --jobs 3` on billy-laptop
(load checked before launch; billy-old as fallback if load > 12), `nice -n 10`, venv `~/gmi-work/lanes/realtx/venv`
(scikit-learn 1.9.1, numpy 2.4.6), tree rsynced to `~/gmi-work/lanes/realtx2/research/`, receipts rsynced back and
md5-verified on both sides. 96 tasks. The C lane is not re-run (GREEN and parent-sufficient in RV-377-190).

## 8. Adjudication (append-only)

Freeze `03a2fea81a79848f5132368fbc992aa695349efd` (this file + `gmi_real_transfer_rv194.py`, one commit; nothing changed after
it). billy-laptop (Python 3.11.14, scikit-learn 1.9.1, numpy 2.4.6, load 6.9 at launch), 3 niced processes, 96/96
tasks, receipts `microscopes/results/real_transfer_rv194/`, aggregate `REAL_TRANSFER_RV194_AGGREGATE.json` (md5
`bd570509…` identical on both hosts). A one-replicate mechanics smoke (`--freeze-sha SMOKE`, `smoke_rv194/` on the
laptop only, not synced, not evidence) preceded the run and changed nothing. Prediction hashes re-checked at write on
96/96.

### 8.1 B_SPECIALIZATION_REAL (mass-weighted term, band, off-band grid at n_test = 8000)

| τ | class | predicted | observed | agree | oppose | band-in | verdict | law right / CV right | gap pred − obs (mean |·|) | se_Δ |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.0 | BAND | SHARED 7, SPEC 1 | SHARED 8 | 7/8 | 1 | 0 | INSIDE_BAND_BY_CONSTRUCTION | 7 / 8 | 0.019 | 0.0045 |
| 0.1 | BAND | SHARED 5, SPEC 3 | SHARED 8 | 5/8 | 3 | 1 | INSIDE_BAND_BY_CONSTRUCTION | 5 / 6 | 0.022 | 0.0043 |
| 0.3 | BAND | SHARED 4, SPEC 4 | SPEC 6, SHARED 2 | 4/8 | 4 | 2 | INSIDE_BAND_BY_CONSTRUCTION | 4 / 4 | 0.015 | 0.0037 |
| 0.5 | OFF | SPEC 8 | SPEC 8 | 8/8 | 0 | 0 | **GREEN** (+0.049) | 8 / 7 | 0.009 | 0.0049 |
| 0.65 | OFF | SPEC 8 | SPEC 8 | 8/8 | 0 | 0 | **GREEN** (+0.222) | 8 / 8 | 0.027 | 0.0065 |
| 0.8 | OFF | SPEC 8 | SPEC 8 | 8/8 | 0 | 0 | **GREEN** (+0.559) | 8 / 7 | 0.035 | 0.0077 |
| 1.0 | OFF | SPEC 8 | SPEC 8 | 8/8 | 0 | 0 | **GREEN** (+0.795) | 8 / 8 | 0.041 | 0.0103 |

- **P-1 holds** (four off-band cells GREEN, 32/32 agreement, 0 opposing, 0 band-inside). **P-2 holds** in verdict class;
  the tally at τ = 0 (SPECIALIZED named 1/8) is below the predicted 2–6/8 — the mass-weighted crossover sits slightly
  above the real slope heterogeneity, so SHARED is named 7/8 and observed 8/8. **P-4 holds** (SHARED test MSE > 0.50 on
  6/8 at τ = 1.0; the law predicted 8/8, the two extra within 1.5 se of the bar). **P-8 holds**: the law names CV's winner
  on 30/32 off-band replicates at 0 vs 15 extra fits (mean 14.9); on the two differing replicates (0.5 r4: CV SHARED;
  0.8 r3: CV NONE) the law was right and CV wrong.
- **P-3 fails**: |Δ_pred − Δ_obs| ≤ 0.05 on 25/32 off-band replicates (8, 7, 6, 4 by cell), not ≥ 28; the calibration
  residual grows with τ (mean |·| 0.009 → 0.041, extremes ±0.09 at τ = 1.0) while the direction never fails. The
  Chow-form τ̂² is a noisier estimator of the realised gap at large offsets than at small ones; a quantitative-gap claim
  is not made.
- **Band as measured vs planned.** `se_Δ` = 0.0024–0.013 at n_test = 8000 against the planning 0.010: the paired test
  error is 2× smaller than the conservative unpaired figure, so the three declared BAND cells were band-inside on only
  0, 1, 2 replicates. Their misses are descriptor-side (e.g. τ = 0 r3: τ̂² = 0.054 from a 9-row mode, predicted
  SPECIALIZED, observed SHARED at 5.5 se), not test-side: at the crossover the obstruction is now the descriptor's
  finite-sample noise, not the test's. No kill fires (K1 no cell RED; K2 no off-band cell with n_in ≥ 4; K5 30/32).
- **Terminal (frozen logic):**
  `B_SPECIALIZATION_REAL_GREEN_OFF_BAND_UNDER_MASS_WEIGHTED_TERM__FREE_LAW_EQUALS_CV_OFF_BAND__CROSSOVER_CELLS_INSIDE_BAND_BY_CONSTRUCTION`.
  At the crossovers CV is right 18/24 vs the law 16/24 (the honest residual: CV still wins there, by two replicates).

### 8.2 F_CONTINUAL_REAL (within-train probe, admissibility band; 0.95 at the frozen 450 queries)

| a | class | predicted | observed | agree | oppose | band-in | verdict | law / CV / holdout right | ρ̂_REPLAY | ρ̂_REWRITE | REPLAY-old pred − obs |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.6 | OFF | EXPANSION 8 | EXPANSION 7, NONE 1 | 7/8 | 0 | 1 | **GREEN** (+1.00) | 7 / 5 / 6 | 0.50 | 0.97 | −3.1 pp |
| 0.8 | OFF | EXPANSION 8 | EXPANSION 8 | 8/8 | 0 | 0 | **GREEN** (+1.00) | 8 / 5 / 8 | 0.51 | 0.96 | −1.0 pp |
| 0.9 | OFF | EXPANSION 8 | EXPANSION 8 | 8/8 | 0 | 0 | **GREEN** (+1.00) | 8 / 5 / 7 | 0.44 | 0.95 | −0.1 pp |
| 0.95 | BAND | REPLAY 5, EXPANSION 3 | REPLAY 6, EXPANSION 2 | 5/8 | 2 | 3 | INSIDE_BAND_BY_CONSTRUCTION | 5 / 2 / 6 | 0.38 | 0.75 | −0.8 pp (mean |·| 1.0) |
| 1.0 | OFF | REWRITE 8 | REWRITE 8 | 8/8 | 0 | 0 | **GREEN** (+34.4) | 8 / 8 / 8 | — | — | −1.6 pp |

- **P-5 holds** (7, 8, 8, 8 of 8; one band-inside replicate lane-wide off the crossover, 0.6 r7, EXPANSION old 0.933 =
  1.6 sd below the bar, observed NONE). **P-6 holds**: the corrected law names REPLAY 5/8 (the corrigendum-V3 rule named
  it 0/8 in RV-377-191); REPLAY observed admissible 6/8; mean |predicted − observed REPLAY old accuracy| 0.98 pp, signed
  −0.83 pp (still pessimistic by under one test sd). The three band-inside replicates are the two opposing ones (REPLAY
  observed 0.962/0.964, predicted 0.940/0.941; z 1.19, 1.41) and the one predicted-inadmissible (REPLAY 0.9467, z 0.32);
  the five band-outside replicates all agree. The cell keeps its by-construction class; no GREEN is claimed for it.
  **P-7 holds** (ρ̂_REPLAY 0.38–0.51, ρ̂_REWRITE 0.95–0.97 at a ≤ 0.9 and 0.75 at 0.95): the probe measures retention.
- **P-9 first clause fails; K5 fires by its letter.** The law names CV's winner on 24/32 off-crossover replicates (< 29).
  All eight differing replicates are the same event: 3-fold CV named **NONE** (EXPANSION old accuracy below 0.95 on
  2/3-size folds, ≈ 360 old rows) where the law named EXPANSION and EXPANSION won on the protected test. Off the
  crossover the law is right 31/32 and CV 23/32; **P-9 second clause also fails, in the law's favour**: at 0.95 the law
  is right 5/8 and CV 2/8 (CV named NONE 3/8 and EXPANSION 3/8). K5 as frozen measures *agreement with* CV, not
  *correctness against* CV; on these receipts it is triggered entirely by CV's own errors. This is a specification
  defect of §5 K5, recorded here and not repaired by re-scoring (never retune after outcome); the frozen terminal
  label stands and the substantive reading is stated beside it.
- **P-10 holds; K6 fires**: the law names the free holdout parent's winner on 37/40 (holdout right 35/40, the law 36/40).
  The free predictor that equals (here: beats) 3-fold CV off-crossover is holdout selection on the 20 % probe; the law is
  holdout selection with the structural decomposition `ê + ρ̂ (1 − â)` and the same cost (0 extra fits, deployed models
  on 80 % of the training split; CV: 12 extra fits, 4.1–4.6 s vs 0.01–0.02 s per replicate).
- **Terminal (frozen logic):** `F_CONTINUAL_REAL_GREEN_OFF_CROSSOVER__PARENT_SUFFICIENT_CV__PARENT_SUFFICIENT_HOLDOUT`.
  Substantive reading from the same receipts: direction GREEN on all four off-crossover cells under the probe law;
  the law is a free predictor that is *more* accurate than 3-fold CV in this lane (31/32 vs 23/32 off-crossover;
  5/8 vs 2/8 at the crossover) and *equal* to free holdout selection (37/40 same winner) — `PARENT_SUFFICIENT_HOLDOUT`
  is the honest parent terminal; `PARENT_SUFFICIENT_CV` is the label of a mis-specified kill.

### 8.3 Cost-charged comparison and aggregate

| lane | off-band replicates | law right | CV right | law = CV | law extra fits | CV extra fits | crossover: law / CV right |
|---|---|---|---|---|---|---|---|
| B | 32 | 32 | 30 | 30 | 0 | 15 | 16 / 18 (of 24) |
| F | 32 | 31 | 23 | 24 | 0 (+ 20 % probe) | 12 | 5 / 2 (of 8); holdout 6 |
| both | 64 | **63** | **53** | 54 | 0 | 12–15 | 21 / 20 (of 32) |

Aggregate terminal by the frozen logic: **`REAL_TRANSFER_PHASE_LAWS_PARENT_SUFFICIENT_CV`** (K5 on F). What the receipts
show: off-band the transferred laws are a free, pre-outcome predictor right on 63/64 replicates where 3-fold CV is right
on 53/64 at 12–15 extra fits per replicate; at the crossovers neither is reliable (law 21/32, CV 20/32, free holdout
6/8 on F) and the obstruction has moved from the test (bands now 2–4× narrower than the crossover gaps) to the
descriptors' own finite-sample noise (τ̂² from 7–17-row modes; ρ̂ from 8–17 disputed probe rows). The RV-377-191 finding
"CV wins at the crossover 5 vs 1" is reversed under the corrected law (5 vs 2), and the RV-377-193 finding "CV right
21/32 vs law 19/32" is reversed off-band (32 vs 30). One iteration; no further run from this freeze. Successors named,
not run: (i) a corrected K5 (law-right vs CV-right) is a scoring-rule change only and needs no run; (ii) descriptor
precision at the crossover (mode-mass floor for τ̂², larger probe for ρ̂) is the next single stage; (iii) a larger digit
world for an off-band 0.95 cell is a new world.
