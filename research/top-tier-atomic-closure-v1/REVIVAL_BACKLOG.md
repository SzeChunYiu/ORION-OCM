# Revival Backlog — engineering the negatives

Artifact: `REVIVAL_BACKLOG_V1.json`. Owner issue: #277. Opened 2026-09-10, append-only, non-final.

## Why this exists

The standing doctrine is that **a negative is a lead, not a dead end**. When any result, test or model
fails, the first response is *diagnose → attribute to one stage → apply the matching lever → re-test
against the strongest parent* — **before** the negative is filed or the lane moves on. A one-pass
negative filed as terminal is a defect.

Two rules bound that duty in opposite directions, and both matter:

- **`PARENT_SUFFICIENT` is a success terminal.** Never engineer past a parent that genuinely owns the
  function. The revival duty applies to mechanism negatives, not to parent-sufficiency.
- **A regime-conditional positive is intermediate, not terminal.** It demands a further iteration that
  either extends the working regime or fixes the failing one.

And the hard constraint on all of it: **never tune an outcome positive.** Any improvement must be earned
by a genuine mechanic change, re-tested against the strongest parent, with every cost charged.

## The ten

| ID | Negative | One-stage attribution | Lever | Status |
|---|---|---|---|---|
| RV-1 | CEGAR never beats direct search (D20, `PARENT_SUFFICIENT`) | abstraction **construction**, not search | incremental refinement | **closed, two boundaries located** |
| RV-2 | `CANNOT_CHECK_NEGATION_PRESENT` (D19) | missing instrument: positive-only `N[X]` | negation-aware semiring | queued |
| RV-3 | substitution beats recomputation by only 7% (D19) | world scale — single solve dominates | scaling curve on LUNARC | queued |
| RV-4 | T72 oracle: 11 no-op targets, 6 sources never revoked (D19) | oracle targeting defect | re-target to true sources | dispatched |
| RV-5 | e-graph amortised ratio 0.418 (D21) | rule set has no optimum-quality headroom | rule family where order matters | queued |
| RV-6 | 84.4% "fail T3 generalization" (GS-R2) | **the endpoint was not measuring generalization** | delete the ranking | **closed, defect reclassified** |
| RV-7 | GSA2 unbeaten on throughput (GS-R2) | cost side — dedup pays 2× cpu | canonical-form dedup | queued |
| RV-8 | library acquisition exceeds later savings (#165 H1) | not re-attributed this window | after strongest-parent comparison | queued |
| RV-9 | freeze chain has no CI gate (D6 A2) | no enforcement gate exists | amendment-aware verification workflow | queued |

## RV-1 closed, and it is the model for the rest

The lever **worked** — incremental refinement genuinely removed 16.0% of the construction overhead, with the
equivalence guard clean at 95 checks and round counts identical to rebuild on all 30 worlds — and it was
**still not enough**. That is the outcome the doctrine is built to handle, and it produced two boundaries
rather than one disappointment.

**Single query, structural.** A sound may-abstraction must read every concrete transition, because omitting
one is exactly the under-approximation already shown to yield false certificates. So its setup is Ω(|E|)
while direct search is O(|V|+|E|) with early exit. The one-time build alone costs 1.267× the entire direct
search and already meets or exceeds it on 21 of 30 worlds.

**Multi query — amortisation self-defeats.** No crossover exists in the frozen grid and none is projected
beyond it. Refinement drives the partition toward discrete: final blocks reach 81.2% of states, 6 of 30
worlds go fully discrete, and after refinement stops the abstraction costs 12.966 operations per query
against direct search's 11.738. *The mechanism that makes an abstraction accurate enough to answer queries
is the same one that destroys its size advantage*, and the `n − k` bound guarantees it terminates at or near
discrete.

D21 reached the same shape independently from a different mechanism — a shared e-graph amortising to 0.418
aggregate, winning only on the largest world. Two lanes converging on where sharing does and does not repay
is stronger evidence about the boundary than either alone.

## RV-8 and RV-10 came from the parent scan, and both change what happens next

**RV-8 stopped being unattributed.** Stitch (POPL 2023) localises DreamCoder-style library-learning cost
to the **abstraction stage specifically**, which under one-stage attribution names H1's failing stage
rather than indicting library learning in general. Separately and more usefully: H1 is a **rediscovery of
Minton's utility problem** in a new substrate, with Soar's expensive chunks as the direct symbolic
ancestor. The utility-problem literature may already state *when* acquisition repays — in which case the
crossing condition is a regime boundary to locate, not a result to rediscover.

**RV-10 is a defect with external proof that it occurs, not a hypothesis.** The Darwin Gödel Machine's own
agent deleted the logging its hallucination detector depended on, and that lineage then *outscored* the
lineage that solved the task honestly — reported by its own authors. That is the "`B_exec` falls because
verification was weakened" hostile family, instantiated for real in a published self-improving system.
This repository has no gate that would catch it. Building one is a missing-gate task, not a revival.

Two companions from the same scan carry the same weight. **ANIL** shows freezing MAML's entire body barely
changes performance — the canonical demonstration that a *signature mechanism can be inert*, which is
exactly why the causal coordinate demands a knockout rather than a pre/post comparison. **NELL's** precision
on newly promoted beliefs fell 90 → 71 → 57 percent with compounding error conceded by its authors, which
attacks the persistent-lineage claim directly.

## Two entries deserve emphasis

**RV-6 turned out to be a measurement defect, not a finding.** The largest retained negative in the
repository was never a scientific result. `SURVIVOR_T3_GENERALIZATION_*` is a hard-gate read and an **exact
deterministic function of one genome bit** — `NOT can_check` ⟺ `FAIL`, across 100,693 of 100,693 survivors,
zero false positives, zero false negatives. So "84.4% fail T3 generalization" means, without exception,
"84.4% carry no consistency checker."

The cause is a predicate asymmetry, verified from source. T2's `scoped_failure` and T3's
`t3_conflict_refusal` both accept `can_check OR F_arch == hierarchical_fibred`. T3's `t3_doubt_probe`
accepts `can_check` **only**, with no fibred route, so a checker-free organism passes T2 and is
*structurally* unable to pass that one T3 family.

Two things corroborate it. The held-out key carries no information: over 18 derived sub-keys every survivor
is either 0/18 or 18/18 feasible and **zero** fall in between, and an empirical-risk estimate cannot be
perfectly bimodal over 18 independent draws. And our own lever package gamed it — `GSA6_DP` and `GSA6_ALL`
have identical distinct-yield at 5802.0 per seed, yet DP alone returns 6,768 checker-bearing exclusive
survivors against ALL's 1,773.

The obstruction is operational, not structural. The unranked viable pool is 84.7% checker-bearing against
the survivor set's 15.6%, a 5.44× depletion with disjoint intervals, while the T2 gate *favours*
checker-bearing organisms by 27.7×. The search's own ranking manufactured the depletion, and deleting it
recovered 2.21× the absolute hold count at 4.7% of the compute. **The 84.4% figure must never again be
quoted as a generalization result.**

**RV-1 is revivable precisely because of how well D20 attributed its own failure.** "Every CEGAR round
rebuilds the abstraction from the full concrete transition relation" names an *implementation property,
not a law*. Rebuilding from scratch is a choice. If incremental refinement still loses, the
`PARENT_SUFFICIENT` becomes *earned at a deeper level* and is filed as a stronger success, not tuned.

## LUNARC

Observed 2026-09-10: `nuc` **96 of 96 nodes idle**, 7-day limit — the primary target. `lu48` had 10 idle
of 186; `hep` is saturated with unrelated work. RV-6, RV-3 and RV-7 are the cluster-appropriate studies.

> **Hard prohibition:** never make a network connection from LUNARC to any external service. Pure offline
> compute only — stage in via `git`/`scp`, compute, bring results back.

## Discipline for every entry

Freeze the protocol and push it in a commit containing **no result file** before running. A post-freeze
change requires a recorded supersession with cause and a re-run. Report every iteration of the chain,
including the ones that failed.
