# GMI Energy and Adversarial Generative Theorems v1

Status: **FORMAL ZERO-PRIOR GENERATIVE HARDENING / PARENT-THEOREM INTEGRATION**

Status date: 2026-09-12.

Purpose:

> Derive energy-state and adversarial distribution-matching realizations from distribution semantics, without treating energy-based models or GANs as primitive historical families.

---

# 1. Every strictly positive finite distribution has an energy representation

Let `X` be a finite state space and `p(x)>0` for every `x in X`.

## Theorem EG-1 — exact energy representation

Define

\[
E(x)=-\log p(x).
\]

Then

\[
p(x)=\frac{e^{-E(x)}}{Z},
\qquad
Z=\sum_{x'}e^{-E(x')}=1.
\]

More generally, adding any constant `c` to every energy leaves the normalized distribution unchanged.

Conversely, every finite real-valued energy function induces a strictly positive normalized distribution through the Gibbs form.

### GMI interpretation

A probability law can therefore be carried by **relative compatibility/energy values** rather than normalized probabilities. This is a representation equivalence, not automatically a computational advantage.

---

# 2. Normalization can be the bottleneck

Although `E(x)` determines `p`, exact likelihood/probability evaluation generally requires the partition function

\[
Z=\sum_x e^{-E(x)}.
\]

## Theorem EG-2 — exact finite normalization requires global aggregate information

For an arbitrary unrestricted energy table on finite `X`, changing the energy at any one state changes `Z` and hence changes the normalized probability at every state.

Thus exact normalized probability queries are globally coupled through `Z`.

### Negative twin

If the obligation only requires comparing two states by probability, then

\[
p(x)>p(y)\iff E(x)<E(y),
\]

and `Z` cancels. Ranking/compatibility obligations can therefore be much cheaper than normalized likelihood obligations.

### GMI consequence

Energy-state selection depends strongly on the semantic obligation: scoring/ranking/sampling may favor unnormalized energy, while exact normalized likelihood can impose a global partition-function burden.

---

# 3. Finite-domain adversarial distribution matching

Let true data distribution be `p` and generator distribution be `q` on finite `X`. Consider discriminator objective

\[
V(D;q)
=
\sum_x p(x)\log D(x)
+
\sum_x q(x)\log(1-D(x)),
\]

with `D(x) in (0,1)` optimized independently at each `x`.

## Theorem EG-3 — optimal discriminator

For fixed `p,q`, the pointwise optimal discriminator is

\[
D^*(x)=\frac{p(x)}{p(x)+q(x)}
\]

whenever `p(x)+q(x)>0`.

### Proof

For each `x`, maximize

\[
p\log D+q\log(1-D).
\]

Setting derivative `p/D-q/(1-D)=0` gives the result; the second derivative is negative. QED.

## Theorem EG-4 — optimal adversarial value equals Jensen-Shannon divergence up to a constant

Substituting `D*` gives

\[
V(D^*;q)
=-2\log2+2\,JS(p\|q).
\]

Therefore the global minimum over unrestricted generator distributions occurs exactly at

\[
q=p.
\]

### Derivation consequence

If direct likelihood is unavailable/undesired but samples from the target are available and a sufficiently rich discriminator can compare target versus generated samples, distribution matching can be converted into a two-player classification/game objective.

This is the property-level derivation behind adversarial generative training.

---

# 4. The discriminator is itself a learned measurement instrument

The exact theorem assumes unrestricted pointwise discriminator optimization. In actual finite-capacity systems:

```text
discriminator class may miss semantic discrepancies
generator may exploit blind spots
optimization may cycle/fail
sample complexity can dominate
```

Thus adversarial generation is attractive only when the learned discriminator is a cheaper/more accessible witness of distribution mismatch than direct density modeling while remaining sufficiently discriminative.

---

# 5. Generative carrier comparison

GMI now has structural derivations for:

```text
autoregressive conditionals    universal chain factorization
invertible flow                bijective transport + change of variables
score field                    gradient of log density determines smooth positive law
latent mixture                 component quotient
energy state                   unnormalized log-density / compatibility
adversarial matching           discriminator witness converts sample mismatch into game objective
```

The remaining problem is **not** why these carriers can exist. It is predicting their learnability and lifecycle burden from pre-outcome distribution/ecology descriptors.

---

# 6. Gap update

`GKF-10 generative factorization` structural coverage is now broader.

Still open:

```text
complexity of conditional factors
transport-map complexity
score/noising path conditioning and sampler burden
energy sampling/normalization difficulty
discriminator witness complexity/stability
latent quotient discoverability
protected cross-family prediction
```

---

# 7. Claim ceiling

EG-3/EG-4 are the standard idealized adversarial-distribution theorem in finite form. They do not prove that finite neural GAN training converges or outperforms likelihood/score-based methods.
