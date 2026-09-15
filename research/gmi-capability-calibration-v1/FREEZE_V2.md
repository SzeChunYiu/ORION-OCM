# Freeze V2 — repaired exact finite-population capability calibration

Issue: #764. Parent ledger: #602 Section M, row `Calibrate capability-prediction uncertainty`.

V1 is permanently retained as `CANNOT_EXECUTE_FROZEN_SAMPLE_DETERMINATE_POPULATION_TOO_SMALL`: its frozen 128-cell population had only 10 determinate cells per coordinate, so a 64-cell determinate sample could not be drawn. No V1 sample or oracle scoring occurred. V2 repairs only that pre-outcome population-construction defect; it does not change the statistical threshold, confidence budget or sample size after seeing outcomes.

**Pre-V2-outcome authority.** At this commit there is no V2 audit population manifest, no V2 sample manifest, no capability oracle score, no V2 calibration receipt and no V2 workflow result.

## Pinned predictor

Use the same merged architecture-name-free F4 predictor pinned by V1:

```text
base commit 7e1103f1a5d1f453e7fd305e23824eacd61f7992
research/gmi-capability-predictor-dev-v1/dev_predictor_v1.py
blob 937b91f6a3787ff04c2b5209c81d249518406859
research/gmi-capability-predictor-dev-v1/DEV_PREDICTOR_PROTOCOL_V1.json
blob f98338e5606b4b9505ee720ad3b57adbf6d4552f
```

Coordinates:

```text
memory_exact
planning_exact
coordination_exact
verified_tool_exact
```

The only predictor-visible uncertainty state used in population construction is whether `predict_one` returns binary `0/1` or `CANNOT_IDENTIFY`. No held oracle outcome/correctness/error bit may be used.

## V2 raw candidate universe

Define

```text
R = {-3,-2,-1,0,1,2,3}^5 \ {-1,0,1}^5
```

in axis order

```text
memory_margin
planning_margin
communication_margin
routing_margin
verification_margin.
```

Thus every candidate is outside the original development cube and

```text
|R| = 7^5 - 3^5 = 16564.
```

For each capability coordinate `j`, run only the pinned F4 predictor on every `q in R` and define

```text
D_j = {q in R : predict_one(q,j) is 0 or 1}.
```

This is a predictor-selection event, not oracle scoring. The V2 implementation must reproduce the following predictor-only cardinalities exactly before any audit sample exists:

```text
|D_memory_exact|        = 4132
|D_planning_exact|      = 4382
|D_coordination_exact|  = 4132
|D_verified_tool_exact| = 4382.
```

A mismatch is a custody/source failure and stops the study.

## Frozen V2 finite audit populations

For each coordinate `j`, define

```text
key_j(q) = SHA256("T602-M5-AUDIT-V2|" + j + "|" + comma_join(q)).hexdigest().
```

Sort `D_j` by `(key_j(q), q)` and take the first `N=128` points. The opaque specimen id is

```text
ACP2_ + first_16_hex_chars(key_j(q)).
```

The V2 population manifest is coordinate-indexed and may contain only:

```text
coordinate
specimen_id
five integer margins
raw candidate count
predictor-determinate-pool count
```

It must contain no capability oracle outcomes, correctness labels, error bits, score fields, sampled-error counts or result terminals. Predictor determinate/abstain status may be summarized only as the already frozen pool cardinality; the binary prediction itself is recomputed later by the scorer and is not stored in the population manifest.

The statistical population for coordinate `j` is exactly its fixed 128 selected determinate points. Selection is frozen before oracle outcomes and is part of the claim scope; no generalization to the excluded/abstained raw universe is implied.

Report separately, as selection/coverage context rather than calibration success, the predictor-determinate fractions

```text
4132/16564  for memory_exact and coordination_exact
4382/16564  for planning_exact and verified_tool_exact.
```

## Frozen V2 sample protocol

Only after `AUDIT_POPULATION_V2.json` is committed, for each coordinate independently:

- sample exactly `n=64` distinct specimen ids from its fixed 128-cell population;
- use `secrets.SystemRandom().sample`, backed by fresh OS entropy;
- do not use or compute capability oracle outcomes before committing the realized sample ids;
- commit the realized ids to `AUDIT_SAMPLE_V2.json`;
- do not retain a reproducible PRNG seed as an alternative authority; the realized id list is the custody authority.

The sample manifest must contain only coordinate, selected specimen ids, population digest/identity and sampling-method metadata. It must not contain predictor values, oracle values, correctness/error fields or certificates.

No V2 sample id may change after the sample commit.

## Statistical theorem — unchanged from V1

For one coordinate, condition on its fixed finite determinate population of size `N=128` with fixed unknown total prediction-error count `K`. Uniform sampling without replacement of `n=64` cells gives

```text
X ~ Hypergeometric(N,K,n)
P_K(X=x) = C(K,x) C(N-K,n-x) / C(N,n).
```

Define

```text
F_K(x) = P_K(X<=x)
U_delta(x) = max {K in {0,...,N}: F_K(x) > delta}.
```

Target theorem:

```text
for every fixed K in {0,...,N},
P_K(K <= U_delta(X)) >= 1-delta.
```

Proof obligation: on `K > U_delta(X)`, definition implies `F_K(X) <= delta`; for any discrete random variable with CDF `F`, `P(F(X) <= delta) <= delta`. Therefore undercoverage probability is at most `delta`. The implementation must provide a complete exact proof/certificate route and an independent finite enumeration, not rely on this prose alone.

No iid, replacement, Bernoulli-superpopulation or asymptotic assumption is permitted.

## Simultaneous four-coordinate calibration — unchanged

Freeze

```text
delta_total = 1/20
delta_j = 1/80 for each of four coordinates.
```

Boole's union bound alone gives

```text
P(all four K_j <= U_j) >= 1 - 4/80 = 19/20.
```

No independence among coordinate samples, coordinate errors or coverage events is assumed or required.

## Certification gate — unchanged

Freeze

```text
epsilon = 1/20.
```

For each coordinate:

```text
CALIBRATED_AT_REGISTERED_FINITE_POPULATION
```

iff

```text
U_j(X_j)/128 <= 1/20.
```

otherwise

```text
CANNOT_CERTIFY_ERROR_RATE.
```

If a future source/predictor change makes the V2 population construction unable to produce 128 determinate cells, terminal is

```text
CANNOT_CALIBRATE_NO_DETERMINATE_POPULATION.
```

Frozen numerical control remains

```text
N=128, n=64, delta=1/80, X=0
U_delta(0)=6
upper error rate = 6/128 = 3/64 < 1/20.
```

The code must derive `6`; hard-coding the result is forbidden.

## Prospective success rule

The principal V2 audit succeeds at this registered finite scope only if all four coordinates:

1. reproduce the frozen predictor-only determinate-pool cardinality before sampling;
2. have a committed 128-cell outcome-free population and 64-cell outcome-free sample;
3. pass all sample-custody checks;
4. after sample commitment, have exact sampled error count `X_j` producing `U_j/128 <= 1/20`;
5. retain simultaneous campaign coverage at least `19/20` by union bound;
6. after the certificate is immutable, pass a full-population oracle census with fixed true error count `K_j <= U_j`.

A failed coordinate is retained. No sample, threshold, population, `delta`, `epsilon` or error definition may be changed in response.

## Frozen negative controls

### NC-1 completely corrupted determinate predictor

On the same frozen V2 sample, flip every binary F4 prediction (`0↔1`) for a research-only corrupted arm. Keep abstentions as abstentions. This guarantees every sampled determinate point is an error, so the calibration gate must return `CANNOT_CERTIFY_ERROR_RATE` for all four coordinates. If any corrupted coordinate certifies, the gate is defective.

### NC-2 abstention accounting

On each coordinate's **raw** candidate universe `R`, report determinate versus `CANNOT_IDENTIFY` counts from the pinned predictor. In a separate accounting wrapper over the selected 128-cell population, replace every seventh specimen in specimen-id order with `CANNOT_IDENTIFY`. Those cells must leave both the determinate numerator and denominator; they may not count as correct. This control does not alter the principal predictor or statistical population.

### NC-3 sample tampering

Reject V2 sample manifests with duplicate ids, unknown ids, wrong coordinate, wrong sample size, outcome/correctness/error fields, wrong population digest, or ids outside that coordinate's frozen 128-cell population.

### NC-4 dependence hostile

Use an 80-atom finite space with four distinct singleton calibration-failure events. Each marginal failure probability is `1/80`; the union failure is exactly `4/80`, so the true simultaneous good probability is exactly `76/80 = 19/20`. The product `(79/80)^4` differs. This demonstrates that the registered simultaneous guarantee is the union bound, not an independence product.

## Exhaustive theorem verification

The production hypergeometric PMF/CDF and upper-bound routine must be checked against an independently written exact combinatorial oracle for all

```text
1 <= N <= 20
1 <= n <= N
0 <= K <= N
all feasible x
```

and multiple exact deltas including `1/2`, `1/5`, `1/20`, and `1/80`.

For every `(N,n,K)`, exactly verify

```text
sum_x P_K(X=x) = 1
P_K(K <= U_delta(X)) >= 1-delta.
```

The independent checker must not call the production `U_delta` implementation when establishing the theorem coverage property.

## Full-population verification

Only after the V2 sample manifest is committed and the sample certificate has been computed and frozen may an independent capability oracle be evaluated on all 128 cells per coordinate. The census reports true fixed `K_j` solely to check whether the realized certificate covered it. It may not alter any statistical input, sample identity or threshold.

## Parent subtraction and claim boundary

The mathematics is standard exact hypergeometric inversion / finite-population sampling without replacement plus Bonferroni/Boole simultaneous coverage. Selective prediction/reject-option and risk-control literature own the broader framing. Relevant parents include exact hypergeometric interval literature, survey sampling without replacement, Waudby-Smith & Ramdas on without-replacement confidence sequences, Geifman & El-Yaniv on selective classification, and conformal risk-control work.

This capsule calibrates only **error rate among the four frozen finite determinate populations selected before oracle outcomes**. It does not calibrate per-example probabilities, the raw candidate universe, abstained cells, a superpopulation, future domains, iid generalization, real-world task prevalence or universal G6.

## Claim ceiling

```text
EXACT_FINITE_POPULATION_CAPABILITY_ERROR_CALIBRATION_AT_REGISTERED_SCOPE
```

Forbidden from this issue alone:

```text
PER_EXAMPLE_PROBABILITIES_CALIBRATED
IID_GENERALIZATION
REAL_WORLD_CAPABILITY_CALIBRATION
UNIVERSAL_G6
COMPLETE_GMI
```
