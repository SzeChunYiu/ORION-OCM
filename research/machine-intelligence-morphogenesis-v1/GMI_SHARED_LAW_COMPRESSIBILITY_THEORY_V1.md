# GMI Shared-Law Compressibility Theory v1

Status: **FORMAL P0 ZERO-PRIOR GAP CLOSURE / FINITE EXACT SCOPE**

Status date: 2026-09-12.

Purpose:

> Close the first part of GKF-01 by deriving when a reusable shared-law representation can be information-theoretically smaller than exact exemplar memory. This is a structural prerequisite for deriving regression, basis/kernel models and compressed learned maps from zero prior.

---

# 1. Finite obligation family

Let there be `N` distinguishable query points and an output alphabet of size `q`.

The unrestricted exact target family is

\[
\mathcal U=\{f:X\to Y\},
\qquad
|\mathcal U|=q^N.
\]

Let a registered structured hypothesis family be

\[
\mathcal H\subseteq\mathcal U,
\qquad
|\mathcal H|=M.
\]

The decoder/evaluator for `H` is treated as fixed shared machinery; developmental state must identify the active member.

---

# 2. Theorem SC-1 — unrestricted exact map lower bound

Any exact developmental state that can represent every member of `U` requires at least

\[
\log_2|\mathcal U|=N\log_2 q
\]

bits in the worst case.

A direct lookup table meets this order.

---

# 3. Theorem SC-2 — structured family state bound

If legal prior knowledge restricts the target to `H`, any exact state identifying every possible member of `H` requires at least

\[
\log_2 M
\]

bits, and an index of the member achieves

\[
\lceil\log_2 M\rceil
\]

bits apart from the fixed decoder.

Thus the exact representation advantage relative to arbitrary lookup can be as large as

\[
N\log_2 q-\log_2 M.
\]

---

# 4. Structural compressibility ratio

Define

\[
\kappa_{law}
=
\frac{\log_2 M}{N\log_2 q}.
\]

Interpretation:

```text
kappa_law ~ 1
    registered shared law gives little exact state compression over arbitrary memory

kappa_law << 1
    target family admits strong reusable structural compression
```

This is a family-level theoretical coordinate, not yet an estimator from finite observations.

---

# 5. Corollary SC-2.1 — finite-precision coefficient family

Suppose a coefficient realization uses `d` coefficients, each represented with at most `b` bits, and the evaluation map is fixed. Then the number of distinct coefficient states is at most

\[
2^{bd}.
\]

Therefore the active exact coefficient state requires at most `bd` bits, and the structural compression ratio satisfies

\[
\kappa_{coef}
\le
\frac{bd}{N\log_2 q}
\]

whenever the target family is actually contained in the coefficient family at the registered precision.

This is the information-theoretic reason a low-dimensional stable regression law can dominate explicit storage as `N` grows.

---

# 6. Corollary SC-2.2 — basis/kernel coefficient state

If a fixed basis dictionary contains `r` reusable basis functions and only their finite-precision weights vary, the same bound applies with coefficient description `br` bits.

Thus basis/kernel-style state is predicted when:

```text
one reusable basis relation serves many queries;
registered precision is finite;
required basis count grows much slower than the number of independent records.
```

This does not select a particular kernel. Kernel/feature geometry remains a separate gap.

---

# 7. Update volatility and the memory counter-pressure

Compression alone is not enough. Let independent updates arrive to individual key values.

Suppose:

```text
c_mem_update      burden of replacing one explicit record
c_law_update      burden of refitting/updating shared-law state
lambda            expected independent update count
```

Ignoring serving differences, explicit memory has lower update burden when

\[
\lambda c_{mem\_update}
<
\lambda c_{law\_update}.
\]

More importantly, if updates are arbitrary and can move the target outside `H`, the shared-law exactness assumption fails completely while lookup remains closed under arbitrary point replacement.

### Closure distinction

A family `H` is **update-closed** under intervention set `J` if every legal update maps a member of `H` to another member of `H`.

If `H` is not update-closed and exact admissibility is required, shared-law state needs either:

```text
family expansion;
residual memory;
full exemplar storage;
or abstention/reverification.
```

This formally links shared-law compression to the predictive-residual/RAG programme.

---

# 8. Theorem SC-3 — arbitrary point updates destroy nontrivial exact compression in the worst case

Suppose the legal update class can independently set each of the `N` outputs to any of `q` values. Then the reachable target family from development is all of `U`, so any exact closed developmental state requires at least

\[
N\log_2 q
\]

bits.

Therefore no fixed smaller exact shared-law family can remain sufficient under unrestricted independent point updates without an auxiliary residual state.

---

# 9. Reuse and total lifecycle crossover

Let

```text
C_law       development/refit burden for shared-law state
C_mem       development burden for explicit memory
s_law       serve cost per query for law evaluation
s_mem       serve cost per query for memory retrieval
R           expected query reuse
```

The shared-law realization has lower total burden iff

\[
C_{law}+Rs_{law}
<
C_{mem}+Rs_{mem},
\]

or, when `s_mem>s_law`,

\[
R>
\frac{C_{law}-C_{mem}}{s_{mem}-s_{law}}.
\]

Thus strong structural compression can still lose at short reuse if fitting is expensive.

---

# 10. Negative twins

The theory predicts opposite realization pressure in matched worlds:

```text
Twin A — shared law
    low M relative to q^N
    stable/update-closed family
    high reuse
    -> coefficient/basis compression favored

Twin B — independent volatile records
    reachable family q^N
    arbitrary local updates
    exact provenance/identity required
    -> explicit memory/residual state favored
```

The transition should be continuous when real systems lie between these extremes.

---

# 11. What remains open in GKF-01

The exact finite theory identifies the right latent quantity:

\[
\log_2|\mathcal H_{effective}|
\]

or an approximate rate-distortion/description analogue.

What remains blocking is estimating that quantity **before protected outcomes** in realistic high-dimensional data without leaking family/world identity.

Required empirical estimator programme:

```text
synthetic worlds with known minimal family size/description
MDL/compression competitors
predictive residual tests
held-family generalization
semantic remint
coefficient-vs-memory crossover prediction
```

A successful estimator would close a central zero-prior gap shared by regression, kernels, neural compression, RAG and continual memory.

---

# 12. Claim ceiling

Closed:

> exact finite information-theoretic compression and update-closure laws selecting shared-law versus arbitrary exemplar state.

Open:

> realistic pre-outcome estimation of effective semantic function-family complexity and approximate compression under noise/generalization.

Status update:

`GKF-01 = FORMAL_CORE_CLOSED__ESTIMATOR_OPEN`.
