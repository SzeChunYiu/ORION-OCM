# GMI Continual-Update Interference Theorems v1

Status: **FORMAL ZERO-PRIOR STRUCTURAL DERIVATION / LINEARIZED EXACT REGIME**

Status date: 2026-09-12.

Purpose:

> Derive replay/local adaptation/parameter expansion pressure from the geometry of retention constraints, rather than treating continual-learning architectures as historical givens.

---

# 1. Linearized task-response model

Let current parameter/developmental state be

\[
\theta\in\mathbb R^d.
\]

For a frozen collection of old protected obligations, let their first-order/exact linear response to a parameter update be represented by

\[
A_{old}\Delta\theta.
\]

For a new obligation, let required response correction be `b`, with response matrix `A_new`:

\[
A_{new}\Delta\theta=b.
\]

Exact old-task retention requires

\[
A_{old}\Delta\theta=0.
\]

---

# 2. Retention-safe update criterion

## Theorem CL-1 — exact zero-forgetting feasibility

There exists an update that exactly preserves all old registered responses while achieving the required new correction iff

\[
b\in A_{new}(\ker A_{old}).
\]

### Proof

Retention requires `Delta theta in ker A_old`. Among such updates, the reachable new-task corrections are exactly the image of `ker A_old` under `A_new`. QED.

### Interpretation

The relevant GMI variable is not merely task similarity. It is whether the new semantic correction is reachable inside the **retention-safe update subspace**.

---

# 3. Dimension of retention-safe plasticity

## Theorem CL-2 — safe update degrees of freedom

The dimension of the exact old-task retention-safe subspace is

\[
d_{safe}=d-\operatorname{rank}(A_{old}).
\]

As old protected obligations constrain more independent parameter directions, remaining exact plasticity shrinks.

### Negative twin

If

\[
\operatorname{rank}(A_{old})=d,
\]

then `ker A_old={0}`. No nonzero exact shared-parameter update can preserve all old responses. Any genuinely new correction requires one of:

```text
relaxing retention
adding new degrees of freedom
changing representation/factorization
external memory/tool state
replay/retraining that moves old and new constraints jointly
```

---

# 4. Why parameter expansion/adapters can become necessary

Augment the parameter state with `k` new coordinates `phi` that do not affect old tasks:

\[
A'_{old}=[A_{old}\;0].
\]

Let the new-task response be

\[
A'_{new}=[A_{new}\;B].
\]

## Theorem CL-3 — expansion enlarges the retention-safe image

The retention-safe correction set after expansion is

\[
A_{new}(\ker A_{old})+\operatorname{im}(B).
\]

Thus expansion can make previously unreachable zero-forgetting corrections reachable.

### Consequence

A local adapter/new module is structurally justified when the desired correction has a component outside the old retention-safe image but inside the image created by the new degrees of freedom.

This is a property-level derivation of expandable/local adaptation without assuming LoRA, adapters or progressive networks by name.

---

# 5. Minimum retention violation when exact safety is impossible

Suppose exact retention is relaxed. For a required new correction `A_new Delta theta=b`, define old-task interference

\[
I(\Delta\theta)=\|A_{old}\Delta\theta\|_2^2.
\]

## Theorem CL-4 — constrained minimum-interference update

The best shared-parameter update solves

\[
I^*(b)=
\min_{\Delta\theta:A_{new}\Delta\theta=b}
\|A_{old}\Delta\theta\|_2^2.
\]

`I*(b)=0` iff the CL-1 feasibility condition holds.

Therefore `I*(b)` is an exact linear-regime interference coordinate.

### GMI phase interpretation

```text
I*(b)=0 and update burden low:
    shared/local parameter update can preserve retention

I*(b)>0 but replay can cheaply move old/new targets jointly:
    replay/retraining regime

I*(b) high and new safe degrees cheap:
    adapter/expansion/modularization regime

volatile exact distinctions with cheap explicit writes:
    external memory regime may dominate parameter change
```

---

# 6. Multiple sequential tasks and plasticity depletion

After tasks `1,...,t` become protected, stack their response constraints into

\[
A_{1:t}.
\]

## Corollary CL-4.1

Exact retention-safe dimension is

\[
d-\operatorname{rank}(A_{1:t}).
\]

It is nonincreasing as independent protected constraints accumulate.

This yields an exact linearized form of **plasticity depletion**: a fixed shared parameter state can lose safe update directions even before optimization difficulty is considered.

Parameter expansion, factorization, selective authority, or forgetting can restore effective plasticity.

---

# 7. Update locality theorem

Suppose parameter coordinates are partitioned into blocks and old-task response matrix has zero columns on block `J`.

## Theorem CL-5 — exact locality immunity

Any update supported only on `J` causes exactly zero first-order/exact-linear change to the registered old-task responses.

### Consequence

If new corrections are reachable through such a block, local modular update has zero registered interference by construction. This is the clean structural reason locality/versioning can dominate global retraining in some ecologies.

---

# 8. Zero-prior continual-development variables

The theorem layer identifies measurable structural coordinates:

```text
rank(A_old) / safe-subspace dimension
new-correction projection onto safe image
minimum interference I*(b)
update support locality
cost of new degrees of freedom
replay/retraining cost
retention strictness
update/revision horizon
```

These variables should predict transitions among shared update, replay, local adapter, parameter expansion, external memory and morphology change.

---

# 9. Gap update

`GKF-12 continual-development architecture` is no longer structurally untyped.

Closed in exact linearized regime:

```text
zero-forgetting feasibility
safe plasticity dimension
expansion benefit
minimum interference objective
local-update immunity
```

Still open:

```text
nonlinear response/Jacobian drift across large updates
finite-data estimation of task-response subspaces
optimization accessibility
stochastic/nonstationary tasks
real replay/expansion/memory lifecycle crossover
```

---

# 10. Claim ceiling

These are exact linear/linearized structural theorems. They do not prove a universal theory of catastrophic forgetting in nonlinear neural networks. They define the base case that any broader GMI continual-development theory must recover.
