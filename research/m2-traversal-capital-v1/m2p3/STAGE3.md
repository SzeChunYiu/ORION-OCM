# M2-P3 stage 3: the scored replication on package B (2026-09-12)

Freeze: [v2/M2P3_FREEZE_V2.json](v2/M2P3_FREEZE_V2.json) (#417, 8313c699), whose statistics, arms and terminals are
inherited unchanged from [M2P3_FREEZE_V1.json](M2P3_FREEZE_V1.json) (#414). Stage 2b: [STAGE2B.md](STAGE2B.md).
Package A's `CANNOT_CHECK_EMITTER_REJECTED` terminal stands separately and is not re-scored.

## The run

LUNARC job 3600810, one array task per viable world: a fresh dev phase (slots 200 000), a checkpoint, an OS-process
restart, then one arm per process on the world's protected stream. Runner `m2p2_gf/m2p1_runner.py` (sha `7d790905`,
the controller_v5 runner plus the guided-first arms), `methods.py` `e0a05654` (the registered unit, untouched),
`M2_LIB_RULE=interleave`. Every reported success is externally verified by checker C after the restart.

Arms: **`PARENT_GF_D4` (primary)** — the MDL library served guided-first at fixed depth 4, always live, no rule, plain
baseline fallback — against **RESET**; plus `SHUFFLED_HISTORY`, `CONTINUED_OCM`, `PARENT_WITH_MDL`, `PARENT_GFQ_D3`
and `PARENT_GFQ_D4` as controls and descriptives.

## The registered test, and the scorer's validation

Per viable world, H0: `mean(PARENT_GF_D4) >= 0.5 x mean(RESET)` on the same protected targets; one-sided paired
sign-flip permutation on `d_t = GF_t - 0.5 x RESET_t` (10 000 permutations, seed 20260912), Holm-corrected across
worlds at alpha 0.05. Terminal: `C2_REPLICATED_SECOND_AUTHOR_MODEL` iff at least 4 viable worlds and at least 80 % of
them pass. **With exactly 4 viable worlds, all four must pass.** Co-registered point prediction: the median of
`GF_D4 / RESET - 1` is −88 % ± 8 points.

**The scorer was validated on real data before it was used** (LUNARC 3600816,
[stage3/m2p3_score_validation.log](stage3/m2p3_score_validation.log), sha256 `3318449e…`): run on M2-P2's eight worlds
it reproduces the independent pre-freeze calibration exactly — 7 / 8 pass, hc08 fails at Holm p = 0.157, median
−0.8766 — computed there by a different script.

## Result: `C2_REPLICATED_SECOND_AUTHOR_MODEL` (4 / 4)

Scored by [stage3/m2p3_score.py](stage3/m2p3_score.py) (LUNARC 3600991), output
[stage3/M2P3_SCORED.json](stage3/M2P3_SCORED.json) (sha256 `991d89f2…`). Every arm verified every target on every
world, with one exception noted below.

| world | targets | `PARENT_GF_D4` | RESET | ratio | Holm p | passes the 50 % bar |
|---|---|---|---|---|---|---|
| world_3_varied_lengths | 57 | 1 420.4 | 42 237.9 | **−96.6 %** | 0.0004 | **yes** |
| world_4_six_chunks | 34 | 2 609.0 | 22 346.1 | **−88.3 %** | 0.0004 | **yes** |
| world_5_nonlinear_focus | 157 | 11 720.4 | 51 770.5 | **−77.4 %** | 0.0004 | **yes** |
| world_6_full_palette | 43 | 1 602.1 | 36 628.6 | **−95.6 %** | 0.0004 | **yes** |

- **Primary: 4 / 4 viable worlds pass**, which is the strict reading the freeze required once exactly four worlds were
  viable (80 % of 4 means all four). The falsifier did not fire.
- **Co-registered point prediction: held.** Median `GF_D4 / RESET − 1` = **−92.0 %**, inside −88 % ± 8 points.
- **Precondition** (`GF_D4 < RESET`): significant on every world (p = 0.0001), as expected by construction.

**Descriptives, reported and not claimed.**

| world | `CONTINUED_OCM` | `PARENT_WITH_MDL` (interleave) | `SHUFFLED_HISTORY` | `PARENT_GFQ_D3` / `D4` (frequency) |
|---|---|---|---|---|
| world_3 | 1 420.4 | 2 839.7 | 84 461.8 | 9 350.3 / 8 220.5 |
| world_4 | 2 609.0 | 5 216.9 | 44 588.6 | 13 990.9 / *excluded* |
| world_5 | 11 720.4 | 22 069.2 | 102 608.1 | 39 724.8 / 22 895.5 |
| world_6 | 1 602.1 | 3 203.2 | 73 257.2 | 1 116.5 / 1 116.5 |

- **The controller again reduces to the fixed parent.** `CONTINUED_OCM` equals `PARENT_GF_D4` to the slot on all four
  worlds, exactly the aliasing found on M2-P2's worlds (#411). Target (3) is untouched by this study and stays
  FALSIFIED.
- **The interleave identity reappears**: the same-library interleaving parent costs ≈ 2 × the guided-first arm
  (1.88–2.00 ×), and `SHUFFLED_HISTORY` costs ≈ 2 × RESET (1.98–2.00 ×) — shuffled fragments never hit.
- **Library choice still varies by world**: on world_6 the frequency library is 30 % cheaper than MDL (1 116.5 vs
  1 602.1), while on world_5 it is nearly twice as expensive. Consistent with ledger row 56.
- **One excluded arm**: `PARENT_GFQ_D4` on world_4 did not verify every target (38 394.9 over 34 targets) and is
  excluded from the descriptives. It is not the primary and cannot affect the terminal.


## What this licenses, and what it does not

**It licenses**: the C2 claim — a history-mined library, served guided-first, makes new verified cognition markedly
cheaper — **replicates on worlds authored by a second model**, under a registration fixed before the author session,
with an effect-size bar that could have failed (M2-P2's own worlds pass it only 7 / 8) and a point prediction that could
have missed. The worlds are not the first author's: **0 / 6 shape collisions and 0 / 6 identical chunk sets against both
M2-P2 and package A** (median nearest Jaccard 0.333 each), reported next to this terminal as the freeze requires.

**It does not license**:
- **a different model family or human authorship** — the author is claude-haiku-4-5, the same family and harness as this
  lane (M2-P2's author was claude-fable-5-1); independence here is model- and session-level only;
- **OCM-specific superiority** — target (3) stays FALSIFIED: the controller reduced to the fixed guided-first parent on
  all four worlds;
- **anything about M2-P2's frozen terminal**, which stays `CANNOT_CHECK_NO_ADMITTING_WORLD` under its own arm set and
  admission rule;
- **general developmental intelligence or open-endedness.**

The claim rung stays **C2**. What moved is target (1): the C2 benefit is no longer a property of one author model's
worlds.
