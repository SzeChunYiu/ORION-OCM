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

**Dependencies.** The ladder quoted from the issue and the eight invariants `I1_MOTIF_REUSE` …
`I8_NEW_EFFECTIVE_UNIT` fixed in `FREEZE_V1.md` sections 1–2; the registered universe of
section 3, rebuilt here and checked against `gmi-833-aj4-process-organizations-v1` (blob
pinned in `MANIFEST_V1.json`); for `I6` the propose/verify/adopt transitions owned by
`gmi-833-g0-governed-self-change-v1`, and for `I8` the macro-library result of
`gmi-833-developmental-reuse-v1`. Every count is published in `RESULT_V1.json` and recomputed
by route B in `ORACLE_RESULT_V1.json`.

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

**Assumptions.** The universe and invariant definitions of AH4L-1; behavioural equivalence
decided by reachable product exploration over binary words (`FREEZE_V1.md` section 3); the
verdict rule stated under "How the verdict is derived", fixed in the code before any number
was read, including the declared internal/external boundary for `I6` and `I7`. The verdicts
describe this scope only, as the Reading paragraph says.

**Dependencies.** AH4L-1, whose eight separating invariants rule out
`NOT_SEPARATING_AT_SCOPE`; the 148 behavioural classes of
`gmi-833-aj4-process-organizations-v1`, reproduced here; the `I4` re-description exhibit
(`i4_collapses_under_absorption`), the `I6` adoption exhibit, whose propose/verify/adopt
transitions `gmi-833-g0-governed-self-change-v1` owns, the `I7` 23-against-22-step exhibit,
and the `gmi-833-developmental-reuse-v1` result that a macro library adds zero expressive
power; `verdicts` and `verdict_counts` in `RESULT_V1.json`.

**Falsifiers.** A behavioural class split by `I2` or `I3` would move that transition off
`SEPARATING_ON_VISIBLE_BEHAVIOUR` (the no-alarm case asserts that `I2` splits none); a
registered word on which the `(state, experience)` re-description disagrees with the `I4`
adaptive witness would void the `L3 -> L4` collapse; and an `I6` or `I7` exhibit that is
missing (`EXTERNAL_BOUNDARY_NOT_EXHIBITED`) or that persists with the guard made internal or
the channel removed would void the external-boundary reading. The hostiles
`governed_internal_guard` and `population_without_channel` plant the last two cases and are
detected (`TEST_RESULT_V1.json`).

**Strongest parents.** Mealy (1955) for the transducers and Moore (1956) for the length bound
and partition refinement that decide behavioural equivalence; Hartmanis and Stearns (1966) on
state structure versus external behaviour; `gmi-833-developmental-reuse-v1`, which forces the
description-only reading of `L7 -> L8`; Lamport (1998) for the attested-update shape behind
`I6` (`PARENT_LEDGER.md`).

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

**Assumptions.** The 260-system universe of AH4L-1 (4 cell-free and 256 one-cell systems,
binary input and output); the two clauses of `I2` as frozen in `FREEZE_V1.md` section 2,
clause (b) comparing word behaviour against every cell-free system at the same interface by
reachable product exploration. The intermediate layer is indicated by the frozen rule of
section 5 that a proper non-empty subset of an invariant's clauses names a layer.

**Dependencies.** AH4L-1's rebuilt universe and its class-size histogram `{1: 144, 29: 4}`;
the `I2` clause decomposition; `i2_clause_counts` and `i2_intermediate_layer_population` in
`RESULT_V1.json`, matched by route B; the hostile `intermediate_layer_erased` in
`TEST_RESULT_V1.json`, whose control requires exactly 144 and 112.

**Strongest parents.** Hartmanis and Stearns, *Algebraic Structure Theory of Sequential
Machines* (1966), which owns why a state cell need not reach the external behaviour; Mealy
(1955) and Moore (1956) for the transducers and their equivalence;
`gmi-833-aj4-process-organizations-v1` for the organization set (`PARENT_LEDGER.md`).

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

**Assumptions.** The 260-system universe of AH4L-1 with `I1` and `I2` exactly as frozen in
`FREEZE_V1.md` section 2; "cumulative" means that every system passing `I2` also passes `I1`,
and the frozen falsifier of section 5 requires a partial order to be published when that
fails. The count is a statement about this universe, not about larger budgets.

**Dependencies.** The `I1` and `I2` predicates of AH4L-1 and the `I2` clause counts of AH4L-3;
`non_cumulative_base_systems` in `RESULT_V1.json`, matched by route B in
`ORACLE_RESULT_V1.json`; the forbidden promotion `LADDER_IS_TOTAL_ORDER` in `FREEZE_V1.md` and
`MANIFEST_V1.json`.

**Strongest parents.** None registered beyond the transducer theory of Mealy (1955) and Moore
(1956) and the organization set of `gmi-833-aj4-process-organizations-v1`
(`PARENT_LEDGER.md`); the ladder itself is quoted from the issue and is not this tranche's
proposal.

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

**Assumptions.** Each transition's declared description encoding: the eight transition-table
bits of a one-cell system for `I1` and `I2`, sixteen bits for a series pair (`I3`) and for the
adaptive witness's two update tables (`I4`), and one- or two-bit feature switches for `I5` …
`I8`. Edit distance is Hamming distance in that encoding, searched exhaustively by increasing
radius from a registered passing seed (`nearest_negative` in `ah4_organization_ladder_v1.py`);
the distances are properties of these encodings, not of the transitions in any encoding-free
sense.

**Dependencies.** The eight invariants of AH4L-1 as the pass/fail predicates; the gate of
`FREEZE_V1.md` section 4 requiring a minimum edit distance wherever one exists;
`nearest_negatives` in `RESULT_V1.json`, with the flipped positions and resulting
descriptions; the hostile `nearest_negative_zero_radius` in `TEST_RESULT_V1.json`.

**Strongest parents.** None registered for the nearest-negative construction itself, which
`PARENT_LEDGER.md` lists as residual contribution; it rests on the transducer theory of Mealy
(1955) and Moore (1956) and on the organization set of `gmi-833-aj4-process-organizations-v1`.

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

**Assumptions.** Level is assigned from the base invariants only (level 2 when both `I2`
clauses hold, level 1 when only `I1` holds, otherwise 0); capability is the exact rational
score vector on the five registered tasks `IDENTITY`, `NEGATION`, `CONST0`, `DELAY1`, `PARITY`
over the 14 protected words of length at most three, compared by componentwise domination with
no scalarization.

**Dependencies.** The `I1` and `I2` predicates of AH4L-1; the prohibition falsifier of
`FREEZE_V1.md` section 5; `level_capability_inversions`, `level_capability_inversion_example`
and `prohibition` in `RESULT_V1.json`, with the inversion count matched by route B; the
hostiles `prohibition_always_refuses`, `prohibition_never_refuses` and
`level_capability_monotone` in `TEST_RESULT_V1.json`.

**Strongest parents.** None registered for the prohibition checker, which `PARENT_LEDGER.md`
lists as residual contribution; the capability comparison rests on the transducer theory of
Mealy (1955) and on the organization set of `gmi-833-aj4-process-organizations-v1`.
