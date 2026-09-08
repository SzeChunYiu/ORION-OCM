# PR #150 factorization survival protocol — protected V2

Status: **FROZEN BEFORE V2 PROTECTED OUTCOME ACCESS**

V2 inherits every world definition, learner-visible-information restriction, metric, hypothesis card, falsifier and claim ceiling from `PROTECTED_PROTOCOL_V1.md` except the explicit changes below. V1 is preserved and is `CANNOT_CHECK_PROTOCOL_IMPLEMENTATION_MISMATCH`; its seeds are burned.

## Why V2 exists

A code-vs-protocol audit after V1 execution started, but before any V1 result was produced or read, found that V1 promised the strongest incremental symbolic parent exact episodic memory while the implementation retained only its learned factor state. V1 was aborted rather than repaired after exposure.

## New protected seeds

Development seeds remain `1..8` and are exploratory only.

V2 protected seeds are **`9101..9140`**. They use the same SHA256-separated stream construction with prefix `E150-V2|<seed>|<stream>`. No V1 protected seed is reused.

## Strengthened parent frontier

V2 replaces the single symbolic parent comparison with a symbolic parent frontier:

1. `symbolic_incremental_memory_parent`: exact episodic memory + learned minimal-support antichains + local contradiction-triggered refit. Episodic bytes are disclosed in `state_bytes`; it may use current evidence for a drifted refit while retaining prior episodes for diagnosis/audit.
2. `symbolic_compact_parent`: learned minimal-support antichains + local contradiction-triggered refit, but no duplicate relevance cache and no forced episodic archive. This prevents an OCM residual from being manufactured by charging a comparator for unnecessary memory.
3. `symbolic_lazy_parent`, `global_refit_parent`, `evolutionary_parent`, `surrogate_parent` remain as in V1.

`reset_factor_ablation` deletes learned factor state every generation but retains the same episode stream in an archive, so rediscovery is separated from information loss. It must not be used as the strongest parent.

The strongest adaptive symbolic parent is the **Pareto frontier of (1) and (2)**, never an outcome-selected weakened member.

## V2 decision rule

An OCM-specific residual is impossible if either symbolic frontier parent weakly dominates `factor_local` at matched capability on the disclosed resource vector. In particular, terminal is `PARENT_SUFFICIENT` if a symbolic parent has:

- held-out accuracy no worse by more than 0.01,
- support F1 no worse by more than 0.01 where identifiable,
- effective coupling <= factor_local,
- discovery + maintenance primitive work <= factor_local,
- state bytes <= factor_local,

with at least one strict resource improvement on >= 30/40 sparse/stable seeds.

For a positive OCM-specific residual, `factor_local` must survive **both** symbolic frontier parents and the remaining adaptive parents, satisfy V1's sparse/stable mechanism criteria, pass the state-deletion causal ablation, expose dense/drift boundaries, and beat the same M11 lifecycle driven by the strongest parent. Beating global refit/evolution alone is insufficient.

## Implementation audit gate

Before V2 protected execution, a deterministic development audit must assert:

- `Episode` exposes only observations and correct actions;
- `symbolic_incremental_memory_parent` retains exact past episodes;
- `symbolic_compact_parent` has the same factor grammar/local invalidation without the episodic archive or relevance cache;
- `factor_local` and both symbolic parents use the same candidate grammar and observation stream;
- the parent-survival summary compares factor_local against both symbolic frontier parents;
- no V2 protected seed appears in any development artifact.

Any mismatch discovered after V2 starts burns V2 and requires V3 with new protected seeds.

## Neural/Transformer comparator

As in V1, a matched neural/Transformer arm remains `CANNOT_CHECK_NEURAL_MATCHED` unless an already dependency-pinned implementation can be run without adding an unmatched pretrained information source. No weak toy neural comparator may be used to promote OCM.

## Claim ceiling

Even if sparse/stable structure is recovered and lifetime search is amortized, the maximum claim remains: **bounded learned monotone causal-factorization benefit in an identifiable sparse regime**. If `symbolic_compact_parent` matches it, the mechanism is parent-owned and the PR #150 OCM-specific theory is narrowed to a general factorization theorem rather than supported as an OCM residual.
