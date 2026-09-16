# GMI #833 finite morphology selection and affine phase schema v1

**Issue:** #893, child of #833 Section J  
**Freeze:** `FREEZE_V1.md`, commit `e052708a7952e814985dcbe6ef84acf772a4619f`  
**Claim ceiling:** `GMI_FINITE_MORPHOLOGY_SELECTION_AND_AFFINE_PHASE_SCHEMA_AT_REGISTERED_SCOPE`

This tranche turns several Section-J questions into one bounded architecture-name-free mathematical object. It is a finite exact theorem package, not a universal utility theory or real-world morphology law.

## 1. Registered selection context

Let `M` be a finite candidate set of computational-mechanism equivalence classes. A registered context determines which candidates are admissible/viable and, separately, which are developmentally reachable under the frozen development/budget contract.

Each active candidate `m` has a raw minimization resource vector

`r(m) in Q^d_{>=0}`.

Raw vectors are primary. A scalar decision is allowed only after a strictly-positive price vector

`w in Q^d_{>0}`

is frozen, giving

`s_w(m)=w dot r(m)`.

The **selection correspondence** returns, without tie-breaking fabrication:

- `NO_VIABLE_MORPHOLOGY` if the registered active set is empty;
- the full Pareto frontier of the active set;
- the full scalar argmin set under frozen `w`.

Architecture/family names do not enter these definitions.

## 2. SEL-1 — scalar minimizers are Pareto-efficient

Let `m` minimize `s_w` with `w_i>0`. Suppose for contradiction that another active candidate `n` strictly Pareto-dominates `m`: `r_i(n)<=r_i(m)` for every coordinate and strict inequality holds somewhere. Then

`w dot r(n) < w dot r(m)`

because all weighted coordinate differences are nonpositive and at least one is strictly negative. This contradicts minimality. Therefore every positive-scalar minimizer lies on the raw Pareto frontier.

The executor checks this over every nonempty subset of the nine vectors in `{0,1,2}^2` and four distinct positive weight vectors: `511 * 4 = 2,044` exact comparisons, with zero violations.

### Reachable restriction

If `R subseteq M` is the nonempty reachable active subset, then

`min_{m in M} s_w(m) <= min_{m in R} s_w(m)`.

This is immediate because the right minimization is over a subset. It is consistent with and deliberately subordinate to the stronger current parent result in `gmi-833-global-vs-reachable-morphology-v1`.

## 3. SEL-2 — sufficient conditions for unique selection

### Scalar margin condition

If an active candidate `m*` satisfies

`s_w(m*) < s_w(m)` for every rival `m != m*`,

then the scalar argmin correspondence is exactly `{m*}` by definition.

### Price-independent componentwise condition

Suppose `m*` weakly dominates every rival coordinatewise and is strict against every rival in at least one coordinate. Then:

1. every rival is Pareto-dominated by `m*`, so the Pareto frontier is exactly `{m*}`;
2. for every strictly-positive `w`, `w dot r(m*) < w dot r(m)` for every rival, so `{m*}` is the unique scalar winner for every positive price vector.

The receipt contains an exact `(1,1)` versus `(1,2)` and `(2,1)` witness and verifies several separated positive scalarizations.

These are sufficient conditions, not necessary conditions for uniqueness.

## 4. SEL-3 — coexistence and the no-fabrication rule

Define finite Pareto coexistence at the registered scope by

`|Pareto(M_active)| > 1`.

For the witness vectors

`A=(1,4), B=(4,1), C=(2,2), D=(5,5)`,

`D` is dominated while `A,B,C` are mutually non-dominating. The exact frontier is therefore `{A,B,C}`. Different positive prices select `A`, `B`, or `C`.

A coordinatewise-minimum summary would report `(1,1)` for `A,B`, but no candidate realizes `(1,1)`. Hence coordinatewise minima can fabricate a pseudo-morphology and may not replace the frontier.

## 5. PHASE-1 — affine morphology phase boundaries

For this tranche only, fix a closed rational ecology/price interval `I=[L,U]`. Candidate viability is frozen on `I`. Each active candidate has exact affine scalar score

`f_m(theta)=a_m+b_m theta`.

For two candidates `i,j` with unequal slopes, equality can occur only at

`theta_ij=(a_j-a_i)/(b_i-b_j)`.

Retain crossings inside `I`. Equal affine functions are permanent ties and create no isolated crossing.

### Theorem PHASE-1A — argmin constancy between crossings

Take an open interval containing no pairwise crossing. For each pair `i,j`, the affine difference

`g_ij(theta)=f_i(theta)-f_j(theta)`

has no zero in the interval. By continuity and linearity its sign is constant there. Therefore every pairwise ordering is constant, hence the exact argmin set is constant throughout that open cell.

Consequently an argmin change can occur only at a registered pairwise crossing boundary (although a crossing of two non-minimal candidates need not change the lower envelope).

### Exact witness

The frozen fixture is

`A(theta)=theta`, `B(theta)=1-theta`, `C(theta)=2/5` on `[0,1]`.

Pairwise crossings are exactly

`2/5, 1/2, 3/5`.

The open-cell argmins are

`A | C | C | B`,

with lower-envelope ties `A=C` at `2/5` and `B=C` at `3/5`; the `A=B` crossing at `1/2` is not a phase transition because `C` is strictly lower.

The executable certificate also checks all 84 triples drawn from the nine affine functions with intercept/slope in `{-1,0,1}`, sampling three exact rational points in every crossing-free cell: 507 exact cell checks and zero violations.

## 6. PHASE-2 — uncertainty-set selection

For an uncertain registered interval `U=[l,u] subseteq I`, partition `U` using all pairwise crossings inside it. Because the argmin is constant on every open cell, the exact **possible-winner set** is obtained by evaluating:

- both interval endpoints;
- every crossing boundary;
- one interior point from every open cell.

Define:

- `ROBUST_UNIQUE` iff the possible-winner set is a singleton;
- `AMBIGUOUS` iff it contains more than one candidate.

For the phase witness:

- `[9/20,11/20]` is `ROBUST_UNIQUE` with winner `C`;
- `[1/3,2/3]` is `AMBIGUOUS` with possible winners `{A,B,C}`.

### Endpoint sufficient condition

Fix proposed winner `m*`. For every rival `j`, the difference

`h_j(theta)=f_j(theta)-f_m*(theta)`

is affine. If `h_j(l)>0` and `h_j(u)>0`, then every point between the endpoints is a convex combination of endpoint values and is also positive. If this holds for every rival, `m*` is uniquely optimal throughout `U`.

This gives a cheap sufficient certificate for robust unique selection.

### Midpoint hostile

`M(theta)=0`, `N(theta)=theta-3/4` on `[0,1]`. At the midpoint `1/2`, `N` is uniquely better, but the full interval has possible winners `{M,N}` with a crossing at `3/4`. Midpoint-only evaluation is therefore unsound for uncertainty claims.

## 7. Fail-closed boundaries

The kernel rejects negative resource coordinates, mismatched resource dimensions, nonpositive scalar weights, duplicate candidate identifiers, empty affine candidate sets, and reversed uncertainty/phase intervals. Empty viable selection returns the typed terminal `NO_VIABLE_MORPHOLOGY` rather than inventing a fallback winner.

## 8. Parent ownership

The underlying mathematics is conventional and parent-owned:

- finite argmin correspondences;
- Pareto dominance/frontiers and positive weighted sums;
- affine lower envelopes and pairwise crossover arrangements;
- elementary interval uncertainty.

The GMI residual at this stage is the common architecture-name-free contract that joins those parents to the existing behavioral-specification, reachability, resource, uncertainty and morphology objects while preserving fail-closed claim boundaries.

## 9. Forbidden promotions

This result does not establish a universal intelligence utility, universal price vector, non-affine/stochastic phase theory, real ecology calibration, history/hysteresis, switching/migration closure, all-known-form recovery, unknown-form discovery, or complete GMI.
