# Analog substrate semantics and bounded numerical-reduction theorem v1

## Semantics

An analog cognitive realization is the declared tuple

\[
(X,U,f,\eta,P,x_0,\rho,T),
\]

with state/input spaces, dynamics \(\dot x=f(x,u,t)+\eta\) (or an explicitly
sampled transition), noise law/bound \(\eta\), numeric/physical precision
instrument \(P\), initialization \(x_0\), readout \(\rho\), and finite
horizon \(T\). Capability equality always names an input class, output norm,
error tolerance, and failure probability. The formal schema and 23-coordinate
lifecycle accounting prohibit free conversion, calibration, settling, readout,
energy, or drift correction.

## Theorem AS-1 — assumption-indexed D1/D6 reduction

On a bounded region suppose \(f\) is computable, L-Lipschitz in state, and a
one-step numerical method has local truncation at most \(C h^2\). Then after
\(N=T/h\) steps its global state error is bounded by

\[
\|e_N\|\le C h\frac{e^{LT}-1}{L}
\]

(with factor \(T\) at \(L=0\)). Thus error at most \(\epsilon\) follows
from

\[
h\le\frac{\epsilon L}{C(e^{LT}-1)},qquad
N=O\!\left(\frac{TC(e^{LT}-1)}{\epsilon L}\right).
\]

**Proof.** The error recurrence
\(e_{k+1}\le(1+Lh)e_k+Ch^2\), unrolled as a geometric sum and bounded by
\((1+Lh)^N\le e^{LT}\), gives the displayed inequality. ∎

D1 stores the parameters/function approximation and D6 stores the numerical
state and transition. The compiler has finite, explicit overhead at every
declared \((T,\epsilon,L,C,d,P)\). It does not establish a uniform polynomial
bound if those coordinates grow adversarially or regularity fails.

For sampled rational affine interval systems
\(x'\in ax+bu+[-\delta,\delta]\), the compiler is exact rather than
approximate. The certificate exhausts 162 parameter/input/state/noise cases with
zero interval or compiler violations.

## Claim ceiling

These two proof-only tasks are closed. The Issue #602 task “Identify any real
burden separation” remains open: a semantics and simulation bound are not a
measurement of physical advantage.
