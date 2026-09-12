# Status ledger and next steps — refreshed 2026-09-12

Every figure below is from an executed run on laptop billy, billy-old or LUNARC; nothing
is projected. Claim ceilings are stated per row.

## The four targets

| target | status | strongest evidence | ceiling |
|---|---|---|---|
| **(1) independent ecology** | 🟢 at second-author-model scope | the mined library, served guided-first, beats RESET on all 8 independently authored M2-P2 worlds (−52 … −95 %) and on the M1 lane's partitions; the earlier "beats the strongest parent" figures (M1 −11 %, FV6 −48 %) were against the *interleaving* parents (#411); **M2-P3 replicated the C2 benefit on worlds authored by a second model: 4 / 4, median −92.0 %, prediction held** | M2-P2's frozen terminal is `CANNOT_CHECK_NO_ADMITTING_WORLD`; the author unit is a model proxy of this lane's model family. A second *grammar* (band 3-4, M2-P4) is a separate axis and it **does NOT replicate**: `C2_NOT_REPLICATED_IN_SECOND_GRAMMAR`, k = 2/8 worlds clear the 50 % bar, median −0.4446 (ledger 66). The precondition still holds on 6/8, so the benefit is present but too small; attribution is to selection (ledger 56), not to history |
| **(2) lifetime economics** | 🟢 fixed regimes · 🟡 mixed | 670 targets: marginal 403 / incremental 215 pay, conservative 475 ✓ or 878 ✗ by attribution rule; **three fresh long-horizon seeds pay on the conservative ledger under the hostile rule** — [LONG_HORIZON_LIFETIME.md](LONG_HORIZON_LIFETIME.md); K1-L FRAGILE; K1 on mixed regimes NOT_ESTABLISHED (three stop rules, #407) | registered grammar; the admission rule still refuses on every lifetime world (deployment is by the validated library) |
| **(3) OCM vs strongest parent** | 🔴 **FALSIFIED** at authored-world scope | the fixed guided-first parent (MDL library, depth 4, no rule, no liveness) ties or beats controller_v5 on 8/8 authored worlds; on four the controller reduces to it exactly; the "≈ half" was the guided-first vs interleave serving identity (#411, ledger 55–58) | no OCM-specific residual is claimed anywhere in this lane |
| **(4) general developmental** | 🟢 at `d = 2` (history vs RESET) | benefit does not decay with arrangement distance (D1: 5.2 % at `d=1` → 12.9 % at `d=2`); pure-`d=2` replicated on 5 seeds, all positive (−11.5 … −44.7 %) | a history-induced search benefit, not an OCM-specific one; `d ≥ 3` empty by counting at this `(m, k)` |

## The mechanism that made it move

One controller, four parts, each earned by a negative:

```text
CONTINUED_OCM = library by validation (freq vs MDL)   ← FOREIGN_M1 v1 negative
              → probe, depth by expected cost on held-out validation   ← coverage-depth negative
              → task-statement rule on a miss, RESET while stood down   ← shift-test defect 1
              → liveness: counter advances every target, periodic re-probe   ← shift-test defect 2
```

Invariant carried by every part: **reads the task statement, solved history and the
outcomes of charged actions — never the solution.** The retraction of the answer-derived
gate is what forced it.

**Terminal at this grammar (#411, #412).** Against the absorbed guided-first parent, the parts
after "library by validation" are neutral or negative on every authored world. Library
selection is unavailable from the tuning stream on hc08/hc09 (ledger 56), miss routing costs
about 2× the plain fallback (ledger 57), and the remaining headroom sits at an oracle chunk
set no learner can mine (ledger 58). No further controller revision is registered.

## RSI spine

| level | status | evidence |
|---|---|---|
| L5 self-diagnosis | 🟡 | **0.818** active / 0.758 exhaustive on the 33-case sealed packet ([RSI-7](rsi/RSI7_RESULT.md); C0 9/9, C1 11/13, C2 6/9); residual C3 called C1 |
| L6 improvement of improvement | 🔴 → 🟡 | active G4 → G7: accuracy 0.455 → **0.818**, cost-to-verified-improvement 14.13 → **2.93** ([RSI-7](rsi/RSI7_RESULT.md)); terminal **NO_IMPROVING_SLOPE** still stands over G0 → G7 (G0–G2 rose). The **policy generation** (P1, decision-theoretic stopping) ran and was **falsified**: 0.485 active, *below* the fixed rule ([RSI-6](rsi/RSI6_RESULT.md)) |

## Next experiments, in order

1. ~~**hc02's last guided-first arm** (`PARENT_GFQ_D4`, LUNARC 3598971_2)~~ — **done.** The row is
   recorded (`PARENT_GFQ_D4` 24 669, verifying every target); hc02's GF_best stays `PARENT_GF_D4`
   at 9 745, so no conclusion moved, as predicted.
2. **Target (1): a second authoring regime — partly done, at *model* scope.** M2-P3 re-ran the
   frozen neutral spec under a second author **model**, then the frozen M2-P2 gates and arm set,
   with the falsifier registered before the author session: `C2_REPLICATED_SECOND_AUTHOR_MODEL`,
   4/4 worlds (#421). What that does **not** establish is **family-level** author independence —
   the second author was another model of this lane's own family. A *different-family* author is
   **not reachable from this lane's tooling** (the available agent models are all Claude), so it
   needs an external author supplied by the operator. Stated once here; not re-litigated per cycle.
3. **Not registered, with the reason: a deployed-cost miner.** The coverage diagnostic (#412)
   shows the mined libraries already beat the true chunks on three worlds, and the remaining gap
   is to an unmineable oracle. A better miner is library-learning parent territory
   (DreamCoder / Stitch) and would bear on target (2), not (3).
4. *Carried items, re-checked and resolved — all but one are closed:*
   - **Policy generation P1** (active diagnosis) — **ran, falsified.** Registered "active accuracy
     rises toward 0.758"; observed **0.485**, below the fixed rule. Active diagnosis is bottlenecked
     by the likelihoods, not the policy ([RSI-6](rsi/RSI6_RESULT.md)).
   - **Repair-catalogue revision** — **done.** The stale `C2 → REDUCE_K_OR_RAISE_P` is replaced by
     `C2 → DEPTH_AWARE_DEPLOYMENT`, the repair that actually worked ([RSI-7](rsi/RSI7_RESULT.md)).
   - **RSI-6 re-score** — **done**, and superseded by RSI-7 (active 0.818 at 2.93 per verified
     improvement). Note the file convention: `rsi/RSI{N}_*.json` holds generations G0…G{N-1}, so
     `RSI8_*.json` is RSI-7's own data file, not an unwritten result.
   - **The P=6 analogue** — **CLOSED, and it completed long ago.** Only the *first* run was
     retracted for a budget defect (`CORE.md`); the analogue then ran to completion.
     [D2_REGISTERED_GRAMMAR.md](D2_REGISTERED_GRAMMAR.md) records **6 seeds** (1000–1002,
     1010–1012) under `PRIMS6 = (inc, dec, double, square, triple, neg)`, **all
     `BENEFIT_SURVIVES_AT_D2`**, benefit not decaying from d=1 to d=2 on any seed; records
     `records/EXT_DISTANCE_*.json`. Research analogue, EXACT_MATCH-controlled — not the
     registered grammar. (An earlier revision of this file called it open; that was an absence
     claim made from a retraction line without searching for the result by name.)

5. **Target (1): a second *grammar* — ran, scored, and it does NOT replicate.** M2-P4 widens
   the authored band to 3-4 with chunk count 10-16 over the *existing* substrate (ledger 61; the
   bound `members <= f + k^2` makes k >= 10 necessary). Stage 2 passed every entry gate 8/8, G-SURF
   included, on an independently authored package. Stage 3 was registered **before** the run
   (`m2p4/stage3/M2P4_STAGE3_FREEZE_V1.json`) and the scorer was validated **before** use against a
   known answer (k=7/8, hc08 at Holm 0.157, median -0.8766). The array was submitted (LUNARC
   3602080). Access was lost mid-run and later restored; the array had completed all eight tasks at
   exit 0:0, the resume precondition returned `COMPLETE` 8/8, and the run was scored.
   **Result: `C2_NOT_REPLICATED_IN_SECOND_GRAMMAR`, k = 2/8, median −0.4446** — a real negative,
   recorded in ledger 66 and [m2p4/stage3/RESULT.md](../m2p4/stage3/RESULT.md). The benefit is not
   absent (precondition holds 6/8, p ≤ 0.036); it is too small against the 50 % bar, and two worlds
   reverse. Attribution: the registered arm fixes one library and one depth and is the best
   available history arm on only 3/8 worlds — ledger 56's selection defect in a second grammar.
   A *prospective* per-world selection rule is the named revival; not done, not claimed.

## What would still falsify the picture

- A second authoring regime (next experiment 2) on which the mined library, served guided-first,
  fails to beat RESET on a material fraction of viable worlds → the C2 benefit is a property of
  one author's worlds.
- *Already fired:* a second **grammar**. M2-P4 (band 3-4, chunk count 10-16) returned
  `C2_NOT_REPLICATED_IN_SECOND_GRAMMAR` — k = 2/8 worlds clear the 50 % bar, median −0.4446
  (ledger 66). The registered 50 %-magnitude claim does **not** survive the band-2-3 tiling.
  What it is *not*: a collapse of the history benefit, which still beats RESET on 6/8 worlds;
  the attribution is the fixed library/depth of the registered arm (ledger 56).
- `d=2` aggregate flips sign on later seeds → the 5/5 was early-seed luck.
- *Already fired:* "the 18-world aggregate shows the integrated arm losing to the parent" — in
  the stronger form of #411: against the guided-first parent the controller never wins.
