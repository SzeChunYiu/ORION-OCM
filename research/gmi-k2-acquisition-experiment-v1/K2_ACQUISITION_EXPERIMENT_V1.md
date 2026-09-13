# K2 acquisition: a positive at a registered scope, and why #323 failed

Status: **K2 SUPPORTED AT REGISTERED MICROWORLD SCOPE; #323 REMAINS NOT_ESTABLISHED**
Date: 2026-09-13

`DC-3` records K2 — retained capital making acquisition of **new** capital
cheaper — as `NOT_ESTABLISHED` at the #323 grammar, bar held on 2 of 9 seeds.
`KRC` predicted the failure mode. This unit runs the experiment.

## 1. KAE-1 — the world, fixed before the numbers

Programs are sequences over four primitives (`inc`, `dec`, `double`, `square`),
evaluated on probes `(0,1,2,3)`. A target is a semantics. Acquisition searches
programs in length order and charges **one unit per candidate examined** — an
exact integer, never a timing. The `H` arm searches an alphabet extended by its
retained library as callable macros; `RESET` searches primitives only.

`K2` is the marginal comparison `cost_H < cost_RESET` on a target neither arm
has solved.

## 2. KAE-2 — reuse must be defined semantically

An earlier classifier asked whether a library part appears as a **substring** of
the target's program. That is wrong: `(inc,double)` and `(double,inc,inc)` have
the same semantics on the probes while sharing no substring, and a target's
recorded program need not be minimal. The corrected predicate is semantic —
**reuse is available iff the library shortens the minimal description**,
`L_H < L_R`. Three of five early mismatches were this classifier defect.

## 3. KAE-3 — necessity, replicated, with no counterexample

Across four libraries and two disjoint target populations:

| population | distinct targets | library-target pairs without reuse | K2 without reuse |
|---|---|---|---|
| exploratory (min length ≤ 4) | 206 | 603 | **0** |
| held-out (min length exactly 5) | 448 | 1,104 | **0** |

Each target is tested once **per library**, so the pair counts exceed the
distinct-target counts; 603 = 205+126+163+109 and 1,104 = 448+195+300+161.

**1,707 no-reuse targets, zero K2 successes.** The held-out population was
never examined at the smaller search cap, so it is not the set the predicate was
developed on. Terminal: `NECESSITY_HOLDS_NO_COUNTEREXAMPLE`.

## 4. KAE-4 — K2 is positive where reuse exists, and sufficiency is partial

| library | held-out K2 \| reuse | held-out K2 \| no-reuse |
|---|---|---|
| `squares` | **148 / 148** | 0 / 300 |
| `orig` | 129 / 253 | 0 / 195 |
| `three_part` | 113 / 287 | 0 / 161 |

So K2 **holds** — at 100% for one library on held-out targets — and reuse is
necessary but **not sufficient**: rates run from 45% to 100%. The asymmetry is
the result, and an iff would be false.

The fourth library, `dec_inc`, is absent from this table on purpose. It has
**zero** reuse targets in the held-out population, so it tests necessity and
harm (448/448 strictly worse) and says nothing at all about sufficiency.
Counting all four libraries as if each tested both directions would overstate
the evidence.

## 5. KAE-5 — absent reuse, retention is harmful, not neutral

On held-out no-reuse targets `H` is strictly **worse** in 195/195, 300/300,
161/161 and 448/448 cases — 100% in every library. Macros enlarge the search
alphabet; with nothing to shorten, the inflation is pure cost. A bare negative
that reports "no benefit" misses this.

**Ties are a third category and are not folded into either side.** In the
exploratory population the `orig` library gives 126 no-reuse targets as
0 K2 + 123 harmed + **3 exact ties**, so "100% harm" is a statement about the
held-out population only, not about every run. The three buckets are required
to exhaust the population, and a test enforces that.

## 6. KAE-6 — what this says about the #323 negative

`DC-3` attributes the 2/9 outcome to retained-capital recombination at that
grammar. KAE-5 supplies the mechanism: where targets do not decompose, a
retained library **raises** acquisition cost. That is a prediction about #323,
not a measurement of it — this microworld is not that assay, shares none of its
code, and no number here came from it. The registered retry should record each
target's decomposition size so the two modes can be told apart.

## 7. Parent subtraction

Library learning is **parent-owned**: reusing acquired abstractions to shorten
later search is the mechanism behind DreamCoder-style abstraction and
Voyager-style skill libraries. This unit claims **no novelty** for that. Its
contributions are the necessity result under a semantic predicate, the measured
harm when reuse is absent, and the cost-model boundary in KAE-8.

## 8. KAE-7/8 — where the KRC condition stops applying

`KRC` proves `K2 ⟺ L ∩ P ≠ ∅` in a unit-charge model with no alphabet. That
model omits search-alphabet inflation, so it does not govern enumeration. Two
candidate laws built from level totals — `|A_H|^{L_H} < |A_R|^{L_R}` and its
cumulative form — each mispredicted **13 of 206** cases, all in the same
direction, because both arms stop **partway through** their final level
(`RESET` at index 133 of 340, `H` at 187 of 258). Position within a level, not
alphabet size or length, decides those cases. No law built from level totals can
capture it, and none is registered here.

## 9. Scope and falsifiers

Not claimed: K2 at #323 or any other assay; that this microworld's costs model
any runtime; that reuse is sufficient; that the harm rate transfers.

Falsified if any no-reuse target anywhere shows `cost_H < cost_RESET`; if the
held-out counts disagree with the frozen receipt; or if a library with nonzero
reuse targets shows K2 at 0.
