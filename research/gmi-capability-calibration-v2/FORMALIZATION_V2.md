# Exact finite-population capability calibration — formalization V2

Issue #766; successor to #764 (`ASSAY_DEFECT_NONDETERMINATE_SAMPLING_FRAME`); parent ledger #602 Section M.

Pre-implementation authority: `FREEZE_V2.md`, commit `dc36946f3f76d7b955c5c4cdbd802353d843ce12`. Outcome-free determinate frame was committed before the audit sample; OS-random sample custody commit `3f2403bb183f045114af40df865860b0bf947333` predates the scorer/result artifacts.

## Claim ceiling

```text
EXACT_FINITE_POPULATION_CAPABILITY_ERROR_CALIBRATION_AT_REGISTERED_DETERMINATE_FRAME
```

This is a calibration of the **finite-population error rate among determinate predictions** under a registered uniform-without-replacement audit. It is not calibration of per-example probabilities, an iid superpopulation, future domains, or the abstention region.

## 1. Selective finite-population object

The pinned F4 predictor emits one of

```text
0, 1, CANNOT_IDENTIFY
```

for each registered capability coordinate. V2 first constructs the sampling frame using only the predictor's determinate/abstain output on the fresh candidate grid `{-3,-2,2,3}^5`. No capability oracle is called during frame construction.

For each coordinate, the frozen determinate frame contains exactly `N=64` of the `1024` candidate-grid cells, so candidate-grid determinate coverage is

```text
64/1024 = 1/16.
```

All four coordinate frames happen to coincide on this grid: the monotone development envelopes identify only joint all-negative and joint all-positive extreme regions. This is a limitation of the finite predictor/frame geometry, **not** an independence claim.

The target statistical quantity for coordinate `j` is therefore

```text
K_j / N,
```

where `K_j` is the fixed number of incorrect determinate predictions in that frozen 64-cell frame.

## 2. Sampling law [parent-owned]

Fix one coordinate and condition on its frozen frame. Let the population contain exactly `K` error cells among `N`. Draw a subset of size `n` uniformly without replacement, and let `X` be the number of sampled errors.

Then exactly

```text
P_K(X=x)
 = C(K,x) C(N-K,n-x) / C(N,n),
```

for feasible `x`, because the numerator counts size-`n` subsets containing exactly `x` of the `K` errors and `n-x` of the `N-K` correct cells, while the denominator counts all size-`n` subsets. No iid or replacement model is involved.

Define

```text
F_K(x) = P_K(X<=x).
```

## 3. CAL-1 — exact one-sided finite-population upper bound [P1]

For confidence failure budget `delta in (0,1)`, define

```text
U_delta(x)
 = max { K in {0,...,N} : F_K(x) > delta }.
```

The set is nonempty for every observed `x>=0`, because when `K=0`, `X=0` surely and hence `F_0(x)=1>delta`.

### Theorem CAL-1

For every fixed finite population/error count `K_0`, if `X` is the registered uniform-without-replacement sample error count, then

```text
P_{K_0}( K_0 <= U_delta(X) ) >= 1-delta.
```

Equivalently, `U_delta(X)/N` is an exact one-sided `(1-delta)` upper confidence bound on the fixed finite-population error rate `K_0/N`.

### Proof

If `U_delta(X) < K_0`, then `K_0` was not admitted in the defining set for `U_delta(X)`. Therefore

```text
F_{K_0}(X) <= delta.
```

For any discrete random variable with CDF `F`,

```text
P(F(X) <= delta) <= delta.
```

To see this directly, the set of integers `x` satisfying `F(x)<=delta` is an initial segment because a CDF is nondecreasing. If it is empty the probability is zero; otherwise let `x*` be its largest element. Then

```text
P(F(X)<=delta) = P(X<=x*) = F(x*) <= delta.
```

Hence

```text
P_{K_0}(U_delta(X)<K_0)
 <= P_{K_0}(F_{K_0}(X)<=delta)
 <= delta,
```

which proves the result. QED.

No monotonicity assumption in `K`, normal approximation, binomial approximation, or asymptotic argument is needed.

## 4. CAL-2 — four-coordinate simultaneous calibration [P1]

For coordinate `j`, let

```text
E_j = { K_j <= U_j(X_j) }.
```

CAL-1 gives

```text
P(E_j^c) <= delta_j.
```

With four coordinates and frozen allocation

```text
delta_j = 1/80,
sum_j delta_j = 1/20,
```

Boole's union bound gives

```text
P(intersection_j E_j)
 >= 1 - sum_j P(E_j^c)
 >= 19/20.
```

No cross-coordinate independence is assumed.

### Dependence hostile

On 80 equiprobable atoms, give each coordinate-bound failure event a different singleton atom. Each marginal success event has probability `79/80`, but joint success is exactly

```text
76/80 = 19/20.
```

The union bound is tight. An unjustified independence product would be

```text
(79/80)^4 = 38950081/40960000,
```

which is different from `19/20`. Thus the campaign guarantee is deliberately union-bound based rather than product based.

## 5. CAL-3 — selective-risk semantics [P1 contract]

The calibrated population is the frozen determinate frame, not the entire candidate grid. If the predictor abstains on a cell, that cell is absent from both the determinate error numerator and determinate denominator.

Therefore every calibration report must carry both:

```text
candidate-grid determinate coverage
finite-population determinate error bound.
```

A predictor can have excellent conditional error calibration and poor coverage. V2 exhibits exactly why that distinction matters: determinate coverage on the registered candidate grid is only `1/16`.

The synthetic abstention control removes every seventh ordered frame prediction. It leaves 54 determinate of 64 and 10 abstentions, so reported determinate coverage becomes

```text
54/64 = 27/32.
```

The abstentions are not counted as successes.

## 6. Frozen numerical inversion [P1/P2]

V2 freezes

```text
N=64
n=48
delta=1/80
epsilon=1/20.
```

For zero sampled errors,

```text
F_K(0)
 = C(N-K,n)/C(N,n)
```

when `N-K>=n`, and zero otherwise.

Exact computation gives

```text
F_3(0) > 1/80
F_4(0) <= 1/80,
```

hence

```text
U_(1/80)(0)=3.
```

Thus the exact upper error-rate bound is

```text
3/64 = 0.046875 < 0.05 = 1/20.
```

This value is generated by the general inversion routine, not hard-coded.

## 7. Independent exhaustive theorem certificate [P2]

The production routine computes the hypergeometric PMF from combinations. An independent checker uses a dynamic programme that counts all size-`n` subsets by their number of error items, without calling the production PMF formula.

For every

```text
1 <= N <= 20,
1 <= n <= N,
0 <= K <= N,
all feasible x,
```

the checker verifies the production PMF against the independently counted subset frequency. It then checks CAL-1 for each exact delta in

```text
{1/2, 1/5, 1/20, 1/80}.
```

The registered exhaustive totals are:

```text
10,395 PMF cells
12,320 (N,n,K,delta) coverage cases.
```

Every case must pass under normal Python and `python -O`.

## 8. Frozen sample result [P3 finite-population certificate]

The determinate frame was committed before sampling. Then 48 distinct ids per coordinate were drawn with `secrets.SystemRandom().sample`, sorted and committed in `AUDIT_SAMPLE_V2.json` before the oracle scorer/result existed.

On the frozen samples, each of the four capability coordinates has

```text
X_j = 0 sampled errors.
```

Therefore every coordinate receives the same preregistered exact certificate:

```text
U_j = 3
upper finite-population error rate = 3/64
terminal = CALIBRATED_AT_REGISTERED_DETERMINATE_FRAME.
```

The simultaneous four-coordinate coverage lower bound is `19/20` under CAL-2.

Only after fixing these sample-derived certificates, the executable performs the registered full-frame oracle census. The true fixed error count is `0/64` for each coordinate, so all four realized certificates cover the full-frame truth. The census validates this realized finite study; it did not choose the sample, threshold, or upper bound.

## 9. Evidence-sensitivity control

The frozen complement hostile replaces each determinate prediction `p` by `1-p` while keeping the same frame and same sample identities. Because the principal frame predictions are exact on this finite frame, the complement has

```text
48/48 sampled errors
64/64 full-frame errors
U=64
upper error rate=1
```

for every coordinate, so all four fail the `epsilon=1/20` calibration gate. The positive terminal is therefore not independent of observed error evidence.

## 10. Custody and fail-closed boundaries

The implementation rejects or CI invalidates:

- a determinate-frame count other than 64;
- frame content not reproduced by the predictor-only builder;
- predictor blob drift from `937b91f6a3787ff04c2b5209c81d249518406859`;
- oracle/correctness fields in the frame manifest;
- sample ids outside the frame, duplicates, wrong sample size, noncanonical sample order;
- outcome/correctness fields in the sample manifest;
- scorer/result artifacts existing at the sample-custody commit;
- result drift between normal Python and `python -O`.

The V1 failed sampling frame remains visible in #764 and is not rewritten into a positive predecessor.

## 11. Parent subtraction

No statistical novelty is claimed. The theorem is standard exact hypergeometric inversion for sampling without replacement, adjacent to classical exact finite-population bounds (including Wright and Wang) and modern without-replacement confidence sequences (Waudby-Smith & Ramdas). Selective classification/risk-control and conformal risk-control work own broader selective-risk methodology.

The repository residual is narrower: an outcome-free determinate-frame construction around the already-merged F4 predictor, freeze-before-outcome sample custody, exact finite-population certification, and explicit abstention/coverage accounting.

## 12. Falsifiers and non-implications

Falsifiers at the registered scope include:

- any exhaustive `N<=20` case violating CAL-1;
- a sample not uniformly drawn without replacement from the frozen frame;
- a principal coordinate whose reported upper rate exceeds `epsilon` but is labeled calibrated;
- a full-frame truth `K_j>U_j` in the registered post-certificate census;
- a complemented coordinate still passing the frozen gate;
- an abstention counted as a correct determinate prediction;
- predictor/frame/sample custody drift.

This result does **not** imply:

```text
PER_EXAMPLE_PROBABILITIES_CALIBRATED
IID_GENERALIZATION
CALIBRATION_ON_ABSTAINED_CELLS
FUTURE_DOMAIN_CALIBRATION
REAL_WORLD_CAPABILITY_CALIBRATION
UNIVERSAL_G6
COMPLETE_GMI
```

If merged with dedicated CI green, the only master-ledger consequence is the #602 Section-M row `Calibrate capability-prediction uncertainty` at this declared finite determinate-frame scope.
