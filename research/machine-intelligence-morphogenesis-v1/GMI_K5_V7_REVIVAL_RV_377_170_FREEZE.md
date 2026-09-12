# K5 V7 non-green lanes: diagnosis and revival freeze (RV-377-170, RV-377-171)

Status: **FROZEN BEFORE ANY V8 EXECUTION** (revival protocol #373: diagnose, attribute to one stage, minimal
justified change, freeze the new prediction, fresh test; never retune after outcomes).

Date: 2026-09-12. Study directory `research/machine-intelligence-morphogenesis-v1` (M).

Source: protected K5 V7, LUNARC job 3605249, beacon round 32138625, 256/256 tasks OK, aggregate
`microscopes/results/k5_bh_v7/K5_BH_AGGREGATE_V7.json`, terminal `K5_BH_V7_CONTAINS_RED`. Six lanes GREEN on
all values. `C_FEATURE_LEARNING` THEORY_RED, `E_CONTROL` INCONCLUSIVE. **Those two protected verdicts stay
authoritative; nothing below reopens them.**

Diagnostic arithmetic on the protected receipts and the analytic world computation were run on billy-old
(`diag_k5rev.py`, receipts read only, experiment core not executed). Numbers are quoted to the precision of the
receipts.

---

## 1. C_FEATURE_LEARNING (RV-377-170)

### 1.1 What the receipts say

The lane pits a fixed-feature logistic readout on `(1, x0, x1)` against a trainable 6-unit tanh MLP under the
frozen development `D7` = 320 full-batch steps, lr 0.25, init U(-0.15, 0.15). The world labels
`y = 1[x0 + 0.4 x1 + 2.5 s x0 x1 >= 0]` on the unit square, `s` = `nonlinear_signal`. Frozen prices give

```
fixed_objective     = 100 * fixed_test_error     + 1.16
trainable_objective = 100 * trainable_test_error + 2.10 + 0.01 * feature_movement
```

so the trainable realization must buy a protected-error **gain** of more than
`delta(s) = 0.94 + 0.01 * movement` percentage points (pp) to win. The receipts give, per cell (8 replicates):

| s | linear-Bayes floor (analytic) | mean fixed test err | mean trainable test err | mean trainable *train* err | mean gain (pp) | replicates with gain > delta | fixed adm. | trainable adm. | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 0.00 | 0.0000 | 0.0167 | 0.0091 | 0.0047 | +0.76 | 1/8 | 8 | 8 | GREEN |
| 0.25 | 0.0446 | 0.0478 | 0.0497 | 0.0410 | -0.19 | 0/8 | 8 | 8 | GREEN |
| **0.60** | **0.0911** | **0.0907** | **0.0916** | **0.0910** | **-0.09** | **0/8** | 8 | 8 | **THEORY_RED** |
| 1.00 | 0.1699 | 0.1898 | 0.1771 | 0.1641 | +1.27 | 4/8 | 2 | 4 | INCONCLUSIVE |

At `s = 0.6` the winner on all 8 replicates was `FIXED_FEATURE`; the mean margin was -1.07 (range -0.80 to
-1.36). Both realizations were admissible on 8/8 replicates. At `s = 1.0`, 4 replicates had the predicted
winner `TRAINABLE_FEATURE` inadmissible (trainable test error 0.1813, 0.1806, 0.2006, 0.1819 against the 0.18
bar), 2 agreed, 2 disagreed.

### 1.2 Stage-by-stage elimination

- **(c) world generator: not the failure.** The analytic linear-Bayes error floor of the frozen world rises
  monotonically 0 / 0.045 / 0.091 / 0.170 at `s` = 0 / 0.25 / 0.6 / 1.0, and the trained fixed readout sits on
  it (0.0907 measured against 0.0911 at 0.6). The nonlinear residual outside the fixed feature span is realised
  exactly as intended (FL-1 obstruction is real: 9.1 pp of irreducible fixed-feature error at 0.6).
- **(b) admissibility constitution: not the failure at 0.6.** Both realizations admissible on 8/8. At 1.0 the
  constitution correctly reports what happened: the predicted winner failed the frozen quality bar in 4/8.
- **(d) scoring: not the failure.** The price surplus (0.98) is the frozen lifecycle price, and the V1 rule plus
  V2 addendum were applied as written; no arithmetic error was found when the margins were recomputed from the
  receipt observables.
- **(a) the frozen prediction: the failure.** The scoring freeze's grid prediction (`0.6 -> TRAINABLE_FEATURE`)
  was derived from the residual-magnitude reading of the feature-learning law alone: the fixed span cannot
  represent the target, so the trainable route must win. The phase freeze's own sentence continues "*trainable
  realization may pass only if development reaches it within budget*", and
  `GMI_FEATURE_LEARNING_NECESSITY_THEOREM_V1.md` (FL-1/FL-2) and `GMI_NEURAL_LINEARIZATION_REGIME_THEOREM_V1.md`
  §5 both state that the obstruction is a necessity theorem for feature change, "*not a claim that the neural
  mechanism will discover the required feature*". The receipts show exactly that clause biting: under `D7` the
  developed MLP's **training** error at 0.6 is 0.0910, the linear-Bayes floor itself. The trainable realization
  reached the fixed-feature solution and nothing beyond it in 320 steps; its gain over the fixed route is zero
  within noise (-0.09 pp against the 0.98 pp it must buy). At 1.0 the interaction term is strong enough that
  `D7` begins to leave the floor (training error 0.164 against floor 0.170; gain +1.27 pp, 4/8 above the
  surplus) but both realizations now straddle the 0.18 admissibility bar.

**One-stage attribution: THEORY (prediction). The crossover was located by residual magnitude without the
reachability term the theory itself carries.** Neither the world, the constitution, nor the scoring contributed.

### 1.3 Minimal justified successor (corrected law)

Keep the world, the development budget `D7`, the prices and the scoring untouched (the experiment core is
unchanged). Replace only the prediction with the reachability-conditioned law:

> `TRAINABLE_FEATURE` wins at `s` iff both realizations are admissible **and** the gain of the developed
> trainable realization exceeds `delta(s)`. Under `D7` the gain is zero within noise for `s <= 0.6` and 1.27 pp
> at `s = 1.0`; the crossover therefore lies in `(0.85, 1.0]` and coincides with the fixed-feature admissibility
> cliff (floor 0.170 at 1.0, measured fixed error 0.19 > 0.18 on 6/8). **Under `D7` no `s` in `[0, 1.2]` yields a
> cell in which `TRAINABLE_FEATURE` is both admissible and winning on >= 6/8 replicates.**

The gain interpolation between the two protected anchors (-0.09 pp at 0.6, +1.27 pp at 1.0) is the only
empirically fitted element and is declared as such; the floor is analytic; the surplus is exact from the prices.

Fresh grid, none of whose values were ever run: `s in {0.40, 0.50, 0.75, 0.85}` (lane cells) and a probe at
`s = 1.2` outside the lane verdict. Frozen predictions (`GMI_K5_BH_REVIVAL_PLAN_V8.json`):

- **P-C1.** `FIXED_FEATURE` wins on >= 6/8 replicates with positive mean margin in every lane cell (lane GREEN).
- **P-C2.** Mean gain at 0.40 and 0.50 lies in [-0.6, +0.6] pp (the `D7` realization stays on the floor).
- **P-C3.** Mean gain at 0.75 lies in [-0.3, 1.0] pp and at 0.85 in [-0.1, 1.2] pp (below `delta`).
- **P-C4.** Per cell, mean fixed test error minus the analytic floor lies in [-0.01, +0.03] (world check).
- **P-C5..C7 (probe 1.2, not in the verdict).** Fixed inadmissible on >= 6/8; trainable admissible on <= 3/8;
  mean gain in [1.0, 3.0] pp.

Falsifiers: any lane cell with `TRAINABLE_FEATURE` winning on >= 6/8 (the trainable route escapes the floor
earlier than the corrected law says); P-C2 or P-C3 outside band. **Kill condition:** a trainable-wins cell at
0.75 or 0.85, or the probe showing the trainable realization admissible on >= 6/8 at 1.2: the reachability
reading of `D7` is then dead and the crossover must be re-derived with development budget as an explicit axis.

Boundary declared in advance: the successor cannot exhibit a `TRAINABLE_FEATURE`-wins regime, because under the
frozen `D7` none exists inside the admissible range. Exhibiting one requires a development-budget axis, which
means a new experiment core (out of scope for RV-377-170; named for RV-377-172).

---

## 2. E_CONTROL (RV-377-171)

### 2.1 What the receipts say

Per goal, the direct route runs 800 Q-learning steps (cost 805 per goal); the model route spends 500 samples
once, then value-iterates per goal (1600 planning ops per goal, plus 50). Costs are deterministic:

```
direct_cost = 805 * r          model_cost = 550 + 1600 * r
```

so `MODEL` is never the cheaper route at any `r >= 1`: **the frozen world realises no cost crossover** (planning
per goal costs more than direct development per goal, and nothing is amortised across goals except the 500
samples). This is a world-design limitation recorded here; it is not the cause of the INCONCLUSIVE.

| r | mean direct return | sd | DIRECT admissible | MODEL admissible | inadmissible replicates (direct return) | verdict |
|---|---|---|---|---|---|---|
| 1 | 0.8013 | 0.182 | 5/8 | 8/8 | reps 3, 6, 7 (0.5842, 0.5467, 0.5964) | INCONCLUSIVE |
| 2 | 0.8752 | 0.106 | 6/8 | 8/8 | reps 0, 5 (0.7934, 0.6787) | INCONCLUSIVE |
| 8 | 0.8787 | 0.067 | 7/8 | 8/8 | rep 2 (0.7198) | INCONCLUSIVE |
| 32 | 0.8554 | 0.020 | 8/8 | 8/8 | none | GREEN |

Every inadmissible replicate is a **quality-threshold** failure (direct normalized return below 0.80), none is
structural; MODEL was admissible on 32/32 (minimum 0.986). On the 26 replicates where DIRECT was admissible,
the prediction `DIRECT` held **26/26**, with margins +1345 / +2140 / +6910 / +25990 exactly as the cost
inequality gives.

### 2.2 Stage-by-stage elimination

- **World generator:** not the cause. The direct route's quality is stochastic by design (finite Q-learning per
  goal); the model route is deterministic given the 500 samples.
- **Scoring / constitution:** not the cause. The V2 addendum did precisely what it was frozen to do: a
  prediction naming an inadmissible realization cannot count as agreement.
- **Theory of the cost crossover:** held on every admissible replicate (26/26).
- **The frozen prediction: the cause.** The predictor names `DIRECT` from the cost inequality plus the model
  error bound and never asks whether `DIRECT` will clear the frozen quality bar, although the phase freeze's
  quality rule ("*an inadmissible low-cost realization cannot win*") is part of the same contract. The direct
  route's per-goal normalized return, pooled over the 344 protected goals, has mean 0.859 and sd 0.161, so
  `P(DIRECT admissible at reuse r) = Phi((0.859 - 0.80) / (0.161 / sqrt r))` = 0.64, 0.70, 0.85, 0.98 at
  `r` = 1, 2, 8, 32, expecting 5.2, 5.6, 6.8, 7.9 admissible replicates of 8; observed 5, 6, 7, 8.

**One-stage attribution: THEORY (prediction). The predictor omitted the admissibility term for the stochastic
route.** The INCONCLUSIVE is the scorer correctly refusing to credit a prediction whose named winner failed the
quality bar the theory was obliged to predict.

### 2.3 Minimal justified successor (admissibility-conditioned prediction)

Keep world, prices, scoring and core unchanged. The prediction now applies the admissibility rule before naming
a winner: `DIRECT` is predicted only where all eight replicates clear the bar with probability >= 0.95 under
the concentration law above, i.e. `r >= 48` (`P(all 8) = 0.958, 0.987, 0.999, 1.000` at 48, 64, 96, 128).

Fresh grid, none of whose values were ever run: `r in {48, 64, 96, 128}` (lane cells), probe `r = 4`.

- **P-E1.** `DIRECT` admissible on 8/8 and winning on 8/8 in every lane cell (lane GREEN).
- **P-E2.** `MODEL` admissible on 8/8 in every cell (minimum model return >= 0.98).
- **P-E3.** Total predicted-inadmissible replicates across the 32 lane replicates is 0 or 1 (law: 0.05 expected).
- **P-E4..E6 (probe r = 4, not in the verdict).** DIRECT inadmissible on 0 to 4 of 8 (law: 1.84 expected); mean
  direct return in [0.77, 0.95]; MODEL admissible 8/8.
- **P-E7 (kill).** Two or more predicted-inadmissible replicates among the 32 lane replicates (law probability
  < 0.002) kill the concentration law.

Boundary declared in advance: the successor tests only the `DIRECT` side; the `MODEL`-wins side of the phase law
cannot be realised by this world at any `r`, and a world with amortised planning is a new core (named for
RV-377-173 if needed, otherwise recorded as a scope boundary).

---

## 3. Execution plan

1. Development tier on billy-old only (`hpc/gmi_k5_bh_run_v8_local.sh`, 80 tasks, <= 2 niced processes),
   receipts under `microscopes/results/k5_bh_v8_dev/`, aggregate
   `K5_BH_REVIVAL_AGGREGATE_V8_DEVELOPMENT.json`. Development results are labelled and never protected.
2. If both lanes are GREEN at development tier: freeze `GMI_K5_BH_EXECUTION_FREEZE_V8.json` (same beacon rule as
   V7, delay 900 s, no reroll), fetch the V8 beacon on billy-laptop only, run the protected V8 on LUNARC
   (`lu2026-2-51`, partition `aurora`), aggregate `K5_BH_REVIVAL_AGGREGATE_V8_PROTECTED.json`.
3. Adjudicate in §4 (append-only); ledger rows RV-377-170 and RV-377-171.

Commit of this file and of `GMI_K5_BH_REVIVAL_PLAN_V8.json` precedes every V8 execution.

---

## 4. Adjudication (append-only)

### 4.1 Development tier (billy-old, 80/80, not protected)

Aggregate `microscopes/results/k5_bh_v8_dev/K5_BH_REVIVAL_AGGREGATE_V8_DEVELOPMENT.json`, terminal
`K5_BH_V8_DEVELOPMENT_GREEN`, 0 structural errors. Seeds derive from the plan file hash (development rule); the
receipts' `git_commit_sha` is `UNKNOWN` because the billy-old lane directory is an rsync copy, not a checkout.

| lane cell | predicted | agree | pred.-inadmissible | mean margin | verdict | auxiliary |
|---|---|---|---|---|---|---|
| C 0.40 | FIXED_FEATURE | 8/8 | 0 | +0.745 | GREEN | fixed err 0.0803 (floor 0.0751, P-C4 ok); gain +0.24 pp (P-C2 ok) |
| C 0.50 | FIXED_FEATURE | 8/8 | 0 | +1.001 | GREEN | fixed err 0.0898 (floor 0.0850); gain -0.02 pp (P-C2 ok) |
| C 0.75 | FIXED_FEATURE | 8/8 | 0 | +0.823 | GREEN | fixed err 0.1245 (floor 0.1207); gain +0.16 pp (P-C3 ok) |
| C 0.85 | FIXED_FEATURE | 7/8 | 0 | +0.658 | GREEN | fixed err 0.1502 (floor 0.1424); gain +0.32 pp, 1/8 above delta (P-C3 ok) |
| E 48 | DIRECT | 8/8 | 0 | +38710 | GREEN | direct admissible 8/8, mean return 0.8513 |
| E 64 | DIRECT | 8/8 | 0 | +51430 | GREEN | 8/8, 0.8691 |
| E 96 | DIRECT | 8/8 | 0 | +76870 | GREEN | 8/8, 0.8660 |
| E 128 | DIRECT | 8/8 | 0 | +102310 | GREEN | 8/8, 0.8597 |

Probes: `s = 1.2`: fixed inadmissible 8/8 (P-C5), trainable admissible 0/8 (P-C6), mean gain +1.99 pp (P-C7;
law extrapolation 1.95), observed NONE 8/8. `r = 4`: DIRECT inadmissible 3/8 (P-E4; law 1.84), mean direct return
0.8045 (P-E5), MODEL admissible 8/8 (P-E6). Kill P-E7: lane inadmissible total 0 (not triggered).

**P-C1..C7 and P-E1..E7 all hold at development tier.** Lane verdicts GREEN/GREEN. This licenses the protected
V8 tier (`GMI_K5_BH_EXECUTION_FREEZE_V8.json`, commit `c9f36e5d`); nothing in the plan was changed after the
development outcome.

### 4.2 Protected tier (LUNARC, job 3605817, beacon round 32144246, 80/80)

Execution freeze `GMI_K5_BH_EXECUTION_FREEZE_V8.json` at commit `c9f36e5d` (unix 1789235202); beacon
`GMI_K5_BH_PUBLIC_BEACON_V8.json` acquired on billy-laptop at round 32144246 (t = 1789236102, ct + 900 s exactly),
randomness `5b90aa68…7ba08d`, no reroll. Submitter, task and aggregate all verified the contract through
`hpc/gmi_beacon_verify.py` against the clone at commit `8701cba8`; every receipt carries round 32144246; the
aggregate's six freeze hashes match the worktree files. Partition `aurora`, array `0-79%80`, 00:10:00 / 512M,
all 80 tasks COMPLETED (max wall 0.79 s). Aggregate `microscopes/results/k5_bh_v8/K5_BH_REVIVAL_AGGREGATE_V8_PROTECTED.json`,
terminal **`K5_BH_V8_PROTECTED_GREEN`**, 0 structural errors.

| lane cell | predicted | agree | pred.-inadmissible | mean margin | verdict | auxiliary |
|---|---|---|---|---|---|---|
| C 0.40 | FIXED_FEATURE | 8/8 | 0 | +1.011 | GREEN | fixed err 0.0753 (floor 0.0751, P-C4 ok); gain -0.02 pp (P-C2 ok) |
| C 0.50 | FIXED_FEATURE | 8/8 | 0 | +0.977 | GREEN | fixed err 0.0798 (floor 0.0850); gain +0.01 pp (P-C2 ok) |
| C 0.75 | FIXED_FEATURE | 7/8 | 0 | +0.504 | GREEN | fixed err 0.1286 (floor 0.1207); gain +0.48 pp, 1/8 above delta (P-C3 ok) |
| C 0.85 | FIXED_FEATURE | 6/8 | 0 | +0.235 | GREEN | fixed err 0.1549 (floor 0.1424); gain +0.74 pp, 2/8 above delta (P-C3 ok) |
| E 48 | DIRECT | 8/8 | 0 | +38710 | GREEN | direct admissible 8/8, mean return 0.8735 |
| E 64 | DIRECT | 8/8 | 0 | +51430 | GREEN | 8/8, 0.8616 |
| E 96 | DIRECT | 8/8 | 0 | +76870 | GREEN | 8/8, 0.8603 |
| E 128 | DIRECT | 8/8 | 0 | +102310 | GREEN | 8/8, 0.8633 |

Probes: `s = 1.2`: fixed inadmissible 8/8 (P-C5), trainable admissible 0/8 (P-C6), mean gain +2.03 pp (P-C7),
observed NONE 8/8. `r = 4`: DIRECT inadmissible 1/8 (P-E4), mean direct return 0.8733 (P-E5), MODEL admissible
8/8 (P-E6). Kill P-E7: lane inadmissible total 0.

**All fourteen numbered predictions hold at protected tier; both lanes GREEN.** The C 0.85 cell sits at the
rule's edge (6/8, margin +0.24, gain 0.74 pp against delta 0.98), which is where the corrected law placed the
crossover ("in (0.85, 1.0]"); a fresh cell above 0.85 is expected to flip and is *not* claimed GREEN.

Deviation (operational, not scientific): the sbatch's `module load Python/3.11.5` did not take effect inside the
array tasks; receipts record Python 3.9.25, the same interpreter the protected V7 run used. The core is pure
stdlib and the development tier (3.11.16) and protected tier agree on every verdict.

### 4.3 Adjudication

- **RV-377-170 (C_FEATURE_LEARNING):** `C_FEATURE_LEARNING_REVIVED_GREEN_ON_FRESH_GRID_UNDER_REACHABILITY_CONDITIONED_LAW__V7_RED_AT_0_6_STANDS`.
  The protected V7 THEORY_RED at 0.6 remains the authoritative falsification of the residual-magnitude
  prediction. The reachability-conditioned law is GREEN on the FIXED side at both tiers and its probe confirms
  that no trainable-wins regime exists under `D7` inside the admissible range. Boundary: exhibiting a
  trainable-wins regime needs a development-budget axis (new core; RV-377-172 if ever wanted, not required).
- **RV-377-171 (E_CONTROL):** `E_CONTROL_REVIVED_GREEN_ON_FRESH_GRID_UNDER_ADMISSIBILITY_CONDITIONED_PREDICTION__V7_INCONCLUSIVE_AT_1_2_8_STANDS__MODEL_SIDE_UNREALISABLE_IN_FROZEN_WORLD`.
  The protected V7 INCONCLUSIVE at 1/2/8 stands. The admissibility-conditioned predictor is GREEN at both tiers;
  the probe at r = 4 (1/8 and 3/8 inadmissible at the two tiers against 1.84 expected) and the untriggered kill
  condition test the concentration law's content. Boundary: the MODEL side of the phase law is unrealisable in
  this world (planning per goal 1600 ops > direct 805); a world with amortised planning is a new core
  (RV-377-173 if ever wanted, not required).

No second revival iteration (RV-377-172/173) is needed: both successors passed at protected tier, and the
declared boundaries are structural to the frozen core, not failures of the successors.
