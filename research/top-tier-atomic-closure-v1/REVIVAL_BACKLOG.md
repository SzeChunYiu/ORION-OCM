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
| RV-1 | CEGAR never beats direct search (D20, `PARENT_SUFFICIENT`) | abstraction **construction**, not search | incremental refinement | dispatched |
| RV-2 | `CANNOT_CHECK_NEGATION_PRESENT` (D19) | missing instrument: positive-only `N[X]` | negation-aware semiring | queued |
| RV-3 | substitution beats recomputation by only 7% (D19) | world scale — single solve dominates | scaling curve on LUNARC | queued |
| RV-4 | T72 oracle: 11 no-op targets, 6 sources never revoked (D19) | oracle targeting defect | re-target to true sources | dispatched |
| RV-5 | e-graph amortised ratio 0.418 (D21) | rule set has no optimum-quality headroom | rule family where order matters | queued |
| RV-6 | **84.4% of survivors fail T3 generalization** (GS-R2) | **not yet attributed** | determined by attribution | dispatched |
| RV-7 | GSA2 unbeaten on throughput (GS-R2) | cost side — dedup pays 2× cpu | canonical-form dedup | queued |
| RV-8 | library acquisition exceeds later savings (#165 H1) | admission rule, not abstraction cost (FNA-4) | already applied and successful | executed at registered scope |
| RV-9 | freeze chain has no CI gate (D6 A2) | no enforcement gate exists | amendment-aware verification workflow | queued |

## RV-8 and RV-10 came from the parent scan, and both change what happens next

**RV-8's revival had already happened, and the abstraction-stage attribution was wrong.** Checking H1
against our own receipts rather than against the parent literature overturns both halves of the earlier
reading. In `FNA4_RESULTS.json`, the `STITCH` arm carries the **highest** marginal acquisition of any arm —
240,294,343 units against the incumbent's 64,305 — and is still the only arm that pays, so acquisition cost
cannot be the failing stage. The discriminating variable is the **admission rule**: utility-gated admission
reaches −10.5% on the fresh 16-task stream, while recurrence-gated admission is actively harmful (+1149%
Reynolds lgg, +1279% e-graph saturation). Misfire counts isolate it exactly — 451,582 and 286,120 against
`STITCH`'s 16,813 — which is high match cost at near-zero applicability, the term Minton's utility formula
charges and the failure his admission test exists to prevent.

FNA-4's own terminal already records the outcome: `PARENT_SUFFICIENT_FOR_EXPERIENCE_CONSOLIDATION_AT_REGISTERED_SCOPE`,
270,829 < 366,072 units (−26.0%) with every cost charged. **The terminal is `PARENT_SUFFICIENT`** — a classical
stdlib-only parent owns this function, so nothing here is an ORION-OCM-specific result. Two consequences:
#165's disposition table still reports H1 as an unqualified capital negative and no longer matches the
evidence, and the *lifetime* repayment claim remains **projected rather than observed**, since break-even sits
at ~6,123 tasks against a 16-task measured stream.

**The crossing condition is ours, not the literature's.** A primary-source sweep (Minton AAAI-88; Tambe,
Newell & Rosenbloom 1990; Kennedy & De Jong 2003; Gratch & DeJong and Greiner & Jurisica, both AAAI-92) finds
a per-rule break-even inequality and formal conditions for deciding that inequality's *sign*, but no analytic
crossover in N. Tambe et al. give "no explicit guarantees about the benefits of chunking"; Minton names the
gap as future work, writing that "there is no such thing as an average domain". FNA-4 supplies precisely that
missing object as a **(mix, horizon) pair** — a critical same-family share of 11.8–17.0% together with the
~6,123-task horizon — which is a boundary to defend and extend rather than rediscover.

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

**RV-6 is the flagship and it is deliberately unattributed.** 85,025 of 100,693 distinct survivors fail
T3 generalization. Four candidate stages — descriptor overfit, gate leakage, selection pressure, genuine
non-generalizing morphology — must be discriminated *by evidence* before any lever is applied. Applying a
lever first would be exactly the diffuse-effort defect the doctrine forbids. Explicitly forbidden here:
moving a threshold, re-drawing the held-out T3 key, re-splitting after seeing results, or loosening a gate.
A lever that raises the hold *rate* by admitting fewer candidates has improved selectivity, not
generalization, so every claim needs rate, absolute count and a shuffle-equal-n null together.

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
