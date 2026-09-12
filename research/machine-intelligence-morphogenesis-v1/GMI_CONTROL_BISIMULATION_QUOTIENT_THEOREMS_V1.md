# GMI Control Bisimulation Quotient Theorems v1

Status: **FORMAL ZERO-PRIOR WORLD-MODEL HARDENING / FINITE MDP BASE CASE**

Status date: 2026-09-12.

Purpose:

> Derive the minimum decision-relevant world-state structure for a finite Markov control problem. A useful world model need not reproduce raw environment state; it must preserve distinctions that change rewards or future transition mass into decision-relevant classes.

---

# 1. Finite Markov decision process

Let finite state set `S`, actions `A`, reward `r(s,a)`, transition kernel `P(s'|s,a)`, and discount `gamma in [0,1)`.

Let partition/equivalence relation `~` divide states into classes `C`.

---

# 2. Reward-transition equivalence

Call two states `s ~ t` **bisimilar with respect to the partition** if for every action `a`:

\[
r(s,a)=r(t,a)
\]

and for every equivalence class `C`,

\[
\sum_{s'\in C}P(s'|s,a)
=
\sum_{s'\in C}P(s'|t,a).
\]

Thus they have identical immediate protected reward and identical transition probability into every decision-relevant class.

---

# 3. Quotient MDP construction

For class `[s]`, define

\[
\bar r([s],a)=r(s,a)
\]

and

\[
\bar P([u]|[s],a)
=
\sum_{u'\in[u]}P(u'|s,a).
\]

The bisimulation conditions make these definitions independent of the chosen representative.

## Theorem CB-1 — exact quotient control model

The quotient state process over equivalence classes is a well-defined MDP. For every class-constant value function `V(s)=\bar V([s])`, Bellman evaluation/optimality in the original MDP agrees exactly with Bellman evaluation/optimality in the quotient MDP.

### Proof

Immediate rewards agree inside each class. Expected next value under a class-constant `V` is

\[
\sum_{s'}P(s'|s,a)\bar V([s'])
=
\sum_C\bar P(C|[s],a)\bar V(C),
\]

which is the quotient Bellman term and is representative-independent by the transition-class equality. QED.

---

# 4. Optimal values and actions are class invariant

## Corollary CB-1.1

The unique discounted optimal value `V*` is constant on bisimulation classes, and there exists an optimal policy that chooses the same action distribution for states in the same class.

### GMI consequence

A world model that distinguishes bisimilar raw states carries unnecessary state for the registered reward/control obligation.

The semantic sufficient state is the **control quotient**, not necessarily the physical/raw state identifier.

---

# 5. Collision/no-go for over-aggressive state merging

Suppose two states `s,t` are merged by a proposed model state, but for some action either:

1. immediate registered reward differs; or
2. transition mass differs into a future class whose optimal value differs.

## Theorem CB-2 — decision-relevant merge can change action values

There exists a registered finite-horizon/discounted continuation value assignment consistent with that distinction for which the action value

\[
Q(s,a)
\]

differs from

\[
Q(t,a).
\]

Therefore a model that merges the states cannot be universally exact for the corresponding control family.

### Interpretation

World-model compression is legal only when discarded distinctions are irrelevant to both current reward and future decision-relevant transitions.

---

# 6. Approximate bisimulation bound

Suppose for two states in one proposed class, for every action:

\[
|r(s,a)-r(t,a)|\le\epsilon_r
\]

and aggregated transition distributions over quotient classes differ in total variation by at most `epsilon_p`.

If future value range is bounded by

\[
\operatorname{span}(V)\le V_{range},
\]

then one-step Bellman action-value discrepancy obeys

\[
|Q(s,a)-Q(t,a)|
\le
\epsilon_r+\gamma\epsilon_p V_{range}
\]

under the convention `TV=1/2 ||p-q||_1` and the standard bounded-function TV inequality using value span.

### GMI consequence

Approximate model compression has a direct error budget:

```text
reward distortion
+ discounted transition-quotient distortion * future value scale.
```

This is a control-specific rate-distortion variable.

---

# 7. Model-based versus policy-only state

For one fixed reward/task, an exact optimal `Q*` or policy can be sufficient for action selection without retaining transition structure.

But if future reward/goals vary while dynamics remain stable, the bisimulation quotient for one reward can be too coarse for another.

Therefore reusable world-model state should be defined relative to the **registered family of future goals/interventions**, not one current task alone.

### GMI prediction

```text
one fixed high-reuse task:
    compile control into value/policy state

many future goals sharing dynamics:
    preserve a richer dynamics/control quotient and replan
```

This strengthens the earlier model-based/model-free amortization theorem with a semantic state criterion.

---

# 8. Partial observability

If raw physical state is not observed, the sufficient control state may be a belief/predictive quotient rather than a partition of raw states.

The bisimulation theorem is therefore a finite fully observed base case. In POMDPs, belief-state/predictive-state theory must be combined with control equivalence.

---

# 9. Developmental implication

A learned world model should not be rewarded merely for pixel/raw-state reconstruction. The protected target is whether its latent state preserves the distinctions needed for future rewards/transitions under the registered goal family.

This provides a zero-prior reason for task-oriented latent world models and for discarding nuisance state detail.

---

# 10. Gap update

`GKF-11` / T7 now has:

```text
Bellman value/policy state                               CLOSED
model/planning vs compiled-policy amortization           CLOSED
finite exact decision-relevant world-state quotient      CLOSED
approximate reward/transition quotient error bound       CLOSED
exploration necessity                                    CLOSED

learned quotient discovery                               OPEN-BLOCKING
partial-observability predictive control quotient        OPEN-BLOCKING
model-error/generalization prediction                    OPEN-BLOCKING
protected world-model vs policy crossover                OPEN-BLOCKING
```

---

# 11. Claim ceiling

This is a finite discounted MDP bisimulation base case. It does not solve representation learning for high-dimensional observations, POMDP state discovery, exploration, or model generalization in real control systems.
