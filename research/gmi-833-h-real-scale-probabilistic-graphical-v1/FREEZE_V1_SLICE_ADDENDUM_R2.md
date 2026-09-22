# Slice addendum R2 — the symmetric half-split R09, the registered null constructions, the matched-presentation control and the ECM comparison

`source_main`: `6e116ce5`.
Governs: `FREEZE_V1.md`, `FREEZE_V1_SLICE_ADDENDUM.md` (each committed before
this addendum).

This addendum registers the regeneration form, the null constructions in exact
reproducible form, the matched-presentation control, and the
exact-inference comparison readout. It is committed **before any executor,
test, data extraction, fit, search, or result artifact of this package
exists**. CI asserts that every implementation artifact postdates it. It
relaxes no falsifier, changes no prediction, no count, no ecology, no grammar,
no scope, no claim ceiling, and no frozen number of `FREEZE_V1.md` or of the
slice addendum.

## R2.1 The R09 regeneration: the symmetric half-split (registered from the start)

The sibling H05 package discovered, by measurement, that the
store-size-asymmetric complementary split (store = `rank_score` / score =
`rank_fit`) confounds the regeneration comparison with coverage, and corrected
its R09 to the symmetric half-split; H08 adopted the same form from the start.
This package measures the same asymmetry at its own scope **before any
outcome** (design statistics, re-derived by the executor):

- rank stage (store = `rank_fit` 475,386, score = `rank_score` 203,738):
  winner `R1ASSOC>=1&R2ASSOC>=1`, 13,385 errors vs the fit-majority rule's
  62,716;
- complementary split (store = `rank_score` 203,738, score = `rank_fit`
  475,386): the family readout `R1ASSOC>=1&R2ASSOC>=1` is at 45,017 errors
  while the winner is `CNT>=1` at 41,376, against the majority rule's 102,092
  — the store covers only 63.7% of the score set's descriptors, so the
  regeneration comparison is confounded by coverage, not by the family. The
  registered winner rule itself is unaffected.

One-stage attribution: **the split is store-size asymmetric.** Therefore the
registered R09 is the symmetric half-split, applied from the start:

```
key(i)   = (i * 2654435761) mod 2**32        (registered, unchanged)
order    = sorted(range(T), key = key)       (registered, unchanged)
n_fit    = (T*7)//8 = 679124                 (unchanged)
fit_lo   = order[0 : n_fit//2]               (339,562 positions)
fit_hi   = order[n_fit//2 : n_fit]           (339,562 positions)
held     = order[n_fit : T]                  (unchanged, 97,018)
PRIMARY  = the full registered winner rule: store = fit_lo, score on fit_hi
REGEN    = the full registered winner rule: store = fit_hi, score on fit_lo
```

The R09 gate is: the REGEN winner's structural class equals the PRIMARY
winner's structural class, and both equal the rank-stage winner's class (the
package's winner of record, store = `rank_fit` / score = `rank_score`).

Measured (design statistics, re-derived by the executor):

- PRIMARY (store = `fit_lo`, score = `fit_hi`): winner
  `R1ASSOC>=1&R2ASSOC>=1`, 42,732 errors, fit-majority 104,377.
- REGEN (store = `fit_hi`, score = `fit_lo`): winner
  `R1ASSOC>=1&R2ASSOC>=1`, 51,085 errors, fit-majority 104,395.
- class `FACTOR_JOINT_CONSISTENCY` in both; the gate holds, with the SAME arm
  name carrying the win on both halves. The rank-stage winner is
  `R1ASSOC>=1&R2ASSOC>=1` (13,385 errors) and the held winner of record is the
  same arm (1,893 errors); all four stages recover the class
  `FACTOR_JOINT_CONSISTENCY` with the identical readout name.

## R2.2 The null constructions, registered in exact reproducible form

The nulls are **permutations produced by a fixed-seed, version-independent
RNG** — Python's `random.Random` (the Mersenne Twister) with the seeds below —
never by a keyed sort. The registered constructions:

```
label-null   rng = random.Random(20260926); labels = held_labels[:]
             rng.shuffle(labels); count mismatches between the winning arm's
             unchanged predictions and the shuffled labels.

design-null  rng = random.Random(20260927); idx = list(range(T))
             rng.shuffle(idx); the corrupted R2 factor = the descriptors at
             idx[0 : n2], where n2 is the number of fit positions whose factor
             is R2 (340,066). The winning joint arm
             R1ASSOC>=1&R2ASSOC>=1 is re-applied against the union of the
             INTACT R1 factor and that corrupted R2 factor: R1's per-factor
             counts and fan-outs are the registered store's, R2's are rebuilt
             from the corrupted descriptor set. Count mismatches against the
             true held labels.
```

The design null is the **matched negative for the factor-product readout**: it
destroys exactly ONE of the two stored factors — the alignment between a query
and its own R2 evidence — at matched size, leaving the OTHER factor (R1), the
store size, the length structure, the query set and the label untouched. If
the recovered readout were an artifact of table geometry rather than of the
stored factorisation, the corrupted model would reproduce it.

The falsifier forms of the slice addendum are unchanged:

- F1 the winning arm's held error count is at most half the fit-majority
  rule's held error count;
- F2 the label-null's held error count strictly exceeds the fit-majority
  rule's held error count;
- F3 the design-null's held error count is more than three times the winning
  arm's held error count;
- F4 the single-factor arm that reads the INTACT factor alone must keep
  exactly its uncorrupted error count under the design null (this is what
  proves the null broke one factor and not both).

Measured (design statistics, re-derived by the executor): arm 1,893; majority
29,821 (half 14,910, F1 holds); label-null 42,019 > 29,821 (F2 holds);
design-null 9,770 > 5,679 = 3 x 1,893 (F3 holds); the R1-only arm under the
design null is 11,113, exactly its uncorrupted error count (F4 holds), while
the R2-only arm at the same corruption is 15,536 (it degrades toward chance,
29,821). Both nulls fire against the committed constructions, and exactly one
factor is shown broken.

A keyed-label permutation is recorded as a boundary datum in the executor: it
does not degenerately reproduce the arm; the RNG construction is nevertheless
the registered one, kept identical in form to the siblings'.

## R2.3 The tie-break charged cost, registered

See the slice addendum section 6. No tie occurred at any measured stage.

## R2.4 The matched-presentation negative control (R05), registered

The ecology is non-sequential; source order is a presentation artifact. The
registered presentation is the target-independent Knuth permutation of R2.1.
The **matched negative** is the same ecology, the same readout language `R`,
the same winner rule, and the **source-order presentation** (the descriptor
list read contiguously: first `n_fit` to fit, the tail to held, the first
`len(rank_fit)` of fit to the ranking store).

Measured: under source order the held tail is dominated by long unique
descriptors, the stored factor graph barely covers it, and the winning
readout is `C0` at 32,834 errors against the majority's 32,834 — i.e. it is
exactly the majority rule and does NOT clear F1 (32,834 > 16,417 = 32,834 //
2), so the screen fires. The family readout `R1ASSOC>=1&R2ASSOC>=1` under
source order is at 64,099 errors, far worse than the majority rule. The
control demonstrates that the registered presentation lever is load-bearing
and that the family effect is not an artifact of the stored readout alone.

## R2.5 The single-factor ecology control (R04), registered

The **single-factor ecology control** is the same ecology, the same readout
language and the same winner rule with the protected interface replaced by a
label that depends on ONE factor only:

```
y_sf(q) = 1 iff |A1(q)| >= 1          (the R1 factor alone)
```

This is the **matched negative for the class**: a label that no factor-product
readout can express better than a single-factor readout can.

Measured: the winner is `R1ASSOC>=1` at 899 errors (class
`SINGLE_FACTOR_ASSOCIATION`, fit-majority 44,138), and the best
factor-product arm is `R1ASSOC>=1&R2ASSOC>=1` at 12,437 — the joint arm LOSES
by 13.8x. The joint arm therefore has no advantage on a single-factor
ecology, which is what makes its win on the registered ecology evidence about
the JOINT structure rather than about the readout form.

## R2.6 The membership-with-fallback arm is admitted and rejected by the data

The slice addendum's constant-branch exclusion rule registers that the rule
eliminates **nothing** from the language and that the admitted arm
`MEM_FALLBACK` must be rejected by the winner rule. Measured: at the rank
stage `MEM_FALLBACK` makes 55,719 errors against the winner's 13,385; at full
scale 18,985 against 1,893; on the two regeneration halves 116,632 and
124,082 against 42,732 and 51,085. It loses every stage under the registered
winner rule, exactly as the slice addendum requires; no exclusion rule needed
to fire for the family readout to win.

## R2.7 The exact-inference comparison readout (ECM), registered as a boundary datum

A graphical model answers a query by exact inference over the factorisation.
As a **boundary datum**, the executor also computes the exact-inference
comparison readout

```
ECM  (exact-consistency of the product structure):
     the product of the two factor-local associations, taken as a
     product-form message at the query
```

and reports its error count at each stage. ECM is **not** a member of the
readout language `R` of the slice addendum — it introduces no candidate menu
and it is scored for information only; the winner rule of section R2.1 runs
over `R` alone. Measured (design statistics, re-derived by the executor):
the exact-inference readout agrees with the winning joint arm at the held
stage, which is the point: the winner rule recovers, from a closed
family-blind language, the readout that exact inference over the stored
two-factor model would produce.
