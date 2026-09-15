# Finite scaling, bottleneck, crossover and finite-size corrections — formalization V1

Issue #774; parent ledger #602 Section U. Pre-implementation authority: `FREEZE_V1.md`, commit `e4d6f9ef941e1b7dfc958c8f8446c7890f40d2a7`.

## 1. Claim boundary and parent subtraction

Claim ceiling:

```text
FINITE_SCALING_BOTTLENECK_AND_CROSSOVER_LAWS_AT_REGISTERED_SCOPE
```

The parent mathematics is elementary finite-size correction, resource-feasibility inequalities, Pareto comparison, and finite crossover analysis. Critical-phenomena literature is used only to discipline terminology: finite systems may show size-dependent crossover/rounding, while singular thermodynamic phase-transition language requires stronger limiting structure. The present artifact therefore proves only registered finite scaling/crossover and binary capability thresholds.

Evidence classes:

- U2-1 through U2-6: P1 exact finite statements;
- n=1..128 panels, 3,375 bottleneck cases and frozen hostiles: P2 exact computation.

Forbidden implications include thermodynamic phase transition, universal scaling exponent, universal morphology winner, real-scale extrapolation and complete GMI.

## 2. Registered resource laws

For integer `n>=1`, anonymous morphologies Q and L have

```text
Q(n) = (n^2, 2n, n)
L(n) = (9n+12, n+4, 2n)
```

in coordinates `(work,memory,verify)`.

Two price vectors are preregistered:

```text
p_work=(1,0,0),
p_verify=(0,0,1).
```

No claim is based on an after-the-fact price vector.

## 3. U2-1 — exact work crossover [P1/P2]

Define

```text
D(n)=work_Q(n)-work_L(n)=n^2-9n-12.
```

Its positive real zero is

```text
n*=(9+sqrt(129))/2.
```

Direct evaluation gives

```text
D(10)=100-102=-2,
D(11)=121-111=10.
```

Moreover

```text
D(n+1)-D(n)=2n-8.
```

Hence D is strictly increasing for every integer `n>=5`. Since D(10)<0<D(11), Q is work-cheaper for every positive integer through 10 and L is work-cheaper from 11 onward. The exhaustive n=1..128 control finds exactly one winner transition, 10 -> 11, and no tie.

This is a `MORPHOLOGY_SELECTION_CROSSOVER`: the selector changes class. It is not a singularity in either underlying resource law.

## 4. U2-2 — smooth scaling is not itself a phase transition [P1/P2]

The real extensions

```text
q(x)=x^2,
l(x)=9x+12
```

are polynomials/affine and therefore smooth for x>0. Their intersection can make a discrete optimizer switch without making either law non-smooth.

The negative control

```text
A(n)=3n+1,
B(n)=5n+7
```

satisfies

```text
B(n)-A(n)=2n+6>0
```

for every positive n. Thus both quantities scale smoothly and yet there is no optimizer crossover on any positive size; exhaustive n=1..128 execution reports zero transitions.

The exact distinction is therefore:

- `SMOOTH_WITHIN_MORPHOLOGY_SCALING`: a property of each resource function;
- `MORPHOLOGY_SELECTION_CROSSOVER`: a change of argmin across competing functions;
- `CAPABILITY_REACHABILITY_THRESHOLD`: a feasibility indicator crossing;
- `THERMODYNAMIC_PHASE_TRANSITION_PROVED`: not established here.

## 5. U2-3 — finite-size correction and scope narrowing [P1/P2]

Dropping L's setup term gives the asymptotic zero-intercept approximation

```text
work_L^asym(n)=9n.
```

The exact additive error is 12 and the exact relative error against `9n` is

```text
12/(9n)=4/(3n).
```

At n=10, the approximation predicts L cheaper because

```text
90<100,
```

while the exact finite law predicts Q cheaper because

```text
100<102.
```

This explicit counterexample falsifies `9n` as an exact finite-size law.

For preregistered tolerance `eta=1/20`, the approximation is within 5% exactly when

```text
4/(3n) <= 1/20
<=> 80 <= 3n
<=> n >= 80/3.
```

Thus for integer sizes the smallest licensed n is 27. The failed extrapolation remains visible and its scope is narrowed rather than reinterpreted away.

## 6. U2-4 — bottleneck and saturation theorem [P1/P2]

Let requirements be strictly positive

```text
q=(q_1,...,q_d)
```

and resources nonnegative

```text
b=(b_1,...,b_d).
```

Define

```text
sigma(b;q)=min_i b_i/q_i.
```

### Theorem

```text
[b_i>=q_i for every i] iff sigma(b;q)>=1.
```

### Proof

If every `b_i>=q_i`, then each ratio `b_i/q_i>=1`, so their minimum is at least one. Conversely, if the minimum is at least one, then every ratio is at least one and multiplying by positive `q_i` gives `b_i>=q_i` for every coordinate. QED.

Indices achieving the minimum are registered bottlenecks. The implementation exhausts all three-dimensional requirement vectors in `{1,2,3}^3` and resource vectors in `{0,1,2,3,4}^3`: 3,375 exact cases, zero disagreements between direct conjunction and the sigma criterion.

For a binary capability defined solely by these conjunctive requirements, once sigma>=1, increasing a nonbinding resource alone cannot create a new binary state beyond feasible. This is binary-feasibility saturation only; it does not say task utility or throughput has saturated.

Frozen saturation control for L at n=11 uses requirements `(111,15,22)`. Both resources `(200,15,22)` and `(10^6,15,22)` have sigma=1, bottlenecks `{memory,verify}`, and remain feasible despite the large work increase.

## 7. U2-5 — exact capability threshold and matched negative twin [P1/P2]

At n=11,

```text
L requirements=(111,15,22).
```

With memory and verification exactly at threshold,

```text
(110,15,22) -> sigma=110/111 < 1 -> infeasible,
(111,15,22) -> sigma=1 -> feasible.
```

Thus the registered capability becomes reachable exactly at work 111 under these fixed companion resources.

Matched negative twin:

```text
(10^6,14,10^6)
```

has memory ratio `14/15<1`, so the capability remains infeasible despite massive work and verification. This proves that a threshold in one coordinate is meaningful only conditional on the other conjunctive requirements.

## 8. U2-6 — resource-coordinate non-universality [P1/P2]

At n=11,

```text
Q=(121,22,11),
L=(111,15,22).
```

Under work-only price, L wins: `111<121`.
Under verification-only price, Q wins: `11<22`.

In the full vector, L is better on work and memory, while Q is better on verification. Therefore neither strictly Pareto-dominates the other.

Consequences at this registered scope:

1. a winner on one resource coordinate is not a universal winner;
2. the distinct work forms `n^2` and `9n+12` are morphology-specific laws, not evidence for one universal scaling exponent;
3. any broader scalarized winner requires a prospectively registered price vector.

## 9. Falsifiers

The claim fails if the integer crossover is not uniquely 10->11 on n=1..128; the n=10 asymptotic/exact winners do not disagree; the 5% correction boundary differs from 27; the smooth control has a crossover; direct feasibility and sigma disagree in any of the 3,375 exact controls; the n=11 threshold/twin fails; the two frozen price vectors do not reverse the winner; one n=11 resource vector dominates the other; normal and optimized Python differ; or finite crossover language is promoted into thermodynamic/universal/real-scale wording.

Strongest permitted terminal:

```text
FINITE_SCALING_BOTTLENECK_AND_CROSSOVER_LAWS_AT_REGISTERED_SCOPE
```
