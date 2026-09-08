# Lifecycle representation hierarchy — exact decision-state convergence for R0B

**Status:** theorem synthesis over source-derived exact parents / no operational lifetime prior / no ML authorization.

This note separates four objects that are easy to conflate:

```text
realized hidden outcome H
ex-post decision class Z(H)
ex-ante belief state over H
policy/action chosen from that belief
```

The literature parents are conventional Bayesian decision theory, Blackwell comparison of experiments, decision-region determination, rational metareasoning, online algorithms with advice, and learning-augmented robust online control.  The contribution here is to instantiate their distinctions exactly on the frozen R0B cost family and to kill representations that are too coarse.

## Level 0 — realized decision class is enough only after the future is known

For a registered scalar resource coordinate define

```text
Z(H) = 1[S(H) < I(H)].
```

A perfect bit `Z(H)` observed before acting selects the cheaper of the two static exact arms and therefore recovers that two-arm clairvoyant static benchmark.

This is an **ex-post action-sufficiency** statement.  It does not say that a probability estimate of `Z` is a sufficient ex-ante economic state.

## Level 1 — `P(Z=1)` is not Bayes-sufficient

`DISTRIBUTIONAL_LIFECYCLE_STATE_V1.md` proves the generic collision theorem:

```text
same representation + disjoint Bayes-optimal action sets
=> no controller on that representation can be Bayes-optimal on both beliefs.
```

The source-derived witness uses

```text
P = 0.5 delta_1 + 0.5 delta_Hc
Q = 0.5 delta_1 + 0.5 delta_142,
```

where `Hc` is the first semantic-static win.  Both beliefs have semantic-region probability `0.5`, but their optimal one-way threshold sets are disjoint on every primary coordinate.

Therefore

```text
P(Z=1)
```

is not a general Bayes decision state for lifecycle investment.

## Level 2 — adding the mean horizon still does not suffice

`moment_collision_verify.py` searches source-derived equal-weight two-point priors with one support point in each static decision region and requires equality of both

```text
E[H]
P(Z=1)
```

while the Bayes-optimal threshold sets are disjoint.

The current source-derived witnesses are:

```text
transitions:
  {H=1,H=5}  versus {H=2,H=4}
  E[H]=3, P(Z=1)=0.5
  optimal sets {1} versus {4,...,142}

arithmetic additions:
  {H=1,H=7}  versus {H=2,H=6}
  E[H]=4, P(Z=1)=0.5
  optimal sets {1} versus {6,...,142}

arithmetic multiplications:
  {H=1,H=10} versus {H=2,H=9}
  E[H]=5.5, P(Z=1)=0.5
  optimal sets {1} versus {9,...,142}
```

The executable verifier is authoritative for these source-derived sets; the priors are theorem counterexamples, not operational demand evidence.

Hence even the representation

```text
(E[H], P(Z=1))
```

cannot generally support optimal economic control.

This is why point forecasts, means, binary calibration and classification accuracy must not be treated as synonymous with decision sufficiency.

## Level 3 — exact expected loss differences are sufficient

For threshold action family `A={0,...,M}`, choose reference `a_0=M` and define

```text
m_tau(P) = E_P[C(H,tau)-C(H,M)],  tau=0,...,M-1.
```

The vector `m(P)` is sufficient for one-shot Bayes threshold choice because all expected action costs differ from the reference expected cost by exactly these components.

On the frozen R0B donor it is also maximally informative in a precise linear sense.

### Theorem — threshold loss-difference transform is invertible

Let

```text
D[h,tau] = C(h,tau)-C(h,M),
```

with rows `h=1,...,M` and columns `tau=0,...,M-1`.

For `h<=tau`, neither threshold has switched, so `D[h,tau]=0`.  Thus `D` is lower triangular.  At `h=tau+1`,

```text
D[tau+1,tau] = I(tau)+S(1)-I(tau+1).
```

Under the frozen IID target population,

```text
I(tau+1)-I(tau)=I(1),
```

so every diagonal entry is `S(1)-I(1)`.  Cold one-query semantic cost is strictly above inverse on all three registered coordinates; therefore

```text
det(D) = (S(1)-I(1))^M != 0.
```

Hence `D` is invertible.  For prior row vector `p`,

```text
m(p)=pD
```

therefore uniquely determines `p`.

### Consequence

There is no nontrivial exact **linear/moment compression** that preserves the complete expected threshold-loss vector for every lifetime prior in this frozen problem.

This does not prove that an action-only quotient must be as large as the posterior.  It proves that any proposed smaller state must exploit a weaker requirement than preserving all threshold losses and must itself be proved sufficient.

## Level 4 — dynamic sufficiency is stricter than one-shot argmin sufficiency

A persistent controller also receives free information from survival:

```text
H>d
```

at age `d`, and may later buy signals, encounter invalidation, or change its admissible state-investment actions.  A state that preserves only today's Bayes-optimal threshold may fail to support tomorrow's posterior update or value-of-information calculation.

The safe conventional parent is therefore the exact posterior

```text
P(H | legal lifecycle history),
```

updated by survival and any admitted signal kernel.  A smaller dynamic information state is welcome, but it needs an explicit transition/update sufficiency proof analogous to protected-contract bisimulation.

## Scientific consequence

The R0B research question has changed materially.  It is no longer:

```text
Can target features predict inverse versus semantic?
```

and not even merely:

```text
Can a binary classifier predict whether the session will be long?
```

The correct question is:

```text
Is there a lawful, calibrated lifecycle observation channel whose posterior over
remaining protected reuse opportunity changes cost-relevant threshold losses
enough to repay its complete acquisition + inference + maintenance + drift +
lifecycle cost?
```

`PAID_HORIZON_INFORMATION_PROTOCOL_V1.md` already provides the exact Bayes and paid-signal calculus for that question.

## Current terminal

The repository has no admitted operational lifetime prior or lawful lifecycle forecast channel in the frozen R0B protocol.  Therefore theorem progress does not authorize fitting a model.

```text
DEMAND_SIGNAL_SOURCE_NOT_ESTABLISHED_R0B_PHASE2C0
LEARNED_ROUTER_NOT_AUTHORIZED
```
