# AH4L-1 … AH4L-6 — what the L0–L8 ladder is at the registered scope

All results are stated at the registered finite scope fixed in `FREEZE_V1.md`. Every number is
reproduced by `RESULT_V1.json` (route A), `ORACLE_RESULT_V1.json` (route B) and
`TEST_RESULT_V1.json`. The issue calls the ladder provisional; this note reports what it
measures to be, including where it is weaker than the wording suggests.

---

## AH4L-1 — Eight invariants, each decidable, each with both outcomes present

**Statement.** Each transition `L_i -> L_(i+1)` has an exactly computable invariant, and the
registered universe contains systems on both sides of all eight.

**Result.** `I1` 234 pass / 26 fail · `I2` 144 pass / 116 fail · `I3` 15,680 irreducible of
67,600 composites · `I4` 4 witness sites against 0 for its matched control · `I5` growth 1
against 0 · `I6` and `I7` each separating with their controls flat · `I8` description delta
`-7` and search delta `-3` against `0` and `0` for a renaming unit, expressive delta `0` on
both. No invariant returned an error terminal on any registered system.

**Assumptions.** Binary input and output; zero or one persistent state cell; the organization
set rebuilt here rather than imported. The reconstruction reproduces the merged AJ4 numbers
exactly: 260 systems, 148 behavioural classes, class-size histogram `{1: 144, 29: 4}`.

**Falsifier.** An invariant with no passing or no failing system at this scope is published as
`NOT_SEPARATING_AT_SCOPE`. None was.

**Strongest parents.** Mealy machine theory, the product construction, Moore's length bound
and partition refinement, macro libraries and their expressive neutrality. None is claimed
novel.

---

## AH4L-2 — Only two of the eight transitions separate on visible behaviour

**Statement.** Sorting each invariant by what it can see:

| transition | verdict |
|---|---|
| `L0 -> L1` | `SEPARATING_ONLY_ON_DESCRIPTION` |
| `L1 -> L2` | `SEPARATING_ON_VISIBLE_BEHAVIOUR` |
| `L2 -> L3` | `SEPARATING_ON_VISIBLE_BEHAVIOUR` |
| `L3 -> L4` | `SEPARATING_ONLY_ON_DESCRIPTION` |
| `L4 -> L5` | `SEPARATING_ONLY_ON_DESCRIPTION` |
| `L5 -> L6` | `SEPARATING_UNDER_DECLARED_EXTERNAL_BOUNDARY` |
| `L6 -> L7` | `SEPARATING_UNDER_DECLARED_EXTERNAL_BOUNDARY` |
| `L7 -> L8` | `SEPARATING_ONLY_ON_DESCRIPTION` |

**How the verdict is derived.** The rule is fixed in the code before any number is read: no
passing or no failing system gives `NOT_SEPARATING_AT_SCOPE`; an invariant that reads a value
outside the visible input gives `SEPARATING_UNDER_DECLARED_EXTERNAL_BOUNDARY` and must exhibit
that boundary; an invariant that splits a behavioural equivalence class gives
`SEPARATING_ONLY_ON_DESCRIPTION`; otherwise `SEPARATING_ON_VISIBLE_BEHAVIOUR`.

**Evidence for the description-only verdicts.** `I1` splits 2 of the 148 behavioural classes:
two systems with identical word behaviour differ on motif reuse. `I4` is exhibited to collapse:
its adaptive witness is re-described as a plain transducer over the pair `(state, experience)`
and the re-description reproduces it on every one of the 62 registered words. `I5` and `I8` are
defined on operator inventories rather than on transducers, and `I8` is deliberately worded so
that expressive power is unchanged — a merged parent already proved a macro library adds zero
expressive power, so a level-8 claim resting on new expressive power would contradict it.

**Evidence for the external-boundary verdicts.** `I6` exhibits two adoption attempts with
identical internal state and identical visible input whose outcomes differ — `(0,1,0)` against
`(1,1,1)` — because only the registered authority differs; the internal-guard control produces
identical outcomes. `I7` exhibits a state reachable in 23 steps with the transfer channel and
only 22 without, with the acquired distinction named.

**Reading.** At this scope the ladder is not eight behavioural levels. Two transitions are
behavioural (`L1->L2` and `L2->L3`), two are relative to a declared internal/external boundary
and collapse when that boundary is absorbed into the input, and four are distinctions of
description. The counts are published in the receipt as `verdict_counts` so the claim is read
off a measurement. That is a
statement about the registered scope, not a claim that the higher levels are empty.

**Forbidden extrapolation.** `PERIODIC_TABLE_OF_MI_COMPLETE`,
`ALL_ORGANIZATION_LEVELS_ENUMERATED`.

---

## AH4L-3 — `L1 -> L2` needs an intermediate layer, and it has 112 members

**Statement.** The `L2` wording — "state-bearing modules" — conflates two clauses that the
registered universe separates.

**Result.** Of 260 systems: 144 hold a state cell **and** are behaviourally distinguishable
from every cell-free system; **112 hold a state cell whose distinction never reaches the
external word behaviour**; 4 hold no cell. The fourth combination, behaviourally
history-dependent without a cell, is empty — 0 systems, as it must be.

**Consequence.** An intermediate layer sits between `L1` and `L2` and must be named rather than
absorbed into either neighbour. It is the 112 systems that are state-bearing but not
history-dependent. The 112 are exactly the non-cell-free members of the four 29-element
behavioural classes.

**Falsifier.** If the cell-only population were 0, the two clauses would coincide at this scope
and no intermediate layer would be indicated.

---

## AH4L-4 — The ladder is not cumulative at its own base

**Statement.** Fourteen registered systems satisfy `I2` while failing `I1`: they are
history-dependent without reusing any local transition effect.

**Result.** `non_cumulative_base_systems = 14`.

**Consequence.** "At level `k`" cannot be read as "satisfies `I1 … Ik`". The ladder is a
partial order at this scope, not a total one. `LADDER_IS_TOTAL_ORDER` is in the forbidden set
for exactly this reason.

**Falsifier.** A registered universe in which every `I2` system also passes `I1` would make the
base cumulative.

---

## AH4L-5 — Nearest negatives exist for every transition, and the distances are small

**Statement.** For each transition there is a system that passes every invariant up to `L_i`
and fails `L_i -> L_(i+1)`, at a measured minimum edit distance in the declared description
encoding.

**Result.** `I1` 2 · `I2` 1 · `I3` 1 · `I4` 7 · `I5` 1 · `I6` 1 · `I7` 1 · `I8` 1. Each is the
exhaustive minimum over increasing Hamming radius, with the flipped positions and the resulting
description published.

**Reading.** Seven of the eight transitions are one or two description bits wide. `I4` is the
outlier at 7: removing experience conditioning requires agreement at every site of both update
tables. A level boundary that a single bit flip crosses is a weak boundary, and the numbers say
so rather than hiding it.

**Falsifier.** A transition with no failing neighbour at any radius would mean the invariant is
not separating in the description encoding; the executor publishes `RED` in that case.

---

## AH4L-6 — Level membership is not intelligence, and a configuration trips the prohibition

**Statement.** The prohibition is not vacuous at this scope: level order and capability order
disagree, in both directions, on the registered task set.

**Result.** Over the 260 systems and the five registered tasks with exact rational scores on 14
protected words, there are **1,914** ordered pairs in which the higher-level system is strictly
dominated in capability by the lower-level one. The first is `M101` at level 2 with capability
`(0, 3/7, 3/14, 3/14, 0)` against `S002` at level 0 with `(0, 1, 3/14, 3/14, 0)` — a cell-free
system that solves negation perfectly while a history-dependent one does not.

**The checker.** `level_claim_verdict` refuses any claim of the form "this system is
intelligent" that is not accompanied by registered capability **and** development evidence,
returning `REFUSED__LEVEL_MEMBERSHIP_IS_NOT_INTELLIGENCE`. It admits the same claim when both
evidences are present (`ADMITTED_WITH_EVIDENCE`) and does not touch a claim that merely states
a level (`NOT_AN_INTELLIGENCE_CLAIM`). All three branches are exercised, and two hostiles plant
a checker that always refuses and one that never does.

**Falsifier.** If no configuration could trip the prohibition, the row would be vacuous and
would stay unchecked. 1,914 inversions and a tripping configuration make it live.

**Forbidden extrapolation.** `LEVEL_MEMBERSHIP_IS_INTELLIGENCE`,
`HIGHER_LEVEL_IMPLIES_HIGHER_CAPABILITY`.
