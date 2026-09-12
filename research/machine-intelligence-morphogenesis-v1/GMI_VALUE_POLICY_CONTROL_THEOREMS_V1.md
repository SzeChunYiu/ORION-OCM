# GMI Value and Policy Control Theorems v1

Status: **FORMAL ZERO-PRIOR CONTROL HARDENING / PARENT-THEOREM INTEGRATION**

Status date: 2026-09-12.

Purpose:

> Derive value-state and direct-policy control realizations from Bellman fixed-point structure and repeated-use economics rather than treating reinforcement-learning families as unexplained architecture names.

---

# 1. Discounted finite Markov decision process

Let finite state set `S`, action set `A`, transition law `P(s'|s,a)`, bounded reward `r(s,a)`, and discount

\[
0\le\gamma<1.
\]

For value function `V`, define Bellman optimality operator

\[
(TV)(s)=\max_a\left[r(s,a)+\gamma\sum_{s'}P(s'|s,a)V(s')\right].
\]

## Theorem VC-1 — Bellman operator is a contraction

Under sup norm,

\[
\|TV-TW\|_\infty
\le
\gamma\|V-W\|_\infty.
\]

### Proof

For each state, difference between maxima is bounded by the maximum actionwise difference; reward cancels and transition probabilities average the value difference, giving factor `gamma`. QED.

## Corollary VC-1.1 — unique optimal value state

By Banach's fixed-point theorem, `T` has a unique fixed point `V*`, and repeated value iteration converges geometrically:

\[
\|T^kV-V^*\|_\infty\le\gamma^k\|V-V^*\|_\infty.
\]

### GMI derivation consequence

When the ecology is Markov, rewards/reuse are stationary, and future decision quality can be summarized by expected discounted return, a value field is a recursively sufficient **decision summary** for optimal control.

This is a zero-prior route to value-based control state.

---

# 2. Greedy policy compilation from an exact value state

Given `V*`, define

\[
Q^*(s,a)=r(s,a)+\gamma\sum_{s'}P(s'|s,a)V^*(s').
\]

Any policy choosing

\[
\pi^*(s)\in\arg\max_aQ^*(s,a)
\]

is optimal.

## Theorem VC-2 — value-to-policy compilation

An exact optimal value state plus one-step model access compiles into an optimal direct action policy.

If the argmax action is stored per state, future decisions can avoid repeated Bellman/planning computation at the cost of policy storage/update burden.

### GMI lifecycle interpretation

This is another compile-versus-online-compute phase:

```text
novel/changing goals or dynamics:
    online model/value/planning may be worth its cost

stable repeated decision state:
    compile/copy into direct policy/action table
```

---

# 3. Model-free Q-state is sufficient when dynamics need not be separately queried

If exact action values `Q*(s,a)` are available, optimal action selection is simply

\[
\arg\max_aQ^*(s,a).
\]

Thus for the obligation “choose optimal action under the fixed task,” the full transition model is semantically unnecessary once exact `Q*` has been compiled.

### Negative twin

If future goals/reward functions change while dynamics stay reusable, a fixed `Q*` for one reward can become obsolete whereas a reusable dynamics model can support replanning. This recovers the model-based versus compiled-policy crossover from the separate lifecycle theorem.

---

# 4. Policy-gradient structural identity

Let differentiable stochastic policy `pi_theta(a|s)` induce trajectory distribution `p_theta(tau)` and expected return

\[
J(\theta)=\mathbb E_{\tau\sim p_\theta}[R(\tau)].
\]

Assume environment dynamics do not depend on `theta`.

## Parent theorem VC-3 — score-function policy gradient

Under regularity allowing differentiation under the integral/sum,

\[
\nabla_\theta J
=
\mathbb E\left[
R(\tau)
\sum_t\nabla_\theta\log\pi_\theta(a_t|s_t)
\right].
\]

### Derivation consequence

When a direct policy is parameterized differentiably and only sampled returns are available, the score-function identity gives an update direction without requiring a differentiable environment model.

This is the structural route to policy-gradient-like development.

---

# 5. Baseline/control-variate theorem behind actor-critic structure

Let `b(s_t)` be any baseline independent of action `a_t` conditional on state.

## Theorem VC-4 — action-independent baseline does not bias score-function gradient

\[
\mathbb E_{a\sim\pi_\theta(\cdot|s)}
[b(s)\nabla_\theta\log\pi_\theta(a|s)]
=0.
\]

### Proof

\[
\sum_a\pi(a|s)b(s)\nabla\log\pi(a|s)
=b(s)\sum_a\nabla\pi(a|s)
=b(s)\nabla1=0.
\]

Thus subtracting a learned state-dependent value baseline can reduce variance without changing the expectation when assumptions hold.

### GMI derivation consequence

A separate learned value/critic state is justified when its development/serve cost is lower than the benefit from reducing policy-update variance/sample burden.

This derives the **policy + value-estimator decomposition** property, not any one actor-critic implementation.

---

# 6. Exploration remains a separate semantic requirement

Bellman/value/policy identities assume enough information has been acquired about rewards/dynamics. `GMI_EXPLORATION_AND_META_LEARNING_THEOREMS_V1.md` proves a collision family where refusing an informative action makes optimal control impossible.

Therefore zero-prior control derivation must jointly reason about:

```text
state/belief sufficiency
exploration information value
world-model reuse
value/policy compilation
update/sample burden
serving latency
```

No single model-free/model-based label is universally privileged.

---

# 7. Gap update

Control-family structural coverage now includes:

```text
Bellman value-state contraction/fixed point                 CLOSED
value -> optimal direct policy compilation                 CLOSED
Q-state sufficiency for fixed reward task                  CLOSED
score-function direct-policy update identity               PARENT-THEOREM CLOSED
value baseline unbiasedness                                CLOSED
exploration necessity                                      CLOSED
model-based vs direct-policy lifecycle threshold           CLOSED
```

Still open:

```text
learned value/model approximation error
function approximation instability
exploration in large POMDPs
sample-efficiency prediction
policy-gradient variance/conditioning estimator
protected model-based/value/policy family selection
```

---

# 8. Claim ceiling

These theorems cover exact finite discounted MDP structure and standard score-function identities. They do not prove convergence of modern deep RL or close partial observability/exploration/generalization in real environments.
