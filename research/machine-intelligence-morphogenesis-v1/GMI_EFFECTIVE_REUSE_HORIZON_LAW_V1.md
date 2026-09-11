# GMI Effective Reuse Horizon Law v1

Status: **CROSS-PARADIGM LIFECYCLE LAW — ELEMENTARY/PARENT-OWNED, ADOPTED INTO GMI**

Refs: `GMI_DEVELOPMENTAL_REALIZATION_PRINCIPLE_V1.md`, `GMI_REALIZATION_DEMAND_SIGNATURE_V1.md`, #323, #233, #377.

## 1. Purpose

Across program libraries, materialized indexes, trained models, compiled representations, preconditioners and other reusable cognitive structures, the same higher-order question recurs:

> Does the structure remain useful for enough future applications to repay the cost of acquiring/building it before it is invalidated, retired or reset?

The internal mechanism can be completely different across morphology families.

The lifecycle arithmetic does not need to be.

---

# 2. Deterministic horizon

Let a reusable realization change have:

```text
A       one-time extra acquisition/build/discovery cost
M       fixed maintenance cost over the registered horizon
Delta   expected serving saving per useful application relative to a matched parent
H_eff   number of useful applications before invalidation/retirement/reset
```

with all quantities measured in the same prospectively declared scalar cost coordinate.

Then the structure is lifecycle-beneficial iff

\[
\boxed{
H_{eff}\,\Delta > A+M.
}
\]

Break-even:

\[
\boxed{
H^* = \frac{A+M}{\Delta}
}
\]

when `Delta > 0`.

This is ordinary amortization arithmetic.

It is not an ORION novelty claim.

---

# 3. Hazard-adjusted effective horizon

Suppose:

- at most `H` future opportunities exist;
- the reusable structure is initially valid;
- after each useful application it survives to the next opportunity with probability `s=1-q`;
- `q` is a fixed per-opportunity invalidation hazard;
- after invalidation this one-shot structure produces no further savings during the registered horizon;
- survival events follow the stated independent geometric model.

Then the probability that the structure is still valid at opportunity `t` is

\[
(1-q)^{t-1}.
\]

The expected useful reuse count is

\[
\eta(H,q)
=
\sum_{t=1}^{H}(1-q)^{t-1}.
\]

Therefore

\[
\boxed{
\eta(H,q)
=
\begin{cases}
H,& q=0,\\[4pt]
\dfrac{1-(1-q)^H}{q},&0<q\le 1.
\end{cases}
}
\]

and expected net lifecycle gain is

\[
\boxed{
G(H,q)=\eta(H,q)\,\Delta-(A+M).
}
\]

The reusable structure is expected-beneficial under this model iff

\[
\eta(H,q)\,\Delta > A+M.
\]

---

# 4. Infinite-opportunity ceiling under drift

For any fixed `q>0`, as `H -> infinity`,

\[
\eta(H,q)\to\frac{1}{q}.
\]

Therefore even an arbitrarily long nominal future horizon cannot repay a build cost if

\[
\boxed{
\frac{\Delta}{q}\le A+M.
}
\]

under this one-shot invalidation model.

This is a useful conceptual boundary:

```text
long chronological horizon
!=
long useful reuse horizon
```

when drift/invalidation is substantial.

---

# 5. Cross-paradigm interpretation

The same law can be instantiated without identifying the internal response variables.

## Program/library morphology

```text
A     mining + validation + applicability-policy construction
Delta saved search/verification work per applicable future target
q     probability library/method becomes invalid/inapplicable before next opportunity
```

#323 directly measures large one-time acquisition charges and target-count break-even regimes in program search.

## Differentiable/neural morphology

```text
A     training / representation / preconditioner / adaptation cost
Delta saved inference or future-learning burden per useful task/query
q     regime drift / task-distribution change / model invalidation / plasticity failure
```

The differentiable DS-E1 microscope already shows a build-heavy preconditioned update law crossing a cheap-build vanilla law when the reuse horizon increases.

## Database/index/materialized realization

```text
A     index/view construction
Delta query savings
q     invalidation/update hazard
```

This is standard lifecycle economics and a direct parent.

## Bayesian/probabilistic realization

Possible instantiations include reusable posterior summaries, sufficient-statistic caches or learned prior/meta-prior structures, but the mapping must be explicit. A Bayesian model's KL or information gain is not automatically `Delta`.

## Symbolic/proof realization

```text
A     theorem/library/index/method construction
Delta future search/checking savings
q     definition/library/version/scope invalidation
```

---

# 6. Why this is a genuine GMI-level law even though it is not novel mathematics

The law is architecture-neutral because it operates on lifecycle quantities that every reusable realization must expose:

```text
construction burden
per-use benefit
useful lifetime / invalidation
maintenance
```

It does **not** assert that code length, gradient conditioning, Bayesian KL and symbolic branching are one quantity.

Those remain family-native response variables that determine `A`, `Delta`, `q` and the distribution of useful opportunities.

Thus GMI can legitimately adopt the parent theorem as a cross-paradigm module:

\[
\text{family-native mechanism}
\to
(A,\Delta,q,H,M)
\to
\text{lifecycle frontier consequence}.
\]

This is a stronger and cleaner form of generality than relabelling family-specific metrics.

---

# 7. Relation to demand signature v1

The law gives precise semantics to two candidate demand variables:

```text
eta = effective useful reuse opportunity
nu  = invalidation/drift process
```

But the realized `q` may depend jointly on obligation drift and morphology robustness.

Therefore distinguish:

```text
nu_Omega       external ecology invalidation process
r_M(nu_Omega)  morphology response / probability its learned structure remains useful
```

The hazard `q` used in a concrete lifecycle model is generally a **demand-response result**, not purely an obligation feature.

This is another reason to preserve the demand/response split.

---

# 8. Retention/plasticity extension

If retaining the reusable structure reduces future learning capacity, represent the resulting expected burden explicitly rather than treating memory as free.

For example:

\[
G
=
\eta\Delta
-
(A+M+C_{plasticity}+C_{revision}+C_{negative\ transfer}).
\]

This remains bookkeeping until the quantities are operationally defined and measured.

No universal scalar prices are assumed.

---

# 9. Rebuild/renewal boundary

The geometric one-shot model above ends savings after invalidation.

If the system may pay to rebuild/retrain, the process becomes a renewal/control problem.

Then the correct parent is not the one-shot equation alone; use renewal theory, nonstationary learning, cache/view maintenance, metareasoning or the appropriate family-native control formulation.

Do not reuse the one-shot formula outside its assumptions.

---

# 10. Vector/Pareto boundary

If costs are vectors rather than one prospectively valued scalar, do not write

```text
eta * Delta > A
```

as if vector `>` were total.

Instead retain the vector change

\[
\Delta B_{life}
=
(A+M)-\eta\Delta
\]

coordinate-wise and evaluate Pareto dominance or a prospectively declared valuation.

---

# 11. Registered propositions

## GMI-RP13a — deterministic effective-horizon break-even

Under the scalar assumptions above, a reusable structure is lifecycle-beneficial iff

\[
H_{eff}\Delta>A+M.
\]

## GMI-RP13b — geometric hazard effective horizon

Under the stated one-shot independent invalidation model,

\[
\eta(H,q)=\frac{1-(1-q)^H}{q}
\]

for `q>0`, with continuous limit `eta(H,0)=H`.

## GMI-RP13c — drift ceiling

For fixed `q>0`,

\[
\eta(\infty,q)=1/q.
\]

Thus if

\[
\Delta/q\le A+M,
\]

no nominal horizon can make the one-shot reusable structure expected-profitable under the model.

Parent ownership:

```text
geometric survival + elementary amortization / lifecycle economics
```

GMI contribution:

```text
common lifecycle semantics across heterogeneous cognitive realizations
```

---

# 12. Falsifiers / misuse alarms

```text
INVALID_HAZARD_MODEL
INDEPENDENCE_ASSUMPTION_UNJUSTIFIED
REBUILD_IGNORED
NEGATIVE_TRANSFER_UNCHARGED
MAINTENANCE_UNCHARGED
SERVING_SAVING_NOT_MATCHED_CAPABILITY
POST_HOC_SCALARIZATION
DRIFT_MEASURED_ONLY_AFTER_PROTECTED_OUTCOME
```

---

# 13. Current terminal

```text
GMI_EFFECTIVE_REUSE_HORIZON_LAW_ADOPTED_V1
```

Claim ceiling:

> architecture-neutral lifecycle theorem module, parent-owned mathematics; useful for GMI realization/development theory but not a novel general intelligence discovery by itself.
