# Slice addendum R2 — the corrected R09, the registered null constructions and the matched-presentation control

`source_main`: `e4fee27337d898a4483639365590ccebce1b1be6`.
Governs: `FREEZE_V1.md`, `FREEZE_V1_ARITHMETIC_ADDENDUM.md`,
`FREEZE_V1_SLICE_ADDENDUM.md` (committed `b8aff012`).

This addendum corrects one registered form of `FREEZE_V1_SLICE_ADDENDUM.md`
(the R09 regeneration), registers the null constructions in exact reproducible
form, registers the tie-break charged cost, and registers the matched-
presentation negative control. It is committed **before any executor, test,
data extraction, fit, search, or result artifact of this package exists**. CI
asserts that every implementation artifact postdates it. It relaxes no
falsifier, changes no prediction, no count, no ecology, no grammar, no scope,
no claim ceiling, and no frozen number of `FREEZE_V1.md` or of the slice
addendum.

## R2.1 The R09 regeneration: corrected to the symmetric half-split

`FREEZE_V1_SLICE_ADDENDUM.md` section 3 registered the regeneration as the
complementary split store = `rank_score` / score = `rank_fit`. Measured
**before any outcome existed** (a design measurement, not a fit), that split
fails:

- primary rank stage (store = `rank_fit` 475,386, score = `rank_score`
  203,738): winner `CNT>=1` at 13,810 errors vs the fit-majority rule's
  32,887;
- complementary split (store = `rank_score` 203,738, score = `rank_fit`
  475,386): winner `LEN<=10` at 72,829 errors vs the fit-majority rule's
  76,763 — the family readout `CNT>=1` degenerates toward `C0` because the
  store covers ~26% of the score set's descriptors.

One-stage attribution: **the split is store-size asymmetric** — the store
covers only ~26% of the score descriptors, so the regeneration comparison is
confounded by coverage, not by the family. The registered selection rule
itself is unaffected.

The corrected R09, registered here and used from now on:

```
key(i)   = (i * 2654435761) mod 2**32        (registered, unchanged)
order    = sorted(range(T), key = key)       (registered, unchanged)
n_fit    = (T*7)//8 = 679124                 (unchanged)
fit_lo   = order[0 : n_fit//2]               (339,562 positions)
fit_hi   = order[n_fit//2 : n_fit]           (339,562 positions)
held     = order[n_fit : T]                  (unchanged, 97,018)
PRIMARY  = the full registered selection: store = fit_lo, score on fit_hi
REGEN    = the full registered selection: store = fit_hi, score on fit_lo
```

The R09 gate is: the REGEN winner's structural class equals the PRIMARY
winner's structural class, and both equal the rank-stage winner's class (the
package's selection of record, store = `rank_fit` / score = `rank_score`). The
asymmetric complementary split and its measured failure are recorded here as
the boundary of the store-size-asymmetry attribution, exactly as the parents
record a failed prediction with its attribution before the corrected run.

Measured (design statistics, re-derived by the executor):

- PRIMARY (store = `fit_lo`, score = `fit_hi`): winner `CNT>=1`, 40,386
  errors, fit-majority 54,714.
- REGEN (store = `fit_hi`, score = `fit_lo`): winner `CNT>=1`, 39,310 errors,
  fit-majority 54,936.
- class `STORED_EXEMPLAR_MEMBERSHIP` in both; the gate holds.

## R2.2 The null constructions, registered in exact reproducible form

The nulls are **permutations of labels or of stored positions produced by a
fixed-seed, version-independent RNG** — Python's `random.Random` (the
Mersenne Twister) with the seeds below — never by a keyed sort: a keyed sort
of held positions or labels is itself a function of the descriptor-index
multiset and achieves a degenerate alignment with the labels (measured: a
keyed label permutation reproduces the arm's own 1,535 errors, so the label
null fails its falsifier). The registered constructions:

```
label-null   rng = random.Random(20260921); labels = held_labels[:]
             rng.shuffle(labels); count mismatches between the selected arm's
             unchanged predictions and the shuffled labels.
design-null  rng = random.Random(20260922); idx = list(range(T))
             rng.shuffle(idx); shuffled store = the set of descriptors at
             idx[0 : n_fit]; the selected readout is re-applied against that
             store with its registered fallback; count mismatches against the
             true held labels.
```

The falsifier forms of `FREEZE_V1_SLICE_ADDENDUM.md` are unchanged:

- F1 the selected arm's held error count is at most half the fit-majority
  rule's held error count;
- F2 the label-null's held error count strictly exceeds the fit-majority
  rule's held error count;
- F3 the design-null's held error count is more than three times the selected
  arm's held error count.

Measured (design statistics, re-derived by the executor): arm 1,535; majority
15,615 (half 7,807, F1 holds); label-null 27,203 > 15,615 (F2 holds);
design-null 13,854 > 4,605 (F3 holds). The design-null beating the majority
rule is the registered and expected weakness of any fixed ~7/8 subset (weak
frequency correlation); the 3x margin over the arm is what separates the
family from it.

## R2.3 The tie-break charged cost, registered

The selection rule ties by "fewer charged-cost units". The registered
per-query charged cost of a readout is the number of stored descriptors it
references: `C0`/`C1` 0; `LEN<=L` 0; `CNT>=K` 1 (one vocabulary-index lookup);
`PREF_VOTE` the number of stored proper prefixes of the query; `EXT_VOTE` the
number of stored extensions of the query. No tie occurred at any measured
stage; the definition is registered so the selection is deterministic in every
environment.

## R2.4 The matched-presentation negative control (R05), registered

The ecology is non-sequential; source order is a presentation artifact. The
registered presentation is the target-independent Knuth permutation of R2.1.
The **matched negative** is the same ecology, the same readout language `R`,
the same selection procedure, and the **source-order presentation** (the
descriptor list read contiguously: first `n_fit` to fit, the tail to held,
the first `len(rank_fit)` of fit to the ranking store). Measured: under
source order the held tail is dominated by long unique descriptors, the
stored table barely covers it, and the family readout `CNT>=1` degrades to
79,435 held errors against the majority's 17,454 (it does not beat the
majority rule at all); the selected arm is `LEN<=10` at 16,406 held errors,
which does **not** clear F1 (16,406 > 8,727), so the screen fires. The control
demonstrates that the registered presentation lever is load-bearing and that
the family effect is not an artifact of the table readout alone.

## R2.5 Consequences that are registered here

- `n_fit`, `n_held`, `rank_fit`, `rank_score`, the Knuth key, the readout
  language `R`, the selection procedure, the charged-cost model and every
  falsifier form are unchanged.
- The corrected R09 (R2.1), the null constructions (R2.2), the tie-break cost
  (R2.3) and the presentation control (R2.4) are the registered forms the
  executor implements and route B re-derives independently from this text
  alone.
