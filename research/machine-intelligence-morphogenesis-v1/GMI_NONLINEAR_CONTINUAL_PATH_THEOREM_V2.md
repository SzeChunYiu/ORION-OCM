# GMI nonlinear continual path theorem v2

Status: **FORMAL GLOBAL-PATH HARDENING / T8 NARROWING**

Date: 2026-09-12.

Purpose: extend local Jacobian-null update bounds to finite large developmental motion by tracking the old-task level set along the whole path.

## 1. Old-task response geometry

Let

\[
g:\mathbb R^d\to\mathbb R^m
\]

be continuously differentiable. Let `theta:[0,T]->R^d` be an absolutely continuous developmental path with Jacobian

\[
J_g(\theta)=Dg(\theta).
\]

## 2. Theorem CP-1 — exact retention along a tangent path

If

\[
J_g(\theta(t))\dot\theta(t)=0
\]

for almost every `t in [0,T]`, then

\[
g(\theta(T))=g(\theta(0)).
\]

### Proof

By the chain rule for absolutely continuous paths,

\[
\frac{d}{dt}g(\theta(t))=J_g(\theta(t))\dot\theta(t)=0
\]

almost everywhere. Integrating gives constant old-task response along the full path. QED.

Thus a large total parameter displacement need not cause forgetting if development continuously follows the instantaneous retention-safe tangent distribution.

## 3. Theorem CP-2 — integrated approximate retention

If instead

\[
\|J_g(\theta(t))\dot\theta(t)\|\le \epsilon(t)
\]

almost everywhere, then

\[
\|g(\theta(T))-g(\theta(0))\|
\le
\int_0^T\epsilon(t)\,dt.
\]

This makes cumulative forgetting a path integral of instantaneous interference rather than a function of endpoint distance alone.

## 4. Discrete relinearization corollary

For finite updates `Delta_i` at states `theta_i`, suppose

\[
\|J_g(\theta_i)\Delta_i\|\le \epsilon_i
\]

and the Jacobian is `L_i`-Lipschitz along each step. Applying the v1 local theorem and the triangle inequality gives

\[
\|g(\theta_K)-g(\theta_0)\|
\le
\sum_{i=0}^{K-1}
\left(
\epsilon_i+\frac{L_i}{2}\|\Delta_i\|^2
\right).
\]

Hence smaller relinearized steps can trade additional development/verification cost for a provable global retention budget.

## 5. Feasibility obstruction

Exact tangent retention is useful only if the new-task objective has a descent/progress direction inside the tangent space

\[
\ker J_g(\theta).
\]

If every direction achieving required new-task progress has nonzero old-task derivative at some necessary region, exact retention within the existing parameterization is impossible along that route. Options then include:

```text
accept bounded forgetting
replay/rehearsal and repair
introduce isolated new parameters/modules
change routing/authority contracts
expand morphology so a new tangent direction exists
```

This is the nonlinear analogue of the exact linear safe-image condition.

## 6. Topological caveat

The old-response level set may have disconnected components or singular points. A desired new solution can exist with the same old outputs yet be unreachable by a continuous tangent path inside the current component. Local nullspace dimension alone does not guarantee global reachability.

This turns the remaining large-update problem into a concrete geometric question: connectivity and task progress on the registered old-response level set.

## 7. GMI consequence

Continual-development descriptors now include:

```text
instantaneous safe tangent dimension
new-task gradient projection into that tangent
path-integrated interference
curvature / relinearization burden
level-set connectivity
module-expansion cost
retention tolerance
```

## Claim ceiling

This closes a global differential retention law for known smooth response maps. Estimating the tangent field, finding feasible paths in high-dimensional learned systems, handling representation discontinuities and predicting replay/adapter/expansion lifecycle crossovers remain OPEN-BLOCKING.
