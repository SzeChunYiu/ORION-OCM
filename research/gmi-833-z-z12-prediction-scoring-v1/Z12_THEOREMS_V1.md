# Z12 named results

All quantities are exact rationals computed with `fractions.Fraction`; no float
appears in any claim. Every result below is produced by two materially
independent routes: route A (streaming per-record accumulation, closed-form
morphology class optima) and route B (integer key aggregation over
`(|A|, |S|, |T|, |S int T|)`, morphology class optima by exhaustive enumeration
of all 65,552 registered candidates). Route B imports nothing from route A.

**Scope shared by every result.** The two pinned populations only:
`POP_M` = 60 morphology records (20 low endpoints, 20 high endpoints, 20 boundary
records) derived from `gmi-833-heldout-20-transitions-v1/RESULT_V1.json`;
`POP_K` = 480 capability records from `FROZEN_PREDICTIONS_V1/V4.json` joined to
`external_values` in `gmi-833-capability-predictor-evaluation-v1/RESULT_V1.json`.
**Forbidden extrapolation shared by every result:** nothing here says the scored
predictions are *true* beyond their own frozen scope, and nothing here is a claim
about any prediction not in these two populations.

---

## `Z12-BND` — bounded-prediction typing is total

**Statement.** Every record in `POP_M` and `POP_K` types as exactly one of
`POINT`, `SET`, `ABSTAIN_FULL`, `REFUTE_WORLD`, each carrying the registered
uniform predictive law `q_i(a) = 1/|S_i|` on `S_i`. Refusals: `0/540`.
`POP_M`: 40 `POINT`, 20 `ABSTAIN_FULL`. `POP_K`: 56 `POINT`, 412 `SET`,
12 `REFUTE_WORLD`.

**Quantifiers.** For all records in the two pinned populations.
**Assumptions.** The registered alphabet of a `POP_K` universe is the union of
every `identified_set` and `external_values` appearing in that universe's own
records; `POP_M`'s alphabet is `{PERSISTENT_STATE, STATELESS}`.
**Falsifiers.** Any record typing as `REFUSED`; any record with a value outside
its alphabet; a `REFUTE_WORLD` record whose truth set is non-empty.
**Strongest parents.** Conformal prediction supplies set-valued predictors with
coverage guarantees (Vovk, Gammerman & Shafer, *Algorithmic Learning in a Random
World*, Springer 2005, doi:10.1007/b106715); selective prediction supplies the
abstain option (Chow, *IEEE Trans. Inform. Theory* 16(1):41-46, 1970,
doi:10.1109/TIT.1970.1054406; El-Yaniv & Wiener, JMLR 11:1605-1641, 2010). This
result claims no new theory of set-valued prediction; it claims that the
programme's own frozen predictions are exhaustively typed under such a law.
**Forbidden extrapolation.** `BOUNDED_TYPING_IMPLIES_PREDICTION_CORRECTNESS`.

## `Z12-VAC` — no vacuous prediction on either population

**Statement.** A record is vacuous iff `S_i = A` and `T_i != A`. Vacuity count is
`0` on `POP_M` (of 60 mass-scored) and `0` on `POP_K` (of 468 mass-scored), rate
`0/1` on both. The 20 `POP_M` full-alphabet predictions are **licensed
abstentions**, not vacuity: their truth set is also the full alphabet, because at
`lambda = lambda*` the two morphology class optima are exactly equal.

**Why the distinction is load-bearing.** On a binary morphology alphabet a tie
prediction *is* the full set, so a vacuity test that only looks at `|S_i| = |A|`
would flag 20 correct abstentions. The truth-conditioned definition separates
them.
**Falsifiers.** Any record with `S_i = A` and `T_i != A`.
**Hostile that fires.** `H1_VACUOUS` (`S_i := A` everywhere) moves the rate
`0/1 -> 2/3` and mean set size `4/3 -> 2/1`, and is detected.
**Forbidden extrapolation.** `NON_VACUITY_IMPLIES_INFORMATIVENESS`.

## `Z12-COV` — exact set coverage is 1 on both populations

**Statement.** `#{i : T_i subset-or-equal S_i} / N` is `60/60 = 1/1` on `POP_M`
and `480/480 = 1/1` on `POP_K`.

**Parent credit.** `gmi-833-capability-predictor-evaluation-v1` already reports
exact coverage for its own population under its own 32-pattern fault law (result
`KE-6`: `hits 234240 / pairs 234240`). The residual here is a coverage definition
uniform across a morphology population and a capability population, re-derived
from the pinned blobs by a source-separated route.
**Falsifiers.** Any record with `T_i` not contained in `S_i`.
**Forbidden extrapolation.** `CALIBRATION_BEYOND_PINNED_POPULATIONS`.

## `Z12-SHP` — exact sharpness

**Statement.** Mean prediction-set size is `4/3` on `POP_M` (max `2`, mean excess
over truth `0/1`) and `40/13` on `POP_K` (max `8`, mean excess `19/117`).

Mean excess `0/1` on `POP_M` is the strong form: every morphology prediction set
is exactly the true optimal set, never larger.
**Falsifiers.** A recomputation disagreeing in either route.
**Forbidden extrapolation.** `SHARPNESS_IMPLIES_OPTIMAL_INFORMATIVENESS`.

## `Z12-CAL` and `CAL-LEM` — element-level calibration error is zero

**Statement (`Z12-CAL`).** Under the registered predictive law and target law,
element-level calibration error is `0/1` in **every** bin of both populations:
`POP_M` bins `|S| = 1` (40 pairs, claim `1/1`) and `|S| = 2` (40 pairs, claim
`1/2`); `POP_K` bins `|S| = 1..8` (56, 400, 156, 352, 80, 72, 196, 128 pairs,
claims `1/1 .. 1/8`). Maximum error `0/1` on both.

**Statement (`CAL-LEM`).** For a record with `T_i subset-or-equal S_i`, the
record's `|S_i|` pairs contribute total realized mass exactly `1` against total
claimed mass exactly `1`. Hence a bin all of whose records cover has calibration
error exactly `0`, and a bin containing a miscovering record has strictly
positive error.
**Proof.** Realized mass of pair `(i,a)` is `1/|T_i|` for `a in S_i int T_i` and
`0` otherwise, so the record's realized total is `|S_i int T_i|/|T_i|`, which is
`1` exactly when `T_i subset-or-equal S_i`. Claimed total is `|S_i|·(1/|S_i|) = 1`.
Subtracting and dividing by the bin's pair count gives the statement. The
converse direction is the strictness: a miscovering record contributes realized
total `< 1` while its claimed total is still `1`, and no other record in the bin
can contribute more than `1`, so the bin mean is strictly below `q`. QED
**Validation before use.** The test plants a covering population (error `0/1`)
and a miscovering population (error `> 0` localized to the miscovering bin,
`0/1` in the clean bin). A checker that cries wolf on clean data is worse than a
miss, so the no-alarm branch is asserted, not assumed.
**Retained v1 quantity.** The record-level mass gap defined in `FREEZE_V1.md`
before amendment 2 is retained as `CAL_1A_record_level_max_mass_gap`: `1/2` on
`POP_M`, `7/8` on `POP_K`. It is a structural offset between a per-element claim
and a set-level realization, **not** a calibration error, and is reported so that
nothing measured is silently dropped.
**Hostile that fires.** `H4_MISCALIBRATED` (claiming `1/(|S|-1)`) moves the
maximum error `0/1 -> 6/7` on `POP_K` and is detected; the honest claim rule on
the same population gives exactly `0`.
**Strongest parents.** Reliability-diagram calibration (Murphy & Winkler,
*J. R. Statist. Soc. C* 26(1):41-47, 1977, doi:10.2307/2346866; Dawid, *JASA*
77(379):605-610, 1982, doi:10.1080/01621459.1982.10477856). `CAL-LEM` is not a
new calibration theory; it is the exact finite identity that makes the instrument
valid on set-valued predictions.
**Forbidden extrapolation.** `ZERO_CALIBRATION_ERROR_IMPLIES_UNIVERSAL_RELIABILITY`.

## `Z12-BRI` — exact Brier, log loss declined

**Statement.** Mean multiclass Brier score against the registered uniform target
law is `0/1` on `POP_M` and `47/1404` on `POP_K`.

**Log loss is declined**, invoking the row's own `or justified alternatives`
disjunction: `log` has no exact rational value and this programme admits no float
in a claim. The declination was registered in `FREEZE_V1.md` before any score
existed.
**Strongest parent.** Brier, *Monthly Weather Review* 78(1):1-3, 1950,
doi:10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2. Proper-scoring-rule theory
is entirely parent-owned (Gneiting & Raftery, *JASA* 102(477):359-378, 2007,
doi:10.1198/016214506000001437).
**Forbidden extrapolation.** `LOG_LOSS_SCORED`.

## `Z12-REG` — zero regret from morphology selection, and the instrument can pay

**Statement.** Under the registered selection rule (lexicographically least
element of the prediction set) and the frozen objective
`J = eta((1-p)e_now + p·e_delay) + lambda·state_bits`, total regret over all 60
`POP_M` records is exactly `0/1`, and total **worst-case** regret (paying the
worst element of every prediction set) is also exactly `0/1`.

The worst-case figure is the stronger one: even an adversarial reading of the 20
tie predictions costs nothing, because at `lambda = lambda*` both class optima
equal `lambda*`.
**The instrument is not trivially zero.** `H6_REGRET_BLIND` replaces the
selection rule by a constant `STATELESS` choice and pays total regret `15/2`
(mean `1/8`) on the same 60 records — so a wrong morphology selection is
detected and priced, and the zero is a property of the predictions, not of the
scorer.
**Independent route.** Route B obtains every class optimum by exhaustively
enumerating all 65,552 registered candidates (16 stateless output tables plus
256x256 one-bit transducers) with its own semantics, and reproduces the parent's
recorded controls exactly: census `65552`, `146` distinct risk/state summaries,
stateless minimum delayed error `1/2`, `40/40` endpoint classifications,
`20` exact boundary ties.
**Strongest parents.** Regret as a decision-theoretic loss (Savage, *JASA*
46(253):55-67, 1951, doi:10.1080/01621459.1951.10500768); the morphology
predictions, the boundary law and the two search procedures are owned entirely by
`gmi-833-heldout-20-transitions-v1` (#901) and are not re-earned here.
**Forbidden extrapolation.** `REAL_SYSTEM_PREDICTION_VALIDATED`,
`UNIVERSAL_MORPHOLOGY_PREDICTION`.

## `Z12-ABS` — abstention is required, exercised and sound

**Statement.** A record is unidentifiable iff `|T_i| > 1`. `POP_M` has exactly 20
unidentifiable records (the boundary ties) and abstains on exactly those 20
(`20/60 = 1/3`), with `0` soundness violations. `POP_K` has 396 unidentifiable
records and `0` soundness violations. Abstention is non-trivial: `POP_M` also
contains 40 records that must **not** abstain, and does not abstain on them.

**Parent credit.** `gmi-833-capability-abstention-v1` owns an abstention theorem
for the capability predictor. The residual here is an executable
abstention-soundness gate over a morphology population whose unidentifiable
records are exactly enumerated rather than asserted.
**Hostile that fires.** `H3_NEVER_ABSTAIN` collapses every set to its least
element, moving the abstention rate `1/3 -> 0/1` and producing `20` soundness
violations, and is detected.
**Forbidden extrapolation.** `ABSTENTION_POLICY_OPTIMALITY`.

## `Z12-WID` — post-hoc widening is refused, not scored

**Statement.** Every scored set carries
`sha256(json.dumps(sorted(S_i), separators=(",",":"), sort_keys=True))`
recomputed from the pinned blob at load time. A record whose set is not
byte-derivable from its pinned parent blob is rejected and fails the run; the
penalty is refusal, so widening cannot buy coverage or calibration.

**The penalty is load-bearing, and shown to be.** `H2_WIDENER` enlarges exactly
one `POP_K` set by one element: mean set size moves by exactly `1/468`
(predicted `1/468`, observed `1/468`) and the provenance check flags exactly
`1` record, with `0` flagged on the untouched population. `H5_TRUTH_LEAK`
replaces every set by the truth set — the sharpest and most covering predictor
possible — and is refused by the same check (`> 0` flagged), with `0` flagged on
the untouched population.
**Falsifiers.** A widened record that is not flagged; a clean record that is.
**Forbidden extrapolation.** `PROVENANCE_IMPLIES_PREDICTION_TRUTH`.

## `Z12-NULL` — the frozen predictor beats 200 randomized controls

**Statement.** For each of 200 seeds `random.Random(s)`, `s in [1000, 1200)`, a
control predictor draws every `POP_M` set uniformly from the three non-empty
subsets of `{PERSISTENT_STATE, STATELESS}`. On the registered lexicographic
composite `(coverage desc, mean|S| asc, mean regret asc)` the frozen predictor
beats **200/200**; `0/200` match or beat it. Frozen composite:
coverage `1/1`, mean set size `4/3`, mean regret `0/1`.
