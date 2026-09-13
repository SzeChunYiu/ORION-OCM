# Semantic adequacy correction — recursive audit SA-1

Date: 2026-09-13. Predecessor reviewed: `5622ac45d0261e8fe0a92f4209b1bb782ce43732`.

## Counterexample and corrected scope

The predecessor semantic-refinement theorem §6 asserted that an adequate
representation must preserve `S_T`, the entire declared response quotient.
Section 7 inferred task-memory growth from growth in `|S_T|`.

Those statements conflate two different obligations. A response-preserving
representation must recover every registered counterfactual response.
A task-solving representation may only need to choose one acceptable action.
The acceptable-action sets `{a,b}` and `{a,c}` have distinct success profiles
under action probes, but a constant representation choosing `a` satisfies
both. Three sets `{a,b}`, `{b,c}`, `{a,c}` additionally show why pairwise
compatibility is insufficient: all pairs intersect, while the full triple
requires two messages. The full response quotient has three classes.

SR-1/SR-2 and the monotonicity of exact response quotients remain valid.
The corrected §6 proves an iff only for full response preservation. Relational
zero-error adequacy is governed by SC-1's hypergraph on compatible histories.
For a deterministic exact function with no side information, different output
values are incompatible, and the quotient-cardinality/message equality remains
valid. ACL-3 also retains its explicit pairwise-incompatibility hypothesis.
The same clarification is propagated to proof-search GP1: preserving every
continuation response is stronger than finding one shared accepted completion.
Its right-congruent quotient and conflict-based GP3 results are retained.
The continual-retention CSR-1/2 law is also retained: it explicitly requires
recovering every exact task answer from persistent memory and task identity,
so it has the stronger response-preservation obligation this repair distinguishes.

An always-successful `safe` action alongside a bit-sensitive `probe` action
separates response diversity from task memory across horizons: full responses
distinguish `2^T` binary prefixes, while an always-safe one-state controller
satisfies every obligation. These are finite slices of the stated sequence
counterexample; no unbounded controller capacity is empirically inferred.

## Recursive update and null-history boundaries

A quotient label is not automatically an executable memory state. Stationary
deterministic quotient updates require class-consistent action legality and
right congruence. Prefix-closed full continuation tests with coherent
concatenation imply that property. Truncated tests instead automatically
update from remaining-horizon `S_T` to `S_(T-1)`, not generally back to `S_T`.
The new checker has both a current-output counterexample and a positive-
horizon delayed-output counterexample, as well as exact refinement controls.

For stochastic observations, a joint law determines conditional responses
only almost surely. The same law concentrated at `(H,Y)=(0,0)` permits both
conditional versions `P(Y=1|H)=(0,0)` and `(0,1)`; their all-history quotients
have one and two classes. This is a typing boundary, not a defect when rooted
response kernels at all admitted histories are already explicitly declared.
The corrected theorem requires the all-history or almost-sure convention and
fixed common response semantics across refinement comparisons.

## Bounded validation and preserved evidence

`grand_gmi_semantic_adequacy_checks_v1.py` cross-checks SC-1 hypergraph coloring
against independent encoder/decoder enumeration for all 343 nonempty
three-state, three-action relational tasks. All 27 exact-function tasks retain
equality between profile count and required messages. It separately checks
216 deterministic three-state process systems, 432 countdown updates, stable
right-congruent refinements, horizon-growth slices and the null-history witness.

Exact output is committed as `GRAND_GMI_SEMANTIC_ADEQUACY_RECEIPT_V1.json`.
The historical recursive checker and receipt remain unchanged: their 110,592
coordinate-refinement checks never tested relational adequacy or established
transition realizability from state cardinality alone.

Current terminal: `GRAND_GMI_SEMANTIC_ADEQUACY_CORRECTION_GREEN_AT_FINITE_SCOPE`.
This is a mathematical correction at declared scope, not empirical GMI closure.

## Parent literature and contribution boundary

[Shalizi and Shalizi, Blind Construction of Optimal Nonlinear Recursive Predictors for Discrete Sequences, §2](https://arxiv.org/pdf/cs/0406011)
was read for the parent distinction: predictive sufficiency preserves the
future distribution, and recursive calculability is a separately stated
property. Their prediction theorem does not imply that every policy achieving
a weaker set-valued control objective must preserve the full predictive state.
The current correction is a finite factorization/compatibility argument, not
a new discovery of sufficient statistics or automaton congruence.
