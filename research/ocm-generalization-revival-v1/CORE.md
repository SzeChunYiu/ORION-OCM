# RV-A: GS-R2 T3 generalization negative — revival lane (START HERE)

Target: `research/ocm-morphology-zoo-v1/results/GS_R2_AGGREGATE.json`
(freeze `55a96624…`, key `GSHeldoutT3V1:4d0a1487e4427449`), which records
`SURVIVOR_T3_GENERALIZATION_FAIL: 85025` against `…HOLD: 15668` over
`n_distinct_survivors: 100693` — 84.44% of distinct T2-viable survivors.

## The one-sentence result

The endpoint is not a generalization measurement. `SURVIVOR_T3_GENERALIZATION_*`
is `evaluate_t3(...)["feasible"]`, a hard-gate read, and it is an exact
deterministic function of a single genome bit:

> **`NOT can_check` ⟺ `SURVIVOR_T3_GENERALIZATION_FAIL`**, 100693/100693,
> false positives 0, false negatives 0.

So "84.4% fail T3 generalization" is, without exception, the statement
**"84.4% of distinct T2-viable survivors carry no consistency checker."**

## Attribution — ONE stage: the T2/T3 correctness-predicate asymmetry

| battery | family | correctness predicate |
|---|---|---|
| T2 `lifetime2.py:142` | `scoped_failure` | `can_check` **OR** `F_arch == hierarchical_fibred` |
| T3 `t3_ecology.py:178` | `t3_conflict_refusal` | `can_check` **OR** `F_arch == hierarchical_fibred` |
| T3 `t3_ecology.py:134` | `t3_doubt_probe` | `can_check` **only** — no fibred route |

`can_check = constraint_solver ∈ units OR L == scoped_nogood`, identically
defined in both batteries. `scoped_failure` is the only T2 family that can set
`harmful_transfers`, so a checker-free organism can satisfy T2 `GATE_CORRECTNESS`
**only** by being `hierarchical_fibred`. T3's `t3_doubt_probe` does not accept
that route, charges one `harmful_transfer`, and flips `GATE_CORRECTNESS`.

Confirmed in the data: **every one of the 85025 FAILs is `hierarchical_fibred`**,
and there are zero survivors that are checker-free and not fibred.
See [ATTRIBUTION.md](ATTRIBUTION.md).

## The held-out key carries no information

The m≥104 battery replicates the frozen key over 18 deterministically derived
sub-keys (`m_total = 153 ≥ crossover m* = 104`). Across all 100693 survivors:

| verdict | feasible calls | n |
|---|---|---|
| FAIL | 0 / 18 | 85025 |
| HOLD | 18 / 18 | 15668 |
| any | 1..17 / 18 | **0** |

Zero draw-variance. An empirical-risk estimate cannot be perfectly bimodal over
18 independent instance draws. The PAC-Bayes slack (`eps(104) = 0.22393 ≤ bar
0.224507`) is therefore being applied to a degenerate estimator: non-vacuity of
the bound does not make the endpoint an estimate of transfer risk.

## Adjacent result: the lever package bought yield with the rejected route

Exclusive distinct survivors per R2 arm, checker-bearing fraction (Wilson 95%):

| arm | levers | n excl. | can_check | fraction |
|---|---|---|---|---|
| GSA5P_fixed | none (parent replication) | 12095 | 2114 | 0.1748 [0.1681, 0.1817] |
| GSA6_NG | novelty gate | 11884 | 2372 | 0.1996 [0.1925, 0.2069] |
| GSA6_DP | dedup promotion | 32879 | 6768 | 0.2058 [0.2015, 0.2102] |
| GSA6_SC | cumulative surrogate | 8856 | 1456 | 0.1644 [0.1568, 0.1723] |
| **GSA6_ALL** | all three | 32770 | 1773 | **0.0541 [0.0517, 0.0566]** |

`GSA6_DP` and `GSA6_ALL` have **identical** distinct-yield (5802.0/seed), yet DP
alone returns 6768 checker-bearing survivors against ALL's 1773. The committed
terminal `LEVER_PACKAGE_BEATS_SURROGATE_PARENT_ONLY` credits the package on
distinct-yield; at equal yield the package is 3.8× more depleted on the axis the
T3 gate actually reads. See [COMPOSITION.md](COMPOSITION.md).

## Receipts

- `results/RVA_A1_ATTRIBUTION.json` — exact cross-tab, single-bit predictor.
- `results/RVA_A2_DRAW_INVARIANCE.json` — draw invariance + per-arm composition.
- [ITERATIONS.md](ITERATIONS.md) — the full chain, including the steps that failed.
- `hpc/rva_attrib.py`, `hpc/rva_drawinv.py`, `hpc/rva_timing.py` — offline
  reductions, run on LUNARC `lu48` (`-A lu2026-2-51`).

## Iteration 2 verdict: the ranking machinery owns it, not the gate

Lane-distributed null (`lane_hetero`, 2.4 M draws, every draw evaluated at T2,
all ranking machinery disabled — `FREEZE_RVA_ITER2.json`, frozen before the run):

| population | n | can_check | fraction | Wilson 95% |
|---|---|---|---|---|
| unranked viable (phenotype-deduped) | 616698 | 522090 | **0.84659** | [0.84569, 0.84749] |
| GS-R2 survivors | 100693 | 15668 | **0.15560** | [0.15338, 0.15785] |

Frozen decision rule → **`RANKING_OWNS_DEPLETION`**, intervals disjoint, ratio
5.44×. The T2 gate favours checker-bearing organisms by **27.7×**
(`P(viable | can_check)` 0.6590 against 0.0652). So the search starts from a
viable pool that is 84.7% checker-bearing and returns a survivor set that is
15.6% checker-bearing: **the depletion is manufactured by the search's own
ranking and promotion, not by the morphology space and not by the gate.**

The obstruction is operational, not structural. See [NULL.md](NULL.md).

## Iteration 3 verdict: the negative is recovered by deleting the ranking

All three ladder rungs are composition-neutral — `lane_hetero` draws carried
T0 → T1 → T2 with no ranking give 0.8398 checker-bearing at **every** rung, and
every T0-viable organism clears T1 and T2. So sampling and all three gates hand
on 84%; the ranking and its parent-pool feedback own the entire drop to 15.6%.

Arm **L1 unranked breadth** — same ladder, same lane, same seeds, same
`t0_budget = 45000`/seed, no rank function, no promotion selection, no parent
pool, survivors phenotype-deduped across seeds exactly as the R2 aggregate does:

| | CPU-h | distinct T2-viable | **distinct T3-HOLD** | hold rate |
|---|---|---|---|---|
| **L1 unranked breadth** | **0.0237** | **41284** | **34628** | **0.8388** [0.8352, 0.8423] |
| GS-R2 pooled (all five arms) | 1.1137 | 100693 | 15668 | 0.1556 |
| best single arm (GSA6_DP) | 0.1825 | 34773 | 7856 | 0.2259 |

**2.21× the absolute hold count of the entire campaign, at 4.7% of its compute**
(104× per CPU-hour). Shuffle-equal-n null: 6423.9 expected under the R2 rate at
L1's n, 34628 observed, z = 382.95. Not selectivity — L1 admits *more*
candidates than any arm and holds at a higher rate.

Against the frozen parents on their own metrics, L1 gives 6891.3 distinct
T2-viable per seed against `GSA2_hetero`'s 5062.7 (1.36×) and 1743228
morphologies per CPU-hour against 354046 (4.92×), both computed the way the R2
aggregate computes them. `PARENT_SUFFICIENT` does not apply: no parent owns this
function.

Why the ranking is not paying for itself: the surrogate `allocation_score` costs
8.04 T0-evaluation units per candidate, while η = 3 halving saves about 4.8
T0-units per viable candidate at a measured T2/T0 tier cost ratio of only 4.60.

See [RESULT.md](RESULT.md).

## Open

Whether a *repaired* rank key can beat unranked breadth. The rank
`allocation_score = P(viable) × predicted dev_score` embeds
`dev_score = solved_fraction − 0.5·cost`, and T2's `scoped_failure` charges the
`hierarchical_fibred` route 0.4× consistency work, so the cost term prices the
checker route out. The archive cannot compensate because `refusal_rate` is a
gate-induced dead axis (verified). A rank that covers the correctness axis is
the next candidate, and it must beat L1, not merely the R2 arms.
