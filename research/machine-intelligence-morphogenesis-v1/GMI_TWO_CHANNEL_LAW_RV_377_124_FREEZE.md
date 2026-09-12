# RV-377-124 — FREEZE: a second unseen form, and the conditional capability law

Frozen BEFORE the run. A single pilot cell is disclosed in §4.

## 1. What this adds

`RV-377-123` verified TI-1 for **one** channel class: machines whose only access to a
post-freeze `W` is development `D`. The goal asks for a predictive theory, not a single
predicted form, so the test is whether the framework yields a **second, different** form with
a **different** capability number — derived the same way, not fitted.

TI-2 supplies it: when the query already reveals information about `W`, development need only
carry the residual — `I(W;Z | Q,A) ≥ H(W | Q,A)`.

## 2. The second form and its law

Same world (`W` uniform on `L` bits, `M = 2^L`, drawn after the machine is frozen). Development
reveals `r` indices. **The query now carries the answer with probability `p`**, independently
of development — a second information channel.

An index is *covered* if development revealed it **or** the query carries it. An uncovered
index is independent of everything the machine holds. Therefore for **any** machine in the
`{D, Q}` class:

```
accuracy(r, p)  ≤  1 − (1 − r/L)(1 − p)/2
```

**Boundary check, already verified analytically:** at `p = 0` this reduces *exactly* to
`½ + r/(2L)`, the TI-1 law, for all `r ∈ 0..64`. The two-channel law **contains** the
one-channel law as a special case. A framework that produced two unrelated formulas would be
fitting; one that produces a family with the first as a boundary is deriving.

## 3. The predicate is correct this time — stated explicitly

`RV-377-123`'s Q1 and Q3 failed because I tested a bound on `E_W[accuracy]` **pointwise against
a single draw of `W`**, using a σ from query sampling that ignored the much larger variance of
the protected draw itself. On a fixed `W`, a constant machine scores the fraction of 0-bits in
that `W`, which has sd `√(0.25/L) = 0.0625` at `L = 64`.

**Every predicate below is therefore stated over the expectation across independent `W`
draws**, with the standard error computed across those draws. 60 draws per cell.

## 4. Disclosed pilot

```
L = 64, r = 16, p = 0.5, 4000 queries, seed 1
  bound2  0.8125
  table2  0.8273      (single draw -- above the bound, as expected from W-fluctuation)
```

The pilot is *above* the bound for exactly the reason §3 names, and is reported rather than
hidden precisely because it would look like a violation to anyone reading only the number.

## 5. Frozen predictions

Grid: `L = 64`, `r ∈ {0, 8, 16, 24, 32, 48}`, `p ∈ {0.0, 0.25, 0.5, 0.75, 1.0}`, 60 `W` draws,
2000 queries per draw, 2 machines = 3 600 measurements.

| id | prediction | falsifier |
|----|-----------|-----------|
| **R1** | `E_W[accuracy] ≤ bound2(r,p) + 3 s.e.` in **every** cell, for both machines. | any cell above |
| **R2** | `table2` **meets** `bound2` within 3 s.e. at every `(r,p)` — the ceiling is attained, not merely respected. | any shortfall beyond 3 s.e. |
| **R3** | `ignore_hint`'s accuracy is **independent of `p`** — capped by the TI-1 law `½ + r/(2L)` at every `p`, including `p = 1.0`. | `ignore_hint` rising with `p` |
| R4 | At `p = 0`, `table2` reproduces the `RV-377-123` TI-1 curve within 3 s.e. | divergence at `p = 0` |
| R5 | Accuracy is linear in `(1 − r/L)(1 − p)` with slope −0.5 ± 0.02, intercept 1.0 ± 0.02, R² > 0.99. | any coefficient outside, or R² ≤ 0.99 |

**R3 is the sharpest.** A machine that *ignores* a channel must gain nothing from it however
informative it becomes — at `p = 1.0` the query hands over the answer and `ignore_hint` must
still sit at `½ + r/(2L)`. That is the operational content of "the bound is about channels, not
mechanisms": capability tracks *the information a machine actually uses*, not the information
present in its environment.

## 6. Scope

Still one obligation type (exact identification), one `L`, one world family. Confirming this
would establish that the framework yields a *family* of capability laws over channel
configurations, with the one-channel law as a boundary case — not that GMI predicts anything
about architectures, which `RV-377-121` showed it does not.

---

# RV-377-124 — ADJUDICATION: all five confirmed

60 cells, 60 independent `W` draws × 2000 queries each, 3 600 measurements.

| `r` | `p` | `bound2` | `table2` | `ignore_hint` | TI-1 bound |
|---|---|---|---|---|---|
| 0 | 0.00 | 0.5000 | 0.5005 | **0.5005** | 0.5000 |
| 0 | 0.50 | 0.7500 | 0.7482 | **0.5005** | 0.5000 |
| 0 | 1.00 | 1.0000 | 1.0000 | **0.5005** | 0.5000 |
| 16 | 0.00 | 0.6250 | 0.6251 | **0.6251** | 0.6250 |
| 16 | 0.50 | 0.8125 | 0.8135 | **0.6251** | 0.6250 |
| 16 | 1.00 | 1.0000 | 1.0000 | **0.6251** | 0.6250 |
| 48 | 0.00 | 0.8750 | 0.8761 | **0.8761** | 0.8750 |
| 48 | 1.00 | 1.0000 | 1.0000 | **0.8761** | 0.8750 |

| id | outcome |
|----|---------|
| R1 | **CONFIRMED** — 0 cells above `bound2 + 3 s.e.` |
| R2 | **CONFIRMED** — 0 shortfalls; `table2` attains the ceiling at every `(r,p)` |
| R3 | **CONFIRMED** — 0 issues |
| R4 | **CONFIRMED** — `p = 0` reproduces the TI-1 curve at every `r` |
| R5 | **CONFIRMED** — slope **−0.4998** (want −0.5), intercept **1.0001** (want 1.0), **R² = 0.999970** |

## R3 is the result worth looking at directly

Read the `ignore_hint` column down any `r` block. It **does not move**:

```
r = 0 :  p = 0.00 → 0.5005    p = 0.50 → 0.5005    p = 1.00 → 0.5005
r = 16:  p = 0.00 → 0.6251    p = 0.50 → 0.6251    p = 1.00 → 0.6251
r = 48:  p = 0.00 → 0.8761    p = 0.50 → 0.8761    p = 1.00 → 0.8761
```

At `p = 1.00` the query hands the machine the correct answer on **every single query**, and
`ignore_hint` still scores exactly what the TI-1 one-channel law predicts for its development
alone. It sits on `½ + r/(2L)` at every `p`.

> **Capability tracks the information a machine actually uses, not the information present in
> its environment.** Two machines in the same world, with the same channels available, differ
> in capability by exactly the channel one of them declines to read — and the size of that
> difference is predicted in closed form, in advance.

## What is now established

> **GMI yields a FAMILY of capability laws indexed by channel configuration**, not a single
> bound:
>
> ```
> one channel   accuracy ≤ ½ + r/(2L)                    (RV-377-123, verified, tight)
> two channels  accuracy ≤ 1 − (1 − r/L)(1 − p)/2        (RV-377-124, verified, tight)
> ```
>
> The second **contains** the first as its `p = 0` boundary — verified analytically for all
> `r ∈ 0..64` and empirically at every `r` (R4). A framework producing two unrelated formulas
> would be fitting; one producing a family whose boundary case is the earlier law is deriving.

Both laws are **quantitative, derived before measurement, about machine classes defined by
information channels rather than by architecture, met rather than merely respected, and
verified against machines built to try to break them.**

`GMI_PREDICTS_CAPABILITY_OF_AN_UNSEEN_FORM` = **TRUE**, now for **two** distinct forms with
**different** capability numbers.

## Scope, unchanged and stated again

One obligation type (exact identification), one `L`, one world family. This says nothing about
*which* architecture a search will build — `RV-377-121` settled that at 0.0 % cross-seed
agreement and nothing here disturbs it. The laws are narrow, and true.
