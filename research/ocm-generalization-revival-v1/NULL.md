# RV-A iteration 2: the ranking machinery, not the gate, owns the depletion

Parent: [CORE.md](CORE.md). Protocol: `FREEZE_RVA_ITER2.json` (sha256
`e9566c31…`, committed with no result file at `e39b82d6`, before the run).
Receipts: `results/RVA_N_NULL_AGGREGATE.json`, `results/null/RVA_NULL_s{0..5}.json`.

## The measurement

Draw from `morphology.gs_bound.lane_hetero` — the lane every GS-R2 arm used —
seeds 0..5, 400000 draws each (2.4 M total), evaluate **every** draw at T2 with
all ranking machinery disabled: no novelty archive, no novelty gate, no
surrogate, no successive halving, no dedup promotion, no cross-round promotion.
Frozen hard gates unchanged. Endpoint `P(can_check | T2-viable)`.

## Result

| population | n | can_check | fraction | Wilson 95% |
|---|---|---|---|---|
| unranked viable, phenotype-deduped | 616698 | 522090 | **0.84659** | [0.84569, 0.84749] |
| unranked viable, raw draws | 638543 | 534968 | 0.83779 | [0.83689, 0.83870] |
| **GS-R2 survivors** (comparator) | 100693 | 15668 | **0.15560** | [0.15338, 0.15785] |

Frozen decision rule → **`RANKING_OWNS_DEPLETION`**. The null lies strictly
above the comparator; the intervals are disjoint by more than two orders of
magnitude in units of their own widths. The ratio is 5.44×.

## The gate does the opposite of depleting checkers

| | viable | dead | P(viable) |
|---|---|---|---|
| `can_check` | 534968 | 276825 | **0.6590** |
| not `can_check` | 103575 | 1484632 | **0.0652** |

Odds ratio favouring the checker-free route: **0.0361**, i.e. the T2 admission
gate favours checker-bearing organisms by **27.7×**. Overall viable rate 0.2661.

So the search begins from a viable pool that is 84.7% checker-bearing and
returns a survivor set that is 15.6% checker-bearing. **The ranking and
promotion machinery inverts the gate's preference.** The 84.4% "T3
generalization failure" is manufactured by the search's own selection, not by
the morphology space and not by the admission gate.

## Frozen falsifiers

**Impossible cell — passed.** Zero viable organisms were both checker-free and
not `hierarchical_fibred`, across all 2.4 M draws. This is an independent
confirmation of the T2 correctness-route mechanism on a population that never
touched the R2 search.

**Sampling-rate check — flagged, investigated, resolved.** The measured
`P(can_check)` over legal draws was 0.33825 against the frozen analytic
expectation 0.37037. The follow-up probe (`results/RVA_SAMPLER_PROBE.json`,
400000 fresh draws) shows the frozen expectation was derived at the **genome**
level while the run measures the **active-unit** level read by
`_capabilities` on the compiled organism, and `compile_genome` prunes dead
units:

- genome-level rate 0.3704325 vs frozen analytic 0.37037037 — agrees to 6×10⁻⁵
  against a Monte-Carlo standard error of 7.6×10⁻⁴;
- active-level rate 0.338025 — matches the null's 0.33825;
- `active_true_genome_false` = 0 (pruning can only remove the capability);
- 14628 draws had a `constraint_solver` pruned as dead;
- bound constants confirmed: `max_extra_units` 5, 12 extra unit types, 9
  learning families, `scoped_nogood` in bound, `n_extras` uniform on {2,3,4,5}.

The sampler is exactly `lane_hetero`; the falsifier's expected constant was
mis-specified. Recorded in `FREEZE_RVA_ITER2_SUPERSESSION.jsonl`: no arm, seed,
endpoint or decision rule changed, and no re-run was required. The endpoint
itself uses the active-level bit, which is the bit both batteries actually read.

## The comparison is like-for-like

`results/RVA_COMPARATOR.json` recomputes the survivor comparator at the
active-unit level over **all** 100693 distinct survivors, not a sample: genome
and active levels disagree on **0**, and active-level `can_check` equals the T3
HOLD count exactly (15668 = 15668). The comparator is therefore measured on the
same bit as the null.

## What this licenses and what it does not

It licenses: the obstruction is **operational, not structural**. A lever aimed
at the ranking/promotion stage has a named target and real headroom — the viable
pool it draws from is 84.7% checker-bearing.

It does not license: any claim about which sub-stage of ranking is responsible.
All five R2 arms sit between 0.054 and 0.206, including `GSA5P_fixed`, which
runs no revival lever at all — so the depletion is present in the common base
pipeline (surrogate-ranked successive halving) and merely modulated by the GSA6
levers. Attributing within the ranking stage is iteration 3.

## Cost

2.4 M T2 evaluations, 6 array tasks on LUNARC `lu48` under `-A lu2026-2-51`,
wall time under 5 minutes. No outbound network connection from any LUNARC node.
