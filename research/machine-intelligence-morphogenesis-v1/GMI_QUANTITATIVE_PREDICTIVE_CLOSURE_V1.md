# GMI Quantitative and Predictive Closure v1

Status: **THEORY-HARDENING CONTRACT / NO CLAIM OF UNIVERSAL COMPLETION**

Status date: 2026-09-12.

Purpose:

> Replace vague statements such as “mechanism X matters” with quantitatively testable response laws, explicit residuals, competing parent laws, uncertainty and closure criteria.

This document defines what it means, at a registered scope, to have no hidden theoretical, quantitative or predictive gap.

---

# 1. Registered scientific cell

A closure cell is

\[
c=(\mathcal E,\mathcal O,P,\mathcal M,\mathcal J,Y),
\]

where:

- `E` is the registered ecology family;
- `O` is the semantic obligation;
- `P` is exogenous resource/substrate context;
- `M` is the compared morphology family;
- `J` is the legal intervention family;
- `Y` is the protected outcome/burden vector.

Closure is always relative to `c`. There is no scope-free claim that all possible intelligence has been solved.

---

# 2. Three residual gaps

For every claim maintain three distinct residuals.

## 2.1 Theory residual

A theory residual exists when a necessary causal arrow, variable, mechanism, side channel, history dependence or semantic distinction has no typed representation.

Let

\[
G_T(c)=\{g_1,\ldots,g_k\}
\]

be unresolved typed theory obligations.

`THEORY_CLOSED_AT_SCOPE` requires `G_T(c)=empty` after recursive hardening, with every dependency either proved, imported under assumptions, empirically registered, falsified/replaced or explicitly outside scope.

## 2.2 Quantitative residual

A quantitative residual exists when direction is known but magnitude/threshold/scaling remains unspecified where it is required to predict the frontier.

For response component `Y_j`, require a registered response law

\[
\hat Y_j=f_j(X,P,A,H;\theta_j)
\]

with:

- pre-outcome covariates `X`;
- resource context `P`;
- mechanism witnesses `A`;
- developmental history `H` where needed;
- parameter/functional uncertainty on `theta_j`.

The raw quantitative residual is

\[
r_j=Y_j-\hat Y_j.
\]

A model is not quantitatively closed merely because mean error is small. Residuals must be tested for structure against all registered omitted-variable probes.

## 2.3 Predictive residual

A predictive residual exists when the law fits development worlds but fails to transfer prospectively.

For protected ecology `e` define

\[
r_j^{P}(e)=Y_j(e)-\hat Y_j(e\mid D,V),
\]

where the prediction was frozen using only development/validation information.

`PREDICTIVELY_CLOSED_AT_SCOPE` requires calibrated held-out predictive intervals and no registered structured residual that survives fresh-family, surface-remint and substrate interventions.

---

# 3. Closure tuple

For each scientific cell publish

\[
C(c)=(T,Q,P,I,S,R),
\]

where:

- `T` = theory dependency closure;
- `Q` = quantitative response closure;
- `P` = prospective predictive closure;
- `I` = identifiability / implementation-invariance closure;
- `S` = scaling/domain-of-validity closure;
- `R` = parent-reduction closure.

No aggregate scalar may hide failure on one coordinate.

Use statuses:

```text
GREEN    closure criterion passed at registered scope
AMBER    bounded residual remains but does not block weaker claims
RED      blocking residual / falsification
OPEN     not yet tested
N/A      legitimately outside registered scope
```

---

# 4. Required quantitative law types

Not every phenomenon should use the same model. At minimum distinguish:

```text
L1 exact algebraic/finite theorem
L2 inequality/lower/upper bound
L3 monotone directional law
L4 finite crossover/threshold law
L5 stochastic response distribution
L6 finite-size/scaling law
L7 causal treatment-effect law
L8 survival/hazard/history law
L9 multiobjective Pareto/frontier law
L10 morphology-transition law
```

A named mechanism without one of these or an explicit `OPEN` status is incomplete.

---

# 5. Predictive sufficiency standard

For outcome vector `Y`, a registered descriptor `Psi` is predictively adequate only if, on protected data,

\[
Y \perp W \mid \Psi(X,P,A,H)
\]

for every registered nuisance/surface variable `W` that should not matter, up to declared tolerance and statistical power.

Operationally:

1. fit `Psi -> Y` on D/V only;
2. freeze model and uncertainty procedure;
3. predict protected families;
4. test residual association with reminted IDs, architecture labels, latent generator families, substrate labels and omitted mechanism probes;
5. if structured association remains, the descriptor is not closed.

This is stronger than pooled AUROC/R2.

---

# 6. Quantitative mechanism score

For a mechanism `a` under intervention `j`, estimate a burden-aware causal response

\[
\tau_a(x,p)=E[Y\mid do(a=1),x,p]-E[Y\mid do(a=0),x,p].
\]

For multiobjective outcomes publish the vector `tau_a`, not a hidden weighted sum.

A mechanism law is accepted only if:

- sign/direction is frozen before P;
- the matched negative twin approaches the predicted null/crossover;
- implementation-equivalent realizations agree within tolerance;
- unrelated surface remints do not change the effect;
- effect heterogeneity is explained by registered coordinates or is promoted to a new gap.

---

# 7. Frontier prediction

Let

\[
\mathcal F(e)=Pareto\{Y(M,e):M\in\mathcal M\}.
\]

The strongest GMI prediction target is not exact scalar rank but a distribution over frontier membership and mechanism core:

\[
Pr(M\in\mathcal F(e)\mid X_e,P_e,A_M,H_M)
\]

and

\[
Pr(a\in K^*(e)\mid X_e,P_e).
\]

Closure requires:

- calibrated frontier-membership probabilities on held-out families;
- uncertainty-aware comparison where Pareto regions overlap;
- mechanism-core prediction under substrate repricing;
- no architecture-family label used as a shortcut.

---

# 8. Scaling closure

Any claimed scaling law must declare:

```text
independent scale variable(s)
resource coupling assumptions
finite-size correction
saturation/bottleneck model
measurement floor/ceiling
metric transform
extrapolation interval
```

A law such as

\[
L(N)=aN^{-b}+L_\infty
\]

is not accepted merely because it fits one range. Competing broken-power-law, logistic/saturation, piecewise and resource-reallocation parents receive first refusal.

No phase-transition language without an order parameter plus size-scaling evidence.

---

# 9. Residual escalation rule

Every structured residual becomes a new registered object.

If residual `r` correlates with variable `z` after freeze:

```text
DO NOT post-hoc patch protected predictions and keep the same P set.
DO retire that P set for the altered theory.
DO type z as demand, context, mechanism response, history or nuisance.
DO construct a collision/negative twin.
DO freeze the successor law.
DO generate fresh protected worlds.
```

This rule turns failure into theory growth rather than benchmark fitting.

---

# 10. Quantitative no-gap checklist

A scientific cell has no known quantitative/predictive gap only if all applicable items are GREEN:

```text
Q1 target semantic variable operationalized
Q2 intervention variables operationalized
Q3 full lifecycle burden meter frozen
Q4 response function class frozen or nested comparison registered
Q5 parameter uncertainty calibrated
Q6 replicate hierarchy correct
Q7 held-out family prediction performed
Q8 substrate repricing performed if P is causal
Q9 surface/remint invariance passed
Q10 implementation-equivalence passed
Q11 negative twins/collisions passed
Q12 residual structure audit passed
Q13 parent quantitative laws compared
Q14 extrapolation/scaling domain declared
Q15 Pareto uncertainty reported
Q16 adaptive-search cost charged
Q17 fresh P used after theory changes
```

Failure of any required item prevents `QUANTITATIVELY_CLOSED_AT_SCOPE`.

---

# 11. Closure budget and priority

For every open gap `g`, assign

\[
Priority(g)=\frac{Pr(change\ claim\mid result)\cdot ClaimValue(g)}{ExpectedCost(g)}.
\]

This is a research-priority heuristic, not evidence.

P0 gaps are those that can invalidate current high-level claims; P1 alter quantitative boundaries; P2 improve resolution; P3 are nonblocking extensions.

---

# 12. Required machine-readable registry

The implementation should maintain a row per claim with at least:

```text
claim_id
claim_text
scope
theory_type
quant_law_type
pre_outcome_predictors
interventions
outcomes
parent_laws
negative_twins
implementation_equivalents
D/V/P receipt ids
residual_tests
status_T/status_Q/status_P/status_I/status_S/status_R
blocking_dependencies
next_high_information_experiment
```

The theory is not allowed to say “no gaps” if the registry contains a blocking OPEN/RED cell.

---

# 13. Strong terminal

The strongest legal terminal is:

```text
NO_KNOWN_UNTYPED_OR_UNTESTED_BLOCKING_GAP_AT_REGISTERED_SCOPE
```

It means:

- every known dependency is typed;
- every required magnitude has a law/bound or explicit open entry;
- every strong law has prospective protected testing;
- structured residuals have been exhausted by the registered hostile suite;
- no stronger parent law explains the evidence with lower burden.

It never means that future mathematics or new ecologies cannot expose a new gap.
