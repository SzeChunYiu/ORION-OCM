# Exact finite-population calibration of F4 capability-prediction uncertainty — V2

Issue #764; parent ledger #602 Section M.

V1 is retained as a protocol negative: its outcome-free population contained only 10 determinate cells per coordinate, so the frozen 64-cell determinate sample was impossible. No V1 audit sample or oracle scoring occurred. V2 was frozen before its replacement population, sample, scorer or result.

## 1. Statistical object and scope

For each of the four registered F4 coordinates, V2 fixes a finite population of `N=128` **determinate** predictions before any oracle capability outcome is read. The population itself is selected from a frozen out-of-development raw grid using only the already-pinned F4 predictor's binary-vs-`CANNOT_IDENTIFY` status and an opaque SHA-256 ordering. Thus selection may depend on the predictor but not on correctness/error labels.

Condition on one coordinate's fixed 128-cell population. Its error pattern is an arbitrary fixed binary vector with unknown total number of errors

```text
K in {0,...,128}.
```

No superpopulation, iid model, Bernoulli parameter or replacement sampling is introduced. The only randomization used for the certificate is the sample draw: `n=64` distinct cells are sampled uniformly without replacement by fresh OS entropy and the realized identities are committed before oracle scoring.

The calibrated quantity is therefore exactly:

> the finite-population error rate `K/128` among that coordinate's frozen determinate V2 cells.

It is **not** a per-example probability, not calibration on abstained cells, and not a claim about future/raw/real-world populations.

## 2. Hypergeometric sampling law [P1]

For fixed `N`, fixed error set of cardinality `K`, and a uniformly sampled `n`-subset, let `X` be the number of sampled errors. Exactly `C(N,n)` sample subsets are equiprobable. A sample with `x` errors chooses `x` members from the `K` error cells and `n-x` members from the `N-K` non-errors, hence

```text
P_K(X=x)
 = C(K,x) C(N-K,n-x) / C(N,n)
```

for feasible `x`, and zero otherwise. This is the finite hypergeometric law by counting; no asymptotic approximation is used.

## 3. Exact upper confidence count by CDF inversion [P1]

Define

```text
F_K(x) = P_K(X <= x)
U_delta(x) = max { K in {0,...,N} : F_K(x) > delta },
```

with exact rational arithmetic and `delta in (0,1)`.

### Theorem CAL-1

For every finite `N>=1`, `1<=n<=N`, every fixed true error count `K`, and every `delta in (0,1)`,

```text
P_K( K <= U_delta(X) ) >= 1-delta.
```

### Proof

Fix the true `K`. If `K > U_delta(X)`, then by the definition of the maximum, `K` is not in the admissible set at the realized `X`; therefore

```text
F_K(X) <= delta.
```

For any integer-valued random variable with CDF `F`, define

```text
x_delta = max {x : F(x) <= delta}
```

when this set is nonempty. Because `F` is nondecreasing,

```text
{F(X) <= delta} = {X <= x_delta},
```

so

```text
P(F(X) <= delta) = F(x_delta) <= delta.
```

If the set is empty, the event is empty and has probability zero. Thus

```text
P_K(K > U_delta(X))
 <= P_K(F_K(X) <= delta)
 <= delta,
```

which is equivalent to the theorem. QED.

The strict `>` in the definition of `U_delta` is load-bearing at discrete boundaries. The executable oracle checks the stated convention exactly rather than replacing it by an asymptotic or continuous approximation.

## 4. Frozen numerical control [P2]

At

```text
N=128
n=64
delta=1/80
x=0,
```

exact inversion gives

```text
U_delta(0)=6.
```

Therefore the one-sided finite-population error-rate upper bound is

```text
6/128 = 3/64 = 0.046875 < epsilon=1/20.
```

The production code derives `6` by exact hypergeometric CDF inversion. The tests independently reconstruct the inversion and exhaust all registered small finite cases; `6` is not a stored lookup answer.

## 5. Simultaneous four-coordinate guarantee [P1]

Let `G_j` be the event that coordinate `j`'s true finite-population error count is at most its reported upper count. CAL-1 gives

```text
P(G_j^c) <= delta_j = 1/80.
```

Boole's inequality gives, without any independence assumption,

```text
P(intersection_j G_j)
 >= 1 - sum_j P(G_j^c)
 >= 1 - 4/80
 = 19/20.
```

The 80-atom hostile uses four distinct singleton failure events, making the union bound exactly tight at `19/20` simultaneous coverage while `(79/80)^4` is different. Thus an independence product is demonstrably not part of the proof.

## 6. Selective prediction and abstention [P1 accounting]

F4's `CANNOT_IDENTIFY` output is not a prediction error and must not be counted correct. V2 first fixes the determinate population using only pre-outcome predictor status; the calibration denominator is then exactly those 128 selected determinate cells.

The raw candidate universe remains reported separately. Its determinate-pool sizes are:

```text
memory_exact        4132 / 16564
planning_exact      4382 / 16564
coordination_exact  4132 / 16564
verified_tool_exact 4382 / 16564.
```

A frozen accounting hostile replaces every seventh selected population id by abstention and verifies that these cells leave both the determinate numerator and denominator. This is a bookkeeping control, not a change to the principal frozen population.

## 7. Evidence-sensitive negative control [P2]

NC-1 complements every binary F4 prediction on the same sampled identities. Hence all 64 sampled determinate predictions are wrong. The same exact inversion must return a bound above `epsilon`; every coordinate must terminate

```text
CANNOT_CERTIFY_ERROR_RATE.
```

This proves the calibration terminal is evidence-sensitive rather than a constant success path.

## 8. V1 failure as a nearest protocol counterexample

V1 demonstrates a distinct failure mode: a nominal population of 128 points need not contain enough determinate predictions to support an `n=64` selective audit. The correct behavior was to stop before outcomes rather than resample or redefine the denominator. V2 repairs the population construction prospectively and leaves V1 visible.

## 9. Exhaustive finite certificate [P2]

The hostile suite independently reconstructs exact hypergeometric counts and CDFs for every

```text
1 <= N <= 20
1 <= n <= N
0 <= K <= N
all feasible x
```

under exact deltas `1/2`, `1/5`, `1/20`, and `1/80`.

For every case it checks:

```text
sum_x P_K(X=x) = 1
production U_delta(x) = independent oracle U_delta(x)
P_K(K <= oracle_U_delta(X)) >= 1-delta.
```

The coverage checker never calls the production `upper_error_count` routine. For additional small cases it also enumerates literal sample subsets and compares the induced error-count frequencies with the combinatorial formula.

## 10. Full-population census boundary

The random-sample certificate is computed and committed before any full-population oracle census. Only afterward may all 128 cells be scored. The census does not create or tighten the confidence bound; it reports the fixed true `K` solely to verify whether the already-frozen certificate covered it.

This order prevents complete population knowledge from leaking backward into sample choice, `delta`, `epsilon`, population construction or the claimed confidence statement.

## 11. Parent subtraction

No new statistical method is claimed. The mathematics is classical finite-population sampling without replacement, exact hypergeometric inversion and Bonferroni/Boole simultaneous coverage. Broader uncertainty parents include survey-sampling theory, exact hypergeometric confidence bounds, without-replacement concentration/confidence-sequence work, selective classification/reject-option risk analysis, and conformal/risk-control methods.

The GMI-specific residual is operational only: applying an exact finite-population certificate to the already-frozen architecture-name-free F4 predictor while preserving abstention semantics, custody order and fail-closed negative controls.

## 12. Claim ceiling and falsifiers

Claim ceiling:

```text
EXACT_FINITE_POPULATION_CAPABILITY_ERROR_CALIBRATION_AT_REGISTERED_SCOPE
```

Falsifiers include:

- any V2 population or sample containing oracle/correctness/error information before the sample commit;
- sample identities outside the frozen population, duplicates, or a non-64 denominator;
- failure to reproduce the V2 population from the frozen predictor-only generator;
- any exact `N<=20` counterexample to CAL-1;
- a production bound differing from the independent exact oracle;
- `U_(1/80)(0) != 6` at `(N,n)=(128,64)`;
- a corrupted-predictor arm receiving a positive calibration terminal;
- abstentions counted as correct determinate predictions;
- full-population scoring preceding the committed sample certificate;
- normal/optimized receipt drift.

Forbidden from this capsule:

```text
PER_EXAMPLE_PROBABILITIES_CALIBRATED
IID_GENERALIZATION
REAL_WORLD_CAPABILITY_CALIBRATION
UNIVERSAL_G6
COMPLETE_GMI
```
