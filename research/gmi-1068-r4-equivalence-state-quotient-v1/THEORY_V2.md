# R4-S1 — contextual response equivalence with explicit legality

R4 V1 is retained as historical evidence. This successor narrows and strengthens its semantics.

For a history `h` and registered continuation/test `t`, the contextual response is not merely an output value. It has three disjoint cases:

- `ILLEGAL`: process composition does not admit the continuation;
- `UNDEFINED`: the continuation is process-admitted but the context evaluator is undefined there;
- `VALUE(o)`: the continuation is admitted and the context returns `o`.

Write this response as `R_kappa(h,t)`.

## Future-response equivalence

For a registered test family `T`:

`h ~_T h'  iff  R_kappa(h,t) = R_kappa(h',t) for every t in T`.

This is an equivalence relation because equality is reflexive, symmetric, and transitive. The quotient is relative to the declared test family and context semantics.

Collapsing `ILLEGAL` and `UNDEFINED` is unsound in general. In the registered six-history fixture, the exact quotient has five classes; collapsing both cases into one generic missing token yields four.

## Conditional continuation congruence

Equivalence alone does not imply a congruence law.

Let `step(h,a)` append an admitted action/process fragment. A congruence theorem requires a map `pre(a,t)` back into the registered test family such that:

`R_kappa(step(h,a), t) = R_kappa(h, pre(a,t))`.

Under this compatibility/closure condition, `h1 ~_T h2` implies `step(h1,a) ~_T step(h2,a)`.

The Lean successor proves exactly this conditional theorem. No unconditional congruence claim survives.

## Sufficient representations and the lower bound

A representation `z(h)` is exactly sufficient for the registered tests when a decoder can reproduce the full three-way response for every history/test pair.

If one registered test distinguishes histories `h1,h2`, any exactly sufficient representation must assign different representation values to them. Thus every exactly sufficient representation partition refines the future-response quotient.

The finite successor enumerates every Bell(6)=203 partition of six named histories. Exactly two partitions are sufficient: the five-class response quotient and the discrete six-class partition. Therefore the minimum sufficient representation has five states in this registered fixture, with one unique coarsest sufficient partition up to relabeling.

This is a finite exact lower bound, not a universal finite-state theorem.

## Context/test dependence

Using only the first registered test merges all six histories into one class, while the full family yields five classes. Hence the core does not determine a unique context-free state partition.

A context-relative architecture-equivalence or organization-equivalence quotient can be defined only after its observable tests and invariances are declared. No intrinsic architecture ontology follows from quotient construction alone.

## Exact boundaries to established parent mathematics

- **Myhill-Nerode.** Exact specialization when histories are deterministic prefixes and the test family contains all relevant right continuations; right congruence and minimum reachable DFA results are parent-owned.
- **Deterministic bisimulation.** Can coincide with future-response equivalence when transition/output observations and deterministic total dynamics satisfy the required closure assumptions. In nondeterministic systems, trace equivalence need not imply bisimulation.
- **Predictive equivalence / predictive state.** Histories are equivalent when every registered future intervention/test has the same future observation law. The predictive quotient is minimal only relative to that complete separating family and exact predictive objective.
- **Predictive-state representations.** Coordinates represent the predictive quotient only when the chosen tests separate all predictive classes. An incomplete coordinate family can merge distinct predictive states.
- **Computational-mechanics causal states.** Parent-owned predictive equivalence of pasts by conditional future distributions under stationary-process assumptions and the associated minimal sufficient statistic result.
- **Classical sufficient statistics.** Parameter sufficiency and future-predictive sufficiency are incomparable without extra assumptions. R4-S1 includes one finite countermodel in each direction.
- **Blackwell / Le Cam.** Compare statistical experiments or information structures via garbling/deficiency-type relations. They are not, by themselves, quotients of a single history space.

## Presentation relabeling

A bijection of presentation names that transports the full response table preserves quotient block structure. This theorem requires response preservation. A control that changes one transported response changes the quotient and is rejected.

## Scope ceiling

`GRAND_GMI_V2_R4_S1_CONTEXTUAL_RESPONSE_EQUIVALENCE_AND_CONDITIONAL_CONGRUENCE_AT_REGISTERED_FINITE_SCOPE`
