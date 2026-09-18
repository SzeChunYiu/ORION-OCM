# gmi-833-z-z12-prediction-scoring-v1

Section Z (issue comment `5684819296`), subsection **Z12 — Prediction sharpness,
uncertainty and scientific risk**: all nine rows.

This package contributes an **instrument**, not predictions. Every prediction it
scores was frozen prospectively by another lane, is already merged on `main`, and
is pinned here by git blob sha.

Claim ceiling:
`GMI_833_Z12_EXACT_PREDICTION_SCORING_PROTOCOL_APPLIED_TO_PINNED_FROZEN_ON_MAIN_PREDICTION_POPULATIONS`

## Two pinned populations

| id | records | source |
|---|---:|---|
| `POP_M` (morphology) | 60 — 20 low endpoints, 20 high endpoints, 20 boundary ties | `gmi-833-heldout-20-transitions-v1/RESULT_V1.json` |
| `POP_K` (capability) | 480 — 468 mass-scored + 12 `REFUTE_WORLD` | `gmi-833-capability-predictor-evaluation-v1` frozen predictions joined to its external truth sets |

## Headline numbers (exact rationals, both routes agreeing)

| score | `POP_M` | `POP_K` |
|---|---|---|
| `COV-1` coverage | `60/60 = 1/1` | `480/480 = 1/1` |
| `SHP-1` mean set size (max) | `4/3` (`2`) | `40/13` (`8`) |
| `SHP-1` mean excess over truth | `0/1` | `19/117` |
| `VAC-1` vacuous | `0` | `0` |
| `ABS-1` abstained / unidentifiable / unsound | `20 / 20 / 0` | `412 / 396 / 0` |
| `CAL-1` max element-level error | `0/1` | `0/1` |
| `BRI-1` mean Brier | `0/1` | `47/1404` |
| `BND-1` refusals | `0` | `0` |

`REG-1`: total regret `0/1` and total **worst-case** regret `0/1` over all 60
morphology records. The blind-selection hostile pays `15/2` on the same records,
so the zero is a property of the predictions, not of the scorer.

Retained pre-amendment quantity `CAL_1A_record_level_max_mass_gap`: `1/2`
(`POP_M`), `7/8` (`POP_K`) — a structural offset, not a calibration error;
see `FREEZE_V1_AMENDMENT_2.md`.

Log loss is **declined** under the row's own *or justified alternatives* clause:
no exact rational value exists and this programme admits no float in a claim.
Brier is scored exactly instead. The declination was registered before any score.

## Two materially independent routes

- **A** `z12_prediction_scoring_v1.py` — streaming per-record `Fraction`
  accumulation; morphology class optima from the closed-form frozen boundary law.
- **B** `independent_scoring_oracle_v1.py` — opens the pinned blobs itself,
  reduces each record to the integer key `(|A|, |S|, |T|, |S int T|)`, aggregates
  integer counts, derives every score from those counts; morphology class optima
  by **exhaustive enumeration of all 65,552 registered candidates** with its own
  semantics. It imports nothing from route A.

Route B independently reproduces every control the parent recorded: census
`65552`, `146` distinct risk/state summaries, stateless minimum delayed error
`1/2`, `40/40` endpoint classifications, `20` exact boundary ties.

## Hostiles — all six move their quantity and all six are detected

| id | moves | detected by |
|---|---|---|
| `H1_VACUOUS` | vacuity `0/1 -> 2/3`, mean size `4/3 -> 2/1` | vacuity gate |
| `H2_WIDENER` | mean size by exactly `1/468` (predicted = observed) | sha256 provenance, `1` flagged, `0` on clean |
| `H3_NEVER_ABSTAIN` | abstention `1/3 -> 0/1`, soundness violations `0 -> 20` | abstention-soundness gate |
| `H4_MISCALIBRATED` | calibration max error `0/1 -> 6/7` | calibration gate |
| `H5_TRUTH_LEAK` | mean size `40/13 -> 341/117`, coverage forced to `1` | provenance refusal |
| `H6_REGRET_BLIND` | total regret `0/1 -> 15/2` | regret gate |

The no-alarm case is asserted for every hostile on the untouched populations.

## Null

200 randomized control predictors (`random.Random(s)`, `s in [1000,1200)`) on
`POP_M`: the frozen predictor beats **200/200**; `0/200` match or beat it on the
registered composite `(coverage desc, mean|S| asc, mean regret asc)`.

## Reproduce

```bash
python3 -I -B  research/gmi-833-z-z12-prediction-scoring-v1/independent_scoring_oracle_v1.py
python3 -I -B  research/gmi-833-z-z12-prediction-scoring-v1/z12_prediction_scoring_v1.py
python3 -I -B  research/gmi-833-z-z12-prediction-scoring-v1/test_z12_prediction_scoring_v1.py -v
python3 -I -O -B research/gmi-833-z-z12-prediction-scoring-v1/test_z12_prediction_scoring_v1.py -v
```

25 tests, stdlib only, verified on CPython 3.8.10 and 3.13.

## What this package does NOT claim

It does not claim any scored prediction is true beyond its own lane's frozen
scope; it does not re-earn `gmi-833-capability-predictor-evaluation-v1`'s `KE-6`
coverage/calibration or `gmi-833-capability-abstention-v1`'s abstention theorem,
both of which are credited in `PARENT_DISCLOSURE_V1.md`; it does not score log
loss; and it licenses no real-system or universal morphology prediction.
