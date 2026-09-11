# Learning-Law Atlas v1

Status: **cross-paradigm mapping / parent subtraction**.

A general morphogenesis theory must explain not only how machines compute, but how experience changes them. The generic statement

\[
M_{t+1}=U(M_t,e_t)
\]

is too broad to be scientifically useful by itself: almost any learning algorithm can be hidden inside an arbitrary `U`.

Track B therefore records the **structure** of known update laws and asks which parts can be derived from a smaller basis.

---

## 1. Gradient / neural learning

Canonical form:

\[
\theta_{t+1}=\theta_t-\eta_t\nabla_\theta J_t(\theta_t).
\]

Structural requirements:

```text
parameterized differentiable computation
objective/loss
credit propagation / derivative structure
optimizer state
```

Parents:

```text
backpropagation
Backprop as Functor
MAML
learned optimizers
differentiable plasticity
```

Track-B question:

> Can a candidate basis derive gradient-style credit assignment with bounded overhead without supplying `BACKPROP` as a primitive?

---

## 2. Bayesian / probabilistic updating

Canonical finite form:

\[
P_{t+1}(h)
=\frac{P(e_t\mid h)P_t(h)}{\sum_{h'}P(e_t\mid h')P_t(h')}.
\]

Structural requirements:

```text
hypothesis distribution
likelihood/evidence model
normalization or equivalent inference semantics
```

Parents:

```text
Bayesian inference
probabilistic programming
Markov categories
Bayesian program learning
```

Track-B question:

> Is stochastic/measure structure fundamental, or can it be resource-boundedly compiled from deterministic primitives plus randomness without collapsing the morphology distinction?

---

## 3. Production / rule acquisition

Generic form:

\[
G_{t+1}=G_t\cup\{r(e_t,H_t)\}
\]

with applicability/utility revision over existing rules.

Structural requirements:

```text
explicit condition/action structure
matching/application
rule induction/chunking
conflict resolution / utility
```

Parents:

```text
Soar chunking
ACT-R production learning
rule induction
TMS/ATMS where revision is involved
```

Track-B question:

> Can explicit discrete rule growth be derived from the same basis as neural parameter adaptation without treating rules as opaque programs?

---

## 4. Program/library learning

Generic form:

\[
\mathcal L_{t+1}
=
CompressOrSynthesize(\mathcal L_t,\text{solved traces},V).
\]

Structural requirements:

```text
executable program language
composition/call
search/synthesis
verification/evaluation
library admission
```

Parents:

```text
OOPS
DreamCoder
Stitch
CEGIS
genetic programming
FunSearch / AlphaEvolve-class program evolution
```

Track-B question:

> Can a cross-paradigm basis derive executable abstraction/library growth without importing a universal interpreter that makes the result vacuous?

---

## 5. Evolutionary / population update

Generic form:

\[
\mathcal P_{g+1}
=
SelectMutateRecombine(\mathcal P_g,E_g).
\]

Structural requirements:

```text
population / archive
variation operator
selection/evaluator
inheritance
```

Parents:

```text
NEAT / HyperNEAT
Genetic Programming
MAP-Elites / QD
novelty search
POET
DGM / evolutionary self-improvement variants
```

Track-B question:

> Is population-level evolution a distinct morphology update law, or a meta-level search process external to individual cognition? Track B must state which level is being compared.

---

## 6. Local plasticity / self-organizing updates

Generic form:

\[
\theta_{ij,t+1}
=
\theta_{ij,t}+f(local\ state_i,local\ state_j,modulator_t).
\]

Parents:

```text
Hebbian plasticity
differentiable plasticity
neural cellular automata / local developmental systems
```

This family is important because it weakens the false dichotomy “central gradient learner versus explicit symbolic learner.”

---

# Cross-paradigm structural coordinates

Instead of classifying update laws only by historical names, record:

```text
local vs global credit
continuous vs discrete state
explicit vs distributed competence
single-machine vs population update
exact vs approximate verification
online vs batch update
whether topology can change
whether the update law itself can change
revision locality
retention/plasticity tradeoff
required information surface
```

This vector is a candidate bridge between named paradigms and a true morphogenesis theory.

---

# Anti-vacuity rule

A generic update primitive

```text
UPDATE(machine, experience) -> arbitrary machine
```

is forbidden as a fundamental explanation.

It would make every learning law derivable by definition and return:

```text
UNIVERSAL_COMPUTATION_ONLY
```

A valid basis must expose enough structure that learning-law compilation cost, locality, information needs and resource tradeoffs can differ and be predicted.

---

# Immediate exact targets

After the Stage-C basis is frozen, attempt tiny derivations of:

```text
L0 one scalar gradient update
L1 one finite Bayesian posterior update
L2 one learned production/rule insertion
L3 one two-subprogram library/macro insertion
L4 one population mutation-selection step
```

The same basis need not make all equally cheap. Differences in bounded compilation/update cost are exactly the data Track B wants.

Allowed result:

```text
COMMON_BASIS_WITH_MORPHOLOGY_DEPENDENT_UPDATE_COSTS
```

which is more informative than forcing all learning laws to look identical.
