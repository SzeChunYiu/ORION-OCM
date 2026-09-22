# Slice addendum R2 — the symmetric half-split `R09`, the registered null constructions and the matched negative control

`source_main`: `6e116ce5`.
Governs: `FREEZE_V1.md`, `FREEZE_V1_SLICE_ADDENDUM.md` (each committed before
this addendum).

This addendum registers the regeneration form, the null constructions in exact
reproducible form, and the matched negative control that `R05` requires. It is
committed **before any executor, test, data extraction, fit, search, or result
artifact of this package exists**. CI asserts that every implementation
artifact postdates it. It relaxes no falsifier, changes no prediction, no
count, no ecology, no grammar, no scope, no claim ceiling, and no frozen number
of `FREEZE_V1.md` or of the slice addendum.

## R2.1 The `R09` regeneration: the symmetric half-split (registered from the start)

The sibling `gmi-833-h-real-scale-nearest-neighbor-v1` discovered, by
measurement, that the store-size-asymmetric complementary split (store =
`rank_score` / score = `rank_fit`) confounds the regeneration comparison with
coverage, and corrected its `R09` to the symmetric half-split. This line
adopts that correction **from the start**, and measures its own asymmetry for
the boundary record:

```
key(i)   = (i * 2654435761) mod 2**32        (registered, unchanged)
order    = sorted(range(T), key = key)       (registered, unchanged)
n_fit    = (T*7)//8                          (unchanged)
fit_lo   = order[0 : n_fit//2]               (293,938 positions)
fit_hi   = order[n_fit//2 : n_fit]           (293,939 positions)
held     = order[n_fit : T]                  (unchanged, 83,983)
PRIMARY  = the full registered winner rule: store = fit_lo, score on fit_hi
REGEN    = the full registered winner rule: store = fit_hi, score on fit_lo
```

The `R09` gate is: the REGEN winner's structural class equals the PRIMARY
winner's structural class, and both equal the rank-stage winner's class (the
package's winner of record, store = `rank_fit` / score = `rank_score`).

Measured design statistics, re-derived by the executor:

| stage | store | score | n | fallback constant | fallback rule's errors | winner | winner's errors |
|---|---|---|---|---|---|---|---|
| rank | `rank_fit` 411,513 | `rank_score` 176,364 | 176,364 | 0 | 56,687 | `VOTE>=5/10` | 1,303 |
| PRIMARY | `fit_lo` 293,938 | `fit_hi` 293,939 | 293,939 | 0 | 94,724 | `VOTE>=5/10` | 5,457 |
| REGEN | `fit_hi` 293,939 | `fit_lo` 293,938 | 293,938 | 0 | 94,668 | `VOTE>=5/10` | 6,923 |
| held | `fit` 587,877 | `held` 83,983 | 83,983 | 0 | 27,222 | `VOTE>=5/10` | 931 |
| source-order control | `fit[0:n_fit]` | `order[n_fit:T]` | 83,983 | 0 | 24,552 | `VOTE>=5/10` | 23,237 |

Class `REWARD_PROPENSITY_ACCUMULATION` at all five stages; the `R09` gate
holds.

**Boundary datum (not the `R09`).** The store-size-asymmetric complementary
split (store = `rank_score` 176,364, score = `rank_fit` 411,513) is measured
for the record and **also** recovers `VOTE>=5/10`, at 10,499 errors against
that stream's fallback constant's 132,705 (clearing F1); its store covers
54,014 of the score stream's 79,684 distinct contexts (0.6779). The winner
class is therefore stable under the coverage asymmetry at this scope — a
robustness datum, not the registered form. The symmetric half-split is the
registered `R09`, because a regeneration comparison must not be confounded
with coverage.

## R2.2 The null constructions, registered in exact reproducible form

Both nulls are **permutations produced by a fixed-seed, version-independent
RNG** — Python's `random.Random` (the Mersenne Twister) with the seeds below —
never by a keyed sort: a keyed sort of positions or labels is itself a
function of the experience-index multiset and can achieve a degenerate
alignment with the labels.

```
label-null   rng = random.Random(20260931); labels = held_labels[:]
             rng.shuffle(labels); count mismatches between the winning arm's
             unchanged held predictions and the shuffled labels.

design-null  rng = random.Random(20260932); rho = the fit experiences'
             received outcomes in fit order; rng.shuffle(rho); rebuild every
             cell's accumulated mass from the shuffled outcomes; re-apply the
             winning readout VOTE>=5/10 with its registered fallback; count
             mismatches against the registered held labels.
```

The design null is the **matched negative for accumulated outcome feedback**:
it destroys only the alignment between a cell and the outcomes its own
experiences received, leaving the store size, the cell structure, the marginal
outcome rate, the label and the query set untouched. If the recovered readout
were an artifact of cell geometry rather than of accumulated feedback, the
shuffled masses would reproduce it.

The falsifier forms of `FREEZE_V1_SLICE_ADDENDUM.md` section 4 are unchanged:

- **F2** the label-null's held error count strictly exceeds the fallback rule's;
- **F3** the design-null's held error count is more than three times the arm's.

Measured design statistics, re-derived by the executor: arm 931; fallback rule
27,222 (half 13,611, **F1** holds); label-null **36,939** > 27,222 (**F2**
holds); design-null **27,222** > 2,793 = 3 × 931 (**F3** holds). Both nulls fire
against the committed constructions.

The design-null's exact value is itself a datum worth registering: shuffled
accumulated masses reproduce **exactly** the fallback rule's held error count
(27,222 of 83,983), i.e. they carry no held information at all, while the arm
carries 931.

## R2.3 The matched negative control (`R05`), registered

`FREEZE_V1.md` section 10 requires a matched negative under which **no cell's
accumulated mass reflects the outcomes its own experiences received**. The
registered construction is a **per-experience Bernoulli received outcome with
the registered marginal**:

```
rng_i  = random.Random(20260933 * 7919 + i)          (one stream per position i)
rho'(i) = 1  iff  rng_i.randrange(1000) < 322        (the registered marginal, per mille)
```

The registered marginal `322/1000` is the design-measurement value, rounded to
whole per mille, of `FREEZE_V1.md` section 4's label-positive rate over the
whole experience table. The executor asserts only two registered facts about
the constructed stream, and reports the rest: its realised received-outcome
mass lies in the registered band `[300, 340]` per mille of `T`, and it is not
identically zero. Its exact realised mass is written into `REAL_RUNS/`.

The control is matched in every registered respect: the same ecology, the same
experience table, the same store, the same cell structure, the same readout
language `R`, the same winner rule, the same fallback constant, the same held
query set, the same labels, and a received-outcome **marginal** equal to the
registered one — while every **cell** mass is independent of the outcomes its
own experiences received.

Measured design statistics, re-derived by the executor:

| arm family | registered ecology | matched negative control |
|---|---|---|
| best value arm | `VOTE>=5/10` **931** | best value arm **27,215** (`VOTE>=4/10`) |
| raw sibling arms (`CNT>=1`, `ASSOC>=2`, `LEN<=9`, `LEN<=9&CNT>=1`) | 49,503 / 39,241 / 53,651 / 48,217 | **bit-identical** (49,503 / 39,241 / 53,651 / 48,217) |
| arms clearing F1 (bound 13,611) | `VOTE>=3/10`, `VOTE>=4/10`, `VOTE>=5/10`, `VOTE>=6/10` | **NONE** |
| best arm of all | `VOTE>=5/10` 931 | `MEM_FALLBACK` 18,132 (does not clear F1) |

The control fires: the accumulated-feedback arm's advantage collapses from
931 to 27,215 — beyond the fallback rule's own 27,222 in margin terms — while
the raw arms are untouched, because they read stored structure and not
accumulated outcome feedback. **F4** holds.

**Boundary datum.** The degenerate boundary (`rho'(i) = 0` for every
experience, i.e. no received outcome at all) is recorded for the record: the
raw arms stay bit-identical, every value arm collapses to exactly the fallback
rule's 27,222, and again no arm clears F1; the best arm of all is
`MEM_FALLBACK` at 18,132. This is the endpoint of the control family and it is
**not** the registered control: it is not marginal-matched. The registered
control above is the marginal-matched one, and on it the arm reads 27,215, not
27,222 — the constructed stream is not identically zero, which is the point of
registering a matched marginal rather than a constant.

## R2.4 The `RECENCY_LAST` arm is registered and rejected by the data

`VOTE>=5/10` reads **accumulated** feedback; `RECENCY_LAST` reads the **last**
received outcome stored at the query's context — a single stored item, which is
not the row's mechanism. It is admitted to `R` by the (empty) exclusion rule
and must lose by the data; the measured rejection at every stage is committed
in `REAL_RUNS/` and reported in `RESULT_V1.json`.

## R2.5 Consequences that are registered here

- `n_fit`, `n_held`, `rank_fit`, `rank_score`, the Knuth key, the readout
  language `R`, the winner rule, the charged-cost model, the fallback constant
  and every falsifier form are unchanged.
- The symmetric half-split `R09` (R2.1), the null constructions (R2.2), the
  matched negative control (R2.3) and the `RECENCY_LAST` admission (R2.4) are
  the registered forms the executor implements and route B re-derives
  independently from this text alone.
