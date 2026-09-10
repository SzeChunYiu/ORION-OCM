# RV-A revival chain — every iteration, including the ones that failed

Parent: [CORE.md](CORE.md). Kept because a revival chain is only auditable if
the steps that went wrong are visible alongside the ones that worked.

| # | step | outcome |
|---|---|---|
| 0 | Orientation over the committed GS-R2 artifacts | The verdict is `evaluate_t3(...)["feasible"]`, a gate read. Solved fraction is not monotone in the verdict (0.8 holds, 0.9 fails), which ruled out a threshold artifact immediately. |
| 1 | A1 attribution | `NOT can_check ⟺ FAIL`, 100693/100693, fp 0, fn 0. Every FAIL `hierarchical_fibred`. |
| 2 | A2 draw invariance | FAIL 0/18, HOLD 18/18, nothing between. The held-out key carries no information. |
| 3 | Preflight P1–P4 | Verdict reproduction, determinism and the capability-bit cross-check all exact on 4000; `refusal_rate` confirmed a gate-induced dead axis. |
| 4 | Freeze iteration 2 | Committed with no result file at `e39b82d6`, sha256 `e9566c31…`. |
| 5 | Lane-distributed null | 0.84659 unranked against 0.15560 observed → `RANKING_OWNS_DEPLETION`. |
| **5a** | **Frozen falsifier flagged** | Sampling rate 0.33825 against the frozen analytic 0.37037. **Investigated, not waved away**: the expectation was derived at genome level, the run measures active-unit level after dead-unit pruning. A 400000-draw probe confirmed both levels. Recorded in `FREEZE_RVA_ITER2_SUPERSESSION.jsonl`; endpoint and decision rule unaffected, no re-run needed. |
| **5b** | **Gap found in my own claim** | The null measured T2 viability *directly*, but the search runs a T0 → T1 → T2 ladder, so the T0 and T1 rungs were **not** exonerated. Caught before the claim was pushed. |
| 6 | Per-rung ladder probe | 0.8398 at every rung, identical counts — all three gates composition-neutral, T0 binding. Gap closed, claim strengthened. |
| 7 | Tier-cost probe | `allocation_score` costs 8.04 T0-units; η = 3 halving saves ≈4.8 at a T2/T0 ratio of 4.60. The ranking does not pay for itself. |
| 8 | L1 unranked breadth, matched budget | 34628 distinct T3-HOLD in 0.0237 CPU-h against the campaign's 15668 in 1.1137. Null z = 382.95. |
| **8a** | **First family checker returned `false`** | It asserted that no family *other than* `t3_doubt_probe` ever fails. That is stronger than the mechanism claims — a minority of both classes fail `chain_transfer`/`interrupted_plan` harmlessly. The **checker** was wrong, not the mechanism. Rewritten to the six claims the mechanism actually makes, keeping the no-alarm case; all six then held with zero violations. |
| **8b** | **Per-seed comparison was not like-for-like** | `mean_distinct_per_seed` in the R2 aggregate is the per-seed count *then averaged*; the L1 figure was the cross-seed-deduped total over seeds. Recomputed to 6891.3. Ratio against `GSA2_hetero` unchanged at 1.36×. |
| **8c** | **Dangling artifact removed** | The exhaustive-census scripts were committed but never ran and named a freeze that was never minted. Removed; the retirement is recorded in [PLAN.md](PLAN.md) as deliberate. |

## Things that were designed and deliberately not run

- **Exhaustive `GS_BOUND_V1` census** (143,881,920 grammars, 20.9 CPU-hours at
  measured rates). Retired at step 8c: a raw ceiling over 1.4×10⁸ grammars is a
  statement about budget rather than bias, and iteration 3 demonstrated headroom
  directly.
- **The `obasis` stratified lane** as a lever. Dropped before any run: its
  analytic `can_check` rate is 0.355, *below* `lane_hetero`'s 0.370, because
  `gs_uniform_sample` draws `n_extras` from {0..5} where `lane_hetero` draws
  from {2..5}. It would have made the composition worse.

## Compute deviation

The brief specified LUNARC partition `nuc` (96/96 idle). The account
`lu2026-2-51` is refused there despite `nuc` appearing in its `sacctmgr`
association list. All work ran on `lu48`, the partition the GS-R2 campaign
itself used. Recorded in `FREEZE_RVA_ITER2.json` under `compute.deviation`.
