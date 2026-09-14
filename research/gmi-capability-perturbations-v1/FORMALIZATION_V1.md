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

## Boundary

These are exact comparative statics for fixed morphology semantics and registered channels. They do not cover compensatory reconfiguration, morphology changes induced by price shifts, unregistered interactions, or open-ended environmental change. Claim ceiling: **G2**.
