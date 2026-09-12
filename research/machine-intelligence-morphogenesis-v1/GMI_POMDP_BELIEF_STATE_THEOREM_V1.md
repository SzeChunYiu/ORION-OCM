# GMI POMDP belief-state theorem v1

Status: **FORMAL PARTIAL-OBSERVATION CONTROL LAW / T7 NARROWING**

Date: 2026-09-12.

Purpose: derive the semantic state required for control under known partial observability before asking which historical architecture should implement it.

## 1. Registered POMDP

Let hidden state be `s_t`, action `a_t`, observation `o_t`, transition kernel `T(s'|s,a)`, observation kernel `O(o|s',a)`, and reward `r(s,a)`. Let the interaction history be `h_t`.

Define the belief state

\[
b_t(s)=Pr(s_t=s\mid h_t).
\]

## 2. Theorem PB-1 — Bayes belief is a sufficient controlled state

Given belief `b_t` and action `a_t`, the predictive next-state law is

\[
\tilde b_{t+1}(s')=\sum_sT(s'|s,a_t)b_t(s).
\]

After observing `o_{t+1}`, the updated belief is

\[
b_{t+1}(s')=
\frac{O(o_{t+1}|s',a_t)\tilde b_{t+1}(s')}
{\sum_x O(o_{t+1}|x,a_t)\tilde b_{t+1}(x)}.
\]

The expected immediate reward is

\[
r(b_t,a)=\sum_s b_t(s)r(s,a).
\]

For every future policy, the conditional distribution of all future rewards/observations given history `h_t` depends on that history only through `b_t`. Therefore optimal control can be written as a policy on belief states.

### Proof sketch

The Markov transition/observation assumptions make the one-step predictive law a function only of `b_t,a_t`. Bayes' rule gives a recursively closed update. Induction over future horizons then gives identical future laws for histories with identical beliefs. QED.

## 3. Collision no-go

If two histories induce different beliefs and there exists some future action/continuation whose reward or observation distribution differs between those beliefs, any controller state that aliases the histories is insufficient for the registered control obligation.

Conversely, the raw belief can sometimes be further quotiented: beliefs that have identical rewards and identical transition mass into future decision-equivalence classes for every action need not remain distinct. Thus belief is a general sufficient state, not always the minimal control quotient.

## 4. GMI derivation consequence

Partial observability plus decision-relevant latent uncertainty predicts:

```text
uncertainty-bearing developmental/execution state
recursive evidence update
counterfactual action-conditioned transition model when planning is useful
possible quotienting of beliefs by decision equivalence
```

A point estimate is sufficient only in negative-twin regimes where all posterior ambiguity is decision-irrelevant.

## 5. Model-based versus compiled policy

The belief-state theorem specifies semantic state, not lifecycle realization. Repeated goals/dynamics, model error, online planning price and policy reuse determine whether the belief transition model is retained explicitly, compiled into value/policy state, or combined in a hybrid.

## 6. Remaining blockers

```text
learning T/O/reward from finite data
belief approximation under large/continuous state
exploration and information acquisition
nonstationary hidden dynamics
minimal nonlinear decision quotient discovery
protected model-based/model-free/hybrid crossover
```

## Claim ceiling

This closes the known-model POMDP sufficient-state theorem inside the GMI derivation chain. It does not close learned world models, exploration, or large-scale POMDP development.
