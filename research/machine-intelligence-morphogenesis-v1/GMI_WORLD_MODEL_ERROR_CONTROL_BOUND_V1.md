# GMI world-model error control bound v1

Status: **FORMAL MODEL-ERROR RESPONSE LAW / GKF-11, R6 NARROWING**

Date: 2026-09-12.

Purpose: quantify when the reuse advantage of a learned world model is erased by reward/transition error.

## 1. Two discounted MDPs

Let true MDP `M` and learned/model MDP `Mhat` share finite state/action spaces and discount `0<=gamma<1`.

Rewards satisfy

\[
0\le r,\hat r\le R_{max}
\]

and uniformly

\[
|r(s,a)-\hat r(s,a)|\le\epsilon_r.
\]

Let total variation use the convention

\[
TV(P,Q)=\sup_A|P(A)-Q(A)|=\frac12\|P-Q\|_1.
\]

Assume

\[
TV(P(\cdot|s,a),\hat P(\cdot|s,a))\le\epsilon_p
\]

for all state-action pairs.

## 2. Theorem WM-1 — fixed-policy value error

For any stationary policy `pi`,

\[
\boxed{
\|V_M^\pi-V_{\hat M}^\pi\|_\infty
\le
\frac{\epsilon_r}{1-\gamma}
+
\frac{\gamma R_{max}\epsilon_p}{(1-\gamma)^2}
=:E_{model}
}.
\]

### Proof

Bellman equations give

\[
V_M^\pi-V_{\hat M}^\pi
=(r_\pi-\hat r_\pi)
+\gamma P_\pi(V_M^\pi-V_{\hat M}^\pi)
+\gamma(P_\pi-\hat P_\pi)V_{\hat M}^\pi.
\]

The first term is at most `epsilon_r`. The second is at most `gamma` times the sup-norm value error. Since rewards are in `[0,Rmax]`, `V_{Mhat}^pi` lies in `[0,Rmax/(1-gamma)]`. Difference of expectations of a function with range at most `Rmax/(1-gamma)` is bounded by that range times TV, so the third term is at most

\[
\gamma\epsilon_p\frac{R_{max}}{1-\gamma}.
\]

Rearrange. QED.

## 3. Theorem WM-2 — policy optimized in the learned model

Let

\[
\hat\pi\in\arg\max_\pi V_{\hat M}^\pi
\]

and let `pi*` be true-optimal. Then pointwise

\[
\boxed{
V_M^{\pi^*}-V_M^{\hat\pi}
\le 2E_{model}
}.
\]

### Proof

Add and subtract learned-model values:

\[
V_M^{\pi^*}-V_M^{\hat\pi}
=
(V_M^{\pi^*}-V_{\hat M}^{\pi^*})
+(V_{\hat M}^{\pi^*}-V_{\hat M}^{\hat\pi})
+(V_{\hat M}^{\hat\pi}-V_M^{\hat\pi}).
\]

The middle term is nonpositive by optimality of `hat pi`; each outer term is bounded by `E_model`. QED.

## 4. Lifecycle crossover refinement

Suppose a reusable model+planner realization has lifecycle burden advantage `G_reuse` over direct policy/value development **when quality is matched**. A sufficient condition for the model route to remain preferable under a scalarized protected loss price `lambda` is roughly

\[
G_{reuse}>2\lambda E_{model}
\]

plus any extra planning/serve burden not already included in `G_reuse`.

The exact registered comparison should use the full burden vector and quality constitution, but the theorem gives a principled model-bias penalty.

## 5. Negative twins

- As `gamma -> 1`, small one-step model errors can have large long-horizon effect.
- Errors concentrated on unreachable states can make the uniform bound loose; occupancy-weighted bounds may be sharper.
- Under partial observability, belief/model-state error must be included; a fully observed MDP bound is insufficient.
- A model-free policy also has estimation/generalization error; this theorem does not assume it is perfect.

## GMI consequence

Zero-prior model-based/model-free prediction should measure:

```text
model reward error interval
transition TV / task-relevant transition error
horizon/discount
model reuse across goals
planning/serve price
policy/value learning burden
quality/risk tolerance
```

## Claim ceiling

This closes a finite discounted-MDP model-error penalty. Learned-model estimation, exploration, occupancy-adaptive bounds, POMDP approximation and protected lifecycle crossover remain OPEN-BLOCKING.
