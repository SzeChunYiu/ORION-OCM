# GMI #833 finite history, switching and hysteresis selection v1

**Issue:** #895, child of #833 Section J  
**Freeze:** `FREEZE_V1.md`, commit `b0290772d2fc9321d281077bbca8f03f3d8611e1`  
**Claim ceiling:** `GMI_FINITE_HISTORY_SWITCHING_AND_HYSTERESIS_SELECTION_AT_REGISTERED_SCOPE`

This tranche extends the finite morphology-selection correspondence from #893 by making one piece of developmental history explicit: the previously selected morphology. It proves exact finite switching/hysteresis and history-erasure laws. It does not claim a stochastic or real-world migration theory.

## 1. Registered history-conditioned selection

Fix a finite architecture-name-free morphology set `M`. At the registered current ecology, morphology `m` has exact nonnegative base cost `c(m)`. The previous morphology is `h in M`. Switching/migration burden is an exact nonnegative matrix

`K : M x M -> Q_{>=0}`.

The current selection correspondence is

`Sel(h) = argmin_{m in M} [ c(m) + K(h,m) ]`.

Tie sets are preserved exactly.

Define **history-dependent current morphology** iff there exist `h1,h2` such that

`Sel(h1) != Sel(h2)`.

This is a property of the registered base costs plus switching contract, not a biological analogy.

## 2. HIST-1 — exact history-dependence criterion

The criterion above is definitional but operationally important: two histories matter scientifically only when they alter the exact current selection set under the same instantaneous ecology/resources.

The positive hostile freezes two forms `A,B` with equal base costs and symmetric cross-switch cost `1`, self-switch cost `0`. Then

`Sel(A)={A}` and `Sel(B)={B}`.

Thus identical instantaneous costs can yield different observed morphology solely because transition burden retains the previous form.

## 3. HIST-2 — symmetric two-form hysteresis band

Let

`K(A,A)=K(B,B)=0`, `K(A,B)=K(B,A)=kappa`, `kappa>=0`,

and define

`delta = c(B)-c(A)`.

From previous `A`, compare staying at `A` with switching to `B`:

`c(A)` versus `c(B)+kappa`.

Switch to `B` exactly when

`delta+kappa < 0`, i.e. `delta < -kappa`.

At `delta=-kappa`, preserve the tie `{A,B}`.

From previous `B`, compare switching to `A` with staying at `B`:

`c(A)+kappa` versus `c(B)`.

Select `A` exactly when

`delta-kappa > 0`, i.e. `delta > kappa`.

At `delta=kappa`, preserve the tie `{A,B}`.

Therefore:

- `delta < -kappa`: both histories select `B`;
- `-kappa < delta < kappa`: previous `A` selects `A`, previous `B` selects `B`;
- `delta > kappa`: both histories select `A`;
- boundaries preserve exact ties.

The middle interval is the finite registered **hysteresis band**. Width is `2*kappa` in the instantaneous-difference coordinate.

The executable receipt checks every `kappa in {0,1,2}` and every integer `delta in {-3,...,3}`: 21 exact contexts with zero mismatches.

### Affine ecology/resource coordinate

If

`delta(theta)=alpha+beta theta`, `beta != 0`,

then the two switching thresholds solve

`delta(theta)=+/- kappa`,

so the exact threshold set is

`{ (-kappa-alpha)/beta, (kappa-alpha)/beta }`, sorted by value.

The frozen witness `delta(theta)=-1+2 theta`, `kappa=1/2` gives thresholds `1/4` and `3/4`.

## 4. ERASE-1 — origin-additive switching erases history

Suppose

`K(h,m)=u(h)+v(m)`

for nonnegative functions `u,v`. Then

`c(m)+K(h,m) = u(h) + [c(m)+v(m)]`.

For fixed previous history `h`, `u(h)` is the same additive constant for every current candidate. Adding a common constant does not alter an argmin, hence

`Sel(h)=argmin_m [c(m)+v(m)]`

for every `h`.

Therefore current selection is history-independent.

Zero switching is the special case `u=v=0`.

The executable certificate exhausts:

- three morphologies;
- base-cost vectors in `{0,1,2}^3`;
- `u` in `{0,1}^3`;
- `v` in `{0,1}^3`;

for `27*8*8 = 1,728` exact origin-additive contexts, with zero history leaks.

This is a sufficient structural law, not a claim that all empirically relevant switching costs are separable.

## 5. ERASE-2 — uniform winner margin

Fix candidate `m*`. If for every previous morphology `h` and rival `n != m*`,

`c(n)-c(m*) > K(h,m*)-K(h,n)`,

then rearrangement gives

`c(m*)+K(h,m*) < c(n)+K(h,n)`.

Thus `m*` is strictly better than every rival under every history, so

`Sel(h)={m*}` for all `h`.

This condition can erase history even when `K` is not origin-additive.

The receipt enumerates 13,824 exact three-morphology contexts formed from base costs in `{0,1,2}^3` and binary switching matrices. It finds 3,735 candidate/context margin certificates and verifies every one produces the predicted history-independent singleton selection.

The theorem is one-way: failure of this strict sufficient margin does not imply history dependence.

## 6. RESET-1 — explicit migration/reset state

Suppose a registered migration/reset intervention maps every previous morphology to one canonical preselection state `h0`. Selection after reset is then, by construction,

`Sel_reset(h)=Sel(h0)`

for every original `h`. Hence the previous morphology identity no longer affects the current selection correspondence.

Any physical/computational reset burden remains a separate lifecycle cost and must be charged if included in the scientific comparison. This theorem only states the identity effect of the reset map.

## 7. Boundaries and fail-closed semantics

The executor rejects malformed morphology sets, missing base/switching entries, negative base cost, negative switching cost and unknown previous/reset morphologies.

History-dependence and history-erasure are exact scoped predicates. No result here implies that history is globally irrelevant outside the registered state summary. A richer non-Markov history may contain information not represented by the single previous-morphology variable.

## 8. Parent ownership

The mathematics is conventional:

- finite dynamic choice with switching costs;
- hysteresis/inertia from transition costs;
- additive terms cancelling from argmin comparisons;
- strict-margin sufficient conditions.

The GMI residual is the architecture-name-free integration into the morphology-selection programme, exact machine-readable claim boundaries, and connection to prior-free/reachable morphology derivation.

## 9. Forbidden promotions

This result does not establish stochastic switching dynamics, endogenous learning of switching costs, general non-Markov history compression, real-world migration calibration, universal hysteresis, complete morphology dynamics, or complete GMI.
