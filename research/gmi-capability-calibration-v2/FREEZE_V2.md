# Freeze V2 — determinate-frame finite-population capability calibration

Issue: #766. Successor to #764 (`ASSAY_DEFECT_NONDETERMINATE_SAMPLING_FRAME`). Parent ledger: #602 Section M, row `Calibrate capability-prediction uncertainty`.

**Pre-implementation freeze.** At this commit no V2 frame manifest, audit sample, calibration executor, oracle scorer, result receipt or V2 workflow exists.

## 1. V1 negative retained

V1 (#764) sampled from a 128-point target population before checking the predictor's determinate frame. After sample custody, the pinned predictor was found to abstain on 118/128 points per coordinate. V1 was closed without redrawing the sample and receives no #602 credit.

V2 changes only the sampling-frame construction justified by that assay defect: **freeze the determinate prediction frame before random sampling.** No capability correctness/error outcome from V1 is used to choose V2 parameters.

## 2. Pinned predictor

Base repository commit:

```text
7e1103f1a5d1f453e7fd305e23824eacd61f7992
```

Predictor:

```text
research/gmi-capability-predictor-dev-v1/dev_predictor_v1.py
blob 937b91f6a3787ff04c2b5209c81d249518406859
```

Protocol:

```text
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

The predictor output (`0`, `1`, or `CANNOT_IDENTIFY`) may be used to construct V2's sampling frame. The capability oracle may **not** be called before the frame and sample commits.

## 3. Candidate grid and opaque identity

Use all 1024 tuples in

```text
G = {-3,-2,2,3}^5
```

with axes

```text
memory_margin
planning_margin
communication_margin
routing_margin
verification_margin.
```

For tuple `m`, define

```text
key(m)=SHA256("T602-M5B-AUDIT-V2|" + comma_join(m)).hexdigest()
specimen_id="AC2_" + first_16_hex_chars(key(m)).
```

Every candidate is outside the original F4 development cube `{-1,0,1}^5`.

## 4. Determinate sampling frames

For each capability coordinate `j`, evaluate the pinned predictor on all 1024 candidate points **without calling the oracle**. The coordinate frame is exactly the set of candidates for which prediction is integer `0` or `1`; `CANNOT_IDENTIFY` candidates are excluded from the coordinate's error-rate population but counted in candidate-grid coverage.

V2 prospectively expects, based only on the registered V1 assay diagnosis, exactly

```text
N_j = 64
```

determinate cells for each coordinate. The frame builder must independently reproduce this count. Any other count is `CANNOT_CHECK_DETERMINATE_FRAME_DRIFT`; do not adjust N.

The frame manifest must include only:

```text
coordinate
specimen_id
five margins
frozen predictor output 0/1
```

and aggregate candidate-grid/determinate counts. It must contain **no oracle outcome, correctness flag, error bit, risk estimate, or calibration result**.

## 5. Audit sample custody

After the determinate-frame manifest is committed, draw for each coordinate

```text
n=48
```

unique ids from its frozen `N=64` frame using `secrets.SystemRandom().sample` (OS-backed entropy), uniformly without replacement. Commit the realized sorted ids to `AUDIT_SAMPLE_V2.json` before oracle scorer/result code exists.

The realized sample manifest is the custody authority; no PRNG seed is needed or retained. It must contain no outcome/correctness fields.

Any redraw after oracle scoring begins invalidates V2.

## 6. Statistical theorem target

Condition on one coordinate's fixed determinate population of size `N` and fixed unknown total prediction-error count `K`. A uniform sample of `n` cells without replacement gives sampled error count

```text
X ~ Hypergeometric(N,K,n)
```

with exact PMF

```text
P_K(X=x)=C(K,x)C(N-K,n-x)/C(N,n).
```

Let

```text
F_K(x)=P_K(X<=x)
U_delta(x)=max{K in {0,...,N}: F_K(x)>delta}.
```

Prove for every fixed finite population/error configuration:

```text
P_K(K<=U_delta(X)) >= 1-delta.
```

Equivalently, `U_delta(X)/N` is an exact one-sided finite-population upper confidence bound on determinate prediction error rate under the registered sampling design.

No iid, replacement, Bernoulli-superpopulation, asymptotic or model-score-calibration premise is allowed.

## 7. Four-coordinate simultaneous guarantee

Freeze

```text
delta_total = 1/20
delta_j     = 1/80 for each of four coordinates.
```

Use only Boole's union bound:

```text
P(for all j: K_j<=U_j) >= 1-sum_j delta_j = 19/20.
```

No cross-coordinate independence assumption is permitted.

Dependence hostile: on 80 equiprobable atoms, let each of four coordinate-bound failure events be a distinct singleton. Each marginal good event has probability `79/80`, joint good is exactly `76/80=19/20`, while the independence product `(79/80)^4` is different. The union bound is tight.

## 8. Frozen certification threshold

Per coordinate:

```text
epsilon = 1/20.
```

Report

```text
CALIBRATED_AT_REGISTERED_DETERMINATE_FRAME
```

iff

```text
U_delta(X)/64 <= 1/20.
```

Otherwise report `CANNOT_CERTIFY_ERROR_RATE`.

Frozen numerical control:

```text
N=64
n=48
delta=1/80
X=0
U_delta(0)=3
U/N = 3/64 = 0.046875 < 1/20.
```

This number must be independently reproduced, never hard-coded.

## 9. Prospective principal success rule

The principal predictor supports the registered calibration claim only if **all four** coordinates:

1. reproduce `N=64` determinate cells from predictor-only frame construction;
2. have a valid pre-oracle sample of 48 unique frame ids;
3. have exact finite-population upper error bound `<=1/20`;
4. jointly retain campaign coverage lower bound `19/20` under the registered allocation;
5. after the certificate is fixed, a full-frame oracle census verifies true fixed error count `K_j<=U_j`.

Any failing coordinate remains a negative. Do not change N, n, deltas, epsilon, grid or sample.

## 10. Negative controls

### NC-1 complement predictor

On the same frozen frame and same frozen audit ids, replace every determinate principal prediction `p` by `1-p`. This deliberately corrupted arm must fail the `epsilon` certification gate on **all four** coordinates. It is a hostile, not a competitor.

### NC-2 abstention accounting

Order each frame by specimen id and replace every seventh determinate prediction with `CANNOT_IDENTIFY`. Report reduced determinate coverage. Abstentions are excluded from both the error numerator and determinate denominator and are never counted as correct.

### NC-3 sample/frame tampering

Reject duplicate ids, unknown ids, wrong sample sizes, ids outside the coordinate frame, oracle/correctness/error fields in frame/sample manifests, or source-predictor drift.

### NC-4 post-custody mutation

CI must prove the V2 freeze commit predates frame/sample/scorer/result, and the sample-custody commit predates scorer/result. The committed sample file must match byte-for-byte under receipt reproduction.

## 11. Exhaustive theorem checker

Verify the production hypergeometric PMF/CDF and `U_delta` against an independent dynamic-programming subset counter for every

```text
1<=N<=20
1<=n<=N
0<=K<=N
all feasible x
```

for exact deltas

```text
1/2, 1/5, 1/20, 1/80.
```

For every `(N,n,K,delta)`, sum the independent DP probabilities over sampled `x` satisfying `K<=U_delta(x)` and require coverage at least `1-delta`.

## 12. Boundaries

This is finite-population **determinate error-risk calibration**. It is not:

- per-example probability calibration;
- calibration of abstentions as correct predictions;
- iid/superpopulation/future-domain generalization;
- calibration under outcome-conditioned sampling;
- real-world task-prevalence calibration;
- universal G6.

Full-frame census occurs only after the sampled certificate and serves as a verification of the realized coverage claim, not as data for choosing the certificate.

## 13. Parent subtraction

The statistics are parent-owned by exact hypergeometric/finite-population confidence bounds and sampling without replacement (including Wright; Wang; Waudby-Smith & Ramdas), with selective-classification and conformal/risk-control work as adjacent parents. The repository contribution is only the freeze-first adapter/custody discipline for an existing F4 predictor.

## Claim ceiling

```text
EXACT_FINITE_POPULATION_CAPABILITY_ERROR_CALIBRATION_AT_REGISTERED_DETERMINATE_FRAME
```

Forbidden from this issue alone:

```text
PER_EXAMPLE_PROBABILITIES_CALIBRATED
IID_GENERALIZATION
REAL_WORLD_CAPABILITY_CALIBRATION
UNIVERSAL_G6
COMPLETE_GMI
```
