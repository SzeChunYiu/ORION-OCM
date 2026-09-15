# #764 freeze — exact finite-population capability-prediction calibration V1

Date: 2026-09-15. Parent ledger: #602 Section M. Child issue: #764.
Branch base before this file: `7e1103f1a5d1f453e7fd305e23824eacd61f7992`.

This commit is the sole pre-population, pre-sample, pre-scoring authority for this tranche. Before this commit on this branch there is no audit-population manifest, sample manifest, random entropy record, scorer, oracle-result file, calibration result, or dedicated workflow for `gmi-capability-calibration-v1`.

## Claim boundary

Target only:

```text
EXACT_FINITE_POPULATION_CAPABILITY_ERROR_CALIBRATION_AT_REGISTERED_SCOPE
```

This tranche may certify an exact one-sided upper bound on the **fixed finite-population error count/rate among determinate predictions** of the pinned F4 capability predictor, under a frozen uniform sample-without-replacement protocol. It may combine four coordinate certificates by a union bound without independence.

It may not claim per-example predictive probabilities, iid/superpopulation generalization, universal capability calibration, real-world capability calibration, architecture-family universality, G6 universal prediction, or complete GMI.

## Pinned predictor authority

The predictor under audit is the already-merged architecture-name-free monotone F4 predictor at:

```text
research/gmi-capability-predictor-dev-v1/dev_predictor_v1.py
```

Pinned Git blob:

```text
937b91f6a3787ff04c2b5209c81d249518406859
```

Companion authority pins:

```text
DEV_PREDICTOR_PROTOCOL_V1.json  f98338e5606b4b9505ee720ad3b57adbf6d4552f
FORMALIZATION_V1.md             0da7ef60c241ee14eb36ba68a64e831e5e9dfcfd
README.md                        cc4b6c3b41c589122ec3d227382c8d49e61d3366
```

The predictor has registered axes

```text
memory_margin
planning_margin
communication_margin
routing_margin
verification_margin
```

and audited target coordinates

```text
memory_exact
planning_exact
coordination_exact
verified_tool_exact
```

The source predictor's deterministic/selective identifiability claim is not upgraded retroactively. This capsule adds a new finite-population statistical error certificate for a frozen audit population.

## Strongest parents / subtraction

The statistical mathematics is parent-owned:

- simple random sampling without replacement from a finite population;
- the hypergeometric distribution for a fixed unknown number of errors;
- exact one-sided inversion of hypergeometric tests/confidence bounds;
- Boole's inequality for simultaneous multi-coordinate coverage;
- selective-classification risk/coverage separation.

Relevant anchors include Tommy Wright (1991), *Exact Confidence Bounds when Sampling from Small Finite Universes*; Weizhen Wang (2015), *Exact Optimal Confidence Intervals for Hypergeometric Parameters*; Waudby-Smith & Ramdas (NeurIPS 2020), *Confidence sequences for sampling without replacement*; and selective-classification work such as Geifman & El-Yaniv (NeurIPS 2017).

The repository residual is the freeze-first F4 adapter, fresh finite audit population, exact-uniform sample custody, exact-rational inversion, abstention discipline, hostile/corrupted controls, deterministic receipt, and fail-closed reconciliation.

## Frozen constants

For every coordinate `j`:

```text
N = 128                    # frozen determinate audit-population size
n = 64                     # simple random sample size without replacement
delta_total = 1/20
delta_j = 1/80             # four equal coordinate allocations
epsilon = 1/20             # admissible finite-population determinate error rate
```

The four `delta_j` sum exactly to `1/20`, so simultaneous confidence is at least `19/20` by a union bound, with no coordinate-independence premise.

All probability arithmetic in scored evidence must use exact `fractions.Fraction` or exact integer combinatorics; binary floating-point values are not authority.

## Frozen fresh audit-population construction

The development corpus uses only axis values `{-1,0,1}`. Each audit coordinate receives 128 fresh out-of-development points generated without consulting oracle outcomes or sampled results.

The population is formed as exactly 64 canonical positive-side candidates and 64 canonical negative-side candidates for the target's driving margin(s). "Positive-side" and "negative-side" are geometric generator labels only; they are not oracle labels and must never be serialized as truth/prediction outcomes in the population manifest.

Canonical candidate enumeration is lexicographic by the ordered axis tuple

```text
(memory_margin,
 planning_margin,
 communication_margin,
 routing_margin,
 verification_margin).
```

After generating the registered candidate pool for a side, take the first 64 distinct points in canonical tuple order. Every point must contain at least one driving coordinate outside `{-1,0,1}`, making it outside the fitted development grid.

### memory_exact population

Positive-side candidates:

```text
memory_margin in {2,3,4}
all other axes in {-1,0,1}
```

Negative-side candidates:

```text
memory_margin in {-4,-3,-2}
all other axes in {-1,0,1}
```

### coordination_exact population

Positive-side candidates:

```text
communication_margin in {2,3,4}
all other axes in {-1,0,1}
```

Negative-side candidates:

```text
communication_margin in {-4,-3,-2}
all other axes in {-1,0,1}
```

### planning_exact population

Positive-side candidates:

```text
memory_margin in {2,3,4}
planning_margin in {2,3,4}
communication_margin,routing_margin,verification_margin in {-1,0,1}
```

Negative-side candidates:

```text
memory_margin in {-4,-3,-2}
planning_margin in {-1,0,1}
communication_margin,routing_margin,verification_margin in {-1,0,1}
```

### verified_tool_exact population

Positive-side candidates:

```text
routing_margin in {2,3,4}
verification_margin in {2,3,4}
memory_margin,planning_margin,communication_margin in {-1,0,1}
```

Negative-side candidates:

```text
routing_margin in {-4,-3,-2}
verification_margin in {-1,0,1}
memory_margin,planning_margin,communication_margin in {-1,0,1}
```

### Opaque cell identities

Every cell ID is deterministically derived only from the target coordinate and canonical point:

```text
cell_id = "cell_" + sha256(
  target + "\n" + canonical_json(point)
).hexdigest()
```

The population manifest may expose target, cell ID, and the five registered margins needed for predictor execution. It must contain **none** of:

```text
oracle
truth
label
error
correct
prediction
predicted
outcome
capabilities
```

as data fields. The manifest is a covariate/population object, not a scored result.

Required population-manifest checks before sampling:

- exactly 128 unique cells per coordinate;
- exactly four registered coordinates;
- every point is outside the original `{-1,0,1}^5` development grid;
- no duplicate point within a coordinate;
- generator reconstruction is byte-identical;
- no oracle/result fields;
- pinned predictor source/blob identity included only as metadata.

## Frozen sample-custody order

The required commit ordering is strict:

```text
1. FREEZE_V1.md only
2. POPULATION_MANIFEST_V1.json (no oracle outcomes)
3. SAMPLE_MANIFEST_V1.json (sample identities + entropy transcript; no scoring)
4. only then: formalization, scorer, tests, scored receipt, census, CI
```

At commit 3, no scorer, oracle-result file, result receipt, corrupted-control result, or full-population census may exist on the branch.

The dedicated workflow must verify this custody from Git history, not merely trust a prose statement.

## Frozen exact-uniform sampling algorithm

For each coordinate independently, sample exactly `n=64` of its sorted `N=128` cell IDs with equal probability over the `C(128,64)` possible 64-subsets.

A naive `PRNG.sample` is not authority because exact equiprobability over combinations is not established by the API contract. V1 instead freezes a direct exact-uniform rank sampler.

Let

```text
M = C(128,64).
B = 2^256.
q = floor(B/M).
L = q*M.
```

For each coordinate:

1. obtain a fresh 32-byte block from `secrets.token_bytes(32)`;
2. interpret it as a big-endian integer `z in {0,...,B-1}`;
3. if `z >= L`, reject the block, record it in the entropy transcript, and draw another fresh block;
4. for the first accepted block, set `r = z mod M`;
5. unrank exactly the `r`-th 64-subset of the sorted 128 cell IDs in lexicographic combination order;
6. commit the full entropy transcript (hex), accepted block index, accepted rank `r`, population digest, and the 64 sampled cell IDs.

### Exact-uniform proof obligation SU-1

Because the accepted set `{0,...,L-1}` contains exactly `q` representatives of every residue class modulo `M`, conditional on acceptance `r=z mod M` is exactly uniform on `{0,...,M-1}`. Rejection and retry preserve exact uniformity. Bijective combination unranking therefore makes every size-64 subset exactly equiprobable with probability `1/M`.

No independence among the four coordinate samples is required for the later simultaneous confidence theorem. Separate entropy transcripts are nevertheless used operationally and are each replay-validated.

## Frozen hypergeometric model

Fix one coordinate after its determinate audit population is frozen. Let

```text
N = 128
K in {0,...,N}
```

be the fixed but unknown number of erroneous determinate predictions in that finite population.

Under the frozen simple random sample of `n=64` distinct cells without replacement, let `X` be the sampled error count. Then exactly

```text
X ~ Hypergeometric(N,K,n)
```

with

```text
P_K(X=x)
= C(K,x) C(N-K,n-x) / C(N,n)
```

on its feasible support.

Define the lower-tail CDF

```text
F_K(x) = P_K(X <= x).
```

For exact `delta in (0,1)`, define

```text
U_delta(x)
= max { K in {0,...,N} : F_K(x) > delta }.
```

The strict `>` is frozen. For any observable `x>=0`, `K=0` belongs to the set because `F_0(x)=1`, so `U_delta(x)` is well-defined.

## Frozen theorem HC-1 — exact one-sided finite-population bound

For every integers

```text
N>=1,
1<=n<=N,
K in {0,...,N},
```

for a uniform sample without replacement and every `delta in (0,1)`, if `X~Hypergeometric(N,K,n)` and `U_delta` is defined above, then

```text
P_K( K <= U_delta(X) ) >= 1-delta.
```

Equivalently,

```text
P_K( K > U_delta(X) ) <= delta.
```

Therefore `U_delta(X)/N` is an exact conservative one-sided `(1-delta)` upper confidence bound on the fixed finite-population error rate `K/N`.

### Frozen proof route HC-1a

The formalization must prove:

1. for fixed `x`, `F_K(x)` is nonincreasing in `K`; an explicit finite coupling or combinatorial argument is required;
2. if `K > U_delta(x)`, monotonicity and the definition of `U_delta` imply `F_K(x) <= delta`;
3. for any integer-valued random variable with CDF `F`, the random lower-tail value obeys

```text
P(F(X) <= delta) <= delta,
```

proved by taking the largest support point `x_*` whose CDF is `<=delta` (or the empty-event case);
4. combine 2 and 3.

No iid, replacement, asymptotic normality, binomial approximation, or superpopulation premise may appear.

## Frozen numerical control HC-C1

At

```text
N=128,
n=64,
delta=1/80,
X=0,
```

the exact inversion must produce

```text
U_delta(0)=6
```

with boundary witnesses

```text
F_6(0) > 1/80,
F_7(0) <= 1/80.
```

Hence

```text
U/N = 6/128 = 3/64 = 0.046875 < 1/20.
```

This numerical control is a theorem/executor check, not a statement that the future sample will contain zero errors.

## Frozen certification terminals

For one coordinate with determinate population size exactly 128 and valid sample custody:

```text
upper_rate = U_(1/80)(X) / 128.
```

If

```text
upper_rate <= epsilon=1/20,
```

terminal:

```text
CALIBRATED_AT_REGISTERED_FINITE_POPULATION
```

Otherwise:

```text
CANNOT_CERTIFY_ERROR_RATE
```

If the generator/predictor yields fewer than 128 determinate eligible cells, or if a coordinate has no determinate eligible cells, the campaign fails closed and may not silently resample from another population. The no-determinate semantic terminal is

```text
CANNOT_CALIBRATE_NO_DETERMINATE_CELLS.
```

For this frozen manifest the population itself is fixed at 128 candidates; whether the pinned predictor is determinate on every one must be checked only after population/sample custody permits predictor execution. A nondeterminate sampled cell is never a success and invalidates the frozen `N=128 determinate-population` precondition rather than being relabelled correct.

## Frozen theorem HC-2 — four-coordinate simultaneous calibration

For coordinate `j`, let event

```text
E_j = {K_j <= U_(delta_j)(X_j)}.
```

HC-1 gives

```text
P(E_j^c) <= delta_j = 1/80.
```

Without any independence assumption,

```text
P(intersection_j E_j)
>= 1 - sum_j P(E_j^c)
>= 1 - 4/80
= 19/20.
```

Thus the four reported finite-population upper bounds are simultaneously valid with probability at least `19/20` under the registered per-coordinate simple-random-sampling design.

The result is simultaneous validity of four finite-population error-count bounds. It is not a claim that the four prediction-error processes, samples, or confidence events are independent.

## Frozen dependence hostile HC-H1

The tests must include two coordinate-confidence failure events of probability `1/4` that are disjoint on four equiprobable atoms. Their individual success probabilities are `3/4`, true simultaneous success is `1/2`, while an unjustified independence product is `9/16`. The valid union lower bound is `1/2` and is attained.

An overlapping-failure control must also show that the union bound may be conservative.

## Frozen exhaustive exact certificate HC-C2

For every

```text
1 <= N <= 20,
1 <= n <= N,
0 <= K <= N,
```

and every feasible sample error count `x`, compare the closed-form exact hypergeometric probability/CDF and inversion against an **independent finite enumeration of sample subsets**.

The independent enumerator must not call the hypergeometric PMF/CDF implementation under test. It must count size-`n` subsets of a canonical `N`-item population whose first `K` items are marked errors, using exact integer counts.

The certificate must verify:

- PMF equality for every feasible `(N,n,K,x)`;
- CDF equality for every feasible `(N,n,K,x)`;
- CDF monotonicity in `K` for each `(N,n,x)`;
- HC-1 coverage for every `(N,n,K,delta)` in a frozen exact delta grid;
- inversion boundary correctness.

Frozen delta grid:

```text
{1/2, 1/3, 1/4, 1/5, 1/10, 1/20, 1/80}.
```

The receipt must expose total checked tuple counts and zero-failure counts. An implementation may cache raw subset-enumeration counts for runtime efficiency, but the independent counting path and closed-form path must remain logically separate.

## Frozen selective-prediction semantics HC-3

Calibration is conditional on the **frozen determinate audit population**. Report for every coordinate:

```text
eligible_population_count
determinate_population_count
abstention_population_count
sample_size
sampled_error_count
upper_error_count
upper_error_rate
terminal
```

Abstentions are never counted as correct predictions, never lower `X`, and never enter the denominator of a determinate-error rate. If the frozen generator does not deliver the preregistered 128 determinate cells for a coordinate, V1 cannot substitute a post-hoc easier denominator.

This is risk/coverage separation: error among determinate predictions and determinate coverage are different quantities.

## Frozen corrupted-predictor control HC-H2

After sample custody is committed, the scorer must include a deliberately corrupted control that flips every binary determinate prediction on the same sampled cells. This is a test-only negative control, not a replacement predictor.

The corrupted control must yield a certificate that fails the frozen `epsilon=1/20` gate. A calibration implementation that reports the same passing terminal for the pinned predictor and this maximally corrupted control is falsified.

## Frozen full-population census rule

Oracle scoring of all 128 cells per coordinate is forbidden until after:

1. population manifest commit;
2. sample manifest/entropy custody commit;
3. scored sampled certificate is computed from the frozen sample.

Only then may `CENSUS_V1.json` reveal all finite-population errors. The census is an independent verification of whether the realized fixed truth `K_j` lies below the already-computed confidence bound. It may not alter the sample, `delta`, `epsilon`, population, or bound.

The canonical result must distinguish:

```text
certificate_covered_fixed_truth = (K_j <= U_j)
```

from the probabilistic guarantee that was established by the sampling design before truth was fully revealed.

## Frozen malformed/custody hostiles

The executor/workflow must fail closed on at least:

- population file containing an oracle/truth/error/prediction field;
- population count not exactly 128 per coordinate;
- duplicate cell IDs or duplicate coordinate points;
- cell ID not matching canonical target/point hash;
- a point inside the original development grid;
- wrong predictor blob/source pin;
- sample not exactly 64 IDs per coordinate;
- duplicate sampled IDs;
- sampled ID outside its coordinate population;
- sample population digest mismatch;
- entropy transcript that does not exactly replay the recorded combination rank/sample;
- accepted entropy block outside the rejection threshold;
- changed `N,n,delta_j,epsilon` after sample custody;
- scorer/result/census artifact existing in the sample-custody commit;
- post-outcome sample mutation;
- abstention counted as a success;
- binary float replacing exact probability authority;
- normal and `python -O` canonical receipts differing byte-for-byte.

## Frozen result schema

`RESULT_V1.json` must include at least:

```text
schema
issue=764
parent_issue=602
freeze_commit
population_commit
sample_custody_commit
pinned_predictor_path/blob
claim_ceiling
N,n,delta_total,delta_j,epsilon
per-coordinate population/determinate/abstention counts
per-coordinate sample error X
per-coordinate U_delta(X)
per-coordinate exact upper rate and terminal
simultaneous lower confidence 19/20
HC-C1 numerical boundary witnesses
HC-C2 exhaustive certificate counts/failures
HC-H1 dependence hostile
HC-H2 corrupted-control terminal
sample replay/custody status
census fixed K and certificate-covered flag
forbidden claims
```

No per-example probability field is permitted.

## Frozen falsifiers

This tranche is falsified if any of the following occurs:

- freeze is not an ancestor of population/sample/scorer/result artifacts;
- population or sample custody occurs after oracle-result code/data already exists on the branch;
- any coordinate sample is not exactly uniform over 64-subsets by the frozen rank protocol;
- exact finite enumeration disagrees with the closed-form hypergeometric calculation;
- any exhaustive HC-1 coverage case falls below `1-delta`;
- the frozen `N=128,n=64,delta=1/80,x=0` control does not give `U=6`;
- a coordinate product-coverage shortcut is reported without a dependence proof;
- an abstention is counted as correct or used to lower the sampled error count;
- the corrupted predictor passes the `epsilon=1/20` calibration gate;
- a sample or threshold mutates after outcomes are available;
- full-population census changes the precomputed certificate;
- normal and `python -O` receipts differ;
- the result claims iid, per-example probabilities, real-world calibration, or universal capability prediction.

## Required completion evidence

Completion requires, in this order after this freeze commit:

1. commit `POPULATION_MANIFEST_V1.json` with no oracle outcome data;
2. draw exact-uniform samples with fresh OS entropy and commit `SAMPLE_MANIFEST_V1.json` plus transcript, before scorer/result/census code exists;
3. add `FORMALIZATION_V1.md` with explicit quantifiers, HC-1/HC-2/SU-1 proofs, parent subtraction, assumptions, nearest counterexamples, and claim ceiling;
4. add exact scorer/executor and adversarial tests;
5. generate sampled certificates, then only afterward reveal a full-population census;
6. produce deterministic canonical `RESULT_V1.json` and receipt reproducer;
7. run normal and `python -O` exact/adversarial tests with byte-identical receipt;
8. dedicated CI must verify Git-history custody, source pins, manifests, exhaustive certificate, scorer, census noninterference, and receipt reproduction;
9. merge before reconciling only #764 and the single #602 row `Calibrate capability-prediction uncertainty`.

No neighboring #602 row or complete-theory terminal is earned by this tranche alone.
