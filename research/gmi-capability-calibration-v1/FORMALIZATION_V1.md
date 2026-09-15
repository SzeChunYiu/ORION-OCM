# Exact finite-population capability-prediction calibration — formalization V1

Issue #764; parent ledger #602 Section M. Pre-population authority is `FREEZE_V1.md` at commit `f46d2b3930b980f85d2d0143cba20b39f396b396`. Outcome-blind population authority is commit `68d5101b26bb095546030e1e37a994f74e62fe15`; exact-uniform sample custody is commit `f528ddcc183d28ae5cd91a98a9c1a860ddd3ba8d`. Both precede this scorer/formalization/result layer.

## Claim boundary and proof classes

Claim ceiling:

```text
EXACT_FINITE_POPULATION_CAPABILITY_ERROR_CALIBRATION_AT_REGISTERED_SCOPE
```

The audited object is the pinned architecture-name-free F4 monotone predictor at Git blob `937b91f6a3787ff04c2b5209c81d249518406859`. Four binary coordinates are audited separately: `memory_exact`, `planning_exact`, `coordination_exact`, and `verified_tool_exact`.

The claim is a finite-population **determinate prediction error-rate certificate** under a simple random sample without replacement. It is not a calibrated probability for an individual prediction, not iid/superpopulation generalization, not real-world capability calibration, and not universal G6 closure.

Evidence classes:

- SU-1, HC-1, HC-2 and the selective-risk statements below are P1 finite mathematical results;
- the frozen 128-cell populations, entropy/sample replay, exact-rational inversion, `N<=20` census, corrupted predictor, and full fixed-population census are P2 exact-computation evidence;
- there is no P4 empirical claim in this capsule.

Strongest parents own the mathematics: simple random sampling without replacement, the hypergeometric law, exact inversion of finite-population tests, Boole's inequality, and selective-classification risk/coverage separation. The repository residual is the freeze-first F4 adapter, custody, exact replay and fail-closed evidence discipline.

## Registered finite population

For each coordinate `j`, the frozen generator determines exactly `N=128` opaque cells. The population manifest contains no oracle outcome. A cell is determined only by the target coordinate and five integer margins; the opaque ID is SHA-256 of that registered covariate object. Every point is outside the development grid `{-1,0,1}^5` in at least one driving coordinate.

The scorer reconstructs all cells and checks 128 distinct points/IDs per coordinate, exact coordinate and all-population ID digests, absence of scored/oracle fields, and the pinned predictor Git-blob identity. The later full-population census cannot change the population, sample, epsilon or delta.

## SU-1 — exact-uniform sample by rejection and combination rank [P1]

Fix one coordinate and sort its 128 cell IDs. There are

```text
M = C(128,64)
```

possible size-64 subsets. Let `B=2^256`, `q=floor(B/M)`, and `L=qM`. Draw a fresh 256-bit integer `Z` from a 32-byte OS-entropy block. Reject when `Z>=L`; otherwise set `R=Z mod M` and return the `R`-th lexicographic 64-combination.

### Theorem SU-1

Conditional on acceptance, `R` is uniform on `{0,...,M-1}`. Rejection and retry preserve exact uniformity, and combination unranking maps ranks bijectively to size-64 subsets. Therefore each sample subset has exactly probability `1/M`.

### Proof

The accepted integers are `{0,...,qM-1}`. For every residue `r`, exactly

```text
r, r+M, ..., r+(q-1)M
```

are accepted and have residue `r mod M`. Thus `P(R=r | accepted)=q/(qM)=1/M`. A rejected draw is discarded before a fresh draw, so retry does not bias residues. Lexicographic unranking is a bijection. QED.

The executable replay checks every entropy block, rejection boundary, accepted integer, rank, unranking and final sample identities. Duplicate, mutated, malformed or non-replaying samples fail closed.

## Hypergeometric sampling law [P1]

Fix a coordinate after its 128 determinate predictions and fixed error indicators exist. Let `K` be the unknown number of errors. Under SU-1, the number `X` of sampled errors satisfies exactly

```text
P_K(X=x) = C(K,x) C(N-K,n-x) / C(N,n),
```

because a size-`n` sample with `x` errors chooses `x` of the `K` error cells and `n-x` of the other cells. No replacement, iid sequence or superpopulation is introduced.

Define

```text
F_K(x) = P_K(X<=x)
U_delta(x) = max {K in {0,...,N}: F_K(x) > delta}.
```

The strict `>` is part of the preregistration.

## HC-1 — exact one-sided finite-population upper bound [P1]

For every integer `N>=1`, `1<=n<=N`, fixed `K in {0,...,N}`, and exact `0<delta<1`, if `X~Hypergeometric(N,K,n)`, then

```text
P_K(K <= U_delta(X)) >= 1-delta.
```

Equivalently `U_delta(X)/N` is a conservative one-sided `(1-delta)` upper confidence bound on the fixed finite-population error rate `K/N`.

### Lemma 1: `F_K(x)` is nonincreasing in `K`

Couple a population with `K` errors and one with `K+1` errors by sampling the same uniformly chosen subset and changing one fixed success cell to error. Pointwise,

```text
X_(K+1) = X_K + I{changed cell selected} >= X_K.
```

Hence `{X_(K+1)<=x} subseteq {X_K<=x}` and `F_(K+1)(x)<=F_K(x)`.

### Lemma 2: inversion implication

If `K>U_delta(x)`, then `F_K(x)<=delta`. Otherwise K itself would belong to the defining set for `U_delta(x)`, contradicting maximality.

### Lemma 3: integer-valued CDF self-bound

For any integer-valued variable with CDF `F`,

```text
P(F(X)<=delta) <= delta.
```

If the event is nonempty, let `x*` be the largest support point with `F(x*)<=delta`. Then `{F(X)<=delta}={X<=x*}` and its probability is `F(x*)<=delta`.

### HC-1 proof

On `{K>U_delta(X)}`, Lemma 2 gives `F_K(X)<=delta`. Therefore

```text
P_K(K>U_delta(X))
<= P_K(F_K(X)<=delta)
<= delta
```

by Lemma 3. Taking complements proves HC-1. QED.

Nearest false generalizations: arbitrary/nonuniform sample selection, post-outcome population selection, a binomial approximation substituted for the registered hypergeometric law, and any claim of future iid generalization.

## Frozen numerical control [P1/P2]

At `N=128,n=64,delta=1/80,x=0`, exact arithmetic gives

```text
F_6(0) = 3599/260350 > 1/80
F_7(0) = 1711/260350 <= 1/80
```

and therefore

```text
U_(1/80)(0)=6,
U/N=6/128=3/64 < epsilon=1/20.
```

For comparison, `x=1` gives `U=9`, so `9/128>1/20`: the calibration gate is not hard-coded to pass.

## HC-2 — simultaneous four-coordinate guarantee [P1]

Let

```text
E_j = {K_j <= U_(delta_j)(X_j)},  delta_j=1/80.
```

HC-1 gives `P(E_j^c)<=1/80` for each coordinate. Without assuming any independence,

```text
P(intersection_j E_j)
>= 1 - sum_j P(E_j^c)
>= 1 - 4/80
= 19/20.
```

This is simultaneous validity of four finite-population error-count bounds, not evidence that coordinates, samples or confidence events are independent.

### Dependence hostile

On four equiprobable atoms, let failure A occur only on atom 0 and failure B only on atom 1. Each success probability is `3/4`, but simultaneous success is `1/2`. The unjustified independence product is `9/16`, which is too high. The valid union lower bound is `1/2` and is attained. If both failures instead overlap on atom 0, simultaneous success is `3/4`, showing the same union bound can be conservative.

## Selective-prediction semantics [P1 contract]

The registered risk is among the frozen determinate population. An abstention is not an error-free success and never lowers `X`. The preregistration requires 128 determinate eligible cells per coordinate. If the pinned predictor abstains on any frozen population cell, the V1 denominator precondition fails and the terminal is

```text
CANNOT_CALIBRATE_NO_DETERMINATE_CELLS.
```

No easier denominator may be chosen after seeing outcomes. Determinate coverage and determinate error risk are distinct quantities.

## HC-H2 — corrupted-predictor negative control [P2]

After sample custody, a test-only control flips every binary determinate prediction on the same sampled cells. If the pinned predictor makes `x` errors, the flipped predictor makes `n-x` errors. The exact same inversion and epsilon gate are applied. A method returning the same passing certificate for the audited and maximally corrupted predictors is falsified.

In the registered execution the audited predictor has zero sampled errors while the corrupted control has 64. The latter gives `U=128`, upper rate 1, and terminal `CANNOT_CERTIFY_ERROR_RATE`.

## Full-population census [P2 verification only]

Only after sample custody is fixed may the oracle score all 128 cells. The census records fixed `K_full` and checks only whether `K_full<=U_delta(X_sample)`. It cannot alter sample identities, `X`, `U`, delta, epsilon or the already-computed terminal. This is realized-coverage verification, not construction of the confidence bound.

## HC-C2 exhaustive exact certificate [P2]

For every

```text
1<=N<=20,
1<=n<=N,
0<=K<=N,
```

an independent bitmask subset enumerator counts intersections of every size-`n` subset with a canonical `K`-item error prefix. That enumerator does not call the hypergeometric PMF/CDF. Its exact counts are compared against the closed-form PMF and cumulative CDF.

The same finite census verifies PMF equality, CDF equality, nonincreasing `F_K(x)` in K, HC-1 coverage for delta grid `{1/2,1/3,1/4,1/5,1/10,1/20,1/80}`, and inversion-boundary correctness. Any disagreement is a falsifier; the receipt reports all case counts and requires zero failures.

## Registered execution disposition

Scoring after sample custody shows the pinned F4 predictor is determinate and correct on all four fresh registered populations. Each 64-cell sample therefore contains zero errors and no abstentions. Every coordinate reports `U=6`, upper rate `3/64`, and terminal `CALIBRATED_AT_REGISTERED_FINITE_POPULATION`. The later full census finds `K=0` in each 128-cell population, which lies below the already-computed bound.

These zero errors are specific to the bounded synthetic monotone-margin audit population. They do not imply universal or real-world capability calibration.

## Falsifiers and claim ceiling

This capsule fails if custody order is violated; the predictor blob changes; entropy/rank replay fails; a sample is duplicated or mutated; finite enumeration disagrees with the closed form; HC-1 coverage falls below `1-delta`; `U_(1/80)(0)` is not 6; abstention is counted as success; the corrupted predictor passes epsilon; census data changes a precomputed certificate; normal and optimized Python differ; or the result is presented as iid, per-example probability, real-world, universal G6 or complete-GMI evidence.

Strongest allowed terminal from this lane alone remains:

```text
EXACT_FINITE_POPULATION_CAPABILITY_ERROR_CALIBRATION_AT_REGISTERED_SCOPE
```
