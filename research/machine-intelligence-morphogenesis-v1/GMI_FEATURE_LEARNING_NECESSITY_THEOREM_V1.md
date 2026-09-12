# GMI Feature-Learning Necessity Theorem v1

Status: **FORMAL NONLINEAR-NEURAL REGIME HARDENING / R2**

Date: 2026-09-12.

## 1. Fixed-feature reachable set

For protected training/evaluation inputs `x_1,...,x_n`, let the current neural output vector be
\[
f_0\in\mathbb R^n
\]
and the current Jacobian/tangent feature matrix be
\[
\Phi_0 = D_\theta f_\theta(X)|_{\theta_0}\in\mathbb R^{n\times p}.
\]

Any exact fixed-feature/lazy first-order realization reachable inside this frozen tangent model has the form
\[
f_0+\Phi_0 a.
\]

For target vector `y`, define the tangent residual
\[
r_0=y-f_0
\]
and orthogonal projector `P_0` onto `col(\Phi_0)`.

## FL-1 — exact fixed-feature obstruction

The minimum squared error achievable by the frozen tangent family is exactly
\[
\boxed{
\inf_a\|y-f_0-\Phi_0a\|_2^2
=
\|(I-P_0)r_0\|_2^2.
}
\]

Therefore if
\[
(I-P_0)r_0\ne 0,
\]
no optimizer that remains inside the frozen tangent span can attain zero protected error.

Any exact solution must do at least one of:

1. change the feature/Jacobian span;
2. use higher-order/nonlinear motion outside the frozen linearization;
3. add new parameters/modules/features;
4. import an external state/mechanism that supplies the missing direction.

This is a **necessity theorem for feature change**, not a claim that a particular neural mechanism will discover the required feature.

## FL-2 — approximate nonlinear escape requirement

Assume the Jacobian is `L_J`-Lipschitz inside a parameter ball of radius `R`. For any update `Delta` with `||Delta||<=R`,
\[
f(\theta_0+\Delta)-f_0
=
\Phi_0\Delta + e(\Delta)
\]
with
\[
\|e(\Delta)\|_2\le \frac{L_J}{2}\|\Delta\|_2^2.
\]

Let
\[
d_\perp=\|(I-P_0)r_0\|_2.
\]

Then any update that reaches target error at most `epsilon` must satisfy
\[
\boxed{
\frac{L_J}{2}\|\Delta\|_2^2
\ge d_\perp-\epsilon.
}
\]

So if `d_perp > epsilon`, exact/near-exact success cannot occur in an arbitrarily small lazy neighborhood.

## GMI consequence

A zero-prior neural regime predictor can separate:

```text
LAZY / FIXED-FEATURE REGIME:
    tangent span already contains target correction
    and required movement stays inside linearization tolerance

FEATURE-LEARNING PRESSURE:
    protected target has a certified tangent-orthogonal residual
    too large to be explained by the registered nonlinear remainder
```

This is an implementation-invariant property test. It does not name MLP, CNN, Transformer, NTK, or any optimizer.

## Executed finite microscope

`run_gmi_feature_learning_necessity_v1.py` exhausts all `3 x 2` tangent matrices and 3-dimensional targets with entries in `{-1,0,1}`:

- 19,683 matrix/target cells;
- 5,353 are exactly reachable in the frozen tangent span;
- 14,330 have strictly positive tangent-orthogonal residual;
- zero projection-identity mismatches.

## Claim ceiling

This closes a **local necessity condition**, not practical feature-learning dynamics. Productive nonlinear feature discovery, optimizer dependence, high-dimensional estimation and held-family prediction remain open.
