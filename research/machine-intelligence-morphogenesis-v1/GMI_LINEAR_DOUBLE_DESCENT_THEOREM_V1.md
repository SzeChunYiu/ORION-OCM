# GMI linear double-descent theorem v1

Status: **EXACT RANDOM-DESIGN BASE LAW / T2 NARROWING**

Date: 2026-09-12.

Purpose: give the modern-overparameterization/generalization programme an exact limit case that any broader nonlinear theory must recover.

## 1. Registered teacher-student world

Let training rows be iid

\[
x_i\sim N(0,I_d),
\qquad y_i=x_i^T\beta+\epsilon_i,
\qquad \epsilon_i\sim N(0,\sigma^2).
\]

Use ordinary least squares when `d<n` and the minimum-Euclidean-norm interpolating solution when `d>n`. Protected test covariates are iid `N(0,I_d)`. Excess squared prediction risk equals

\[
E\|\hat\beta-\beta\|_2^2.
\]

## 2. Theorem DD-1 — underparameterized exact expectation

For `n>d+1`, OLS is unbiased and

\[
E[R_{excess}]
=\sigma^2\frac{d}{n-d-1}.
\]

This follows from the inverse-Wishart identity

\[
E[(X^TX)^{-1}]=\frac{I_d}{n-d-1}.
\]

## 3. Theorem DD-2 — overparameterized minimum-norm exact expectation

For `d>n+1`, the minimum-norm estimator decomposes into projection of `beta` onto the random row space plus fitted noise. Rotational symmetry gives expected nullspace signal loss

\[
\left(1-\frac nd\right)\|\beta\|_2^2.
\]

Since `XX^T` is Wishart with `d` degrees of freedom,

\[
E\,tr[(XX^T)^{-1}]=\frac{n}{d-n-1}.
\]

Hence

\[
E[R_{excess}]
=
\left(1-\frac nd\right)\|\beta\|_2^2
+
\sigma^2\frac{n}{d-n-1}.
\]

## 4. Interpolation phase

Both finite-sample formulas diverge as the dimension approaches the interpolation boundary from their valid sides. Far into the overparameterized regime, the variance term falls again while the nullspace bias approaches its own asymptote. Thus nonmonotone risk versus parameter dimension is already an exact consequence of development rule + random geometry; parameter count alone is not a monotone intelligence coordinate.

## 5. GMI interpretation

The relevant coordinates are

```text
sample count n
effective developed dimension d
noise sigma^2
source/feature alignment and signal norm
implicit solution selector (minimum norm here)
conditioning / interpolation proximity
```

A broader neural theory must explain how nonlinear feature learning changes these effective coordinates rather than treating overparameterization itself as an explanation.

## 6. Negative twins

- Different implicit bias/regularization changes the formula.
- Anisotropic/non-Gaussian design changes the spectral law.
- Nonlinear learned features make `d` and alignment endogenous.
- At `|n-d|<=1` these expectations are not finite under the stated unregularized model.

## 7. Executed calibration

`run_gmi_linear_double_descent_v1.py` uses deterministic Gaussian Monte Carlo on 14 under/overparameterized cells, 500 trials per cell. All cells fall within 10% relative error of the exact expectation; worst observed relative deviation is approximately 0.05077.

Receipt: `GMI_LINEAR_DOUBLE_DESCENT_RECEIPT_V1.json`.

## Claim ceiling

This is an exact isotropic linear random-design theorem plus finite Monte Carlo calibration. It does not solve nonlinear deep-network generalization, but it is now a mandatory reduction test for any proposed GMI neural generalization law.
