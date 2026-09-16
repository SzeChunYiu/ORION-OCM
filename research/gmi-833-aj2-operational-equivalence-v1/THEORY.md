# AJ2 — state/effect roles and operational equivalence

## Scope

This tranche consumes AJ1's substrate-indexed typed operational frame. It does **not** add `state` as a new primitive.

For the registered unit/trivial system `I` and system `A`:

- a preparation/state-role process is `p : I -> A`;
- an effect/test-role process is `e : A -> I`;
- the closed composite `e ∘ p : I -> I` is assigned an operational outcome law by `Obs_S`.

At the frozen finite microscope scope, each closed experiment has a binary outcome and is represented by the exact rational probability `Pr(1 | e,p)`.

## AJ2-EQ — operational equivalence

For a registered admissible test family `E`:

`p ~_E q  iff  for all e in E, Obs_S(e∘p) = Obs_S(e∘q)`.

Equality of complete registered response vectors immediately gives reflexivity, symmetry and transitivity, so `~_E` is an equivalence relation. The executable certificate checks those laws directly over every table in the frozen finite universe rather than relying only on the analytic observation.

Non-equivalence is constructive at this finite scope: if `p !~_E q`, some registered effect is a separating context. The checker returns such an effect and exhaustively verifies that no inequivalent pair lacks one.

## AJ2-Q — quotient and state reconstruction

The quotient `Prep(A)/~_E` is the set of operationally distinct preparation classes at the **declared test scope**. Each quotient class has a unique complete response signature and each distinct signature corresponds to exactly one quotient class. Thus a conventional finite state representation can be reconstructed as the set of response signatures / quotient classes when the registered tests are the complete observational interface for the claim being made.

This is an extensional scientist-side construction. It does not imply that an implementation stores, names or represents the quotient internally.

The exhaustive microscope covers all `3^9 = 19,683` response tables for three preparations, three tests and probabilities `{0,1/2,1}`. It independently computes the quotient both by response-vector hashing and by connected components of the pairwise-equivalence graph; the two constructions agree in every world.

## Hostile boundaries

1. **Syntax is not operational identity.** Two differently named preparations with identical response vectors collapse to the same operational class.
2. **A separator is required for non-equivalence.** A hand-built pair with different responses is separated by a registered effect.
3. **Test scope matters.** Two preparations are equivalent under a restricted one-effect family and become inequivalent when a second admissible test is registered. Therefore a finite restricted test family cannot be silently promoted to universal contextual equivalence.
4. **Operational equivalence is not unconditionally bisimulation or trace equivalence.** Those relations quantify over their own transition/observation structures and coincide only under additional adequacy/congruence assumptions.

## Parent ownership

Operational states/effects as preparation/test roles and equality by all operational statistics are parent ideas in operational/general probabilistic theories. Observational/contextual equivalence is parent semantics in programming languages and process calculi. Bisimulation and coalgebraic behavioural equivalence are stronger/different state-dynamics parents depending on the chosen observations and contexts. AJ2 claims no novelty for those notions.

The GMI contribution here is the explicit reduction step from AJ1's process frame to state/effect roles, the scoped quotient contract, the fail-closed incomplete-test boundary and its exact executable finite certificate.

## Claim ceiling

`AJ2_OPERATIONAL_EQUIVALENCE_AND_STATE_RECONSTRUCTION_AT_FINITE_REGISTERED_TEST_SCOPE`

Forbidden promotions:

- `UNIVERSAL_CONTEXTUAL_EQUIVALENCE_FROM_INCOMPLETE_TESTS`
- `QUOTIENT_REPRESENTED_INSIDE_MACHINE`
- `BISIMULATION_EQUALS_OPERATIONAL_EQUIVALENCE_UNCONDITIONALLY`
- `ABSOLUTE_STATE_ONTOLOGY_PROVEN`
