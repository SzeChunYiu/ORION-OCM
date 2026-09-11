# GMI Bias–Resource Geometry v1

Status: **CANDIDATE CROSS-PARADIGM PRINCIPLE — PARENT-OWNED INDUCTIVE-BIAS MATHEMATICS, NEW SYNTHESIS ROLE**

Refs: #233, #377, `GMI_SEMANTIC_QUOTIENT_REALIZATION_THEOREM_V1.md`, `GMI_DEVELOPMENTAL_REALIZATION_PRINCIPLE_V1.md`.

## 1. Motivation

Track B began by asking whether neural, symbolic, probabilistic and programmatic intelligence are fundamentally different forms grown from one deeper substrate.

The realization work suggests a stronger architecture-neutral decomposition.

For a registered obligation `Omega`, every morphology supplies at least:

```text
1. a semantic realization of the required future distinctions;
2. an induced proposal / prediction / hypothesis / action bias;
3. an update law that changes that bias from experience;
4. a complete resource profile for building, serving, updating and maintaining it.
```

Two morphologies can look architecturally different while inducing closely related search/learning biases.

Conversely, two systems with the same architecture label can induce very different biases because of initialization, pretraining, data, optimizer, memory or controller state.

Therefore architecture labels may be scientifically downstream of a more general object:

\[
\boxed{
\mathcal G_M^\Omega
=
(S_\Omega, Q_M, U_M, \rho_M)
}
\]

with structural realization `M` supplying a concrete implementation.

---

# 2. Semantic state remains first

`S_Omega` is the obligation-relative semantic developmental quotient or declared approximation/sufficiency contract.

Bias is evaluated only among realizations that satisfy the same semantic/capability obligation at the registered scope.

A cheaper system that solves a weaker problem is not a better bias.

---

# 3. `Q_M` — cognition-generation / inductive-bias geometry

`Q_M` is the morphology's pre-solution distribution, ordering or restriction over possible future cognition/actions/hypotheses.

Examples:

```text
neural learner
  parameterization + initialization + features + pretraining
  induce a function/policy prior and optimization geometry

symbolic learner
  rule language + agenda + search ordering
  induce a discrete hypothesis/proof/action bias

Bayesian learner
  model class + prior
  explicitly induce posterior/predictive bias

program learner
  grammar + library + description lengths + recognition model
  induce a program/search prior

memory/skill system
  stored cases + retrieval index + ranking/applicability
  induce a retrieval/serving bias

OCM
  inherited fragments/assets + controller/applicability state
  induce a proposal/search order
```

`Q_M` need not be represented explicitly as a normalized probability distribution. Rank, code length, search schedule or deterministic proposal order can instantiate the same role when the semantics are defined.

---

# 4. `U_M` — how experience changes the bias

The central developmental question is how experience changes `Q_M`.

Examples:

```text
SGD changes parameters/features -> changes future predictions/proposal geometry
Bayes conditioning changes posterior -> changes predictive/action distribution
chunking/library learning changes rule/program search space
retrieval memory changes nearest cases / served skills
OCM history changes fragment/controller/search order
```

This is exactly HST's higher-level object:

```text
history -> changed future cognition generation.
```

The architecture is one mechanism that realizes `Q` and `U`.

---

# 5. `rho_M` — resources cannot be removed from the theory

A bias that gives excellent predictions but requires unbounded acquisition/search is not generally better.

Record at least where relevant:

```text
prior/hand-authored information
training/development work
persistent state / parameter bytes
proposal/search work
serving/inference work
verification/checker work
update/revision work
maintenance/indexing
plasticity / interference cost
morphology discovery cost
```

The scientific object is therefore **bias–resource geometry**, not inductive bias alone.

---

# 6. Parent ownership

Nothing in the statement “learning requires inductive bias” is new.

Parents include:

```text
No Free Lunch
Bayesian priors
PAC/PAC-Bayes
algorithmic probability / Levin/OOPS
statistical learning / hypothesis classes
meta-learning / learned inductive bias
DreamCoder/library learning
neural implicit bias literature
algorithm selection
resource rationality / bounded rationality
```

The GMI role is to use this as the common cross-paradigm coordinate tying semantic state, development, morphology and lifetime resources together.

---

# 7. GMI-BRG1 — architecture labels are not sufficient statistics for developmental behavior

In general,

```text
architecture family label
```

does not uniquely determine:

```text
Q_M
U_M
rho_M.
```

Examples:

- two identical Transformer architectures can have different pretrained weights and therefore different priors/skills;
- the same program grammar with a different learned library has different search geometry;
- the same production architecture with different chunks/utilities has different behavior;
- the same Bayesian update with different priors has different predictions.

Therefore a theory of machine-intelligence forms should characterize induced bias/update/resource behavior rather than classify only by visible architecture.

---

# 8. GMI-BRG2 — morphology can be scientifically meaningful through constrained realizability

Architecture is still important because it constrains which `Q,U,rho` triples are cheap, stable or learnable.

For example:

```text
dense differentiable parameterizations
  can make certain distributed biases cheap to update with gradients

explicit sparse rules/programs
  can make local exact revision/composition cheap

probabilistic factorizations
  can make uncertainty/marginalization explicit

memory/index systems
  can make one-shot persistence/retrieval cheap
```

So morphology is a **realization constraint on attainable bias–resource geometry**, not merely a cosmetic label.

This is where phase laws should live.

---

# 9. GMI-BRG3 — ecology alignment

Let an ecology induce a distribution `P_E` over tasks/targets.

Let a realization induce bias `Q_M` before protected target success.

A useful morphology-specific developmental effect requires some form of alignment:

```text
structures favored by Q_M
are more likely/useful under P_E
```

than under an appropriate control ecology.

This is deliberately broad. The exact bridge depends on the parent formalism:

```text
Bayesian expected log loss / KL
PAC-Bayes bound
program code length / search probability
proposal rank/surprisal
classification error
regret
useful-descendant mass
```

No one metric is universal without assumptions.

---

# 10. Exact finite cross-paradigm calibration

`gmi_cross_paradigm_bias_phase.py` uses one finite supervised-learning obligation:

```text
input domain: five ordered points
concept universe: all 2^5 = 32 deterministic Boolean labelings
structured subset: six monotone threshold concepts
```

The ecology parameter `p` is:

```text
with probability p:
  concept is uniform over the six threshold functions
with probability 1-p:
  concept is uniform over the 26 non-threshold functions.
```

Four learners use the same examples/test obligation:

```text
EXEMPLAR_MEMORY
  stores examples; unseen prediction = 1/2

SYMBOLIC_THRESHOLD
  version space over threshold functions

BAYES_THRESHOLD_MIX
  fixed mixture prior over threshold structure + universal Boolean concepts

PARAMETRIC_PERCEPTRON
  one-neuron linear-threshold model trained by the perceptron update
```

These are calibration realizations, not claims that a one-neuron learner represents modern deep learning.

---

# 11. Exact no-free-lunch phase point

The six threshold functions are `6/32 = 3/16` of the complete concept universe.

At

\[
p_0=3/16,
\]

every individual Boolean concept has equal probability `1/32`.

This is the uniform concept ecology.

For the registered held-out prediction score, exhaustive enumeration verifies:

```text
EXEMPLAR_MEMORY       average = 1/2
SYMBOLIC_THRESHOLD    average = 1/2
BAYES_THRESHOLD_MIX   average = 1/2
PARAMETRIC_PERCEPTRON average = 1/2
```

for every registered training-set size `m=1..4`.

This is a finite NFL-style calibration, not a GMI novelty theorem.

---

# 12. Bias phase reversal

For each of the three threshold-biased learners:

```text
average performance on threshold concepts    > 1/2
average performance on non-threshold concepts < 1/2
```

for the registered training sizes.

Therefore:

```text
p > 3/16 -> threshold-aligned bias has positive expected advantage over unbiased exemplar baseline
p = 3/16 -> advantage = 0
p < 3/16 -> the same bias is harmful on average.
```

The exact crossover is not evidence that the three morphologies are equivalent.

They have different:

```text
performance magnitude
state representation
update law
computation/storage cost
uncertainty semantics
```

What is common is the ecology alignment of their threshold-directed inductive bias.

---

# 13. Why this is an important Track-B correction

The exact toy suggests that the scientific unit above architecture labels may be:

```text
semantic obligation
+ induced bias/update geometry
+ resource realization.
```

A neural and a symbolic learner can share an ecologically aligned bias while realizing it differently.

A neural architecture with the wrong learned bias can be worse than a symbolic system, and vice versa.

This is consistent with parent learning theory and does not yet establish a universal cross-paradigm law.

---

# 14. Resource phase remains separate

The finite accuracy result intentionally does not assign hardware/runtime prices to the four algorithms.

After capability/bias calibration, attach separately measured/defined resource receipts.

Then ask which realization lies on the lifetime frontier.

Do not infer resource superiority from accuracy.

---

# 15. Strong falsifier of the broader hypothesis

The broader GMI bias-resource hypothesis fails to compress architecture choice usefully if:

```text
family label remains necessary after full pre-outcome Q/U/rho characterization;
no common bias quantities transfer across families;
family-native predictors always dominate with no cross-family residual;
resource response is too high-dimensional to predict across morphologies.
```

Allowed terminal:

```text
FAMILY_NATIVE_BIAS_RESOURCE_THEORIES_SUFFICIENT.
```

---

# 16. Next empirical ladder

## BRG-E0 — exact finite ecology phase

Current script/certificate.

## BRG-E1 — family-held-out synthetic transfer

Fit/freeze a common bias-alignment measure on two of:

```text
symbolic threshold
Bayesian prior
parametric gradient/perceptron
program-search prior
```

and test on the held-out family without architecture label.

## BRG-E2 — real OCM + formal proof/program family

Use direct pre-solution rank/surprisal measures where already available.

## BRG-E3 — real code/math

After #208/#46 real developmental receipts exist, ask whether the same bias-resource vocabulary explains anything prospectively across both verification regimes.

---

# 17. Current claim

Allowed:

```text
CROSS_PARADIGM_INDUCTIVE_BIAS_PHASE_EXACT_AT_FINITE_SCOPE
ARCHITECTURE_LABEL_NOT_PRIMARY_EXPLANATION_IN_REGISTERED_TOY
BIAS_RESOURCE_GEOMETRY_CANDIDATE_FOR_GMI
```

Not allowed:

```text
UNIVERSAL_BIAS_RESOURCE_LAW
NEURAL_AND_SYMBOLIC_INTELLIGENCE_EQUIVALENT
GENERAL_MACHINE_INTELLIGENCE_SOLVED
```

The upward Track-B hypothesis becomes:

> Machine-intelligence morphologies are resource-constrained realizations of semantic developmental states and induced cognition-generation biases. Ecologies select among these realizations by bias alignment and lifetime resource economics; development changes the bias, and morphogenesis changes which bias-resource geometries are reachable.

This is now precise enough to attack prospectively.
