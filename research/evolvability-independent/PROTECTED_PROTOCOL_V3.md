# PR #150 factorization survival protocol — protected V3

Status: **FROZEN BEFORE V3 PROTECTED OUTCOME ACCESS**

V1 and V2 are preserved as `CANNOT_CHECK_PROTOCOL_IMPLEMENTATION_MISMATCH`; their protected seeds are burned. V3 inherits the scientific questions, worlds, no-leakage rule, 8-generation lifetime, 96 train / 256 fresh evaluation episodes per generation, 12 observable Boolean coordinates, four output families, sparse/stable, dense and drift regimes, bounded monotone DNF grammar, claim ceilings and negative-terminal discipline from V1/V2 except where explicitly replaced below.

## Protected custody

- development seeds: `1..8` only;
- V3 protected seeds: **`9301..9340`**;
- RNG streams: SHA256 prefix `E150-V3|<seed>|<stream>` with separate hidden-structure, train, evaluation, drift and evolutionary streams;
- V1/V2 protected seeds are never reused;
- learner-visible episode fields are exactly `x` and `correct_actions`;
- task ID, regime, generator seed, hidden supports, hidden cause, donor identity and routing key remain evaluator-only.

No V3 protected seed may be run before the V3 source audit and the branch qualification suite pass.

## Internal adversarial review roles

- **Causal/identifiability reviewer:** audits alternative-support identifiability and hidden-label leakage.
- **Online/meta-learning reviewer:** strengthens symbolic, lazy, evolutionary and learned-surrogate parents and audits drift.
- **OCM/M11 systems reviewer:** checks diagnose → minimum change → pre-outcome receipt → shadow → external adoption → restart → fresh reuse.
- **Publication-methods reviewer:** owns protected custody, vector accounting, abort rules and claim ceilings.

A defect found after protected execution starts burns V3; no in-place protected repair is allowed.

# Hypothesis cards

## E150-A — reusable method/factor discovery without task identity

**THEORY QUESTION** Can reusable sparse methods be discovered from heterogeneous episodes without task/family identity or routing-key leakage?

**PREDICTION** In sparse/stable identifiable worlds, minimal reusable clauses are recovered and future generations stop paying repeated induction work unless contradicted.

**STRONGEST PARENT** `symbolic_compact_parent`: same observable episodes, same bounded grammar, same exact antichain/MDL learner, same contradiction-triggered local refit, but no duplicate relevance cache. `symbolic_incremental_memory_parent` additionally retains the exact episode archive.

**RED COUNTEREXAMPLE** Either symbolic frontier parent matches capability/structure/locality and is componentwise no more expensive.

**MECHANISM** Recover minimal monotone alternative-support clauses from positive/negative episodes and persist them across generations.

**CAUSAL ABLATION** `reset_factor_ablation` deletes learned factors every generation while retaining the episode archive.

**RESULT** Protected only; no development result is promotable.

**RESOURCE VECTOR** Full vector below; no scalar collapse.

**FALSIFIER** Sparse/stable support F1 < 0.90 on identifiable supports, no state-deletion cost effect, or strongest parent dominates.

**CLAIM CEILING** Bounded monotone method/factor discovery; never general program synthesis.

## E150-B — higher-order/alternative dependency supports

**THEORY QUESTION** Can all minimal alternative supports be learned rather than receiving a supplied dependency graph or using leave-one-out single-parent attribution?

**PREDICTION** Width-2 alternative supports are identifiable/recoverable under sparse/stable data; width-6 dense supports become data-limited and/or non-identifiable at the frozen episode budget.

**STRONGEST PARENT** Exact symbolic minimal-support learner over the same grammar and observations.

**RED COUNTEREXAMPLE** Parent recovers the same supports; leave-one-out remains incomplete; or dense structure is not identifiable.

**MECHANISM** Enumerate candidate conjunctions present in positives, reject clauses contradicted by negatives, prune supersets, then choose a minimal covering antichain.

**CAUSAL ABLATION** `loo_dependency_ablation`; no supplied graph arm is allowed to count as discovery.

**RESULT** Protected only.

**RESOURCE VECTOR** Support precision/recall/F1 plus induction/validation/resource coordinates.

**FALSIFIER** Sparse identifiable exact-support F1 < 0.90.

**CLAIM CEILING** Identifiable bounded monotone hyperedge/support discovery only.

## E150-C — learned relevance/subspace without routing keys

**THEORY QUESTION** Can a learned factorization yield a useful relevance subspace without a supplied routing key, after maintenance is charged?

**PREDICTION** Relevance equals the union of variables in live learned factors; explicit cache maintenance should help only if it pays for itself relative to deriving relevance from factor state.

**STRONGEST PARENT** `symbolic_compact_parent`, which derives relevance from its learned clauses when needed and carries no separate relevance cache.

**RED COUNTEREXAMPLE** Same relevance quality with lower state/maintenance for the parent.

**MECHANISM** `factor_local` maintains an explicit relevance cache only after a factor refit; every literal read and changed cache entry is charged.

**CAUSAL ABLATION** Remove the relevance cache while retaining identical factors (`symbolic_compact_parent`).

**RESULT** Protected only.

**RESOURCE VECTOR** Relevance precision/recall, maintenance operations, state bytes and all factor-learning costs.

**FALSIFIER** Cache has no causal resource benefit or parent dominates.

**CLAIM CEILING** Relevance-from-factor-state; not autonomous attention.

## E150-D — failure-cause diagnosis with cause hidden

**THEORY QUESTION** Can the minimum sufficient failure layer be inferred without a cause label?

**PREDICTION** Intervention-identifiable cases are solved; observational/interventional aliases return `CANNOT_CHECK`.

**STRONGEST PARENT** Same-information TMS/nogood intervention table.

**RED COUNTEREXAMPLE** Parent matches or OCM guesses an alias.

**MECHANISM** Existing M11 ablation-based diagnosis; hidden cause stays evaluator-only.

**CAUSAL ABLATION** Remove restoring intervention evidence.

**RESULT** Governed separately by frozen `HIDDEN_CAUSE_PROTOCOL_HC1.md`; no V3 result may overwrite that lane.

**RESOURCE VECTOR** `[identifiable_accuracy, alias_cannot_check_rate, interventions, diagnosis_state_bytes, false_jumps]`.

**FALSIFIER** Any wrong minimum, alias guess or favorable information mismatch.

**CLAIM CEILING** `INTERVENTION_IDENTIFIABLE_DIAGNOSIS`.

## E150-E — multi-generation factor refinement / effective coupling

**THEORY QUESTION** Does learned factor state reduce the number of cognitive components touched by later adaptation over generations?

**PREDICTION** Sparse/stable: after initial induction, contradiction scans remain but refits/touched components collapse. Drift: only contradicted output factors refit. Dense: repeated global touching or non-identifiability erases locality.

**STRONGEST PARENT** Symbolic frontier, plus global refit, exact-retention lazy symbolic, warm-start evolutionary search and learned-surrogate parents.

**RED COUNTEREXAMPLE** Symbolic compact parent has the same touched-component trajectory and a no-worse resource vector.

**MECHANISM** Persist factors and refit only outputs contradicted by new evidence.

**CAUSAL ABLATION** Reset learned factor state every generation; global refit every output; lazy rederive every generation.

**RESULT** Protected only.

**RESOURCE VECTOR** Per-generation and lifetime componentwise vector below.

**FALSIFIER** No sparse/stable amortization, reset does not remove it, or strongest parent owns it.

**CLAIM CEILING** Regime-bounded factorized adaptation.

## E150-F — real M11 self-reorganization bridge

**THEORY QUESTION** Can a learned diagnosis/factor change traverse the real governed self-change lifecycle and survive restart for fresh reuse?

**PREDICTION** Minimum D2 repair can be proposed, prediction-receipted before shadow, externally adopted, persisted, restarted and reused; a broader repair is refused.

**STRONGEST PARENT** Same M11 lifecycle driven by the adaptive symbolic factor parent.

**RED COUNTEREXAMPLE** Equal fresh capability with smaller/equal parent state or governance cost.

**MECHANISM** Existing `ocm.selfmodel` proposal/governance/adoption ledger and runtime replay.

**CAUSAL ABLATION** Broader-than-minimum proposal; missing intervention evidence; deletion/restart hostile; pre-outcome receipt ordering.

**RESULT** Governed separately by the frozen V1 M11 bridge test; V3 cannot promote equality as a win.

**RESOURCE VECTOR** Fresh successes, proposal/shadow/adoption events, installed bytes, restart persistence.

**FALSIFIER** Any governance failure, lost fresh reuse, or strongest parent match/dominance.

**CLAIM CEILING** Governed persistent repair, not autonomous recursive self-improvement.

# V3 comparator frontier

1. `factor_local`: persistent learned factors + explicit relevance cache + local contradiction-triggered refit.
2. `symbolic_compact_parent`: identical factor grammar/learner/refit policy, no duplicate relevance cache/archive.
3. `symbolic_incremental_memory_parent`: compact symbolic parent + exact persistent episode archive; archive writes/state are charged.
4. `symbolic_lazy_parent`: exact persistent episode archive; current-generation support induction is deferred until evaluation; archive is retained and charged.
5. `global_refit_parent`: exact archive; every generation refits every output on all retained episodes.
6. `evolutionary_warm_parent`: warm-start population search, with the current learned model included and a constant-negative baseline included. Its per-generation **literal-evaluation budget** is the factor-local arm's observed induction+invalidation literal evaluations from that same training generation, divided across outputs. This is a matched literal-evaluation comparison, not a total-cost scalar.
7. `surrogate_window_parent`: learned unary/pairwise literal statistics refit to the current generation.
8. `surrogate_persistent_parent`: the same learned statistics accumulated across generations.
9. `reset_factor_ablation`: exact episode archive retained, learned factors deleted and all outputs rediscovered every generation.
10. `loo_dependency_ablation`: known-incomplete single-coordinate relevance proxy.

A dependency-pinned matched neural/Transformer adaptation implementation is not present in the repository. The neural comparison remains `CANNOT_CHECK_NEURAL_MATCHED`; no weak toy neural arm may be used to promote OCM.

# V3 accounting corrections

## Non-identifiable support scoring

Let `T` be identifiable true supports, `U` true but non-identifiable supports, and `L` learned supports. Precision is computed over `L \\ U`, so a correct support in `U` is neither rewarded nor scored as a false positive. False learned supports not in the oracle remain false positives. Recall is over `T`. If `T` is empty, support P/R/F1 are `CANNOT_CHECK` (`null`) for that unit.

## Contradiction/invalidation work

Every training example and learned-factor literal inspected merely to decide whether a component needs refitting is charged separately. Locality is not allowed a free change detector.

## Relevance-cache maintenance

Explicit relevance cache recomputation is charged by literal reads and changed entries. The compact parent is allowed to derive relevance from its factors without carrying duplicate persistent cache state.

## Archive retention

Any parent that claims exact episodic retention carries the serialized archive in `state_bytes` and pays a frozen per-field archive-write operation count.

# Capability/resource vector

No composite score decides the claim. Every arm reports per generation:

`[heldout_accuracy, heldout_balanced_accuracy, support_precision, support_recall, support_f1, identifiable_supports, nonidentifiable_supports, relevance_precision, relevance_recall, induction_literal_evals, induction_candidates, induction_selection_ops, invalidation_literal_evals, invalidation_examples, update_components_touched, prediction_literal_evals, validation_examples, maintenance_ops, rediscovery_ops, state_bytes, effective_coupling]`.

`effective_coupling = update_components_touched / 4` for that generation.

Lifetime comparisons retain each resource coordinate separately; sums of heterogeneous resource coordinates are forbidden as decision statistics.

# Frozen V3 decision rules

An OCM-specific learned-factorization residual requires all of the following:

1. sparse/stable protected median generation-8 raw and balanced accuracy are each non-inferior to every symbolic frontier parent by margin 0.01;
2. sparse/stable median support F1 is >= 0.90 on checkable units, with all non-identifiable units separately counted;
3. sparse/stable median relevance precision and recall are each >= 0.90;
4. by generation 8, persistent factor state has reduced touched components relative to `reset_factor_ablation`, and deleting factor state increases rediscovery on at least 30/40 sparse/stable seeds;
5. no symbolic frontier parent componentwise weakly dominates `factor_local` on capability/structure/relevance plus cumulative resource coordinates and final state, with at least one strict resource improvement, on >= 30/40 sparse/stable seeds;
6. dense and drift results are fully disclosed. Non-identifiable dense support recovery is `CANNOT_CHECK`, never silently converted into a favorable score;
7. the frozen M11 lifecycle lane must leave a positive residual after the same symbolic-parent lifecycle. Equality is `PARENT_SUFFICIENT`;
8. the hidden-cause HC1 lane must not depend on oracle labels. Same-information parent equality is `PARENT_SUFFICIENT`;
9. all 40 protected seeds are published, and no protected family is removed after outcomes.

If `symbolic_compact_parent` matches factor/capability/locality and is componentwise no worse with strictly lower relevance-maintenance/state on >=30/40 sparse/stable seeds, the principal terminal is **`PARENT_SUFFICIENT`** even if factorized adaptation beats global refit, reset, or matched-budget evolution.

If sparse/stable identifiable factor recovery itself fails, that mechanism is **`REFUTED`**.

If a structure coordinate is not identifiable at the frozen sample budget, it is **`CANNOT_CHECK`**.

# Claim ceiling

The strongest possible V3 positive is:

> In an identifiable bounded monotone sparse-factor regime, persistent learned factors can amortize repeated structure discovery and localize future adaptation.

That statement is algorithm-general. It becomes an OCM-specific result only if a residual survives the strongest adaptive parent frontier and the real M11 lifecycle parent subtraction. A failure to survive narrows PR #150 from an OCM advantage theory to a generic factorization/amortization principle with explicit sparsity, identifiability and drift boundaries.
