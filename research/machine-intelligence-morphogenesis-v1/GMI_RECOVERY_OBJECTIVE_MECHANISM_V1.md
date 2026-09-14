# Why neutral rediscovery fails, and the one change that flips it

Date: 2026-09-14. Lane: machine-intelligence-morphogenesis-v1.
Witness: `gmi_microscope/recovery_objective_witness.py`.
Receipt: `microscopes/results/STAGE_RECOVERY_OBJECTIVE_V1.json`.
Reproduced in CI by `test_gmi_derivation_witness_reproduction.py`.

Addresses the standing negative shared by checklist items 22, 23 and 35:
neutral rediscovery `NOT_EARNED`, 0 of 264 K4 cells green.

## The negative this is about, stated fairly

`RV-377-109` did the hard thing properly. It froze the budget-starvation defence
as a prediction, ran at ten times the budget, and the defence **failed**:

| verdict | 20 000 | 200 000 | Δ |
|---|---:|---:|---:|
| `THEORY_RED` | 159 | 159 | +0 |
| `THEORY_RED_NULL_DOMINATES` | 69 | 69 | +0 |
| `INCONCLUSIVE_GRAMMAR` | 36 | 36 | +0 |

Not one cell moved. The budget *was* plumbed through — search winner cost
changed on 194 of 264 cells — yet the frozen-target witness margin moved on
**none**. The freeze recorded the conclusion it had named in advance: the
failure is structural, not budgetary, and extra compute is evidence *against*.

Nothing below reverses that. It is a correct negative at its scope.

## The clue is the direction

The damaging part is not that recovery failed. It is that the gap **widened**:
more search made the non-target frontier materially cheaper while leaving the
target exactly where it was. A search that is merely under-resourced does not
behave that way. A search optimising *the wrong objective* does exactly that.

Checklist item 35 names the suspect in one phrase: the objective is
**"reward-only"**, without **"charged burden"**. This witness tests that phrase.

## The smallest setting in which a family can be missed

A realization precomputes `k` of `K = 8` steps and carries `w` wasted build
steps:

```
build cost = k + w        paid once
serve cost = K - k        paid on every one of r queries
```

The target family is the compiled end, `k ≥ 6`. Two objectives, differing in
nothing else:

```
A   BUILD-CHARGED ONLY    minimise  k + w
B   FULL LIFECYCLE        minimise  k + w + r·(K − k)
```

## Recovery flips on the objective alone

| reuse `r` | A: build-charged | B: full lifecycle |
|---:|---|---|
| 1 | missed | missed |
| 2 … 32 | missed (all) | **recovered** (all) |

**A recovers the family on 0 of 9 ecologies. B recovers it on 8 of 9.**

The single miss under B is the control that matters: at `r = 1` there is no
reuse, so the compiled family genuinely *should not* be recovered. B is not an
objective that simply prefers the target — it prefers it exactly when the
ecology makes it correct. The witness aborts if B recovers everywhere.

## The widening signature, reproduced

At `r = 16`, tracking an anytime search's incumbent:

| budget | winner `(k,w)` | cost under A | distance to family |
|---:|---|---:|---:|
| 3 | (2,1) | 3 | 4 |
| 6 | (0,1) | 1 | 6 |
| 54 | (0,0) | **0** | **6** |

Eighteen times the budget made the incumbent **strictly cheaper** (3 → 0) and
**strictly further** from the family (4 → 6). That is the `RV-377-109` shape:
a frontier that cheapens while the target does not move.

Under B, the same candidates in the same order recover the family from budget 6
onward. **Under A no budget ever helps**, because the objective does not reward
the thing the family exists to provide.

## The guarantee is about the endpoint, not the trend

Under A the cost is `k + w`, so a completed search lands at `k = 0` — verified
by exhaustion over all 54 candidates at every reuse: **0 of 9 ecologies** put a
completed A-search in the family.

But the incumbent path is **not monotone**. It runs
`cost 5/dist 5 → 3/dist 4 → 1/dist 6 → 0/dist 6`: the distance *falls* before
it rises. So the guarantee holds at the endpoint and not along the way, which
carries a practical warning for reading K4 at partial budget:

> **A cell drifting toward its target is not evidence that more search would
> reach it.** The approach can reverse.

## The threshold is PVR-3's, not a new constant

Under B the family is first recovered at `r = 2`. One extra precomputed step
costs 1 to build and saves 1 per query, so this is the same break-even that
governs consolidation, chunking, teaching, culture and concept formation —
`S < (r−1)(C−U)`. Nothing new is introduced to make recovery work.

## What this establishes, and what it does not

**Established.** If a recovery objective under-charges the benefit the target
family provides, then recovery fails at every budget, the frontier cheapens
while the target is immobile, and the failure is structural in exactly the
sense `RV-377-109` demonstrated. All three are reproduced here by exhaustive
enumeration, and the same search recovers the family when only the objective
changes. The threshold at which it flips is PVR-3's, not a new constant.

**Tested against the real K4 objective, and EXCLUDED.**
`gmi_k4_resource_native_v4.lifecycle` charges nine channels including
`serve_compute_latency`, `state_storage`, `update_retraining`, `communication`
and `verification`, and divides `development_compute` by the reuse multiplier.
It is a lifecycle objective, not a build-only one. **The mechanism proposed
here is therefore not the explanation of the 0-of-264 result**, and this
document does not reclassify a single K4 cell.

What it did do is say what signature to look for. Reading the cost model for
that signature found a different and deeper cause, recorded separately in
[`GMI_K4_COST_STRUCTURE_ROOT_CAUSE_V1.md`](GMI_K4_COST_STRUCTURE_ROOT_CAUSE_V1.md):
the K4 cost model contains **no substitutions at all** — no channel can be
bought with another — so there is no cost structure for any mechanism to
exploit, whatever the objective charges.

**Falsifier for this document.** Exhibit an objective that charges lifecycle
cost and still fails to recover the family in an ecology with reuse above the
break-even.

**Status.** Retained as a derivation about objectives in general, and as the
record of a hypothesis that was proposed, tested against the real instrument,
and refused. It is not evidence about K4.
