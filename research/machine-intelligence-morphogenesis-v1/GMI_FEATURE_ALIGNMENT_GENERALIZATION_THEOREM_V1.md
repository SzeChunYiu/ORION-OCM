# GMI Feature-Alignment Generalization Theorem v1

Status: **EXACT TEACHER-STUDENT GENERALIZATION LAW / ZERO-PRIOR CALIBRATION**

Status date: 2026-09-12.

Purpose:

> Give GMI an exact finite-sample law linking representation/feature alignment, effective dimension and protected generalization. This supplies a solvable base case for the broader question of why a learned lower-dimensional feature representation can generalize better than a larger expressive one.

---

# 1. Registered source model

Let input

\[
x\sim\mathcal N(0,I_d)
\]

and semantic target be

\[
f^*(x)=\beta^Tx.
\]

Development labels include independent noise

\[
y=f^*(x)+\epsilon,
\qquad
\epsilon\sim\mathcal N(0,\sigma^2).
\]

Choose an `r`-dimensional orthogonal feature subspace with projector `P`, where

\[
0\le r<d.
\]

Decompose signal

\[
\beta=P\beta+(I-P)\beta.
\]

Define omitted semantic signal energy

\[
B=\|(I-P)\beta\|_2^2.
\]

Fit ordinary least squares using only the `r` retained orthonormal feature coordinates from `n` IID development examples. Assume

\[
n>r+1.
\]

Protected loss is squared error to the **noise-free semantic target** `f*(x)`, not to a fresh noisy label.

---

# 2. Reduction to retained and omitted Gaussian coordinates

By rotational invariance, write

\[
x=(z,u),
\]

where

\[
z\sim\mathcal N(0,I_r),
\qquad
u\sim\mathcal N(0,I_{d-r})
\]

independently, and

\[
f^*(x)=a^Tz+b^Tu
\]

with

\[
\|b\|^2=B.
\]

From the retained feature model's viewpoint, the omitted term plus label noise is independent effective noise

\[
\eta=b^Tu+\epsilon
\]

with variance

\[
\sigma_{eff}^2=B+\sigma^2.
\]

---

# 3. Exact expected estimation error

Let design matrix

\[
Z\in\mathbb R^{n\times r}
\]

have IID standard normal rows. OLS satisfies

\[
\hat a-a
=(Z^TZ)^{-1}Z^T\eta.
\]

Conditional on `Z`,

\[
\mathbb E[\|\hat a-a\|^2\mid Z]
=(B+\sigma^2)\operatorname{tr}((Z^TZ)^{-1}).
\]

For Gaussian design, `Z^TZ` is Wishart and for `n>r+1`,

\[
\mathbb E[(Z^TZ)^{-1}]
=
\frac{I_r}{n-r-1}.
\]

Therefore

\[
\mathbb E\|\hat a-a\|^2
=
(B+\sigma^2)\frac{r}{n-r-1}.
\]

---

# 4. Theorem FA-1 — exact expected protected generalization error

The expected semantic test error of the `r`-dimensional feature realization is

\[
\boxed{
R_r
=
B
+
(B+\sigma^2)\frac{r}{n-r-1}
}
\]

for `n>r+1`.

### Proof

For independent test input `(z,u)`, prediction error is

\[
(\hat a-a)^Tz-b^Tu.
\]

Conditional cross term vanishes by independence/zero mean. Expected squared error is

\[
\mathbb E\|\hat a-a\|^2+\|b\|^2.
\]

Substitute the Wishart expectation above. QED.

---

# 5. Full-dimensional comparator

Fit ordinary least squares on all `d` features, assuming

\[
n>d+1.
\]

There is no representation bias (`B=0`), so

\[
\boxed{
R_d
=
\sigma^2\frac{d}{n-d-1}
}.
\]

---

# 6. Theorem FA-2 — exact compression/generalization crossover

The `r`-dimensional feature realization has lower expected protected error than the full `d`-dimensional OLS realization iff

\[
\boxed{
B
<
\sigma^2\frac{d-r}{n-d-1}
}.
\]

### Proof

Compare `R_r<R_d` and solve for `B`. Using

\[
\frac{d}{n-d-1}-\frac{r}{n-r-1}
=
\frac{(d-r)(n-1)}{(n-d-1)(n-r-1)},
\]

and

\[
1+\frac{r}{n-r-1}
=
\frac{n-1}{n-r-1},
\]

yields the stated threshold. QED.

---

# 7. Interpretation

The exact phase law separates two quantities:

```text
feature/source misalignment:
    B = semantic signal energy omitted by the representation

finite-data variance saved by compression:
    sigma^2 (d-r)/(n-d-1)
```

Thus lower-dimensional features win when the semantic signal they discard is smaller than the estimation variance they save.

Predictions:

```text
larger observation noise sigma^2:
    favors stronger dimension reduction

smaller development sample n:
    favors stronger dimension reduction

better source alignment (smaller B):
    favors reduced feature state

large omitted semantic energy B:
    favors richer representation

n -> infinity:
    variance advantage vanishes and any fixed B>0 eventually favors full features under this exact model
```

---

# 8. Why this matters for neural theory

A deep network can be viewed, in one regime, as learning a representation followed by a simpler predictor.

FA-1/FA-2 show exactly what a broader GMI neural generalization theory must estimate:

\[
\boxed{
\text{task-relevant feature alignment}
\quad\text{versus}\quad
\text{effective estimation dimension}
}
\]

Raw parameter count is not sufficient.

A highly overparameterized model may still behave like a low-effective-dimensional predictor if development selects/learns a well-aligned feature subspace; conversely a compact but misaligned representation can have irreducible bias.

---

# 9. Relation to PCA and low-rank state

PCA minimizes reconstruction error of inputs, whereas FA-1 cares about **target-semantic signal energy** omitted by the feature subspace.

A high-variance input direction can be irrelevant to `beta`; a low-variance direction can be critical to the target under non-isotropic sources.

Therefore unsupervised variance compression and task-relevant predictive compression must be distinguished.

---

# 10. Negative twins

## Perfect alignment

If `B=0`, the lower-dimensional feature representation strictly reduces expected estimation error relative to a larger model under the registered finite-data assumptions.

## Missed target direction

If `B` exceeds the FA-2 threshold, compression hurts protected generalization despite lower variance.

## No label noise / abundant data

As noise vanishes or sample size grows, the variance-saving justification for discarding real semantic signal disappears.

---

# 11. Extensions / open variables

The exact theorem assumes:

```text
isotropic Gaussian inputs
fixed orthogonal feature subspace
linear target
ordinary least squares
homoskedastic Gaussian label noise
```

A broader theory needs:

```text
non-isotropic source covariance
learned/data-dependent feature maps
nonlinear targets
classification/margin semantics
feature-learning development cost
overparameterized/interpolating regimes
source shift
```

But every broader law should recover FA-1/FA-2 in this limit.

---

# 12. Gap update

`GKF-03` / T2 gains:

```text
finite-family description bound                         CLOSED
stability mechanism                                    CLOSED
PAC-Bayes mechanism                                    CLOSED/PARENT
implicit linear development selection                  CLOSED
exact feature-alignment/effective-dimension risk law   CLOSED

learned nonlinear feature alignment estimator          OPEN-BLOCKING
overparameterized nonlinear risk prediction            OPEN-BLOCKING
mechanism-selection law                                OPEN-BLOCKING
```

---

# 13. Claim ceiling

This is an exact teacher-student linear-Gaussian generalization theorem. It does not explain modern deep-network generalization by itself. It makes one important hidden variable—task/source alignment versus effective dimension—quantitative and falsifiable.
