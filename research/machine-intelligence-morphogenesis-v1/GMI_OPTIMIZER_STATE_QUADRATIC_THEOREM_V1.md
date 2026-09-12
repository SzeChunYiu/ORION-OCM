# GMI Optimizer-State Quadratic Theorem v1

Status: **FORMAL DEVELOPMENT-STATE LAW / R2**

Date: 2026-09-12.

A developmental theory that records only the current parameters but not optimizer state is incomplete whenever future reachability is protected.

For a quadratic mode with curvature `lambda`, Polyak heavy-ball development
\[
x_{t+1}=x_t-\eta\nabla f(x_t)+\beta(x_t-x_{t-1})
\]
induces the scalar error recurrence
\[
e_{t+1}=(1+\beta-\eta\lambda)e_t-\beta e_{t-1}.
\]

Thus two learners with identical current `x_t` but different `(x_{t-1}, beta)` can have different protected futures.

## OS-1 — optimizer state is developmental state

The Markov state for heavy-ball development is at least
\[
(x_t,x_{t-1})
\]
(or an equivalent momentum state), not `x_t` alone.

This is an exact collision theorem: equal current parameters do not imply equal future development.

## OS-2 — optimal quadratic asymptotic factor

For a positive-definite quadratic with spectrum in `[mu,L]`, the classical heavy-ball parameter choice
\[
\eta_*=\frac{4}{(\sqrt L+\sqrt\mu)^2},
\qquad
\beta_*=
\left(\frac{\sqrt L-\sqrt\mu}{\sqrt L+\sqrt\mu}\right)^2
\]
has worst modal root radius
\[
\boxed{
q_{HB}
=
\frac{\sqrt L-\sqrt\mu}{\sqrt L+\sqrt\mu}.
}
\]

Optimal fixed-step gradient descent has factor
\[
q_{GD}=\frac{L-\mu}{L+\mu}.
\]

For `L>mu`,
\[
q_{HB}<q_{GD}.
\]

The point is not novelty: this is a parent optimization result. The GMI consequence is that optimizer memory has a quantitative, ecology-relevant reachability effect and must be charged as developmental state/burden when future learning is in scope.

## Executed calibration

`run_gmi_optimizer_state_quadratic_v1.py` checks 100 `(mu,L)` spectral intervals, sampling 101 eigenvalues per interval. Numerical root radii match the analytic factor within `5e-8`; all 92 nontrivial `L>mu` intervals show a strictly smaller asymptotic factor than optimal fixed-step GD.

## Kill / scope

Heavy-ball can be worse outside its registered assumptions. This theorem does not predict Adam, SGD noise, nonconvex basin discovery, or modern deep-network feature learning.
