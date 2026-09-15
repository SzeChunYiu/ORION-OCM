# GMI #833 derivation robustness controls — freeze v1

**Child issue:** #859  
**Parent:** #833 Section D  
**Frozen from main:** `becafa164595e4fc6452c3ec4ca040560cbd5eb7`  
**Claim ceiling:** `GMI_DERIVATION_ROBUSTNESS_CONTROLS_ENFORCED_AT_REGISTERED_FINITE_SCOPE`

This is the pre-implementation custody record. Executor, fixtures, tests, expected receipt, reconciliation spec and workflow must postdate this freeze.

## Exact target rows

This tranche may reconcile only:

1. `Require matched grammar twins that remove the predicted mechanism without changing irrelevant search capacity.`
2. `Require alternate encodings of the same semantics.`
3. `Require alternate search algorithms.`
4. `Require alternate resource scalarizations / Pareto analysis.`

It does not claim that all historical or future derivations already satisfy these controls.

## Parent contract

The package must consume the merged #855/#856 no-smuggling audit as a prerequisite gate. It must also preserve #837 prior-disclosure language and raw resource vectors from the foundation/morphcap stack. Parent mathematics stays parent-owned.

## R1 — matched mechanism-removal twin

A positive arm `G+` and negative arm `G-` are a valid matched twin only if all registered nuisance/capacity coordinates are equal and the target semantic mechanism is the only registered mechanism-level difference.

Frozen nuisance/capacity coordinates include at least:

- finite semantic candidate-count/effective-capacity declaration;
- maximum composition depth;
- non-target primitive inventory/cardinality;
- task/ecology/evaluator identity;
- search budget, tie policy and stopping rule;
- raw resource coordinate schema/prices where frozen.

`G-` must remove the target semantic fingerprint without adding a target-equivalent compensating macro. A performance drop under an unmatched twin cannot support a mechanism-necessity inference.

Required terminal vocabulary:

- `MATCHED_MECHANISM_TWIN`
- `UNMATCHED_MECHANISM_TWIN`
- `TARGET_MECHANISM_NOT_REMOVED`
- `COMPENSATING_TARGET_MACRO`

## R2 — semantic encoding remints

Two encodings qualify only through a registered semantics-preserving map. Raw syntax/state names are non-semantic.

The gate must verify at finite scope:

- bijection (or explicitly justified quotient map) between candidate IDs;
- equality of canonical protected behavior;
- equality of raw resource vectors under the registered coordinate map;
- equality of target-mechanism/property labels after canonical projection.

Required terminals:

- `ENCODING_ROBUST_AT_REGISTERED_FINITE_SCOPE`
- `ENCODING_NOT_SEMANTICALLY_EQUIVALENT`
- `CANNOT_CHECK_ENCODING_MAP`

Hostile: alleged remint silently deletes one semantic candidate or changes a resource vector.

## R3 — alternate search algorithms

At least two genuinely distinct registered search procedures must operate on the same frozen semantic candidate set/objective/budget. Search execution cost is recorded separately from candidate lifecycle cost.

The control reports:

- selected semantic optimum/set per algorithm;
- exhaustive/coverage certificate or explicit incompleteness;
- `SEARCH_ROBUST` only when the scoped scientific conclusion agrees;
- `SEARCH_SENSITIVE` when one algorithm misses or changes the relevant conclusion.

Positive witness must use two distinct algorithms with same correct semantic conclusion. Hostile must include an early-stopping heuristic that misses the true optimum while exhaustive enumeration finds it.

## R4 — alternate scalarizations / Pareto

Every resource-sensitive record keeps raw resource vectors and computes the exact Pareto set before scalar scores. At least two preregistered strictly positive scalarizations are evaluated.

The control distinguishes:

- `SCALARIZATION_ROBUST` — the scientific property claim is shared by the Pareto set / all registered scalarizations even if exact candidate identity differs;
- `SCALARIZATION_SENSITIVE` — the claimed universal winner/property changes under admissible weights;
- price-conditional winner statements, which remain allowed when labeled.

Hostile: `(1,4)` vs `(4,1)` reverses candidate identity under `(4,1)` vs `(1,4)`; a universal candidate-winner claim must fail.

## Cross-control admission

A `DerivationRobustnessRecord` may emit

`ROBUST_AT_REGISTERED_D_CONTROLS_SCOPE`

only when:

- R1 matched-twin gate passes;
- R2 at least two semantic-equivalent encodings agree on the protected scientific property;
- R3 at least two distinct searches agree on the scoped scientific conclusion, or a registered exhaustive theorem removes search dependence;
- R4 Pareto + at least two positive scalarizations are compatible with the claim wording;
- every compared arm is clean/evaluable under the #855 no-smuggling audit.

Missing evidence returns `CANNOT_ESTABLISH_D_ROBUSTNESS_<CONTROL>` rather than defaulting to robust.

## Exact finite evidence commitments

Post-freeze artifacts must provide:

- one robust positive derivation witness exercising all four controls;
- one isolated hostile per control;
- cross-control combined hostiles so one passing control cannot launder a failing one;
- exact rational resource arithmetic;
- deterministic normal and `python -O` tests;
- byte-stable receipt;
- exact parent receipt pin for #855;
- PR check-only / main-push apply-only reconciliation for the four target rows.

## Claim boundary

Forbidden from this tranche alone:

- `ALL_GMI_DERIVATIONS_ROBUST`
- `ARCHITECTURE_PRIOR_FREE_UNIVERSALLY`
- `REPRESENTATION_INDEPENDENT_UNIVERSALLY`
- `SEARCH_INDEPENDENT_UNIVERSALLY`
- `RESOURCE_PRICE_INDEPENDENT_UNIVERSALLY`
- `KNOWN_FAMILY_RECOVERY_COMPLETE`
- `COMPLETE_GMI`
