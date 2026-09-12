# GMI Transformer Microfeature Theorems v1

Status: **EXACT / CONDITIONAL MICRO-MECHANISM THEOREMS AND PROOF SKETCHES**

Status date: 2026-09-12.

Refs:

- `GMI_NEURAL_LLM_TRANSFORMER_MICROFEATURE_CALCULUS_V1.md`
- `GMI_SEMANTIC_QUOTIENT_REALIZATION_THEOREM_V1.md`
- `GMI_PREDICTIVE_RESIDUAL_QUOTIENT_THEORY_V1.md`

Purpose:

> Extract theorem-level statements from the Transformer/LLM microfeature calculus so architectural explanations are not only taxonomic.

These results are exact only under their explicit assumptions. They do not prove practical superiority of any named architecture.

---

# TMT-1 — order-information necessity

Let histories `h` and `h'` satisfy

\[
h'=g\cdot h
\]

for a permutation `g`, and let the protected obligation distinguish them:

\[
q_O(h)\ne q_O(h').
\]

Suppose realization `M` computes a complete decision state `z(h)` such that

\[
z(g\cdot h)=z(h)
\]

and all protected outputs/future update behavior are functions only of `z` and legal shared context.

Then `M` cannot be exact for `O` on both histories.

## Proof

Permutation invariance gives `z(h')=z(h)`. Since protected behavior is a function of the same decision state and shared context, the two histories produce identical protected behavior. Exact adequacy requires different behavior for quotient-distinct histories. Contradiction.

## Consequence

Some order-distinguishing state is necessary for order-sensitive sequence obligations. The theorem does not identify the implementation.

---

# TMT-2 — finite-window impossibility

Let `suffix_W(h)` be the final `W` observations of history `h`.

Assume

\[
suffix_W(h)=suffix_W(h')
\]

but

\[
q_O(h)\ne q_O(h').
\]

Any stateless realization whose decision is a function only of `suffix_W` and shared exogenous context cannot be exact on both histories.

## Proof

Identical suffixes imply identical machine input states, hence identical decisions. Exact target semantics require a distinction. Contradiction.

## Consequence

Increasing context, compressing earlier history into recurrent state, or retrieving external state are alternative ways of supplying missing distinctions.

---

# TMT-3 — fixed-routing union lower bound

Fix a registered routing stage. For each legal input `x`, let `E(x)` be the minimal required dependency edge set for exact execution at that stage under a frozen primitive semantics.

Let a fixed safe routing graph be `E_*`.

If exactness requires every edge in `E(x)` to be available on input `x`, then

\[
E_*\supseteq \bigcup_x E(x).
\]

Therefore any additive per-edge fixed-routing burden `c_e>0` satisfies

\[
B_{fixed}\ge c_e\left|\bigcup_xE(x)\right|.
\]

An oracle input-dependent router with no discovery overhead has average edge burden

\[
B_{dyn}^{oracle}=c_e\,\mathbb E_x|E(x)|.
\]

Hence the maximum structural routing opportunity before search/discovery overhead is

\[
\Delta B_{route}^{oracle}
\ge
c_e\left(
\left|\bigcup_x E(x)\right|-
\mathbb E_x|E(x)|
\right).
\]

## Scope warning

`E(x)` is relative to the frozen stage/primitives. Multi-layer paths, recurrence or alternative computations can change the required edge representation. Therefore this is not a universal attention lower bound.

---

# TMT-4 — softmax variational characterization

For `s in R^n`, temperature `T>0`, and probability simplex `Delta_n`, define Shannon entropy

\[
H(p)=-\sum_i p_i\log p_i.
\]

Then

\[
\operatorname{softmax}(s/T)
=
\arg\max_{p\in\Delta_n}
\left[p^Ts+TH(p)\right].
\]

## Proof sketch

Use Lagrangian

\[
\mathcal L(p,\lambda)
=p^Ts-T\sum_i p_i\log p_i
+\lambda(\sum_i p_i-1).
\]

Stationarity gives

\[
s_i-T(1+\log p_i)+\lambda=0,
\]

so

\[
p_i\propto e^{s_i/T}.
\]

Strict concavity for `T>0` gives uniqueness.

## Consequence

Temperature is an entropy-vs-score routing parameter.

---

# TMT-5 — causal information legality

Let `F_i` be the sigma-field / legal information available before producing output at step `i`.

If the obligation requires output `Y_i` to be `F_i`-measurable, a system whose computation depends on information outside `F_i` violates the information constitution even when its numerical prediction is correct on a finite benchmark.

## Consequence

A causal mask is an implementation of a legal-information restriction for autoregressive tasks; it is not merely a regularizer.

---

# TMT-6 — exact cache substitution

Let deterministic function

\[
(K_t,V_t)=f_\theta(x_{\le t})
\]

be repeatedly recomputed during autoregressive continuation, and assume `theta` and `x_{\le t}` remain unchanged.

Replacing recomputation by stored exact values `(K_t,V_t)` leaves all downstream deterministic outputs unchanged.

## Proof

Referential transparency: the cached value equals the function value that would be recomputed under identical inputs and parameters.

## Consequence

Exact KV caching is a semantics-preserving serving materialization with memory-vs-compute tradeoff.

---

# TMT-7 — implementation invariance of exact attention

Let algorithms `A` and `A'` compute the same mathematical map

\[
f(Q,K,V,M)
\]

for every registered input under the same numeric semantics.

Then no protected semantic test depending only on `f` can distinguish them.

Any difference is in resource/physical response unless the implementation changes numeric error, failure behavior or developmental state.

## Consequence

An IO-aware exact attention algorithm belongs to the same semantic mechanism class as naive exact attention while potentially occupying a different hardware frontier.

---

# TMT-8 — tied-parameter function-class inclusion

Let untied model family be parameterized by

\[
(\theta_1,\theta_2)\in\Theta\times\Theta
\]

and tied family impose

\[
\theta_1=\theta_2.
\]

Then the tied function class is a subset of the untied class:

\[
\mathcal F_{tied}\subseteq\mathcal F_{untied}.
\]

## Proof

Every tied parameter setting is a valid untied setting with the equality constraint; the converse need not hold.

## Consequence

Weight sharing cannot increase raw representational function class relative to the same untied parameterization, but can reduce state/description/sample burden by imposing a useful prior.

---

# TMT-9 — residual Jacobian identity

For differentiable residual map

\[
y=x+f(x),
\]

\[
J_y=I+J_f.
\]

For a stack

\[
x_{l+1}=x_l+f_l(x_l),
\]

the end-to-end Jacobian is

\[
\prod_l (I+J_{f_l}).
\]

## Consequence

There exists an explicit identity term in local signal/gradient propagation. This supplies a precise optimization-geometry mechanism for skip connections, while not guaranteeing stability when `J_f` is large/pathological.

---

# TMT-10 — autoregressive chain factorization

For any discrete sequence distribution with positive/defined conditionals,

\[
p(x_{1:n})
=p(x_1)\prod_{t=2}^n p(x_t\mid x_{<t}).
\]

Therefore autoregressive factorization is probabilistically exact in principle; modeling difficulty lies in representing/learning the conditionals and serving them efficiently.

---

# TMT-11 — population cross-entropy optimum

Let true conditional distribution be `p(y|x)` and candidate be `q(y|x)`. Expected conditional cross entropy satisfies

\[
\mathbb E_{x,y\sim p}[-\log q(y|x)]
=
H_p(Y|X)
+
\mathbb E_x KL(p(\cdot|x)\|q(\cdot|x)).
\]

Thus, when the candidate class contains `p` and optimization reaches the population optimum,

\[
q^*(\cdot|x)=p(\cdot|x)
\]

almost surely on the registered support.

## Consequence

Next-token cross entropy has a clean ideal predictive target. Finite data, misspecification, optimization, distribution shift and non-predictive target residuals remain separate gaps.

---

# TMT-12 — quantization collision no-go

Let exact authority states `z,z'` satisfy

\[
q_O(z)\ne q_O(z').
\]

Let serving quantizer `Q` satisfy

\[
Q(z)=Q(z').
\]

If downstream serving behavior depends only on `Q(z)` and shared context, exact obligation satisfaction on both states is impossible.

## Proof

The serving system receives identical states but exact semantics require distinguishable behavior. Contradiction.

## Consequence

Any exact quantization must remain injective over obligation-relevant distinctions or retain a compensating side channel. Approximate quantization is governed by allowed semantic distortion.

---

# TMT-13 — key/value cache state scaling

For decoder with `L` layers, sequence length `n`, per-KV-head dimension `d`, and `H_kv` independent KV heads, cache element count scales as

\[
\Theta(2LndH_{kv})
\]

ignoring batch and datatype constants.

Thus reducing `H_kv` while holding other terms fixed reduces cache size linearly.

## Consequence

MQA/GQA-like sharing has an exact first-order cache-memory rationale. Quality effects require empirical/conditional theory.

---

# TMT-14 — fixed-window / cache distinction

KV caching does **not** increase the mathematical context available to a model if the model still restricts attention/state to a window of width `W`. It only avoids recomputation of available prefix-derived state.

Therefore

```text
context capacity
!=
cache efficiency.
```

Conflating them is a type error.

---

# TMT-15 — decoding policy / model distribution distinction

Let base model define distribution `p_theta`. A decoder `D` maps that distribution and random/search state to emitted sequence/action.

Changing temperature/top-k/top-p/beam search can change output behavior while leaving `theta` and `p_theta` unchanged.

Therefore:

```text
model predictive state
!=
decision/search policy.
```

Evaluation must specify which object is being claimed to improve.

---

# 16. Exact microscope programme

Implement finite/exact tests:

```text
X-TMT1  enumerate permutation-sensitive finite obligations and invariant encoders
X-TMT2  enumerate W-suffix collisions
X-TMT3  enumerate required edge-set families and verify fixed union lower bound
X-TMT4  numerically/symbolically verify softmax variational optimum
X-TMT5  exact causal-mask dependence: perturb the last token, compare prefix outputs
X-TMT6  compare recomputation vs exact cache traces
X-TMT7  naive vs block-wise online exact attention, exact and float64
X-TMT8  enumerate tied/untied tiny linear/nonlinear families
X-TMT9  symbolic Jacobian checks
X-TMT10 exact autoregressive chain factorization on a finite distribution
X-TMT11 finite conditional distributions and KL decomposition
X-TMT12 enumerate quantizer collisions and target distinctions
X-TMT13 cache element accounting
X-TMT14 fixed-window vs cache: run the X-TMT2 collision construction through the X-TMT6 cache trace and show that
        the cache changes op counts and leaves the induced partition of histories bit-identical
X-TMT15 decoding policy vs model distribution: one exact p_theta decoded by greedy / temperature / top-k / top-p /
        beam, showing distinct emissions from a bit-identical conditional table
```

Status: the programme is **fully implemented** in `gmi_microscope/tmt.py` at X-TMT1..X-TMT15 and executed GREEN (15/15) in
`GMI_TRANSFORMER_MICROFEATURE_EXACT_RECEIPT_V1.json`. TMT-14 and TMT-15 were previously recorded as type distinctions with
no finite check; both now carry one.

Receipts must distinguish theorem implementation checks from empirical neural evidence. Every check above is
`MATH_IMPLEMENTATION_CHECK__NOT_EMPIRICAL_NEURAL_EVIDENCE`: it establishes a statement about the theorem on an enumerated
finite scope and establishes nothing about any trained neural network.

---

# 17. What remains empirical

The theorems above do **not** settle:

```text
which positional encoding is best
optimal number of heads
why specific induction circuits emerge
optimal GQA grouping
optimal normalization choice
SwiGLU advantage magnitude
practical long-context extrapolation
optimizer-generalization interaction
large-model in-context learning mechanism
hallucination rates
alignment behavior
```

Those are response-law experiments, not missing definitions.
