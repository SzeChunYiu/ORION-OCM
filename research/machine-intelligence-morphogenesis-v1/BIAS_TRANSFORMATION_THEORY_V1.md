# Bias Transformation Theory v1 — provisional synthesis

Status: **candidate synthesis, not a novelty claim.** Parent-heavy: universal induction/search, meta-learning, algorithm selection, resource rationality, continual learning, evolutionary search and HST all own substantial pieces.

## 1. Starting point

Bare universal computation does not explain practical intelligence. A practical learner must embody a bias about which computations/hypotheses/updates are worth trying.

Represent the effective developmental state as

\[
D_t=(\mathcal H_t,\pi_t,K_t,R_t,V_t,E_t),
\]

where:

- `H_t` — accessible hypothesis/representation/configuration class;
- `pi_t` — prior/proposal/search distribution or order;
- `K_t` — experience-conditioned update/proposal kernel;
- `R_t` — resource allocation / cost semantics;
- `V_t` — verifier/feedback interface;
- `E_t` — current ecology/task regime.

This is deliberately close to HST's `(L,Q,H,E,R,V,C)`; Track B should converge rather than create competing theory.

## 2. A machine-intelligence morphology is a bias package

A morphology corresponds to a structured region/factorization of `D_t`:

```text
architecture/topology affects H/pi/K
learned weights/rules/library affect pi/K
optimizer/search affects K
memory/indexes affect pi and resource cost
verifier coupling affects useful-feedback geometry
hardware affects R
```

Thus morphology cannot be identified from architecture alone.

## 3. Development is bias transformation

Ordinary within-form learning changes `D_t`:

\[
D_{t+1}=\Phi(D_t,e_t).
\]

Examples:

```text
pretraining changes pi / representation
MAML changes initialization and local K
library learning changes program prior/pi
Bayesian conditioning changes pi/posterior
production learning changes H and K
OCM history changes search order/applicability
```

A representation change alters `H`; learned routing changes `pi`; an optimizer change changes `K`; hardware/compiler changes alter `R`.

## 4. Meta-development

A stronger system learns how to choose transformations of its own developmental geometry:

\[
\Phi_{t+1}=\Psi(\Phi_t, \text{meta-experience}).
\]

This includes mature parent categories:

```text
meta-learning
learned optimizers
AutoML / NAS
algorithm selection
PowerPlay / self-improvement
evolution of plasticity / mutation operators
```

Therefore `bias transformation` itself is not ORION novelty.

## 5. A possible operational notion of developmental generality

For a distribution/sequence of ecologies, define the complete cost of adapting the developmental geometry and acquiring required competence.

A morphology-generator/meta-learner is more general at a registered scope when it achieves low regret / Pareto disadvantage relative to the best admissible fixed or switching morphology sequence while paying all meta-development cost.

Scalar example only when a price vector is frozen:

\[
Regret_T
=
C_{meta}(E_{1:T})
-
\inf_{M_{1:T}\in\mathcal A} C(M_{1:T};E_{1:T}).
\]

This is heavily parent-owned by online learning/experts/meta-learning and should be used as measurement, not novelty.

## 6. The upward Track-B residual

A field-level residual would require showing that the same theory predicts **how the bias package itself should change** as ecology/resource/verifier structure changes, and that the predicted transformation is recovered without a hand-supplied portfolio.

Candidate pattern:

```text
ecology structure
-> predicted developmental-geometry property
-> predicted frontier transition
-> neutral generator/search produces matching geometry
-> disjoint ecology confirms
```

## 7. Relationship to OCM

OCM's strongest existing developmental evidence can be interpreted as one measured bias transformation:

```text
verified history
-> changed proposal/search prior
-> later fresh solutions cheaper
```

This is evidence for a local change in `pi/K`, not evidence that the OCM asset schema is the universal atom.

OCM may later serve as one explicit implementation of a bias-transforming morphology with unusual governance/revision properties.

## 8. Current claim boundary

```text
BIAS_TRANSFORMATION_IS_A_UNIFYING_VIEW
NOT_A_NOVEL_GENERAL_INTELLIGENCE_THEORY_BY_ITSELF
PREDICTIVE_CROSS_PARADIGM_LAW_REQUIRED
```