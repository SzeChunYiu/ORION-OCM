# Real transfer of three held-family K5 phase laws to real learners on real data (RV-377-190; RV-377-191 reserved)

Status: **FROZEN BEFORE ANY RUN.** Revival protocol #373: the laws, grids, descriptors, prices, admissibility
constitution, scoring rule, parent and kill conditions below are fixed at the commit that introduces this file and
`gmi_real_transfer_v3.py`; the receipts carry that commit SHA and every split seed derives from it. Nothing is
retuned after an outcome. Study directory `research/machine-intelligence-morphogenesis-v1` (M). Date 2026-09-12.

## 0. What this closes and what it cannot

Closure-gap class 3 REAL-TRANSFER (`GMI_CLOSURE_GAP_LEDGER_V7.md`) is open because the K5 held-family response laws
have only been tested in the study's own synthetic worlds (V7 protected, V8 revival) and the two real-data pilots
(V1 RED, V2 finite-portfolio bound GREEN) tested a *selector*, not a *phase law*. This freeze transfers three of the
eight frozen K5 laws to real off-the-shelf learners (scikit-learn only; no ORION/GMI code inside any machine) on real
data, with the phase parameter *estimated from the training split* rather than set by a world generator, and the
K5 prediction rule, price vector, quality thresholds and scoring rule transcribed unchanged.

It cannot close independent authorship (same author), modern scale, or hardware evidence. The three lanes are the
ones whose phase parameter has a faithful real analogue; the other five (routing density, residual fraction, query
reuse, prefix sharing, goal reuse) are exact-cost lanes whose "worlds" are accounting identities, not learners.

## 1. Common protocol

- **Freeze commit** `H` = the commit introducing this file and `gmi_real_transfer_v3.py`. If a mechanics defect
  forces a code change before the protected run, the fixing commit becomes `H` and is recorded in §5 with the diff
  summary; predictions, grids, prices and thresholds may not change.
- **Seed rule** `seed(lane, value, rep) = int(SHA256("GMI-RT-V3|" + H + "|" + lane + "|" + value + "|" + rep)[:16], 16) mod 2^32`.
  Every protected split, k-means, random-feature draw and MLP initialisation is seeded from it.
- **Protected split** per replicate: `train_test_split(test_size=0.25, random_state=seed)` (stratified for
  classification; for the housing lane a seeded permutation giving 400 training and 2000 test rows). Descriptors,
  machines, prices and both predictions are computed on the training split; the runner deep-copies and SHA-256
  hashes the prediction record *before* the first access to the test split and re-checks the hash at write time.
- **Grid** ≥ 4 values × 8 replicates per lane (5 values for the continual lane). Cells are scored by the K5 V1
  stochastic rule (≥ 6/8 agreement AND positive mean margin = GREEN; ≥ 6/8 opposing admissible winners AND negative
  mean margin = THEORY_RED; else INCONCLUSIVE) with the V2 addendum (≥ 6 predicted-inadmissible replicates =
  THEORY_RED; 1–5 = INCONCLUSIVE; agreement requires the predicted winner to be admissible). A lane is GREEN only if
  every cell is GREEN. Margin uses the K5 convention (alternative-minimum minus predicted; +1 if the predicted winner
  is the only admissible; −1 if inadmissible).
- **Parent subtraction.** Ordinary model selection = 3-fold cross-validation *of every strategy* on the training
  split with the same admissibility thresholds and the same price vector applied to the CV estimates. The GMI law
  predicts from descriptors *without* cross-validating the strategies. Per lane: if the GMI prediction equals the CV
  prediction on every replicate, the lane records `PARENT_SUFFICIENT_CV`; otherwise the differing replicates are
  listed with which predictor the protected test vindicated.
- **Kill conditions** (any lane): a cell with ≥ 6/8 predicted-inadmissible replicates is THEORY_RED (V2 addendum);
  a lane whose EXPANSION / SHARED / FIXED baseline is itself inadmissible on ≥ 6/8 replicates of a cell is
  `STRUCTURAL_INVALID` for that cell (the real learner cannot meet the frozen constitution; not a law failure).
- **Terminal** `REAL_TRANSFER_PHASE_LAWS_GREEN_ON_<k>_OF_3_LANES`, k = number of GREEN lanes. One revival
  iteration (RV-377-191) is allowed if any lane is RED: attribute to ONE stage, minimal change, fresh seeds from the
  revival commit.
- **Execution** billy-laptop only (`~/gmi-work/lanes/realtx`, uv venv Python 3.11.14, scikit-learn 1.9.1, numpy
  2.4.6), `nice -n 10`, 3 processes. Datasets: `sklearn.datasets.load_digits` (bundled) and
  `fetch_california_housing` (pre-fetched; SHA-256 of data+target recorded in the aggregate:
  digits `f6d9e39f…b70443`, housing `f8ce0321…e3a0b7`).

## 2. Lane F_CONTINUAL_REAL — task overlap (K5 lane F, corrigendum V3 form)

**Real world.** sklearn digits (1797 × 64). Old task: `y_old = 1[digit ∈ {0,1,2,3,4}]`. New task with label
agreement `a`: `a = 1.0` identical; `0.9` class 5 joins the positives; `0.8` additionally class 4 leaves; `0.6`
additionally class 6 joins and class 3 leaves; `0.95` the brighter half of class 5 (mean pixel intensity above the
training-split median of class-5 intensities) joins the positives. Old and new training data are disjoint halves of
the training split (the K5 world's structure: same input distribution, two labelers). Test split labelled both ways.

**Machines.** `MLPClassifier(hidden=64, max_iter=300, tol=0, no early stopping, warm_start=True)`.
REWRITE = continue training the old model on new data only; REPLAY = continue training the old model on stored old
data + new data; EXPANSION = keep the old model, train a separate new model.

**Descriptors (training split only).** `â` = fraction of training inputs with `y_old = y_new`;
`ω̂ = cos(π(1 − â))` (K5 units: the K5 world's overlap–agreement relation `agreement = 1 − arccos(ω)/π`);
`ê` = held-out error of the old model on a 20 % inner holdout of the old half (the learner's base error).

**Transferred law** (F: strict retention plus overlap; corrigendum V3 midpoint rule). Predicted accuracies
REWRITE (old `â − ê`, new `1 − ê`), REPLAY (old and new `1 − ê − (1 − â)/2`, the midpoint separator loses half of
the disputed mass on each task), EXPANSION (`1 − ê`, `1 − ê`). Admissible iff old ≥ 0.95 and new ≥ 0.90 (K5
thresholds). Predicted winner = cheapest predicted-admissible strategy under the K5 price
`cost = 1.0 × parameters + 0.001 × stored old scalars + 1e-5 × (epochs × samples)` (REWRITE < REPLAY < EXPANSION
whenever admissible). Expected per-cell predictions for `ê ≈ 0.01–0.03`: `a = 0.6, 0.8, 0.9 → EXPANSION`;
`a = 0.95 → REPLAY` iff `ê ≤ 0.025` (the K5 0.98-cell regime: rewrite inadmissible, replay admissible), else
EXPANSION; `a = 1.0 → REWRITE`. The cell prediction is made per replicate from `(â, ê)`.

**K5 correspondence.** `a ∈ {0.6, 0.8, 0.9, 0.95, 1.0}` ↔ `ω̂ ∈ {0.31, 0.81, 0.95, 0.988, 1.0}`; the K5 protected grid
was `ω ∈ {0, 0.6, 0.9, 0.98}` with EXPANSION at the first three and REPLAY at 0.98.

## 3. Lane B_SPECIALIZATION_REAL — heterogeneity (K5 lane B)

**Real world.** California housing (20 640 × 8, real target). Per replicate: 400 training rows, 2000 test rows,
inputs standardised and target standardised on the training rows; modes = `KMeans(k=4)` on the training inputs
(router = `predict`, routing error 0, charged 0.02 work per query as in K5). Heterogeneity knob
`τ ∈ {0.0, 0.1, 0.3, 0.8}`: `y ← y + τ · z_mode/√5`, `z = (−3, −1, 1, 3)` (the K5 world's unit-variance offsets).
`τ = 0` is the fully real cell; the offsets are the only synthetic element and are declared as such. The
prediction never reads `τ`; it reads the descriptor below.

**Machines.** SHARED = `Ridge(alpha=1)` on all training rows; SPECIALIZED = k-means router + one `Ridge(alpha=1)` per
mode.

**Descriptors (training split only).** Residuals `r` of the shared fit; `σ̂²` = pooled within-mode residual variance;
`τ̂²` = weighted between-mode variance of the mode-mean residuals minus its noise floor `(m − 1) σ̂² / n` (floored at 0);
`n_j` per-mode counts; `p = 9` parameters.

**Transferred law** (K5 `specialization`: expected objectives, router error 0, per-mode estimation variance of a
`p`-parameter linear model in place of a mean):
`E[SHARED] = σ̂² + τ̂² + σ̂² p / n + 0.002·1 + 1e-5·n`,
`E[SPECIALIZED] = σ̂² + σ̂² p · mean_j(1/n_j) + 0.002·4 + 1e-5·(n + 2000·0.02)`.
Predicted admissible iff the expected MSE ≤ 0.50 (K5 threshold, standardised-target units); predicted winner =
lower expected objective among the predicted-admissible. Observed objective = protected test MSE + the same price.
The law carries only *offset* heterogeneity; real slope heterogeneity across modes is a way for it to fail and is
the declared attribution if the `τ = 0` cell is RED.

**K5 correspondence.** Crossover `τ̂² ≈ σ̂² p (mean_j 1/n_j − 1/n) + Δprice`; at `n_j ≈ 100`, `σ̂² ≈ 0.4` this is
`τ̂ ≈ 0.17`, straddled by the grid.

## 4. Lane C_FEATURE_LEARNING_REAL — nonlinear signal with the reachability clause (K5 lane C, RV-377-170 form)

**Real world.** sklearn digits, real binary target `y_real = 1[digit ≥ 5]`, inputs = PCA-16 of the standardised
pixels (fit on the training split, re-standardised). Linear surrogate `g(x)` = decision function of a logistic
regression on the real target, fitted on the training split and scaled by its training standard deviation. Label at
signal `s`: `y_s = 1[(1 − s) g(x) + s (2 y_real − 1) ≥ 0]`, `s ∈ {0.0, 0.3, 0.6, 1.0}`: at `s = 0` the target is the
linear surrogate (fixed span suffices), at `s = 1` the real label; in between the real label overrides the surrogate
first on low-margin inputs, i.e. exactly where the real target's nonlinear residual lives. The test labels use the
training-fitted surrogate and the real test labels.

**Machines.** FIXED_FEATURE = `RBFSampler(gamma = 1/16, 288 components)` (frozen random features) +
`LogisticRegression` readout (state 289 parameters). TRAINABLE_FEATURE = `MLPClassifier(hidden = 16)` (state
16·16 + 16 + 16 + 1 = 289, matched) under the frozen development budget `D_real` = 200 epochs, adam, lr 1e-3,
alpha 1e-4, no early stopping. Feature movement = ‖θ_final − θ_init‖₂ (initial weights obtained from the same
`random_state` with a 1-step, lr 1e-12 fit).

**Descriptors (training split only).** `ŝ` = training error of the fixed-feature readout (the real analogue of the
K5 linear-Bayes floor); `e_tr(MLP)` = training error of the developed trainable realization under `D_real`
(the reachability descriptor); development receipts: epochs/iterations and movement.

**Transferred law** (RV-377-170 reachability-conditioned form). Price surplus
`δ = 0.02 (state_MLP − state_fixed) + 0.005 (epochs_MLP − iterations_fixed) + 0.01 · movement` (pp of error).
Predicted gain `= 100 (ŝ − e_tr(MLP))` pp. Both predicted admissible iff their training errors ≤ 0.18 (K5 threshold).
TRAINABLE_FEATURE wins iff both are predicted admissible AND predicted gain > δ; if exactly one is predicted
admissible it wins; none → NONE. Observed objective `= 100 × test error + 0.02 × state + 0.005 × steps + 0.01 ×
movement` (K5 prices), admissible iff test error ≤ 0.18, winner = lower objective among admissible.

**Content.** The law reads reachability from *training* error under the frozen budget (K5 form, where D7 gave
train ≈ test); the CV parent reads held-out error. They differ exactly where the trainable realization overfits, so
this lane is where the GMI law and ordinary CV can disagree; whichever the protected test vindicates is recorded.

## 5. Execution record (append-only)

- Freeze commit `H = cd4c653dfcd4cf4f88b60db33882d10403defa16` (this file + runner). A one-replicate mechanics smoke
  run (`--freeze-sha SMOKE`, one cell per lane, `smoke/smoke.log` on billy-laptop, not evidence) preceded the
  protected run; it found no defect and nothing was changed after it.
- Protected run: billy-laptop (Python 3.11.14, scikit-learn 1.9.1, numpy 2.4.6, Linux x86_64), 3 niced processes,
  104/104 tasks, receipts `microscopes/results/real_transfer_v3/`, aggregate `REAL_TRANSFER_AGGREGATE_V3.json`
  (md5 `779f3c9c…` verified identical on both hosts), dataset SHA-256 as registered in §1.
- Revival iterations: `GMI_REAL_TRANSFER_REVIVAL_RV_377_191_FREEZE.md` (RV-377-191 F descriptor, RV-377-192 B
  descriptor; freeze `7fe510c7`, receipts `microscopes/results/real_transfer_v3_revival/`, 72/72) and
  `GMI_REAL_TRANSFER_REVIVAL_RV_377_193_FREEZE.md` (RV-377-193 B world; freeze `267f39ee`, receipts
  `microscopes/results/real_transfer_v3_revival2/`, 32/32).

## 6. Adjudication (append-only)

Aggregate terminal: **`REAL_TRANSFER_PHASE_LAWS_GREEN_ON_1_OF_3_LANES`** (C_FEATURE_LEARNING_REAL GREEN;
F_CONTINUAL_REAL INCONCLUSIVE; B_SPECIALIZATION_REAL INCONCLUSIVE).

| cell | predicted (law) | agree | pred.-inadm. | mean margin | verdict | GMI = CV | CV right / GMI right |
|---|---|---|---|---|---|---|---|
| C 0.0 | TRAINABLE 8/8 | 8/8 | 0 | +3.67 | GREEN | 8/8 | 8 / 8 |
| C 0.3 | TRAINABLE 8/8 | 7/8 | 0 | +0.92 | GREEN | 8/8 | 7 / 7 |
| C 0.6 | TRAINABLE 8/8 | 7/8 | 0 | +1.42 | GREEN | 8/8 | 7 / 7 |
| C 1.0 | TRAINABLE 8/8 | 7/8 | 0 | +1.31 | GREEN | 8/8 | 7 / 7 |
| F 0.6 | EXPANSION 6, NONE 2 | 6/8 | 0 | +0.50 | GREEN | 7/8 | 7 / 6 |
| F 0.8 | EXPANSION 7, NONE 1 | 7/8 | 0 | +0.75 | GREEN | 7/8 | 8 / 7 |
| F 0.9 | EXPANSION 6, NONE 2 | 6/8 | 0 | +0.50 | GREEN | 5/8 | 5 / 6 |
| F 0.95 | REPLAY 2, EXPANSION 2, NONE 4 | 1/8 | 2 | −524.7 | INCONCLUSIVE | 4/8 | 4 / 1 |
| F 1.0 | REWRITE 8/8 | 8/8 | 0 | +34.4 | GREEN | 8/8 | 8 / 8 |
| B 0.0 | SHARED 8/8 | 5/8 | 2 | −0.240 | INCONCLUSIVE | 5/8 | 5 / 5 |
| B 0.1 | SHARED 8/8 | 1/8 | 5 | −0.506 | INCONCLUSIVE | 7/8 | 2 / 1 |
| B 0.3 | SHARED 8/8 | 0/8 | 4 | −0.527 | INCONCLUSIVE | 1/8 | 2 / 0 |
| B 0.8 | SHARED 6, NONE 2 | 0/8 | 2 | −0.552 | INCONCLUSIVE | 0/8 | 8 / 0 |

**C_FEATURE_LEARNING_REAL — GREEN on all four cells.** The reachability-conditioned law (training-error gain against
the frozen price surplus δ = 0.96–1.01 pp) predicted TRAINABLE_FEATURE on 32/32 replicates (predicted gain 1.9–5.1
pp from `ŝ` = 0.040–0.074 and MLP training error 0.004–0.030); the protected test vindicated it on 29/32 (observed
gains −0.0…6.7 pp; the three misses had observed gains 0.89, 0.44, 0.00 pp below δ). Both realizations were
admissible on 32/32 (test errors 0.04–0.09 and 0.007–0.06 against 0.18). **Parent subtraction:
`PARENT_SUFFICIENT_CV`** — 3-fold CV on the training split named the same winner on 32/32 replicates (and was wrong on
the same three). Boundary: the grid never crossed the law's own crossover (the fixed random-feature realization never
won, even at `s = 0` where the target is linear, because 288 RBF features fit a linear boundary less well than a
16-unit MLP on the digits PCA-16 inputs); the FIXED-wins regime would need a larger price surplus (a bigger MLP) or a
weaker trainable budget and is not exhibited here.

**F_CONTINUAL_REAL — INCONCLUSIVE (4/5 cells GREEN).** Off the crossover the transferred law is right where it makes
a prediction: 27/28 non-NONE predictions at 0.6/0.8/0.9 agreed (0 opposing), 8/8 at 1.0. The lane fails only through
(a) 9/40 `NONE`/`REPLAY` predictions traced to the 108-sample holdout estimate of the learner's base error
(`ê` 0.007–0.074 within one cell against 0.05 of admissibility headroom) and (b) the 0.95 cell, which sits on the real
learner's crossover (REPLAY old accuracy mean 0.949 against the 0.95 bar). Diagnosis and revival in
`GMI_REAL_TRANSFER_REVIVAL_RV_377_191_FREEZE.md` §4 (RV-377-191).

**B_SPECIALIZATION_REAL — INCONCLUSIVE (0/4 cells).** The law predicted SHARED on 30/32; observed SPECIALIZED 16/32,
SHARED 6/32, NONE 10/32. Two causes, separated in `GMI_REAL_TRANSFER_REVIVAL_RV_377_191_FREEZE.md` §2 and
`…RV_377_193_FREEZE.md`: the offset-only heterogeneity descriptor is blind to what a *featured* shared model absorbs
(RV-377-192), and the unbounded feature tails of California housing at n = 400 produce 1–7-row k-means modes and
test-leverage blow-ups (RV-377-193). CV was right on 17/32 (8/8 at τ = 0.8).

**Lane terminals.** C: `C_FEATURE_LEARNING_REAL_GREEN_4_OF_4__PARENT_SUFFICIENT_CV__FIXED_WINS_REGIME_NOT_EXHIBITED`.
F: `F_CONTINUAL_REAL_INCONCLUSIVE__GREEN_OFF_CROSSOVER_4_OF_5_CELLS` → RV-377-191. B:
`B_SPECIALIZATION_REAL_INCONCLUSIVE_0_OF_4` → RV-377-192 → RV-377-193.
