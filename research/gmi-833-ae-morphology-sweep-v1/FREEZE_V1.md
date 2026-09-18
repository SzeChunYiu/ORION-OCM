# FREEZE — gmi-833-ae-morphology-sweep-v1

**Committed before any implementation blob of this package exists.** The git
history must show this file's commit strictly preceding the first commit that
introduces `morphology_sweep_v1.py`, `independent_sweep_oracle_v1.py`,
`test_morphology_sweep_v1.py`, `RESULT_V1.json`, `MANIFEST_V1.json`,
`SWEEP_THEOREMS_V1.md`, `PARENT_OWNERSHIP_V1.md`, `CORE.md` or
`ISSUE_833_RECONCILIATION_AE_MORPHOLOGY_SWEEP_V1.json`.

- issue: `833`
- issue comment: `5692689542` (Section AE)
- source_main: `349c2e62c4ae01f52cf66f61e4dacdbdfcf10071`
- section map consumed: `research/gmi-833-ae-section-map-v1/AE_SECTION_MAP_V1.md`
  (this tranche is its batching-plan item **12**, the Tier-2 sweep)

## Claim ceiling

```
GMI_833_AE_MORPHOLOGY_SELECTION_PREDICTOR_COMPARISON_AT_REGISTERED_FINITE_SCOPE
```

## The EXACT rows this tranche may reconcile — and no others

Four rows, one per subsection, byte-exact from a live fetch of comment
`5692689542` at `source_main`:

1. anchor `### AE5 — Predictive-state / causal-state unification audit`
   `- [ ] Determine which quantity, if any, predicts morphology/resource cost under GMI.`
2. anchor `### AE6 — Manifold hypothesis and geometric structure`
   `- [ ] Derive when manifold assumptions fail and another morphology should be selected.`
3. anchor `### AE10 — Resource-bounded usable information`
   `- [ ] Determine whether GMI morphology selection is better predicted by raw information, usable information, or a vector of resource-conditioned sufficient statistics.`
4. anchor `### AE13 — Causality and intervention`
   `- [ ] Test whether causal structure changes selected morphology relative to observational prediction alone.`

**No neighboring row is earned here.** In particular this tranche does NOT
close any other AE5, AE6, AE10 or AE13 row, does not touch AE6's prospective
real-dataset row (Tier 3), and does not close AE13's five proof rows.

## Correction to the section map, declared before implementation

The section map asserts these four rows need "**no new mathematics**, only
registered morphology-selection receipts pinned by blob sha". That assertion is
**wrong** and this freeze records the correction before any result exists.

The morphology receipts on `main`
(`gmi-833-morphology-selection-v1`, `gmi-833-morphology-selection-schema-v1`,
`gmi-833-global-vs-reachable-morphology-v1`,
`gmi-833-finite-morphology-metrics-v1`, `gmi-833-finite-candidate-space-v1`)
contain **no information-theoretic quantity whatsoever** — no entropy, no
mutual information, no achievability measure. Their selection correspondence
takes an *already given* active candidate set and a resource vector. They
therefore cannot, on their own, answer "which quantity predicts the selected
morphology", because nothing in them maps a world to an active set.

The residual contribution of this tranche is exactly that missing map: a
**viability bridge** from an exact achievability quantity to the parent's
active set. It is small, but it is new, and it is declared here rather than
discovered afterwards.

## Registered harness (frozen before results)

- Domain `X = {0,1}^3` under the uniform measure; target `Y` binary.
- Candidate morphology set `M` — five architecture-name-free rule classes, each
  with a nonnegative integer resource vector `r(m) = (fan_in, depth, memory_cells)`:
  `m0` constants `(0,0,1)`; `m1` arity-1 juntas `(1,1,2)`; `m2` arity-2 juntas
  `(2,2,4)`; `m4` GF(2)-affine forms `(3,1,4)`; `m3` arity-3 juntas / full table
  `(3,3,8)`.
- `acc(m, W)` = max over `h` in the class of `Pr_W[h(X) = Y]`, exact `Fraction`.
- Viability bridge (**the residual**): `active(W, tau) = { m : acc(m,W) >= tau }`.
- Selection = the parent choice correspondence applied to `active(W, tau)`:
  `NO_VIABLE_MORPHOLOGY` when empty; otherwise the **full** scalar argmin set
  under a frozen strictly-positive price `w`, with no fabricated tie-break, and
  the raw Pareto frontier reported alongside.
- Frozen prices `w_A = (1,1,1)` and `w_B = (1,3,1)`; frozen threshold
  `tau = 3/4` with the phase boundary in `tau` derived exactly.
- World census: all `256` deterministic worlds `Y = f(X)` on `{0,1}^3` under
  uniform `X`, plus the registered causal fixtures.

## Named results this tranche may claim

- `SWEEP-1` raw Shannon information does not determine the selected morphology
  (collision census over the 256-world census).
- `SWEEP-2` single-budget usable information does not determine it either.
- `SWEEP-3` the resource-conditioned achievability vector does determine it,
  non-vacuously (strictly coarser than the world, strictly finer than either
  scalar).
- `SWEEP-4` exact `tau` phase boundary at which a locality-exploiting
  morphology is displaced by a non-local one when the locality assumption fails.
- `SWEEP-5` two Markov-equivalent worlds with identical observational joints,
  identical observational selection, and **different** interventional selection.
- `SWEEP-6` the AE5 scalar family (predictive-state cardinality, GF(2)
  predictive rank, causal-state entropy at uniform support, registered
  description length) each fails the same functional-dependence test.

## Forbidden promotions

```
UNIVERSAL_MORPHOLOGY_SELECTION_LAW
CONTINUOUS_OR_UNBOUNDED_MORPHOLOGY_SPACE_THEOREM
REAL_SYSTEM_MORPHOLOGY_VALIDATION
REAL_DATASET_INTRINSIC_STRUCTURE_TEST
HARDWARE_ENERGY_MEASUREMENT
TRAINING_TIME_REPRESENTATION_MEASUREMENT
KOLMOGOROV_COMPLEXITY_COMPUTED
CAUSAL_DISCOVERY_FROM_OBSERVATION_ALONE
COMPLETE_GMI
```

## Instrument-blocked rows explicitly NOT touched

AE6's `Prospectively test intrinsic-structure -> morphology transitions on
synthetic and real datasets.` requires a real-dataset programme and stays OPEN.
