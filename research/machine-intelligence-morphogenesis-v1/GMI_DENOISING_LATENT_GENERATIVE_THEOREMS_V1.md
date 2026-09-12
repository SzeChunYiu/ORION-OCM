# GMI Denoising and Latent Generative Theorems v1

Status: **FORMAL ZERO-PRIOR GENERATIVE HARDENING / EXACT IDENTITIES**

Status date: 2026-09-12.

Purpose:

> Derive two major generative training structures from exact statistical identities: score state from Gaussian denoising, and latent inference/decoder state from the evidence lower bound decomposition.

---

# 1. Squared-error denoiser is a posterior mean

Let clean random vector be `X in R^d`. Observe corrupted state

\[
Y=X+\sigma Z,
\qquad
Z\sim\mathcal N(0,I),
\]

independent of `X`, with `sigma>0`.

Consider measurable denoiser `f(Y)` trained under squared error

\[
\mathbb E\|X-f(Y)\|_2^2.
\]

## Theorem DL-1 — conditional mean is the optimal denoiser

The pointwise risk-minimizing denoiser is

\[
f^*(y)=\mathbb E[X\mid Y=y].
\]

### Proof

Condition on `Y=y`. For any vector `a`,

\[
\mathbb E[\|X-a\|^2\mid Y=y]
=
\mathbb E[\|X-m(y)\|^2\mid Y=y]
+
\|a-m(y)\|^2,
\]

where `m(y)=E[X|Y=y]`. The cross term vanishes by definition of conditional expectation. QED.

---

# 2. Gaussian denoising determines the noisy-data score

Let `p_Y(y)` be the density of `Y`, which is smooth under Gaussian convolution.

## Theorem DL-2 — Tweedie/score identity

\[
\boxed{
\mathbb E[X\mid Y=y]
=
y+\sigma^2\nabla_y\log p_Y(y)
}
\]

or equivalently

\[
\nabla_y\log p_Y(y)
=
\frac{f^*(y)-y}{\sigma^2}.
\]

### Proof

Write Gaussian kernel

\[
\varphi_\sigma(y-x)
\propto
\exp\left(-\frac{\|y-x\|^2}{2\sigma^2}\right).
\]

The corrupted density is

\[
p_Y(y)=\int p_X(x)\varphi_\sigma(y-x)dx.
\]

Differentiate under the integral:

\[
\nabla_y p_Y(y)
=
\int p_X(x)\varphi_\sigma(y-x)
\frac{x-y}{\sigma^2}dx.
\]

Divide by `p_Y(y)` and recognize the normalized posterior density of `X|Y=y`:

\[
\nabla\log p_Y(y)
=
\frac{\mathbb E[X|Y=y]-y}{\sigma^2}.
\]

QED.

### GMI derivation consequence

Under Gaussian corruption, a squared-error denoising objective does not merely learn an arbitrary reconstruction map. Its optimal residual

\[
f^*(y)-y
\]

is exactly proportional to the score of the corrupted density.

Thus GMI can derive score-state learning from a denoising obligation without assuming score-based/diffusion architectures historically.

---

# 3. Why a noise ladder can help

At `sigma>0`, Gaussian convolution smooths the data distribution and gives an everywhere-smooth density under mild integrability assumptions, even when the clean distribution is concentrated or singular.

The structural motivation for a multi-noise realization is therefore:

```text
large noise:
    smoother/coarser density geometry, easier broad transport

small noise:
    finer target detail, harder/local geometry
```

A sequence of noise levels can trade one difficult direct generation problem for a path of local denoising/score problems.

### Claim boundary

This is a structural reason, not a proof that any particular diffusion schedule is optimal or efficiently learnable.

---

# 4. Denoising prediction target

For each noise level `sigma`, the exact optimal MSE denoiser determines the noisy score.

GMI should therefore compare:

```text
complexity of conditional denoiser/score fields across sigma
number of sampling/integration steps
noise schedule conditioning
serve latency
training sample burden
exactness/likelihood requirement
```

against autoregressive, flow, latent and energy alternatives.

The unresolved question is the lifecycle complexity of those fields and samplers, not whether denoising can encode score information.

---

# 5. Latent-variable model and inference state

Let joint generative model be

\[
p(x,z)=p(z)p(x|z).
\]

For any normalized proposal/inference distribution `q(z|x)` whose support is compatible with the posterior, define

\[
\mathcal L(q;x)
=
\mathbb E_{q(z|x)}
\left[
\log p(x,z)-\log q(z|x)
\right].
\]

## Theorem DL-3 — exact ELBO/KL decomposition

\[
\boxed{
\log p(x)
=
\mathcal L(q;x)
+
\mathrm{KL}\big(q(z|x)\,\|\,p(z|x)\big)
}
\]

and therefore

\[
\mathcal L(q;x)\le\log p(x),
\]

with equality iff `q(z|x)=p(z|x)` almost everywhere under `q`.

### Proof

Using

\[
p(z|x)=\frac{p(x,z)}{p(x)},
\]

expand

\[
\mathrm{KL}(q\|p(z|x))
=
\mathbb E_q\left[
\log q(z|x)-\log p(x,z)+\log p(x)
\right].
\]

Rearrange. QED.

---

# 6. GMI derivation of encoder/decoder structure

The identity implies that if:

```text
a latent quotient z makes p(x|z) simpler than direct p(x)
exact posterior inference is expensive
an approximate q(z|x) is learnable
```

then a two-part species is structurally justified:

```text
generative decoder/state:   p(x|z), p(z)
inference/recognition state: q(z|x)
```

The inference state exists to approximate the otherwise expensive posterior required by development/evidence objectives.

This is the property-level derivation behind VAE-like systems, not a claim that one neural parameterization is uniquely optimal.

---

# 7. Latent-variable negative twins

## No compression through latent state

If `Z` must carry nearly all target identity information and `p(x|z)` remains complex, the latent factorization may add inference burden without reducing generative burden.

## Posterior collapse / unused latent variable

If

\[
p(x|z)=p(x)
\]

for all relevant `z`, then posterior equals prior and latent state carries no information about `x`. The decoder has ignored the latent carrier.

## Exact inference available cheaply

If `p(z|x)` is already tractable, a separate learned recognition network can be unnecessary.

---

# 8. Information interpretation

The average KL term

\[
\mathbb E_x\mathrm{KL}(q(z|x)\|p(z))
\]

contains information/regularization pressure on the latent state, while reconstruction/conditional likelihood measures retained target detail.

Thus latent generative systems instantiate the same broad GMI trade:

\[
\text{compress semantic state}
\quad\text{vs}\quad
\text{retain target distinctions}.
\]

---

# 9. Gap update

Generative structural coverage now includes:

```text
autoregressive factorization                         CLOSED
flow support/invertibility constraints               CLOSED
score-field density sufficiency                      CLOSED
Gaussian denoising -> score identity                 CLOSED
latent component lower bound                        CLOSED
ELBO / approximate posterior inference structure     CLOSED
energy representation + normalization burden         CLOSED
ideal adversarial distribution matching              CLOSED
```

Still open:

```text
pre-outcome complexity of each representation
learnability/optimization
noise-path/sampler selection
latent quotient discovery
approximate inference quality
protected cross-family lifecycle prediction
```

---

# 10. Claim ceiling

These are exact statistical identities under registered assumptions. They do not establish diffusion or VAE superiority, neural convergence, or a universal best generative factorization.
