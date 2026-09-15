# FORMALIZATION V1 — finite scaling, bottlenecks and crossovers

Issue #774; parent #602 Section U. `FREEZE_V1.md` is the pre-implementation authority.

## U2-1 — exact finite work crossover [P1]

For real `n>0`, define

```text
W_Q(n)=n^2,
W_L(n)=9n+12,
d(n)=W_Q(n)-W_L(n)=n^2-9n-12.
```

The roots of `d` are

```text
(9 ± sqrt(129))/2.
```

The negative root is below zero. The positive root

```text
n*=(9+sqrt(129))/2
```

lies strictly between 10 and 11 because

```text
11 < sqrt(129) < 13.
```

Since the leading coefficient of `d` is positive, `d(n)<0` for positive `n<n*` and `d(n)>0`
for `n>n*`. Therefore for every positive integer `n`,

```text
n<=10  => W_Q(n)<W_L(n),
n>=11  => W_L(n)<W_Q(n).
```

Thus the first strict integer L win is exactly `n=11`.

### Finite-size correction to the zero-intercept approximation

The asymptotic zero-intercept approximation is `W_L^0(n)=9n`. Its omitted setup term is 12, so the
relative correction with respect to `9n` is exactly

```text
(W_L-W_L^0)/W_L^0 = 12/(9n) = 4/(3n).
```

At the frozen tolerance `1/20`,

```text
4/(3n) <= 1/20
iff 80 <= 3n.
```

Hence the first positive integer licensed by that tolerance is `n=27`. At `n=10`, the approximation
predicts `90<100` and therefore L, while the exact laws give `100<102` and therefore Q. The approximation
is consequently falsified as an exact finite law at a concrete frozen point even though its relative error
vanishes as `n` grows.

## U2-2 — smooth laws do not imply a thermodynamic phase transition [P1/definition]

`W_Q` and `W_L` are polynomials and therefore infinitely differentiable on `n>0`. The morphology selector

```text
S(n)=argmin{W_Q(n),W_L(n)}
```

changes identity across `n*`. This is a **morphology-selection crossover** induced by taking an argmin over
two smooth laws.

The lower envelope is continuous at `n*`, but the active derivatives differ:

```text
W_Q'(n*)=2n* > 20,
W_L'(n*)=9.
```

So the engineered envelope has a kink. That finite optimizer kink is not, by itself, evidence for a
thermodynamic-limit singularity, diverging correlation length, universal critical exponent, or any other
statistical-physics phase-transition criterion. Finite-size-scaling literature explicitly studies rounding
and shifts of transitions in finite systems, reinforcing the terminology boundary rather than licensing a
thermodynamic claim from this two-law optimizer. The registered terminal is therefore
`MORPHOLOGY_SELECTION_CROSSOVER` only.

The frozen control `A(n)=3n+1`, `B(n)=5n+7` has

```text
B(n)-A(n)=2n+6>0
```

for every positive `n`; both quantities scale smoothly but no selection crossover exists. Scaling itself
therefore does not imply a crossover.

## U2-3 — conjunctive bottleneck / binary saturation theorem [P1]

Let `q=(q_1,...,q_d)` with every `q_i>0` be a registered requirement vector and `b=(b_1,...,b_d)` with
`b_i>=0` the available resources. Define

```text
sigma(b;q)=min_i b_i/q_i.
```

A conjunctive binary capability is defined as feasible exactly when every coordinate requirement is met:
`b_i>=q_i` for all `i`.

**Theorem.**

```text
capability feasible  iff  sigma(b;q)>=1.
```

**Proof.** If every `b_i>=q_i`, then every ratio `b_i/q_i>=1`, hence their minimum is at least 1.
Conversely, if the minimum ratio is at least 1, every ratio is at least 1 and therefore every
`b_i>=q_i`. ∎

The set

```text
Bottleneck(b;q)={i : b_i/q_i = sigma(b;q)}
```

is nonempty in finite dimension. If capability is infeasible, increasing only a coordinate outside the
current bottleneck set cannot repair a strictly subunit bottleneck that is left unchanged. Once every
coordinate reaches threshold, the registered **binary feasibility value** is already 1 and increasing any
coordinate alone cannot increase that binary value. This is the exact saturation statement; it is not a
claim that continuous utility, quality, throughput, or scientific progress has saturated.

At `n=11`, L has `q=(111,15,22)`. The frozen controls are

```text
(110,15,22): sigma=110/111 < 1, work bottleneck, infeasible;
(111,15,22): sigma=1, feasible;
(111000,14,22): sigma=14/15 < 1, memory bottleneck, infeasible.
```

The last case is a finite witness of the stronger algebraic statement: if memory remains 14, arbitrarily
large work cannot make the conjunction feasible.

## U2-4 — Pareto non-universality / price reversal [P1]

At `n=11`,

```text
q_Q=(121,22,11),
q_L=(111,15,22).
```

L is strictly better in work and memory; Q is strictly better in verification. Hence neither resource
vector Pareto-dominates the other.

Under the frozen work-only price `p_work=(1,0,0)`, L costs 111 versus Q's 121, so L wins. Under the
independently frozen verification-only price `p_verify=(0,0,1)`, Q costs 11 versus L's 22, so Q wins.
Thus no coordinate-free universal winner follows from the primary work comparison.

## U2-5 — claim ceiling / extrapolation boundary [P5-style consequence]

The exact finite results establish only:

- the registered polynomial/affine laws and their integer crossover;
- the explicit `4/(3n)` finite correction and 5% boundary;
- the conjunctive binary bottleneck theorem;
- one resource-price reversal and Pareto incomparability.

They do not establish a universal scaling exponent, a universal-best morphology, a thermodynamic phase
transition, or real-scale extrapolation. In particular, the n=10 counterexample forbids promoting the
zero-intercept `9n` approximation to an exact finite law outside its declared error regime.

## Strongest-parent subtraction

The algebra is elementary and parent-owned. Finite-size-scaling work such as Binder & Landau (1984)
explicitly analyzes finite-size rounding of anomalies associated with infinite-system transitions; that
literature motivates the terminology discipline but does not turn this optimizer crossover into a
statistical-physics phase transition. The repository contribution is the frozen combined microscope,
exact hostile controls, and executable scope enforcement.

## Claim ceiling

`FINITE_SCALING_BOTTLENECK_AND_CROSSOVER_LAWS_AT_REGISTERED_SCOPE`.
