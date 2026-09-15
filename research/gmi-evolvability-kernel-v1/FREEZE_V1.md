# FREEZE V1 — prospective exact useful-descendant / evolvability prediction

Issue: #779  
Parent: #602 V5  
Formal parent: HST-T10 / #233

This file is the pre-implementation scientific authority. It freezes the descendant space, current
object, proposal kernels, held utility predicates, predicted descendant masses and first-useful proposal
burdens, negative twins, parent subtraction and claim ceiling before any executor/result artifact exists
on this branch.

## 1. Shared present state and descendant universe

Every arm starts from exactly the same current object

```text
x0 = 000000
```

and the same complete descendant state space

```text
X = {0,1}^6.
```

All 64 descendants are admissible. The verifier is the same exact utility-membership predicate in every
arm. No arm receives a warm-start descendant, an inherited solution, a different search space, or a
different admissibility rule.

## 2. Frozen proposal kernels

### RESET

Uniform over all descendants:

```text
Q_R(z) = 1/64.
```

### CONTINUED

A factorized history-conditioned proposal kernel:

```text
P_C(z0=1)=3/4,
P_C(z1=1)=3/4,
P_C(zi=1)=1/2 for i=2,3,4,5.
```

### SHUFFLED_HISTORY

The same concentration profile reminted to irrelevant coordinates:

```text
P_S(z4=1)=3/4,
P_S(z5=1)=3/4,
P_S(zi=1)=1/2 for i=0,1,2,3.
```

`CONTINUED` and `SHUFFLED_HISTORY` must have equal exact Shannon entropy and equal sorted probability
multisets. Their difference is semantic alignment of biased coordinates with the held utility, not the
amount of concentration.

## 3. Frozen developmental history

History contains only two single-feature obligations:

```text
D0(z): z0 = 1
D1(z): z1 = 1.
```

None of the protected held utility predicates below is identical to `D0` or `D1`. This is task-definition
nonidentity; no stronger claim of statistical independence is made.

## 4. Frozen protected held utilities and predictions

For a kernel `Q` and useful set `U`, the registered HST-T10 quantity is

```text
Ev_Q(U) = sum_{z in U} Q(z).
```

### 4.1 Structured unseen composition

```text
U_AND = {z: z0=1 and z1=1}.
```

Frozen predictions:

```text
Ev_C(U_AND) = 9/16,
Ev_R(U_AND) = 1/4,
Ev_S(U_AND) = 1/4.
```

For iid verified proposals the first useful proposal count `T_U` has geometric mean `1/Ev_Q(U)`, hence

```text
E_C[T_AND] = 16/9,
E_R[T_AND] = 4,
E_S[T_AND] = 4.
```

The held conjunction is not one of the two single-feature development obligations.

### 4.2 Shifted-ecology negative twin

```text
U_ANTI = {z: z0=0 and z1=0}.
```

Frozen predictions:

```text
Ev_C(U_ANTI) = 1/16,
Ev_R(U_ANTI) = 1/4,
Ev_S(U_ANTI) = 1/4,
```

so

```text
E_C[T_ANTI] = 16,
E_R[T_ANTI] = 4,
E_S[T_ANTI] = 4.
```

This is the load-bearing harmful-transfer/reset twin: the same inherited proposal bias that helps
`U_AND` hurts `U_ANTI`.

### 4.3 Unrelated/reminted control

```text
U_45 = {z: z4=1 and z5=1}.
```

Frozen predictions:

```text
Ev_C(U_45) = 1/4,
Ev_R(U_45) = 1/4,
Ev_S(U_45) = 9/16,
```

with means `4,4,16/9`. This makes semantic reminting observable: equal-strength concentration helps only
where the biased coordinates align with future utility.

## 5. Frozen theorem obligations

### EV-1 exact finite useful-descendant mass

For every finite probability kernel `Q` on `X` and useful set `U subseteq X`,

```text
Ev_Q(U) = P_{Z~Q}[Z in U] = sum_{z in U} Q(z).
```

### EV-2 iid first-useful proposal burden

If iid proposals `Z_1,Z_2,... ~ Q` are verified independently proposal-by-proposal against one fixed
useful set `U`, and `p=Ev_Q(U)>0`, then for

```text
T = min{t>=1: Z_t in U}
```

```text
P(T>k) = (1-p)^k,
E[T] = 1/p.
```

The reported quantity is a **proposal count**, not wall-clock time. If `p=0`, the correct terminal is

```text
UNREACHABLE_ZERO_USEFUL_MASS
```

and no finite expectation may be fabricated.

### EV-3 factorized closed form

For a product kernel and a conjunction fixing coordinate values, useful mass equals the product of the
corresponding coordinate probabilities. The executor must compute all registered masses twice:

1. complete enumeration over all 64 descendants;
2. independent factorized closed form.

Exact rational equality is required.

### EV-4 equal-concentration remint control

For CONTINUED and SHUFFLED_HISTORY:

- sorted probability multisets over all 64 descendants must be exactly equal;
- exact Shannon entropy, represented symbolically as the same weighted multiset of rational
  probabilities rather than a floating approximation, must be identical.

Therefore different utility mass cannot be attributed merely to one kernel being more concentrated.

## 6. Hostile zero-mass control

Register a point-mass kernel at `000000` and useful set

```text
U_ZERO = {111111}.
```

Then `Ev=0` exactly and the first-useful terminal must be `UNREACHABLE_ZERO_USEFUL_MASS`.

## 7. Strongest-parent subtraction

The probability arithmetic is parent-owned: finite probability mass, product distributions, geometric
waiting time, and standard proposal/search-bias reasoning. HST-T10 already owns the local evolvability
object.

The repository residual is only the freeze-first developmental-kernel assay, exact continued/reset/remint
comparison on one fixed descendant universe, harmful-transfer twin, and evidence discipline. It is not a
new theorem of probability and not a universal evolvability law.

## 8. Acceptance / falsifiers

Success requires all of:

- this freeze predates executor/result artifacts;
- all three kernels normalize exactly over 64 states;
- enumerated and factorized masses agree exactly for all three protected utilities and all arms;
- every frozen mass/burden prediction is reproduced without post-outcome kernel/task changes;
- all arms share the same `x0`, descendant space, verifier and admissibility;
- held task definitions are not identical to either development obligation;
- CONTINUED and SHUFFLED_HISTORY have equal sorted mass multisets/concentration signature;
- U_AND helps CONTINUED, U_ANTI hurts CONTINUED, U_45 helps SHUFFLED_HISTORY exactly as frozen;
- zero-mass control returns `UNREACHABLE_ZERO_USEFUL_MASS`;
- normal Python and `python -O` produce byte-identical deterministic receipts.

Any failure leaves #602 V5 open.

## 9. Claim ceiling

Allowed:

```text
USEFUL_DESCENDANT_EVOLVABILITY_PREDICTION_VALIDATED_AT_REGISTERED_FINITE_SCOPE
```

Forbidden from this child alone:

```text
UNIVERSAL_EVOLVABILITY_LAW
OPEN_ENDED_EVOLUTION_PROVED
REAL_WORLD_EVOLVABILITY_CALIBRATED
CONTINUED_DEVELOPMENT_ALWAYS_BETTER
COMPLETE_GMI
```
