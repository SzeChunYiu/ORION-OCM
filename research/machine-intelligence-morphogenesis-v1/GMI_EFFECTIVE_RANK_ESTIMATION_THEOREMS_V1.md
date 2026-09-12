# GMI Effective-Rank Estimation Theorems v1

Status: **PARENT MATRIX-PERTURBATION INTEGRATION / ASSUMPTION-INDEXED ESTIMATOR**

Status date: 2026-09-12.

Purpose:

> Use one matrix-perturbation theorem to harden several zero-prior descriptors that depend on latent rank/effective dimension: predictive/Hankel state, low-rank adaptation, PCA/factor state, and conditional-specialization mode rank.

---

# 1. Noisy matrix observation

Let true registered matrix be

\[
A\in\mathbb R^{m\times n}
\]

and observed/estimated matrix

\[
\widehat A=A+E.
\]

Assume an externally justified operator-norm error bound

\[
\|E\|_{op}\le\varepsilon.
\]

Let singular values in descending order be `sigma_i(A)` and `sigma_i(Ahat)`.

---

# 2. Parent theorem ER-1 — singular-value perturbation

Weyl/Mirsky perturbation theory gives

\[
|\sigma_i(\widehat A)-\sigma_i(A)|
\le
\|E\|_{op}
\le\varepsilon
\]

for every singular-value index `i`.

This is established parent matrix analysis.

---

# 3. Exact rank recovery under a spectral gap

Suppose true rank is `r`, so

\[
\sigma_r(A)>0,
\qquad
\sigma_{r+1}(A)=0.
\]

## Theorem ER-2 — thresholded rank is exactly identifiable when signal exceeds twice the error radius

If

\[
\sigma_r(A)>2\varepsilon,
\]

then thresholding observed singular values at `epsilon` recovers the exact rank:

\[
\#\{i:\sigma_i(\widehat A)>\varepsilon\}=r.
\]

### Proof

For `i<=r`, in particular the smallest nonzero singular value,

\[
\sigma_r(\widehat A)
\ge
\sigma_r(A)-\varepsilon
>
\varepsilon.
\]

For `i>r`, `sigma_i(A)=0`, so

\[
\sigma_i(\widehat A)\le\varepsilon.
\]

QED.

### Interpretation

Rank is not inherently unmeasurable; it is measurable when the smallest retained singular direction is separated from the observation/noise uncertainty.

---

# 4. Effective rank at semantic tolerance

For tolerance `tau>0`, define effective rank

\[
r_\tau(A)=\#\{i:\sigma_i(A)>\tau\}.
\]

## Theorem ER-3 — robust effective-rank classification away from the threshold

If every singular value lies outside the uncertainty band

\[
[\tau-\varepsilon,\tau+\varepsilon],
\]

then

\[
r_\tau(A)
=
\#\{i:\sigma_i(\widehat A)>\tau\}.
\]

More generally:

```text
observed sigma_i > tau+epsilon  -> true sigma_i > tau
observed sigma_i < tau-epsilon  -> true sigma_i < tau
inside the band                 -> rank membership unresolved
```

This yields an explicit abstention region instead of false certainty.

---

# 5. Predictive/Hankel state application

For finite observed Hankel block `H`, minimal exact linear predictive-state dimension is its rank only if the block is sufficient for the full process.

With noisy estimate `Hhat`, ER-2/ER-3 provide a **within-block** rank/effective-rank guarantee once an operator error bound is available.

Two distinct uncertainties must therefore be reported:

```text
measurement/statistical matrix error:
    ||Hhat-H||_op

coverage error:
    whether chosen prefixes/suffixes expose the full infinite/process rank
```

ER-2 solves the first, not the second.

---

# 6. Low-rank adaptation application

Let true task-update/residual matrix be `Delta`. If an estimator `Deltahat` satisfies

\[
\|\widehat\Delta-\Delta\|_{op}\le\varepsilon
\]

and `sigma_r(Delta)>2epsilon` while higher singular values vanish/negligible under the registered tolerance, then the update rank is identifiable by thresholding.

This turns the LoRA/adapter structural rule into an assumption-indexed pre-outcome estimator when the residual matrix can be probed from development information.

---

# 7. Mode-specialization application

Stack mode/task parameter vectors as rows of matrix

\[
\Theta.
\]

The earlier mode-rank theorem identifies minimal linear shared-basis dimension as

\[
\operatorname{rank}(\Theta).
\]

If mode parameter estimates are noisy, ER-2/ER-3 determine when the shared-basis dimension is robustly identifiable and when uncertainty overlaps the specialization boundary.

---

# 8. PCA/factor-state application

For covariance/data matrix with singular/eigenvalue spectrum, rank truncation is meaningful only relative to estimation uncertainty and semantic tolerance.

A singular direction below the matrix-error radius cannot be declared a stable latent factor from that estimate alone.

This guards against overinterpreting small empirical eigenvalues as true factors.

---

# 9. How to obtain epsilon

The theorem deliberately treats

\[
\varepsilon
\]

as an input to be justified by the measurement model.

Possible sources include:

```text
matrix concentration from IID samples
bootstrap/validated uncertainty
bounded deterministic numerical error
intervention/probe repetition
hardware precision/noise guarantees
```

A guessed error radius does not close the estimator gap.

---

# 10. Negative twin / impossibility zone

If

\[
\sigma_r(A)\lesssim\varepsilon,
\]

then an observed matrix can be consistent with worlds of different exact/effective rank inside the uncertainty ball.

No estimator based only on `Ahat` and that error guarantee can universally distinguish them.

Thus the spectral gap is an identifiability condition, not just a convenient numerical heuristic.

---

# 11. Gap update

The same theorem narrows several gaps:

```text
GKF-07 predictive-state dimension:
    noisy finite-block rank estimation with gap     CLOSED
    infinite-horizon coverage                       OPEN-BLOCKING

GKF-08 residual/update rank:
    noisy residual rank with gap                    CLOSED
    constructing residual estimator                 OPEN

GKF-06 mode rank:
    noisy linear mode-rank with gap                 CLOSED
    nonlinear functional rank                       OPEN-BLOCKING

PCA/factor state:
    spectrum/rank uncertainty rule                  CLOSED
    task-semantic factor relevance                  OPEN
```

---

# 12. Claim ceiling

Weyl-type perturbation bounds do not solve data coverage, nonlinear manifold dimension or the problem of obtaining a valid operator-norm error radius. They turn rank estimation into an explicit signal-gap-versus-uncertainty test instead of an untyped heuristic.
