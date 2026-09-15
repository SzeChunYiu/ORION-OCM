# GMI #833 — Global-vs-Reachable Morphology Selection Freeze V1

Status: PRE-IMPLEMENTATION FREEZE
Source issue: #874
Master programme: #833
Target checklist row: Section J — `Separate optimal morphology from reachable morphology.`

## Frozen source

- source `main`: `367e14e9296cf79924ce56d89fad34b3769acb5d`
- branch: `research/874-global-vs-reachable-morphology-v1`

All executable checker, hostile tests, result receipt, theorem note, manifest, reconciliation spec, and workflow must postdate this freeze commit.

## Parent authority and subtraction

This tranche does not reclaim developmental reachability or generic constrained/Pareto optimization mathematics.

Exact merged parent objects at freeze:

- foundation receipt: `research/gmi-833-foundation-v1/RESULT_V1.json`, Git blob `c0c574c4ec6e237d5fdafa694eac131399625a70`;
- corrected developmental/lifecycle receipt: `research/gmi-grand-unification-v1/GRAND_GMI_DEVELOPMENTAL_LIFECYCLE_RECEIPT_V2.json`, Git blob `8b7acb21cc21d41e54b23c91a9fca75af5612208`;
- developmental reachability theorem: `research/gmi-grand-unification-v1/DEVELOPMENTAL_REACHABILITY_SELECTION_THEOREM_V1.md`, Git blob `27ecb316987bca886c1fc882a4f8c9e270bba4dc`.

The corrected V2 lifecycle receipt supersedes the historical V1 receipt and is the executable parent authority.

## Frozen theorem target

For a registered finite morphology set `M`, nonempty reachable subset `R ⊆ M`, and an exact scalar minimization objective `f`:

1. `min_M f <= min_R f`.
2. `min_R f = min_M f` iff `R` intersects `Argmin_M f`.
3. Equal optimum values do not imply equal optimizer sets.
4. If `R1 ⊆ R2`, then `min_R2 f <= min_R1 f`.
5. For componentwise minimization, `Pareto(M) ∩ R ⊆ Pareto(R)`, but the reverse inclusion can fail when a dominator is unreachable.
6. The corrected DRS V2 witness is reused only as a concrete parent-bound illustration; full lifecycle Pareto coexistence is not replaced by a deployment-only scalar projection.

## Required hostile controls

Fail closed on empty universes/reachable sets, `R` outside `M`, incomplete or inexact scalar objectives, malformed Pareto profiles, false nested-reachability declarations, tied global optima with only a strict subset reachable, and the false claim `Pareto(R) ⊆ Pareto(M)`.

## Claim ceiling

`GMI_FINITE_GLOBAL_VS_REACHABLE_MORPHOLOGY_SELECTION_SEPARATED_AT_REGISTERED_SCOPE`

Forbidden promotions from this tranche alone:

- `GLOBAL_OPTIMUM_ALWAYS_REACHABLE`
- `REAL_OPTIMIZER_CONVERGENCE`
- `UNIQUE_MORPHOLOGY`
- `PARETO_REACHABLE_FRONTIER_SUBSET_OF_GLOBAL_FRONTIER`
- `UNRESTRICTED_CONTINUOUS_OR_TURING_COMPLETE_OPTIMIZATION`
- `PROSPECTIVE_MORPHOLOGY_TRANSITIONS_PREDICTED`
- `P3_RECOVERY_COMPLETE`
- `COMPLETE_GMI`
