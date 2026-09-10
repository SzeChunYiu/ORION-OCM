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
- `hpc/rva_attrib.py`, `hpc/rva_drawinv.py`, `hpc/rva_timing.py` — offline
  reductions, run on LUNARC `lu48` (`-A lu2026-2-51`).

## Open

Whether the depletion is owned by the **gate** (frozen physics; structural) or by
**ranking/promotion** (operational) is decided by the lane-distributed null in
[PLAN.md](PLAN.md), not yet run at this commit.
