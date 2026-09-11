# GMI Parent Assumption Map v1

Status: **F1 hardening**. Parent results are adopted only under their actual assumptions. GMI-v1 may compose them, but composition does not erase assumption boundaries.

---

# 1. UAI / AIXI / Universal Intelligence

## Imported result family

Universal Artificial Intelligence combines sequential decision theory with Solomonoff-style universal induction to define an ideal general agent over computable environments. Universal Intelligence defines a broad environment-weighted performance measure.

## Assumptions / boundaries relevant to GMI

```text
sequential interaction setting
specified action/percept/reward semantics
algorithmic probability / universal-machine dependence up to constants
AIXI ideal is uncomputable
performance measure depends on the chosen environment class/weighting
resource/developmental accounting is not the primary object
```

## GMI may use it for

```text
environment-relative general-agent framing
warning that a generality measure requires an environment measure
formal ideal-agent parent / upper-level comparison
```

## GMI may NOT infer

```text
practical computable optimality of a morphology
one unique architecture
learning/morphogenesis resource efficiency
externally verified truth from internal reward
```

Primary anchors:
- Hutter, arXiv `cs/0004001`
- Legg & Hutter, arXiv `0712.3329`

---

# 2. Predictive State Representations (PSR)

## Imported result family

Action-conditional predictions of future observations can serve as state; linear PSRs can be no larger than the minimal POMDP representation in the studied setting.

## Assumptions / boundaries

```text
controlled stochastic dynamical system
state defined for prediction of future observations under actions/tests
linear PSR result has its own linear-system/rank construction
not a theorem about arbitrary learner self-modification/resource history
```

## GMI use

PSR is a strong parent for the idea that state can be defined by future observable consequences rather than hidden implementation variables.

## GMI extension

GMI future traces additionally include registered machine-development and resource receipts when those are part of the obligation.

Primary anchor:
- Littman, Sutton & Singh, NeurIPS 2001, *Predictive Representations of State*.

---

# 3. Computational mechanics / epsilon-machines

## Imported result family

Past histories are grouped by equality of conditional future distributions; causal-state representations provide minimal predictive representations under the framework's assumptions.

## Assumptions / boundaries

```text
stochastic-process prediction setting
causal states defined by predictive equivalence of pasts
typically passive-process prediction unless extended
minimality/uniqueness is relative to predictive semantics
```

## GMI use

Direct parent for future-equivalence quotients and task-relative minimality.

## GMI may NOT infer

That the predictive causal state is automatically sufficient for action, learning-algorithm state, resource accounting or self-modification unless those future consequences are included in the equivalence contract.

Primary anchor:
- Shalizi & Crutchfield, *Computational Mechanics: Pattern and Prediction, Structure and Simplicity*.

---

# 4. MDP bisimulation metrics / state abstraction

## Imported result family

State similarity can be defined using reward/transition similarity and related to value-function differences in discounted MDPs.

## Assumptions / boundaries

```text
MDP setting
registered reward/transition model
particular discount/value assumptions for bounds
state abstraction concerns future control value/transition behavior
```

## GMI use

Parent for approximate future-equivalence and quantitative state aggregation.

## GMI extension

If the machine's own future learning/update/resource state is a protected quantity, it must be included in the meta-state/transition semantics before applying an abstraction theorem.

Primary anchor:
- Ferns, Panangaden & Precup, *Metrics for Finite Markov Decision Processes*.

---

# 5. Information Bottleneck / rate-distortion

## Imported result family

Compress an input/representation while retaining information relevant to a target; optimize a relevance–compression tradeoff.

## Assumptions / boundaries

```text
defined joint distributions / relevance variable
specific mutual-information objective
representation-rate/relevance tradeoff
not automatically a sequential action or development theory
```

## GMI use

Parent for task-relative representation compression and information-resource phase phenomena.

## GMI may NOT infer

That mutual information alone captures compute, learning, verification, maintenance or plasticity cost.

Primary anchor:
- Tishby, Pereira & Bialek, *The Information Bottleneck Method*.

---

# 6. Information-theoretic bounded rationality

## Imported result family

Decision policies trade expected utility against information-processing cost relative to a prior/default policy; constraints can induce specialization/hierarchy.

## Assumptions / boundaries

```text
defined utility/payoff
specific KL/information cost
choice of prior/default policy matters
usually scalarized objective
```

## GMI use

Parent for resource-conditioned specialization and rational information/computation allocation.

## GMI extension

GMI keeps a raw multi-resource vector and external admissibility semantics before choosing a scalarized objective.

---

# 7. Factored MDPs / DBNs / graphical models

## Imported result family

Large global state/action models can have compact structured representations when transition/reward dependencies factor sparsely; algorithms can exploit the structure.

## Assumptions / boundaries

```text
chosen state-variable factorization
conditional dependency structure
algorithmic benefit depends on sparsity/structure and solver
factorization discovery itself may be hard
```

## GMI use

Direct parent for the distinction between huge minimal/global state spaces and compact local/factored realizations.

## GMI may NOT infer

That one particular factorization is fundamental or that compact factorization is always cheap to learn/maintain.

Primary anchor:
- Boutilier, Dearden & Goldszmidt, *Stochastic Dynamic Programming with Factored Representations*.

---

# 8. OOPS / PowerPlay / universal program search

## Imported result family

Incremental program search can reuse previous solutions/code and change future search bias; solver and task repertoire can co-develop.

## Assumptions / boundaries

```text
specified programming language/search bias
specified verification/task semantics
bias-optimality claims are relative to search setup/resources
reuse benefit is ecology/task dependent
```

## GMI use

Parent for K1-style history-induced search transformation and solver/task co-development.

## GMI may NOT infer

That every history improves future tasks, that the result is cross-domain, or that K2/K3 follows from K1.

---

# 9. PAC-Bayes lifelong / meta-learning

## Imported result family

Prior tasks sampled under declared meta-environment assumptions can support bounds on future unseen tasks through learned priors/representations/learning algorithms.

## Assumptions / boundaries

```text
meta-distribution / task-sampling assumptions
specified hypothesis/prior/posterior/learner class
probabilistic confidence/generalization statement
bound quality may be loose
relatedness is not arbitrary-domain transfer
```

## GMI use

Parent theorem module for conditional K2-style future-learning improvement.

## GMI may NOT infer

Unconditional learning-to-learn across unrelated domains or externally verified real-world capability from a formal bound alone.

Primary anchors:
- Pentina & Lampert 2014 PAC-Bayesian lifelong learning;
- Maurer, Pontil & Romera-Paredes 2016;
- Alquier, Mai & Pontil 2017;
- PACOH / later PAC-Bayes meta-learning.

---

# 10. Modularity / facilitated variation / architecture evolution

## Imported result family

Related varying goals and/or connection-cost pressure can cause modular/hierarchical architectures to emerge and can accelerate adaptation/evolvability.

## Assumptions / boundaries

```text
specific evolutionary representation/variation operators
specific task-goal families
fitness/resource pressure definition
architecture family/search regime
```

## GMI use

Parent evidence that morphology is ecology/resource dependent and that architecture can carry future-adaptation bias.

## GMI may NOT infer

One universal morphology phase law or cross-paradigm quantitative prediction from these family-specific results alone.

Primary anchors:
- Kashtan & Alon 2005 PNAS;
- related facilitated-variation work;
- Clune, Mouret & Lipson 2013.

---

# 11. Algorithm selection / rational metareasoning

## Imported result family

Given instance/context features and a portfolio of algorithms/computations, choose the one with best expected performance/value net of computation cost.

## Assumptions / boundaries

```text
portfolio/candidate computation set specified
performance/value model or learnable features
cost/utility semantics declared
selection does not itself imply endogenous invention of new algorithms
```

## GMI use

Parent for fixed-portfolio morphology choice and executive computation allocation.

## GMI extension

Endogenous morphogenesis asks how the portfolio/candidate structures themselves arise/change.

---

# 12. Drift / stochastic-shortest-path theory

## Imported result family

Given a valid progress potential or Markov costed state model, derive/bound expected hitting time/cost.

## Assumptions / boundaries

```text
valid potential/drift or transition/cost model
stopping conditions
technical boundedness/integrability conditions depend on theorem
```

## GMI use

Parent for `developmental geometry -> burden` once geometry/potential is already supplied.

## GMI may NOT infer

That a useful compact morphology-independent potential can be derived from raw architecture for free.

---

# 13. No-Free-Lunch / computability / speedup limits

## Imported limits

GMI adopts limits against:

```text
one universally best optimizer over unrestricted closed problem classes
one exact computable burden/reachability predictor for arbitrary Turing-complete systems
one guaranteed asymptotically fastest program for every computable problem class under unrestricted claims
```

These limits do not forbid strong conditional theories on structured ecologies.

---

# Composition rule

Parent modules may be composed only when their assumptions are simultaneously satisfied or an explicit bridge theorem/empirical calibration is supplied.

Forbidden move:

```text
Parent A proves X under assumptions A
Parent B proves Y under assumptions B
therefore GMI proves X+Y for arbitrary machines
```

Required move:

```text
state assumptions A ∩ B
show the GMI specialization satisfies them
then import the corresponding conclusions
```

## Current F1 status

```text
PARENT_ASSUMPTION_MAP_V1_REGISTERED
PRIMARY_SOURCE_RECONSTRUCTION_PARTIAL
FORMAL_REDUCTION_PROOFS_PARTIAL
```

F1 closes only after the major reduction maps are checked against the precise parent statements rather than abstract-level summaries.