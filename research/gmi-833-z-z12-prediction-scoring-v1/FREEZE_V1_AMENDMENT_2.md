# Z12 freeze v1 — amendment 2: CAL-1 was a mis-specified instrument

Committed **before** the corrected calibration numbers are used in any receipt or
reconciliation. The v1 instrument was run, its output was inspected, it was found
to be measuring the wrong thing, and it is being repaired rather than reported.
The v1 quantity is **retained**, not deleted.

## The defect

`FREEZE_V1.md` defined `CAL-1` at record level: bin records by the claimed
single-element confidence `c = 1/|S_i|`, and compare `c` against the mean of
`h_i = |T_i intersect S_i| / |S_i|`.

That compares a **per-element** claim against a **set-level** realization. When
the truth set `T_i` has `m > 1` elements all inside `S_i`, `h_i = m/|S_i|`, which
exceeds `c = 1/|S_i|` by construction — a structural offset, not a calibration
error. On the pinned populations the v1 instrument reports a maximum bin error of
`7/8` on `POP_K` and `1/2` on `POP_M` **while coverage is exactly `1`**. A
calibration score that is large on a perfectly covering predictor is not
measuring calibration.

The same defect makes the registered `H4_MISCALIBRATED` hostile inert: claiming
`c' = 1/(|S_i|-1)` moves the v1 maximum bin error from `7/8` **down** to `6/7`,
so the hostile perturbs the quantity but the detector cannot fire on it. A
hostile that cannot be detected tests nothing — the exact failure class this
tranche was warned about.

Failure attribution: **one stage, the instrument's binning level.** Not the
predictor, not the population, not the hostile.

## Registered repair

`CAL-1` is re-specified at **element level**, which is the level at which the
predictive law `q_i(a) = 1/|S_i|` actually makes a claim.

- Enumerate pairs `(i, a)` for every record `i` and every `a in S_i`.
- Claimed probability `q = 1/|S_i|`. Realized target mass `y_i(a) = 1/|T_i|` if
  `a in T_i`, else `0` (the registered target distribution already fixed in
  `FREEZE_V1.md` for `BRI-1`).
- Bin pairs by `q`; bin error is `|mean_bin(y) - q|`; `CAL-1` reports the bin
  table and the maximum. All exact rationals.

`REFUTE_WORLD` records contribute no pairs (amendment 1 already excludes them).

The v1 record-level quantity is retained under the name
`CAL_1A_record_level_mass_gap`, reported beside the corrected score, so that
nothing measured is silently dropped.

## Named lemma this repair makes provable

**`CAL-LEM` (element-level calibration is exactly the coverage deficit).**
For any record with `T_i subset-or-equal S_i`, the pairs of record `i`
contribute total realized mass exactly `1` against total claimed mass exactly
`1`; a bin all of whose records cover has calibration error exactly `0`. A bin
containing a record with `T_i not-subset-of S_i` has strictly positive error.
Scope: the registered uniform predictive law and uniform target law, finite
alphabets, `|S_i| > 0`. Falsifier: a covering population with nonzero bin error,
or a miscovering population with zero bin error. Both branches are asserted in
the test as planted controls, so `CAL-1` is validated on a known-clean case and
on a known-dirty case before any of its numbers are reported.

## Consequence for `H4_MISCALIBRATED`

Under the repaired instrument the frozen predictor's element-level error is `0`
in every bin, and the `c' = 1/(|S_i|-1)` claim yields strictly positive error in
every bin with `|S_i| > 1`. The hostile now both **moves** the quantity and is
**detected**, and the no-alarm case on the true population is asserted rather
than assumed.

Everything else in `FREEZE_V1.md` and amendment 1 is unchanged.
