# Z15 named results

Exact rational arithmetic throughout; no float appears in any claim. Every
verdict is produced by two source-separated routes: route A (per-candidate
`Fraction` scan plus a verified summary reduction) and route B (a multiplicity
histogram built from an independently written semantics, decided with **integer**
objective coefficients obtained by clearing denominators). Route B imports
nothing from route A and nothing from the Z12 package.

**Scope shared by every result.** The registered finite world set only: 20
`(p, eta)` worlds x 3 lambda positions (`lambda*/2`, `3·lambda*/2`, `lambda*`) =
60 worlds, over the registered universe of 65,552 binary mechanisms (16 stateless
output tables, 256x256 one-bit transducers), reducing to 146 distinct
`(state_bits, e_now, e_delay)` summaries. Plus the 480 pinned capability records
for `F3`.
**Forbidden extrapolation shared by every result.** Surviving these falsifiers
does not verify the theory; the set of four is not claimed complete; nothing here
licenses a real-system or universal claim.

---

## `Z15-REDUCE` — the flagship theory reduces to four decisive falsifiers

**Statement.** The flagship morphology-selection theory is stated in four
sentences without reference to the repository (`FREEZE_V1.md`, section "The
flagship theory, stated without the repository"), and four executable falsifiers
`F1/F1+`, `F2`, `F3`, `F4` decide it. Four is inside the row's registered range
of three to five. Each falsifier carries a fixed threshold (`fires iff count > 0`),
a planted positive that makes it fire, and a clean no-alarm case on real data.

**Clean results.** `F1` `0/40`; `F1+` `0/60`; `F2` `0/60`; `F3` `0/480`;
`F4a` `0` changes over `12,000` world-checks under `200` seeded remints;
`F4b` `0` changes over `360` `(world, scale)` checks.
**Planted results.** `F1` `20/40`; `F1+` `20/60`; `F2` `20/60`; `F3` `1/480`;
`F4a` `> 0` changes across `200` distinct corrupted multisets; `F4b` `240/360`.
**Falsifier of this result.** Any falsifier silent on its plant, or firing on
clean data.
**Forbidden extrapolation.** `FALSIFIER_SET_IS_COMPLETE`,
`THEORY_VERIFIED_BY_SURVIVING_FALSIFIERS`.

## `Z15-F1` — systematic morphology-selection failure

**Statement.** Over the 40 registered endpoint worlds, the theory's predicted
morphology class equals the exhaustively computed argmin class in `40/40` cases.
The deliberately shifted boundary `2·lambda*` fails in `20/40`, reproducing
exactly the `shifted_threshold_failures = 20` recorded by the parent lane.

**Strongest parent.** The predictions, the boundary law and the two search
procedures are owned by `gmi-833-heldout-20-transitions-v1` (#901); this result
owns only the falsifier that decides them.

## `Z15-F1-BLIND` — `F1`'s resolution limit, EARNED BY COUNTEREXAMPLE

**Statement.** `F1` restricted to endpoints is **blind** on the open interval
`r in (1/2, 3/2) \ {1}` of boundary multipliers, and decisive outside
`[1/2, 3/2]`.

**Proof.** The registered endpoints sit at `lambda*/2` and `3·lambda*/2`. A
shifted boundary `r·lambda*` reproduces the true endpoint classification exactly
when `lambda*/2 < r·lambda* < 3·lambda*/2`, i.e. `1/2 < r < 3/2`. QED
**Counterexample.** `r = 6/7`: `F1` records `0/40` mismatches and does not fire.
**Measured confirmation.** Over the registered 200-seed null, `F1` catches
`143/200`; the `57` survivors realize exactly `12` distinct multipliers
`{2/3, 3/4, 3/5, 4/3, 4/5, 4/7, 5/4, 5/6, 5/7, 6/5, 6/7, 7/6}`, **all** inside
`(1/2, 3/2)`, with `0` survivors outside the interval and `0` catches inside it.
The characterization is verified, not asserted.
**Attribution.** One stage: the registered world ladder. Two points a factor of
three apart cannot localize a boundary better than a factor of two. No re-running
of endpoints repairs it.

## `F1PLUS-DEC` — the revival is unconditionally decisive

**Statement.** For **every** rational `r != 1`, `F1+` — `F1` evaluated over all
60 registered worlds, endpoints and boundaries — fires.

**Proof.** At `lambda = lambda*` the two class optima are `eta·p/2` and
`lambda`, which coincide, so the exhaustive argmin is the two-element tie. A
shifted law with `r > 1` predicts the singleton `{PERSISTENT_STATE}` there and
one with `r < 1` predicts `{STATELESS}`; a singleton never equals the tie, so at
least one of the 20 boundary worlds mismatches. QED
**Measured confirmation.** `200/200` randomized boundaries caught, `0/200`
surviving; `F1+` remains silent on the true law (`0/60`).
**Why this is not tuning.** The world ladder, the threshold and the theory are
unchanged; the revival uses the 20 boundary worlds the frozen design already
contained but `F1` did not read. The frozen `F1` and its measured `143/200` are
retained beside it rather than replaced.

## `Z15-F2` — architecture-uncommitted recovery stays inside the predicted set

**Statement.** Over all 60 registered worlds, the exhaustive winner class set —
computed from opaque candidate summaries carrying no architecture name — is
contained in the predicted set in `60/60` cases. Narrowing the prediction to
`{STATELESS}` at the 20 worlds with `lambda < lambda*` makes the falsifier fire
`20/60`.

**Scope note.** `architecture-uncommitted` here means the search sees only
`(state_bits, e_now, e_delay)` summaries and opaque identifiers; it does **not**
mean prior-free, and no such claim is made.

## `Z15-F3` — capability miscalibration beyond registered uncertainty

**Statement.** Registered uncertainty for the capability predictor is set
containment: the emitted set claims to contain the truth. Over the 480 pinned
records, the externally computed truth set is contained in the frozen prediction
set in `480/480` cases. Removing one truth element from one covering set makes
the falsifier fire `1/480`.

**Parent credit.** The predictions and external truth sets are owned by
`gmi-833-capability-predictor-evaluation-v1` (#1022), whose `KE-6` already
reports exact coverage for its own population.

## `Z15-F4` — invariance under transformations claimed irrelevant, and non-invariance under one that is not

**Statement (`F4a`, candidate-identifier remint).** Over 200 seeded permutations
of the 65,552 candidate surface identifiers — `12,000` world-checks — the winner
class set changes in `0` cases, and all 200 remints produce the same summary
multiset (`distinct_multisets = 1`). A pseudo-remint that also permutes the error
coordinates produces `200` distinct multisets and thousands of changes, and fires.

**Statement (`F4b`, common unit rescaling).** Under the registered ladder
`c in {1/7, 1/2, 2, 3, 11/5, 100}`, the map `(eta, lambda) -> (c·eta, c·lambda)`
changes the winner class set in `0` of `360` `(world, c)` checks — the objective
scales by `c > 0`, so the argmin set is invariant. Rescaling `eta` **alone**,
which is *not* claimed irrelevant, changes it in `240` of `360` checks.

**Why the pair matters.** An invariance checker that reported `0` for every
transformation would be a constant `False` dressed as a result. The registered
pair forces the checker to distinguish: silent on the genuinely irrelevant
transformation, firing on the relevant one, both measured on the same universe.

## `Z15-PUBLISH` — failed preregistered predictions published beside the successes

**Statement.** `FAILED_PREDICTION_REGISTER_V1.json` carries **6** failed,
falsified or open entries and **2** success entries. Every entry is pinned by
repository path, git blob sha and a verbatim anchor that must occur **exactly
once** in the pinned file; all `8` resolve.

| id | kind |
|---|---|
| `FP-KE3D` | three prospectively frozen registration laws falsified by their own falsifiers |
| `FP-KE3D-OPEN` | the affected row published as still open, not closed on synthetic data |
| `FP-939-OVERSTRONG` | the one confirmed corpus overclaim, revived rather than narrowed |
| `FP-REV-OPEN` | six open revival tickets carried as obligations |
| `FP-SHIFTED-BOUNDARY` | a preregistered wrong boundary falsified 20/20 — **a designed negative control, labelled as such, not a discovered failure** |
| `FP-Z12-CAL-V1` | this programme's own Z12 calibration instrument, found mis-specified and repaired before its numbers were used |

**Validation of the register checker itself.** The test plants a non-occurring
anchor (`anchor_count = 0`, rejected) and a missing file (`exists = False`,
rejected), so the checker is shown able to fail before its passes are believed.
**Forbidden extrapolation.** `ALL_FAILED_PREDICTIONS_ENUMERATED`,
`NEGATIVE_CONTROL_IS_A_DISCOVERED_FAILURE`.
