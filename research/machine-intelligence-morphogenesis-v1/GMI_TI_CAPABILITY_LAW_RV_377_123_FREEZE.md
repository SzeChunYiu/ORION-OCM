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
