# Z11 named results — IMB-v1

Scope is fixed by `FREEZE_V1.md` (+ `FREEZE_V1_AMENDMENT_1.md`): `519` generated
cases in six classes over the three-mode ladder (`L = 4`, `b ∈ {0,1,2}`, window
`{2,3}`) and the two-level delay-1 population (binary, and alphabet `A ∈ {2,3,4}`),
under `UNIFORM`, `IID(q)`, `PERIOD2` and `EMPIRICAL(stream, offset)` input laws;
nine registered theories plus `200` seeded null theories; exact rational scoring.
Both routes agree on every score of every theory and every truth field of every
case. The scored object is always a **theory** (a pure function of the public
specification); no trained model exists anywhere in IMB-v1.

---

## `IMB-1` — the benchmark scores theory prediction, and every case demands all five fields

**Statement.** Each of the `519` cases carries a hidden truth computed by
exhaustive enumeration — profile `E(k)`, transition thresholds (marginals),
resource frontier, selected architecture class at every price, failure-mode set
per level — and a prediction record is accepted only if it carries all five
fields keyed exactly by the case's levels and prices; a record missing a field
is rejected and scored as a MISS on every cell (`HZ2`: `519/519` rejected, class
choice `0`, abstentions `0`). `T_ABSTAIN` scores `0` hits and `0` misses on every
field, so abstention is never counted as agreement (`HZ3` detected).

**Quantifiers.** All `519` cases, all nine registered theories, all `200` nulls.
**Assumptions.** Row-2 schema of `FREEZE_V1.md` §1; the six scoring definitions of §4.
**Dependencies.** `CASES_V1.json` (enumerated truths); `PREDICTIONS_V1.json`; both route receipts.
**Falsifiers.** A record accepted with a missing field; `T_ABSTAIN` with a non-zero hit or miss count; a scored quantity that depends on any model output.
**Strongest parents.** Preregistered theory competition (`gmi-833-z-z6-discrimination-v1` `DS-1`..`DS-6`); the exact scoring vocabulary of `gmi-833-z-z12-prediction-scoring-v1`; benchmark design with hidden test sets and published generation rules (Nosek et al. 2018 preregistration, doi:10.1073/pnas.1708274114).
**Forbidden extrapolations.** `BENCHMARK_SCORE_PRESENTED_AS_MODEL_ACCURACY`; `ABSTENTION_COUNTED_AS_AGREEMENT`.

---

## `IMB-2` — exact synthetic worlds, empirical-stream workloads and hidden ecologies all have enumerated ground truth

**Statement.** Ground truth is enumerated for `41` distinct `(universe, law)`
pairs: at `b = 2` all `65536` next-state tables reduce to `2910` distinct address
signatures (route A) and every `b = 2` floor is proved `0` by a shift-register
witness (route B); at `b ≤ 1` route B enumerates all `256` explicit machines per
mode. `C4_EMPIRICAL_STREAM` uses the empirical 4-bit-window law of three pinned
real files (`README.md`, `LICENSE`, `z12_prediction_scoring_v1.py`; blob shas
recomputed and checked, `HZ7` catches a one-byte drift). On those streams the
empirical pair-Bayes error equals the enumerated stateless floor in `9/9`
`(stream, m)` cells (e.g. `README.md`: `m=1` `60333/129754`, `m=2` `59413/129754`;
`LICENSE`: `26023/60574`, `39034/90861`) and the enumerated `b = 1` delay-2 floor
(`34945/129754`, `8414/30287`, `99223/369802`) lies in the frozen interval
`[0, R0(0,2)]` in `3/3` streams (`B2` HIT). `C5_HIDDEN` holds `60` cases drawn by
`random.Random(secret)` with `sha256(secret)` committed in the freeze and the
preimage revealed only in the executor commit (`HZ6`: a wrong preimage fails).

**Quantifiers.** All `41` laws; all `60` hidden cases; the three pinned streams.
**Assumptions.** Bit order MSB-first, windows sliding by one bit; the hidden draw protocol is the published one and is replayed by route B to the same case-set `sha256`.
**Dependencies.** The three pinned blobs; the sha256 commitment of `FREEZE_V1.md` §2; the enumerations of both routes.
**Falsifiers.** A `b = 2` witness with non-zero error under some law; a stream whose pair-Bayes error differs from the enumerated floor; a hidden case outside the §2 ranges.
**Strongest parents.** The Z13 three-mode ladder floors (`gmi-833-z-z13-adjudication-v1` `ZA-1`); the two-level floor `R0(q) = min(q, 1−q)` and `1 − 1/A` (`gmi-833-z-z1-master-principle-v1` `IC-1b`, `IC-1c`); commitment schemes for hidden test data (hash commitments).
**Forbidden extrapolations.** `EMPIRICAL_STREAM_WORKLOAD_PRESENTED_AS_REAL_SYSTEM_DEPLOYMENT`; `Z10_ROWS_CLOSED_BY_THIS_PACKAGE`; `HIDDEN_CASES_REDRAWN_AFTER_A_SCORE_WAS_SEEN`.

---

## `IMB-3` — negative controls and discrimination cases are in the benchmark

**Statement.** The `9` flat ecologies `p = (1, 0, 0)` have profile `E ≡ 0`,
every marginal `0`, frontier `{0}`; `T_GMI_IC1` scores `1` on them (`225/225`
cells) and any positive threshold there is a MISS. The scrambled-truth control
(`C6(b)`) pairs each case with the truth of another case in its `(class,
universe)` group; the frozen all-cell form alarms on `8` of `9` registered
theories including the provably clean `T_GMI_IC1` (`9901/11380`), i.e. it has no
specificity, and under `FREEZE_V1_AMENDMENT_1.md` the informative-cell form
governs: `1536` cells on which the scrambled and real truths differ, where
`T_GMI_IC1` scores `0`, the best null `9/32`, and a planted truth reader `1`
(`HZ1` detected under both forms). `C7_DISCRIMINATION` is derived: `517/519`
cases carry at least two non-abstaining theories that disagree on class choice;
per-pair counts are reported (`T_GMI_IC1|T_HALF` `210`, `|T_LEVEL` `107`,
`|T_MDL` `495`, `|T_OCCAM_HARD` `449`, `|T_SRM` `447`, `|T_SATISFICE` `464`).

**The recorded false alarms.** On the informative cells `T_MDL` (`151/384`) and
`T_OCCAM_HARD` (`133/384`) exceed the best null. Both are price-blind pure
functions of the public specification (one class choice per case) and cannot
read any truth; their score is the base rate of their fixed choice among the
scrambled truths, not leakage. They are recorded as
`FALSE_ALARM_ON_CLEAN_THEORY`; harness leakage itself is excluded by
`T_PEEK ≡ T_NULL_0` under the honest harness. The control's specificity is
therefore limited to price-sensitive theories, and that limit is published.

**Quantifiers.** All `519` cases; all registered theories.
**Assumptions.** The pairing of the amendment; the null is the `200` `T_NULL_k`.
**Dependencies.** `FREEZE_V1_AMENDMENT_1.md`; `IMB-1`; the `T_PEEK` fallback proof in the receipt.
**Falsifiers.** A flat ecology with a non-`{0}` frontier; a truth reader scoring below `1` on the informative cells; `T_GMI_IC1` above the null there.
**Strongest parents.** Negative-control and permutation-test logic (label shuffling as a leakage detector); `DS-6` observational equivalence.
**Forbidden extrapolations.** `THEORY_GIVEN_ACCESS_TO_HIDDEN_TRUTH`; nothing is claimed about the control's power against theories not registered here.

---

## `IMB-4` — the scoring is quantitative and exact on all six axes

**Statement.** Class choice: `HIT` iff predicted set `=` true argmin set;
`166` two-level tie cells have truth `{0,1}` and `T_GMI_IC1` predicts `{0,1}` on
all of them. Profile: coverage with sharpness `1 − width/η`, a full-range
interval flagged `VACUOUS` and never covered (`HZ4`: `1250/1250` flagged,
`0` covered, `0` declared for calibration). Thresholds: exact-point or covered
interval. Frontier and failure modes: set equality. Calibration: per-`γ`
coverage among declared non-vacuous predictions; `T_LEVEL` declares `γ = 1` on
`C1` with coverage `567/675 = 21/25` and is reported `MISCALIBRATED` (`HZ8`).
The composite is the raw six-tuple; no weights are registered.

**Quantifiers.** Every cell of every record.
**Assumptions.** §4 of the freeze verbatim.
**Dependencies.** `IMB-1`; the scorer of each route; the calibration table of the receipt.
**Falsifiers.** A vacuous interval counted as covered; a calibrated verdict with some `coverage(γ) < γ`; a weighted composite anywhere in the receipt.
**Strongest parents.** Conformal/set-valued prediction coverage (Vovk, Gammerman & Shafer 2005, doi:10.1007/b106715); reliability/calibration (Dawid 1982, doi:10.1080/01621459.1982.10477856); the `Z12` exact scoring instrument.
**Forbidden extrapolations.** `VACUOUS_INTERVAL_COUNTED_AS_COVERAGE`; `COMPOSITE_SCORE_WITH_UNREGISTERED_WEIGHTS`.

---

## `IMB-5` — GMI against the competitors, and the observational-equivalence control

**Statement.** `T_GMI_IC1` scores `1` on class choice (`11380` hits, `0`
misses, `155` licensed abstentions of `11535` cells — all on ladder cases with a
non-uniform law where its delay-2 interval leaves the verdict open), `1` on
thresholds (`731/731`), `1` on frontier (`519/519`), `1` on failure modes
(`1250/1250`), profile coverage `1250/1250`, `CALIBRATED`. `T_DECLARED` (the
declared-cost argmin) emits byte-identical records and disagrees on `0` cases:
reported `NON_DISCRIMINATING`, never a win (`B4`). The competitors: `T_HALF`
class choice `2111/2307`, thresholds `418/731`, frontier `511/519`,
`MISCALIBRATED`; `T_LEVEL` `11311/11535`, thresholds `513/731`, `MISCALIBRATED`;
`T_MDL` `3471/11535`; `T_OCCAM_HARD` `8341/11535`; `T_SRM` `7819/11535`;
`T_SATISFICE` `7320/11535`. Each of the four non-GMI model selection principles
disagrees with the truth on a non-empty subset of `C1 ∪ C2` (`5532`, `2133`,
`2683`, `2943` of `8100` cells) and is beaten by `T_GMI_IC1` (`B5`). The best of
`200` nulls scores `3071/11535`, `20/731`, `157/519`, `27/125` on the four fields
(`B6`); route B's own independent `200`-null family is likewise beaten.

**Quantifiers.** All cases, all theories, both null families.
**Assumptions.** The competitor definitions of `FREEZE_V1.md` §3, with the executor choices listed in the receipt.
**Dependencies.** `IMB-2`, `IMB-4`; both null families; `DS-6` of `gmi-833-z-z6-discrimination-v1`.
**Falsifiers.** A competitor with a class-choice score `≥ T_GMI_IC1`; a `T_DECLARED` disagreement; a null at or above `T_GMI_IC1` on any of the four fields.
**Strongest parents.** Rissanen MDL (doi:10.1016/0005-1098(78)90005-5); Vapnik SRM; Simon satisficing (doi:10.2307/1884852); Occam's razor as lexicographic simplicity; bounded-optimal argmin of the declared cost (Z6 `T02..T08`).
**Forbidden extrapolations.** `OBSERVATIONAL_EQUIVALENCE_REPORTED_AS_A_WIN`; `RESULTS_EXTENDED_BEYOND_L4_TWO_SYMBOL_OR_ALPHABET_4_SCOPE`.

---

## `IMB-6` — one frozen prediction misses at the `p = 0` boundary and is published

**Statement.** `B3` froze "`T_HALF` misses thresholds on every `C2` case with
`q ≠ 1/2` and every `C3` case with `A ≠ 2`". The count is `144/162` and `48/54`:
the `18` and `6` cases with `p = 0` have true threshold `0` and `T_HALF` predicts
`0` there. The corrected quantifier (`p > 0`: `144/144`, `48/48`) is derived after
the run and is recorded, not scored. The other two `B3` clauses hold (`T_LEVEL`
misses the upper threshold on `108/108` `C1` cases with `p2 > 0` and is
`MISCALIBRATED`). `B1`, `B2`, `B4`, `B5`, `B6` are HITs.

**Falsifiers.** A `B3` miss missing from `FAILED_PREDICTION_REGISTER_V1.json`; a register number not reproducible from the receipt.
**Quantifiers.** The six frozen predictions `B1`–`B6`.
**Assumptions.** The freeze wording is scored literally; no post-hoc quantifier is scored.
**Dependencies.** `IMB-5`; the receipt's `frozen_predictions` block; the register.
**Strongest parents.** The published-failed-prediction discipline of `gmi-833-z-z13-adjudication-v1` and `gmi-833-z-z5-critical-phenomena-v1` `CP-6`; preregistration (Nosek et al. 2018).
**Forbidden extrapolations.** `FROZEN_PREDICTION_REPAIRED_INTO_A_HIT_AFTER_A_MISS`.

---

## `IMB-7` — the instruments

Eight hostiles, each carrying an `applicable` flag that fails the run when the
hostile does not move its quantity; all applicable, all detected: `HZ1` planted
truth reader (`1` on both control forms vs null `204/769` / `9/32`), `HZ2`
missing field, `HZ3` abstain-as-hit (`T_ABSTAIN` would score `1`), `HZ4` vacuous
interval, `HZ5` tampered generation rule changes the case-set `sha256`, `HZ6`
wrong preimage, `HZ7` drifted blob, `HZ8` `γ = 1` with coverage `21/25`. Null:
`200` seeded theories per route. No-alarm cases: `T_DECLARED` reported
`NON_DISCRIMINATING` with `0` disagreements; `T_GMI_IC1` scores `0 ≤ 9/32` on the
governing scrambled control.

**Falsifiers.** An inapplicable or undetected hostile; a route disagreement on any score.
**Quantifiers.** All eight hostiles, both null families, both no-alarm cases.
**Assumptions.** Each hostile perturbs exactly one quantity and the `applicable` flag measures that quantity.
**Dependencies.** `IMB-1`..`IMB-5`; both receipts.
**Strongest parents.** The `applicable`-flag and vacuity discipline of `gmi-833-z-z12-prediction-scoring-v1` and `gmi-833-z-z7-impossibility-v1` (`IM-4`, `IM-7`).
**Forbidden extrapolations.** Nothing is claimed about hostiles not listed.
