# Slice addendum R2 — the symmetric half-split R09, the registered null constructions, the tie-break cost and the matched-presentation control

`source_main`: `8e5dcf99`.
Governs: `FREEZE_V1.md`, `FREEZE_V1_SLICE_ADDENDUM.md` (each committed before
this addendum).

This addendum registers the regeneration form, the null constructions in exact
reproducible form, the tie-break charged cost, and the matched-presentation
negative control. It is committed **before any executor, test, data
extraction, fit, search, or result artifact of this package exists**. CI
asserts that every implementation artifact postdates it. It relaxes no
falsifier, changes no prediction, no count, no ecology, no grammar, no scope,
no claim ceiling, and no frozen number of `FREEZE_V1.md` or of the slice
addendum.

## R2.1 The R09 regeneration: the symmetric half-split (registered from the start)

The sibling H05 package discovered, by measurement, that the
store-size-asymmetric complementary split (store = `rank_score` / score =
`rank_fit`) confounds the regeneration comparison with coverage, and corrected
its R09 to the symmetric half-split. This package **applies that correction
from the start**: the registered regeneration is the symmetric half-split of
the fit.

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

- PRIMARY (store = `fit_lo`, score = `fit_hi`): winner `ASSOC>=2`, 25,907
  errors, fit-majority 152,818.
- REGEN (store = `fit_hi`, score = `fit_lo`): winner `ASSOC>=2`, 31,249
  errors, fit-majority 152,848.
- class `CUE_ASSOCIATION_FANOUT` in both; the gate holds.

The store-size-asymmetric complementary split (store = `rank_score` 203,738,
score = `rank_fit` 475,386) is measured for the boundary record and **also**
recovers `ASSOC>=2` (69,329 errors vs the fit-majority rule's 213,847; store
coverage of the score set 0.343). The family readout is stable under the
coverage asymmetry here — a robustness datum, not the registered form. The
symmetric half-split is the registered R09.

## R2.2 The null constructions, registered in exact reproducible form

The nulls are **permutations produced by a fixed-seed, version-independent
RNG** — Python's `random.Random` (the Mersenne Twister) with the seeds below —
never by a keyed sort: a keyed sort of held positions or labels is itself a
function of the descriptor-index multiset and achieves a degenerate alignment
with the labels. The registered constructions:

```
label-null   rng = random.Random(20260923); labels = held_labels[:]
             rng.shuffle(labels); count mismatches between the winning arm's
             unchanged predictions and the shuffled labels.
design-null  rng = random.Random(20260924)
             cues   = the fit descriptors q with len(q) >= 3, in fit order
             elems  = the final letter of each such descriptor, in fit order
             rng.shuffle(elems); shuffled store = for each (cue, elem) pair,
             A(cue) gains elem; the winning readout is re-applied against that
             shuffled association table with its registered fallback; count
             mismatches against the true held labels.
```

The design null is the **matched negative for content-at-the-cue**: it destroys
only the content-to-content adjacency between a cue and the letters stored
after it, leaving the store size, the cue set and the query set untouched. If
the recovered readout were an artifact of table geometry rather than of the
stored associations, the shuffled table would reproduce it.

The falsifier forms of `FREEZE_V1_SLICE_ADDENDUM.md` are unchanged:

- F1 the winning arm's held error count is at most half the fit-majority
  rule's held error count;
- F2 the label-null's held error count strictly exceeds the fit-majority
  rule's held error count;
- F3 the design-null's held error count is more than three times the winning
  arm's held error count.

Measured (design statistics, re-derived by the executor): arm 1,249; majority
43,775 (half 21,887, F1 holds); label-null 48,065 > 43,775 (F2 holds);
design-null 23,969 > 3,747 (F3 holds). Both nulls fire against the committed
constructions.

A third permutation, the position-shuffle (a shuffled-position store of the
sibling H05 form, `random.Random(20260925)`), gives 1,592 held errors against
the arm's 1,249 — inside the 3x falsifier margin (1,592 < 3,747), so it is
**not** a registered null for this ecology: a random ~7/8 subset of the
descriptor list still carries weak cue-coverage signal, which is exactly why
the registered design null destroys the content-to-content adjacency rather
than the positions. It is recorded here as the boundary datum that fixes the
registered construction.

## R2.3 The tie-break charged cost, registered

The winner rule ties by "fewer charged-cost units". The registered per-query
charged cost of a readout is the number of stored descriptors it references:
`C0`/`C1` 0; `LEN<=L` 0; `ASSOC>=K` 1 (one association-fan-out lookup at the
cue); `MEM_FALLBACK` 2 (one membership lookup and one fan-out lookup);
`PREF_VOTE` the number of stored proper prefixes of the query; `EXT_VOTE` the
number of stored extensions of the query. No tie occurred at any measured
stage; the definition is registered so the winner rule is deterministic in
every environment.

## R2.4 The matched-presentation negative control (R05), registered

The ecology is non-sequential; source order is a presentation artifact. The
registered presentation is the target-independent Knuth permutation of R2.1.
The **matched negative** is the same ecology, the same readout language `R`,
the same winner rule, and the **source-order presentation** (the descriptor
list read contiguously: first `n_fit` to fit, the tail to held, the first
`len(rank_fit)` of fit to the ranking store). Measured: under source order the
held tail is dominated by long single-element descriptors, the stored table
barely covers it, and the family readout `ASSOC>=2` degrades to 51,702 held
errors against the majority's 45,231 (it does not beat the majority rule); the
winning readout is `LEN<=7` at 31,584 held errors, which does **not** clear F1
(31,584 > 22,615 = 45,231 // 2), so the screen fires. The control demonstrates
that the registered presentation lever is load-bearing and that the family
effect is not an artifact of the table readout alone.

## R2.5 Consequences that are registered here

- `n_fit`, `n_held`, `rank_fit`, `rank_score`, the Knuth key, the readout
  language `R`, the winner rule, the charged-cost model and every falsifier
  form are unchanged.
- The symmetric half-split R09 (R2.1), the null constructions (R2.2), the
  tie-break cost (R2.3) and the presentation control (R2.4) are the registered
  forms the executor implements and route B re-derives independently from this
  text alone.

## R2.6 The membership-with-fallback arm is admitted and rejected by the data

The slice addendum's constant-branch exclusion rule registers that the rule
eliminates **nothing** from the language and that the admitted arm
`MEM_FALLBACK` must be rejected by the winner rule. Measured (design
statistics, re-derived by the executor): at the rank stage `MEM_FALLBACK`
makes **53,183** errors against the winner's **8,600**; at full scale 18,331
against the winner's 1,249; on the two regeneration halves 109,174 and
112,930 against 25,907 and 31,249. It loses every stage under the registered
winner rule, exactly as the slice addendum requires; no exclusion rule needed
to fire for the family readout to win.
