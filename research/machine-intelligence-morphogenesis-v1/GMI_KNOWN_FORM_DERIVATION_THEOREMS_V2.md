# GMI Known-Form Derivation Theorems v2

Status: **ADDITIVE FORMAL ZERO-PRIOR DERIVATION LAYER**

Status date: 2026-09-12.

Purpose:

> Extend the zero-prior theorem layer to known families not closed in v1. The goal is property/mechanism derivation from obligation structure, not historical architecture-name reconstruction.

---

# 1. Recursive partitions and decision trees

Let the input space be partitioned recursively by binary predicates into `L` terminal cells `R_1,...,R_L`, and let the target be constant on each cell:

\[
f(x)=a_\ell\quad\text{for }x\in R_\ell.
\]

## Theorem KF-14 — recursive partition realization

A binary decision tree whose internal nodes are the partition predicates and whose leaves store `a_l` represents `f` exactly with `L` leaves.

If the leaf values are all distinct and every cell is reachable, any deterministic leaf-output tree using the same predicate language requires at least `L` terminal output states.

### Derivation consequence

When obligation geometry is piecewise/discontinuous and a small recursive partition explains large regions exactly, GMI predicts hierarchical conditional branching rather than a globally smooth coefficient map.

### Negative twin

For a single smooth linear law, recursive partitioning incurs unnecessary cell growth while KF-1 gives a compact coefficient state.

### Remaining gap

Predicting the useful partition predicates and leaf growth from pre-outcome data remains empirical.

---

# 2. Additive residual correction / boosting-like structure

Suppose the target decomposes

\[
f(x)=\sum_{t=1}^T h_t(x)
\]

for functions from a weak family `H`.

## Proposition KF-15 — exact staged residual decomposition

Define residuals

\[
r_0=f,
\qquad
r_t=r_{t-1}-h_t.
\]

Then after `T` exact residual corrections,

\[
r_T=0.
\]

### Derivation consequence

If no single weak realization is adequate but residual error remains representable by the same cheap family, GMI predicts staged additive correction.

### Negative twin

If residuals leave the weak family or are dominated by noise, repeated correction gives no guaranteed benefit and may increase variance/overfit.

### Limitation

This is a decomposition theorem, not a proof that greedy gradient boosting will find the decomposition in arbitrary data.

---

# 3. Graph-local message passing

Let a graph `G=(V,E)` carry initial node states `x_v`. Consider a `T`-round local message-passing realization in which each node updates only from its current state and immediate neighbors.

## Theorem KF-16 — finite graph receptive field

After `T` synchronous rounds, the state at node `v` is a function only of the labeled radius-`T` neighborhood of `v`.

### Proof

Induction on `T`. At `T=0` the claim is immediate. One update can depend only on neighbors' radius-`T` states, whose union is contained in the radius-`T+1` neighborhood. QED.

## Corollary KF-16.1 — locality impossibility

If two graph instances have isomorphic labeled radius-`T` neighborhoods around `v` but require different protected outputs at `v`, no `T`-round local message-passing system can solve both exactly.

### Derivation consequence

Permutation-respecting relational obligations with local dependency naturally favor shared neighborhood aggregation; required dependency radius lower-bounds message-passing depth or motivates nonlocal routing.

### Negative twin

For obligations depending on distant/global graph structure, bounded-depth local message passing is insufficient without additional global state, positional structure, hierarchy, or long-range communication.

---

# 4. Selective recurrent retention and gating

Consider scalar state update

\[
z_{t+1}=g_t z_t +(1-g_t)u_t,
\qquad g_t\in\{0,1\}.
\]

## Proposition KF-17 — exact retain-or-overwrite primitive

If `g_t=1`, then `z_{t+1}=z_t` exactly. If `g_t=0`, then `z_{t+1}=u_t` exactly.

Thus a multiplicative gate implements a zero-cost semantic switch between preservation and overwrite in this registered model.

### Derivation consequence

When an obligation requires long retention punctuated by sparse selective writes, GMI predicts an explicit retention/write control mechanism rather than unconditional recurrent mixing.

### Negative twin

If every timestep should fully refresh state, the retain gate provides no semantic advantage.

### Limitation

This derives gating as a mechanism. It does not uniquely derive LSTM/GRU architecture or prove their optimization superiority.

---

# 5. Linear state-space order

For an exact finite-dimensional linear time-invariant input/output system, classical realization theory relates minimal state dimension to Hankel rank.

## Parent theorem KF-18 — minimal linear realization rank

Under standard controllability/observability assumptions, the minimal state dimension of an exact LTI realization equals the rank of the system Hankel operator/matrix.

### GMI interpretation

If measured sequence behavior has low effective Hankel rank and stable linear dynamics, GMI predicts a compact recurrent linear state rather than explicit history or dense all-pairs sequence interaction.

### Negative twin

Strong input-dependent nonlinear transitions or variable dependency routing can invalidate a low-order fixed linear state model.

### Remaining gap

Robustly estimating effective state order and the linear/nonlinear boundary from finite protected data remains open.

---

# 6. Sparse exact routing

For sequence length `n`, suppose the registered target dependency graph on an instance has exactly `m(x)` required directed edges.

## Proposition KF-19 — exact sparse dependency cost

Any implementation that explicitly evaluates only required edges uses `m(x)` edge interactions for that instance; a dense all-pairs realization evaluates `n^2` ordered pairs (or `n(n-1)/2` under symmetric conventions).

### Derivation consequence

If required dependency density

\[
\delta(x)=m(x)/n^2
\]

is small and the sparse pattern can be found more cheaply than the avoided interactions, GMI predicts sparse/local/structured routing.

### Negative twin

Dense dependencies or expensive pattern discovery remove the advantage.

This is the quantitative property-level derivation behind sparse/local attention, not a uniqueness theorem for one sparse-attention algorithm.

---

# 7. Model-based online planning versus compiled policy

Suppose a stable environment/task permits an online planner with per-decision cost `c_plan`. A policy can be compiled/developed at one-time cost `C_policy` and then served at `c_policy<c_plan` per decision while preserving the registered decision quality.

## Theorem KF-20 — planning-to-policy crossover

For `R` future decisions under unchanged semantics, compiling the policy is cheaper iff

\[
R>
\frac{C_{policy}}{c_{plan}-c_{policy}}.
\]

### Derivation consequence

Low reuse, changing goals/dynamics, or high uncertainty favors retaining an explicit world model/search procedure. High stable reuse favors amortized policy/value realization.

### Negative twin

If dynamics/goals change before the crossover horizon, compiled direct policy can become stale while model-based recomputation remains adaptive.

### Important limitation

This theorem assumes both methods reach matched protected quality. Predicting model error, exploration value and policy-learning burden remains a separate control-theory gap.

---

# 8. Tool / solver routing

Let legal tools `j=1,...,m` have expected protected loss `L_j(O)`, burden vector `b_j(O)`, and admissibility indicator `a_j(O)` on obligation `O`.

## Proposition KF-21 — obligation-directed tool selection

Under fixed scalar resource prices `pi`, the optimal single-tool decision is

\[
j^*(O)
\in
\arg\min_{j:a_j(O)=1}
\left[L_j(O)+\pi^Tb_j(O)\right].
\]

### Derivation consequence

If different obligation regions have different frontier tools, GMI predicts a typed router over heterogeneous solvers rather than forcing one universal computational mechanism.

### Negative twin

If one tool dominates all others across the entire registered obligation family, routing adds only overhead.

### Remaining gap

The hard problem is predicting tool loss/burden before running the tool and learning when tool composition, rather than single selection, is required.

---

# 9. Exact verifier and proposal separation

Let a proposal mechanism generate a candidate and let an exact verifier decide admissibility.

## Proposition KF-22 — sound admission under exact verification

If authoritative state changes only after verifier acceptance and the verifier has zero false accepts on the registered obligation, then no rejected/invalid proposal enters authoritative state.

This separates proposal quality from admission soundness.

### Derivation consequence

High-coverage but fallible proposal plus cheap exact verification and high false-adoption loss implies a generate/verify lifecycle rather than direct proposal serving.

### Negative twin

If verification cost dominates and false-adoption loss is negligible, the extra gate can be economically dominated.

This is the property-level core already calibrated by the VGSC exact experiments; no coined family name is needed for the theorem.

---

# 10. What remains genuinely unclosed

The following cannot be removed by the structural theorems above:

```text
practical neural optimization reachability
practical neural generalization from finite development data
approximate symmetry measurement and degradation law
best dense shared representation vs conditional experts
metric discovery for exemplar methods
Bayesian graphical-structure discovery
useful tree split discovery
message-passing oversquashing magnitude and nonlocal crossover
state-space order under nonlinear/nonstationary sequences
attention dependency discovery and routing error
RAG predictive-target residual estimation
nonlinear adapter residual rank
heuristic value for combinatorial search
model error vs planning value
policy-learning burden vs planning burden
generative factorization choice: autoregressive vs diffusion vs flow vs latent
continual-learning architecture response
reasoning/test-time search allocation
multi-tool composition
```

These are now the principal quantitative theory gaps for zero-prior derivation. They require response laws or impossibility bounds, not more architecture naming.

---

# 11. Revised zero-prior criterion

A known family is considered **structurally derived** when:

1. GMI predicts the sufficient-state/operator property vector from ecology descriptors before search;
2. there is an exact/parent lower or upper bound explaining the property advantage;
3. a negative twin removes the advantage;
4. neutral search recovers an implementation-equivalent realization.

It is considered **quantitatively derived** only when a frozen pre-outcome response law predicts its frontier crossover on held ecology families.

The global programme therefore continues recursively until every registered known family is either quantitatively derived, reduced to another family, or explicitly outside the registered scope.
