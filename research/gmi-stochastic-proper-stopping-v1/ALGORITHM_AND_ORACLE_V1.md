# Exact constructor and independent oracle

## Constructive route

The main implementation first removes states lacking a path to goal under
actions whose entire positive support remains in the current set. Iterating
this operation to a fixed point computes SPS-1's viable domain.

It enumerates deterministic stationary action tables on that domain. For each,
a support-graph test rejects any policy with a state unable to reach goal.
A rational Gaussian elimination independently solves its cost and action-count
systems. Statewise lexicographic minima are computed, and a *single recorded
policy* must attain every minimum. A mismatch raises an error, rather than
presenting incompatible profiles as a policy.

Empty legal action sets, unavailable terminal actions and trapped regions are
represented directly. Malformed probabilities, negative charges and inexact
floating inputs are rejected rather than silently normalized.

## Independent occupancy-flow oracle

For a nonempty viable subproblem inject α_s=1 at each state. Let y_sa≥0
be its total action occupation and impose, for every state s,

    Σ_a y_sa − Σ_(r,a) P(s|r,a)y_ra = 1.

The objectives are lexicographic (Σ_sa c_sa y_sa, Σ_sa y_sa).
Every proper history policy, one initial run at each state, gives a feasible
flow by summing visit probabilities. Conversely a finite feasible y has
y_s=Σ_a y_sa≥1. The randomized stationary policy y_sa/y_s is proper:
a closed nonterminal recurrent class would, on summing its flow equations,
have zero net outflow but strictly positive injection, a contradiction.
Therefore its unique occupation vector is y. This is a complete
finite-expectation policy comparison, not just a second stationary search.

The nonnegative flow polyhedron has no lines and has full row rank: columns
of a proper deterministic policy give invertible I−Qᵀ. A finite linear
minimum exists at a vertex when bounded below. Both objectives are
nonnegative; secondary mass minimization on the primary minimum face discards
any remaining nonzero nonnegative ray, so a lexical minimizing vertex exists.
The oracle enumerates each n-column basis, uses determinant/Cramer's rule,
checks nonnegativity and *all* flow equalities, and minimizes the two scalar
objectives. It shares no support-search, policy evaluator or elimination code
with the constructor. SPS-2 proves the joint stationary output realizes these
sums; comparisons with positive injections (1,1) and (1,2) test both value components.

For partial viability the checker separately enumerates all original
stationary tables and classifies absorption with explicit closed-subset tests.
Their union of proper-from-start domains is compared to the constructor's
fixed point. The oracle's flow problem then receives that independently
determined domain, not a domain asserted by the implementation.

## Falsifying controls

- A reachable goal branch plus an unavoidable trap rejects naive reachability.
- Safe zero loops reject arbitrary scalar-greedy policy selection.
- Cost1 geometric trials have finite expectation and unbounded support length.
- Zero-charge geometric trials reject the greatest extended Bellman claim.
- A finite δ can choose a higher original cost; no numeric δ is used as a
  lexical certificate.
- Independent occupancy objectives test both exact expected cost and expected
  count; zero-cost cases test progress without adding a real execution price.
- Malformed rows and negative costs have distinct input errors.
- Deterministic/no-loop and strictly positive stochastic controls preserve the
  established ZCS/PCA regimes.

These controls are mathematical countermodels. They do not execute a native
task or use a sampled success rate to estimate a kernel.
