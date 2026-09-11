# Morphogenesis null model v1 — generic selection is parent-owned

Status: **strong ordinary parent/null**, not a proposed ORION novelty.

## 1. Why Gamma needs a null model

Writing

```text
Gamma(B,E,R,V,H) -> M
```

is not yet a theory. Bayesian model selection, MDL, universal/bias-optimal search, PAC-Bayes, rate-distortion, evolutionary selection and architecture search already provide broad ways to select structures under data/performance/cost pressure.

Track B must therefore test whether a morphology law says more than:

> search many candidate machines and keep the one with best penalized performance.

---

# 2. Scalarized parent baseline

Only when a capability utility and resource price vector are frozen prospectively, define a lifecycle objective such as

\[
J_E(M)=
C_{build}(M)
+ C_{acquire}(M,E)
+ H\,C_{use}(M,E)
+ C_{update}(M,E)
+ C_{verify}(M,E)
+ C_{maint}(M,E)
+ Risk(M,E)
- \lambda Q(M,E).
\]

Then a generic selection parent is simply

\[
M^*(E)=\arg\min_M J_E(M).
\]

If no scalar utility/price vector is scientifically justified, the primary object remains the Pareto frontier rather than `J`.

---

# 3. Probabilistic/Gibbs-style parent baseline

Given a structural prior `pi_B(M)` induced by basis/description language `B`, a generic distribution over candidate morphologies can be written schematically as

\[
P(M\mid E) \propto \pi_B(M)\exp[-\beta J_E(M)].
\]

This resembles familiar Bayesian/MDL/Gibbs selection ideas. It is useful as a mathematical baseline but receives no Track-B novelty credit.

Alternative parents include universal-code priors and resource-bounded search schedules.

---

# 4. What a real morphology law must add

A useful Track-B law must predict, before protected architecture search, something like:

```text
as ecology coordinate z crosses registered threshold z*,
frontier membership should switch from morphology family A to B
```

and the prediction should survive:

```text
new task family
new encoding/search implementation
strong parent configurations
raw resource accounting
```

The scientific content therefore lies in deriving **which ecology coordinates alter which lifecycle terms and why**, not in the argmin itself.

Candidate coordinates currently include:

```text
reuse horizon
feedback/credit information structure
noise/stochasticity
compositional/algorithmic structure
partial observability
exact-verification strength/cost
revision/drift rate
memory/compute/communication prices
parallel hardware structure
```

---

# 5. Phase boundary skeleton

For two morphologies `A,B` at matched capability, a simple affine lifecycle model gives

\[
J_A-J_B
= \Delta C_{build}
+H\Delta C_{use}
+r\Delta C_{revision}
+\cdots.
\]

A phase boundary occurs where

\[
J_A(E)=J_B(E).
\]

The already-executed toy amortization calibration is one trivial instance.

This equality is arithmetic, not a new intelligence law. The nontrivial work is to predict the cost functions/frontier from structural properties of `E` and `M` and then confirm them prospectively.

---

# 6. Parent families to subtract

At minimum:

```text
Bayesian model selection
Minimum Description Length
Solomonoff/universal coding priors
Levin/bias-optimal search
PAC-Bayes / complexity-regularized learning
rate-distortion / information bottleneck
neural architecture search / AutoML
multiobjective/Pareto optimization
quality-diversity/evolutionary selection
resource-rational metareasoning
```

If one of these parents predicts the registered morphology transition without a new Track-B mechanism:

```text
PARENT_SELECTION_LAW_SUFFICIENT
```

and Track B absorbs it.

---

# 7. What remains potentially upward

The candidate residual is:

> **A small set of measurable ecology/resource/verification coordinates predicts the developmental Pareto frontier among non-equivalent machine-intelligence morphologies, with the transition derived from how those coordinates interact with representation, credit assignment, topology, update law and persistence.**

That is substantially stronger than ordinary architecture search and substantially narrower than a universal-best-intelligence claim.
