# GMI #602 formal-gap V2 hostile-proof corrigenda

Status: **NORMATIVE CORRIGENDA FOR `GMI_602_FORMAL_GAP_CLOSURE_V2.md`**  
Date: 2026-09-14.  
Rule: these corrections narrow T602-25 and T602-26; they do not raise any claim ceiling.

## C602-25 — update-law selection needs attainment or an infimum statement

T602-25's notation

\[
U^*\in\arg\min_{U\in\mathcal U}E[L(U)\mid E,R,V,H]
\]

is used only when the minimum is attained in the registered admissible law class.

Without an attainment/compactness/existence theorem, the correct object is the infimum

\[
L^*(E,R,V,H)=\inf_{U\in\mathcal U}E[L(U)\mid E,R,V,H],
\]

and an `epsilon`-optimal law satisfies

\[
E[L(U_\epsilon)\mid E,R,V,H]\le L^*+\epsilon.
\]

Therefore #602 may not infer existence of an optimal update law merely from the common update-object definition.

## C602-26 — reachability statement is discrete/support-graph unless generalized measure-theoretically

T602-26's positive path-product wording is exact for a finite/countable registered developmental state space, or for an explicitly discretized/support graph whose legal edges have positive transition mass.

For a general continuous-state Markov kernel, a single point can have probability zero even while every neighborhood of it is reachable. The measure-theoretic replacement is:

- target `A` is horizon-`T` reachable when `P(Z_T in A)>0` (or `P(tau_A <= T)>0` for first-hit reachability);
- support reachability is stated using positive-measure neighborhoods/support sets rather than positive probability of exact point paths;
- global impossibility means `P(tau_A<infinity)=0` under the registered process.

The encoding-invariance and total-variation comparison in T602-26 remain valid when written for measurable bijections/pushforward kernels and trajectory events. The simple edge/path formulation should be read as the finite/countable microscope specialization.

## Claim effect

These corrections prevent two illicit upgrades:

1. a conditional law-selection problem does not guarantee an attained optimizer; and
2. a continuous search process is not declared unreachable merely because every exact state path has zero point mass.
