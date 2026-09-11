# Continual development — learning from one's own acquisitions (registered 2026-09-11, before any run)

## The gap this closes

Every arm so far *develops* only in its dev phase; the lifetime that follows serves a fixed
library. The shift lifetime (A → B → A′, [PLASTICITY.md](PLASTICITY.md)) shows the cost of
that: the controller stands down correctly in B, but B's own solved targets teach it
nothing, so the B segment costs **5 208 vs RESET 3 933 (+32 %)** — the transition window
plus the stood-down overhead — and A′ recovers only because A's library was retained.
"History makes new verified cognition easier to acquire" has to hold *during* life, not
only before it.

## Mechanism (`CONTINUAL_OCM`, `m2p1_runner.py`)

The liveness_v3 controller unchanged, plus, **while stood down** and only after a re-probe
of every retained library has missed:

1. **Mine** from the organism's own verified acquisitions: corpus = the last 32 solved
   targets excluding the 8 most recent; candidates = the registered `learn_generator`
   (as-is) and greedy MDL, exactly the dev-phase pair.
2. **Validate** each candidate on the 8 most recent solved targets (held out from mining):
   depth by the expected-cost rule on their tilings; the candidate's cost on each is
   measured by a **charged guided-only probe** (hit → its position; miss → β plus the
   baseline the organism already paid); per-cell rule and fallback fitted on those deltas.
   Deploy iff mean delta > 0 and strictly better on more than half of the slice.
3. **Retain** every library; re-probes try each in turn (each charged), so a return to an
   earlier regime reactivates its library without re-learning.
4. Re-mining is attempted at most once per 16 new verified solutions.

What is read: the task statement, the organism's own solved history, and the outcomes of
charged actions. What is charged: every probe (all retained libraries), every validation
probe, every interleave excess. Mining itself is fit cost, charged as in the dev ledger.
The validation baseline is the acquisition the organism had to pay anyway — the
incremental attribution, unambiguous here because those solves were the targets themselves.

## Registered predictions

| world | v3 (measured) | prediction under CONTINUAL_OCM | falsifier |
|---|---|---|---|
| shift A→B→A′, B segment | 5 208 (+32 % vs RESET 3 933) | ≤ 3 740 (**≤ −5 %** vs RESET): stood down after ~8, re-mined after 16 verified B solves, live for the remainder | B ≥ RESET |
| shift lifetime | 2 192 (−38 %) | ≤ 1 900 (≤ −46 %) | ≥ 2 192 |
| shift A, A′ | 507 / 861 | unchanged within the re-probe phase (±3 %) | worse by > 3 % |
| FV8 (library valueless) | +0.004 % vs RESET | within **+0.05 %** — re-mining triggers but never validates; cost = validation probes only | > +0.05 % |
| E5 | 414.1 | unchanged (never stood down) | ≠ 414.1 |

**Claim ceiling if positive.** Developmental learning continues through life on the
registered units without touching them; the ceiling stays the registered grammar and
authored ecologies. A multi-regime lifetime (A → B → A′ → B′) is the next test.

## Outcome, continual_v1 (2026-09-11; records/continual/SHIFT_v1_*, E5_v1_*)

| world | v3 | continual_v1 | prediction | verdict |
|---|---|---|---|---|
| E5 | 414.1 | **414.1** | unchanged | held |
| shift A / A′ | 507 / 861 | **507 / 861** | unchanged | held |
| shift B | 5 208 | **5 524** (+40 % vs RESET) | ≤ 3 740 | **falsified** |
| shift lifetime | 2 192 | 2 297 | ≤ 1 900 | **falsified** |
| FV8 | 56 057.9 (+0.004 %) | **56 073.9 (+0.032 %)** — 7 re-mine attempts, none validated, 1912 slots charged in total | ≤ +0.05 % | held |

**Attribution (per-target rows, two stages, both mechanical).**
1. *Corpus straddled the shift.* The first re-mine (target 40) mined a 32-solution window
   that was three-quarters A-regime; both candidates failed validation (0/8) — correct, 248
   slots charged. The second (target 56) recovered B's motifs (`inc·double, square·square,
   square·dec, square·inc, square·double`), validated 7/8 with mean delta +3 020, and cost
   7 684 slots of validation probes — four targets before B ends. The mechanism needs
   ≈ 24 verified in-regime solutions (16 corpus + 8 held out) before it can deploy; a
   30-target segment leaves ≤ 6 targets to amortise, and my prediction also priced the
   transition window at 1.3× RESET where the rows show 2.3×.
2. *Liveness window not reset on activation.* The window still held the stood-down misses,
   so the freshly validated library was stood down on its first miss (target 57 → 58 back
   at baseline). A′ is unaffected (its reactivation probe hit and kept hitting).

**Revival, continual_v2 (registered before its run).** (a) Regime-aware corpus: mine only
from solutions acquired since the last stand-down, at least 8 in the corpus and 8 held
out. (b) A fresh liveness window on every activation. (c) The fair test is a lifetime whose
new regime is long enough to amortise learning it. The A world holds 136 members, so
60-target segments are infeasible at this recipe (`too small A=61`, recorded); with a
0.2 / 0.1 / 0.7 split it supports **45-target segments** (A → B → A′, 135 targets; dev on
27 tasks). Arms: RESET, PARENT_WITH_MDL, CONTINUED_OCM (v3), CONTINUAL_OCM (v2), one dev
phase (`ECO_SHIFT45.json`, laptop billy).

Predictions for the 45-segment lifetime: v3's B segment **+10…+40 % vs RESET** (transition
≈ 8 × 2.3×, then stood down); continual_v2's B segment **≤ −5 % vs RESET** (deployed by
≈ B + 24, live for ≈ 21 targets at guided cost), lifetime below v3 by ≥ 10 %. Falsifiers:
B ≥ RESET under v2; v2 lifetime ≥ v3 lifetime. FV8 under v1 is still running; its record
is reported when it lands.

## Outcome, continual_v2 on the 45-segment lifetime (records/continual/SHIFT45_*, ECO_SHIFT45.json)

| arm | lifetime | A | B | A′ |
|---|---|---|---|---|
| RESET | 3 476 | 3 407 | 3 776 | 3 245 |
| PARENT_WITH_MDL | 3 198 | 1 071 | 7 552 | 969 |
| CONTINUED_OCM (v3) | 2 038 | 536 | 4 703 (+24.5 %) | 875 |
| **CONTINUAL_OCM (v2)** | **1 964** | 536 | **4 115 (+9.0 %)** | **1 241** |

v3's B landed inside its registered band (+10…+40 %). continual_v2's B **falsified** (≤ −5 %
registered; +9.0 % measured) and A′ **falsified** (unchanged registered; +42 %). One re-mine
event at target 72 (B + 27): corpus 13 in-regime solutions, MDL candidate 6/8 better on the
held-out slice, mean delta +2 306, deployed, 5 231 slots charged. The library it learned is
six of B's eight motifs.

**Attribution from the rows (exact, B total excess +15 233 over RESET):**
- targets 45–51, the *old* library's stand-down latency under the 8-window hit-rate rule:
  probe + rule-routed interleave at ≈ 2.3× RESET — **+34 376**;
- stood-down targets 52–71: two re-probes — +2 926;
- the re-mine target 72: +2 173;
- **targets 73–89 after deployment: −24 242** (eleven probe hits at 211–541 slots against a
  RESET of ≈ 2 200–5 200; six misses at β + 2× baseline because the learned library's rule —
  fitted on probe deltas — routed misses to the interleave).
- A′: the B library was live at the boundary and paid the same latency again before A's
  library was re-probed on the cadence; v3 had nothing live and reactivated on its first
  re-probe.

So the learning works — the post-deployment window runs at −38 % vs RESET — and what
fails is the **liveness rule at a regime change**, twice per lifetime.

**Revival, continual_v3 (registered before its run; runner `standdown_misses` = 3).**
(i) Stand down after 3 consecutive misses instead of a hit-rate < 0.25 over 8 (which needs
7 misses). (ii) At the moment of stand-down, probe every other retained library at once
(one β each) — a return to a known regime costs one probe, not a cadence wait. (iii) Under a
continually-learned library, a probe miss pays β + baseline, never the interleave: its rule
was fitted on probe deltas and says where the probe hits, not where the interleave pays.

Predictions (SHIFT45, same dev state): A 536 ± 5 % (false stand-downs in A are ≤ 3-miss
events and recover on the next re-probe); **B ≤ 3 590 (≤ −5 % vs RESET)**; **A′ ≤ 875**
(instant reactivation, ≈ 600 expected); lifetime ≤ 1 650 (≤ −52 % vs RESET), below v3 by
≥ 15 %. Falsifiers: B ≥ RESET; A′ > 919; A > 563.

## Outcome, continual_v3 on the 45-segment lifetime (records/continual/SHIFT45_v3_*)

| arm | lifetime | A | B | A′ |
|---|---|---|---|---|
| RESET | 3 476 | 3 407 | 3 776 | 3 245 |
| CONTINUED_OCM (v3 controller) | 2 038 | 536 | 4 703 (+24.5 %) | 875 |
| continual_v2 | 1 964 | 536 | 4 115 (+9.0 %) | 1 241 |
| **continual_v3** | **1 720 (−50.5 %)** | 536 | **3 888 (+3.0 %)** | **735** |

Held: A (536), A′ (735 ≤ 875; the B library stood down after three misses and A's was
re-probed at once), lifetime ≤ 1 650 missed by 4 % but the ≥ 15 % margin over the v3
controller held (−15.6 %). **B falsified a third time** (≤ 3 590 registered), and the
sequence is +24.5 % → +9.0 % → +3.0 %. Excess by window (exact): transition 45–47 **+14 025**
(was +34 376 under the 8-window rule), re-probes +4 389, **the failed re-mine at target 64
+11 019** (an 8-program corpus; both candidates failed validation, 9 556 slots of probes
charged), the successful re-mine at 80 +5 648, **targets 81–89 −30 029** (nine hits at
400–900 slots against a RESET of 2 100–5 200; no misses now that a learned library never
interleaves). Total +5 052.

One cause: the first attempt fires as soon as 16 solutions exist in the regime, and an
8-program corpus is too thin for MDL to recover a regime (the 13- and 24-program attempts
both deployed). **continual_v4: `min_corpus` 8 → 12** (first attempt needs 20 in-regime
solutions). Registered before the run, on SHIFT45 **and on two fresh shift worlds
(A seeds 602, 603; train 28 / 49)** so the constant is tested out of sample; plus E5 / FV8
regressions of the v3 liveness rule.

Predictions: SHIFT45 B ≤ 3 400 (≤ −10 % vs RESET), A 536 ± 5 %, A′ ≤ 875, lifetime ≤ 1 600;
fresh worlds: B ≤ 0.95 × RESET, lifetime ≤ −45 % vs RESET and below the v3 controller by
≥ 10 %; E5 ≤ 414.1 × 1.05; FV8 ≤ +0.05 % vs RESET. Falsifiers: B ≥ RESET on any world;
E5 > 434.8; FV8 > +0.05 %.

## Outcome, continual_v4 on SHIFT45 (records/continual/SHIFT45_v4_*)

| arm | lifetime | A | B | A′ |
|---|---|---|---|---|
| continual_v3 | 1 720 | 536 | 3 888 (+3.0 %) | 735 |
| **continual_v4** | **1 649 (−52.6 %)** | 536 | **3 676 (−2.6 %)** | 735 |

**B is below RESET for the first time** (the falsifier "B ≥ RESET" is silent); E5 unchanged
(414.1, so the 3-miss stand-down causes no false stand-downs there). The ≤ 3 400 target
**missed**: the target-64 attempt was correctly skipped (8-program corpus < 12, nothing
charged) — but the implementation reset the new-solution counter on the skip, so the real
attempt still waited until target 80 and served nine targets. A skipped attempt mines
nothing and must not consume the counter: **continual_v4.1** (bug fix, no constant
changed; version stamped in every arm record). Registered before its run: the attempt
fires at the first re-probe cadence with ≥ 20 in-regime solutions (≈ target 72), B ≤ 3 400,
A / A′ unchanged, lifetime ≤ 1 580. The fresh worlds s602 / s603 run their continual arm
last in their chains and therefore under v4.1; their predictions stand as registered.

## Outcome, continual_v4.1 on SHIFT45 (records/continual/SHIFT45_v4.1_*)

| arm | lifetime | A | B | A′ |
|---|---|---|---|---|
| RESET | 3 476 | 3 407 | 3 776 | 3 245 |
| CONTINUED_OCM (fixed library, v3 controller) | 2 038 | 536 | 4 703 (+24.5 %) | 875 |
| **continual_v4.1** | **1 506 (−56.7 %)** | 536 | **3 471 (−8.1 %)** | **510** |

The attempt fired at target 72 as registered (16-program corpus, deployed, 5 321 charged)
and served 17 targets. B ≤ 3 400 **missed by 2 points** (−8.1 % vs the registered −10 %);
B < RESET, A unchanged and lifetime ≤ 1 580 held; A′ came out *better* than registered
(510 vs "unchanged 735"): the B library stood down after three misses at the boundary, A's
library was re-probed at once, and A′ now costs less than A itself (no cold-start cadence).
Against the fixed-library controller the continual arm is −26 % over the lifetime.

```text
B segment, five registered rounds:  +24.5 %  →  +9.0 %  →  +3.0 %  →  −2.6 %  →  −8.1 %
(fixed library) (v1 corpus)  (v2 regime corpus + window)  (v3 3-miss stand-down, no interleave)  (v4.1 corpus ≥ 12, counter fix)
```

What remains of B's cost is mechanical and priced: the old library's three-miss transition
(≈ 14 k), the validation probes (5.3 k) and the 27 targets before enough in-regime solutions
exist to learn from. The out-of-sample test is the two fresh shift worlds (A seeds 602 /
603), registered above; their outcome decides whether any of this is tuned to SHIFT45.

## Out of sample — fresh shift worlds s602 / s603, FV8 (records/continual/SHIFT45_s60{2,3}_*, FV8_v4_*)

| world | arm | lifetime | A | B | A′ | events |
|---|---|---|---|---|---|---|
| s602 (train 28) | RESET | 3 538 | 3 428 | 3 698 | 3 488 | |
| | fixed-library controller | 2 156 (−39 %) | 773 | 4 633 (+25 %) | 1 061 | |
| | **continual (v4)** | **1 741 (−50.8 %)** | 773 | **3 514 (−5.0 %)** | 935 | skip 64; deploy 80 (corpus 25, 8/8, 5 691) |
| s603 (train 49) | RESET | 3 804 | 3 803 | 3 438 | 4 172 | |
| | fixed-library controller | 2 128 (−44 %) | 734 | 4 422 (+29 %) | 1 228 | |
| | **continual (v4.1)** | **1 850 (−51.4 %)** | 734 | **3 920 (+14.0 %)** | 897 | skip 64; **fail 72** (corpus 17, MDL 0/8, 240); deploy 88 (corpus 32, 8/8, 3 911) |
| FV8 | continual (v4) | 56 072 (+0.029 %) | | | | 7 attempts, none validated |
| E5 | continual (v4) | 414.1 | | | | never stood down |

Held out of sample: lifetime ≤ −45 % vs RESET on both (−50.8 / −51.4), ≥ 10 % below the
fixed-library controller on both (−19 / −13 %), A′ recovered on both, FV8 and E5 inside their
bounds. **Missed:** B ≤ 0.95 × RESET — s602 at 0.9503 (one slot over the line; recorded as a
miss) and s603 at +14 %, where the attempt at target 72 mined a 17-program corpus whose MDL
library did not tile the held-out slice (0/8, rejected for 240 slots) and the next attempt
waited for 16 more solutions. On every attempt the registered frequency library is dominated
by design: 16 fragments make the probe's β = 20 + 400 + 8 000 dearer than the baseline, so the
expected-cost rule pins it at depth 1 and it never hits; the compact MDL library (6–7
fragments, β ≤ 1 463) is the one that pays. s605's A world was too small (`too small A=53`),
so the next fresh world is s604 (train 50).

**Invariant.** In-life learning of a regime pays within a segment only when the segment is
long compared with the in-regime solutions the learner needs (≈ 25–32 programs for MDL on
these worlds); a 45-target segment is at that edge, which is why B sits within ±10 % of RESET
across worlds while the lifetime is −50 % on all of them.

**continual_v4.2 (registered before its run).** A failed validation is evidence the corpus was
too small, not a reason to wait for 16 more solutions: the next attempt comes at the next
re-probe with ≥ 8 new solutions (`min_new_after_fail` = 8). Nothing else changes. Predictions:
s603 B ≤ 0.98 × RESET (attempt at 80 on a ≈ 25-program corpus deploys, ≥ 9 targets served);
s602 unchanged within ± 2 % (its first attempt deployed); fresh s604: lifetime ≤ −45 % vs RESET
and ≥ 10 % below the fixed-library controller, B < RESET, A′ ≤ the fixed-library A′.
Falsifiers: s603 B ≥ RESET; s604 lifetime ≥ the fixed-library controller.

## Outcome, continual_v4.2 (records/continual/SHIFT45_s60{2,3}_v4.2_*, SHIFT45_s604_*)

| world | RESET | fixed-library controller | continual_v4.2 | B (v4.2) | A′ (v4.2) | events |
|---|---|---|---|---|---|---|
| s602 | 3 538 | 2 156 | 1 785 (−49.5 %) | 3 672 (−0.7 %) | 911 | deploy 72 (corpus 17, 5 944) |
| s603 | 3 804 | 2 128 | **1 667 (−56.2 %)** | **3 369 (−2.0 %)** | 897 | fail 72 (240); deploy 80 (corpus 25, 3 361) |
| **s604** (fresh, train 50) | 3 673 | 2 292 | **2 729 (−25.7 %)** | 3 858 (−6.9 %) | **3 625** | deploy 72 (corpus 17, **frequency** library, 16 164) |

Held: s603 B ≤ 0.98 × RESET (3 369 vs 3 369.2 — at the line), s603 lifetime, s604 B < RESET.
**Missed:** s602 "unchanged ± 2 %" (+4.5 % — the earlier attempt mined a thinner corpus and
learned a slightly weaker library); **s604's lifetime is 19 % *above* the fixed-library
controller** — the registered falsifier fired.

**Attribution (s604 rows 90–106).** The library learned at 72 was the *frequency* candidate
(16 fragments, validated 7/8 on the slice, β = 8 420 at depth 3; the MDL candidate had 5
fragments, 5/8). In B it served well (−6.9 %). At the B → A′ boundary it was not stood down for
17 targets: its long fragments tile an occasional A′ target (hits at 92, 95, 100, 103, 107),
each hit resetting the three-consecutive-miss streak, while every miss cost β + baseline
(10–12 k per target against a RESET of 2–4 k). At 104–106 three misses finally lined up, A's
library was re-probed and A′ ran at the fixed controller's cost from 107 on (rows identical).

**Invariant.** Liveness must be judged on *value*, not on hits: a library that hits one target
in three while its misses cost β each is a net loss and must stand down. The consecutive-miss
rule is a special case that fails exactly for expensive libraries with sporadic hits.

**continual_v5 (registered before its run).** Value-based liveness: on each live target record
the realised delta (hit → the library's expected baseline, taken from its own validation slice,
minus the position; miss → −probe cost); stand down when the sum over the last 8 targets is
negative (after ≥ 3 targets). Everything else unchanged (stand-down still re-probes the other
retained libraries at once). Predictions: s604 A′ ≤ 1 100 and lifetime ≤ 1 950 (≥ 15 % below
the fixed controller); SHIFT45 / s602 / s603 within ± 3 % of v4.1 / v4.2; E5 414.1 ± 5 %;
FV8 ≤ +0.05 %. Falsifiers: s604 lifetime ≥ 2 292; any B ≥ RESET; E5 > 434.8.

## Outcome, continual_v5 (records/continual/SHIFT45*_v5_*)

| world | RESET | fixed controller | v4.x | **v5** | B (v5) | A′ (v5) |
|---|---|---|---|---|---|---|
| SHIFT45 | 3 476 | 2 038 | 1 506 | 1 715 (+13.9 %) | 3 814 (+1.0 %) | 796 |
| s602 | 3 538 | 2 156 | 1 785 | 1 859 (+4.1 %) | 3 814 (+3.1 %) | 989 |
| s603 | 3 804 | 2 128 | 1 667 | 2 128 (+27.7 %) | 4 423 (+28.6 %) | 1 228 |
| **s604** | 3 673 | 2 292 | 2 729 | **1 813 (−50.6 %; −21 % vs fixed)** | 3 625 (−12.6 %) | **1 107** |
| E5 | 44 738 | 414.1 | 414.1 | 414.1 | | |

s604 recovered as registered (A′ ≤ 1 100 missed by 7 slots; the lifetime falsifier silent).
**The other three regressed** (± 3 % registered; +4 / +14 / +28 % measured; two B segments back
above RESET) — s603's B is byte-for-byte the fixed controller's, i.e. the learned library
never served. Attribution: the value window is not regime-aware — at a regime change it still
carries the previous regime's positive hit deltas, so the old library stands down later than
under the three-miss rule; the regime therefore starts later, the corpus at target 72 is a
different (thinner) set, and the library it yields is weaker or is itself stood down by the
same rule before it can earn a positive window.

**Invariant.** The two stand-down signals detect different failures and neither subsumes the
other: consecutive misses are fast at a regime change; realised value catches an expensive
library whose sporadic hits do not pay for its misses.

**continual_v5.1 (registered before its run): stand down on EITHER signal.** Nothing else
changes. Predictions: SHIFT45 / s602 / s603 within ± 3 % of v4.1 / v4.2 (1 506 / 1 785 /
1 667); s604 within ± 3 % of v5 (1 813), A′ ≤ 1 150; E5 414.1 ± 5 %. Falsifiers: any lifetime
above its bound; any B ≥ RESET on SHIFT45 / s603 / s604.

**continual_v5 on FV8: 57 167 = +1.98 % vs RESET (v4: +0.03 %) — a regression, recorded
(records/continual/FV8_v5_*).** The event log rules out liveness: no learned library was ever
deployed (13 attempts, 0 deployed). Two attempts (targets 40 and 72) charged **64 492 and
65 801 slots** of *validation probes*: a 16-fragment frequency candidate whose expected-cost
rule chose depth 3 (some validation programs tile at ≤ 3 tokens) and whose probes then missed
on all eight tasks at the full β = 8 420. The other eleven attempts cost 264–288 each. A
program that tiles in ≤ D tokens must be reachable by a ≤ D-word probe, so either the depth
rule and the probe disagree about the library (an assay defect) or the tilings are counted on
programs the probe cannot reproduce. The fit is now instrumented (per-task tiling depth vs
probe outcome, `tiling_probe_violations` asserted in every event) and FV8 re-runs under v5.1
to catch the case; the cause will be attributed from that record, not guessed.

## Outcome, continual_v5.1 — positive on all four shift lifetimes (records/continual/SHIFT45*_v5.1_*)

| world | RESET | fixed-library controller | **continual_v5.1** | vs RESET | vs fixed | B (v5.1) | A′ (v5.1) |
|---|---|---|---|---|---|---|---|
| SHIFT45 (in-sample) | 3 476 | 2 038 | **1 506** | −56.7 % | −26 % | 3 471 (−8.1 %) | 510 |
| s602 | 3 538 | 2 156 | **1 785** | −49.5 % | −17 % | 3 672 (−0.7 %) | 911 |
| s603 | 3 804 | 2 128 | **1 667** | −56.2 % | −22 % | 3 369 (−2.0 %) | 897 |
| s604 | 3 673 | 2 292 | **1 895** | −48.4 % | −17 % | 3 858 (−6.9 %) | 1 124 |
| E5 | 44 738 | 414.1 | 414.1 | | | | |

Held: SHIFT45 / s602 / s603 byte-identical to v4.1 / v4.2 (the three-miss signal fires first
there); s604 A′ ≤ 1 150 (1 124) and its lifetime falsifier silent; E5 unchanged. Missed: s604
"within ± 3 % of v5" (+4.5 %: the union rule stood the sporadic-hit library down a few targets
later than the value rule alone). FV8 under v5.1 pending.

```text
continual_v5.1 vs RESET            −48…−57 % on four shift lifetimes (three out of sample)
continual_v5.1 vs fixed controller −17…−26 % on all four
B segment (the regime never seen in development) below RESET on all four: −0.7 … −8.1 %
A′ (return to the first regime) recovered on all four by re-probing the retained library
```

Every B segment is still within ten points of RESET: a 45-target regime is at the edge of what
the learner needs (≈ 25 in-regime solutions) before it can pay, and the transition costs of
the old library are priced. What the chain has established is the mechanism; the size of the
in-segment benefit is a property of segment length relative to the learning horizon.

**FV8 attributed (records/continual/FV8_v5.1_instrumented_*).** v5.1 reproduces v5 on FV8
(57 167.1; the liveness rule is not the cause). The instrumented fit shows, at targets 40 and
72, the frequency candidate with **1 of 8** validation programs tilable at depth 3, exactly
one probe hit, `tiling_probe_violations` 0 — no assay defect. The expected-cost depth rule
was right for *deployment* (one large saving outweighs seven β losses in expectation), but
validation probes buy information, not savings, and the deployment criterion — strictly
better on more than half of the slice — is unreachable for a candidate with ≤ 4/8 tilable
tasks. **continual_v5.2 (registered before its run):** a candidate whose tilable tasks are
≤ n/2 is rejected before any probe is charged, and a validation stops as soon as the majority
is out of reach. Derived from the criterion, no constant added. Predictions: FV8 ≤ +0.05 %
vs RESET; SHIFT45 / s602 / s603 / s604 within ± 1 % of v5.1 (their deployed candidates had
≥ 5/8 tilable; s603's rejected attempt at 72 had 0 tilable and is now skipped at zero cost).
Falsifiers: FV8 > +0.05 %; any shift lifetime > 1 % above v5.1.

## Widening set (continual_v5.1; records/continual/SHIFT45_s60{6,7,8,9}_*, E7_v5.1_*, E8_v5.1_*)

| world | RESET | fixed controller | **continual_v5.1** | vs RESET | vs fixed | B | A′ |
|---|---|---|---|---|---|---|---|
| s606 | 3 566 | 2 197 | **1 784** | −50.0 % | −19 % | 3 730 (+1.4 %) | 905 |
| s607 | 3 629 | 2 048 | **1 487** | −59.0 % | −27 % | 3 139 (−15.8 %) | 808 |
| s608 | 3 838 | 1 943 | **1 608** | −58.1 % | −17 % | 3 503 (−0.6 %) | 833 |
| s609 | 3 523 | 2 217 | **1 871** | −46.9 % | −16 % | 3 995 (+2.3 %) | 861 |
| E7 (static) | 62 935 | 507.5 | 507.5 | | | | |
| **E8 (static)** | 40 850 | 596.3 | **7 479.6** | −82 % | **+1 154 %** | | |

Eight shift lifetimes now (one in-sample, seven fresh): the continual arm is −47…−59 % vs
RESET and −16…−27 % below the fixed-library controller on every one; A′ recovers on every one;
the never-developed regime B is below RESET on 5 / 8 and within +2.3 % on the rest.

**E8 is a regression of the three-miss signal**: on a static world whose library hits almost
always, a chance streak of three misses stands the library down and every stood-down target
costs ≈ RESET (40 k) until the next re-probe — the fixed controller never stands down. The
pure value rule (v5) would not have: its window sum stays positive. v5 was slow at regime
changes only because a miss was priced as its probe cost, not the interleave excess it
triggers. **continual_v5.3 (registered before its run): the value rule alone, with every
live target priced as (expected baseline − total charged), settled after the solve.** One
rule, fast at regime changes (three interleaved misses at ≈ 2.3× RESET outweigh the previous
hits) and immune to chance streaks (one miss never outweighs a window of 40 k hits).
Predictions: E8 ≤ 700; E7 / E5 unchanged; FV8 ≤ +0.05 %; SHIFT45 / s602 / s603 / s604 within
± 5 % of v5.2. Falsifiers: E8 > 700; any shift lifetime above the fixed controller.

## Outcomes, continual_v5.2 and v5.3 (records/continual/*_v5.2_*, *_v5.3_*)

| world | v5.1 | **v5.2** (validation skip) | v5.3 (value rule alone, full cost) |
|---|---|---|---|
| SHIFT45 | 1 505.7 | **1 504.5** | 1 751.3 (A′ 1 101) |
| s602 | 1 785.4 | **1 784.2** | 1 842.1 (A′ 1 085) |
| s603 | 1 666.7 | **1 663.7** (rejected attempt now 0) | 1 865.3 (A′ 1 321) |
| s604 | 1 895.4 | **1 895.4** | 2 114.6 (A′ 1 528) |
| FV8 | 57 167 (+1.98 %) | **56 057.9 (+0.004 %; 13 attempts, 0 slots charged)** | — |
| E8 | 7 479.6 | — | **7 479.6 (identical)** |
| E7 / E5 | 507.5 / 414.1 | — | 507.5 / 414.1 |

v5.2 **held every prediction** (± 1 % on the four shift worlds; FV8 ≤ +0.05 %): the
criterion-derived skip removes the validation cost entirely on a library-valueless world. v5.3
**falsified its E8 prediction** — E8 is byte-identical under the value rule alone, so the
three-miss signal was *not* its cause and my attribution was wrong — and it is worse than
v5.1 on all four shift worlds (A′ 1 085–1 528 vs 510–1 124: the value window is slower at
the B → A′ boundary even with the full cost). v5.2 is therefore the current controller;
v5.3 is retired as a recorded miss.

**E8, read from the record.** Both arms serve the same 8-fragment MDL dev library. The
continual arm misses on every one of the first 24 targets (≈ RESET + probe) while the fixed
arm's record hits at 941, 1 063, 1 062 …; from target 25 the learned library hits at 130–650
and *beats* the fixed record. A direct test of both probe code paths on E8's first target
misses in both (1 884 slots, no hit) with the current runner — so the fixed arm's 596.3 was
produced by an older runner and may not be reproducible. The fixed CONTINUED_OCM arm is
re-running on E8 from the same dev state with the current runner; the E8 verdict waits for it.

**E8 corrected — a launch error, not a controller regression.** The morning's E8 arms
(records 596.3 / 40 850) ran on `M2P1_ECOLOGY_E8_m7.json` (63 targets, 7 motifs); my
regression launches picked `M2P1_ECOLOGY_E8_m6.json` (55 targets, 6 motifs — a different
world), whose protected targets match **0 / 55** of the old record. The continual arm was
therefore deployed with a library developed on one world onto another: it missed on the first
24 targets, learned the new world's library from its own solutions at target 24 (38 749 slots
of validation) and served the rest at 130–650 — an *accidental cross-world transfer* test,
kept as an exploratory record (`records/continual/E8_v5.3_*` is that run). The matched
comparison (continual_v5.2 on E8_m7 from the same dev state) is running; the fixed controller
on the mismatched world is also running so the accidental transfer can be read fairly.
Ledger row 24 is corrected accordingly; v5.3 remains retired on the shift-world evidence.
The runner is restored to continual_v5.2 with controller_v4's dev-phase rule.

**E8 settled (records/continual/E8m7_v5.2_*, E8m6_from_m7_*).** Matched world (E8_m7, same
dev state): continual_v5.2 **596.3 — byte-identical to the fixed controller**; no regression.
The accidental mismatch is itself a result: a library developed on E8_m7 and deployed on
E8_m6 (different motifs) leaves the fixed controller at **29 680** (stood down, ≈ RESET − the
occasional hit), while the continual arm learned E8_m6's library from its own first 24
solutions and finished at **7 480** — 4× cheaper than the fixed controller and −82 % vs RESET
on a world it never developed on. Unplanned, therefore exploratory; registered below as a
prospective test.

## Cross-world transfer (registered 2026-09-11 before the runs; billy-old)

Deploy a lifetime developed on world X onto world Y with different hidden motifs, same grammar
and regime: (E7 → E8_m7), (E8_m7 → E7), (E5 → E7), (E7 → E5). Arms on Y: RESET, the fixed
controller with X's dev state, continual_v5.2 with X's dev state. Predictions on every pair:
the fixed controller within ± 30 % of RESET (it stands down and pays the re-probe cadence);
continual ≤ 0.5 × the fixed controller and ≤ −50 % vs RESET (it learns Y in life). Falsifiers:
continual ≥ the fixed controller on any pair; continual ≥ RESET on any pair. Claim if positive:
the developmental *procedure* (probe with history-learned depth, charged validation on one's
own acquisitions, retained libraries) transfers across worlds even when the library does not —
a first K2-flavoured observation, still inside one grammar.

## Cross-world transfer — outcome (records/crossworld/)

| develop on → deploy on | targets | RESET | fixed controller (X's library) | **continual_v5.2 (X's library)** | cont / fixed | events |
|---|---|---|---|---|---|---|
| E7 → E8_m7 | 63 | 40 850 | 41 036 (1.005×) | **35 980** | **0.877** | learned at 24 (freq, 5/8 tilable, 36 070); served 25–35; stood down at 38; no second attempt |
| E8_m7 → E7 | 43 | 62 935 | 63 198 (1.004×) | **37 264** | **0.590** | learned at 24 (35 965); served 25–42 at ≈ 600 |
| E5 → E7 | 43 | 62 935 | 63 090 (1.002×) | **37 192** | **0.590** | learned at 24 (35 965); served 25–42 |
| E7 → E5 | 21 | 44 738 | 44 947 (1.005×) | 44 947 | 1.000 | attempt at 16 skipped (too few); lifetime ended |

Held: the fixed controller within ± 30 % of RESET on every pair (it stands down and pays the
cadence: +0.2…+0.5 %). **Missed:** continual ≤ 0.5 × fixed (0.88 / 0.59 / 0.59 / 1.00) and
≤ −50 % vs RESET; the "continual ≥ fixed" falsifier fires by equality on E7 → E5.

**What the rows say.** On the 43-target pairs the arm learns the foreign world at target 24
and serves the rest at the matched controller's cost; the mean is then ≈ (24 × RESET + 36 k)
/ 43 ≈ 0.57 × RESET — the *learning horizon* (≈ 24 in-regime solutions) plus the validation
charge bound the benefit, as they do inside a shift segment. Predicted from that model: 0.57
(measured 0.59). On the 21-target pair the horizon exceeds the lifetime: no headroom, equality
— the honest terminal at that length. On E7 → E8_m7 the library learned from 16 easy early
solutions (5/8 tilable) covered the easy half, missed on the harder targets from 36 on, was
stood down at 38, and **no second attempt came**: the stand-down reset the regime corpus, so
20 fresh solutions were required again and the lifetime ended first.

**Invariant.** Standing down a library *learned in the current regime* is not evidence of a
regime change; only a developmental or foreign-regime library's stand-down is. **continual_v5.4
(registered before its run):** a learned library's stand-down keeps the regime corpus and
retries after 8 new solutions; libraries carry the regime they were learned in. Predictions:
E7 → E8_m7 second attempt near target 48 on a ≈ 40-solution corpus, cont / fixed ≤ 0.70;
E8_m7 → E7 and E5 → E7 unchanged (± 2 %); SHIFT45 / s602 / s603 / s604 unchanged (± 2 %:
their learned libraries stand down only at the A′ boundary, where A's library hits and no
re-mining occurs). Falsifiers: E7 → E8_m7 ≥ 0.85 × fixed; any shift lifetime > 2 % above v5.2.

**Claim as it stands.** The developmental *procedure* transfers to a foreign world when the
library does not: on every pair long enough to contain the learning horizon, the continual arm
learns the new world in life and lands well below the fixed controller and RESET; the size of
the benefit is bounded by (lifetime − horizon) / lifetime. Still one grammar.

## Twelve shift lifetimes (continual_v5.2 + controller_v4 dev on s610–s613; records/continual/SHIFT45_s61*_*)

| world | RESET | fixed controller | **continual** | vs RESET | vs fixed | B | A′ (fixed → continual) |
|---|---|---|---|---|---|---|---|
| s610 | 3 713 | 1 832 | **1 640** | −55.8 % | −10 % | 3 114 (−13.7 %) | 978 → 1 289 |
| s611 | 3 502 | 2 033 | **1 537** | −56.1 % | −24 % | 3 330 (−15.9 %) | 943 → 586 |
| s612 | 3 746 | 1 962 | **1 508** | −59.7 % | −23 % | 2 831 (−17.4 %) | 1 262 → 998 |
| s613 | 3 601 | 1 727 | **1 695** | −52.9 % | −1.9 % | 3 595 (+8.9 %) | 930 → 930 |

```text
12 shift lifetimes (1 in-sample, 11 fresh):  continual below the fixed controller on 12 / 12  (−1.9 … −27 %)
                                             continual below RESET on 12 / 12                 (−47 … −60 %)
                                             B (never developed) below RESET on 8 / 12; A′ recovered on 12 / 12
```

s613 is the first world where in-life learning never validated: three attempts (targets 72,
80, 88; corpora 17, 25, 32 in-regime programs) and both candidates had **0 / 8 validation
programs tilable at the chosen depth** every time, so every attempt was rejected at zero cost
(v5.2) and B ran at the fixed controller's cost. From 32 canonical B programs the compact
candidate should hold most of B's eight motifs, so a 0 / 8 tiling is unexplained by counts
alone; the event record did not keep the candidate libraries. It now does (libraries, the
per-task tiling depths and the validation programs), and s613 re-runs to attribute this from
the record rather than by conjecture. s610's A′ (1 289 vs 978) is the expensive-learned-
library transition already priced on s604.

**s613 attributed from the record (records/continual/SHIFT45_s613_recorded_*).** At target
72 the MDL candidate was `doublesquare, decdec, incsquare, decdouble, incinc, decsquare` —
five of B's eight motifs — and it tiles **4 / 8** of the validation programs (the event's
"0 / 8" was a reporting slip in the skip branch, now fixed; the count that drove the decision
was 4). The skip rule was right: a candidate that can at best tie the majority is refused at
zero cost. What stayed missing over 17 → 25 → 32 programs is structural to the two
candidates: the frequency library (all 8 motifs + 8 recurring pairs) is complete but its
16 tokens make depth 3 dearer than the baseline, so the expected-cost rule pins it at depth
1–2 where nothing tiles; greedy MDL spends its 6–8 slots on recurring motif *pairs* and never
completes the motif set. **continual_v5.5 (registered before its run): a third candidate,
the count ranking truncated to the MDL library's size ("compact frequency") — complete and
cheap, no new mining, validated by the same probes.** Predictions: s613 validates a B library
by target 80 and B ≤ 0.95 × RESET; SHIFT45 / s602 / s603 / s604 / s610 within ± 2 % or
better (the selection can only add a candidate the same probes must prefer). Falsifiers:
s613 B ≥ RESET; any regression > 2 %.

hc06 under controller_v3: 2 546 (unchanged; MDL chosen at probe cost 4 591 vs 28 581) — held.

**continual_v5.4 outcome (records/crossworld/*_v5.4_*).** E7 → E8_m7: **16 229 vs the fixed
controller's 41 036 — 0.395×** (registered ≤ 0.70 held): the first learned library stood down
at 38, the corpus was kept, a second attempt at target 40 deployed (38 402 charged) and served
the rest. E8_m7 → E7 and E5 → E7 unchanged (0.590), and all four shift lifetimes byte-identical
to v5.2 — as registered. Cross-world transfer now: **0.40 / 0.59 / 0.59 × the fixed controller
on the three pairs long enough to learn**, equality on the 21-target pair.

**s613 under v5.5 (records/continual/SHIFT45_s613_v5.5_*).** The compact-frequency candidate
did what it was built for — validated 6 / 8 at target 80 (six of B's eight motifs, mean delta
+1 499, 4 917 charged) and deployed — and then the next three targets all needed the two
motifs it lacked (`decinc`, `squaredouble`): three misses at β + baseline, stand-down, a
re-probe at 88 that missed, and the segment ended. B 3 835 (+16 % vs RESET) against 3 595
under v5.2 — the registered ≤ 0.95 × RESET **missed**; lifetime 1 775 vs 1 695. SHIFT45
unchanged (MDL still preferred). The candidate is kept only if the remaining regressions hold
(it can only add an option the same probes must prefer); s613 stays a recorded negative at
this segment length — its learning horizon (≈ 32 in-regime programs for a complete compact
library) is longer than the 45-target segment allows, the invariant already stated.

**continual_v5.5 regressions (records/continual/*_v5.5_*): held.** SHIFT45 1 504.5, s602
1 784.2, s604 1 895.4, s610 1 640.4 — byte-identical; **s603 improved 1 663.7 → 1 614.5**
(the compact-frequency candidate won the validation at target 72 and deployed eight targets
earlier). v5.5 is kept. s613 remains a recorded negative at 45-target segments (learning horizon).

## Developmental capital — recombining retained capital (C3 test; registered 2026-09-11 before any run)

**Question (#373 §6, K2).** Does history make the *acquisition of new search capital* cheaper,
not just the search? Every continual result so far learns a new regime from scratch: ≈ 20
in-regime solutions, then mining, then validation. A developmental organism should acquire a
regime built from parts it has already met in other company faster than one it has never met.

**World (A → B → C).** A from a seed; B = the complement of A's motifs (disjoint); **C = four
of A's motifs + four of B's**, with every normal form that is a member of A or B removed from
C's stream, so each C target mixes the two earlier regimes. 45 targets per segment, 135 per
lifetime, development on A only (`m2_abc_ecology.py`). A seeds 601, 602, 603.

**Mechanism (continual_v6).** One extra candidate at each re-mining attempt: the fragments of
every library the organism has retained (developmental and learned), ranked by how many of the
current regime's solved programs contain them, truncated to eight — a *recombination* of
retained capital, validated by the same charged probes as the other candidates. Because it
only has to be *selected*, not discovered, it may be attempted with 4 corpus programs
(+ 8 held out) instead of 12. **Ablation:** `CONTINUAL_OCM_NOREC` — identical, without the
recombination candidate. Controls: RESET, the same-library parent, the fixed controller.

**Predictions (per seed).** (1) In C, the recombination arm deploys a library covering ≥ 6 of
C's 8 motifs having consumed ≤ 14 in-regime solutions; the ablation needs ≥ 20. (2) C-segment
mean: recombination ≤ 0.85 × ablation on ≥ 2 / 3 seeds. (3) Lifetime: recombination ≤ ablation
on 3 / 3. (4) Regressions: SHIFT45 / s602 / s603 / s604 and E5 / FV8 and the three cross-world
pairs within ± 2 % of v5.5 / v5.4. **Falsifiers:** recombination ≥ ablation on the C segment on
2 / 3 seeds (history does not speed acquisition), or any regression > 2 %.

**Claim ceiling if positive.** A first measured K2 effect in this lane: retained capital from
earlier regimes cuts the in-life cost of acquiring a new regime's library, isolated by an
ablation. The parent is library persistence in DreamCoder-style learners; the residual tested
here is that the organism *decides by charged validation on its own acquisitions* which
retained fragments to recombine and when. One grammar; not yet K3.

## C3 test, continual_v6 — outcome: NEGATIVE (records/abc/ABC_s60{1,2,3}_v6_*)

| seed | segment | RESET | same-library parent | fixed controller | continual, no recombination | **continual + recombination** |
|---|---|---|---|---|---|---|
| 601 | C | 4 080 | 7 415 | 4 243 | 3 459 | **3 459** |
|  | lifetime | 3 755 | 5 346 | 2 982 | 2 416 | **2 416** |
| 602 | C | 3 554 | 6 441 | 3 763 | 3 494 | **3 494** |
|  | lifetime | 3 560 | 4 888 | 2 912 | 2 575 | **2 575** |
| 603 | C | 3 619 | 6 670 | 3 800 | 4 654 | **4 840** |
|  | lifetime | 3 620 | 5 004 | 2 825 | 2 815 | **2 877** |

**Falsified on all three seeds.** Recombination equals the ablation on s601 / s602 and is worse
on s603 (C +4 %, and its lifetime is 1.8 % *above* the fixed controller). Prediction (1) — a C
library covering ≥ 6 / 8 motifs from ≤ 14 in-regime solutions — did not happen on any seed.
Regressions held on SHIFT45 / s602 / s603 / s604, E5, FV6 and the three cross-world pairs
(byte-identical); **FV8 regressed** (+4.96 % vs RESET; attributed below).

**Attribution (records, not conjecture).** Both learned B libraries carry `regime 47`: the
B → C change was never registered as a new regime, because v5.4 treats the stand-down of a
library learned in the current regime as *not* a regime change and keeps the corpus. At C the
kept corpus was ≈ three-quarters B, so the recombination candidate was ranked on B programs:
on s601 it held B's motifs and one of C's four A-motifs and tiled 4 / 8 validation tasks
(refused, correctly); at 104 and 112 the same; the deployment finally came from full mining at
112. On s603 the recombined candidate tied MDL at 104 (5 / 8) and its validation probes were
charged (16 530 vs 8 173) — the 4 % loss. The v5.4 invariant is right on E7 → E8_m7 (the
same regime, an incomplete library) and wrong on A → B → C (a new regime): **the organism
cannot tell the two apart at stand-down time**, so deciding there is the defect.

**FV8 attribution (records/continual/FV8_v6_*).** Not the recombination candidate (refused at
zero cost). At target 88 v5.5's compact-frequency candidate — first exercised on FV8 in this
run — validated 7 / 8 at depth 4 (β 54 240 ≈ the expected baseline 53 338; mean delta
+19 500), was deployed, and then hit ≈ 54 % of targets: seven hits saved 201 k, six misses cost
β each (325 k), and the validation itself charged 244 827. An eight-task validation slice
overestimated the hit rate of a library whose single miss costs a whole baseline.

## continual_v6.1 (registered 2026-09-11 before any run)

Three mechanism changes, each derived from a recorded failure and none a tuned constant:

1. **Two windows, validation chooses** (C3 attribution). Candidates are built both on the regime
   window and on the window since the last stand-down of *any* library; the charged
   validation on the organism's most recent acquisitions decides which corpus was right.
2. **Deploy on a positive lower confidence bound** of the validation delta (FV8 attribution) —
   the lane's own EU-admission rule (mean − 1.96 · s.e. > 0) applied to in-life validation.
3. **Non-tilable validation tasks are not probed** (the probe cannot reach them at the chosen
   depth; their outcome is recorded as a miss at −β and nothing is charged).

**Predictions.** C3 (unchanged thresholds from the v6 registration): on ≥ 2 / 3 seeds the
recombination arm's C segment ≤ 0.85 × the ablation's, and it deploys a C library from ≤ 14
post-stand-down solutions; lifetime ≤ ablation on 3 / 3. FV8: the depth-4 deployment is
blocked by the confidence bound (`blocked_by_ci` recorded) and FV8 ends ≤ +3.0 % vs RESET — the
earlier +0.05 % bound was set when validation was cheap and is kept as a **recorded miss**, not
re-tuned. Regressions: SHIFT45 / s602 / s603 / s604 / E5 / FV6 / three cross-world pairs within
± 2 %. Falsifiers: recombination C ≥ ablation C on 2 / 3 seeds; any regression > 2 %.

## C3 test, continual_v6.1 — outcome (records/abc/*_v6.1_*, records/continual/*_v6.1_*)

| seed | segment | RESET | fixed controller | v6 ablation | **v6.1 ablation** | **v6.1 + recombination** |
|---|---|---|---|---|---|---|
| 601 | C | 4 080 | 4 243 | 3 459 | **2 700** | 2 751 |
|  | lifetime | 3 755 | 2 982 | 2 416 | **2 147** | 2 164 |
| 602 | C | 3 554 | 3 763 | 3 494 | **2 842** | 2 842 |
|  | lifetime | 3 560 | 2 912 | 2 575 | **2 334** | 2 334 |
| 603 | C | 3 619 | 3 800 | 4 654 | **4 424** | 4 424 |
|  | lifetime | 3 620 | 2 825 | 2 815 | **2 818** | 2 818 |

**C3 falsified a second time** (recombination C ≥ ablation C on 3 / 3). What v6.1 did do is
make *both* continual arms acquire the new regime much sooner: the regime C segment fell
22 % / 19 % / 5 % from v6, and on s601 / s602 it is now 36 % / 24 % below the fixed controller
— the "two windows, validation chooses" change deployed `mdl_recent` from the post-stand-down
corpus at target 112. That is better in-life acquisition by a designed procedure, not K2.

**Why recombination still adds nothing (s601, records).** At 104 the recombination candidate
built on the 6 post-stand-down programs held 5 of C's 8 motifs and tiled 3 / 8 validation
tasks — refused. By 112 the mined `mdl_recent` tiled 8 / 8 (lower bound +3 374) and beat the
recombined candidate (7 / 8, +1 822). Recombination inherited learn_generator's
support ≥ 2 rule, which drops three of C's motifs from a six-program corpus; that rule guards
*new* fragments against one-off substrings, whereas retained fragments already carry support
from earlier regimes.

**Regressions (± 2 % registered).** SHIFT45 1 488.0 (−1.1 %), s602 1 759.5 (−1.4 %), s604
1 877.2 (−1.0 %), E5 and FV6 byte-identical — held. **s603 1 701.8 (+5.4 %) — falsifier
fired**: the confidence bound blocked a compact library at target 72 (5 / 8, mean +1 165,
lower bound −228) that would have paid, and deployment waited until 80. The bound's
justification is FV8 (still running); it is kept or retired on that record.

## continual_v6.2 (registered before its run)

One change: a retained fragment enters the recombination candidate on **one** sighting in the
current corpus (`recomb_support` = 1). Predictions (thresholds unchanged from the v6
registration): recombination C ≤ 0.85 × ablation C on ≥ 2 / 3 seeds, with a C library deployed
at the 104 attempt; shift / E5 / FV6 within ± 2 % of v6.1. Falsifier: recombination C ≥ ablation
C on 2 / 3 seeds. If it fires, this chain terminates at **NO_TRANSFERABLE_HEADROOM** for
recombination at this grammar and cadence: the 8-solution validation slice needs the new
regime's own solutions, and once it has them, mining the same corpus already recovers the
regime — retained capital has no window in which it is both admissible and better.

## C3 test, continual_v6.2 — outcome: registered claim NOT MET (records/abc/*_v6.2_*)

| seed | recombination C | ablation C (v6.1) | ratio | recombination lifetime | ablation lifetime |
|---|---|---|---|---|---|
| 601 | **1 918** | 2 700 | **0.710** | 1 886 | 2 147 |
| 602 | 2 842 | 2 842 | 1.000 | 2 334 | 2 334 |
| 603 | 4 424 | 4 424 | 1.000 | 2 818 | 2 818 |

The registered claim (≤ 0.85 × on ≥ 2 / 3 seeds) is **not met** (1 / 3) and the falsifier fires.
The registration said the chain would then terminate at NO_TRANSFERABLE_HEADROOM *because
retained capital has no window in which it is both admissible and better* — **s601 contradicts
that premise**: there the recombination candidate built from six post-stand-down programs
tiled 8 / 8 (lower bound +3 052), deployed at target 104, and cut regime C's cost 29 % while the
ablation waited until 112. So the terminal is recorded as *registered claim not met*, not as a
proven absence of headroom.

**What separates the seeds (records).** Not coverage: the retained libraries cover 7 / 8, 7 / 8
and 8 / 8 of C's motifs. The number of post-stand-down C programs available at the 104 attempt
was **6 / 4 / 3** — set by where the stand-down happened to fall relative to the 8-target
re-mining cadence. With 4 programs, support-1 admitted boundary artefacts that crowded out true
motifs (0 / 8 tiled); with 3, no candidate could be formed. The cadence exists to limit *charged*
re-probes of stood-down libraries; re-mining costs nothing unless a candidate validates.

## Assay defect found and closed: survivorship in one record

v6.1's FV8 figure (56 072, "+0.03 %") is **withdrawn**. The confidence-bound-blocked attempt at
target 88 charged 190 587 slots against that target's 200 000 search budget, the solve then ran
out of budget, and `mean_B_slots` — which averages verified rows — silently dropped the target
(119 / 120 verified). Counted, FV8 under v6.1 is ≈ +4 %, no better than v6. A scan of **all 814
arm records** on the three hosts (173 billy-old, 277 laptop, 364 LUNARC; per-target criterion,
any rung, with a must-flag control) finds this to be the **only** failed target in the lane —
every other reported mean is over the full target set. (A first LUNARC scan flagged 153 files: a
false-positive class — the frozen multi-rung ladder records one row per target per rung, so
unsolved low rungs are normal; the checker was corrected and re-run before anything was reported.)

Fix in the runner (v6.3): learning charges are added to a target's cost but are **never deducted
from its search budget**, and every arm report now carries `all_targets_verified`.

**The in-life confidence bound is retired.** Its only claimed benefit was the survivorship figure
above; it cost s603 +5.4 % and E7 → E8_m7 +43 % (23 159 vs 16 229 — it blocked the second
deployment). It stays in the code behind `deploy_ci = False`, on the record.

## C3b — new registration (2026-09-11, before any run; fresh seeds only)

Because the fix below was suggested by seeds 601–603, those seeds are **regressions, not
confirmation**. The test is on fresh A → B → C lifetimes, A seeds 604–612 (604–606 on laptop
billy, 607–612 on LUNARC), five arms each.

**Mechanism (continual_v6.3).** Re-probing retained libraries stays on the 8-target cadence
(charged); **re-mining may be attempted on any stood-down target** (free unless a candidate
validates). Plus the two corrections above (budget-independent learning charges; bound retired).

**Predictions.** On ≥ 2 / 3 of the fresh seeds that pass the ecology gate, the recombination arm's
regime-C cost ≤ 0.85 × the ablation's; its lifetime ≤ the ablation's on every fresh seed; every
arm verifies every target. Regressions: s601–603, the four shift lifetimes, E5 and FV6 within
± 2 % of v6.2, except that retiring the bound should return s603 to ≤ 1 701.8 and E7 → E8_m7 to
≤ 16 229 × 1.02; FV8 verifies all 120 targets and its cost is recorded as the priced boundary it
is (validating a depth-4 library there costs ≈ three baselines). **Falsifier:** fewer than 2 / 3
of fresh seeds meet the 0.85 bar — then C3 is recorded **NOT_ESTABLISHED at this grammar** and
this chain stops.

## continual_v6.3 — outcomes (every arm verifies every target; records/abc/*_v6.3_*, records/crossworld/*_v6.3_*)

**C3b, fresh laptop seeds (LUNARC seeds 607–612 still running; the C3b terminal is recorded when
they finish):**

| seed | RESET C | fixed controller C | ablation C | recombination C | ratio | lifetimes (RESET / fixed / ablation / recombination) |
|---|---|---|---|---|---|---|
| 604 | 3 808 | 4 017 | 6 039 | 6 222 | 1.030 | 3 781 / 3 124 / 3 478 / 3 539 |
| 605 | 2 897 | 3 077 | 3 536 | 3 991 | 1.129 | 3 334 / 2 811 / 2 762 / 2 913 |
| 606 | 3 204 | 3 276 | 2 768 | 2 847 | 1.029 | 3 485 / 2 724 / 2 077 / 2 104 |

Recombination is worse than the ablation on all three fresh laptop seeds. The registered bar
(≤ 0.85 × on ≥ 2 / 3 of the nine fresh seeds) can now be met only if all six LUNARC seeds pass.

**Regressions.** Shift lifetimes SHIFT45 1 497.3 (+0.6 %), s602 1 758.1 (−0.1 %), s604 1 890.8
(+0.7 %) — held; **s603 1 576.8**, the best of any version. Cross-world pairs all improved:
E7 → E8_m7 **14 443** (0.35 × the fixed controller), E8_m7 → E7 **30 028** and E5 → E7 **29 974**
(0.47 ×) — re-mining on any stood-down target learns the foreign world sooner. E5 and FV6
identical. ABC seeds 601–603: ablation lifetimes 2 151 / 2 302 / 2 308 (s603 −18 % vs v6.2).
**FV8: 63 722 (+13.7 % vs RESET), all 120 targets verified** — the honest figure.

**s604 attributed (records/abc/ABC_s604_v6.3_*).** Both continual arms cost ≈ 6 000 in regime C
against RESET's 3 808. Three things, all visible in the rows: (i) every eight targets a charged
re-probe of both retained libraries costs exactly +10 304 (β 1 884 + β 8 420); (ii) C is made of A's
and B's motifs, so each old library hits a C target now and then, is reactivated, and pays β-priced
misses before standing down again (108–113); (iii) every stand-down of the *developmental*
library reset the regime corpus, so regime C never accumulated the 20 solutions needed to learn —
the first attempt was "too few solutions in this regime" at target 129. The reset is a v2
mechanism that v6.1's two windows made redundant. The ablation fails identically, so this is an
acquisition defect in both arms, exposed by exactly the mixed regime where retained capital
should matter most.

**FV8 attributed (records/continual/FV8_v6.3_*).** Validation charged 235 506; the rest of the
920 k excess over the fixed controller is two *validated* deployments that lost — an MDL library
at target 76 (depth 4, β 69 904, 6 / 8 tiled, validated +16 807) and a compact library at 91 (depth 4,
β 54 240, 5 / 8, +11 970). The organism made the same mistake twice with first-hand evidence
after the first.

## continual_v6.4 and C3c (registered 2026-09-11, before any run)

Mechanism (three parts, each from a recorded failure, no new constant):
(a) the regime window is never reset — the two windows and validation decide (s604);
(b) a liveness event log (stand-down / reactivate / deploy / failed deployment) in every record;
(c) **evidence must exceed the evidence that already failed**: when a learned library stands down
having realised negative value while live, later candidates must tile *more* validation tasks than
it did (FV8) — the organism's own failed learning attempts raise its bar.

Predictions. *Diagnostic (the seeds that exposed the defects; not confirmation):* s604 — both
continual arms' regime-C cost ≤ RESET's (3 808); FV8 — the second validated deployment is blocked
(`failed_deployment` in the log), FV8 ≤ +8 % vs RESET, all targets verified. *Regressions (± 2 % of
v6.3):* the four shift lifetimes, E5, FV6, the three cross-world pairs, ABC 601–603 / 605 / 606.
*C3c (fresh A seeds 613–615 on laptop billy, 616–621 on LUNARC):* recombination's regime-C cost
≤ 0.85 × the ablation's on ≥ 2 / 3 of the fresh seeds that pass the ecology gate, and **both continual
arms' regime-C cost ≤ RESET's on every fresh seed**; every arm verifies every target.
**Terminal rule, stated now:** if C3c fails its bar, C3 (retained capital cutting the in-life cost
of acquiring a new regime) is recorded **NOT_ESTABLISHED at this grammar** and this chain stops —
no further C3 revisions on this grammar.

## C3b terminal (all nine fresh seeds; every arm verifies every target): **C3 NOT_ESTABLISHED at this grammar**

| seed | RESET C | fixed C | ablation C | recombination C | ratio | lifetime RESET / fixed / ablation / recombination |
|---|---|---|---|---|---|---|
| 604 | 3,808 | 4,017 | 6,039 | 6,222 | 1.030 | 3,781 / 3,124 / 3,478 / 3,539 |
| 605 | 2,897 | 3,077 | 3,536 | 3,991 | 1.128 | 3,334 / 2,810 / 2,762 / 2,913 |
| 606 | 3,204 | 3,276 | 2,768 | 2,847 | 1.029 | 3,485 / 2,724 / 2,077 / 2,104 |
| 607 | 3,993 | 4,155 | 5,206 | 5,276 | 1.013 | 3,805 / 2,928 / 2,980 / 3,004 |
| 608 | 2,983 | 3,145 | 2,907 | 2,796 | 0.962 | 3,522 / 2,498 / 2,138 / 2,101 |
| 609 | 4,106 | 4,316 | 3,275 | 2,559 | **0.781** | 3,744 / 3,161 / 2,409 / 2,170 |
| 610 | 3,419 | 3,582 | 3,574 | 1,984 | **0.555** | 3,592 / 2,700 / 2,372 / 1,842 |
| 611 | 3,109 | 3,319 | 3,662 | 3,842 | 1.049 | 3,482 / 2,824 / 2,568 / 2,551 |
| 612 | 3,262 | 3,471 | 3,874 | 4,841 | 1.250 | 3,519 / 2,698 / 2,421 / 2,743 |

Recombination meets the registered bar (≤ 0.85 × the ablation's regime-C cost) on **2 / 9** fresh
seeds (s609 0.78, s610 0.56) against a registered 2 / 3. **C3b fails, and by its own registered rule
C3 — retained capital cutting the in-life cost of acquiring a new regime's library — is recorded
NOT_ESTABLISHED at this grammar and the C3 chain stops.** The two seeds where it helped are real
records, not noise-free: on 7 / 9 seeds the recombination candidate either never validated
earlier than mining or validated libraries that served worse.

**The C3c registration's C3 component is withdrawn.** It was registered after C3b's stop rule and
before C3b's outcome; running it as a C3 test would let a later registration override an earlier
commitment — the forking-paths move #373 forbids. Nothing in C3c had been run.

**What C3b shows about K1 acquisition (the claim that remains live).** In the mixed regime C the
continual arm's regime-C cost is **above RESET on 6 / 9** fresh seeds — the s604 defect is
general, not a seed accident — while its *lifetime* beats RESET on 9 / 9 and the fixed
controller on 7 / 9. v6.4 parts (a)–(c) address those recorded failures (rows 33–34), not C3.

## v6.4 — re-labelled before any run

The v6.4 runs test only the K1-acquisition and controller claims:
*diagnostic* (s604, FV8 — as registered above), *regressions* (± 2 % of v6.3, as registered), and a
**fresh-seed K1 test** on A seeds 613–621: both continual arms' regime-C cost ≤ RESET's on every
fresh seed that passes the ecology gate, both lifetimes ≤ the fixed controller's on ≥ 8 / 9, every
arm verifies every target. The recombination-vs-ablation ratio is reported **descriptively only**
and is not C3 evidence.

## continual_v6.4 — outcome: FALSIFIED, reverted (records/abc/*_v6.4_*, records/continual/*_v6.4_*)

Every arm verifies every target. Against the registration:

| check | registered | measured | verdict |
|---|---|---|---|
| s604 diagnostic: both continual arms' regime-C cost ≤ RESET (3 808) | ≤ 3 808 | ablation 5 292, recombination 8 773 | **failed** |
| FV8 diagnostic | second deployment blocked, ≤ +8 % | blocked (log: deploy at 76, fail at 79, 5/8 candidate refused); +6.6 % | held |
| shift regressions ± 2 % of v6.3 | ± 2 % | SHIFT45, s602, s604 identical; **s603 1 800 vs 1 577 (+14 %)** | **failed** |
| ABC regressions ± 2 % of v6.3 | ± 2 % | ablation lifetimes +5 … +33 % on s601/602/603/605/606; recombination +12 % (s603), +18 % (s605) | **failed** |
| E5, FV6, cross-world pairs | ± 2 % | identical | held |
| fresh K1 test (613–615 so far): both continual arms' regime-C ≤ RESET on every fresh seed | every seed | s613 fails (5 230 / 4 391 vs 3 766); s614, s615 pass | **failed** |

The regressions track the new `failed_deployment` counter (4–5 on the worst runs). **v6.4 is
reverted**: the current controller is v6.3's behaviour plus the liveness log (v6.5), with v6.4's two
changes kept behind recorded flags (`M2_V64A` = no regime reset, `M2_V64C` = failure evidence).
LUNARC seeds 617–621 were already running v6.4 and are kept as descriptive records (records/abc/ABC_s61{7..9}_v6.4_*, ABC_s62{0,1}_v6.4_*): regime-C cost of the ablation arm above RESET on 2 / 5 (s617, s621), lifetimes below RESET on 5 / 5.

**Attribution run (diagnostic, not a claim).** One variable at a time on the four worst-regressed
worlds (s603 shift; ABC s605, s606, s613 ablation arm): v6.5 base, base + (a) only, base + (c) only.
The base run must reproduce v6.3 exactly — the check that the log changes nothing.

## v6.4 attribution — outcome (records/attribution/)

| world | v6.5 base (= v6.3) | + (a) never reset the regime window | + (c) failure evidence |
|---|---|---|---|
| s603 shift | 1 576.8 | **1 800.4** (2 failed deployments) | 1 576.8 |
| ABC s606 (ablation arm) | 2 077.4 | **2 760.8** (5) | 2 077.4 |
| ABC s605 (ablation arm) | 2 761.5 | **2 930.4** (2) | 2 761.5 |
| ABC s613 (ablation arm) | 2 612.5 | **3 066.5** (4) | 2 612.5 |

The base reproduces v6.3 byte-for-byte on every world with a v6.3 record (the log changes nothing).
**(a) is the whole regression; (c) is neutral here** and is what took FV8 from +13.7 % to +6.6 %.
**Current controller: v6.6 = v6.3 + (c)** (failure evidence on by default).

**Why (a) failed, from the attribution.** The regime reset is right at a genuine change (A → B: the
incumbent stands down and the new regime must not be mined on the old one's corpus) and wrong only
when an old library that was re-probed back to life stands down again inside the window (s604's
oscillation on a mixed regime). (a) removed both.

## v6.7 — incumbent-only regime reset (registered 2026-09-11, before any run)

A regime change is signalled only by the stand-down of the **incumbent** — a library that was live
when the current regime window began; a library reactivated inside the window and failing again is
recorded as an oscillation and does not reset the corpus. One change on top of v6.6 (`M2_V67`).

Predictions: **s604** — the ablation arm's regime-C cost ≤ RESET's (3 808); the four attribution
worlds and SHIFT45 / s602 / s604-shift within ± 2 % of v6.6; **fresh K1 test** on 613–615 (laptop) and
617–621 (LUNARC; 616 failed the ecology gate): both continual arms' regime-C cost ≤ RESET's on ≥ 7 / 8
fresh seeds and lifetimes ≤ the fixed controller's on ≥ 7 / 8, every arm verifying every target. The
same seeds also run v6.6 so the comparison is paired.
**Stop rule, stated now:** if v6.7 fails the s604 diagnostic or the fresh bar, the mixed-regime
limitation is recorded as a **boundary** — within a regime assembled from two earlier ones the
continual arm can cost more than RESET, while its lifetime stays below RESET — and this chain ends.

## v6.7 — outcome: FALSIFIED; stop rule applied (records/v67/)

s604 diagnostic: the ablation arm's regime-C cost **7 472** (v6.6: 6 039; RESET 3 808) — **failed**, and
worse. Regression: ABC s605 ablation 2 978.7 vs v6.6 2 761.5 (+7.9 %) — **failed**. Fresh K1 bar
(both continual arms' regime-C ≤ RESET on ≥ 7 / 8): failed (s613, s615, s619, s620, s621 each fail an
arm). Everywhere no oscillation occurred, v6.7 is byte-identical to v6.6 (four shift lifetimes, s613,
s614, s615, 618–621, the three cross-world pairs).

**Boundary, by the registered stop rule.** Within a regime assembled from motifs of two earlier
regimes, none of the controller variants tested (v6.3 → v6.7) keeps the continual *ablation* arm's
regime cost at or below RESET on every seed: the old libraries partly fit, oscillate between live and
stood-down, and the new regime's corpus is either starved (reset) or polluted (no reset). Its
*lifetime* stays below RESET on every fresh seed. This chain ends here. **v6.6 remains the current
controller.**

## What v6.6 does on the eight fresh A → B → C seeds (descriptive — suggested these seeds, confirms nothing)

| seed | RESET C | RESET life | fixed life | ablation C | ablation life | **full arm C** | **full arm life** |
|---|---|---|---|---|---|---|---|
| 613 | 3,766 | 3,543 | 2,727 | 3,868 | 2,612 | **3,575** | **2,414** |
| 614 | 3,886 | 3,700 | 2,735 | 3,045 | 2,002 | **3,404** | **2,228** |
| 615 | 2,647 | 3,194 | 2,408 | 5,012 | 3,093 | **2,450** | **2,204** |
| 617 | 3,146 | 3,326 | 2,457 | 2,522 | 2,184 | **2,522** | **2,184** |
| 618 | 3,582 | 3,670 | 2,758 | 3,115 | 2,252 | **2,800** | **2,146** |
| 619 | 3,550 | 3,486 | 2,785 | 2,852 | 1,936 | **3,720** | **2,226** |
| 620 | 3,741 | 3,509 | 2,461 | 5,506 | 2,764 | **3,386** | **2,005** |
| 621 | 3,916 | 3,609 | 2,929 | 4,330 | 2,718 | **2,835** | **2,220** |

The **full arm** (with the recombination candidate) is at or below RESET's regime-C cost on
**7 / 8**, below the fixed controller's lifetime on **8 / 8** and below RESET's lifetime on
**8 / 8**; the ablation arm on 4 / 8, 6 / 8, 8 / 8. Recombination ≤ 0.85 × the ablation's
regime-C cost on 3 / 8 — below the C3 bar; **C3 stays NOT_ESTABLISHED** and this is not C3
evidence. It is a K1 hypothesis about the current full controller, so it is registered for
confirmation on **new** seeds below instead of being promoted from the seeds that produced it.

**FV8 under the current controller (records/v67/runOCM_FV8_v66.json, _v67.json):** 59 741 = **+6.6 % vs
RESET**, all 120 targets verified, identical under v6.6 and v6.7 (no oscillation occurred) — the
failure-evidence rule's figure from v6.4, reproduced. FV8 remains a priced negative: the first validated
deep library still loses before the rule can act.

## K1-v6.6 confirmation (registered 2026-09-11, before any run)

Fresh A → B → C seeds 622–633 on LUNARC (12; any that fail the ecology gate are reported, not
replaced), five arms each, the v6.6 controller (`scripts_v66`, `M2_V67` unset). **Predictions for the
full continual arm:** lifetime below the fixed controller's on ≥ 10 / 12 of the seeds that pass the gate;
lifetime below RESET's on every such seed; regime-C cost at or below RESET's on ≥ 9 / 12; every arm
verifies every target. **Falsifier:** fewer than 10 / 12 below the fixed controller, or any lifetime
above RESET. Claim ceiling if it holds: in-life acquisition of a mixed regime by the current
controller beats the fixed-library controller over a lifetime, on fresh seeds, in this grammar.

## K1-v6.6 confirmation — outcome: FALSIFIED (records/k1v66conf/; every arm verifies every target)

Twelve fresh seeds were registered; s630 failed the ecology gate (reported, not replaced), leaving 11.

| seed | RESET life | fixed life | **full-arm life** | RESET C | full-arm C |
|---|---|---|---|---|---|
| 622 | 3,589 | 3,184 | **2,518** | 3,514 | 2,627 |
| 623 | 3,551 | 2,742 | **4,719** | 3,539 | 9,417 |
| 624 | 3,858 | 3,574 | **3,699** | 4,338 | 3,978 |
| 625 | 3,570 | 2,352 | **1,982** | 3,502 | 2,609 |
| 626 | 3,626 | 2,973 | **4,825** | 3,589 | 10,054 |
| 627 | 3,577 | 3,120 | **2,497** | 3,996 | 3,798 |
| 628 | 3,481 | 2,506 | **4,466** | 3,151 | 9,751 |
| 629 | 3,555 | 2,724 | **4,296** | 3,780 | 7,726 |
| 631 | 3,468 | 2,706 | **2,024** | 3,338 | 3,053 |
| 632 | 3,592 | 2,791 | **2,308** | 3,329 | 3,307 |
| 633 | 3,658 | 2,688 | **2,289** | 3,887 | 4,048 |

| bar | registered | measured |
|---|---|---|
| full-arm lifetime below the fixed controller | ≥ 10 / 12 | **6 / 11** |
| full-arm lifetime below RESET | every seed | **7 / 11** |
| full-arm regime-C cost at or below RESET | ≥ 9 / 12 | **6 / 11** |

The 8 / 8 on the seeds that suggested the claim did not replicate on fresh seeds — the reason it was
registered for confirmation rather than promoted. On four seeds (s623, s626, s628, s629) the full arm's
regime-C cost is 2.2–2.8 × RESET.

**Attribution (liveness logs and per-target excess, records/k1v66conf/).** Two defects, both visible:
(i) **retry spacing** — v4.2 retries a failed re-mining attempt after `min_new − min_new_after_fail`
new solutions and v6.2 lowered `need` to 12 when a pool exists, so the two composed into an attempt
every **4** targets instead of the intended 8; on s623 and s628 each failed validation charged
35–60 k (targets 109, 113, 117, 121, 125, 129); (ii) **oscillation of a library already recorded as
failing in deployment** — v6.4(c) raises the bar for *new* candidates but the failed library itself keeps
being re-probed back to life (s629: five `failed_deployment` events on the same library; s626: the
β = 8 420 library re-probed every cadence).

## continual_v6.8 (registered 2026-09-11, before any run)

(d) after a failed attempt the retry comes after `min_new_after_fail` **new** solutions whatever `need`
is (a composition bug, fixed to its stated intent); (e) a library that failed in deployment is
**retired** — not re-probed — until a regime change lifts retirements. Flags `M2_V68D`, `M2_V68E`;
defaults unchanged until validated.

*Diagnostic (one variable at a time; the failing seeds, not confirmation):* s623, s626, s628, s629 under
base / +d / +e / +d+e from the same dev states; registered expectation: +d+e cuts the full arm's
regime-C cost on all four and below RESET on ≥ 3 / 4. *Regressions:* SHIFT45 / s602 / s603 / s604,
E5, FV6, FV8 and the three cross-world pairs within ± 2 % of v6.6. **K1-v6.8 confirmation** on new
fresh seeds 634–645 (LUNARC; five arms, full dev phase): the same bars as K1-v6.6, unchanged —
full-arm lifetime below the fixed controller on ≥ 10 / 12 of the seeds that pass the gate, below RESET
on every one, regime-C at or below RESET on ≥ 9 / 12, every arm verifying every target.
**Stop rule, stated now:** if K1-v6.8 fails, the continual controller's K1 claim on mixed regimes is
recorded **NOT_ESTABLISHED at this grammar**; the continual-development claim stays scoped to regime
shifts (12 / 12 lifetimes) and cross-world acquisition (3 / 3 pairs).

## continual_v6.8 regressions — outcome: one registered bar FAILED (laptop billy, billy-old; every target verified)

| run | v6.6 | v6.8 | change |
|---|---|---|---|
| SHIFT45 | 1 497 | 1 497 | 0 |
| SHIFT45 s602 | 1 758 | 1 642 | −6.6 % |
| SHIFT45 s603 | 1 577 (v6.7) | 1 538 | −2.5 % |
| SHIFT45 s604 | 1 891 | 1 891 | 0 |
| A→B→C s604 (full arm) | 3 498 | 3 478 | −0.6 % |
| A→B→C s613 | 2 414 | 2 156 | −10.7 % |
| A→B→C s614 | 2 228 | 2 060 | −7.5 % |
| A→B→C s615 | 2 204 | 2 143 | −2.8 % |
| E5 | 414 | 414 | 0 |
| FV6 | 2 103 | 2 103 | 0 |
| cross-world E5 → E7 | 29 974 | 29 974 | 0 |
| cross-world E8m7 → E7 | 30 028 | 30 028 | 0 |
| **cross-world E7 → E8m7** | **14 443** | **21 921** | **+51.8 % (bar: ± 2 %)** |

Several runs improved by more than the ± 2 % band (reported as outside the band, in the favourable
direction). E7 → E8m7 regressed far outside it; it is still below the fixed controller (41 036) but
the cross-world ratio worsens from 0.35 to 0.53. **v6.8 therefore cannot become the default**, whatever
its K1 confirmation shows. FV8 is still running.

**Attribution (one variable at a time, billy-old):** d alone reproduces 21 921 exactly; e alone gives
14 443, identical to v6.7. Mechanism, from the liveness and re-mining logs: (d) moves the re-mining
schedule from targets 12 / 16 / 20 / 24 to 12 / 20 / 28, so a different first library deploys (MDL
at 28, not frequency at 24); it stands down at 40 after three consecutive misses — positive realised
value, so (e) does not retire it; the re-mine at 41 finds no candidate that passes the tilability bar;
and at 44 the cadence re-probe **revives the stood-down library on a single hit**, which pre-empts every
further re-mining until 62 (targets that v6.7's second library solved at ≈ 12 k cost 45–80 k).
v6.7 avoided this only because its re-mine at 39 succeeded before a cadence tick. d is not the defect
— it does what it states; the defect is that a library measured and stood down *inside the regime it
was learned in* can be revived by a sporadic hit — the same oscillation seen on s626 and s629, which
(e) covers only when the library's value went negative.

## continual_v6.9 (registered 2026-09-11, before any v6.9 run)

(f) a library that stands down inside its own regime (the v5.4 branch: not a regime change) is
**retired until the regime changes**, like a library that failed in deployment. Flag `M2_V69F` on top
of d and e; defaults unchanged. Predictions: **E7 → E8m7 ≤ 14 732** (v6.7 + 2 %); every other
regression above no more than 2 % worse than v6.8; on the diagnostic seeds s623 / s626 / s628 / s629
the full arm's regime-C cost at or below v6.8's (+d+e) on each. **K1-v6.9 confirmation** on new fresh
seeds 646–657 (LUNARC), same bars as K1-v6.6 / v6.8. **Stop rules:** v6.8's stop rule stands for v6.8
and is not rescued by v6.9. If K1-v6.9 also fails, the flag-level revision chain for mixed-regime K1
closes: K1 on mixed regimes is NOT_ESTABLISHED at this grammar for the continual controller, and the
next attempt must be a different mechanism class (for example an explicit regime-change detector),
not another retry or retirement flag.

## Outcomes of the v6.8 / v6.9 registrations (2026-09-11; every arm verifies every target)

**K1-v6.8 confirmation (fresh seeds 634–645, all 12 gated; records/k1v68conf/) — FAILED.** Full-arm
lifetime below the fixed controller **8 / 12** (bar ≥ 10 / 12); below RESET 12 / 12; regime-C cost at or
below RESET **7 / 12** (bar ≥ 9 / 12). **The registered stop rule fires: K1 on mixed regimes is
NOT_ESTABLISHED at this grammar.** This is recorded as the outcome, not as pending a later version.

**v6.8 diagnostic (records/k1diag/) — second bar FAILED.** On s623 / s626 / s628 / s629, +d+e cut the full
arm's regime-C cost on all four (9 417 → 5 223, 10 054 → 4 635, 9 751 → 6 444, 7 726 → 5 311), but below
RESET on **0 / 4** (registered ≥ 3 / 4). Lifetimes stay 13–34 % above the fixed controller on all four.

**v6.8 FV8 regression:** 58 325 vs 59 741 (−2.4 %).

**v6.9 regressions — E7 → E8m7 FALSIFIED.** 20 511 against the registered ≤ 14 732 (v6.8: 21 921). (f)
worked as stated — the stood-down library was retired at 40 and a new one deployed at 49 — but the
residual gap is d's later schedule: the early failed attempts on this pair were **uncharged**, so d's
spacing bought nothing and delayed the first deployment from 24 to 28. Every other regression was
identical to or cheaper than v6.8: SHIFT45 1 497, s602 1 642, s603 1 538, s604 1 891, A→B→C s604 3 478,
s613 2 135, s614 2 038, s615 2 108, E5 414, FV6 2 103, FV8 58 325, E5 → E7 29 974, E8m7 → E7 30 028.
v6.9 diagnostic: regime-C at or below +d+e on 4 / 4 (identical on three; s628 6 296 vs 6 444) — passed.
*Latent limitation seen in the logs:* in the shift worlds the regime-B library stands down at 91–92, just
after the return to A, and (f) classes that as an in-regime stand-down and retires it; costless in these
lifetimes, but a lifetime returning to B a second time would have to re-mine instead of paying one probe.

**K1-v6.9 confirmation (fresh seeds 646–657, all 12 gated; records/k1v69conf/) — FAILED.** Lifetime
below the fixed controller **11 / 12**; below RESET 12 / 12; regime-C at or below RESET **5 / 12** (bar ≥ 9 / 12).
Per the v6.9 stop rule the flag-level revision chain for mixed-regime K1 is **closed**.

## CORRECTED: the primary cause of the K1-v6.6 falsification is a failure-evidence lock-out

The attribution recorded above (retry spacing; oscillation) was secondary. The v6.4(c) / v6.6
failure-evidence bar requires a candidate to tile **more** validation tasks than the best library that
failed in deployment. With `val_n` = 8, a failed library that tiled 8 / 8 sets a bar of 8 that **no
candidate can clear**, and the bar is never lowered. From then on every re-mining attempt still charges its
validation probes and cannot deploy: s623's first such attempt had an MDL candidate winning 8 / 8 with a
positive lower bound, refused. Charges on these impossible attempts: s623 253 877, s626 210 441, s628
251 482, s629 95 567 (0.7–1.9 k per target of lifetime); d only halves their number.

*Observational separation, pooled over K1-v6.6 / v6.8 / v6.9 (three runner versions, 35 seeds):* every
seed that entered the lock-out lost to the fixed controller (**7 / 7**); seeds that never entered it beat
the fixed controller on **25 / 28**. The causal test is v6.10 below. The regime-C bar is a separate
negative: six seeds with no lock-out still pay more than RESET in C — the recombination regime already
recorded as C3 NOT_ESTABLISHED.

## continual_v6.10 (registered 2026-09-11, before any v6.10 run)

Registered after K1-v6.9's outcome and after its stop rule closed the flag chain. It is **not** a further
K1 revision and cannot rescue v6.6 / v6.8 / v6.9: it repairs a defect found in the evidence (the lock-out),
and it tests a **narrower, separately named claim**, stated here before its run.

- **(h) futility bar** (`M2_V610H`): a candidate whose tilable count cannot clear the failure-evidence bar is
  not probed — the bar is the third conjunct of the deployment criterion and is known before any probe.
  **Decision-invariant by construction.** Falsifier: on every run, the deploy / stand-down / retirement /
  reactivation log must be **identical** to v6.9 (the `chosen` field of failed re-mining events is exempt: a
  skipped candidate reports zero wins, so the reported best of a failed attempt can differ); lifetime never
  higher, and lower by at least the impossible-attempt charge over the target count on lock-out seeds.
  (h) alone is **not** predicted to beat the fixed controller.
- **(i) regime-scoped failure evidence** (`M2_V610I`): the bar is reset when a new regime begins (where
  retirements are already lifted). Behavioural. Predicted **inert** (identical results) where no regime
  reset follows a failed deployment: the three cross-world pairs, E5 and FV6.
- **Diagnostic** (LUNARC, one variable at a time on top of v6.9): h / i / h+i on the seven lock-out seeds
  (623, 626, 628, 629, 636, 642, 647) and three identity controls (634, 640, 646). Prediction for h+i:
  lifetime below the fixed controller on ≥ 5 / 7 lock-out seeds.
- **Claim under test — K1-L, lifetime advantage on mixed regimes** (narrower than K1, which stays
  NOT_ESTABLISHED): on new fresh seeds 658–669 under h+i, full-arm lifetime below the fixed controller on
  ≥ 10 / 12 gated seeds and below RESET on every one, every arm verifying every target. The regime-C bar is
  **not** predicted to pass and is reported alongside. Regressions: everything above identical to v6.9 under
  (h), and within + 2 % of v6.9 under h+i. Stop rule: if K1-L fails, the lifetime claim on mixed regimes is
  NOT_ESTABLISHED at this grammar too.

Defaults remain continual_v6.6 throughout, so the standing positives — regime-shift lifetimes (12 / 12) and
cross-world acquisition (3 / 3 pairs) — are unaffected by any of the above.

## Outcomes of the continual_v6.10 registration (2026-09-11; every arm verifies every target)

**(h) is decision-invariant — confirmed.** The deploy / stand-down / retirement / reactivation log is
identical to v6.9 on **10 / 10** diagnostic seeds (s634 / s636 / s640 / s642 against v6.9 reference runs
added for this check, records/k1diag610/), on the four shift worlds, four A → B → C seeds, E5 and FV6.
Lifetime is never higher and falls where futile validation was being paid: s623 3 686 → 2 913, s626
3 370 → 3 040, s628 3 314 → 2 461, s629 3 388 → 2 892, s642 3 400 → 2 646, s647 3 417 → 2 677, s640 2 630
→ 2 537, A → B → C s615 2 108 → 2 021; regime-C cost falls by up to 40 %.

**Host regressions (14 runs each for h and h+i; laptop billy, billy-old):** (h) is identical to v6.9 in
both cost and log on all of them — SHIFT45 / s602 / s603 / s604, A → B → C s604 / s613 / s614 (s615 is
cheaper, as above), E5, FV6, FV8 58 325 and the three cross-world pairs (E7 → E8m7 stays 20 511, so v6.9's
E7 → E8m7 falsification is untouched by (h)).

**(i) had no effect anywhere it was run.** h+i equals h in cost on all ten diagnostic seeds and on every
host run; its log differs from h only by `evidence_reset` entries in the shift and A → B → C worlds, and
is identical on the cross-world pairs, E5, FV6 and FV8 as predicted. Mechanism: no regime reset follows a lock-out in these lifetimes — once the
developmental library is gone the organism has no regime-change signal, so a regime-scoped reset never
fires. (i) is reported as having no demonstrated effect, not carried as a live mechanism.

**Diagnostic prediction for h+i — FALSIFIED.** Lifetime below the fixed controller on **2 / 7** lock-out
seeds (s628 2 461 vs 2 506, s647 2 677 vs 2 772; s642 misses by 0.3 %), against the registered ≥ 5 / 7.
The lock-out itself persists; (h) only stops paying for it.

**K1-L confirmation (fresh seeds 658–669; s665 failed the ecology gate and is reported, not replaced;
records/k1l610/) — PASSED.** Full-arm lifetime below the fixed controller **11 / 11** gated seeds and below
RESET **11 / 11**, every arm verifying every target. Reported alongside, not predicted: regime-C cost at or
below RESET on **10 / 11**. The one lock-out seed (s662) also beat the fixed controller (2 533 vs 2 675).
**K1-L — lifetime advantage on mixed regimes — is established at C2 scope, under continual_v6.10hi.** K1
itself stays NOT_ESTABLISHED: its verdict (v6.6 / v6.8 / v6.9) is not amended by this result.

## Registered next (2026-09-11, before any of these runs)

- **Bar arithmetic, fixed once.** A count bar "≥ k / 12" means a proportion of **gated** seeds:
  pass iff (passing seeds) / (gated seeds) ≥ k / 12, with at least 10 gated seeds; otherwise CANNOT_CHECK.
  (Earlier reports applied ≥ 10 / 12 as 10 of 11; under this rule that is ≥ 0.833, i.e. 10 of 11 passes and
  9 of 11 fails — unchanged outcomes.)
- **K1-L attribution (LUNARC, h-only on the eleven K1-L dev states).** Prediction: identical to h+i on every
  seed. If it holds, the K1-L pass is attributed to (h) alone.
- **K1 under v6.10hi — a new claim with its own lineage**, registered after the lock-out repair: fresh
  seeds 670–681, all three original bars unchanged (lifetime below the fixed controller ≥ 10 / 12 and below
  RESET on every gated seed, regime-C at or below RESET ≥ 9 / 12, every arm verifying every target). Stated
  mechanism: validation charges land in the regime-C window, so removing futile ones moves that number
  directly; a pass would show the regime-C cost was largely an artefact of futile validation, **not** that
  recombination improved — C3 stays NOT_ESTABLISHED on its own terms. The v6.6 / v6.8 / v6.9 K1 verdict
  stands. Stop rule: if it fails, K1 on mixed regimes stays NOT_ESTABLISHED and the next attempt must
  address regime-change detection.
- **Adopt (h) into the defaults — identity check on the v6.6 base** (`continual_v6.6+h`, hosts): identical
  liveness logs and cost never higher than v6.6 on SHIFT45 / s602 / s603 / s604, A → B → C s604 / s613 /
  s614 / s615, E5, FV6, FV8 and the three cross-world pairs. The cross-world pairs have no v6.6 baseline run,
  so each gets both a v6.6 and a v6.6+h run and is compared pairwise. If identity holds everywhere, (h)
  becomes part of the default controller.

