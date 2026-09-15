# FORMALIZATION V1 — prospective capability perturbations

Issue #784; parent #602 V4. `FREEZE_V1.md` at commit
`ee62a2ae888ebddbc925972bc149468884e24ba5` is the pre-scoring authority.

## Registered predictor

The pinned predictor is exactly the Git blob

```text
937b91f6a3787ff04c2b5209c81d249518406859
research/gmi-capability-predictor-dev-v1/dev_predictor_v1.py
```

Its development set is the complete grid `{-1,0,1}^5`.  It fits a monotone
partial-order envelope on five architecture-name-free margins:

```text
m = (memory, planning, communication, routing, verification).
```

For each target `t`, a held point `x` is predicted as

```text
1  if some positive development point y satisfies y <= x coordinatewise,
0  if some negative development point z satisfies x <= z coordinatewise,
CANNOT_IDENTIFY otherwise.
```

The development corpus is monotone, so the positive-below and negative-above
conditions cannot both hold.

The independent capability oracle is frozen separately:

```text
memory_exact        = [memory >= 0]
planning_exact      = [memory >= 0 AND planning >= 0]
coordination_exact  = [communication >= 0]
verified_tool_exact = [routing >= 0 AND verification >= 0].
```

This lane does not refit the predictor or alter those definitions.

## P4-1 — exact perturbation maps [P1]

### Ablation

For the registered component ablation, only the memory margin changes:

```text
T_A(m)_memory = a,
T_A(m)_j = m_j for j != memory.
```

Therefore the post-point is unique once the frozen pre-point and frozen
after-value `a` are given.  The scorer reconstructs this post-point instead of
trusting a duplicated result row.

### Resource repricing

Let routing budget be `B`, routing demand be `d>0`, and unit price be `p`.
The frozen routing margin is

```text
r(B,d,p) = B - p d.
```

For the main registered repricing,

```text
B=5, d=1, p:3 -> 7,
r_pre = 5-3 = +2,
r_post = 5-7 = -2.
```

For the safe control,

```text
p:2 -> 3,
r_pre = +3,
r_post = +2.
```

These are exact integer equalities; no estimated effect or fitted coefficient
appears.

### Environmental drift

For communication margin `c` and nonnegative shock `s`,

```text
T_D(c,s) = c-s.
```

Hence the main drift gives `2-4=-2` and the safe control gives `3-1=2`.

These transformation statements are deterministic arithmetic.  They are not
general causal-effect claims outside the registered synthetic oracle.

## P4-2 — held-domain separation [P1]

Every scored pre and post point contains at least one coordinate whose
absolute value is at least two.  Therefore no scored point belongs to the
development grid `{-1,0,1}^5`.

This is stronger than merely saying each pair contains one held point: both
members of every pair are outside the fit grid, so replacing a decisive held
point by an in-grid surrogate is machine-detectable.

## P4-3 — exact main ablation prediction [P1 + P2 replay]

The main post-ablation point is

```text
x_A=(-2,0,0,0,0).
```

For `memory_exact`, any positive development witness would need memory
coordinate at most `-2`, impossible because the development minimum is `-1`.
A negative development point exists above `x_A`, e.g.
`(-1,0,0,0,0)`, so the monotone envelope predicts `0`.

The same argument applies to `planning_exact`: no positive development point
can lie below `x_A`, while a development point with memory `-1` and planning
`0` is negative and lies above it.  Thus planning is predicted `0`.

For `coordination_exact`, no positive development point can lie below `x_A`
because the unrelated memory coordinate would still have to be `<=-2`.
But a negative-above witness would require communication `-1`; that is not
above held communication `0`.  Hence neither envelope side fires and the
registered output is `CANNOT_IDENTIFY`.

The same reasoning applies to `verified_tool_exact`: a negative point must
have routing or verification `-1`, which is not coordinatewise above the held
zeros.  Therefore the post vector is exactly

```text
(0,0,CANNOT_IDENTIFY,CANNOT_IDENTIFY).
```

The independent oracle vector is `(0,0,1,1)`.  The two determinate losses
`{memory_exact, planning_exact}` are therefore both correct, while the two
unrelated positives are explicit abstentions and are not counted as success.

## P4-4 — exact repricing prediction [P1 + P2 replay]

The main post-repricing point is

```text
x_R=(0,0,0,-2,0).
```

For `verified_tool_exact`, no positive development point can lie below `x_R`
because routing in development is at least `-1`.  A negative point with routing
`-1` and all other coordinates zero lies above `x_R`; therefore the predictor
returns `0`, matching the oracle.

For memory, planning, and coordination, the negative condition for each target
requires a `-1` on its own relevant axis, which cannot be above the held zero
on that axis.  Positive witnesses are blocked by the unrelated routing
coordinate `-2`.  Thus those three targets abstain.  The exact post vector is

```text
(CANNOT_IDENTIFY,CANNOT_IDENTIFY,CANNOT_IDENTIFY,0).
```

The only determinate direct deficit is `verified_tool_exact`.

## P4-5 — exact drift prediction [P1 + P2 replay]

The main post-drift point is

```text
x_D=(0,0,-2,0,0).
```

For `coordination_exact`, positive-below is impossible because development
communication is at least `-1`, and a negative development point with
communication `-1` lies above `x_D`; therefore the prediction is `0`.

For the other three targets, positive witnesses are blocked by the unrelated
communication coordinate `-2`, while negative-above witnesses would require a
`-1` on the relevant memory/planning/routing/verification axis and so are not
above the held zero.  Hence the exact post vector is

```text
(CANNOT_IDENTIFY,CANNOT_IDENTIFY,0,CANNOT_IDENTIFY).
```

The only determinate direct deficit is `coordination_exact`.

## P4-6 — safe controls [P1 + P2 replay]

Every safe pre/post point has all nonperturbed axes equal to zero and the
perturbed axis strictly positive (`+2` or `+3`).  The development point
`(0,0,0,0,0)` lies below every such point and is positive for all four
registered capabilities.  Therefore the monotone predictor returns `1` for
all four targets.

Since the fitted corpus is monotone, no conflicting negative-above witness can
coexist.  Thus A1, R1, and D1 are each exactly `(1,1,1,1)` before and after the
safe perturbation.

## P4-7 — abstention accounting [P1]

Let `D` be the set of determinate predictor cells and `A` the set of
`CANNOT_IDENTIFY` cells.  Registered accuracy is defined only on `D`:

```text
accuracy_D =
  |{i in D : prediction_i = oracle_i}| / |D|.
```

No element of `A` may enter either numerator or denominator.

For the six frozen pre/post pairs there are 48 cells total.  The preregistered
outcomes yield

```text
|D| = 40,
correct_D = 40,
|A| = 8.
```

So the receipt reports `40/40` determinate accuracy and eight abstentions,
rather than falsely reporting `48/48`.

## P4-8 — custody and falsifiers [P2 protocol]

The executable fails closed if any of the following occurs:

1. the pinned predictor Git blob changes;
2. reconstructed repricing or drift arithmetic disagrees with the frozen
   post-point;
3. any scored point falls back inside `{-1,0,1}^5`;
4. any frozen oracle or predictor vector changes;
5. an expected `CANNOT_IDENTIFY` is replaced by a guessed oracle value;
6. any determinate prediction disagrees with the independent oracle;
7. a main direct-deficit set changes;
8. a safe control changes or abstains;
9. normal and optimized Python receipts differ.

The dedicated test suite includes mutations for each load-bearing category,
and CI reproduces the committed receipt byte-for-byte under both ordinary
Python and `python -O`.

## Strongest-parent subtraction

The monotone-envelope predictor, threshold capability definitions, and basic
resource-margin arithmetic are parent-owned by the already merged F4
development predictor.  This lane contributes only the stronger freeze-first
prospective held-perturbation custody test, exact transformation replay,
abstention discipline, and adversarial evidence.

## Claim ceiling

Allowed:

```text
PROSPECTIVE_CAPABILITY_PERTURBATIONS_VALIDATED_AT_REGISTERED_SYNTHETIC_SCOPE
```

Not established here:

```text
UNIVERSAL_CAPABILITY_PREDICTOR
REAL_WORLD_PERTURBATION_CALIBRATION
CAUSAL_EFFECT_IDENTIFIED_OUTSIDE_REGISTERED_ORACLE
G6_UNIVERSAL
COMPLETE_GMI
```
