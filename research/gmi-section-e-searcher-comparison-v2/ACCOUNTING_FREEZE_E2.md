# E2 arithmetic / cache accounting freeze

Date frozen: 2026-09-15.
Authority: #715, after `FREEZE_E2.md` and **before any scored E2 witness execution**.

This supplement closes one accounting detail intentionally left qualitative in the main E2 freeze. It does not change any scientific outcome prediction.

## Shared discrete verifier cache

A searcher pays 32 truth-example touches the first time a discrete affine mask is semantically verified. Re-visiting a previously verified discrete mask uses the frozen exact cache and pays no new truth-example touches, but the proposal/mutation attempt remains charged.

Thus:

```text
truth_example_touches = 32 * unique_discrete_candidates_verified
```

for purely discrete searchers.

For neutral drift at the frozen five-proposal horizon the witness must enumerate all `5^5=3125` mutation-choice paths and report both exact success probability and exact expected number of unique verified masks. No Monte Carlo.

## Rational arithmetic operation rule

For relaxed NAS/DARTS computations, every rational `+`, `-`, `*`, or `/` executed by the registered implementation counts as one `arithmetic_update_op`, independent of operand value. Comparisons, tuple/index access, loop control, hashing/cache lookup and final threshold comparisons are not arithmetic ops.

The implementation must increment the counter at the same source operation that performs the corresponding rational arithmetic. A frozen result number is not sufficient.

## Relaxed prediction counting law

For one example and gate vector `z`:

```text
term_i = 1 - 2*z_i*x_i
p_z(x) = (1 - product_i term_i)/2
```

A loss-only forward example executes:

- 15 ops for five terms (multiply by 2, multiply by `x_i`, subtract from 1);
- 5 multiplications in the registered product loop (including multiplication of initial product 1 by first term);
- 2 ops for `(1-product)/2`;
- 1 subtraction for prediction error;
- 3 ops for square, divide by 32, and loss accumulation.

Total: **26 arithmetic ops/example**.

Therefore ten 32-example endpoint-loss evaluations in the one-shot ablation method use

```text
10 * 32 * 26 = 8320 arithmetic_update_ops.
```

The five endpoint comparisons are not arithmetic ops.

## Exact forward/backward counting law

The DARTS-like exact gradient routine uses the same 26 forward/loss ops per example plus, for each of five gate coordinates:

- four multiplications for the product of the other four terms;
- four ops for `2*error`, multiply by partial product, divide by 32, accumulate gradient.

That is 8 gradient ops/gate = 40 additional ops/example.

Total exact loss+gradient pass:

```text
32 * (26 + 40) = 2112 arithmetic_update_ops.
```

The registered one-step update executes two arithmetic ops/gate (`8*g_i`, then subtract), adding 10:

```text
DARTS arithmetic_update_ops = 2122.
```

The final hard exact verification contributes 32 truth-example touches but no search-update arithmetic under this coordinate.

## Discrete-search reporting

- Uniform random without replacement: no search-update arithmetic; proposal attempts equal verified candidates.
- Strict evolutionary at ten proposals: one start + at most five distinct one-bit neighbors are verified and cached; all ten mutation attempts remain charged; arithmetic update ops = 0.
- Neutral CGP-like drift at five proposals: enumerate all 3125 paths; report exact expected unique candidates / expected truth-example touches, plus exact hit probability. Proposal attempts are exactly five on nonterminal paths and stop at target on terminal paths; expected proposal count must also be derived exactly.

This supplement is part of the E2 pre-outcome authority chain.
