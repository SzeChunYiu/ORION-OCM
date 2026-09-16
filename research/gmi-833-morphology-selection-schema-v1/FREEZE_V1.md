# GMI #833 morphology selection schema v1 — freeze

Parent issue: #833 Section J. Programme checkpoint: issue comment 5692726505.
Base main: `861b1ba1cb871677867140d523ac49b37f15b832`.

## Frozen scientific scope

Finite architecture-name-free candidate mechanism classes under an explicitly registered context. A context supplies a viable/reachable subset and exact nonnegative lifecycle/resource vectors. Scalar selection is conditional on a frozen strictly-positive price vector; raw vectors remain primary.

For phase analysis, each viable candidate may instead carry an exact affine scalar score

`f_m(theta)=a_m+b_m*theta`

on a closed rational interval `I=[L,U]`, with viability fixed on that interval. The phase analysis is about this registered affine microscope only.

## Frozen theorem targets

### SEL-1 — finite morphology-selection correspondence

Define a total fail-closed schema returning:

- `NO_VIABLE_MORPHOLOGY` when the registered viable/reachable set is empty;
- the raw Pareto frontier of viable candidates;
- for each frozen positive price vector, the exact scalar argmin set rather than a fabricated unique winner.

Prove/check that every positive-scalar minimizer is Pareto-efficient and that restricting the candidate set to a reachable subset cannot produce an objective value better than the global viable optimum.

### SEL-2 — sufficient conditions for unique selection

Prove that if one viable candidate has strictly smaller scalar score than every rival, the scalar argmin is exactly that singleton. More strongly, if one candidate componentwise weakly dominates every rival and is strict against each rival somewhere, it is the unique Pareto member and the unique minimizer under every strictly-positive price vector.

A hostile must show that incomparability can yield coexistence and price-dependent winners.

### SEL-3 — Pareto coexistence

Define coexistence as a Pareto frontier with cardinality greater than one. Preserve the entire frontier. A hostile must show that coordinatewise minima can fabricate an unattainable pseudo-morphology and are not a valid replacement for the frontier.

### PHASE-1 — exact affine phase boundaries

For finite affine scores on `I`, construct the exact set of pairwise crossing points

`theta_ij=(a_j-a_i)/(b_i-b_j)`

that lie in `I`. Prove that the exact argmin set is constant on every open cell between consecutive registered crossing points; changes can occur only at a registered boundary. Equal affine functions are permanent ties, not isolated boundaries.

The executor must independently verify the theorem over an exact rational finite fixture by comparing analytic cells/boundaries against direct score evaluation.

### PHASE-2 — uncertainty-set selection semantics

For a registered uncertain ecology/price interval `U=[l,u] subseteq I`, define the possible-winner set as the union of exact argmins across all phase cells and boundaries intersecting `U`.

Prove/check:

- `ROBUST_UNIQUE` iff that possible-winner set is a singleton;
- `AMBIGUOUS` iff it contains more than one candidate;
- endpoint-only strict dominance is sufficient for robust uniqueness of one affine candidate over every rival because each pairwise score difference is affine and therefore attains its extrema at endpoints.

A hostile must show that evaluating only the midpoint can miss a boundary/winner inside the uncertainty interval.

## Required boundaries

This tranche does **not** claim:

- a universal intelligence utility or universal price vector;
- non-affine or stochastic phase laws;
- real-world ecology calibration;
- history/hysteresis or switching-cost closure;
- unrestricted topology/manifold structure;
- all-known-form recovery;
- complete GMI.

Parent ownership is explicit: finite argmin/Pareto theory, affine lower envelopes, hyperplane/crossover arrangements, and interval uncertainty are conventional mathematics. The GMI residual is their architecture-name-free integration with the existing specification/reachability/resource contracts and fail-closed machine-checkable claim discipline.

Expected claim ceiling if all exact/hostile checks are GREEN:

`GMI_FINITE_MORPHOLOGY_SELECTION_AND_AFFINE_PHASE_SCHEMA_AT_REGISTERED_SCOPE`
