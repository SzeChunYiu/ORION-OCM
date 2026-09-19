# FREEZE — gmi-833-ae-ae3-compression-learning-v1

**Committed before any implementation blob of this package exists.** The git
history must show this file's commit strictly preceding the first commit that
introduces `ae3_compression_learning_v1.py`, `independent_code_oracle_v1.py`,
`test_ae3_compression_learning_v1.py`, `RESULT_V1.json`, `MANIFEST_V1.json`,
`AE3_THEOREMS_V1.md`, `PARENT_OWNERSHIP_V1.md`, `CORE.md` or
`ISSUE_833_RECONCILIATION_AE3_COMPRESSION_LEARNING_V1.json`.

- issue: `833`
- issue comment: `5692689542` (Section AE)
- source_main: `349c2e62c4ae01f52cf66f61e4dacdbdfcf10071`
- section map consumed: `research/gmi-833-ae-section-map-v1/AE_SECTION_MAP_V1.md`,
  batching-plan item **1**

## Claim ceiling

```
GMI_833_AE3_COMPRESSION_NOTIONS_SEPARATED_FROM_LEARNING_ON_A_REGISTERED_FINITE_CODING_LANGUAGE_FAMILY
```

## The EXACT rows this tranche may reconcile — and no others

All eight rows under anchor `### AE3 — Compression is not automatically learning`, byte-exact from a live fetch of comment
`5692689542` at `source_main`:

1. `- [ ] Formalize at least three notions separately: lossless description compression, task-relevant lossy compression, and model/generalization compression.`
2. `- [ ] Prove/construct cases where data compresses but the compressed representation is useless for the target task.`
3. `- [ ] Prove/construct cases where a useful predictor is not the shortest description under the chosen coding language.`
4. `- [ ] Distinguish memorization/compression from out-of-sample generalization.`
5. `- [ ] Relate GMI precisely to MDL/Bayesian coding/PAC-Bayes/compression bounds where applicable; subtract parent-owned theorems.`
6. `- [ ] State Kolmogorov-complexity uncomputability boundaries explicitly; forbid claims that GMI computes the true shortest program in general.`
7. `- [ ] Define computable surrogates and quantify their representation-language dependence.`
8. `- [ ] Test whether GMI predictions survive multiple coding languages/universal-machine remints up to the actually justified invariance boundary.`

**No neighboring row is earned here.** In particular this tranche closes no AE4
row, and the coding-language registry it builds is offered to AE4 without
claiming any AE4 result.

## Registered harness (frozen before results)

- Domain `X = {0,1}^3` under the uniform measure; target `Y = f(X)` binary; the
  census is all `256` targets.
- Registered training set `S0 = { x : x2 = 0 }` (4 points); the held-out set is
  its complement.
- A **coding language** is a finite prefix-free program set over the same output
  space, parameterised by four integer code lengths
  `(rule, negated rule, xor of two rules, literal table)` with a registered
  16-rule basis. Kraft feasibility `16*2^-a + 16*2^-b + 256*2^-c + 256*2^-d <= 1`
  is checked exactly with `Fraction`.
  - `L1 = (6,7,11,9)` and `L2 = (5,7,11,10)`, both Kraft-tight.
  - `L3` is a structurally different run-length language, not rule-based.
- Three notions, defined separately and never identified:
  - `A` lossless description compression: `K_L(tab f)`.
  - `B` task-relevant lossy compression: the minimal junta arity attaining
    accuracy `>= tau` on the task.
  - `C` model/generalization compression: the minimal code length of a program
    whose **out-of-sample** accuracy is `>= gamma`.

## Named results this tranche may claim

- `AE3-1` pairwise non-equivalence of `A`, `B`, `C` by exhaustive
  functional-dependence census (all six ordered pairs witnessed).
- `AE3-2` equal compression, opposite task usefulness.
- `AE3-3` a useful predictor that is strictly longer than the shortest
  description consistent with the sample.
- `AE3-4` train-set memorization does not determine out-of-sample accuracy.
- `AE3-5` an exact two-part-MDL / Bayes-MAP crosswalk with an exact
  MDL-selects-the-worse-hypothesis witness.
- `AE3-6` the Kolmogorov uncomputability boundary as a **registered forbidden
  promotion with a machine-checked guard**, never as a computed quantity.
- `AE3-7` exact language dependence of the computable surrogates.
- `AE3-8` the justified invariance boundary: which verdicts survive a sampled
  Kraft-feasible remint family and which require leaving it.

## Forbidden promotions

```
KOLMOGOROV_COMPLEXITY_COMPUTED
GMI_COMPUTES_TRUE_SHORTEST_PROGRAM
UNIVERSAL_MACHINE_INVARIANCE_PROVED
COMPRESSION_IMPLIES_LEARNING
LEARNING_IMPLIES_COMPRESSION
UNBOUNDED_CODING_LANGUAGE_THEOREM
REAL_CORPUS_COMPRESSION_MEASUREMENT
COMPLETE_GMI
```
