# AI1–AI8 blind-derivation freeze v1

**This freeze predates generator/search/classifier/outcome implementation on this branch.**

## Allowed lower substrate presented to the blind lane

Inputs are two binary coordinates `(x0,x1)`. The arithmetic process presentation may use only:

- input reads `X0`, `X1`;
- integer constants `-1,0,1`;
- `NEG`;
- `ADD`;
- positive-part `POS(z)=max(0,z)`;
- serial/parallel composition.

A second presentation is a stack program with pushes plus the same generic arithmetic semantics. Generic finite tables and equality/conditional rules are allowed only as competing non-arithmetic organizations in the selection stage; they are not labels/rewards for the arithmetic search.

Forbidden from generator/search/evaluator source and features:

`neuron, neural, layer, MLP, dense, backprop, CNN, RNN, convolution, attention, transformer, mixture-of-experts, MoE, target-architecture-id`.

Search/evaluator may see only task input/output behavior, primitive/resource counts, reachability budget and verifier success.

## Frozen tasks

Primary blind task:

`Q_XOR: y = 1 iff x0 != x1`, equivalently `|x0-x1|` on binary inputs.

Matched negative/control task:

`Q_ID: y=x0`.

Prediction P-A: affine/constant-only arithmetic cannot realize `Q_XOR`; adding generic positive-part nonlinearity can.

Prediction P-B: the minimum exact arithmetic construction should contain at least two nonlinear branches combined by aggregation; direct identity should remain simpler on `Q_ID`.

## Frozen post-generation structural fingerprint

The post-generation lane may inspect only architecture-independent graph properties:

- P1: reusable numeric transforms that can be lifted to generic mutable coefficient slots;
- P2: many-to-one aggregation/mixing;
- P3: non-affine transform;
- P4: repeated composition of transforms/aggregation/nonlinearity;
- P5: distributed mutable numeric state after the generic parameter-lift DEV operator;
- P6: updateability from task evidence under generic DEV machinery.

The blind search is **not** rewarded for satisfying P1–P6. Family names are exposed only after candidate generation and scoring.

## Frozen searches/presentations

S1: bottom-up semantic dynamic programming over arithmetic expression trees, ordered by exact primitive size.

S2: breadth-first search over a stack-machine presentation, state = stack of extensional semantics, max stack depth 3.

Both searches stop only on exact external-specification satisfaction or registered budget exhaustion.

## Frozen NN-D1 supplied family

For expressibility only, test the supplied acyclic family

`h1=POS(w10*x0+w11*x1)`
`h2=POS(w20*x0+w21*x1)`
`y=v1*h1+v2*h2`

with all six integer coefficients in `{-1,0,1}` (729 networks; 2,916 input evaluations). Compilation must derive scalar multiplication from repeated `ADD/NEG`, not assume multiply hardware. A second stack presentation must agree.

## Frozen selection/resource model

Raw resource vectors `(build, per_use, memory)`:

- unclassified nonlinear-composition candidate: `(20, 1, 4)`;
- generic equality/conditional rule: `(2, 3, 1)`;
- exact finite table: `(100, 1/2, 100)`.

Raw Pareto vectors remain primary. For the *frozen scalar prediction only*, use

`C_H = build + H * per_use`.

Predicted scalar regimes:

- `H < 9`: RULE;
- `H = 9`: RULE + COMPOSITION tie;
- `9 < H < 160`: COMPOSITION;
- `H = 160`: COMPOSITION + TABLE tie;
- `H > 160`: TABLE.

Held-out evaluation horizons frozen now: `H={1,5,9,10,50,159,160,200}` with predicted winners respectively

`RULE, RULE, {RULE,COMPOSITION}, COMPOSITION, COMPOSITION, COMPOSITION, {COMPOSITION,TABLE}, TABLE`.

Switching-cost prediction for rule/composition with symmetric switch cost `k=4`:

- from RULE, switch to COMPOSITION only for `H>11`;
- from COMPOSITION, switch to RULE only for `H<7`;
- `7<=H<=11` is the registered history-dependent persistence band (with boundary/tie details reported exactly by the outcome checker).

## Frozen strong-claim ceiling

Even if every bounded prediction succeeds, the strongest allowed positive is:

`NN_D1_D2_D3_BLIND_RECOVERY_AT_REGISTERED_BINARY_TOY_SCOPE`.

Forbidden: universal neural inevitability, real-scale neural optimality, all-neural-family derivation, or `GMI_DISCOVERS_ALL_MI`.
