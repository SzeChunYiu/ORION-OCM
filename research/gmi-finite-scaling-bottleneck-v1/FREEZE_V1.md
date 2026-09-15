# #774 freeze — finite scaling, bottleneck, crossover and finite-size corrections V1

Date: 2026-09-15. Parent ledger: #602 Section U. Child issue: #774.

This is the pre-implementation authority. No executor, test, formalization, result, or dedicated workflow for this lane exists on this branch before this commit.

## Claim boundary

Target only:

```text
FINITE_SCALING_BOTTLENECK_AND_CROSSOVER_LAWS_AT_REGISTERED_SCOPE
```

This lane may close the registered finite-microscope meanings of saturation/bottleneck, smooth scaling versus selection crossover, capability resource threshold, finite-size correction, failed extrapolation with narrowed scope, and non-universality across charged resource coordinates.

It may not claim a thermodynamic phase transition, universal scaling exponent, universal best morphology, real-scale extrapolation, or complete GMI.

## Parent terminology

Finite-size-scaling literature treats finite-size crossover/rounding and critical-size corrections separately from singular thermodynamic-limit transitions. Parent anchors include Imry & Bergman (1971), Binder & Landau (1984), Lee & Kosterlitz (1991), and modern finite-size-scaling analyses. This artifact therefore freezes the following vocabulary:

- `SMOOTH_WITHIN_MORPHOLOGY_SCALING`: a registered resource function itself varies smoothly under a real-valued size extension;
- `MORPHOLOGY_SELECTION_CROSSOVER`: the discrete minimizing morphology changes when two smooth resource laws cross;
- `CAPABILITY_REACHABILITY_THRESHOLD`: a binary registered capability becomes feasible when every conjunctive resource requirement is met;
- `THERMODYNAMIC_PHASE_TRANSITION_PROVED`: forbidden from this finite artifact.

## Frozen anonymous morphology laws

For integer size `n>=1`:

```text
Q:
  work_Q(n)   = n^2
  memory_Q(n) = 2n
  verify_Q(n) = n

L:
  work_L(n)   = 9n + 12
  memory_L(n) = n + 4
  verify_L(n) = 2n
```

Frozen selection price vectors:

```text
p_work   = (1,0,0)
p_verify = (0,0,1)
```

No other price vector may be introduced in the scored V1 result.

Frozen exhaustive integer panel:

```text
n = 1,...,128
```

## U2-1 — exact crossover and finite-size correction [P1/P2]

The work difference is

```text
D(n) = work_Q(n)-work_L(n) = n^2 - 9n - 12.
```

Its positive real root is

```text
n_star = (9 + sqrt(129))/2.
```

Frozen integer prediction:

```text
D(n)<0 for 1<=n<=10  -> Q is work-cheaper;
D(n)>0 for n>=11     -> L is work-cheaper.
```

The implementation must enumerate n=1..128 and show exactly one integer winner transition, between 10 and 11.

Dropping L's setup cost yields asymptotic approximation

```text
work_L_asym(n)=9n.
```

This predicts L already at n=10 because 90<100, while the exact finite law gives 102>100 and therefore Q. The frozen finite-size correction is

```text
work_L - work_L_asym = 12,
relative correction  = 12/(9n)=4/(3n).
```

Frozen relative-error tolerance:

```text
eta = 1/20.
```

The asymptotic zero-intercept law is within this relative tolerance iff

```text
4/(3n) <= 1/20  <=> n>=27.
```

V1 must report `ASYMPTOTIC_9N_NOT_EXACT_FINITE_LAW` and scope the <=5% approximation to n>=27.

## U2-2 — smooth scaling versus crossover [P1]

The real extensions

```text
q(x)=x^2,
l(x)=9x+12
```

are smooth for x>0. No singularity is inferred in either resource law. The registered discrete selector changes identity across their equality; that is a morphology-selection crossover.

Frozen smooth no-crossover control:

```text
A(n)=3n+1,
B(n)=5n+7.
```

For every positive n, A(n)<B(n); the implementation must report zero selection transitions on n=1..128. Merely scaling with n is therefore insufficient to create a crossover.

## U2-3 — bottleneck / saturation theorem [P1]

Let strictly positive registered requirements be

```text
q=(q_1,...,q_d)
```

and available resources

```text
b=(b_1,...,b_d), b_i>=0.
```

Define normalized slack

```text
sigma(b;q) = min_i b_i/q_i.
```

Frozen theorem:

```text
all resource constraints b_i>=q_i
iff sigma(b;q)>=1.
```

Indices attaining the minimum are the registered bottlenecks.

For a binary capability defined only by these conjunctive constraints, once sigma>=1, increasing any already-nonbinding coordinate without decreasing another cannot change feasibility from true to a 'more true' state. This is binary capability saturation only; it says nothing about utility/performance beyond feasibility.

## U2-4 — exact resource threshold / negative twin [P1/P2]

At n=11, morphology L requires

```text
q_L(11)=(111,15,22).
```

Freeze memory=15 and verify=22 while varying work:

```text
b_minus=(110,15,22) -> unreachable;
b_star =(111,15,22) -> reachable.
```

Matched negative twin:

```text
b_mem=(10^6,14,10^6) -> unreachable
```

because memory remains below 15 despite excess work and verification.

## U2-5 — resource-coordinate non-universality [P1/P2]

At n=11:

```text
work_Q=121, work_L=111 -> L wins p_work;
verify_Q=11, verify_L=22 -> Q wins p_verify.
```

Thus no universal winner follows from one charged coordinate. V1 must also report the Pareto relation at n=11: Q is better on verification while L is better on work and memory, so neither dominates the other in the full three-coordinate vector.

No architecture-independent universal exponent is inferred: the registered work laws themselves have different forms (`n^2` versus `9n+12`) and the claim remains morphology/resource specific.

## U2-6 — extrapolation failure and scope narrowing [P1/P2]

The exact finite counterexample to the zero-intercept extrapolation is frozen at n=10:

```text
asymptotic approximation says L work-cheaper: 90<100;
exact finite law says Q work-cheaper: 100<102.
```

This single counterexample falsifies `9n` as an exact finite law. It is not discarded; the approximation is narrowed to the preregistered relative-error statement `n>=27 => error<=5%`.

## Frozen receipt requirements

The deterministic receipt must contain:

- issue/parent/freeze/claim ceiling;
- exact resource laws and price vectors;
- exact n=1..128 work winner sequence summarized by transition locations/count;
- continuous root represented symbolically as `(9+sqrt(129))/2` plus a bounded decimal only for display;
- exact n=10/n=11 crossover evidence;
- exact setup/relative correction and n>=27 scope;
- smooth no-crossover control;
- generic bottleneck theorem controls plus n=11 threshold and negative twin;
- work-vs-verification winner reversal and n=11 Pareto nondominance;
- explicit terminology/forbidden-claim fields.

All exact scientific decisions use integer/Fraction arithmetic; decimal root display must not drive any branch.

## Falsifiers

This lane fails if there is any extra/missing work winner transition in n=1..128; Q does not win at n=10; L does not win at n=11; the 5% finite-size boundary differs from n=27; the no-crossover control changes winner; the bottleneck equivalence fails on exhaustive registered controls; work=110 is accepted at the frozen n=11 witness; work=111 with exact other thresholds is rejected; the memory=14 twin is accepted; work and verification price vectors do not reverse the n=11 winner; Q or L strictly Pareto-dominates the other at n=11; optimized mode changes results; or any wording promotes a thermodynamic/universal/real-scale claim.
