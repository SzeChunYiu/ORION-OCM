# GMI Generative Information-Factorization Theorems v1

Status: **FORMAL ZERO-PRIOR GENERATIVE HARDENING / INFORMATION BASE LAW**

Status date: 2026-09-12.

Purpose:

> Put autoregressive, latent and other exact generative factorizations on one information baseline. Different realizations can alter conditional complexity, learnability, sampling depth and serving burden, but they do not create information about an exact target distribution for free.

---

# 1. Entropy chain rule

Let discrete random vector be

\[
X=(X_1,\ldots,X_n).
\]

## Theorem GIF-1 — exact entropy factorization

\[
\boxed{
H(X_1,\ldots,X_n)
=
\sum_{i=1}^n H(X_i\mid X_{<i})
}
\]

for any variable ordering.

### GMI interpretation

An exact autoregressive factorization redistributes joint target information into conditional pieces. With ideal true conditionals, the total Shannon information needed for lossless coding remains the joint entropy `H(X)`.

The benefit of a particular ordering/factorization is therefore not lower fundamental entropy but potentially:

```text
simpler conditional laws
better parameter sharing
more accessible development signal
compatible causal/streaming interface
```

against sequential serving depth.

---

# 2. Dependence is exactly the potential entropy saving versus independent marginals

Independent-coordinate coding using true marginals has ideal expected length

\[
\sum_iH(X_i).
\]

The excess over joint entropy is the total correlation / multi-information

\[
\sum_iH(X_i)-H(X)\ge0.
\]

### Consequence

If coordinates are independent, modeling dependencies cannot reduce ideal information burden. If dependence is strong, a conditional/latent structure can exploit it.

This gives an architecture-neutral **dependency-information coordinate** for generative factorization.

---

# 3. Latent-state decomposition

Let latent variable `Z` participate in a joint law with `X`.

The joint entropy identities give

\[
H(X)=I(X;Z)+H(X|Z).
\]

and

\[
H(Z)+H(X|Z)
=
H(X)+H(Z|X)
\ge H(X).
\]

## Theorem GIF-2 — two-part latent code cannot beat target entropy

An ideal code that explicitly sends `Z` and then `X|Z` has expected information at least `H(X)`, with equality when

\[
H(Z|X)=0
\]

(i.e. latent identity is a deterministic function of `X`, under the exact coding interpretation).

### GMI interpretation

A latent variable is valuable not because it violates the target entropy lower bound, but because it can make:

```text
conditional generation simpler
semantic control/composition easier
inference/query structure reusable
sampling or transfer cheaper
```

while paying latent inference/state burden.

---

# 4. Sufficient latent quotient

Suppose protected obligations depend on a semantic quotient `Q=q(X)` rather than exact `X`.

Then the information lower bound changes from `H(X)` to at least the information required for `Q` under the registered loss/distortion.

This is why an intelligent generative species can legitimately discard nuisance detail if the constitution does not require exact reconstruction.

The correct generative state is obligation-relative, not raw data entropy by default.

---

# 5. Mixture/component identity

If supports are disjoint and component `Z` is a deterministic function of `X`, then

\[
H(Z|X)=0
\]

and

\[
H(X)=H(Z)+H(X|Z).
\]

In this special case, the latent component code exactly decomposes target entropy with no overhead in the ideal code-length sense.

This formalizes the earlier component-state lower bound from an information perspective.

---

# 6. Continuous targets and differential entropy caution

For continuous variables, differential entropy is coordinate/scale dependent and can be negative. Therefore GMI must not compare continuous representation burden using raw differential entropy alone.

Use registered alternatives such as:

```text
quantized finite-precision entropy
relative entropy / likelihood
rate-distortion at task-relevant tolerance
mutual information (when well-defined)
explicit precision burden
```

This links generative theory to the physical-precision hardening.

---

# 7. Cross-entropy training decomposition

For discrete true target `p` and model `q`, expected negative log likelihood is

\[
\mathbb E_p[-\log q(X)]
=
H(p)+KL(p\|q).
\]

Thus minimizing ideal cross entropy is exactly minimizing model mismatch `KL(p||q)` because target entropy is fixed.

This base identity applies whether `q` is autoregressive, latent-marginal, flow-discretized, energy-normalized or another normalized model.

### GMI consequence

Differences among normalized generative families arise from:

```text
which q are representable at a given burden
how accessible development is
likelihood/evidence computation cost
sampling/serving cost
approximation/precision constraints
```

not from changing `H(p)`.

---

# 8. Representation-complexity target

For generative family `R`, define a registered minimum lifecycle burden at target mismatch tolerance `epsilon`:

\[
C_R^*(\epsilon)
=
\inf_{q\in R:\,KL(p\|q)\le\epsilon}
B_R(q).
\]

The zero-prior generative-selection problem is then to predict/estimate the family of curves

\[
C_R^*(\epsilon)
\]

for competing representations, including training/search/sample cost.

This is a precise formulation of the remaining GKF-10 gap.

---

# 9. Negative twins

```text
independent coordinates:
    no information-theoretic gain from dependency modeling

highly dependent but simple latent quotient:
    latent/conditional representation can greatly simplify component laws

exact low-latency parallel serving requirement:
    sequential AR may lose despite exact factorization

singular/discrete target:
    ordinary equal-dimensional diffeomorphic flow is structurally mismatched
```

---

# 10. Gap update

`GKF-10` now has a common information baseline:

```text
joint entropy / chain rule                              CLOSED
independence-versus-dependence information gap          CLOSED
latent two-part information identity                    CLOSED
cross-entropy = entropy + KL                            CLOSED
family minimum burden at KL tolerance formalization     CLOSED

pre-outcome estimation of C_R^*(epsilon)                OPEN-BLOCKING
optimization/learnability/sampling laws                 OPEN-BLOCKING
protected cross-family prediction                       OPEN-BLOCKING
```

---

# 11. Claim ceiling

Information identities do not select a unique generative architecture. They eliminate false advantages and define the quantity the remaining theory must predict: representation/development/serving burden needed to approach the same target information law.
