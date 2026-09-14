# Section D conditional free-lunch / morphology-phase freeze V1

Date frozen: 2026-09-14.
Owner: #602 Section D. Child tracker: #666.

This file is the **pre-outcome authority** for the first Section D tranche. It is
committed before the witness, receipt, or any scored result exists.

## 0. Question and correction under test

The contributed `BOX_TRIAGE_V1.md` attacks the Section D target

```text
(E, R, V, H) -> Pareto frontier over morphologies
```

using No-Free-Lunch (NFL): if all obligations are averaged with the relevant
symmetry, no morphology/search algorithm has a universal advantage.

We do **not** propose to refute Wolpert--Macready. We test a sharper claim:

> NFL is the zero-structure / symmetry negative control. A strict morphology
> free lunch exists when pre-outcome ecology/obligation side-information breaks
> that symmetry and changes which morphology is decision-optimal.

The proposed repaired Section D target at a registered finite morphology class
`M` is

```text
(S_M(O), E, R, V, H) -> Pareto_M(O,E,R,V,H)
```

where `S_M(O)` is a pre-outcome, architecture-name-free structural signature of
the obligation sufficient to distinguish the morphology decisions that the
frozen candidate class can make.

This is deliberately **relative to the frozen candidate class**. It is not a
claim that one finite signature is complete for every possible future machine.

## 1. Parent mathematics that gets first refusal

The result must be reported as parent-owned wherever appropriate.

1. Wolpert & Macready (1997), *No Free Lunch Theorems for Optimization*:
   under the NFL averaging assumptions, elevated performance on one problem
   class is offset elsewhere.
2. Schumacher, Vose & Whitley (2001), sharpened NFL result for function classes;
   Igel & Toussaint (2003), *On classes of functions for which No Free Lunch
   results hold*: for the finite uniform setting, NFL holds on a class iff the
   class is closed under permutation of the input domain.
3. Blackwell (1951/1953), comparison of experiments / value of information:
   decision-relevant information cannot worsen Bayes risk when the decision
   maker may condition its action on that information.

The candidate GMI contribution is **not** any of those theorems. It is their
explicit use as a governance theorem for Section D: identify the structural
side-information, prove that it has decision value, and require an NFL symmetry
control beside every claimed phase law.

## 2. Formal decision theorem frozen before execution

Let `W` be a finite world set with distribution `mu`, `M` a finite morphology
set, and `L(m,w)` a scalar registered lifecycle loss. Let `Z=phi(w)` be a
pre-outcome descriptor.

Define

```text
R0 = min_m E[L(m,W)]
RZ = min_delta E[L(delta(Z),W)]
   = E_Z min_m E[L(m,W) | Z].
```

### Prediction T1 -- conditional free-lunch inequality

The witness must confirm on its finite examples and the document must prove:

```text
RZ <= R0.
```

Strict inequality is predicted exactly when no single morphology lies in the
conditional argmin set for almost every positive-mass descriptor cell.
Equivalently, if

```text
intersection_{z: P(Z=z)>0} Argmin_m E[L(m,W)|Z=z]
```

is empty, then descriptor-conditioned selection is strictly better than every
constant morphology.

This theorem is a finite decision/value-of-information statement. It does not
contradict NFL because NFL corresponds to a distribution/class whose symmetries
make the descriptor uninformative for algorithm choice.

## 3. Exact NFL negative control frozen before execution

Domain for the control:

```text
X = {0,1,...,7}
Y = {0,1}
F_all = all 2^8 Boolean functions X -> Y, uniformly weighted.
```

Two non-revisiting black-box search policies are frozen:

```text
LOW_FIRST  = 0,1,2,3,4,5,6,7
HIGH_FIRST = 7,6,5,4,3,2,1,0
```

Performance after `q` calls is the best value observed so far.

### Prediction NFL-1

For every `q=1..8`, the exact performance distribution and exact mean over
`F_all` are identical for LOW_FIRST and HIGH_FIRST.

This is the required negative control. If it fails, the witness is wrong.

## 4. Structured free lunch frozen before execution

Two structured subfamilies are frozen, with equal prior mass.

```text
UP_t(x)   = 1[x >= t],  t in {0,...,8}
DOWN_t(x) = 1[x <= t],  t in {-1,...,7}
Z in {UP, DOWN}
```

The all-zero member is included in each family (`UP_8`, `DOWN_-1`).

At one query:

- HIGH_FIRST is predicted to obtain value 1 on 8/9 UP worlds and 1/9 DOWN
  worlds;
- LOW_FIRST is predicted to obtain value 1 on 1/9 UP worlds and 8/9 DOWN
  worlds.

### Prediction FL-1

Without the descriptor `Z`, either constant policy has expected one-query value

```text
1/2.
```

Conditioning on `Z` and choosing HIGH_FIRST for UP and LOW_FIRST for DOWN has
expected one-query value

```text
8/9.
```

The strict free-lunch gap is therefore frozen as

```text
8/9 - 1/2 = 7/18.
```

This is the headline "break": not a violation of NFL, but an exact measurement
of how much advantage appears when a registered structural distinction breaks
the NFL symmetry.

## 5. Frozen morphology grammar

The held-out phase witness uses Boolean obligations on five bits (`n=5`, 32
inputs). Candidate names below are mechanism descriptions, not architecture
families.

All candidates are verified exhaustively on all 32 inputs before being admitted.
A wrong candidate is infeasible, not merely expensive.

### M0 -- `full_map`

- persistent cells: `2^n`;
- description/install units: `2^n`;
- serve operations/query: `1`;
- exact for every obligation.

### M1 -- `xor_fold`

Represents an affine GF(2) function by bias plus active input positions.

- persistent cells: `1 + s`, where `s` is active support size;
- description/install units: `1+s`;
- serve operations/query: `s`;
- exact only when the obligation has algebraic degree <= 1.

The descriptor is **algebraic degree/support**, not the label "linear model".

### M2 -- `default_exceptions`

Stores the majority response plus every input requiring the minority response.

- `k = min(#0,#1)`;
- persistent cells: `1+k`;
- description/install units: `1+k`;
- serve operations/query: `2` (membership test + response);
- exact for every obligation.

The descriptor is **minority cardinality**, not the label "retrieval".

### M3 -- `count_step`

Returns one response below a cut in Hamming weight and the other at/above it.

- persistent cells: `2` (cut + polarity);
- description/install units: `2`;
- serve operations/query: `n` (count the bits);
- exact only when some Hamming-weight step matches the obligation exactly.

The descriptor is **minimum Hamming-weight-step residual**, not the label
"threshold network".

### M4 -- `count_step_plus_exceptions`

Uses the best Hamming-weight step plus exact correction keys.

- let `e` be the minimum number of errors made by any count step;
- persistent cells: `2+e`;
- description/install units: `2+e`;
- serve operations/query: `n+1`;
- exact for every obligation after storing the `e` corrections.

This is called "hybrid" only after the result; the search representation itself
contains no family label.

## 6. Resource / verifier contract frozen before execution

The physical coordinate vector for a candidate at horizon `Q` is

```text
(persistent_cells,
 lifecycle_ops)
```

with

```text
lifecycle_ops = description/install units
              + exhaustive_verification_units
              + Q * serve_ops_per_query

exhaustive_verification_units = 2^n = 32
```

for every candidate. Verification is therefore charged and common, rather than
silently free.

A hard memory budget is applied **before** Pareto comparison. A candidate over
budget is infeasible.

Pareto dominance is frozen as ordinary coordinatewise dominance:
`a` dominates `b` iff it is no worse in both coordinates and strictly better in
at least one. There is no scalar price vector and no post-outcome weighting.

## 7. Pre-outcome structural signature under test

For the frozen grammar, record only:

```text
algebraic_degree
algebraic_support_size_if_degree_le_1
minority_count
best_hamming_weight_step_residual
```

plus the already registered `(E,R,V,H)` coordinates.

### Prediction S-1 -- coarse ecology collision

Four held-out obligations below use the same `n=5`, same verifier, same query
horizon and the same hard memory budget `R_mem=8`, but require four different
unique feasible Pareto morphologies. Therefore `(E,R,V,H)` **without** the
obligation-structure signature is predicted to be insufficient for exact
morphology selection at this scope.

### Prediction S-2 -- repaired sufficiency

The four-value structural signature above is predicted to separate the four
held-out decisions without an architecture-family label.

This is the planned answer to the contributed triage: the original coarse map is
falsified, but a morphology-relative structural quotient is testable rather than
forbidden by NFL.

## 8. Held-out five-bit obligations frozen before the witness exists

All use `n=5`, `Q=16`, exhaustive verification, and hard memory budget 8.

### W-A -- affine sparse support

```text
y(x) = x0 XOR x2 XOR x4
```

Predicted unique feasible Pareto morphology: `xor_fold`.

### W-B -- singleton residual

```text
y(x) = 1 iff x = 10101, else 0
```

Predicted unique feasible Pareto morphology: `default_exceptions`.

### W-C -- symmetric count step

```text
y(x) = 1 iff HammingWeight(x) >= 3
```

Predicted unique feasible Pareto morphology: `count_step`.

### W-D -- count step with one local defect

```text
y(x) = 1 iff HammingWeight(x) >= 3,
then flip the output only at x=00000.
```

Predicted unique feasible Pareto morphology: `count_step_plus_exceptions` with
`e=1`.

If any of those predictions is false, retain the failure and do not rewrite the
world.

## 9. Analytic horizon phase predictions frozen before execution

Remove the tight memory cap (`R_mem=64`) and vary query horizon `Q`. Generic
exception storage is allowed to compete; this is intentionally a stronger
parent than pairwise rule-vs-table comparisons.

For a candidate with description size `d` and serve cost `c`, versus `full_map`,
common verification cancels and the pairwise crossing solves

```text
d + Q c = 32 + Q.
```

But the **frontier-entry** boundary may be later if a third morphology dominates
`full_map` at the pairwise tie. The frozen predictions below include that
stronger-parent effect.

### P-A -- W-A frontier transitions

Predicted exact Pareto sets:

```text
Q <= 13:       {xor_fold}
Q in {14,15}:  {xor_fold, default_exceptions}
Q >= 16:       {xor_fold, default_exceptions, full_map}
```

### P-B -- W-B frontier transitions

```text
Q <= 30:       {default_exceptions}
Q >= 31:       {default_exceptions, full_map}
```

### P-C -- W-C frontier transitions

```text
Q <= 5:        {count_step}
Q in 6..15:    {count_step, default_exceptions}
Q >= 16:       {count_step, default_exceptions, full_map}
```

### P-D -- W-D frontier transitions

```text
Q <= 3:        {count_step_plus_exceptions}
Q in 4..16:    {count_step_plus_exceptions, default_exceptions}
Q >= 17:       {count_step_plus_exceptions, default_exceptions, full_map}
```

These boundaries were derived algebraically from the frozen resource equations,
not measured from code.

## 10. Remint and search-algorithm predictions

### R-1 -- disjoint surface remint

Apply bit-coordinate permutation

```text
pi = (2,4,1,0,3)
```

to all four held-out obligations. The structural signature and Pareto sets are
predicted to be unchanged up to the renamed active positions / exception key.

### A-1 -- selector independence

Two independently implemented frontier selectors must agree exactly:

1. exhaustive all-pairs dominance census;
2. incremental skyline insertion in a different candidate order.

A disagreement is an assay defect, not a scientific result.

## 11. Falsifiers

This tranche is falsified or weakened if any occurs:

1. NFL-1 fails on the uniform all-function control;
2. FL-1 does not yield the frozen `7/18` conditional advantage;
3. one of W-A..W-D does not recover its frozen morphology under `R_mem=8`;
4. `(E,R,V,H)` alone happens to identify a common optimal morphology across the
   four collision worlds, defeating S-1;
5. any P-A..P-D frontier transition differs from its frozen boundary;
6. remint changes the scientific verdict;
7. the two frontier selectors disagree;
8. the witness requires architecture words to choose a candidate;
9. any result is promoted to a universal theorem over all obligations or all
   future morphology classes.

## 12. Claim ceiling before execution

No #602 Section D box is checked by this freeze alone.

Possible positive terminal after execution:

```text
NFL_SYMMETRY_CONTROL_REPRODUCED
STRICT_FREE_LUNCH_FROM_REGISTERED_STRUCTURE_SUPPORTED
COARSE_D_MAP_FALSIFIED_AND_STRUCTURAL_REPAIR_SUPPORTED_AT_FINITE_SCOPE
PROSPECTIVE_PHASE_BOUNDARIES_CONFIRMED_OR_FAILED_AS_FROZEN
```

Never authorized by this tranche:

```text
NO_FREE_LUNCH_THEOREM_FALSE
UNIVERSAL_BEST_MORPHOLOGY
COMPLETE_UNBOUNDED_ECOLOGY_SCHEMA
REAL_SCALE_GMI_PHASE_LAW
```
