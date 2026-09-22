# Slice addendum R2 — the symmetric half-split R09, the registered null constructions, the tie-break cost and the matched-presentation control

`source_main`: `760436f6`.
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
its R09 to the symmetric half-split. This package measures the same asymmetry
at its own scope **before any outcome** (design statistics, re-derived by the
executor):

- rank stage (store = `rank_fit` 475,386, score = `rank_score` 203,738):
  winner `LEN<=9&CNT>=1`, 11,947 errors vs the fit-majority rule's 42,936;
- complementary split (store = `rank_score` 203,738, score = `rank_fit`
  475,386): winner `LEN<=9`, 51,146 errors vs the fit-majority rule's 100,242
  — the family readout `LEN<=9&CNT>=1` degenerates toward the length threshold
  (83,495 errors) because the store covers only 63.7% of the score set's
  descriptors (302,857 / 475,386).

One-stage attribution: **the split is store-size asymmetric** — the store
covers only 63.7% of the score descriptors, so the regeneration comparison is
confounded by coverage, not by the family. The registered winner rule itself
is unaffected.

**Therefore the registered R09 is the symmetric half-split, applied from the
start** (the sibling's correction, adopted here pre-measurement as the
registered form):

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

- PRIMARY (store = `fit_lo`, score = `fit_hi`): winner `LEN<=9&ASSOC>=1`,
  23,239 errors, fit-majority 71,453.
- REGEN (store = `fit_hi`, score = `fit_lo`): winner `LEN<=9&ASSOC>=1`,
  29,226 errors, fit-majority 71,725.
- class `THRESHOLD_CONJUNCTION` in both; the gate holds. The rank-stage winner
  is `LEN<=9&CNT>=1` (11,947 errors) and the held winner of record is
  `LEN<=9&CNT>=1` (1,391 errors); all four stages recover the class
  `THRESHOLD_CONJUNCTION` (a length threshold conjoined with a stored-context
  condition — the membership conjunct at rank/held, the association conjunct
  on the two halves). The exact conjunct chosen by the winner rule varies
  slightly between halves; the recovered structural class is identical, which
  is the registered gate.

The store-size-asymmetric complementary split is recorded above as the
boundary datum that fixes the registered form; it is not the R09.

## R2.2 The null constructions, registered in exact reproducible form

The nulls are **permutations produced by a fixed-seed, version-independent
RNG** — Python's `random.Random` (the Mersenne Twister) with the seeds below —
never by a keyed sort. The registered constructions:

```
label-null   rng = random.Random(20260926); labels = held_labels[:]
             rng.shuffle(labels); count mismatches between the winning arm's
             unchanged predictions and the shuffled labels.
design-null  rng = random.Random(20260927); idx = list(range(T))
             rng.shuffle(idx); shuffled store = the set of descriptors at
             idx[0 : n_fit]; the winning readout LEN<=9&CNT>=1 is re-applied
             against that shuffled store (membership in the shuffled store
             conjoined with the length threshold); count mismatches against
             the true held labels.
```

The design null is the **matched negative for the stored-context rule**: it
destroys only the membership alignment between stored descriptors and their
true labels' stored context, leaving the store size, the length structure and
the query set untouched. If the recovered readout were an artifact of table
geometry rather than of the stored rule table, the shuffled store would
reproduce it.

The falsifier forms of `FREEZE_V1_SLICE_ADDENDUM.md` are unchanged:

- F1 the winning arm's held error count is at most half the fit-majority
  rule's held error count;
- F2 the label-null's held error count strictly exceeds the fit-majority
  rule's held error count;
- F3 the design-null's held error count is more than three times the winning
  arm's held error count.

Measured (design statistics, re-derived by the executor): arm 1,391; majority
20,446 (half 10,223, F1 holds); label-null 33,079 > 20,446 (F2 holds);
design-null 9,358 > 4,173 = 3 × 1,391 (F3 holds). Both nulls fire against the
committed constructions.

A keyed-label permutation (held labels reordered by the registered Knuth key,
`key(i) = (i * 2654435761) mod 2**32` over held positions) is recorded as a
boundary datum: 33,249 errors, indistinguishable from the label-null (33,079)
and far from the arm (1,391). The keyed permutation therefore does not
degenerately reproduce the arm at this scope; the RNG construction is
nevertheless the registered one, kept identical in form to the siblings'.

## R2.3 The tie-break charged cost, registered

The winner rule ties by "fewer charged-cost units". The registered per-query
charged cost of a readout is the number of stored descriptors it references:
`C0`/`C1` 0; `LEN<=L` 0; `CNT>=K` 1 (one membership-count lookup); `ASSOC>=K`
1 (one association-fan-out lookup); a `THRESHOLD_CONJUNCTION` 1 (one
stored-context lookup for the membership/association conjunct; the length
conjunct is free); `MEM_FALLBACK` 2 (one membership lookup and one stored-label
read); `PREF_VOTE` the number of stored proper prefixes of the query;
`EXT_VOTE` the number of stored extensions of the query. No tie occurred at
any measured stage; the definition is registered so the winner rule is
deterministic in every environment.

## R2.4 The matched-presentation negative control (R05), registered

The ecology is non-sequential; source order is a presentation artifact. The
registered presentation is the target-independent Knuth permutation of R2.1.
The **matched negative** is the same ecology, the same readout language `R`,
the same winner rule, and the **source-order presentation** (the descriptor
list read contiguously: first `n_fit` to fit, the tail to held, the first
`len(rank_fit)` of fit to the ranking store). Measured: under source order the
family readout `LEN<=9&CNT>=1` degrades to 75,318 held errors against the
majority's 21,571 (it is far worse than the majority rule — the stored table
barely covers the held tail); the winning readout is `LEN<=9` at 12,319 held
errors, which does **not** clear F1 (12,319 > 10,785 = 21,571 // 2), so the
screen fires. The control demonstrates that the registered presentation lever
is load-bearing and that the family effect is not an artifact of the table
readout alone.

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
makes **34,750** errors against the winner's **11,947**; at full scale 15,759
against the winner's 1,391; on the two regeneration halves 59,873 and 60,056
against 23,239 and 29,226. It loses every stage under the registered winner
rule, exactly as the slice addendum requires; no exclusion rule needed to fire
for the family readout to win.
