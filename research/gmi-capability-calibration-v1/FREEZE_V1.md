# Freeze V1 — exact finite-population capability-prediction calibration

Issue: #764. Parent ledger: #602 Section M, row `Calibrate capability-prediction uncertainty`.

**Pre-implementation authority.** At this commit there is no audit population manifest, no sample manifest, no calibration executor/scorer, no oracle result, no receipt and no workflow for this capsule.

## Pinned predictor

The predictor under audit is the merged F4 architecture-name-free monotone predictor on `main` at base commit:

```text
7e1103f1a5d1f453e7fd305e23824eacd61f7992
```

Pinned files/blobs:

```text
research/gmi-capability-predictor-dev-v1/dev_predictor_v1.py
blob 937b91f6a3787ff04c2b5209c81d249518406859

research/gmi-capability-predictor-dev-v1/DEV_PREDICTOR_PROTOCOL_V1.json
blob f98338e5606b4b9505ee720ad3b57adbf6d4552f
```

Registered capability coordinates:

```text
memory_exact
planning_exact
coordination_exact
verified_tool_exact
```

F4's existing deterministic/selective identifiability claim is not reinterpreted as probability. This capsule adds a separate finite-population audit.

## Frozen audit population generator

Candidate margin grid:

```text
G = {-3,-2,2,3}^5
```

in axis order

```text
memory_margin
planning_margin
communication_margin
routing_margin
verification_margin
```

so every candidate point is outside the original development cube `{-1,0,1}^5`.

For every tuple `m`, define

```text
key(m) = SHA256("T602-M5-AUDIT-V1|" + comma_join(m)).hexdigest()
```

Sort all `4^5=1024` tuples by `(key(m),m)` and take the first `N=128`. Opaque specimen id is

```text
ACP_ + first_16_hex_chars(key(m)).
```

The population manifest will contain only specimen id and the five integer margins. **It must not contain oracle capability outcomes, correctness labels, error bits or scorer outputs.**

Each capability coordinate uses these same 128 target points as a distinct fixed finite prediction population.

## Frozen sample protocol

For each capability coordinate independently:

- population size `N=128`;
- audit sample size `n=64`;
- draw 64 distinct specimen ids uniformly without replacement using Python `secrets.SystemRandom().sample` backed by OS entropy;
- draw only after the population manifest is committed;
- write the realized ids to `AUDIT_SAMPLE_V1.json`;
- do **not** record or use oracle outcomes before the sample manifest commit;
- the realized sample manifest, not a reproducible PRNG seed, is the custody authority.

The sample manifest must be a strict subset of the registered population, contain no duplicates, and contain no outcome/correctness fields.

No sample identity may be changed after oracle scoring begins.

## Frozen statistical contract

For one capability coordinate, condition on its fixed determinate prediction population of size `N` and let `K` be the fixed but unknown total number of prediction errors. Under the registered uniform-without-replacement audit sample of size `n`, sampled error count `X` has the hypergeometric law

```text
P_K(X=x)
  = C(K,x) C(N-K,n-x) / C(N,n).
```

Define exact lower-tail CDF

```text
F_K(x) = P_K(X<=x)
```

and one-sided upper confidence limit

```text
U_delta(x)
 = max { K in {0,...,N} : F_K(x) > delta }.
```

Frozen theorem target:

```text
for every fixed K in {0,...,N},
P_K( K <= U_delta(X) ) >= 1-delta.
```

No iid, Bernoulli-superpopulation, replacement or asymptotic assumption is allowed.

For four coordinates allocate

```text
delta_total = 1/20
delta_j     = 1/80  for each of four coordinates
```

and combine the four coordinate coverage events only with Boole's union bound:

```text
P(all four K_j <= U_j) >= 1 - 4/80 = 19/20.
```

No coordinate-independence assumption is permitted.

## Frozen certification gate

Per-coordinate registered finite-population error threshold:

```text
epsilon = 1/20.
```

For coordinate `j`, report

```text
CALIBRATED_AT_REGISTERED_FINITE_POPULATION
```

iff

```text
U_j(X_j)/N <= epsilon.
```

Otherwise report

```text
CANNOT_CERTIFY_ERROR_RATE.
```

If a frozen predictor produces zero determinate cells for a coordinate, report

```text
CANNOT_CALIBRATE_NO_DETERMINATE_CELLS.
```

Abstentions are reported as coverage, never counted as correct determinate predictions.

Frozen numerical control:

```text
N=128
n=64
delta_j=1/80
X=0
U_delta(0)=6
upper error rate = 6/128 = 3/64 = 0.046875 < 1/20.
```

The implementation must independently reproduce `U=6`; hard-coding it is forbidden.

## Frozen prospective success rule

The principal F4 audit is considered successful at this registered finite-population scope only if all four capability coordinates:

1. have nonzero determinate coverage;
2. have a valid frozen sample of exactly 64 determinate cells;
3. produce exact hypergeometric upper error rate `<= 1/20`;
4. retain simultaneous campaign confidence at least `19/20` by the declared allocation;
5. are later verified by a full-population census to have true fixed error count `K_j <= U_j` (census verifies the realized certificate after scoring; it may not alter the certificate).

Failure of any coordinate is retained and does not permit changing `n`, `delta`, `epsilon`, population construction or sample identities.

## Frozen negative controls

### NC-1 corrupted predictor

Define a research-only corrupted arm after scoring code exists by flipping the frozen F4 predictor output on every specimen whose opaque id has first hex nibble in `{0,1,2,3}` **when the base predictor is determinate**. This rule is frozen now, before audit ids/outcomes are materialized. It is not an alternative F4 model.

The corrupted arm must use the same audit sample identities as the principal arm. It must not be certified at `epsilon=1/20` for at least one registered capability coordinate. If all four corrupted coordinates still certify, the evidence-sensitivity control fails.

### NC-2 abstention accounting

A synthetic wrapper replacing every 7th determinate prediction (ordered by specimen id) with `CANNOT_IDENTIFY` must reduce reported determinate coverage. Those abstentions must be removed from the error numerator **and denominator** and may not be counted as correct. This is accounting-only and does not alter the principal predictor.

### NC-3 sample tampering

Reject sample manifests with duplicate ids, unknown ids, wrong sample size, outcome/correctness fields, or any sample id not determinate for the audited coordinate.

### NC-4 dependence hostile

Construct four coordinate-calibration failure events on a finite atom space with the declared marginal failure budgets but non-independent joint structure. Verify the simultaneous guarantee uses only the union bound and differs from a product-of-coverages calculation.

## Exhaustive theorem verification

The exact hypergeometric implementation must be checked against an independently written enumeration for every

```text
1 <= N <= 20
1 <= n <= N
0 <= K <= N
all feasible x.
```

For every `(N,n,K)` enumerate all `C(N,n)` samples conceptually through exact combinatorial counts, verify the PMF/CDF, compute `U_delta(X)` for multiple exact deltas, and verify the stated coverage inequality. The checker may use combinatorial counts instead of materializing subsets, but its formula path must be independent of the production bound routine.

## Proof boundaries

This calibrates **finite-population determinate prediction error rate** under uniform sampling without replacement. It does not calibrate per-example probabilities, score reliability curves, a superpopulation, future domains, iid generalization, real-world task prevalence, or G6 universally.

The four finite populations are fixed after population materialization. Statistical randomness is only the audit sample draw.

The full-population census is a post-certificate verification and cannot be used to choose the sample or threshold.

## Strongest parents

The mathematics is parent-owned by exact hypergeometric/finite-population confidence bounds and sampling without replacement. Relevant literature includes Wright (1991), Wang (2015), Waudby-Smith & Ramdas for without-replacement confidence sequences, selective classification/risk-control work, and conformal risk control. Repository novelty is not claimed for the bound.

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
