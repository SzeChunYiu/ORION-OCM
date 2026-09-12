# GMI P0 Zero-Prior Response Theorems v1

Status: **FORMAL ZERO-PRIOR HARDENING / EXACT FINITE THEORY — EMPIRICAL CLOSURE STILL OPEN**

Status date: 2026-09-12.

Purpose:

> Close the theorem-heavy core of the highest-priority known-form derivation gaps: shared-law compression versus explicit memory, static versus dynamic routing, finite predictive-state dimension, residual/low-rank adaptation complexity, and conditional specialization.

This document does not claim real-world closure. It isolates exact parts of the response laws so that only measurable pre-outcome estimators and protected empirical transfer remain open.

---

# 1. Shared-law state plus sparse residual memory

Let the registered query set have `N` distinguishable points and output alphabet size `q>=2`. Let `h` be a known base law. Consider all targets that differ from `h` on at most `r` query points.

Define

\[
S(N,q,r)=\sum_{j=0}^{r}{N\choose j}(q-1)^j.
\]

## Theorem P0-1 — exact sparse-residual cardinality

The number of targets within Hamming radius `r` of `h` is exactly

\[
S(N,q,r).
\]

Therefore any exact developmental state that can identify every such target requires at least

\[
B_{res}(N,q,r)=\left\lceil \log_2 S(N,q,r)\right\rceil
\]

bits in the worst case.

### Proof

Choose exactly `j` overridden query positions in `{N \choose j}` ways. At each overridden position choose one of the `q-1` values different from the base value. Summing over `0<=j<=r` gives the result. QED.

## Corollary P0-1.1 — multiple separated base laws

Let a base-law family `H={h_1,...,h_M}` have pairwise Hamming distance greater than `2r`. Then the radius-`r` Hamming balls around the base laws are disjoint, so the exact target family has cardinality

\[
M S(N,q,r),
\]

and exact state requires at least

\[
\left\lceil \log_2(MS(N,q,r))\right\rceil
\]

bits.

An enumerative code over `(base law, residual pattern)` achieves this cardinality order exactly.

## Corollary P0-1.2 — compression crossover

An unrestricted exact record table over `N` queries requires

\[
B_{table}=N\log_2 q
\]

bits of target identity information.

Therefore shared-law-plus-residual representation is information-theoretically smaller exactly when

\[
\log_2 M+\log_2 S(N,q,r)<N\log_2 q
\]

(up to integer code rounding).

At `r=N`,

\[
S(N,q,N)=q^N,
\]

so unrestricted independent updates destroy the nontrivial compression advantage.

### GMI derivation consequence

This gives a common derivation axis for:

```text
compact coefficient/basis model     small base-law complexity, small residual
external memory / RAG               stable base law + sparse volatile residual
local adapters / residual updates   structured low-complexity residual
full explicit memory                residual approaches unrestricted target family
```

The remaining empirical gap is estimating effective base-family size / residual radius (or an approximate rate-distortion analogue) before protected outcomes.

### Negative twin

If every query may change independently and exactness is required, `r=N` and the target family has `q^N` states. No exact shared-law compression below the arbitrary-table information bound is possible without additional structure.

---

# 2. Static versus dynamic dependency routing

Let `X` be a finite ecology of query/input types. Every `x in X` has a required dependency-edge set `E_x` drawn from a universal edge set `U_0`.

Let

\[
U=\bigcup_{x\in X}E_x.
\]

Assume that omitting any required edge makes the realization semantically inadmissible for that input.

## Theorem P0-2 — static exact routing union lower bound

Every single static routing mask `S` that is exact for all inputs must satisfy

\[
U\subseteq S.
\]

Hence its minimum active-edge count is exactly `|U|`.

### Proof

For every edge `e in U`, there exists an input `x` with `e in E_x`. Exactness on that input requires `e in S`. Thus all edges in the union are necessary. Choosing `S=U` is sufficient. QED.

## Theorem P0-3 — exact dynamic-routing burden crossover

Suppose active-edge burden is `c_e>0` per edge per query. An oracle dynamic router activates exactly `E_x` and pays per-query routing burden `c_r>=0`.

Let

\[
\bar e=\mathbb E_x|E_x|.
\]

Then

\[
C_{static}=c_e|U|,
\]

while

\[
C_{dyn}=c_r+c_e\bar e.
\]

Dynamic exact routing is cheaper iff

\[
c_r<c_e(|U|-\bar e).
\]

If router failure probability is `p_r` and a failure incurs registered semantic/risk penalty `lambda`, then dynamic routing is favored under the scalarized burden iff

\[
c_r+\lambda p_r<c_e(|U|-\bar e).
\]

### Negative twin

If `E_x` is the same for every input, then `|U|=\bar e`. There is no routing-opportunity gap; any positive router burden makes dynamic routing strictly worse.

### GMI derivation consequence

The architecture-neutral predictor is not the word `attention`; it is

\[
\Delta_{route}=|U|-\mathbb E|E_x|,
\]

combined with router discovery/error cost. Large positive `Delta_route` predicts a niche for input-dependent routing; zero predicts fixed routing.

The remaining gap is a pre-outcome estimator of the unknown required dependency sets and router error/cost in real tasks.

---

# 3. Approximate predictive-state lower bound

For each legal history `h`, let `P_h` be the protected distribution over registered future response traces under a frozen continuation protocol. Let total-variation distance be `d_TV`.

A state encoder `s(h)` with decoder distribution `Q_{s(h)}` is `epsilon`-predictively sufficient if

\[
d_{TV}(P_h,Q_{s(h)})\le\epsilon
\]

for every registered history.

## Theorem P0-4 — predictive-distribution packing lower bound

Let `H_0` be a set of `K` histories whose future distributions satisfy

\[
d_{TV}(P_h,P_{h'})>2\epsilon
\]

for every distinct `h,h' in H_0`.

Then every `epsilon`-predictively sufficient state must assign distinct states to all histories in `H_0`. Therefore it needs at least `K` states and at least

\[
\lceil\log_2K\rceil
\]

bits.

### Proof

If two such histories shared one state `z`, then by the triangle inequality

\[
d_{TV}(P_h,P_{h'})
\le d_{TV}(P_h,Q_z)+d_{TV}(Q_z,P_{h'})
\le2\epsilon,
\]

contradiction. QED.

## Corollary P0-4.1

The `2epsilon` packing number of the future-response family is a lower bound on approximate recurrent/predictive-state cardinality.

At `epsilon=0`, this reduces to the exact future-response quotient theorem.

### Negative twin

If all registered future distributions lie inside one `2epsilon` ball, this theorem yields no multi-state lower bound; persistent fine-grained state may be unnecessary at the registered tolerance.

### GMI derivation consequence

This converts the recurrent-state gap into a measurable geometric target: estimate packing/covering complexity of future-response distributions rather than guessing an architecture-specific hidden dimension.

---

# 4. Exact low-rank residual state over finite fields

To isolate the information geometry of low-rank adaptation without real-valued precision loopholes, consider `m x n` residual matrices over the finite field `F_q`.

## Theorem P0-5 — exact count of rank-r residual matrices

The number of `m x n` matrices over `F_q` having rank exactly `r` is

\[
N_{m,n,r}(q)
=
\prod_{i=0}^{r-1}
\frac{(q^m-q^i)(q^n-q^i)}{q^r-q^i}.
\]

Therefore exact identification of an arbitrary residual of rank at most `r` requires at least

\[
B_{rank\le r}
=
\left\lceil
\log_2
\sum_{j=0}^{r}N_{m,n,j}(q)
\right\rceil
\]

bits.

A factorized realization `UV` with `U in F_q^{m x r}` and `V in F_q^{r x n}` gives a constructive upper bound of

\[
r(m+n)\log_2q
\]

bits before quotienting non-unique factorizations.

### Consequence

When a required update has small exact/effective rank relative to `min(m,n)`, a residual factorization can have much lower update burden than rewriting an arbitrary full `m x n` state. As rank approaches full rank, the advantage disappears.

### Negative twin

For arbitrary full-rank residuals, low-rank factorization no longer spans the target family. The update must either increase rank or use a different realization.

### GMI derivation consequence

This is the exact finite analogue of the property-level derivation behind low-rank adapters. The open real-valued gap is estimating protected effective residual rank under bounded precision and nonlinear layer composition.

---

# 5. Conditional specialization: what information theory does and does not derive

Consider `m` observable modes. In each mode, a target is an arbitrary table over `N` distinguishable queries with alphabet size `q`.

The joint target family contains

\[
q^{mN}
\]

independent mode-table combinations.

## Theorem P0-6 — independent modes admit no exact state compression from parameter sharing alone

Any exact representation capable of all independent mode tables requires at least

\[
mN\log_2q
\]

bits of target identity information.

A factorized store with one exact table per mode achieves this order.

Therefore conditional specialization does not, by itself, create an information-theoretic parameter-count advantage when mode functions are independent.

## Theorem P0-7 — routing can reduce execute-all serving burden

If evaluating one mode-specific block costs `c_e`, executing all `m` blocks costs `mc_e`. If the active mode is known/identified and routing costs `c_r`, routed execution costs

\[
c_r+c_e.
\]

Routing beats execute-all evaluation iff

\[
c_r<(m-1)c_e.
\]

However, a monolithic conditional program that branches on the observed mode may match the same asymptotic serving burden.

### Important negative result

These theorems derive **conditional computation**, not a unique Mixture-of-Experts architecture. To derive expert factorization rather than generic conditional branching, GMI still needs a law involving function overlap, interference, optimization accessibility, communication/load-balance cost, and shared-versus-specialized parameter efficiency.

This keeps `GKF-06 conditional specialization` open but much narrower.

---

# 6. Updated zero-prior gap status

The exact theorem layer now closes the following atoms:

```text
GKF-01 shared-law compressibility:
    exact finite family/radius information law CLOSED
    real pre-outcome compressibility estimator OPEN

GKF-05 dependency geometry:
    exact static-union and dynamic-routing crossover CLOSED
    required-edge discovery/router error estimator OPEN

GKF-07 recurrent/predictive state:
    exact quotient + approximate packing lower bound CLOSED
    finite-data predictive packing estimator OPEN

GKF-08 residual complexity:
    finite sparse-residual and finite-field low-rank laws CLOSED
    real semantic residual/rank estimator OPEN

GKF-06 conditional specialization:
    independent-mode information lower bound and execute-all routing crossover CLOSED
    expert-vs-generic-conditional factorization law OPEN
```

---

# 7. Claim ceiling

These results strengthen zero-prior property derivation. They do not establish:

```text
real neural optimization reachability
real router learnability
real effective residual rank
real predictive-state dimension
MoE superiority over strong dense/conditional parents
protected held-family prediction
```

Those are now smaller, explicitly measurable empirical gaps rather than untyped theory gaps.

Desired next terminal:

`P0_ZERO_PRIOR_RESPONSE_LAWS_EXACT_LAYER_GREEN`.
