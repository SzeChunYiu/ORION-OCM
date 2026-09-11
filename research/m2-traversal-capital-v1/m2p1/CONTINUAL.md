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
