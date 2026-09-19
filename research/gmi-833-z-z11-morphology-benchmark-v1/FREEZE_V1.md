# GMI #833 Section Z / Z11 — Intelligence Morphology Benchmark (IMB-v1) freeze

Committed **before any executor, oracle, case generation, scoring run or receipt
exists in this package**. Git order proves it. The benchmark-generation rules
below are published here, before any hidden outcome exists — that is the content
of row 7.

- `source_main`: `f1e150ea89d1e3422d5ab18ec9a61d36ff17c3e5`
- branch: `research/833-sec-z811`

Claim ceiling:

```
GMI_833_Z11_EXACT_THEORY_PREDICTION_BENCHMARK_WITH_HIDDEN_SEEDED_ECOLOGIES_EMPIRICAL_STREAM_WORKLOADS_AND_SCORED_COMPETITOR_THEORIES_AT_REGISTERED_FINITE_TRANSDUCER_SCOPE
```

## 0. Disclosure — what was known before this freeze was written

Known: the registered floors and laws named in the sibling Z8 freeze §0
(`IC-1`, `λ* = ηp·R0`, `R0(q) = min(q, 1−q)`, `R0(A) = 1 − 1/A`, the nine
three-mode ladder floors), the 13-rule competitor registry of
`gmi-833-z-z6-discrimination-v1` (`DS-1`) and its finding that every
declared-cost parent is observationally equivalent to the repaired law while
`MDL`, hard Occam and `SRM` disagree (`DS-6`), and the exact scoring vocabulary of
`gmi-833-z-z12-prediction-scoring-v1`. **Not known:** any floor under an empirical
input stream, any hidden-ecology outcome, any score of any theory on this
benchmark. No case has been generated and no theory has been run.

## 1. What the benchmark scores

A **theory** is a pure function from a case's **public specification** to a
**prediction record**. It never sees the case's **hidden truth**; the harness
strips the truth before the call, and a planted truth-reading theory is a
hostile that must be caught. The scored object is the theory, never a model:
there is no trained system anywhere in IMB-v1.

Every case's public specification carries: the universe type, the declared
accounting `(η, p_m, ρ)`, the price set `Λ_case`, and the **input-law
description** — `UNIFORM`, `IID(q)`, `PERIOD2`, or `EMPIRICAL(blob, offset)`
with the stream itself public. The hidden truth is computed by exhaustive
enumeration at run time: the profile `E(k)`, the envelope vertex set
(**resource frontier**), the marginals (**transition thresholds**), the argmin
set at each `λ ∈ Λ_case` (**selected architecture class**), and the per-level
**failure-mode** set `{m : p_m > 0 and floor(k, m) > 0}`.

**Row 2 is enforced by schema**: a prediction record must carry all five fields
`profile`, `frontier`, `thresholds`, `selection_by_price`, `failure_modes`;
a record missing any field is rejected, and rejection is a scored outcome, not
an abstention.

Each field entry is one of `POINT(value)`, `INTERVAL(lo, hi, γ)` with a declared
coverage target `γ ∈ {1, 3/4, 1/2}`, `SET(values)`, or `ABSTAIN`.

## 2. Case classes and generation rules (row 7 — published before any outcome)

| class | count | generation rule |
|---|---:|---|
| `C1_LADDER` | `135` | the Z13 three-mode universe (`L = 4`, `b ∈ {0,1,2}`, window `{2,3}`), `UNIFORM`, `η ∈ {1,2,3}`, `p` over eighths; `Λ_case = {j/16 : j = 0..24}` |
| `C2_TWO_LEVEL_IID` | `189` | the two-level delay-1 population, `IID(q)` for the seven registered laws, `η ∈ {1,2,3}`, `p ∈ k/8`; `Λ_case = {j/16 : j = 0..24}` |
| `C3_ALPHABET` | `81` | the alphabet-`A` two-level population, `A ∈ {2,3,4}`, `UNIFORM`, `η ∈ {1,2,3}`, `p ∈ k/8`; `Λ_case = {j/16 : j = 0..24}` |
| `C4_EMPIRICAL_STREAM` | `3 × 15 = 45` | **realistic workloads**: the input law is the empirical distribution of consecutive 4-bit windows of a real, pinned file's byte stream (bit order MSB-first, windows sliding by one bit). Streams: `README.md` blob `d7519609d064a4c478696ec6378f23c771a3db20` (8110 bytes), `LICENSE` blob `d645695673349e3947e8e5ae42332d0ac3164cd7` (11358 bytes), `research/gmi-833-z-z12-prediction-scoring-v1/z12_prediction_scoring_v1.py` blob `2825c19583aa7ca0dc3f9f475553fd9ea419ed3c` (23113 bytes). Three-mode ladder, `η = 1`, `p` over the 15 triples with entries in `{0, 1/4, 1/2, 3/4, 1}`; the executor recomputes each blob sha and fails on drift |
| `C5_HIDDEN` | `60` | **hidden test ecologies**: drawn by `random.Random(secret)` where `sha256(secret) = b7adc75b3ec9b7f3c4fd9f7a9130198a21f01a341d4167bf7ef9abf4a0c9271f`; the preimage is revealed only in the executor commit. Draw, per case: universe type uniformly from `{LADDER, TWO_LEVEL}`, `η ∈ {1..4}`, `p` over sixteenths, input law uniformly from `{UNIFORM, IID(q) with q ∈ {k/10 : k = 1..9}, PERIOD2, EMPIRICAL(one of the three streams, at a random bit offset in [0, 4096))}`, one price `λ = j/32`, `j ∈ 0..48` |
| `C6_NEGATIVE_CONTROL` | `9 + 1` | (a) `9` flat ecologies `p = (1, 0, 0)` at `η ∈ {1,2,3}` × three laws — no transition exists, every marginal is `0`, the frontier is `{0}`; a theory predicting a positive threshold or a non-trivial niche is scored MISS; (b) `1` **scrambled-truth control**: every theory is additionally scored against the truth of a different case (a fixed cyclic shift of the case list); a theory scoring above the null there is a leakage alarm |
| `C7_DISCRIMINATION` | derived | every case on which at least two registered theories emit different non-abstaining class choices; reported as a set with per-pair counts, never generated separately |

Total generated cases: `135 + 189 + 81 + 45 + 60 + 9 = 519`, plus the scrambled
control pass.

## 3. Registered theories, fixed now

| id | theory | how it predicts from the public spec |
|---|---|---|
| `T_GMI_IC1` | the registered GMI law | stateless floors = the Bayes error of the target given the current symbol under the stated input law (`R0(q) = min(q, 1−q)` at `IID`, `1 − 1/A` at alphabet `A`, `0` for the now-channel, the empirical pair-Bayes error for `EMPIRICAL`); `b ≥ 1` delay-1 floor `0`; `b = 2` floors `0`; `b = 1` delay-2 floor `5/16` under `UNIFORM`, `0` under `PERIOD2`, and `INTERVAL(0, R0(0, 2), γ = 1)` otherwise; thresholds are the marginals of the predicted profile (interval arithmetic where a cell is an interval); frontier and class choice by `IC-1` applied to the predicted profile, `ABSTAIN` where an interval leaves the verdict undetermined at its endpoints |
| `T_HALF` | the retired `λ* = ηp/2`, input-law blind | uniform floors regardless of the stated law |
| `T_LEVEL` | the level-valued ladder law of `Z13-P1` | thresholds `η·p2·5/16` and `η·(p2·5/16 + p1/2)`; class choice from those thresholds |
| `T_DECLARED` | Bayesian decision theory / bounded-optimal argmin of the declared cost (Z6 `T02..T08`) | argmin of `E(k) + λk` over `T_GMI_IC1`'s predicted profile — registered as the **observational-equivalence control**: it must disagree with `T_GMI_IC1` on `0` cases, and the benchmark must report that as `NON_DISCRIMINATING`, never as a win |
| `T_MDL` | Rissanen two-part code | selects `argmin_k [ machine bits(k) + Σ_m ceil(log2 C(N, N·floor(k, m))) ]` with `machine bits(k) = 3·(1 + k)·2^(k+1)` and `N = 32`; ignores `η`, `λ` |
| `T_OCCAM_HARD` | lexicographic (fewest resources, then error) | always level `0`; `ABSTAIN` on frontier and thresholds |
| `T_SRM` | structural risk minimisation with a fixed price | `argmin_k Σ_m p_m·floor(k, m) + k/4`; ignores `η`, `λ` |
| `T_SATISFICE` | Simon's satisficing | the cheapest level with `Σ_m p_m·floor(k, m) ≤ 1/4`; `ABSTAIN` on thresholds |
| `T_ABSTAIN` | always abstains | control: must score `0` hits and `0` misses |
| `T_NULL_k` | `200` seeded random theories | each field drawn uniformly from the field's output space; the null the true result must beat |

`T_HALF`, `T_LEVEL`, `T_MDL`, `T_OCCAM_HARD`, `T_SRM`, `T_SATISFICE` all use
`T_GMI_IC1`'s floor predictions where they need a profile; what differs is the
law they apply to it. `T_HALF` alone uses uniform floors everywhere.

## 4. Scoring (row 8), defined before any score exists

All scores are exact rationals.

- **Class choice (architecture class)**: per `(case, λ)` cell, `HIT` iff the
  predicted set equals the true argmin set; `MISS` otherwise; `ABSTAIN`
  separately. Score `= hits / (hits + misses)`; abstention rate `= abstains / cells`.
- **Capability profile**: per `(case, k)` cell, covered iff the truth lies in the
  predicted point/interval; sharpness `= 1 − width/η` (a point has sharpness `1`;
  the full range `[0, η]` has sharpness `0` and is flagged `VACUOUS` — a vacuous
  interval is never counted as covered).
- **Thresholds**: per marginal cell, `HIT` iff exact equality (point) or covered
  (interval), with sharpness as above; on a case whose true marginal is `0`
  (no transition) a positive point prediction is a `MISS`.
- **Resource frontier**: `HIT` iff the predicted vertex set equals the true one.
- **Failure modes**: per `(case, k)`, `HIT` iff the predicted channel set equals
  the true one.
- **Calibration**: for each declared `γ`, `coverage(γ)` = covered / declared
  among non-vacuous interval and point predictions at that `γ` (points carry
  `γ = 1`); calibration error `= max_γ |coverage(γ) − γ|`; a theory is
  `CALIBRATED` iff every `γ` it uses has `coverage(γ) ≥ γ`.
- **Composite**: reported as the raw tuple of the six scores; no weighting is
  registered, so no single number is claimed.

## 5. Two routes, hostiles, null

Route B may not import Route A; it rebuilds the case list from the rules of §2,
recomputes every hidden truth by a different enumeration (full output tables
rather than per-address majority), re-reads the emitted prediction records and
re-scores them with its own scorer. Agreement is by exact equality of every score.

Hostiles, each with an `applicable` flag that FAILS the run if the hostile does
not move the quantity it perturbs: `HZ1` a planted truth-reading theory
(`T_PEEK`) is caught by the scrambled-truth control; `HZ2` a record missing a
required field is rejected; `HZ3` a scorer counting `ABSTAIN` as `HIT` is caught
by `T_ABSTAIN` scoring above `0`; `HZ4` a vacuous interval counted as covered is
caught by the `VACUOUS` flag; `HZ5` a tampered generation rule changes the
case-set `sha256`; `HZ6` a wrong seed preimage fails the commitment check;
`HZ7` a drifted empirical-stream blob fails the pin; `HZ8` a theory declaring
`γ = 1` with coverage below `1` is reported `MISCALIBRATED` (planted: `T_LEVEL`
on `C1_LADDER`).

Null: the `200` `T_NULL_k` theories; the true result must beat the best null on
every one of class choice, thresholds, frontier and failure modes. No-alarm case:
`T_DECLARED` vs `T_GMI_IC1` must be reported `NON_DISCRIMINATING` with `0`
disagreements, and the scrambled-truth control must put `T_GMI_IC1` at or below
the best null.

## 6. Predictions frozen now

- `B1` `T_GMI_IC1` reaches class-choice score `1` on `C1`, `C2`, `C3`, `C6(a)`
  and on every `C5` case whose law is `UNIFORM`, `IID`, or `PERIOD2` on the
  two-level type; on ladder cases with a non-uniform law it abstains where its
  delay-2 interval leaves the verdict open, and every non-abstained cell is a `HIT`.
- `B2` on `C4` the empirical pair-Bayes error equals the enumerated stateless
  floor in every `(stream, m)` cell (`9/9`), and the `b = 1` delay-2 interval
  covers the enumerated floor in `3/3` streams.
- `B3` `T_HALF` misses thresholds on every `C2` case with `q ≠ 1/2` and every
  `C3` case with `A ≠ 2`; `T_LEVEL` misses the upper threshold on every `C1`
  case with `p2 > 0` (`108` of `135`) and is `MISCALIBRATED`.
- `B4` `T_DECLARED` disagrees with `T_GMI_IC1` on `0` cases.
- `B5` `T_MDL`, `T_SRM`, `T_SATISFICE`, `T_OCCAM_HARD` each disagree with the
  truth on a non-empty subset of `C1 ∪ C2` class choices, and each of the four is
  beaten by `T_GMI_IC1` on class choice.
- `B6` every `T_NULL_k` scores strictly below `T_GMI_IC1` on class choice,
  thresholds, frontier and failure modes.

A miss on any of `B1`–`B6` goes to `FAILED_PREDICTION_REGISTER_V1.json` and is
not repaired into a hit by this lane.

## 7. The exact issue rows this package may reconcile

Section Z lives in issue comment `5684819296`. Verbatim rows of
`### Z11 — Intelligence Morphology Benchmark`:

```
- [ ] Design a benchmark whose target is theory prediction, not merely model accuracy.
- [ ] Each case must require predictions of morphology, capability profile, transition threshold(s), resource frontier and failure mode(s).
- [ ] Include synthetic exact worlds with known ground truth.
- [ ] Include realistic workloads.
- [ ] Include hidden test ecologies.
- [ ] Include negative controls and theory-discrimination cases.
- [ ] Publish benchmark-generation rules before hidden outcomes.
- [ ] Define quantitative scoring for morphology, capability, thresholds, failures and calibration.
- [ ] Benchmark GMI against strongest competing theories.
```

Scope statement for row 4, fixed now: `realistic workloads` is discharged by
**empirically sourced, non-synthetic input streams** from pinned real files
(`C4_EMPIRICAL_STREAM`, and the `EMPIRICAL` law inside `C5_HIDDEN`). It is
**not** real-system deployment with measured CPU/GPU/wall-time/memory/I/O/energy,
which is `### Z10` and remains open; the forbidden promotion below records that.

**No neighboring row is earned here.** No `### Z6`, `### Z8`, `### Z10`,
`### Z12` or `### Z13` row is touched.

## 8. Forbidden promotions

```
EMPIRICAL_STREAM_WORKLOAD_PRESENTED_AS_REAL_SYSTEM_DEPLOYMENT
Z10_ROWS_CLOSED_BY_THIS_PACKAGE
BENCHMARK_SCORE_PRESENTED_AS_MODEL_ACCURACY
THEORY_GIVEN_ACCESS_TO_HIDDEN_TRUTH
OBSERVATIONAL_EQUIVALENCE_REPORTED_AS_A_WIN
ABSTENTION_COUNTED_AS_AGREEMENT
VACUOUS_INTERVAL_COUNTED_AS_COVERAGE
COMPOSITE_SCORE_WITH_UNREGISTERED_WEIGHTS
RESULTS_EXTENDED_BEYOND_L4_TWO_SYMBOL_OR_ALPHABET_4_SCOPE
HIDDEN_CASES_REDRAWN_AFTER_A_SCORE_WAS_SEEN
Z6_ROWS_RE_EARNED_HERE
```
