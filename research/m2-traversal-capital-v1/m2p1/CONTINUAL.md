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

