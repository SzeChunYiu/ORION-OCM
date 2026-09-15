# Derivation robustness controls — v1

**Issue:** #859, child of #833 Section D  
**Freeze:** `FREEZE_V1.md`  
**Claim ceiling:** `GMI_DERIVATION_ROBUSTNESS_CONTROLS_ENFORCED_AT_REGISTERED_FINITE_SCOPE`

This tranche converts four Section-D robustness requirements into an executable admission schema. It does not claim every GMI result already satisfies the schema; it establishes the gate and an exact finite witness/hostile set.

## 1. Review lanes and parent ownership

The design separates four questions:

1. **Formal-methods / matched-control review** — what must remain invariant for a mechanism-removal twin to be interpretable?
2. **Representation-bias review** — what counts as an alternate encoding rather than a renamed or silently altered problem?
3. **Search / optimization review** — which conclusions survive a change of search procedure and resource prices?
4. **Hostile review** — can a superficially compliant near-miss launder an unmatched twin, incomplete search, or price-dependent winner into a robust claim?

Parent ideas are not re-claimed: controlled ablation/matched experimental comparisons, reproducible algorithm comparison, Pareto optimality and weighted scalarization, and inductive/representation bias remain established methodological/mathematical parents. The #855 no-smuggling package is the repository parent for lexical/semantic/cost/search/evaluation/ecology audit vocabulary.

Relevant methodological context includes work on unbiased/reproducible algorithm comparison and standard Pareto/weighted-sum scalarization theory. The residual contribution here is the typed GMI execution gate and its finite exact evidence.

---

## 2. R1 — matched mechanism-removal twin

Let `G+` be a positive derivation arm and `G-` the registered negative twin. A valid mechanism contrast requires:

- target mechanism enabled in `G+` and disabled in `G-`;
- no target-equivalent compensating macro in `G-`;
- equality of all registered nuisance/capacity coordinates;
- identical no-smuggling-visible generic primitive identifiers for the compared arms;
- explicit positive/negative protected outcome.

The finite gate freezes nuisance coordinates including candidate/effective capacity, maximum composition depth, non-target primitive inventory, task, ecology, evaluator, search budget, tie/stopping rules, and resource-coordinate schema.

If any nuisance coordinate differs, terminal is `UNMATCHED_MECHANISM_TWIN`; a performance drop is therefore not admitted as mechanism-necessity evidence.

### Positive witness

`G+` and `G-` each expose capacity 4, depth 3, identical non-target primitives, task/ecology/evaluator, search budget 4, canonical tie rule, certified-complete stopping, and compute/memory resources. Only the registered target-mechanism bit differs. The positive protected outcome is true and the negative outcome false.

### Hostiles

- negative depth changed from 3 to 1 -> `UNMATCHED_MECHANISM_TWIN`;
- target mechanism left enabled -> `TARGET_MECHANISM_NOT_REMOVED`;
- target-equivalent compensation declared -> `COMPENSATING_TARGET_MACRO`.

---

## 3. R2 — semantics-preserving encoding remints

Raw syntax is non-semantic. Each encoding candidate carries a canonical semantic ID, protected behavior, raw resource vector and protected property. The gate projects every encoding onto

`canonical_id -> (protected_behavior, raw_resources, protected_property)`.

Two encodings count as alternate remints only when:

- at least one pair has disjoint raw identifier sets;
- canonical IDs are unique;
- resource values are nonnegative exact rationals;
- canonical projections are identical.

The positive witness uses syntactically disjoint `alpha_*` and `zeta_*` IDs, with reversed enumeration order, yet projects to the same four semantic candidates.

Hostiles:

- delete one semantic candidate;
- alter one resource coordinate.

Both terminate `ENCODING_NOT_SEMANTICALLY_EQUIVALENT`.

This establishes only registered finite encoding robustness, not universal representation independence.

---

## 4. R3 — alternate search algorithms

The positive witness freezes one semantic candidate set, one task-loss objective and budget 4, then runs two distinct certified procedures:

- exact enumeration evaluates all 4 candidates;
- admissible branch-and-bound uses registered lower bounds and evaluates only the unique optimum before proving every remaining lower bound worse.

Both select `k_balanced`, whose protected mechanism property is true. Their search execution costs are recorded separately (`4` vs `1` evaluations), so search efficiency is not confused with candidate lifecycle cost.

`SEARCH_ROBUST` requires:

- at least two distinct procedure kinds;
- complete/exhaustive or admissible-bound certificates for every procedure;
- agreement on the scoped protected scientific conclusion.

### Early-stop hostile

An incomplete heuristic evaluates `baseline` first and stops after one evaluation. Exact enumeration selects `k_balanced` (property true), while the heuristic selects `baseline` (property false). The gate emits `SEARCH_SENSITIVE`; it never averages away the disagreement.

---

## 5. R4 — raw Pareto set before scalarized winner language

The positive candidate resource vectors are:

- `k_balanced = (2,2)`;
- `k_compute = (1,4)`;
- `k_memory = (4,1)`;
- `baseline = (5,5)`.

For minimization the exact Pareto set is

`{k_balanced, k_compute, k_memory}`.

All three Pareto candidates carry the protected mechanism property, while `baseline` is dominated and lacks it.

Three strictly positive scalarizations select different candidate identities:

- `(compute,memory)=(4,1)` -> `k_compute`;
- `(1,4)` -> `k_memory`;
- `(1,1)` -> `k_balanced`.

Therefore candidate identity is price-sensitive, but the scientific **property** is invariant across the full Pareto set and all registered scalarization winners. The correct terminal is `SCALARIZATION_ROBUST` for the property-level claim, with `candidate_identity_sensitive=true` retained in evidence.

If the same evidence is used to claim one universal candidate winner, the terminal becomes `SCALARIZATION_SENSITIVE`.

This distinction prevents a price-dependent optimization choice from being misreported as a universal scientific morphology law.

---

## 6. #855 no-smuggling integration

The exact parent result is pinned by Git blob and claim ceiling. For both matched-twin arms, the parent auditor receives only generic search-visible primitive identifiers (`add`, `index_read`) and its full lexical/semantic/cost/search/evaluation/ecology clean fixture. Both must return `CLEAN_AT_REGISTERED_AUDIT_SCOPE`.

If the parent receipt drifts, cannot be loaded, or either arm is not clean/evaluable, global D-robustness cannot be established.

---

## 7. Cross-control admission

A record receives

`ROBUST_AT_REGISTERED_D_CONTROLS_SCOPE`

iff all of the following hold simultaneously:

1. R1 returns `MATCHED_MECHANISM_TWIN` and the protected contrast is present;
2. R2 returns `ENCODING_ROBUST_AT_REGISTERED_FINITE_SCOPE`;
3. R3 returns `SEARCH_ROBUST`;
4. R4 returns `SCALARIZATION_ROBUST` for the actual claim wording;
5. both twin arms are clean/evaluable under #855.

Missing controls fail closed using `CANNOT_ESTABLISH_D_ROBUSTNESS_*`. A single failed control yields `D_ROBUSTNESS_NOT_ESTABLISHED` even if every other control passes.

The combined hostile deliberately changes only the negative twin depth while leaving encoding, search, scalarization and no-smuggling controls green; global robustness still fails. This prevents cross-control laundering.

## 8. Falsifiers

The registered claim is falsified if any of the following occurs:

- a nuisance/capacity change is accepted as a matched twin;
- a deleted/cost-changed encoding is treated as a semantic remint;
- an incomplete search disagreement is labeled robust;
- raw Pareto trade-offs are omitted before universal winner language;
- candidate identity reversal is hidden instead of separated from property robustness;
- a missing control defaults to robust;
- a non-clean #855 arm is admitted;
- normal and optimized executions disagree or fail exact receipt replay.

## 9. Claim boundary

Earned only at green CI:

`GMI_DERIVATION_ROBUSTNESS_CONTROLS_ENFORCED_AT_REGISTERED_FINITE_SCOPE`.

Forbidden from this tranche alone:

`ALL_GMI_DERIVATIONS_ROBUST`, `ARCHITECTURE_PRIOR_FREE_UNIVERSALLY`, `REPRESENTATION_INDEPENDENT_UNIVERSALLY`, `SEARCH_INDEPENDENT_UNIVERSALLY`, `RESOURCE_PRICE_INDEPENDENT_UNIVERSALLY`, `KNOWN_FAMILY_RECOVERY_COMPLETE`, `COMPLETE_GMI`.
