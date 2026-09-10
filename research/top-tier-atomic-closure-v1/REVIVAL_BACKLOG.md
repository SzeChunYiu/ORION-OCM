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

## The nine

| ID | Negative | One-stage attribution | Lever | Status |
|---|---|---|---|---|
| RV-1 | CEGAR never beats direct search (D20, `PARENT_SUFFICIENT`) | abstraction **construction**, not search | incremental refinement | dispatched |
| RV-2 | `CANNOT_CHECK_NEGATION_PRESENT` (D19) | missing instrument: positive-only `N[X]` | negation-aware semiring | queued |
| RV-3 | substitution beats recomputation by only 7% (D19) | world scale — single solve dominates | scaling curve on LUNARC | queued |
| RV-4 | T72 oracle: 11 no-op targets, 6 sources never revoked (D19) | oracle targeting defect | re-target to true sources | dispatched |
| RV-5 | e-graph amortised ratio 0.418 (D21) | rule set has no optimum-quality headroom | rule family where order matters | queued |
| RV-6 | **84.4% of survivors fail T3 generalization** (GS-R2) | **not yet attributed** | determined by attribution | dispatched |
| RV-7 | GSA2 unbeaten on throughput (GS-R2) | cost side — dedup pays 2× cpu | canonical-form dedup | queued |
| RV-8 | library acquisition exceeds later savings (#165 H1) | not re-attributed this window | after strongest-parent comparison | queued |
| RV-9 | freeze chain has no CI gate (D6 A2) | no enforcement gate exists | amendment-aware verification workflow | queued |

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
