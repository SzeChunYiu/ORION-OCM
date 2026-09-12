# GMI Generative and Control Factorization Theorems v1

Status: **FORMAL ZERO-PRIOR STRUCTURAL DERIVATION / QUANTITATIVE REAL-WORLD SELECTION STILL OPEN**

Status date: 2026-09-12.

Purpose:

> Derive several major generative and control realization properties from target-distribution and ecology structure, without assuming historical architecture names.

---

# 1. Autoregressive factorization is universally exact for finite discrete sequences

Let `X=(X_1,...,X_n)` be a finite discrete random vector with joint distribution `P`.

## Theorem GF-1 — chain-rule realization

For every ordering of the variables,

\[
P(x_1,...,x_n)
=
P(x_1)\prod_{i=2}^{n}P(x_i\mid x_1,...,x_{i-1})
\]

on every event with well-defined conditionals.

Thus a family of conditional next-step laws is an exact sufficient realization of the joint distribution.

### Derivation consequence

When the obligation is naturally sequential/discrete and the conditional laws are reusable/compressible, GMI can derive a causal-prefix predictor without knowing the term `autoregressive model`.

### Resource consequence

A direct ancestral sampler following this factorization uses `n` conditional draw stages in the chosen order. This sequential serving depth is a native burden unless conditional independences permit blocking/parallelization.

### Negative twin

If serving latency strongly penalizes `n` sequential stages and an alternative exact parallel transport is cheap, the chain-rule realization may be semantically sufficient but lifecycle-suboptimal.

---

# 2. Exact flow realization has a support-type constraint

Let latent `Z` have a density with respect to Lebesgue measure on `R^d`. Let `f:R^d->R^d` be a differentiable bijection with differentiable inverse and nonsingular Jacobian almost everywhere.

## Theorem GF-2 — diffeomorphic pushforward preserves absolute continuity

`X=f(Z)` is also absolutely continuous with respect to Lebesgue measure, with density given by change of variables.

Therefore an ordinary equal-dimensional diffeomorphic flow cannot exactly represent a target distribution containing point masses or supported entirely on a lower-dimensional set of Lebesgue measure zero.

### Proof

The change-of-variables theorem gives

\[
p_X(x)=p_Z(f^{-1}(x))\left|\det J_{f^{-1}}(x)\right|
\]

almost everywhere. Hence the pushforward has a density. QED.

### Derivation consequence

A low-complexity invertible transport is attractive when the target is compatible with such a transport and exact likelihood/invertibility matter. Singular/discrete targets are a registered negative twin unless the realization is augmented, discretized or otherwise changed.

---

# 3. Score field is sufficient for a smooth positive density up to normalization

Let `p,q` be strictly positive continuously differentiable densities on a connected open domain `Omega subset R^d`.

## Theorem GF-3 — score uniqueness

If

\[
\nabla\log p(x)=\nabla\log q(x)
\]

for every `x in Omega`, then `p=q` after normalization.

### Proof

The gradient of `log p-log q` is zero on a connected domain, so `log p-log q` is constant. Thus `p=cq`; normalization forces `c=1`. QED.

### Derivation consequence

For a smooth positive target distribution, the score field

\[
s(x)=\nabla\log p(x)
\]

is an information-sufficient carrier of the density (with normalization/boundary conditions). This gives a zero-prior route to score-based generative state without naming diffusion.

### Claim boundary

Score sufficiency does not establish that a score field is easy to learn or sample from. Diffusion/score systems add a noising path and reverse dynamics whose numerical/training burdens remain empirical response-law variables.

---

# 4. Disjoint mixture components require component identity

Suppose the target support decomposes into `K` disjoint measurable components `A_1,...,A_K`, each with positive probability.

## Theorem GF-4 — exact component-state lower bound

Any latent component variable `Z` that deterministically identifies which support component contains a sample must have at least `K` distinguishable states, hence at least

\[
\lceil\log_2K\rceil
\]

bits.

A `K`-state categorical latent variable is sufficient for component identity.

### Derivation consequence

Strong global multimodality can create a useful discrete latent quotient before modeling within-component variation.

### Negative twin

If component identity has no semantic or computational reuse, introducing a discrete latent state can add burden without benefit.

---

# 5. Generative zero-prior selection variables

The theorem layer implies that the relevant GMI question is not `AR or diffusion?` by name. It is to compare the minimal lifecycle burden of several sufficient carrier/operator choices:

```text
sequential conditional law
invertible transport
score field + sampling dynamics
latent quotient + conditional generator
retrieval/residual generator
```

The current exact descriptors include:

```text
conditional dependency/sequential depth
support type (discrete, absolutely continuous, singular/manifold)
invertible-transport complexity
score-field complexity/smoothness
multimodal quotient cardinality
sampling-step/latency budget
likelihood/exactness requirement
```

`GKF-10` therefore remains open only at the **complexity/learnability estimator and cross-family lifecycle prediction** layer; the major carrier-level distinctions are formally typed.

---

# 6. Model-based versus direct-policy control as an amortization problem

Consider a family of control obligations sharing one environment dynamics law but varying over `K` registered goals/tasks.

Let:

```text
C_M      one-time burden to obtain/maintain a reusable world/dynamics model
C_P      development burden to obtain one direct policy for one goal
c_plan   per-decision serving burden using model + planning
c_exec   per-decision serving burden using a compiled/direct policy
R        expected number of decision uses per goal
```

Assume matched protected decision quality for the comparison.

Then

\[
C_{MB}=C_M+KRc_{plan},
\]

and

\[
C_{MF}=KC_P+KRc_{exec}.
\]

## Theorem CF-1 — exact model/planning versus policy-compilation crossover

Model-based planning is cheaper iff

\[
C_M+KRc_{plan}<KC_P+KRc_{exec}.
\]

If `c_plan>c_exec` and `KC_P>C_M`, define

\[
R^*=\frac{KC_P-C_M}{K(c_{plan}-c_{exec})}.
\]

Then:

```text
R < R*   -> reusable model + online planning favored
R > R*   -> per-goal/direct policy compilation favored
```

under the registered scalarized burden and matched quality.

### Interpretation

Goal diversity increases the value of a reusable dynamics model because `C_M` is amortized across goals. High repeated use of a fixed goal increases the value of compiling planning into a cheap direct policy.

## Corollary CF-1.1 — model error penalty

If model-based decisions incur additional expected protected loss/risk penalty `Lambda_M`, replace the left side by

\[
C_M+KRc_{plan}+\Lambda_M.
\]

Model error can therefore reverse the structural advantage even when model learning is data-efficient.

### Negative twins

```text
one fixed goal + very high reuse:
    policy/value compilation can dominate expensive repeated planning.

rapidly changing goals + reusable stable dynamics:
    a world model can dominate relearning a direct policy for every goal.

high model bias / unstable dynamics:
    model-based reuse can become harmful despite favorable nominal amortization.
```

### GMI consequence

`GKF-11 control factorization` is reduced to measurable terms:

```text
dynamics reusability across goals
model-development burden
per-goal policy-development burden
planning serve cost
compiled-policy serve cost
model error/risk
number of goals and reuse horizon
```

The remaining hard gap is prospectively estimating these quantities in complex partially observed environments.

---

# 7. Hybrid prediction

The crossover law predicts a natural hybrid without naming one historically:

1. use a reusable world model when goals/regimes are diverse;
2. plan for novel goals while reuse is low;
3. once a goal/strategy is reused enough to cross the amortization threshold, compile/cache the result into a direct policy/value structure;
4. invalidate/replan when dynamics or goals shift.

Thus GMI predicts transitions among model-based, model-free and hybrid cached planning as lifecycle phases, not mutually exclusive species.

---

# 8. Claim ceiling

This document closes structural sufficiency/no-go and simple amortization laws. It does not close:

```text
real score/diffusion learnability
real normalizing-flow complexity
real AR conditional complexity
model-learning sample complexity in general environments
exploration burden
partial-observability/world-model sufficiency
protected cross-family generative/control prediction
```

Those remain empirical/theoretical response laws, now attached to explicit variables rather than architecture names.
