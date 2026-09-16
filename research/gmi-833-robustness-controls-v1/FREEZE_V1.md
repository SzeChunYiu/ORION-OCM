# GMI #833 derivation robustness controls — freeze v1

**Child issue:** #863  
**Parent:** #833 Section D  
**Frozen from main:** `115145b60bae9d066d583a4c5d877ee59eb527ab`  
**Claim ceiling:** `GMI_DERIVATION_ROBUSTNESS_CONTROL_REQUIREMENTS_FORMALIZED_AT_REGISTERED_FINITE_SCOPE`

This is the pre-implementation custody record. Executor code, fixtures, tests, receipt, theorem note, manifest, reconciliation spec, and workflow must postdate this freeze.

## Exact target rows

This tranche may reconcile only:

1. `Require matched grammar twins that remove the predicted mechanism without changing irrelevant search capacity.`
2. `Require alternate encodings of the same semantics.`
3. `Require alternate search algorithms.`
4. `Require alternate resource scalarizations / Pareto analysis.`

It does not assert that historical GMI experiments already pass these controls. It defines what future/retrofitted derivation records must contain and how sensitivity must be surfaced.

## Scientific category

There are two distinct predicates:

- **control compliance**: all required robustness controls are validly registered and evaluated;
- **scientific robustness**: the registered scientific conclusion is invariant under those controls.

A sensitive experiment may satisfy the control requirement while correctly refusing a robustness claim. The checklist rows above concern the first predicate.

## R1 — matched grammar negative twin

For a positive finite candidate universe `C+` and target mechanism predicate `m:C+->{0,1}`, define the mechanism-free background projection `b(c)` from every registered non-target primitive/operator/search-capacity feature.

A registered negative twin `C-` is matched iff:

1. every `c in C-` has `m(c)=0`;
2. the multiset `{b(c): c in C-, m(c)=0}` equals the mechanism-free multiset `{b(c): c in C+, m(c)=0}`;
3. ecology/evaluator/search budget/stopping semantics are identical;
4. the only allowed removal is candidates containing the target mechanism.

Any difference in mechanism-free background multiplicities is `GRAMMAR_TWIN_UNMATCHED`. Total candidate count may fall solely because target-containing candidates are removed; that difference must be reported rather than disguised as equal total search capacity.

Frozen positive fixture: two target-containing candidates plus four mechanism-free background candidates; the twin removes exactly the two target candidates and preserves the four mechanism-free background signatures.

Frozen hostile: delete one additional mechanism-free candidate; the twin must fail.

## R2 — alternate semantic encodings/remints

A remint pair consists of finite encodings `e1,e2` plus a declared bijection `phi` between their symbols/candidates and a protected semantic map `sem`. It is valid iff:

- `phi` is bijective over the registered finite domain;
- `sem_1(c) = sem_2(phi(c))` for every candidate;
- task/evaluator/resource semantics are compared after mapping results back to canonical semantic classes.

Terminals:

- `ENCODING_INVARIANT_AT_REGISTERED_REMINTS` if canonical conclusions agree;
- `ENCODING_SENSITIVE` if they differ;
- `CANNOT_AUDIT_ENCODING` if the map is absent, non-bijective, or not semantics-preserving.

Frozen hostile: lexicographic tie-breaking over surface identifiers must change the chosen canonical class after a pure semantics-preserving remint and therefore surface `ENCODING_SENSITIVE`.

## R3 — alternate search algorithms

Register at least two materially distinct algorithms with the same candidate semantics, scientific objective/evaluator, and declared resource/search budget frame.

The record must distinguish:

- `SEARCH_INVARIANT_AT_REGISTERED_ALGORITHMS`;
- `SEARCH_ALGORITHM_SENSITIVE`;
- `CANNOT_COMPARE_SEARCH_BUDGETS` when budgets/resources are not commensurate;
- `CANNOT_AUDIT_SEARCH` when fewer than two valid searchers are registered.

Frozen positive fixture: exhaustive enumeration and independent branch-and-bound with an admissible lower bound recover the same unique optimum on a finite universe.

Frozen hostile: forward and reverse budget-one early-stop search on tied candidates return different semantic winners, producing `SEARCH_ALGORITHM_SENSITIVE`.

## R4 — alternate scalarizations and Pareto analysis

For minimization resource vectors `r(c) in Q_{>=0}^d`, raw vectors and the Pareto relation are primary.

The record must compute:

- the Pareto frontier;
- at least two strictly positive registered weight vectors, unless a stronger theorem covers the full intended weight region;
- scalar winners for each weight vector;
- whether the scientific conclusion is price-conditional.

Frozen theorems/controls:

1. positive weighted sums preserve strict Pareto dominance;
2. registered Pareto-incomparable vectors can reverse under positive weights;
3. agreement on a finite weight sample does not imply completeness over all scalarizations or all Pareto points.

Frozen hostile: `a=(1,4)` and `b=(4,1)` reverse under weights `(4,1)` and `(1,4)`.

## Global protocol terminal

Required machine-distinct outcomes:

- `CONTROL_REQUIREMENTS_SATISFIED` — all R1–R4 blocks are structurally valid/evaluable;
- `ROBUST_AT_REGISTERED_CONTROLS` — requirements satisfied and all registered conclusions invariant;
- `SENSITIVE_AT_REGISTERED_CONTROLS` — requirements satisfied but at least one control changes the conclusion;
- `CANNOT_AUDIT_<CONTROL>` — a required block is missing/malformed.

No control may default to clean when evidence is missing.

## Parent ownership / literature boundary

This tranche does not claim novelty for:

- negative/control experiments and falsification logic;
- inductive/representation/search bias (Mitchell 1980; Mitchell 1982);
- no-free-lunch/search dependence (Wolpert & Macready 1997, DOI 10.1109/4235.585893);
- semantics-preserving/metamorphic testing as an invariance-testing pattern;
- Pareto order, multiobjective optimization, or weighted scalarization.

The residual contribution is the typed GMI robustness-control contract and fail-closed governance integration.

## Evidence commitments

Post-freeze artifacts must include:

- stdlib-only exact finite executor;
- positive + hostile fixtures for every control;
- exact rational arithmetic for resources/weights;
- a missing-control fail-closed census;
- deterministic normal and `python -O` tests;
- byte-stable receipt;
- reconciliation restricted to the four exact rows.

## Forbidden promotions

This tranche alone cannot support:

- `ALL_GMI_RESULTS_ROBUST`
- `ALL_GRAMMARS_NEUTRAL`
- `ENCODING_INVARIANCE_UNIVERSAL`
- `SEARCH_ALGORITHM_INDEPENDENCE_UNIVERSAL`
- `SCALARIZATION_INDEPENDENCE_UNIVERSAL`
- `ALL_HISTORICAL_RESULTS_REPLICATED`
- `P3_RECOVERY_COMPLETE`
- `COMPLETE_GMI`
