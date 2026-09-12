# RV-377-123 — FREEZE: an exact capability law for unseen machine forms, and its test

Frozen BEFORE the run. **A single pilot cell was run to check the harness and is disclosed in
§4.**

## 1. Why this world, after `RV-377-122`

`RV-377-122` failed its own sanity gate: a generic machine on 22 heterogeneous worlds scored
`FULL = 0.000` on 10 of them and its query counts were so small that one query was 4–10
percentage points. The repair is **not** 22 bespoke adapters. It is **one world whose protected
variable, channel content and query count are all controlled**, so that TI-1 yields a
closed-form number instead of a comparison between two noisy quantities.

## 2. The world and the law

`W` is a uniformly random bitstring of length `L`, drawn **after** the machine is frozen, so
`M = 2^L`. Development `D` reveals `r` distinct index/bit pairs chosen uniformly. A query asks
for the bit of `W` at a uniformly drawn index.

`P` and `R` are independent of `W`. An index never revealed therefore carries no information
any machine can possess: on a revealed index the answer is determined, on an unrevealed index
every machine is reduced to a coin. Hence for **any** machine `F(P,D,Q,A,R)`:

```
accuracy(r)  ≤  r/L + (1 − r/L)·½  =  ½ + r/(2L)
```

with equality for a machine that stores `D` and guesses elsewhere.

## 3. Why this is a prediction about an UNSEEN form

The law **names no architecture**. It is a statement about a *channel class* — the set of all
machines whose only access to `W` is `D` and `Q` — and it bounds every member of that class,
including machines nobody has built or described. A machine that beat it would have to obtain
bits of `W` from `P` or `R`, contradicting their independence by construction.

So the form being predicted is defined by the theory rather than inherited from history, and
its capability is predicted **quantitatively and in advance**: `½ + r/(2L)`, exactly, for every
`r`.

Five machines are instantiated to test it, including three that are *deliberately wrong* about
the world's structure (`majority`, `extrapolate`, `parity` all assume regularities that are not
there). None has seen `W`.

## 4. Disclosed pilot — one cell

```
L = 64, r = 32, 4000 queries, seed 1
  bound            0.7500
  table machine    0.7548     (+0.7 sigma)
  ablated table    0.4305     (development reminted from an independent world)
```

The ablated arm falls *below* ½ because a machine that trusts foreign development answers
confidently and wrongly on the indices it believes are revealed. That is expected and confirms
the ablation removes information rather than merely adding noise.

## 5. Frozen predictions

Grid: `L = 64`, `r ∈ {0, 4, 8, …, 64}` (17 values), **5 seeds**, **4000 queries** per cell,
5 machines = 425 measurements. At `p ≈ 0.75`, one sigma is 0.0068, so 3σ ≈ 0.021.

| id | prediction | falsifier |
|----|-----------|-----------|
| **Q1** | **No machine exceeds `½ + r/(2L)` by more than 3σ in any of the 425 cells.** This is TI-1's ceiling over the whole channel class. | any cell above bound + 3σ |
| Q2 | The `table` machine **meets** the bound within 3σ at every `r` — the ceiling is tight, not merely an upper bound. | table below bound − 3σ at any `r` |
| Q3 | With development reminted from an independent world, every machine scores **≤ ½ + 3σ**. | any ablated cell above |
| Q4 | Measured `table` accuracy is **linear in `r/L`** with slope 0.5 ± 0.02 and intercept 0.5 ± 0.02, R² > 0.99. | any coefficient outside, or R² ≤ 0.99 |
| Q5 | At least one of the three structurally-wrong machines scores **strictly below** `table` at some `r` — cleverness without information does not substitute for information. | all three match table everywhere |

**Q1 is the falsifiable core.** If any machine beats the bound, either TI-1 is false or this
world leaks, and both are reportable. Q2 is what makes the law a *prediction* rather than a
vacuous inequality: an upper bound no one approaches predicts nothing.

## 6. What a confirmation licenses, and what it does not

Confirming Q1–Q5 would establish that **GMI contains at least one law that predicts, in
advance and in closed form, the capability of a class of machine defined without reference to
any existing architecture, and that the prediction is met experimentally and is tight.**

It would **not** rescue the K4 property-vector programme (`RV-377-121`: cross-seed agreement
0.0 %), would not establish anything about architectures outside this channel class, and would
not extend beyond the exact-identification obligation used here. The law is narrow. Its virtue
is that it is *true, tight, and about machines that do not yet exist* — which is what the K4
claim was supposed to be and was not.

---

# RV-377-123 — ADJUDICATION: the law holds, is tight, and one of my predicates was mis-specified

## First pass — 425 cells, `L=64`, 17 values of `r`, 5 seeds, 4000 queries

| id | outcome |
|----|---------|
| Q1 | **FALSIFIED as written** — 80 cells above `bound + 3σ` |
| Q2 | **CONFIRMED** — the `table` machine meets the bound at every `r`, 0 shortfalls |
| Q3 | **FALSIFIED as written** — 111 ablated cells above `½ + 3σ` |
| Q4 | **CONFIRMED** — slope **0.5016**, intercept **0.5003**, **R² = 0.999815** |
| Q5 | **CONFIRMED** — wrong-structure machines fall below `table` on 9 cells |

## The Q1/Q3 failures are my error, not the theorem's — diagnosed, not assumed

Every Q1 violation is a constant or near-constant machine at small `r`. `always_zero` scores,
on a **fixed** `W`, exactly the fraction of 0-bits in that `W`:

```
seed 5: fraction of 0-bits = 0.5625  -> always_zero scores 0.5625
seed 1: fraction of 0-bits = 0.4688
seed 2: fraction of 0-bits = 0.3594
sd of that fraction over L=64 bits = 0.0625
```

The observed 0.5693 is **1.1 standard deviations of the draw of `W` itself**. It is not
information about `W`; it is `W` happening to contain more zeros than ones.

**TI-1 bounds `E_W[accuracy]`** — the expectation over the protected draw. I tested it
**pointwise against a single draw**, with a σ computed from query sampling only, ignoring the
much larger variance contributed by `W`. The predicate was wrong. The same applies to Q3.

## Corrected test — 40 independent `W` draws per cell

| `r` | bound | table | always_zero | majority | extrapolate | parity |
|---|---|---|---|---|---|---|
| 0 | 0.5000 | 0.5005 | 0.5007 | 0.5007 | 0.5005 | 0.5007 |
| 16 | 0.6250 | 0.6236 | 0.5007 | 0.6263 | 0.6344 | 0.6102 |
| 32 | 0.7500 | 0.7487 | 0.5007 | 0.7464 | 0.7564 | 0.7508 |
| 48 | 0.8750 | 0.8763 | 0.5007 | 0.8719 | 0.8824 | 0.8768 |
| 64 | 1.0000 | 1.0000 | 0.5007 | 1.0000 | 1.0000 | 1.0000 |

```
Q1'  E_W[acc] <= bound + 3 s.e.  : violations = 0  -> CONFIRMED
Q3'  E_W[ablated] <= 0.5 + 3 s.e.: violations = 0  -> CONFIRMED
```

**Zero violations across all machines and all `r`.** And `always_zero` sits at **0.5007 at
every `r`** — flat across the entire development range. A machine that ignores the channel
extracts nothing from it no matter how much is offered, which is the law's content made visible.

## What is established

> **`TI_1_EXPERIMENTALLY_VERIFIED_ON_REAL_MACHINES` = TRUE at registered scope.**
>
> For the channel class *"machines whose only access to a post-freeze protected `W` is
> development `D` and query `Q`"*, the capability ceiling `accuracy ≤ ½ + r/(2L)` is
> **correct** (0 violations over 40 draws × 5 machines × 9 values of `r`), **tight** (the
> `table` machine attains it at every `r`), and **linear to R² = 0.999815** with the predicted
> slope 0.5 and intercept 0.5.

This is a capability prediction **about machines that do not exist**. The class is defined by
its information channels, not by any architecture; the bound applies to every member including
ones never built or described; it was derived before measurement; and it is met, not merely
respected.

Three of the five machines were deliberately wrong about the world's structure. None beat the
bound. `extrapolate`, `majority` and `parity` differ from `table` only in how they guess where
they have no information — and guessing differently never buys accuracy beyond `½ + r/(2L)`.

## Flagged rather than dismissed

`extrapolate` sits consistently *above* the bound in the point estimate (0.5738 vs 0.5625 at
`r=8`; 0.6344 vs 0.6250 at `r=16`) while staying inside 3 s.e. The excess is small and the test
passes, but it is **consistent in sign across `r`**, which random error need not be. It is
recorded here rather than waved through, and a larger-draw re-test is registered. If the bias
survives more draws, either `extrapolate` exploits an index-adjacency regularity this world
does not intend to contain, or the world leaks through query-index locality.

## Scope — what this does NOT do

It does **not** rescue the K4 property-vector programme; `RV-377-121` stands at 0.0 %
cross-seed agreement. It does **not** extend beyond this channel class, beyond
exact-identification obligations, or to `L ≠ 64`. It says nothing about *which* architecture a
search will find — only about what any architecture in the class can achieve.

The law is narrow. Its virtue is that it is **true, tight, quantitative, verified, and about
machines that do not yet exist** — which is what the K4 claim was supposed to be and was not.
