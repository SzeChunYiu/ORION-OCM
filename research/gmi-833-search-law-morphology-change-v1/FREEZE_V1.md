# GMI #833 — Search-Law Morphology-Change Freeze V1

Status: PRE-IMPLEMENTATION FREEZE
Source issue: #879
Master programme: #833
Target checklist row: Section J — `Derive when search law changes observed morphology.`

## Frozen source

- source `main`: `6368cda406d8e3395283049abacb36129ae94637`
- branch: `research/879-search-law-morphology-change-v1`

All executable checker, hostile tests, canonical result receipt, theorem note, manifest, reconciliation spec, and workflow must postdate this freeze commit.

## Parent authority and subtraction

This tranche does not reclaim finite-budget prefix selection, generic algorithm selection, or the empirical fact that search/encoding can change finite-budget recovery.

Exact merged parent object at freeze:

- finite search-budget morphology receipt:
  `research/gmi-833-finite-search-budget-morphology-v1/RESULT_V1.json`, Git blob `4ea315e651475cc8afcc39860a0d2ac621e9f571`.

Historical merged parent evidence retained without re-claiming it:

- #712 / Section-E E1 exact reachability and charged search-bias burden;
- #724 / Section-E E2 same-world parent-searcher comparison;
- #395 normative realization optimum versus bounded morphogenetic discovery;
- #864 semantic remint equivariance with explicit search-order non-invariance hostile.

## Frozen theorem target

For one registered finite nonempty morphology set `M`, one exact scalar minimization objective `f`, and two complete deterministic charged search laws `L1,L2`, each with a permutation of `M`, strictly positive exact evaluation costs, and the same earliest-seen tie policy:

1. each observed morphology `I_j(B)` is piecewise constant in exact budget `B`; hence cross-law disagreement can change only at a completion threshold belonging to at least one law;
2. whenever both incumbents exist, identity disagreement decomposes exactly into either different incumbent values or equal incumbent values with different morphology identities;
3. changing the search law need not change observed morphology;
4. if `f` has a unique global optimizer, both laws agree on it for every `B >= max(B*_1,B*_2)`;
5. if `f` has multiple global optimizers, zero-regret complete search can still leave morphology identity search-law-dependent under earliest-seen tie-breaking;
6. if objective values are injective on `M`, identity disagreement whenever both incumbents exist implies value disagreement;
7. the finite disagreement set over budget is a union of half-open threshold cells induced by the sorted union of both completion schedules.

## Exact certificate target

Enumerate all worlds with:

- `1 <= |M| <= 4`;
- objective values in `{0,1,2}`;
- unit evaluation costs;
- every ordered pair of complete search permutations;
- every integer budget `0..|M|`.

The bounded census must check decomposition, threshold constancy, unique-optimum eventual agreement, existence of tied-optimum complete-budget identity disagreement, and existence of changed laws with no observed morphology change. General positive rational costs remain analytic plus dedicated exact witnesses.

## Required hostile controls

Fail closed on:

- empty/duplicate universes;
- non-permutation or incomplete law traces;
- mismatched universes/objective semantics across compared laws;
- missing/extra/inexact objectives;
- missing/extra/nonpositive/inexact law costs;
- negative/inexact budgets;
- fabricated morphology before any completion;
- false `equal value => equal identity` promotion;
- false `complete search => same identity` promotion under global ties;
- false `different law => different morphology` promotion;
- stochastic/universal-searcher promotion.

## Claim ceiling

`GMI_FINITE_DETERMINISTIC_SEARCH_LAW_MORPHOLOGY_DISAGREEMENT_DERIVED_AT_REGISTERED_SCOPE`

Forbidden promotions from this tranche alone:

- `ANY_SEARCH_LAW_CHANGE_ALTERS_MORPHOLOGY`
- `SEARCH_LAW_INVARIANT_IDENTITY_UNDER_GLOBAL_TIES`
- `STOCHASTIC_SEARCH_LAW_THEOREM`
- `UNIVERSAL_SEARCHER_DOMINANCE`
- `REAL_OPTIMIZER_CONVERGENCE`
- `PROSPECTIVE_MORPHOLOGY_TRANSITIONS_PREDICTED`
- `P3_RECOVERY_COMPLETE`
- `COMPLETE_GMI`
