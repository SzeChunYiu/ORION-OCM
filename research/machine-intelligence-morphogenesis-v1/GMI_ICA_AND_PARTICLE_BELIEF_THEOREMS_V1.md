# GMI Independent-Component and Particle-Belief Theorems v1

Status: **PARENT-THEOREM INTEGRATION / ZERO-PRIOR PROBABILISTIC HARDENING**

Status date: 2026-09-12.

Purpose:

> Close two remaining classical registry gaps: when latent independent-source structure is identifiable from mixtures, and when sample/particle belief is a justified approximation to an intractable probabilistic state.

---

# 1. Linear independent-source model

Assume observations

\[
x=As
\]

where `A` is an invertible `d x d` mixing matrix and latent components

\[
s=(s_1,\ldots,s_d)^T
\]

are mutually independent.

The zero-prior structural question is whether the latent factorization is identifiable from the observation law or whether arbitrary rotated coordinates are equally valid.

---

# 2. Gaussian non-identifiability

## Theorem IC-1 — isotropic Gaussian sources are rotationally non-identifiable

If

\[
s\sim\mathcal N(0,I),
\]

then for every orthogonal matrix `R`,

\[
Rs\sim\mathcal N(0,I)
\]

and its coordinates are again jointly Gaussian with identity covariance, hence independent.

Therefore

\[
x=A s=(A R^T)(R s)
\]

provides infinitely many equally valid independent-component decompositions.

### GMI consequence

Independence alone does not identify a unique latent source basis in the all-Gaussian case. A source-separation species cannot infer semantic latent axes from that assumption alone.

---

# 3. Non-Gaussian independent components

Classical ICA identifiability theory, based on Darmois–Skitovich-type results, establishes the following parent theorem.

## Parent theorem IC-2 — ICA identifiability up to permutation and scaling

For an invertible linear mixture of mutually independent nondegenerate components, if at most one component is Gaussian, then the independent components are identifiable from the distribution of `x` up to:

```text
permutation of components
nonzero scaling/sign of each component
```

under the standard ICA assumptions.

This is established parent mathematics, not a new GMI theorem.

### GMI derivation consequence

A latent independent-source representation is structurally justified when:

```text
observations are well modeled by invertible/approximately invertible mixing
latent factors are approximately independent
non-Gaussian structure breaks rotational ambiguity
source-factor representation reduces downstream semantic/development burden
```

The invariant ambiguity (permutation/scaling) should be quotiented out rather than treated as semantic uncertainty when downstream obligations are invariant to it.

---

# 4. Why decorrelation/PCA is not enough

Uncorrelated coordinates need not be independent outside the Gaussian family.

Therefore second-order covariance diagonalization can identify a low-rank/orthogonal representation but generally cannot recover independent non-Gaussian sources uniquely.

### GMI distinction

```text
PCA/factor state:
    optimize second-order reconstruction/variance geometry

ICA-like state:
    exploit higher-order/non-Gaussian independence structure
```

A general theory should not collapse these into one latent-compression mechanism.

---

# 5. Negative twins

```text
all-Gaussian independent sources:
    arbitrary orthogonal rotation remains equally valid -> source axes non-identifiable

noninvertible severe mixing:
    information about sources can be destroyed -> exact unmixing impossible

strong source dependence:
    ICA assumption itself fails -> independent latent state can be semantically wrong
```

---

# 6. Sample/particle belief approximation

Let exact belief distribution be `P` and let particles

\[
X_1,\ldots,X_N\overset{iid}{\sim}P.
\]

For bounded test/decision statistic

\[
f:X\to[a,b],
\]

define empirical estimate

\[
\hat\mu_N=\frac1N\sum_{i=1}^Nf(X_i),
\qquad
\mu=\mathbb E_Pf(X).
\]

## Theorem PB-1 — bounded particle expectation concentration

Hoeffding gives

\[
P(|\hat\mu_N-\mu|\ge\epsilon)
\le
2\exp\left(
-\frac{2N\epsilon^2}{(b-a)^2}
\right).
\]

Thus it is sufficient that

\[
\boxed{
N
\ge
\frac{(b-a)^2}{2\epsilon^2}
\ln\frac{2}{\delta}
}
\]

to estimate the registered bounded belief statistic within `epsilon` with confidence at least `1-delta`.

### GMI consequence

When exact belief closure is unavailable but protected decisions depend on a finite collection of bounded expectations, a sample/particle representation has an explicit accuracy-versus-memory/compute law.

---

# 7. Multiple protected belief queries

For `M` bounded test functions with the same range width, a union bound gives simultaneous accuracy `epsilon` with probability `1-delta` when

\[
N
\ge
\frac{(b-a)^2}{2\epsilon^2}
\ln\frac{2M}{\delta}.
\]

This connects particle count to the number of protected belief distinctions the species must answer.

---

# 8. Effective sample size warning

Real particle filters involve importance weights and resampling; particles are not generally IID from the exact posterior.

For normalized weights `w_i`, a common diagnostic is

\[
N_{eff}
=
\frac{1}{\sum_i w_i^2}.
\]

This is a diagnostic, not a universal theorem guaranteeing the IID Hoeffding rate.

### GMI requirement

Do not use nominal particle count `N` as capability state when weights collapse or resampling induces strong dependence. Register approximation mechanism, weight concentration and actual error evidence separately.

---

# 9. Degeneracy negative twin

If the target posterior concentrates in a region that proposal particles almost never reach, finite particle count can provide a grossly wrong belief even though the exact belief is well defined.

Thus sample-based belief is attractive only when the proposal/update process gives adequate target coverage.

This is the belief analogue of unseen-support transfer failure.

---

# 10. Gap update

Known-family probabilistic registry gains:

```text
ICA rotational Gaussian non-identifiability            CLOSED
ICA non-Gaussian linear identifiability                PARENT-THEOREM CLOSED
PCA-vs-independence distinction                        CLOSED
IID particle expectation accuracy law                  CLOSED
multi-query particle count law                         CLOSED

real nonlinear source separation                       OPEN
approximate independence/source discovery              OPEN
sequential importance/resampling error law              OPEN-BLOCKING
proposal degeneracy prediction                          OPEN-BLOCKING
```

---

# 11. Claim ceiling

ICA identifiability is conditional on its classical assumptions. The particle theorem is IID Monte Carlo, not a full convergence theorem for sequential Monte Carlo under arbitrary dynamics. Both are calibration laws that broader GMI theory must recover in their registered limits.
