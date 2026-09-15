# FREEZE V1 — finite scaling, bottlenecks and crossovers

Parent: #602 Section U  
Child: #774

This file is the pre-implementation authority. It freezes the anonymous resource laws, price vectors,
finite-size tolerance, terminology, exact witnesses, falsifiers and claim ceiling before any executor,
test or result artifact exists.

## Scope and terminology

This is a finite exact microscope. It distinguishes:

1. **smooth within-morphology scaling** — a resource law as problem size varies;
2. **morphology-selection crossover** — the discrete selected morphology changes when two smooth charged
   cost laws cross;
3. **capability-reachability threshold** — a registered binary capability becomes feasible only when all
   required resource coordinates cross their thresholds.

The terms `critical point` and `thermodynamic phase transition` are forbidden for this finite result.
Finite-size-scaling/critical-phenomena literature is strongest-parent context for that terminology
boundary; no new statistical-physics theorem is claimed.

## Frozen resource laws

For every integer `n>=1`, anonymous morphologies Q and L have requirements

```text
Q:
  work(n)   = n^2
  memory(n) = 2n
  verify(n) = n

L:
  work(n)   = 9n + 12
  memory(n) = n + 4
  verify(n) = 2n
```

Primary charged comparison freezes price vector

```text
p_work = (1,0,0).
```

The independently frozen negative price vector is

```text
p_verify = (0,0,1).
```

It is not selected after seeing the primary result; it exists to test universal-winner language.

## Frozen predictions

### U2-1 exact crossover and finite-size correction

The continuous equality `n^2=9n+12` has positive root

```text
n* = (9 + sqrt(129))/2.
```

Prediction on positive integers:

```text
Q is strictly work-cheaper for n<=10,
L is strictly work-cheaper for n>=11.
```

The zero-intercept approximation replaces `9n+12` by `9n`. It predicts L already at n=10, so it must
be recorded as a failed exact finite extrapolation. The relative omitted setup term is exactly

```text
12/(9n) = 4/(3n).
```

Freeze tolerance `1/20` (5%). The approximation is licensed at that tolerance only for integer `n>=27`.

### U2-2 terminology discriminator

Both resource laws are polynomial/affine and therefore smooth for real `n>0`. The selector
`argmin{n^2,9n+12}` changes identity at their equality; call this only
`MORPHOLOGY_SELECTION_CROSSOVER`.

Frozen no-crossover control:

```text
A(n)=3n+1
B(n)=5n+7
```

where A is strictly cheaper for every positive `n`. Scaling alone must not fabricate a crossover.

### U2-3 conjunctive resource threshold / bottleneck

For strictly positive requirement vector `q=(q_1,...,q_d)` and available resources
`b=(b_1,...,b_d)`, define

```text
sigma(b;q) = min_i b_i/q_i.
```

Frozen theorem target:

```text
binary capability feasible  iff  sigma >= 1.
```

Indices attaining the minimum are bottlenecks. After binary feasibility is achieved, increasing one
non-bottleneck coordinate alone cannot change the binary feasible/infeasible value; this is the only
registered saturation claim.

At `n=11`, L requires

```text
(work,memory,verify) = (111,15,22).
```

Positive threshold pair:

```text
b_fail = (110,15,22)  -> infeasible
b_pass = (111,15,22)  -> feasible
```

Negative twin:

```text
memory=14, verify=22
```

remains infeasible regardless of how large work becomes, because memory is a bottleneck.

### U2-4 no universal winner from one charged coordinate

At `n=11`:

```text
work:   L=111 < Q=121
verify: Q=11  < L=22.
```

Therefore the work winner reverses under the independently frozen verification-only price vector. The
unpriced resource vectors must be reported as a Pareto tradeoff rather than a universal best morphology.

## Frozen executable census

The executor must enumerate every integer `n=1..128` and verify:

- exactly one work-selection change, between 10 and 11;
- no extra work crossing through 128;
- the zero-intercept approximation makes the specific n=10 error;
- exact relative correction `4/(3n)` and first 5%-licensed integer `27`;
- the n=11 bottleneck witnesses above;
- work/verification winner reversal;
- no crossover in the `3n+1` versus `5n+7` control.

All arithmetic except the symbolic irrational root representation must be integer/Fraction exact.

## Strongest parents / subtraction

Parent-owned mathematics includes elementary polynomial inequalities, min-ratio bottleneck accounting,
Pareto/resource scalarization, and finite-size/crossover terminology. The repository contribution is the
frozen combined microscope, executable exact boundary checks, explicit failed extrapolation, and claim
discipline.

## Claim ceiling

Allowed:

```text
FINITE_SCALING_BOTTLENECK_AND_CROSSOVER_LAWS_AT_REGISTERED_SCOPE
```

Forbidden from this child alone:

```text
THERMODYNAMIC_PHASE_TRANSITION_PROVED
UNIVERSAL_SCALING_EXPONENT
UNIVERSAL_BEST_MORPHOLOGY
REAL_SCALE_EXTRAPOLATION_PROVED
COMPLETE_GMI
```
