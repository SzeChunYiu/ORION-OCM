# Teaching, imitation and cultural accumulation — checklist items 18 and 19

Date: 2026-09-13. Status: **DERIVATION + EXACT WITNESS**. Closes two gaps the coverage audit recorded as
absent: *"all 26 occurrences of 'teaching' are the event-alphabet sense, a supervised input label, not
pedagogy — no imitation, no demonstration, no sender-cost/receiver-benefit result"* and *"no
individual → social → persistent-culture chain."*

Nothing new is assumed. The claim is that **transmission across agents is the same break-even as reuse
across time**, with the population as the reuse count.

## 1. The identification

PVR-3 prices reuse within one agent: `fresh = rC`, `retain = C + S + (r−1)U`. Read the same ledger across
agents instead of across time:

| | within one agent, over time | across agents |
|---|---|---|
| `C` | derive the lemma once | one agent derives the skill alone |
| `S` | store and index it | **transmit** it — the sender's teaching cost |
| `U` | look it up later | **absorb** it — the receiver's cost of learning from a demonstration |
| `r` | later occurrences | **the population** |

So `fresh = nC` (everyone derives alone) against `taught = C + S + (n−1)U` (one derives, teaches, the rest
absorb). **This is PVR-3 verbatim.**

> **Teaching pays exactly when `n > 1 + S/(C − U)`, and never when `U ≥ C`.**

**Imitation is the `S → 0` case** — no deliberate sender cost, the receiver merely observes. The threshold
collapses to `n > 1`: **imitation pays from the second learner onward whenever observing is cheaper than
deriving.** That is why imitation is the cheap and ubiquitous case and explicit teaching is the rarer one:
teaching must clear a threshold that imitation does not.

## 2. Verified against the closed form (`gmi_microscope/teaching_culture_witness.py`)

| `C` | `S` | `U` | predicted threshold | first `n` where teaching wins | agrees |
|---:|---:|---:|---|---|---|
| 10 | 3 | 1 | 1.333 | 2 | ✅ |
| 10 | 12 | 1 | 2.333 | 3 | ✅ |
| 6 | 3 | 2 | 1.75 | 2 | ✅ |
| 5 | 1 | **5** | **never** (`U ≥ C`) | none | ✅ |
| 8 | 0 | 2 | 1.0 | 2 | ✅ |
| 20 | 30 | 4 | 2.875 | 3 | ✅ |

Every cell matches, including the impossibility case.

## 3. Cultural accumulation (item 19) is the same law in the generation limit

A retained skill also serves later cohorts at `U`, so with `G` generations of `n` agents the reuse count is
`G·n`:

| generations | derive-alone | with transmission | saving | ratio |
|---:|---:|---:|---:|---:|
| 1 | 40 | 16 | 24 | 2.50 |
| 10 | 400 | 52 | 348 | 7.69 |
| 100 | 4 000 | 412 | 3 588 | **9.71** |

**The per-agent cost tends to `U` and becomes independent of `C`.** However expensive a skill was to
discover, a culture that retains it pays only the cost of absorbing it. That is the individual → social →
persistent chain, derived rather than asserted, and it is unbounded in `G`.

## 4. What the law does not say — and this is the load-bearing limit

At `n = 4`, `C = 10`, `S = 3`, `U = 1` the **population** saves 24. The **sender** pays `C + S = 13`
where deriving alone would have cost `C = 10` — the sender is **worse off by exactly `S`.**

> Teaching is **population-rational and sender-irrational.** The law derives when transmission pays *for
> the group*; it does not derive why any individual would pay to transmit.

That gap is **item 16** (shared obligation, reciprocity, compensation), not item 18, and it is named here
rather than papered over. Imitation escapes it entirely: with `S = 0` nobody pays to transmit, which is a
second reason imitation should be the common case.

## 5. One law, four items

The same break-even now governs:

* **item 7** — consolidation versus replay (reuse across time, against a capacity bound);
* **item 10** — skill chunking and why levels are self-limiting (reuse across contexts);
* **item 18** — teaching and imitation (reuse across agents);
* **item 19** — cultural accumulation (reuse across generations).

Memory, skill, pedagogy and culture are the same accounting at four scales. That unification is the result;
each individual item is a specialization of it.

**Falsifier:** any regime inside PVR-3's assumptions where transmission strictly beats deriving with
`n ≤ 1 + S/(C−U)`, or where `U ≥ C` yet transmission still wins. Either breaks PVR-3, not this reading.
**Assumptions inherited:** no invalidation or eviction, stable validity, constant independent costs — and,
added here, faithful transmission. Lossy transmission raises the receiver's effective `U` and therefore the
threshold.
