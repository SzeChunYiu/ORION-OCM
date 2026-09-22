# Slice addendum R2 — the symmetric half-split R09, the registered null constructions, the tie-break cost, the matched-presentation control and the single-particle-store control

`source_main`: `6e116ce5`.
Governs: `FREEZE_V1.md`, `FREEZE_V1_SLICE_ADDENDUM.md` (each committed before
this addendum).

This addendum registers the regeneration form, the null constructions in exact
reproducible form, the tie-break charged cost, the matched-presentation negative
control and the single-particle-store negative control. It is committed
**before any executor, test, data extraction, fit, search, or result artifact of
this package exists**. CI asserts that every implementation artifact postdates
it. It relaxes no falsifier, changes no prediction, no count, no ecology, no
grammar, no scope, no claim ceiling, and no frozen number of `FREEZE_V1.md` or
of the slice addendum. Every number quoted below is a design statistic the
executor re-derives; route B re-derives it independently from this text alone.

## R2.1 The R09 regeneration: the symmetric half-split (registered from the start)

The sibling `gmi-833-h-real-scale-nearest-neighbor-v1` discovered, by
measurement, that the store-size-asymmetric complementary split (store =
`rank_score` / score = `rank_fit`) confounds the regeneration comparison with
coverage, and corrected its R09 to the symmetric half-split. This package
measures the same asymmetry at its own scope **before any outcome** (design
statistics, re-derived by the executor):

- rank stage (store = `rank_fit` 475,386, score = `rank_score` 203,738):
  winner `PLUR`, 5,366 errors vs the fit-majority rule's 42,073;
- complementary split (store = `rank_score` 203,738, score = `rank_fit`
  475,386): winner `PLUR`, 46,478 errors vs the fit-majority rule's 98,557 —
  the plurality arm's error rate rises from 5,366/111,908 = 0.048 to
  46,478/261,501 = 0.178.

One-stage attribution: **the split is store-size asymmetric** — the store
covers 89.1% of the score set's positions (232,968 / 261,501) against the rank
stage's 98.1% (109,816 / 111,908), so the stored particle population attached
to a score query is a sparser and more biased sub-population of the full one,
and the regeneration comparison is confounded by that coverage, not by the
family. The registered winner rule itself is unaffected.

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

- PRIMARY (store = `fit_lo`, score = `fit_hi`): winner `PLUR`, 16,581 errors,
  fit-majority 70,170.
- REGEN (store = `fit_hi`, score = `fit_lo`): winner `PLUR`, 20,732 errors,
  fit-majority 70,460.
- class `POPULATION_PLURALITY` in both; the gate holds. The rank-stage winner
  is `PLUR` (5,366 errors) and the held winner of record is `PLUR` (622
  errors); all four stages recover the class `POPULATION_PLURALITY`, and in
  this package the winner rule additionally picks the **same readout** `PLUR`
  at every stage — unlike the siblings, whose conjunct varies slightly between
  halves and whose registered gate is the class alone.

## R2.2 The null constructions, registered in exact reproducible form

The nulls are **permutations produced by a fixed-seed, version-independent
RNG** — Python's `random.Random` (the Mersenne Twister) with the seeds below —
never by a keyed sort. The registered constructions:

```
label-null   rng = random.Random(20260926); labels = scored_held_labels[:]
             rng.shuffle(labels); count mismatches between the winning arm's
             unchanged predictions and the shuffled labels.
design-null  rng = random.Random(20260927); the stored particle votes are
             reweighted: over the sorted list of distinct STORED descriptors,
             the vector of their particle votes v(p) is permuted by
             rng.shuffle; the winning readout PLUR is re-applied to the SAME
             store with the reweighted particle votes (same store size, same
             query set, same population membership -- only the assignment of
             votes to particles moves).
```

The design null is the **matched negative for the population consensus**: it
destroys only the alignment between a particle's vote and the population it
belongs to, leaving the store size, the population structure, the query set and
the length structure untouched. If the recovered readout were an artifact of
population geometry rather than of the consensus of the particles' votes, the
reweighted population would reproduce it.

The falsifier forms of `FREEZE_V1_SLICE_ADDENDUM.md` are unchanged:

- F1 the winning arm's held error count is at most half the fit-majority rule's
  held error count;
- F2 the label-null's held error count strictly exceeds the fit-majority rule's
  held error count;
- F3 the design-null's held error count is more than three times the winning
  arm's held error count.

Measured (design statistics, re-derived by the executor): arm 622; majority
20,001 (half 10,000, F1 holds); label-null 26,342 > 20,001 (F2 holds); design
null 33,268 > 1,866 = 3 × 622 (F3 holds). Both nulls fire against the committed
constructions. The design null leaves the two admitted single-item reads where
the data puts them — `MEM_FALLBACK` 2,426 (unchanged: its stored branch degrades
with the stored-table vote, and the reweight leaves those votes in place) and
`PARTICLE_1` 29,697 (it reads one particle's vote, which the reweight moves) —
and leaves the membership arm `CNT>=1` exactly at its measured 19,933, as a
construction that touches only particle votes must.

A keyed-label permutation (held labels reordered by the registered Knuth key,
`key(i) = (i * 2654435761) mod 2**32` over held positions) is recorded as a
boundary datum: 25,686 errors, indistinguishable from the label-null (26,342)
and far from the arm (622). The keyed permutation therefore does not
degenerately reproduce the arm at this scope; the RNG construction is
nevertheless the registered one, kept identical in form to the siblings'.

## R2.3 The tie-break charged cost, registered

The winner rule ties by "fewer charged-cost units". The registered per-query
charged cost of a readout is the number of stored descriptors it references:
`C0`/`C1` 0; `LEN<=L` 0; `CNT>=K` 1 (one membership-count lookup); `ASSOC>=K`
1 (one association-fan-out lookup); a `THRESHOLD_CONJUNCTION` 1 (one
stored-context lookup for the membership/association conjunct; the length
conjunct is free); `PARTICLE_1` 1 (one stored particle read); `MEM_FALLBACK` 2
(one membership lookup and one stored-table read); `PLUR` and `PLUR_W` the
number of stored particles of the query (the population it aggregates);
`PREF_VOTE` the number of stored proper prefixes of the query; `EXT_VOTE` the
number of stored extensions of the query. No tie occurred at any measured
stage; the definition is registered so the winner rule is deterministic in
every environment.

## R2.4 The matched-presentation negative control (R05), registered

The ecology is non-sequential; source order is a presentation artifact. The
registered presentation is the target-independent Knuth permutation of R2.1.
The **matched negative** is the same ecology, the same scored query set, the
same readout language `R`, the same winner rule, and the **source-order
presentation** (the descriptor list read contiguously: first `n_fit` to fit, the
tail to held, the first `len(rank_fit)` of fit to the ranking store). Measured:
under source order the family readout `PLUR` degrades to 21,096 held errors
against the majority's 21,104 — it is **worse than a coin weighted by the
majority rule and no longer separates at all** — and the winning readout is
`LEN<=6` at 15,162 held errors, which does **not** clear F1 (15,162 > 10,552 =
21,104 // 2), so the screen fires. The control demonstrates that the registered
presentation lever is load-bearing and that the family effect is not an artifact
of the population readout alone.

## R2.5 The single-particle-store negative control (R04), registered

The registered negative control for the plurality mechanism collapses each
query's stored particle population to **at most one particle** (the
lexicographically first stored child), leaving everything else — the store, the
query set, the label, the arms — identical. Under that collapse the plurality
read has no population to be a plurality over: it becomes the one particle's own
vote. Measured: `PLUR` 12,210 errors against the majority's 20,001 — it **fails
F1** (12,210 > 10,000) — while on the registered ecology the same arm makes 622.
The control therefore fires: the mechanism requires a stored **population**, and
a single stored particle does not carry the answer.

Its companion datum is the admitted single-particle read `PARTICLE_1` on the
registered ecology: 12,278 errors, i.e. within 68 decisions of the collapsed
control's 12,210, and a factor of 19.7 worse than `PLUR`'s 622. The two arms
that read one stored item — the partial stored-table read `MEM_FALLBACK` (2,426)
and the one-particle read `PARTICLE_1` (12,278) — are the admitted competitors
and are rejected by the data at every stage.

## R2.6 The admitted arms, rejected at every stage

The slice addendum's constant-branch exclusion rule registers that the rule
eliminates **nothing** from the language and that the admitted arms must be
rejected by the winner rule. Measured (design statistics, re-derived by the
executor), against the winner `PLUR`:

| stage | `PLUR` | `MEM_FALLBACK` | `PARTICLE_1` | `PLUR_W` |
|---|---|---|---|---|
| rank (store `rank_fit`, score `rank_score`) | **5,366** | 18,310 | 25,662 | 19,169 |
| held (store `fit`, score `held`) | **622** | 2,426 | 12,278 | 9,533 |
| PRIMARY (store `fit_lo`, score `fit_hi`) | **16,581** | 49,965 | 47,440 | — |
| REGEN (store `fit_hi`, score `fit_lo`) | **20,732** | 54,378 | 53,136 | — |

The count-weighted plurality `PLUR_W` is a second `POPULATION_PLURALITY` arm
in the language and is a genuinely different aggregation: it loses by the data
(9,533 held against 622), so the winner rule's choice is not merely "some
population read" but the **unweighted strict plurality** the protected
interface registers. No exclusion rule needed to fire for the family readout to
win.

## R2.7 Consequences that are registered here

- `n_fit`, `n_held`, `rank_fit`, `rank_score`, the Knuth key, the registered
  scored query set, the registered particle vote constant, the readout language
  `R`, the winner rule, the charged-cost model and every falsifier form are
  unchanged.
- The symmetric half-split R09 (R2.1), the null constructions (R2.2), the
  tie-break cost (R2.3), the presentation control (R2.4), the single-particle
  store control (R2.5) and the rejection datum (R2.6) are the registered forms
  the executor implements and route B re-derives independently from this text
  alone.
