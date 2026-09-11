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

## Outcome

_pending_
