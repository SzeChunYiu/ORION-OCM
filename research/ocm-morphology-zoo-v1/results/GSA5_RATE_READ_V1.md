# GSA5_RATE_READ_V1 — why GSA5_surrogate runs at 72k morphologies/cpu-h

Mechanism read on issue #221 (morphology-zoo lane), prompted by the GSAB1
post-fix adaptive batch. The aggregate terminal
`MORPHOLOGY_SEARCH_COST_DOMINATES__SWEEP` is **unchanged** — this read
explains the GSA5 residual inside it; it re-litigates nothing.

- data: `lunarc:~/zoo221/gs` batch **GSAB1** (repair of the lane-arm sampler
  wiring defect), 30/30 tasks COMPLETED, jobs 3587721–3587750,
  freeze sha `4dd79f8e…`, code-digest drift vs freeze **false**
- aggregate arm stats are GSAB1 seeds only (the defective pre-fix `GSA_*`
  dispositions remain retained as scored artifacts)
- twin: `results/GSA5_RATE_READ_V1.json`

## Question

Same lane, same per-seed budget (45000 T0 evals, n0=729, eta=3, insurance
0.15, seeds 0–5): GSA2_hetero 354 046 vs GSA5_surrogate 72 150
morphologies/cpu-h — **4.91× apart**, with the report flagging "same lane,
surrogate ranking" as the distinguishing variable. Which ONE stage owns it?

## One-stage attribution

**The promotion-and-parent-allocation ranking stage** (GSA5
`rank=surrogate_allocation` vs GSA2 `rank=novelty`). The rate ratio
decomposes exactly into two factors, both owned by that stage:

| factor | value | definition |
|---|---|---|
| distinct-phenotype yield | **2.267×** | mean distinct T2-viable phenotypes/seed: 5062.7 (GSA2) / 2233.3 (GSA5) |
| CPU per seed | **2.171×** | mean cpu-s/seed: 111.257 (GSA5) / 51.258 (GSA2) |
| **product = rate ratio** | **4.92 ≈ 4.91** | 354 046 / 72 150 |

### Stage 1 — distinct-yield collapse (2.267×), the proving numbers

Per seed both arms run **identical tier-eval counts** (s0: T0 45 000,
T1 17 123, T2 5802 — matched in every seed) and both retain **5802 T2
survivors**, because the SH schedule fixes promotion counts and the T1/T2
gates pass 100.0% in both arms. The entire yield difference is
**duplication among survivors**:

| s0 | GSA2 (novelty) | GSA5 (surrogate) |
|---|---|---|
| distinct phenotypes / 5802 survivors | 5075 (87.5%) | 2086 (36.0%) |
| duplicates | 727 | 3716 |
| top phenotype multiplicity | 17× | **138×** |
| survivors in phenotypes seen ≥3× | 10.5% | **65.9%** |

Mechanism: `allocation_score = p_viable × max(0, predicted_t1_score)` is a
pure function of the ~120-dim grammar one-hot feature vector
(`search/surrogate_allocate.py: genome_feature_vector`). It cannot
distinguish genomes sharing a feature vector, so it re-promotes the
incumbent high-scoring cells; the parent-pool refresh
(`search/successive_halving.py:230-233`) sorts parents by the **same**
`rank_fn`, and 80% of each cohort is mutation/crossover of those parents —
the collapse is self-reinforcing. Novelty ranking diversifies promotions
AND parents; expected-value ranking concentrates both. This is real
structure (exploitation-collapse under a phenotype-blind rank), not a
wiring defect.

### Stage 2 — CPU overhead (2.171×)

+60.0 cpu-s/seed of pure ranking machinery on top of byte-matched
real-eval work: 62 fresh `EnsembleSurrogate` retrains/seed (2 sklearn
HistGradientBoosting fits each, on the round-local 531 T0 / 204 T1
records) plus ~750 single-row sklearn predicts/round in `rank_prepare`
(≈0.97 s/round; GSA5 per-round cpu 1.75–1.91 s vs ~0.8 s for GSA2, flat
across rounds).

## Exonerated stages (with numbers)

- **Lane composition — controlled**: GSAB1 manifest pins GSA5
  `lane_weights {"hetero": 1.0}`, identical to GSA2_hetero; same seeded
  `weighted_sampler`. (The earlier mis-wiring — sampler object evaluated
  instead of genomes — was named by worker N, repaired, retained.)
- **Viability funnel — exonerated**: T0 viable rate 74.84% (GSA2) vs
  74.22% (GSA5); T1 and T2 pass rates 1.0000 in both arms; identical
  per-seed tier-eval counts. The round-0 fresh-draw 2.2–16.3% viability
  range and ~70% parent-pool-mutation rise are shared by both arms.
- **Evaluation cost per genome — exonerated for the eval tiers**: the
  delta is ranking machinery, not real evaluation.

## Defect named (worker-N style): `GSA5_HOLDOUT_MAE_NAN`

`search/surrogate_allocate.py:_StumpTree.predict` can return the
internal-node `float("nan")` leaf marker set by `_build` (the depth guard
`depth < GS_SUR_DEPTH` exits the walk on a split node whose leaf value is
the marker). `train_t1`'s holdout MAE is computed with these builtin
stumps even when `impl="sklearn"`, so `holdout_mae_t1` came out **NaN in
5/6 GSA5 seeds and a degenerate 0.0 in s2** — the surrogate's only
validation statistic was never usable on-host; ranking quality went
unmeasured. The ranking itself is unaffected in the sklearn path (stumps
are used only for the holdout MAE).

Not defects: GSA5's `lane_weights` are correctly pinned; round-local
surrogate training (`n_train_t0=531`, never cumulative) is a frozen design
choice that caps the surrogate at ≤729 examples/round — a plausible
revival lever, not wiring.

## Implication (levers, not executed here)

1. novelty-gated surrogate allocation (surrogate proposes, novelty
   disposes) to break duplicate promotion;
2. batch-row predicts + cumulative-round training to cut the 2.17× CPU
   factor;
3. dedup-by-`phenotype_digest` at promotion so T2 budget cannot be
   re-spent on already-survived phenotypes.
