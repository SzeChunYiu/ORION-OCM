# The probe gate — a deployable applicability control, and the first conservative-ledger positive

After the [retraction](APPLICABILITY.md) of the answer-derived gate, the replacement had
to satisfy one invariant: **a deployment predicate may read the task statement and the
outcomes of charged actions, never the solution.**

## The mechanism

No fitted rule. For each target, run the **guided stream alone** — library tokens plus
primitives, words of ≤ 3 tokens, every word one charged slot, the same accounting as
`solve` — and stop at the first externally verified hit or at `β = T + T² + T³` slots.
A hit costs what it cost; a miss falls back to `RESET` at `β + b`. Nothing about the
target is read except its coefficients and the outcome of the probe.

This is the `λ = 1` prefix of the mission's `λ(z)` proposal. Its worst case is `b + β`,
which for `T = 16` is `b + 4 368` — far tighter than the registered interleave's `2b`.

## Results

| ecology | regime | served | RESET | parent (always serve) | **PROBE** | oracle (best of RESET/interleave) |
|---|---|---|---|---|---|---|
| FOREIGN_M1 (M1's own partitions) | heterogeneous | 70 % | 29 387 | 19 992 | **14 796** | 11 965 |
| life_3001 (670 targets) | uniform | 100 % | 3 614 | 3 238 | **1 658** | 2 603 |
| life_3003 (669 targets) | uniform | 100 % | 3 647 | 3 242 | **1 633** | 2 625 |

```text
vs the strongest parent :  −26.0 %   −48.8 %   −49.6 %
```

On the 670-target worlds the probe **beats the "oracle"**. That is not a leak: the oracle
is the per-target best of the two *registered* arms, and the probe is a different
integration mode — a hit on the guided stream alone costs ≈ `g`, while the interleave
reaches the same composition at ≈ `2g`. The 50/50 alternation was leaving half the
benefit on the table exactly where the library is good.

The observable-feature gate on the same FOREIGN_M1 run **lost** to always-serve
(22 558 vs 19 992), confirming the retraction: static task-statement features do not
predict applicability; a charged probe action does.

## The ledger — observed horizon, deployable gate

The gate fits nothing, so its marginal and incremental costs are **zero**; `β` is already
inside its `B`. The only chargeable acquisition is developmental solving:

| world | horizon | saved / target | conservative cost | break-even | pays | net |
|---|---|---|---|---|---|---|
| life_3001 | 670 | 1 956 | 929 652 | **475** | **✓** | **+380 889** |
| life_3003 | 669 | 2 014 | 937 922 | **466** | **✓** | **+409 386** |
| FOREIGN_M1 | 40 | 14 591 | 926 665 | 63.5 | ✗ | −343 021 |

**The conservative ledger pays** — every developmental solve charged as pure overhead —
over a horizon that was actually executed. That has not happened before in this
programme. On FOREIGN_M1 the horizon (40) is simply shorter than the break-even (63.5);
marginal and incremental pay there.

An earlier version of the tool charged the probe gate a 715 k fit it never performed;
corrected by pure recomputation on the saved JSON, nothing re-run.

## Bound obligation

`B ≤ b + β` on every target is the probe's own P1-class claim. Per-target rows are now
saved so it is discharged empirically on every future run; the three runs above predate
that and are not certified against it.

## Scope

Two ecology shapes (one uniform, one heterogeneous), one `β` rule, the library's
value already known to be non-negative on average. **Not** shown: behaviour when the
library is harmful on average *and* the probe misses often (the `β` overhead regime), or
`β` derived from anything but `T`.
