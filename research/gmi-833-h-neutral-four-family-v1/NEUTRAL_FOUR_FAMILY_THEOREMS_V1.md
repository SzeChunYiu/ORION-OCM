# Neutral four-analogue theorems v1

## NG-1 — target-independent finite generation

Fix the lower grammar in `neutral_four_family_v1.py::GRAMMAR` before supplying
an obligation. Its constructors denote total functions on `Z3`: projections,
constants, modular sum/product, zero test, generic indexed read, and temporal
delay. Closing the non-temporal constructors through the registered cost bound
depends only on arity and grammar. The unary and binary indexed branches contain
all `3^3=27` and `3^9=19,683` maps respectively before target filtering.
Therefore target responses affect admissibility/selection but not candidate
generation. A stable pre/post grammar digest plus full provenance and denotation
checks makes this stronger than a forbidden-token scan.

Semantic quotienting merges programs with equal complete response tables before
the resource selector runs. Labels are assigned by a separate structural
classifier after selection. This proves common lower-grammar recovery only at
the registered finite scope; it is not universal grammar neutrality.

## STATE-1 — exact persistent quotient and negative regime

For the positive sequential traces, histories ending in `0`, `1`, and `2`
produce distinct next protected responses on the same continuation `0`.
Consequently every exact deterministic realization needs at least three future-
response states. The one-cell update/output `s' = o = s+x (mod 3)` attains the
bound. In the negative traces the protected output is the current symbol, so a
stateless projection is exact and strictly cheaper.

When the environment also exposes full prefix history through ordinary argument
channels, a horizon-`H` replay realization uses `H(H-1)/2` additions, while the
persistent realization uses `H` additions plus one charged cell. Persistence is
strictly preferred exactly when the cell price is below the avoided replay work.

## COEFFICIENT-1 — affine response and decision analogues

Over one `Z3` input, the affine class contains `3^2=9` distinct laws, so an
injective representation of the entire class needs at least two ternary symbols.
The frozen positive response is affine, and the frozen binary response is a
zero-level decision on an affine score. The non-affine unary twin excludes the
affine class. Compact composition and the complete generic indexed map are both
exact; their charged description/serve vectors cross under the two frozen price
regimes. This is a finite coefficient/decision analogue, not a real regression,
classification, fitting, or generalization result.

## LINK-1 — nonlinear link analogue and affine negative

The positive unary response is non-affine but factors as a fixed unary response
map after a one-dimensional affine score. The negative is affine and needs no
nonlinear link. Complete formula enumeration independently confirms the same
classification. The exact linked-law count supplies the registered finite
coding bound, and indexed/composed price reversal supplies a resource crossover.
No exponential-family likelihood, dispersion, optimizer, or statistical GLM
claim follows.

## LIFT-1 — cross-coordinate lifted interaction

For a two-input table define the mixed finite difference

`D(x,y)=f(x,y)-f(x,0)-f(0,y)+f(0,0) (mod 3)`.

Every additively separable response has `D=0`. The positive table has a nonzero
mixed difference and is realized by generic multiplication plus addition. The
negative table is affine/additively separable. The four-coefficient bilinear-
affine class contains `3^4=81` laws and therefore needs four ternary symbols in
the class-wide injective worst case. This is a finite lifted-interaction analogue,
not kernel learning, an RKHS generalization theorem, or a real kernel benchmark.

## NG-REMINT — carrier transport

For every permutation `pi` of `Z3`, transport each primitive denotation by
conjugation, transport inputs and protected outputs by `pi`, and rename delayed
states by `pi`. Structural induction on compositions preserves every response;
the checker covers all six carrier permutations for each frozen static table and
all 54 transition/output cells. This is representation transport, not evidence
that arbitrary grammar presentations have equal search cost.

## Gate consequence

The exact prediction, grammar, recovery, negative, finite-bound, crossover,
held-out, remint, and source-separated-search gates have artifact-level evidence.
The real-scale gate is open for every named family. Hence all four family rows
must remain unchecked. The one-grammar/multiple-bounded-classes row was already
closed by PRs #931–#937 and #951; this package only corroborates it at a separate
registered finite scope and makes no Issue #833 mutation.
