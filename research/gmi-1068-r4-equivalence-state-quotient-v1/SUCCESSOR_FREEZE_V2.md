# R4-S1 successor freeze — response semantics and quotient boundaries

Issue: #1068
Ancestor round: R4
Ancestor merge: 8e4e42ce31c0c06d9d2f560f2d9b63e27ef31c8c
Successor base: current main after R3 successor #1078

This freeze is committed before any R4-S1 outcome-bearing checker, oracle, result, or Lean successor exists.

## Defects to adjudicate

1. R4 V1 represents responses as total values and therefore does not distinguish an illegal continuation from a legal continuation whose context evaluation is undefined.
2. Equality of response signatures is an equivalence relation, but continuation congruence requires a closure/compatibility condition connecting continuation of a history with precomposition of registered tests.
3. The parent map is too coarse to justify identifying Myhill-Nerode, bisimulation, predictive quotients, classical sufficient statistics, predictive-state coordinates, causal states, and Blackwell/Le Cam comparison.
4. R4 V1 does not exhaustively test the representation lower bound over all partitions of a nontrivial finite history set.
5. Presentation relabeling invariance needs an actual transformed presentation and a negative control; copying the original response table is not evidence.

## Frozen response object

For each history/test pair the successor response is exactly one of:

- ILLEGAL — the continuation is not admitted by the process structure;
- UNDEFINED — the continuation is legal but the context evaluator is undefined;
- VALUE(o) — the continuation is legal and evaluates to contextual observation/value o.

Contextual future equivalence requires equality of this full response object on every registered test.

## Frozen theorem targets

- equivalence laws for the three-way response object;
- conditional continuation congruence under an explicit precomposition/compatibility map on the registered test family;
- any exactly sufficient representation must refine the contextual future quotient;
- exhaustive finite partition census for six named histories, including an illegal-vs-undefined separator;
- restricted-test counterexample showing no unique context-free quotient;
- trace-equivalent/non-bisimilar finite nondeterministic counterexample;
- two finite counterexamples proving classical parameter sufficiency and predictive sufficiency are incomparable without extra assumptions;
- exact parent-boundary registry for Myhill-Nerode, deterministic bisimulation, predictive equivalence, PSRs, causal states, classical sufficiency, and Blackwell/Le Cam;
- response-preserving bijective relabeling preserves the quotient, with a response-changing control that does not.

## Claim ceiling

GRAND_GMI_V2_R4_S1_CONTEXTUAL_RESPONSE_EQUIVALENCE_AND_CONDITIONAL_CONGRUENCE_AT_REGISTERED_FINITE_SCOPE

## Forbidden promotions

- ILLEGAL_EQUALS_CONTEXT_UNDEFINED
- EQUIVALENCE_IMPLIES_CONGRUENCE_WITHOUT_TEST_CLOSURE
- TRACE_EQUIVALENCE_EQUALS_BISIMULATION_UNIVERSALLY
- CLASSICAL_PARAMETER_SUFFICIENCY_EQUALS_PREDICTIVE_SUFFICIENCY
- EVERY_PSR_IS_A_MINIMAL_PREDICTIVE_QUOTIENT
- BLACKWELL_LECAM_IS_A_HISTORY_STATE_QUOTIENT
- UNIQUE_CONTEXT_FREE_STATE_PARTITION
- FULL_GMI
