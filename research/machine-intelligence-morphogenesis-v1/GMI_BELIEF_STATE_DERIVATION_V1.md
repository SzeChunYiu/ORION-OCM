# Belief states, Bayesian update, and the posterior/point-estimate line (B13)

Date: 2026-09-14. Lane: machine-intelligence-morphogenesis-v1.
Witness: `gmi_microscope/belief_state_witness.py`.
Receipt: `microscopes/results/STAGE_BELIEF_STATE_V1.json`.
Executed on `laptop-billy`; receipt md5-verified. Reproduced in CI.

CSR-1 says a machine holds one state per distinction it must still make. When
what matters is **latent** and observations are noisy, the distinctions that
survive are distinctions between *posteriors*.

> A belief state is not a modelling choice. It is the quotient on a partially
> observed world.

Exact rational arithmetic throughout — no sampling, no floating point.

## The belief state is the quotient, and the update is what keeps it

| history length | histories | distinct beliefs | collapsed |
|---:|---:|---:|---:|
| 2 | 4 | 3 | 1 |
| 3 | 8 | 4 | **4** |
| 4 | 16 | 5 | **11** |

Histories grow as `2^n` while distinct beliefs grow far more slowly: **order is
forgotten, counts are not.** The belief state is exactly what survives the
quotient, and the update rule is not a borrowed primitive — it is the
bookkeeping that keeps a posterior normalised, written out.

## When a point estimate is insufficient

Two actions: `a1` pays only under `A`; `a2` pays under `B` or `C`.

| belief (A,B,C) | MAP | MAP acts | full acts | agree |
|---|---|---|---|---|
| **(2/5, 3/10, 3/10)** | A | `a1` | **`a2`** | **✗** |
| (9/10, 1/20, 1/20) | A | `a1` | `a1` | ✅ |
| (1/2, 1/4, 1/4) | A | `a1` | `a1` | ✅ |
| (1/5, 2/5, 2/5) | C | `a2` | `a2` | ✅ |

The point estimate fails on one of four, losing **1/5** of expected payoff. It
fails exactly where the mode is a *minority* of the mass — `A` is the single
most likely hypothesis at 2/5 while `B` and `C` together hold 3/5.

> A point estimate is sufficient when the mode carries the decision, and
> insufficient when the decision is carried by the rest of the mass. **That is a
> property of the payoff and the belief together, never of the belief alone.**

## Factorization under conditional independence

| joint | factorizes | factored cost | full cost |
|---|---|---:|---:|
| independent | ✅ | **6** | 9 |
| diagonal | **✗** | — | **9** |

Factoring stores 6 numbers against 9, and is cheaper whenever it is **legal**.
The diagonal joint shows legality is a fact about the distribution, checked here
rather than assumed — the same shape as the distributed-versus-symbolic result
in B4.

## Posterior maintenance versus an amortized predictor

*A first version compared a one-time table against a per-step update count and
found maintenance cheaper at every horizon. That is not a crossover, it is two
different units.* Both are charged over a lifetime of `Q` queries about
arbitrary histories: `compiled = 2^n + Q`, `maintain = Q·n`.

| horizon `n` | queries `Q` | compiled | maintain | cheaper |
|---:|---:|---:|---:|---|
| 2 | 64 | **68** | 128 | **compile** |
| 4 | 64 | **80** | 256 | compile |
| 10 | 4 | 1028 | **40** | **maintain** |
| 10 | 64 | 1088 | **640** | maintain |

> A machine facing long histories maintains a belief not because it is
> principled but because **the table it would otherwise build does not fit**.
> Where the table does fit, the table is correct.

Note the direction against B16. There the repeated quantity was *queries over a
fixed world*, so compiling amortized and won at high reuse. Here the repeated
quantity is *history length*, which multiplies what a table must hold, so
compiling loses as the horizon grows. Same accounting; different thing repeated.

## Neutral recovery, with no `BAYES_UPDATE` and no distribution family

| belief | needs full posterior | recovered state |
|---|---|---|
| (2/5, 3/10, 3/10) | ✅ | **full posterior** (3 numbers) |
| (9/10, 1/20, 1/20) | ✗ | **point estimate** (1 number) |

> A machine that keeps a distribution was not *given* one. It was charged for
> the smallest state that still acts correctly, and that state happened to be a
> distribution.

## Scope

- Three hypotheses, two observations, fixed exact likelihoods. The *shape* of
  each result is the claim; the specific thresholds depend on these numbers.
- The `(1/2, 1/4, 1/4)` row agrees between MAP and full posterior via an exact
  tie in expected payoff, broken by action order. It is reported as agreement
  and should not be read as a margin.
- Section 5 prices replaying the history on every query. A machine consuming a
  single stream incrementally pays `n` once, not `Q·n`, and maintenance then
  dominates everywhere — that is a different ecology, not a different law.
- Conditional independence is checked on two joints, not sampled over a family.

**Falsifier.** Exhibit a partially observed world where two histories reaching
the same posterior must still be told apart; or a belief where the mode is a
minority of the mass and the point estimate still acts correctly under every
payoff.
