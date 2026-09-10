# RV-A iteration 3: the revival — removing the ranking recovers the negative

Parent: [CORE.md](CORE.md). Receipts: `results/RVA_L1_AGGREGATE.json`,
`results/RVA_TIER_COST.json`, `results/ladder/`, `results/l1/`.

## Step 1: all three ladder rungs are exonerated

The iteration-2 null measured T2 viability directly, but the search runs a
T0 → T1 → T2 successive-halving ladder. The per-rung probe closes that gap:
`lane_hetero` draws, no ranking, no promotion, no parent pool, every organism
that clears a rung carried to the next, 6 seeds × 120000 draws.

| rung | distinct viable (summed over seeds) | can_check | fraction |
|---|---|---|---|
| T0 | 110297 | 92624 | 0.8398 |
| T1 | 110297 | 92624 | 0.8398 |
| T2 | 110297 | 92624 | 0.8398 |

Every T0-viable organism clears T1 and T2 — the counts are literally identical —
so **T0 is the binding rung and none of the three gates changes the
composition.** Sampling delivers 84%, and all three gates hand on 84%.

## Step 2: what the ranking costs and what it saves

Measured on the frozen stack (`results/RVA_TIER_COST.json`, 4000 timed calls per
tier):

| operation | seconds | in T0-evaluation units |
|---|---|---|
| T0 evaluation | 9.97e-05 | 1.00 |
| T1 evaluation | 2.59e-04 | 2.59 |
| T2 evaluation | 4.59e-04 | 4.60 |
| T3 evaluation | 1.14e-04 | 1.14 |
| **surrogate `allocation_score`** | **8.02e-04** | **8.04** |

With η = 3 the halving avoids about ⅔ of T1 evaluations (1.73 T0-units) and ⅔ of
T2 evaluations (3.07 T0-units) per viable candidate — roughly **4.8 T0-units
saved**, against **8.04 T0-units spent** ranking each one, at each of the two
promotion sites. Successive halving's benefit scales with the tier cost ratio,
and here that ratio is only 4.60. **The ranking costs more than the halving
saves, before any question of what it selects.**

## Step 3: the matched-budget control

Arm **L1 unranked breadth**: `lane_hetero`, the same T0 → T1 → T2 ladder, no
rank function, no promotion selection, no parent pool, at exactly the GS-R2
arms' own `t0_budget_per_seed = 45000` and seeds 0..5, survivors deduplicated by
phenotype across seeds exactly as `GS_R2_AGGREGATE.json` deduplicates its arms.

| arm | CPU-h | distinct T2-viable | distinct/seed | morph/CPU-h | **distinct T3-HOLD** | hold rate | hold/CPU-h |
|---|---|---|---|---|---|---|---|
| **L1 unranked breadth** | **0.0237** | **41284** | **6891.3** | **1743228** | **34628** | **0.8388** | **1462177** |
| GSA5P_fixed | 0.1889 | 13504 | 2251.3 | 71486 | 3001 | 0.2222 | 15886 |
| GSA6_NG | 0.2262 | 13210 | 2202.0 | 58404 | 3233 | 0.2447 | 14294 |
| GSA6_DP | 0.1825 | 34773 | 5802.0 | 190527 | 7856 | 0.2259 | 43044 |
| GSA6_SC | 0.2447 | 10324 | 1723.2 | 42186 | 2353 | 0.2279 | 9615 |
| GSA6_ALL | 0.2714 | 34655 | 5802.0 | 127710 | 2823 | 0.0815 | 10403 |
| **GS-R2 pooled** (all five) | **1.1137** | **100693** | – | – | **15668** | **0.1556** | **14069** |

L1's hold rate 95% interval is [0.8352, 0.8423].

**Absolute count, which is the figure that matters:** L1 returns **34628**
distinct T3-holding phenotypes against the entire five-arm GS-R2 campaign's
**15668** — **2.21×** — while spending **0.0237 CPU-hours against 1.1137**,
i.e. **2.13%** of the campaign's compute, a **47.0× reduction**. Per CPU-hour
the ratio is **104×**.

> **Corrected 2026-09-10.** This line originally read "4.7% of the campaign's
> compute" — the 47× reduction transposed into a percentage. The error
> understated the result. See [CORRECTIONS.md](CORRECTIONS.md) C1; every other
> figure in this document was re-derived from the receipts and is sound
> (`results/RVA_NUMBER_AUDIT.json`, 17 checks, 1 failing).

## Step 4: against the two frozen parents, on the parents' own metrics

| | distinct T2-viable per seed | morphologies per CPU-hour |
|---|---|---|
| L1 unranked breadth | **6891.3** | **1743228** |
| GSA2_hetero (strongest parent) | 5062.7 | 354046 |
| GSA5_surrogate | 2233.3 | 72150 |

L1 beats the strongest frozen parent by **1.36×** on distinct-yield per seed and
**4.92×** on morphologies per CPU-hour — the two metrics the parents were frozen
on and on which the committed terminal rule was selected. So
`PARENT_SUFFICIENT` does not apply: no parent owns this function.

Both figures are computed the way the R2 aggregate computes them, which matters:
`mean_distinct_per_seed` there is the per-seed distinct count **then averaged**
(`aggregate_gs_r2.py` builds `dist_per_seed` and takes its mean), not the
cross-seed-deduped total divided by seeds. L1's per-seed counts are
[6829, 6837, 6757, 7058, 6891, 6976] → 6891.3; the deduped-total-over-seeds
figure would be 6880.7, and the receipt reports both. `morphologies_per_cpu_hour`
is the cross-seed-deduped union over the arm's total CPU on both sides, so that
one was already like-for-like.

## Step 5: the null, and why this is not selectivity

The selectivity trap is a lever that raises the hold *rate* by admitting fewer
candidates. L1 admits **more** candidates than every arm (41284 distinct viable
against the best single arm's 34773) *and* holds at a higher rate, so it cannot
be that artifact. The shuffle-equal-n null makes it explicit:

| | |
|---|---|
| H₀ | L1's survivors hold at the GS-R2 pooled rate 0.15560 |
| expected holds at L1's n = 41284 | 6423.9 (sd 73.65) |
| observed holds | **34628** |
| z | **382.95** |

Per-seed T3-hold counts are [5748, 5702, 5693, 5924, 5736, 5859], mean 5777.0.

## Step 6: a third independent confirmation of the attribution

On L1's 41284 survivors — a population that never touched the R2 search, the
R2 ranking or the R2 parent pool — `can_check_equals_hold` is **true**: the
distinct `can_check` count and the distinct T3-HOLD count are both 34628, with
zero exceptions. The A1 equivalence now holds on the R2 survivors (100693), on
the preflight resample through the real evaluation path (4000), and here.

## What is and is not claimed

**Claimed.** On the metrics the zoo programme actually reports and selected its
terminal rule on — distinct T2-viable yield, morphologies per CPU-hour, and
T3-eligible survivors — the surrogate-ranked successive-halving apparatus is
dominated by unranked breadth at matched T0 budget, on every axis at once. The
84.4% T3 failure is recovered to 16.1% by deleting the ranking, and the absolute
hold count rises 2.21× over the whole campaign at 2.13% of its cost
([corrected](CORRECTIONS.md) from 4.7%).

**Not claimed.** That unranked breadth is a better *optimizer*. L1 maximizes
nothing; it enumerates viable morphologies broadly. If the programme's objective
were maximal `dev_score` rather than diverse viable yield, this comparison would
have to be redone against that objective. What the evidence shows is that the
ranking machinery was not buying the objective the campaign was scored on, and
was actively inverting the composition on the held-out endpoint.

**Not a gate change.** No gate was loosened or tightened, no threshold moved, no
T3 key re-drawn or consulted to design L1, no re-split after seeing results. L1
uses the frozen hard gates verbatim and charges every evaluation it makes.

## Cost and provenance

All runs on LUNARC `lu48` under `-A lu2026-2-51`, single core per shard, no
outbound network connection from any node. L1: 6 array tasks, 85.3 CPU-seconds
total. Ladder probe: 6 tasks, 213.5 CPU-seconds. Tier-cost probe: 1 task.
