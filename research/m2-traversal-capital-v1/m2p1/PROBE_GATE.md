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

## Probe depth learned from history — a registered prediction falsified favourably

The depth-3 probe misses every 4-token target (D2: served 0 %; FV8: served 0 %). The
mechanism-derived fix sets the probe depth from **history**: the tiling-token count of the
solved training programs is observable, because history is solved. On D2 that gives
depth 4, `β = 54 240`.

**Registered before the run:** ~50 % hits, expected `B ≈ 61 k`, i.e. *likely negative*.

**Observed:**

| | RESET | parent (interleave) | **PROBE, depth from history** | oracle |
|---|---|---|---|---|
| mean `B`, pure d = 2, n = 60 | 51 459 | 42 089 | **22 685** | 34 313 |
| served | | | **100 %** | |

−55.9 % vs RESET, **−46.1 % vs the strongest parent**, on novel arrangements in the
registered grammar, leak-free. The prediction was wrong because the interleave's 30/60
"strictly better" was read as ~50 % reachability. It is not: under the interleave a
guided hit at `2g > b` counts as *worse* even when guided-alone reaches it at `g < b`.
**The 50/50 alternation masks reachability rather than measuring it.** Recorded as a
falsified prediction, direction favourable.

**Bound obligation discharged** on this run's per-target rows: `B ≤ RESET + β` holds on
all 60 targets, 0 violations, max excess 17 799 < β. Six targets were found later than
baseline would have found them — the probe's honest overhead, inside the bound.

Ledger: conservative does not pay on D2 (break-even 221 vs 60 targets — developmental
solving of 120 length-8 targets is 6.4 M slots); marginal pays (+1.73 M). D2 is a
small-horizon ecology built to test distance, not economics.

## Regime map for deployable gates, as now measured

| ecology | composition depth | probe depth 3 | probe depth = history | task-statement rule |
|---|---|---|---|---|
| FOREIGN_M1 | ≤ 3 | **−26 % vs parent** | coverage-depth: +22 % vs RESET ✗ → cost-depth running | lost |
| E7 (43 targets) | ≤ 3 | **−37 % vs parent** (served 49 %) | — | lost (−7 %) |
| FV6 (foreign vocabulary, 120 targets) | ≤ 3 | **−40 % vs parent** (served 100 %, beats oracle) | — | −30 % vs parent |
| life_3001 / 3003 | ≤ 3 | **−49 % vs parent** | — | (oracle-feature ceiling only) |
| D2 (pure d = 2) | 4 | −7 % vs RESET (overhead) | **−46 % vs parent** | −7.6 % vs parent |
| FV8 | 4 | −15 % vs RESET (overhead) | running | −1 % vs RESET |

E7 adds a fourth ecology where the depth-3 probe wins (RESET 62 935 · parent 58 636 ·
**probe 36 970** · oracle 32 731), recovering 86 % of the oracle gap by serving on
half the targets. The composed gate (probe → rule on a miss) was uninformative at
coverage depth 4 on FOREIGN_M1 — with 92.5 % probe hits the rule almost never engaged —
and is re-evaluated under the cost-depth rule.

The probe with history-learned depth is the strongest deployable form everywhere it has
been run *when the depth is chosen by expected cost*; the coverage rule is retired. The composed gate (probe → rule on miss) is running where the probe misses.
