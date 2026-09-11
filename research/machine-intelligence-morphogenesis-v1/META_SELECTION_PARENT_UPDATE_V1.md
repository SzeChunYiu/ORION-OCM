# Meta-selection / meta-learning parent update v1

Status: **parent subtraction for the surviving morphology-phase claim.**

## 1. Algorithm selection already owns fixed-portfolio phase prediction

Rice's 1976 Algorithm Selection Problem explicitly separates:

```text
problem/instance space
feature space
algorithm space
performance space
```

and asks for a mapping from instance features to the algorithm expected to perform best under the chosen performance criterion.

Therefore a Track-B result of the form

```text
measure ecology features
-> choose neural vs symbolic vs probabilistic from a human-supplied portfolio
```

is an **algorithm-selection result**, not by itself a new general theory of machine intelligence.

Required terminal if no stronger residual exists:

```text
ALGORITHM_SELECTION_PARENT_SUFFICIENT
```

## 2. Meta-learning already owns experience-conditioned future priors/learners

PAC-Bayes meta-learning work explicitly learns experience-dependent priors/distributions over hypotheses from previous tasks to improve learning on future related tasks. More recent formulations can learn the learning algorithm itself rather than only a model prior.

Therefore:

```text
past tasks reshape prior over future hypotheses
```

and even

```text
past tasks improve the future learning algorithm
```

are parent-owned at a broad level.

Track B must not call these phenomena novel solely because they are expressed as developmental geometry.

## 3. Rational metareasoning owns cost-aware computation choice

Russell & Wefald treat computations as actions whose value depends on their expected effect on downstream action quality minus computational cost.

Therefore:

```text
choose search/probe/update because expected downstream value exceeds cost
```

is parent-owned.

## 4. Stochastic shortest path owns finite cost-to-target dynamics

For finite morphology/configuration spaces, expected cost to reach a verified target under stochastic transitions is naturally a stochastic shortest-path / MDP problem.

Again, Track B receives no novelty credit for merely writing a costed developmental graph.

## 5. Residual after these parents

The strongest remaining Track-B question is narrower and higher:

> Can a compact, architecture-neutral generative basis and structural theory predict the *emergence and developmental geometry* of morphology classes that are not supplied as a fixed algorithm portfolio, and can those predictions transfer across morphology paradigms and held-out ecologies?

This requires all of:

```text
endogenous morphology generation
not just portfolio selection

structure -> geometry prediction
not just measured historical performance

developmental/resource equivalence
not source-code labels

family-scale bounded acquisition/compilation
not one-off finite simulation

prospective phase prediction
not post-hoc algorithm selection

unknown-form reduction against all applicable parents
```

## 6. Strongest possible parent-product null

A very strong null is:

```text
universal/program basis
+ AutoML/NAS/program evolution
+ algorithm selection
+ meta-learning
+ rational metareasoning
+ ordinary resource accounting
```

If that parent product reproduces the complete Track-B signature, then ORION's contribution is a useful integration/metrology framework, not a distinct foundational intelligence law.

Registered terminal:

```text
PARENT_PRODUCT_SUFFICIENT_FOR_GMI_SIGNATURE
```

## 7. Current consequence

Do not spend research effort proving that one can:

- select different known algorithms in different regimes;
- learn a prior over related future tasks;
- value computations by expected downstream utility;
- express finite development as an MDP.

Those are foundations to **use**.

Spend effort on the unresolved mapping:

\[
\text{structure / factorization / update law}
\to
\text{developmental geometry}
\to
\text{prospective frontier}
\to
\text{endogenously generated morphology}.
\]

## Parent anchors

- John R. Rice, *The Algorithm Selection Problem*, Advances in Computers 15, 1976.
- Ron Amit & Ron Meir, *Meta-Learning by Adjusting Priors Based on Extended PAC-Bayes Theory*, ICML 2018.
- Zakerinia, Behjati & Lampert, *More Flexible PAC-Bayesian Meta-Learning by Learning Learning Algorithms*, ICML 2024.
- Stuart Russell & Eric Wefald, *Principles of Metareasoning*, Artificial Intelligence 49, 1991.
- Dimitri Bertsekas & John Tsitsiklis, *An Analysis of Stochastic Shortest Path Problems*, MOR 16(3), 1991.
