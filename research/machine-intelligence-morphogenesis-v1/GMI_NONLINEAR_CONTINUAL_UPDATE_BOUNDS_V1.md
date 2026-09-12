# GMI Nonlinear Continual-Update Bounds v1

Status: **FORMAL NONLINEAR LOCAL HARDENING / EXACT DIFFERENTIAL BOUNDS**

Status date: 2026-09-12.

Purpose:

> Extend the exact linear retention-safe subspace theory to smooth nonlinear response maps. Quantify when a Jacobian-nullspace update remains approximately retention-safe and when curvature invalidates the linear picture.

---

# 1. Nonlinear old-task response map

Let protected old-task response vector be

\[
g:\mathbb R^d\to\mathbb R^m
\]

with Jacobian

\[
J(\theta)=Dg(\theta).
\]

At current developmental state `theta`, consider update `Delta`.

Assume `J` is `L_J`-Lipschitz on the segment from `theta` to `theta+Delta` in operator norm:

\[
\|J(\theta+u)-J(\theta+v)\|_{op}
\le
L_J\|u-v\|_2.
\]

---

# 2. Exact first-order-null update drift bound

## Theorem NC-1 — quadratic retention drift in a Jacobian-null direction

If

\[
J(\theta)\Delta=0,
\]

then

\[
\|g(\theta+\Delta)-g(\theta)\|_2
\le
\frac{L_J}{2}\|\Delta\|_2^2.
\]

### Proof

By the fundamental theorem of calculus,

\[
g(\theta+\Delta)-g(\theta)
=
\int_0^1J(\theta+t\Delta)\Delta\,dt.
\]

Subtract the zero first-order term `J(theta)Delta`:

\[
=
\int_0^1
[J(\theta+t\Delta)-J(\theta)]\Delta\,dt.
\]

Take norms and apply Jacobian Lipschitzness:

\[
\le
\int_0^1 L_J t\|\Delta\|^2dt
=
\frac{L_J}{2}\|\Delta\|^2.
\]

QED.

### GMI consequence

The exact linear nullspace remains an **approximately safe nonlinear update cone** for sufficiently small updates, with forgetting growing at most quadratically under the registered curvature bound.

---

# 3. Approximate null direction

If

\[
\|J(\theta)\Delta\|\le\epsilon_1,
\]

then

## Corollary NC-1.1

\[
\|g(\theta+\Delta)-g(\theta)\|
\le
\epsilon_1+rac{L_J}{2}\|\Delta\|^2.
\]

Thus old-task drift decomposes into linear interference plus curvature correction.

---

# 4. Safe radius for a retention tolerance

Suppose exact first-order nulling holds and old-task response drift tolerance is `tau>0`.

## Corollary NC-1.2

Any update satisfying

\[
\|\Delta\|
\le
\sqrt{\frac{2\tau}{L_J}}
\]

is guaranteed to remain within the registered old-response tolerance.

### Interpretation

Large nonlinear updates can leave the local safe region even when their initial direction lies in the old-task Jacobian nullspace. This formally motivates small local updates, trust regions, relinearization, replay/verification, or new isolated degrees of freedom.

---

# 5. New-task local reachability with error bound

Let new-task response be

\[
h:\mathbb R^d\to\mathbb R^r
\]

with Jacobian `K(theta)` and `L_K`-Lipschitz Jacobian. For desired local correction `b`, suppose

\[
K(\theta)\Delta=b.
\]

## Theorem NC-2 — nonlinear correction error bound

Actual new-task correction satisfies

\[
\|h(\theta+\Delta)-h(\theta)-b\|
\le
\frac{L_K}{2}\|\Delta\|^2.
\]

The proof is identical to NC-1 after subtracting the first-order term.

### Combined local feasibility

A candidate update in `ker J(theta)` that solves `K(theta)Delta=b` exactly at first order gives old-task error and new-task correction error both `O(||Delta||^2)` inside the registered smoothness region.

---

# 6. Curvature-limited plasticity

The linear theory used safe-subspace dimension

\[
d-\operatorname{rank}J.
\]

The nonlinear theory adds a second coordinate:

\[
L_J
\]

or a more local directional curvature estimate.

Two species can have the same first-order safe dimension but radically different useful update radii because one response map bends much faster.

A zero-prior continual-development predictor should therefore include:

```text
safe-subspace dimension
minimum linear interference
Jacobian curvature / drift
required new-task correction norm
relinearization frequency
verification tolerance
```

---

# 7. Exact immunity from isolated new parameters

If new parameters `phi` are introduced such that

\[
g(\theta,\phi)=g(\theta,0)
\]

for all `phi` in the relevant registered range, then updates in `phi` have exact old-task immunity until the composition/gating contract changes.

### GMI consequence

This is a stronger reason for modular expansion than local Jacobian nullspace when strict retention matters: architectural isolation can create exact semantic separation rather than a small-step approximation.

---

# 8. Negative twin

If `L_J` is very large or the required new-task correction demands a large update norm, the quadratic drift guarantee becomes weak. A locally safe direction can still cause severe forgetting after a large step.

GMI should then predict replay, verification, staged updates, or isolated new degrees of freedom rather than trusting one large nullspace step.

---

# 9. Gap update

`GKF-12 continual development` now has:

```text
exact linear zero-forgetting feasibility                  CLOSED
safe dimension / expansion benefit                       CLOSED
minimum linear interference                              CLOSED
nonlinear Jacobian-null drift bound                      CLOSED
nonlinear new-task local correction bound                CLOSED
exact isolated-module immunity when composition permits  CLOSED

finite-data Jacobian/curvature estimation                OPEN
large nonlocal update geometry                           OPEN-BLOCKING
real replay/adapter/expansion lifecycle prediction       OPEN-BLOCKING
```

---

# 10. Claim ceiling

These are local smoothness bounds. They do not solve global nonlinear continual learning, where Jacobians and representations can change dramatically along the development path.
