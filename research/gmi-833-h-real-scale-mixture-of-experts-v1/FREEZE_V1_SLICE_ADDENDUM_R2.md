# Slice addendum R2 — regeneration, the registered nulls, the unexcited-context control, the matched-presentation control and the boundary datum

`source_main`: `3cbf841c`.
Governs: `FREEZE_V1.md`, `FREEZE_V1_SLICE_ADDENDUM.md` (both committed before
this addendum).

This addendum is committed **before any executor, test, data extraction, fit or
result artifact exists**, and CI asserts the ordering. It registers the
seeded constructions and the control's exact form in reproducible terms so they
cannot be read after the outcome.

## R2.1 The symmetric half-split regeneration (R09)

The fit slice is split symmetrically, registered from the start rather than
chosen after a first result:

```
fit_lo = the first  n_fit // 2 = 339,562 positions of the presentation order
fit_hi = the remaining 339,562 positions
```

The regeneration is evaluated in BOTH directions and the winner rule must
recover the SAME structural class and the SAME arm in both:

```
primary : store = fit_lo, score = fit_hi
regen   : store = fit_hi, score = fit_lo
```

A registration that recovers its class in one direction only does not satisfy
`R09` at this scope.

## R2.2 The registered null constructions

Two nulls are registered, both seeded, both exact, both evaluated after the
frozen-prediction record of `FREEZE_V1.md` section 8 is written.

**The label-shuffle null.** Seed `random.Random(20260926)`. On the held slice,
take the 97,018 full-source labels in presentation order and shuffle them with
that generator; score the winner's frozen predictions against the shuffled
labels. The null must make STRICTLY MORE errors than the fit-majority rule's,
or `F2` fires. The shuffled label vector is committed in the receipt so the
count is replayable.

**The global design null.** Seed `random.Random(20260927)`. The null destroys
the ROUTING CONTEXT globally rather than one expert: every query's stored
evidence is replaced by the evidence of a position drawn uniformly at random
from the store — the same draw for every arm, so the store size, the expert
partition, the length structure and the query set are all untouched, and the
only thing destroyed is the correspondence between a query and its stored
evidence. `F3` requires the null to exceed THREE TIMES the winning arm's held
error count; the null's predictions and its per-arm error counts are committed,
and the assert is that every arm that does not read stored evidence (the
constants and the length arms) keeps its UNCORRUPTED error count, which is what
proves the corruption moved exactly what it claims to move.

## R2.3 The fallback-branch reachability, measured

The registered decision function of `MEM_FALLBACK` (slice addendum section 3)
takes its fallback branch exactly on the queries the store does not contain.
Measured on the frozen constructions, that count is **46,697 / 17,150 / 95,100
/ 94,246** at rank / held / primary / regen. The executor asserts, per stage,
that this count is strictly positive, so the branch is load-bearing rather than
decorative; and it asserts the arm's stored branch is the store's routed
predicate `spred(q)`, so the arm's description and its decision function agree.

## R2.4 The unexcited-context control, exactly

Registered in two forms. The PRIMARY form is `B'`:

```
context : r(q)  ->  r0(q) = 0                 (the single moving coordinate)
label   : y(q) = 1 iff f_{r(q)}(q) >= 1       (HELD FIXED at y)
store, expert partition, slices, query sets, language, winner rule: unchanged
```

The `B'` requirement is a three-part assertion, evaluated at every stage:

1. **every routing-free arm is decision-identical across the two arenas** — the
   fixed-expert family and the union family, per arm, per query, zero decision
   mismatches;
2. **every router-selected arm collapses onto its matched fixed-expert
   counterpart** — `SEL_CNT>=t` against `E0_CNT>=t` for `t = 1,2,3`, and
   `SEL_FAN>=t` against `E0_FAN>=t` for `t = 1,2` — with zero decision
   mismatches and therefore equal error counts;
3. **the routed advantage vanishes**: the winner's margin over the best
   routing-free arm, strictly positive in the excited arena, is exactly zero in
   the unexcited arena.

The SECONDARY reading (`arena B`) additionally replaces the label with
`y0(q) = 1 iff f0(q) >= 1`. It is registered, measured and committed, and it is
labelled as a secondary reading because it moves the label as well as the
context: the two labels disagree on **306,000 of the 776,142** descriptor
positions (`FREEZE_V1_SLICE_ADDENDUM.md` section 8), so `arena B` cannot
simultaneously assert the routing-free identity of (1) as a statement about
context alone. **The first specification of this control was internally
inconsistent and is recorded here as a correction, not silently replaced:** it
redefined the label while demanding the routing-free identity, and those two
requirements cannot both hold because the label is itself a function of the
context. `B'` is registered as the primary form for that reason, and the
correction is stated so the change is visible as a specification fix rather
than as a choice made after seeing which version passed.

## R2.5 The matched-presentation control (the source-order arena)

Under the identical ecology, expert partition, readout language, winner rule
and arithmetic slices, but reading the descriptor list in SOURCE ORDER instead
of under the registered Knuth permutation, the registered `F1` margin must NOT
be cleared by the winner of that arena: the winning arm's error count must
exceed half the arena's fit-majority rule. The control fires when the
registered presentation lever is load-bearing; the arena's winner, its majority
rule, the constant arms and the routed arm's error count are all committed so
the firing is replayable. The exact registered numeric forms are written in
this addendum's table below, before the executor.

| quantity, source-order arena | registered form |
|---|---|
| score set | the last `n_held = 97,018` positions of source order |
| the arena's fit-majority rule | computed from the store's own positions |
| `F1` half-margin | `majority_errors // 2` |
| control fires | the arena's winner's errors **>** that half-margin |

## R2.6 The exact-inference comparison readout (boundary datum, outside the language)

Registered as a comparison scored for information only, outside the readout
language `R`, which stays closed at 37 arms: **`ECM_ALL_EXPERTS_PRODUCT`**, the
product-form marginalisation over ALL experts,

```
( scnt_0(q)+1 ) * ( scnt_1(q)+1 ) * ( scnt_2(q)+1 ) * ( scnt_3(q)+1 ) > 1
```

which is exact inference over the model's full joint rather than under the hard
router. It is registered here so that the receipt can carry the comparison
between the family-blind winner and BOTH exact semantics: the model's full-joint
marginalisation (this datum, a product form, outside `R`) and the routed
readout under the registered hard router (which is `SEL_FAN>=1`, inside `R`).
The datum drives no winner, no gate and no certificate, and no error count for
it is registered here: it is measured, committed and reported, and its value is
whatever the run produces.

## R2.7 The charged-cost tie-break, and the alias rule's application

Where two arms tie on error count the winner rule proceeds to charged cost and
then to readout name. Under `FREEZE_V1.md` section 5 Rule 1, two committed arms
whose decision functions are identical at every registered stage and every query
are ONE readout registered under two names; the second name is recorded as an
alias and is not a competitor for either the winner or the runner-up slot. The
receipt therefore carries, per stage: the **alias sets**, the **min-error set**
with each member's charged cost, whether the stage is a cost-decided tie, and
the **runner-up with aliases removed**, so that the best genuinely distinct
competitor to the winner has an answer on the record rather than being a second
name for the winner's own predicate.
