# F4 capability perturbation calculus v1

Let each registered capability depend on signed margins `z_i = capacity_i - requirement_i`. At this scope the exact capability predicates are the four already registered threshold predicates for memory, planning, coordination and verified tool use.

## Repricing theorem

With fixed spend `B`, positive unit price `p`, and integer requirement `q`, purchasable capacity is `floor(B/p)`, so the signed margin is

`z(p) = floor(B/p) - q`.

Therefore a price perturbation `p -> p'` predicts the post-change capability by replacing only that margin with `z(p')` and applying the frozen capability predictor. A target flips exactly when the changed margin crosses a load-bearing threshold of its predicate. The registered negative twin changes price without crossing zero and must not flip memory.

## Ablation theorem

Removing `a >= 0` units of a registered capacity changes its margin by

`z' = z - a`.

All other margins are unchanged. Thus any target whose exact predicate does not depend on the ablated axis is invariant at this scope; a load-bearing ablation flips the target only if it crosses its threshold. The registered twin ablates communication while protecting planning.

## Drift theorem

Increasing a registered environmental requirement by `d >= 0` at fixed capacity gives the same margin update

`z' = z - d`.

The causal interpretation differs from ablation, but the exact capability consequence factors through the same signed margin. The registered positive increases verification requirement through zero and flips verified tool use; the twin changes communication requirement while keeping verified tool use unchanged.

## Exact abstention-identifiability theorem

Let the development corpus be a finite set of pairs `(x, y)` ordered componentwise by the five signed margins, and assume the binary capability target is monotone. For a query `z`:

- if there exists a positive development point `x+ <= z`, monotonicity forces `y(z)=1`;
- if there exists a negative development point `x- >= z`, monotonicity forces `y(z)=0`;
- if neither witness exists, the development corpus plus monotonicity does not determine `y(z)`, so the only admissible output is `CANNOT_IDENTIFY`.

The first two witnesses cannot coexist in a monotone corpus: if `x+ <= z <= x-`, transitivity gives `x+ <= x-`, contradicting `y(x+)=1 > 0=y(x-)`.

This gives a logical calibration of abstention, not a probability calibration. The executable control exhausts the probe grid `{-2,0,2}^5` (243 points × 4 targets = 972 cells), checks that the independently reconstructed witness certificate equals the frozen predictor output in every cell, and checks every determinate output against the exact capability oracle. An explicit mixed-extreme query `(memory=2, planning=-2, others=0)` has neither planning witness and therefore must abstain even though the hidden oracle is 0.

## Boundary

These are exact comparative statics for fixed morphology semantics and registered channels. They do not cover compensatory reconfiguration, morphology changes induced by price shifts, unregistered interactions, probabilistic uncertainty calibration, or open-ended environmental change. Claim ceiling: **G2**.
