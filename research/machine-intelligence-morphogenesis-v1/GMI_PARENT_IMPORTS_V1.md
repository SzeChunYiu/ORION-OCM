# GMI Parent Imports v1

Status: **adopt, do not reinvent**. This file records theorem/result modules that General Machine Intelligence Theory v1 treats as part of its foundation.

The point is not to claim these results as ORION novelty. The point is to build a coherent theory from the strongest mathematics already available.

## 1. Universal agent / performance theory

### Universal Artificial Intelligence / AIXI

Hutter combines sequential decision theory with Solomonoff-style universal induction to define a general agent in an unknown computable environment. UAI provides a rigorous top-down theory of intelligent action, while its ideal agent is uncomputable and practical approximations require additional assumptions/resources.

Anchors:
- Marcus Hutter, *A Theory of Universal Artificial Intelligence based on Algorithmic Complexity* (2000), https://arxiv.org/abs/cs/0004001
- Hutter, *Universal Artificial Intelligence*, https://www.hutter1.net/ai/uaibook2.htm

**Imported into GMI:**

```text
environment-relative intelligent behavior
sequential decision framing
algorithmic environment/model priors
formal optimal-agent ideal / computability boundary
```

**Not supplied by this parent:** practical morphology/developmental factorization law under complete resource accounting.

### Universal Intelligence measure

Legg & Hutter formalize an intelligence measure for arbitrary machines by averaging performance across environments with complexity weighting.

Anchor: Shane Legg & Marcus Hutter, *Universal Intelligence: A Definition of Machine Intelligence* (2007), https://arxiv.org/abs/0712.3329

**Imported:** the principle that generality requires an explicit weighting/class of environments. GMI's frontier/profile is intentionally more resource/development oriented and does not claim to supersede this measure.

---

## 2. Minimal / sufficient state theory

### Predictive-state representations

Littman, Sutton & Singh represent controlled-system state by action-conditional predictions of future observations and show that linear predictive representations can be no larger than the minimal POMDP state representation under their setting.

Anchor: *Predictive Representations of State*, NIPS 2001, https://proceedings.neurips.cc/paper/2001/file/1e4d36177d71bbb3558e43af9577d70e-Paper.pdf

### Computational mechanics / epsilon-machines

Causal states are equivalence classes of pasts with identical predictive distributions; epsilon-machines are minimal predictive representations under the theory's assumptions.

Anchor: Shalizi & Crutchfield, *Computational Mechanics: Pattern and Prediction, Structure and Simplicity*, https://arxiv.org/abs/cond-mat/9907176

### Bisimulation/state abstraction

Ferns, Panangaden & Precup define quantitative state similarity metrics for MDPs based on bisimulation, with value-function bounds.

Anchor: *Metrics for Finite Markov Decision Processes*, https://arxiv.org/abs/1207.4114

**Imported into GMI:**

```text
history/state equivalence by future consequences
minimal predictive/sufficient state
approximate state aggregation / bisimulation metrics
```

**GMI extension target:** include not only future environment observations/reward but future *machine development/update/resource traces* under a declared cognitive obligation.

---

## 3. Information / representation / bounded rationality

### Information Bottleneck

Tishby, Pereira & Bialek formulate representation learning as compressing an input while preserving information relevant to a target, deriving a rate-distortion-like variational problem.

Anchor: https://arxiv.org/abs/physics/0004057

### Information-theoretic bounded rationality

Ortega, Braun and collaborators formulate bounded rational action by trading utility against information-processing cost, yielding free-energy style decision principles.

Anchors:
- Ortega & Braun, *Information, Utility & Bounded Rationality*, https://arxiv.org/abs/1107.5766
- Ortega et al., *Information-Theoretic Bounded Rationality*, https://arxiv.org/abs/1512.06789

Gottwald & Braun further show information-processing constraints can induce specialization and hierarchical organization in bounded-rational multi-agent systems.

Anchor: https://arxiv.org/abs/1809.05897

**Imported into GMI:**

```text
relevant-information compression
performance-information cost tradeoff
resource-conditioned specialization/hierarchy
```

**GMI extension target:** complete developmental lifecycle resources, external verification, and cross-paradigm morphology comparison.

---

## 4. Factorization / structured state

Boutilier, Dearden & Goldszmidt show that MDPs with huge explicit state spaces can exploit dynamic-Bayesian-network / decision-tree factorization to obtain compact representations and structured dynamic programming.

Anchor: *Stochastic Dynamic Programming with Factored Representations*, Artificial Intelligence 121 (2000), https://www.cs.toronto.edu/~cebly/Papers/sdp.pdf

**Imported:**

```text
compact factorization of large global state
local conditional structure
structured planning / state aggregation
```

This is the direct parent for Track B's observation that an exponential global developmental quotient may still have a compact local realization.

---

## 5. Incremental program search / search-bias transformation

### OOPS

Schmidhuber's Optimal Ordered Problem Solver performs incremental bias-optimal program search and shifts future search bias by reusing successful code from prior tasks.

Anchor: https://people.idsia.ch/~juergen/nipsoops/nipsoops.html

### PowerPlay

PowerPlay jointly searches for new tasks and solver modifications, retaining old skills while increasing/speeding the solver's repertoire.

Anchor: https://arxiv.org/abs/1112.5309

**Imported:**

```text
history changes future search bias
program reuse / stored successful code
solver/task co-development
improving prior skills can itself be a developmental objective
```

Therefore ORION cannot claim generic history-induced future-search change as unique novelty.

---

## 6. Lifelong learning / meta-generalization

### PAC-Bayes lifelong learning

Pentina & Lampert derive a PAC-Bayesian generalization bound for lifelong learning, including transfer of parameters and low-dimensional representations to future unseen tasks.

Anchor: https://proceedings.mlr.press/v32/pentina14.html

### PACOH

Rothfuss et al. derive PAC-Bayesian meta-learning bounds and PAC-optimal hyper-posteriors with guarantees for unseen tasks.

Anchor: https://proceedings.mlr.press/v139/rothfuss21a.html

### Learning learning algorithms

Zakerinia, Behjati & Lampert extend PAC-Bayesian meta-learning to learning the learning algorithm itself, rather than only a prior over models.

Anchor: https://proceedings.mlr.press/v235/zakerinia24a.html

### Multitask representation learning

Maurer, Pontil & Romera-Paredes derive regimes in which shared representations improve multitask / learning-to-learn sample complexity.

Anchor: https://www.jmlr.org/papers/v17/15-242.html

### Lifelong regret

Alquier, Mai & Pontil derive regret bounds for sequential lifelong representation refinement.

Anchor: https://proceedings.mlr.press/v54/alquier17a.html

**Imported into GMI:**

```text
conditional future-task transfer guarantees
learned representations / priors / learning algorithms
formal dependence on task-relatedness assumptions
meta-overfitting/generalization as a real issue
```

**GMI consequence:** K2/K3 cannot be called new simply because history improves future learning; ORION must specify the verifier/resource/governance residual and empirical regime.

---

## 7. Morphogenesis / modularity / evolvability

### Modularly varying goals

Kashtan & Alon show that evolution under related goals that vary by recombining subgoals can spontaneously produce modular network organization and rapid adaptation.

Anchor: https://pmc.ncbi.nlm.nih.gov/articles/PMC1236541/

### Connection-cost modularity

Clune, Mouret & Lipson show that direct selection for lower connection cost alongside performance can produce more modular and evolvable networks.

Anchor: https://pmc.ncbi.nlm.nih.gov/articles/PMC3574393/

**Imported:**

```text
ecology structure can shape architecture
resource pressures can select modularity/hierarchy
morphology can affect future evolvability
```

Thus broad `ecology -> architecture -> future adaptation` is a parent result, not an ORION novelty claim.

---

## 8. Search/runtime / metareasoning / limits

GMI adopts the following families as mathematical infrastructure:

```text
Levin / universal search and algorithmic complexity
Rice algorithm selection
rational metareasoning / value of computation
stochastic-shortest-path and MDP control
additive/multiplicative/variable drift analysis
No-Free-Lunch theorems
Blum speedup and computability/halting limits
```

These own much of:

```text
search bias and universal allocation
portfolio/algorithm choice
cost-aware computation selection
potential/drift -> hitting-time bounds
limits on one universal best optimizer/program
```

---

# 9. Parent-module composition

The current theory can be read as the following composition:

```text
UAI / Universal Intelligence
        gives environment-relative intelligent performance

predictive state / epsilon-machine / bisimulation
        gives task-relative sufficient state

factored models + programming languages
        give computational realizations/factorizations

IB / bounded rationality / resource theory
        gives compression and cost-performance tradeoffs

search / algorithm selection / metareasoning
        gives resource-aware cognition allocation

PAC-Bayes / meta-learning / lifelong theory
        gives conditional developmental transfer

NAS / evolution / modularity / PowerPlay
        gives morphology and solver change

external verifier + constitution + complete developmental ledger
        gives the ORION governance/metrology layer
```

The scientific question is no longer whether each box is individually new. It is whether this composition is mathematically coherent, whether it yields useful derived results, and whether one invariant developmental law survives across materially different realization families.

## Current terminal

```text
PARENT_IMPORTS_ARE_FOUNDATIONAL_COMPONENTS_OF_GMI_V1
NO_REINVENTION_REQUIRED
NEW_LAW_OPTIONAL_BUT_PREDICTIVE_VALIDATION_REQUIRED_FOR_FIELD_LEVEL_NOVELTY
```