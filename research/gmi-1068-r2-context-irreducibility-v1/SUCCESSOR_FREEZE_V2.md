# R2-S1 successor freeze — explicit context scope and intervention boundaries

Issue: #1068
Ancestor R2 merge: 21d93256842021b41b2af52108e612dbe1ec404a
Frozen parent candidate: R1-S1 head 90be32b432ce0daeda57c4bd09e4330c4d7e3ec7

This freeze precedes R2-S1 outcome-bearing implementation. No R2-S1 result is earned unless R1-S1 is re-earned unchanged or an explicit dependency refresh rebinds this freeze.

## Defects under attack

1. R2 V1 declares a partial evaluator but its finite executable route only uses total reward maps.
2. "Context = evaluator + preorder" underdescribes task/ecology/resource restrictions that select which substrate-admitted histories are in scope.
3. Intervention questions must be distinguished from intervention availability: a context may request/evaluate an intervention, while C_S still determines whether that process exists.
4. Cross-context scalar aggregation requires additional weighting/measure semantics and cannot be silently inferred from K.
5. Mutual non-derivability is a model-theoretic nonuniqueness result, not a theorem that physical facts and values can never correlate.

## Frozen context schema

For a substrate history space Hist(C_S), a context may declare:

- a scope predicate S_k(h) selecting histories relevant to the question;
- a partial evaluator nu_k(h) returning a result only where defined;
- a preorder on the result space;
- target/success/resource projections or test/intervention questions when needed by a derived notion.

The context scope is always a restriction of substrate-admitted histories. It does not create a process absent from C_S.

## Frozen theorem targets

- same C_S admits distinct value/order contexts;
- same declared evaluation question can be paired with process universes having different reachability;
- explicit partial-evaluator finite hostile;
- context-scope restriction changes contextual attainability even with the same evaluator;
- requested intervention absent from C_S remains impossible;
- scalarization of incomparable results imports extra contextual weights;
- cross-context aggregation can reverse under different weighting measures;
- no claim that context and physics are statistically independent;
- parent ownership for decision theory, reward/IRL ambiguity, Pareto order and environment-weighted intelligence;
- reconcile all R2 rows.

## Claim ceiling

GRAND_GMI_V2_R2_S1_PROCESS_CONTEXT_NONUNIQUENESS_WITH_EXPLICIT_SCOPE_AND_PARTIAL_EVALUATION

## Forbidden promotions

- CONTEXT_SCOPE_CREATES_SUBSTRATE_PROCESSES
- VALUES_STATISTICALLY_INDEPENDENT_OF_PHYSICS
- UNIQUE_CONTEXT_FREE_INTELLIGENCE_SCALAR
- PARTIAL_EVALUATOR_TREATED_AS_TOTAL
- INTERVENTION_QUESTION_IMPLIES_INTERVENTION_AVAILABLE
- FULL_GMI
