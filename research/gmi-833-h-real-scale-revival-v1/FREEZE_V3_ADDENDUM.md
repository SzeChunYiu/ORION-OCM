# V3 addendum to FREEZE_V1.md — a defect in the ranking stage, corrected before the re-test

`source_main`: `5e57d4292266bccf435136e1f7d72caa32e920a0`.
Receipts being corrected: `REAL_RUNS_V1/` and the V2 receipts produced under
`FREEZE_V2_ADDENDUM.md`.

This addendum corrects an **implementation parameter that no freeze ever
registered**, and it changes **no prediction**. It is committed before the
re-test and CI asserts that order, exactly as the arithmetic addendum was.

## 1. The defect

The family-blind search has two stages: a coarse screen of all 6,324
enumerated pairs on a small block, then a ranking of the 40 survivors. The
ranking stage **refits each survivor and scores it on the same rows**. That is
in-sample model comparison, and it rewards capacity rather than fit. `G_S`
contains a delay cell, so a candidate whose head reads `STATE` carries an
unbounded-memory accumulator that an in-sample criterion cannot charge for.

The defect is demonstrable without reference to any registered prediction.
At `SIGMA_R02`, on 87,747 rows of the search slice:

| candidate | in-sample squared error, 87,747 rows | squared error refitted and scored on 100,000 disjoint fit rows |
|---|---|---|
| `MUL(ARG,PARAM)` with head `ADD(BIAS,S)` | 8.30709 | 6.68889 |
| `MUL(ARG,PARAM)` with head `ADD(S,STATE)` | **8.29877** | **20.7657** |

The stateful candidate wins in sample by 0.100 per cent and loses out of
sample by a factor of 3.105. The in-sample ranking is therefore not measuring
what the search is for, and the margin it decides on is far below the
disagreement between the two criteria. A ranking whose winner flips with the
block size — 20,000 rows chose the affine head, 87,747 chose the stateful one —
is an unregistered free parameter deciding a registered prediction. That is a
defect whether or not it changes an outcome.

## 2. The correction

The ranking stage scores **out of sample within the search slice**. The search
slice is split once, by position, into a ranking-fit part — the first 70 per
cent — and a ranking-score part — the last 30 per cent. Each survivor is fitted
on the ranking-fit part by the same generic routine and scored on the
ranking-score part, which it has not seen. Candidates are ordered by
(support-admissibility, out-of-sample squared error, node count, `BODY`
rendering, `HEAD` rendering), the same key as before with the loss now out of
sample.

- The screen stage is unchanged and stays in-sample: it is a coarse prefilter
  over all 6,324 pairs, it decides nothing on its own, and it is recorded.
- The **held-out slice is not touched**. Both parts of this split live inside
  the search slice, which is disjoint from the fit slice and from the held-out
  slice by the rule of `FREEZE_V1.md` section 4.
- The rule is applied identically at all three scopes.
- The support-admissibility rule of `FREEZE_V2_ADDENDUM.md` is unchanged and is
  still measured on fit-slice rows.

Out-of-sample model comparison is the textbook remedy for a capacity-biased
criterion; it is not this package's idea and is not claimed as one.

## 3. What does not change

No prediction, no falsifier, no ecology, no slice rule, no grammar, no
classifier priority, no arithmetic rule, no real-scale definition, no scope
identifier, no claim ceiling, no forbidden promotion. The prediction set of
`FREEZE_V2_ADDENDUM.md` section 5 stands verbatim and is re-evaluated on the
corrected run.

The correction can move a recovered class in either direction. It is registered
here **before** the re-run precisely because its direction is not known, and
because a package that fixed a search defect only when the defect was
inconvenient would be worth nothing.

## 4. What this is not

This is **not** a third attempt at a failed prediction. `FREEZE_V2_ADDENDUM.md`
section 6 permits one revival per failure and that budget is spent. If `Q3a`
fails again at `SIGMA_R03B` the `GLMs.` row is reported open, as it already is,
and is not attempted again in this package. `ECOLOGY_ITERATION_UNTIL_POSITIVE`
and `POST_HOC_FALSIFIER_REPLACEMENT` remain in `forbidden_promotions`, and both
earlier receipt sets stay committed so no outcome can be quietly replaced.

## 5. One consequence for `R10`

Ranking now happens on tens of thousands of rows, which cannot be committed to
the repository. The source-separated oracle therefore re-derives the ranking on
a committed block of the same rows — the first 1,500 ranking-fit rows and the
first 1,500 ranking-score rows — against the primary's own ranking on exactly
that block, which the primary commits alongside. `R10` is accordingly the claim
that **two source-separated implementations of the registered procedure agree
on identical inputs**, together with the oracle's independent exact replay of
every held-out quantity, its independent re-derivation of every structural
class, and its independent check of the cost arithmetic. It is **not** a claim
that the oracle re-derived the full-scale ranking, and `RESULT_V1.json` says so
in the `independent_search` block.
