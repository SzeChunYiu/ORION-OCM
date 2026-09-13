# Robust Decision Precision Parent Subtraction V1

Status: **PARENT BOUNDARY EXPLICIT**  
Date: 2026-09-13

## Parent-owned content

The following are established theory and are not claimed as Grand-GMI inventions:

- Wald-style minimax statistical decision theory;
- robust optimization with worst-case loss/objective functions;
- perturbation and sensitivity analysis of optimization/argmin decisions;
- Blackwell comparison of experiments and data-processing/garbling arguments;
- recent prior-free/ambiguity-aware Blackwell-style experiment comparison under maxmin criteria.

In particular, the generic fact that extra information can simulate a garbled experiment is classical, and the algebraic perturbation inequality behind a `2 delta` regret guarantee is elementary robust-decision mathematics.

## Grand-GMI residual

The contribution of this tranche is the typed placement of decision precision inside the unifying morphology chain.

Grand GMI first derives the obligation, ecology and robust decision coordinates. Only then does it ask how much numerical/statistical/model precision is sufficient:

\[
\text{uniform loss error }\delta
\Longrightarrow
\text{robust regret }\le2\delta.
\]

This implication requires a nonempty finite action set, finite precision, a finite robust optimum, and actual selection of an estimated minimizer. Absolute score differences are formed only for finite scores. With certified estimated-selection slack `alpha`, the bound is `2 delta+alpha`. These domain and approximate-optimization distinctions are parent theory; see Boyd and Vandenberghe, [*Convex Optimization*, section 4.1.1](https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf).

Therefore a declared tolerance `epsilon` induces the sufficient precision gate

\[
\delta\le\epsilon/2,
\]

while a unique exact-action obligation with robust margin `Delta` induces

\[
\delta<\Delta/2.
\]

The equality margin can force a tie, so unique action preservation uses a strict inequality. A singleton action set is stable without a competing margin calculation. These are sufficient gates from the declared certificates; an inadequate error bound alone does not prove the underlying realization inadequate.

The precision certificate may come from quantization theory, numerical analysis, sampling bounds, sensor physics, approximation theory or another parent domain. GMI does not replace those sources; it composes them with the obligation-derived decision margin/tolerance and the physical resource frontier.

This is what makes finite precision, sensing quality, model accuracy and confidence **machine-intelligence morphology variables** rather than implementation afterthoughts.
