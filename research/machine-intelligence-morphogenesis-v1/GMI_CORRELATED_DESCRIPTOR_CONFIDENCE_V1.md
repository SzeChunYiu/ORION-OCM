# GMI Correlated Descriptor Confidence v1

Status: **ASSUMPTION-INDEXED ESTIMATOR HARDENING / R3**

Date: 2026-09-12.

The earlier iid Hoeffding pilot is insufficient when dependency, residual, routing or ecology observations are correlated.

Let `X_t` be a stationary scalar descriptor with mean `mu`, variance `sigma^2`, and autocorrelation `rho_k`.

For
\[
\bar X_n=\frac1n\sum_{t=1}^n X_t
\]
the variance is exactly
\[
\boxed{
\operatorname{Var}(\bar X_n)
=
\frac{\sigma^2}{n}
\left[
1+
2\sum_{k=1}^{n-1}
\left(1-\frac{k}{n}\right)\rho_k
\right].
}
\]

Define the finite-sample correlation inflation
\[
\tau_n=
1+
2\sum_{k=1}^{n-1}
\left(1-\frac{k}{n}\right)\rho_k.
\]

Then
\[
\operatorname{Var}(\bar X_n)=\sigma^2\tau_n/n.
\]

## CD-1 — assumption-indexed confidence radius

If a prospectively justified upper bound
\[
\sigma^2\tau_n\le V_n
\]
is available, Chebyshev gives
\[
\Pr\left(
|\bar X_n-\mu|\ge
\sqrt{\frac{V_n}{n\delta}}
\right)
\le\delta.
\]

This is weaker than iid concentration but valid under the registered second-order dependence bound.

A descriptor extractor that silently substitutes iid `n` for effective sample size is invalid when `tau_n>>1`.

## Two-state Markov exact calibration

For a stationary two-state chain with `P(X=1)=pi` and second eigenvalue `rho`, autocorrelation is exactly `rho^k`, so the variance formula is closed form by the finite geometric sum.

A deterministic Monte Carlo calibration over nine `(pi,rho)` cells, 10,000 trajectories per cell and length 128 gives worst relative variance error about `2.74%`.

## GMI consequence

Pre-outcome descriptor reports must include:

```text
sampling unit
dependence/mixing assumption
effective information or tau_n interval
uncertainty radius
abstention condition when the dependence bound is not identified
```

## Claim ceiling

This does not solve arbitrary high-dimensional dependence. It replaces an invalid iid assumption with a typed correlation-aware estimator contract.
