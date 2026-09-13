# Generalization Identifiability Parent Subtraction V1

Status: **PARENT BOUNDARY EXPLICIT**  
Date: 2026-09-13

## Parent-owned content

Grand GMI does not claim invention of statistical learning theory, version spaces, identifiability, minimax prediction, PAC/VC theory or No-Free-Lunch results.

Wolpert/Schaffer-style No-Free-Lunch results establish severe limits on assumption-free induction across unrestricted target families. Standard statistical/computational learning theory makes learnability depend on restrictions on the hypothesis/model class, sampling process and loss.

## Grand-GMI residual

This tranche contributes an architecture-free, obligation-typed generalization object:

\[
R_{gen}(E,D,T)
=
\sup_{z\in D(E)}
\inf_y\sup_{e:D(e)=z}d_Y(y,T(e)).
\]

It thereby separates:

- what the protected training/probe process actually observed (`D`);
- what worlds remain admitted (`E`);
- which held-out response the obligation asks for (`T`);
- how much unresolved target ambiguity remains (`R_gen`);
- which additional structure or information would be needed to shrink it.

The scientific residual is not “learning needs inductive bias.” It is the exact integration of that fact into the same Grand-GMI semantic/resource machinery and the resulting prospective-prediction gate:

`THEORY_DETERMINED_TO_EPSILON requires feasible centers and a selector in the frozen predictor class`.

The necessary scalar condition `R_gen<=epsilon` is sufficient in the unrestricted class under strict slack or an appropriate attainment theorem. At equality an unattained infimum can leave the tolerance infeasible; GIR-6 therefore checks the actual feasible-center sets. This distinction and the required compactness/measurable-selection machinery are parent-owned optimization and decision theory.

This makes post-hoc explanation and prospective prediction operationally distinguishable in the formal theory.
