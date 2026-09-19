# GMI #833 Section Z / Z12 — exact prediction-scoring protocol, freeze v1

Source `main`: `91c6d2876ba80c517a186e28fce3bdbe4e3fc218`.

This freeze is committed **before** any scorer, oracle, hostile, null or test in
this package exists. `git log` must show this commit strictly preceding the
first implementation commit of `research/gmi-833-z-z12-prediction-scoring-v1/`.
Audit #976 filed a `POST_HOC_SUSPECT` for a freeze that postdated its result by
89 minutes; this freeze registers every definition, every gate threshold, every
hostile and the null before a single number is computed.

## Claim ceiling

```
GMI_833_Z12_EXACT_PREDICTION_SCORING_PROTOCOL_APPLIED_TO_PINNED_FROZEN_ON_MAIN_PREDICTION_POPULATIONS
```

## The exact rows this tranche may reconcile

Section Z lives in issue comment `5684819296`, subsection
`### Z12 — Prediction sharpness, uncertainty and scientific risk`. The nine rows
are, verbatim:

1. `- [ ] Prevent vacuous predictions that allow every morphology.`
2. `- [ ] Require probability distributions, ranked sets, confidence sets or otherwise quantitatively bounded predictions where appropriate.`
3. `- [ ] Score calibration.`
4. `- [ ] Score coverage.`
5. `- [ ] Score log loss/Brier score or justified alternatives.`
6. `- [ ] Score regret from wrong morphology selection.`
7. `- [ ] Measure prediction-set size/sharpness.`
8. `- [ ] Require abstention when GMI cannot identify the answer.`
9. `- [ ] Penalize post-hoc widening of prediction sets.`

**No neighboring row is earned here.** No row of Z1–Z11 or Z13–Z18, and no row
of the issue body sections A–M or of any other Z comment, may be reconciled by
this package. The trailing `## Groundbreaking flagship closure rule` prose block
carries no rows and is never touched.

## Parent ownership, declared before measuring

This package contributes an **instrument**, not predictions. Every prediction it
scores was frozen prospectively by another lane, already merged on `main`, and
is pinned here by git blob sha. Two parents already compute part of what Z12
asks for, and this package must credit them rather than re-announce their work:

- `gmi-833-capability-predictor-evaluation-v1` already computes, as its result
  `KE-6`, exact coverage and an exact calibration-error table under a registered
  32-pattern fault law, each reported beside its abstention rate. Rows 3 and 4
  are therefore **parent-served in part**; the residual claimed here is a
  source-separated re-derivation from the pinned blobs under a scoring
  definition that is uniform across both populations, plus the binning by
  prediction-set size that the parent does not compute.
- `gmi-833-capability-abstention-v1` already owns an abstention theorem. Row 8's
  residual here is the *executable* abstention-soundness gate over a morphology
  population with exactly enumerated unidentifiable records.
- `gmi-833-heldout-20-transitions-v1` owns the morphology predictions, the
  boundary law `lambda* = eta*p/2`, and the two search procedures. Nothing about
  the truth of those predictions is re-claimed; they are the scored object.

Rows 1, 2, 5, 6, 7 and 9 have no on-main parent instrument found by two
independent searches (directory-name scan of all 102 `research/gmi-833-*`
packages, and a content grep for `brier`, `regret`, `sharpness`, `vacuous`,
`widening`). If such a parent is found later it must be credited by amendment.

## Scored populations (pinned before scoring)

| id | source file | blob sha | what a record is |
|---|---|---|---|
| `POP_M` | `research/gmi-833-heldout-20-transitions-v1/RESULT_V1.json` | `da3c747269bb39528f6293e5daa3c2142a935bde` | one `(case, endpoint)` morphology prediction over alphabet `A_M = {PERSISTENT_STATE, STATELESS}` |
| `POP_M` world params | same file, `cases[*]` | same | `(p, eta, lambda_low, lambda_high, threshold)` as exact rationals |
| `POP_K1` | `research/gmi-833-capability-predictor-evaluation-v1/FROZEN_PREDICTIONS_V1.json` | `7e1ca514ddb7361993585f6ba375d26a08ba13f1` | frozen `identified_set` / `disposition` per `(universe, case_index, budget)` |
| `POP_K4` | `research/gmi-833-capability-predictor-evaluation-v1/FROZEN_PREDICTIONS_V4.json` | `cb7b1467f6f8a6ba2798835f41b2e830c95c2edb` | same, for the V4 universes |
| truth for `POP_K*` | `research/gmi-833-capability-predictor-evaluation-v1/RESULT_V1.json` | `21280ff68f75cc3dfba863f26612672cd411b4bd` | `curves[*].detail[*].points[*].external_values`, the externally computed consistent-value set |

`POP_K` admits exactly those universes present in **both** a
`FROZEN_PREDICTIONS_V*.json` and `RESULT_V1.json['curves']` with identical case
ordering and identical `budget` vectors per point. A universe failing that
alignment is refused, never silently dropped.

`POP_M` has 40 endpoint records plus 20 boundary records at `lambda = lambda*`,
60 records total. The boundary records' predictions are derived from the frozen
boundary law, not invented here: `lambda < lambda*` predicts
`{PERSISTENT_STATE}`, `lambda > lambda*` predicts `{STATELESS}`, and
`lambda = lambda*` predicts the tie `{PERSISTENT_STATE, STATELESS}`.

## Registered definitions — all exact, `Fraction`/`int` only

For record `i`: `S_i` is the predicted set, `T_i` the true set, `A` the
registered alphabet, `N` the population size.

- **`BND-1` bounded-prediction typing.** Every record must type as exactly one of
  `POINT` (`|S_i| = 1`), `SET` (`1 < |S_i| < |A|`), `ABSTAIN_FULL`
  (`S_i = A`), each carrying the registered uniform predictive distribution
  `q_i(a) = 1/|S_i|` on `a in S_i` and `0` elsewhere. A record that is empty,
  untyped, or carries values outside `A` is **refused** and fails the run.
- **`VAC-1` vacuity.** Record `i` is vacuous iff `S_i = A` **and** `T_i != A`.
  A full-alphabet prediction where the truth is genuinely the full alphabet is a
  *licensed* abstention, not vacuity — the two are separated deliberately,
  because on a binary morphology alphabet they are otherwise indistinguishable.
  Gate: `vacuity_rate == 0` on the real populations.
- **`COV-1` coverage.** `cov = #{i : T_i subset-or-equal S_i} / N`, exact.
- **`SHP-1` sharpness.** `mean|S| = (sum |S_i|)/N`, `max|S|`, and excess
  `mean(|S_i| - |T_i|)`, all exact. Smaller is sharper.
- **`CAL-1` calibration.** Bin records by claimed single-element confidence
  `c = 1/|S_i|`. Within a bin, the achieved predictive mass on truth is
  `h_i = |T_i intersect S_i| / |S_i|`. Bin calibration error is
  `|mean_bin(h) - c|`; `CAL-1` reports the per-bin table and the maximum, exact.
- **`BRI-1` Brier.** Multiclass Brier against the registered target
  distribution `t_i(a) = 1/|T_i|` on `a in T_i`:
  `BS_i = sum_{a in A} (q_i(a) - t_i(a))^2`, exact rational; `BRI-1` is the mean.
  **Log loss is declined**, invoking this row's own `or justified alternatives`
  disjunction: log loss has no exact rational value, and every number in this
  programme must be exact. The declination is registered here, before any score
  exists, so it cannot be read as an omission discovered after the fact.
- **`REG-1` regret from wrong morphology selection.** Only defined on `POP_M`,
  where a decision has a registered cost. The frozen objective is
  `J(candidate, world) = eta*((1-p)*e_now + p*e_delay) + lambda*state_bits`
  with `e_* in {k/16}`; the class optimum is `J*(class) = min` over candidates of
  that class. Selection rule `sigma` is registered as **lexicographically least
  element of `S_i`**. `regret_i = J*(sigma(S_i)) - min_class J*(class)`, and the
  worst-case variant `regret_worst_i = max_{s in S_i} J*(s) - min_class J*(class)`.
  Both exact rationals. `REG-1` reports mean and total of each.
- **`ABS-1` abstention.** Record `i` abstains iff `|S_i| > 1`. A record is
  *unidentifiable* iff `|T_i| > 1`. **Abstention soundness**: no unidentifiable
  record may carry `|S_i| = 1`. Gate: soundness violations `== 0`.
- **`WID-1` post-hoc widening.** Each record carries
  `sha256(canonical_json(sorted(S_i)))` recomputed from the pinned blob at scoring
  time and compared to the value derived from the same blob at load time by the
  independent route. Any record whose set is not byte-derivable from its pinned
  parent blob is **rejected and fails the run**. The penalty is therefore
  refusal, not a score adjustment; a widened set cannot buy coverage.

## Two materially independent routes (required for every number above)

- **Route A** `z12_prediction_scoring_v1.py`: streaming, per-record `Fraction`
  accumulation; morphology class optima from the closed-form frozen law
  (`J*(STATELESS) = eta*p/2`, `J*(PERSISTENT_STATE) = lambda`).
- **Route B** `independent_scoring_oracle_v1.py`: opens the pinned blobs itself,
  canonicalizes each record to the integer key
  `(|S|, |T|, |S int T|, [T subset S])`, aggregates integer counts per key, and
  derives every score from those counts by integer/least-common-denominator
  arithmetic; morphology class optima by **exhaustive enumeration of all 65,552
  registered candidates** (16 stateless output tables + 256x256 one-bit
  transducers) with its own semantics implementation. Route B imports nothing
  from Route A and shares no helper module.

Route B's enumeration must independently reproduce the parent's recorded
controls: `65552` candidates, `146` distinct risk/state summaries, stateless
minimum delayed error exactly `1/2`, `40/40` endpoint classifications, and `20`
exact boundary ties. Disagreement anywhere fails the run.

## Hostiles — each must be shown to MOVE its quantity and to be DETECTED

A hostile that cannot move the quantity it perturbs passes while testing
nothing. For every hostile `h` the receipt records the exact rational delta
`score(h) - score(true)` **and** the detection verdict, and asserts the
no-alarm case on the true population.

| id | perturbation | quantity it must move | detector |
|---|---|---|---|
| `H1_VACUOUS` | `S_i := A` for all `i` | `VAC-1` rate, `SHP-1` mean | vacuity gate |
| `H2_WIDENER` | enlarge exactly one `S_i` by one element | `SHP-1` mean by exactly `1/N`; `COV-1` if it repairs a miss | `WID-1` sha256 provenance |
| `H3_NEVER_ABSTAIN` | `S_i := {min S_i}` for all `i` | `ABS-1` abstention rate; soundness violations on the 20 boundary ties | abstention-soundness gate |
| `H4_MISCALIBRATED` | claim `c = 1/(|S_i|-1)` where `|S_i|>1` | `CAL-1` max bin error | calibration gate |
| `H5_TRUTH_LEAK` | `S_i := T_i` | `COV-1` to `1`, `SHP-1` to minimum | `WID-1` provenance refusal |
| `H6_REGRET_BLIND` | `sigma := const STATELESS` | `REG-1` mean regret | regret gate (`>0` on low endpoints) |

## Null the true result must beat

200 randomized predictors, `random.Random(seed)` for `seed in range(1000, 1200)`,
each drawing every `S_i` uniformly from the non-empty subsets of `A`. The frozen
predictor must beat every one of the 200 on the registered lexicographic
composite `(coverage desc, mean|S| asc, mean regret asc)`. Target: `0/200`
randomized predictors match or beat the frozen predictor. If any does, the result
is reported as a failure, not refitted.

## Forbidden promotions

`SCORING_IMPLIES_PREDICTION_CORRECTNESS`, `CALIBRATION_BEYOND_PINNED_POPULATIONS`,
`REAL_SYSTEM_PREDICTION_VALIDATED`, `UNIVERSAL_MORPHOLOGY_PREDICTION`,
`LOG_LOSS_SCORED`, `COMPLETE_GMI`, `PARENT_RESULTS_RE_EARNED_HERE`,
`ABSTENTION_POLICY_OPTIMALITY`.

## Falsifiers registered now

- Route A and Route B disagreeing on any exact rational.
- Route B failing to reproduce any parent-recorded control.
- Any hostile whose recorded delta is `0` (it could not fire).
- Any hostile that is not detected.
- Vacuity rate, abstention-soundness violations, or provenance rejections
  nonzero on the real populations.
- Any randomized null matching or beating the frozen predictor.
