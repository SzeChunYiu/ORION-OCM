# Randomized switch minimax V1 — finite zero-sum parent for unknown horizon

**Status:** finite reduction + LP/minimax parent adoption / no ML / no production scheduler authorization.

`ONLINE_SWITCH_THEOREM_V1.md` exhausts deterministic time-only one-way switch
policies.  The next conventional parent is its exact randomized closure, not a
learned horizon predictor.

The only mature theorem imported here is the finite zero-sum minimax/linear
programming duality result (von Neumann + LP strong duality).  We prove the OCM
reduction and weak-duality certificate explicitly.

## 1. Finite game

Freeze one scalar resource coordinate and horizon range

```text
H in {1,...,Hmax}.
```

For deterministic switch threshold `tau in {0,...,Hmax}`, let `C_tau(H)` be the
exact expected cost from `ONLINE_SWITCH_THEOREM_V1.md`.  Let

```text
O(H) = min(I(H), S(H))
```

be the clairvoyant best static exact arm, used only as an evaluation benchmark.
Define normalized loss matrix

```text
A[H,tau] = C_tau(H) / O(H).
```

The row player chooses the realized effective lifetime.  The column player
chooses the switch threshold.  Lower loss is better for the machine.

## 2. Any randomized time-only one-way policy is a distribution over thresholds

Before semantic activation, the policy uses stateless inverse search.  Its
allowed online observation in this family is only elapsed query count plus
private random bits; it receives no future horizon, future target or target
feature.  Once semantic is activated it never switches back.

### Theorem 1 — distribution representation

Every randomized policy in this family induces a probability vector

```text
p_tau = P(first semantic query occurs at tau+1),
```

with `tau=Hmax` also absorbing all paths that never switch inside the bounded
experiment.  Conversely every probability vector `p` over thresholds is
implemented by sampling `tau~p` at epoch start and following deterministic
policy `P_tau`.

Hence the expected competitive ratio at realized horizon `H` is exactly

```text
sum_tau p_tau A[H,tau].
```

### Proof

A sample of all private random bits fixes every future random choice of a
time-only policy.  Because the only pre-switch external state is elapsed time,
that sample determines one first switch time (or no switch before `Hmax`).
Grouping random-bit samples by this threshold gives `p`.  Conditional on a
threshold, execution is exactly deterministic `P_tau`, so total expectation is
the stated mixture.  The converse construction is immediate.  QED.

This theorem would fail if the policy were allowed to condition switch time on
query identity/features, semantic state acquired before the switch, or another
observation channel.  Those are deliberately outside this parent.

## 3. Primal LP — machine's optimal mixed switch time

The exact minimax randomized policy solves

```text
minimize    r
subject to  sum_tau A[H,tau] p_tau <= r      for every H
            sum_tau p_tau = 1
            p_tau >= 0.
```

The objective `r` is the worst expected competitive ratio over all frozen
horizons.

## 4. Dual LP — adversarial horizon certificate

The dual matrix-game form is

```text
maximize    v
subject to  sum_H q_H A[H,tau] >= v          for every tau
            sum_H q_H = 1
            q_H >= 0.
```

A feasible `q` is a distribution over horizons that certifies a lower bound on
every randomized switch-time policy.

## 5. Weak-duality proof

For any feasible `p,q`,

```text
min_tau sum_H q_H A[H,tau]
<=
sum_H q_H sum_tau p_tau A[H,tau]
<=
max_H sum_tau p_tau A[H,tau].
```

The left inequality holds because a convex combination over columns cannot be
smaller than the minimum column expectation.  The right inequality holds because
a convex combination over rows cannot exceed the maximum row expectation.

The dual constraints make the left side at least `v`; the primal constraints
make the right side at most `r`.  Therefore

```text
v <= r.
```

QED.

Finite zero-sum minimax / LP strong duality gives equality at optimum.  We adopt
that general theorem rather than re-proving LP strong duality.

## 6. Numerical certificate discipline

The source curves are currently floating expected values, so the implementation
uses a pinned mature LP solver rather than claiming exact rational arithmetic.
For each resource coordinate it solves both primal and dual independently and
reports:

```text
primal optimum r;
dual optimum v;
absolute duality gap |r-v|;
maximum primal constraint violation;
maximum dual constraint violation;
support probabilities;
worst realized horizons under p;
dual support horizons.
```

Call the result numerically certified only if all feasibility/duality tolerances
pass.  This is not a machine-checked exact-real proof.

## 7. Meaning of a residual

If the optimal game value is materially above `1`, that gap is **not yet an
algorithm-selection residual**.  It is the price, inside this restricted online
information structure, of not knowing the future lifetime.

Before learning task features, ask which observation could reduce that gap:

```text
external announced horizon / workload contract;
stopping-hazard model learned from independent prior epochs;
registered reset/invalidation process;
current/past query structure, only if it predicts future demand or changes
strategy value enough to survive feature cost.
```

Under the frozen minimax horizon game, a learned model cannot infer an
adversarially hidden `H` from nothing.  Increasing model capacity is not an
information channel.

## 8. Resource-vector boundary

The game is solved separately per scalar resource coordinate.  Different mixed
policies across transitions/additions/multiplications imply price dependence.
There is no universal mixed strategy unless a vector/constraint objective is
prospectively specified.

## 9. Terminals

```text
RANDOMIZED_TIME_ONLY_SWITCH_SUFFICIENT_R0B_PHASE2B2
  optimal mixed threshold is within the registered small competitive gap

RANDOMIZED_TIME_ONLY_SWITCH_LEAVES_ONLINE_RESIDUAL_R0B_PHASE2B2
  a substantial minimax gap remains; next study the observation/stopping model,
  not a learned query selector by default

RANDOMIZED_SWITCH_LP_CANNOT_CERTIFY
  primal/dual solver or feasibility/duality checks fail
```

No terminal authorizes a neural router.