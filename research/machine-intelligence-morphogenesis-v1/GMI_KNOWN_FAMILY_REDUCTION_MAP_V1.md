# GMI Known-Family Reduction Map v1

Status: **ZERO-PRIOR REGISTRY HARDENING / EXACT OR DEFINITIONAL REDUCTIONS**

Status date: 2026-09-12.

Purpose:

> Prevent the known-family registry from becoming an endless list of historical acronyms. A named family does not require an independent GMI primitive if it is an exact special case, composition, or bounded reduction of already-derived carrier/operator mechanisms.

A family is considered structurally covered when either:

1. GMI derives its defining property vector from obligation/resource geometry; or
2. there is a clear bounded semantics-preserving reduction to already-derived mechanisms, with any extra assumptions stated explicitly.

This document is about structural derivation. Quantitative held-family prediction and neutral rediscovery remain separate gates.

---

# 1. Linear/statistical reductions

## Ridge regression = linear coefficient state + quadratic state price

Consider squared loss with `L2` penalty

\[
J(\theta)=\|y-X\theta\|_2^2+\lambda\|\theta\|_2^2.
\]

This is exactly the linear-coefficient state of KF-1 with an additional registered quadratic parameter burden.

When interpreted probabilistically with Gaussian observation noise and isotropic Gaussian prior on `theta`, minimizing this objective is also the MAP estimator up to scale constants.

**Reduction:** coefficient state + prior/regularization burden. No new carrier.

## Logistic regression / GLM = coefficient state + output-link semantics

For Bernoulli target with

\[
P(Y=1|x)=\sigma(\theta^Tx),
\]

negative log likelihood is binary cross entropy. The developmental state remains coefficient vector `theta`; only the observation/decision link differs.

More generally a GLM combines linear sufficient predictor `eta=theta^Tx` with a registered response-family/link law.

**Reduction:** coefficient state + likelihood/link operator. The unresolved zero-prior issue is response-family/link selection, not a distinct domain.

## Linear discriminant analysis = Gaussian belief + coefficient decision boundary

With class-conditional Gaussians sharing covariance, log posterior odds are affine in `x`. Hence the Bayesian belief model compiles into a linear discriminant rule.

**Reduction:** Gaussian probabilistic belief + compiled linear decision rule.

---

# 2. Basis and kernel reductions

## Polynomial/spline/RBF models

All are coefficient states over a chosen basis

\[
f(x)=\sum_j\theta_j\phi_j(x).
\]

Differences lie in basis geometry, locality and regularization.

**Reduction:** basis-coefficient state. The gap is zero-prior basis discovery/adequacy.

## Kernel machines

`GMI_KERNEL_AND_GP_DERIVATION_THEOREMS_V1.md` proves the RKHS representer theorem by orthogonal decomposition: the regularized solution lies in the span of observed kernel sections.

**Reduction:** similarity-defined basis expansion + coefficient state.

## Gaussian process

Finite-query GP posterior is Gaussian conditioning over function values.

**Reduction:** probabilistic belief state + kernel similarity geometry.

---

# 3. Partition/ensemble reductions

## Random forest

A random forest is a collection of decision-tree predictors plus an aggregation rule.

**Reduction:** recursive-partition realization + ensemble aggregation. Its distinctive quantitative questions are tree diversity/correlation, bootstrap/randomization cost and serving burden.

## Bagging

**Reduction:** replicate/perturb development data -> multiple predictors -> ensemble averaging/voting. The ensemble variance/correlation law already supplies the core benefit condition.

## Gradient boosting

**Reduction:** staged additive residual correction over weak learners. `GMI_KNOWN_FORM_DERIVATION_THEOREMS_V1.md` already derives the additive residual property; remaining issue is weak-learner accessibility/generalization.

## Stacking

**Reduction:** heterogeneous ensemble + learned aggregation coefficient/model. No new carrier.

---

# 4. Probabilistic reductions

## Naive Bayes

**Reduction:** probabilistic belief + conditional-independence factorization. PB-1 gives the exact posterior product law.

## Bayesian network / factor graph

**Reduction:** probabilistic belief with sparse factorization induced by conditional-independence/compatibility structure. Graph structure changes inference burden, not the existence of probability-state semantics.

## HMM

**Reduction:** recurrent probabilistic belief. PB-2 gives exact recursive belief update.

## Kalman filter

**Reduction:** HMM/state-estimation belief specialized to linear-Gaussian closure. PB-3 gives exact finite `(mean,covariance)` state.

## Particle filter

**Reduction:** approximate probabilistic belief represented by an empirical weighted sample measure when exact parametric closure is unavailable.

The open question is particle count/error/cost, not a new semantic domain.

## Probabilistic program

**Reduction:** symbolic/program carrier + probabilistic belief/conditioning operators.

---

# 5. Symbolic/program reductions

## Expert/production rule system

**Reduction:** finite symbolic state + conditional rewrite/transition rules.

## Datalog / logic closure

**Reduction:** symbolic relation set + monotone/fixed-point rule application.

## SAT/CSP/SMT

**Reduction:** symbolic constraint carrier + propagation/search + verifier/admissibility semantics. Richer theories change primitive constraint solvers but not the fundamental carrier classification.

## Theorem prover

**Reduction:** symbolic state + proof-search frontier + exact proof verifier.

## Program synthesis

**Reduction:** symbolic program carrier + search/frontier + semantic verifier.

---

# 6. Search/planning reductions

## BFS / DFS / beam / best-first / branch-and-bound

All are frontier-state realizations differing in frontier order, bound/evaluation semantics and resource cap.

**Reduction:** search/frontier carrier + selection/evaluation policy.

## A*

**Reduction:** best-first frontier + registered lower-bound/heuristic state.

## Minimax / alpha-beta

**Reduction:** adversarial search frontier + alternating authority/value semantics; alpha-beta is bound-based pruning.

## MCTS

**Reduction:** stochastic frontier/tree + adaptive sampling/statistical value estimate.

## Dynamic programming

**Reduction:** search/computation + explicit reuse/cache of overlapping subproblem quotient states. It is the compile/cache phase of repeated subproblems.

## Classical planning / MPC

**Reduction:** transition/world model + search/optimization frontier; MPC adds repeated finite-horizon replanning.

---

# 7. Neural family reductions

## Perceptron

**Reduction:** coefficient state + threshold/link operator.

## MLP

**Reduction:** layered nonlinear coefficient/composition state. Parent depth-separation theorems show layered composition can have genuine representation-burden advantages; neural reachability remains separate.

## Residual network

**Reduction:** layered nonlinear coefficient state + explicit identity/residual composition operator. The residual Jacobian identity already formalizes one mechanism.

## CNN / equivariant network

**Reduction:** coefficient state + group/locality-induced parameter tying. Exact finite-group projection/symmetry-deviation laws already derive the sharing pressure.

## GNN/message passing

**Reduction:** distributed/local dynamical state + permutation-respecting shared local operators. Graph-cut communication laws derive depth/width/routing pressure.

## RNN

**Reduction:** nonlinear implementation of recurrent/predictive-state carrier.

## LSTM/GRU

**Reduction:** recurrent state + selective retain/overwrite gates. The historical gate parameterization is one realization of the derived selective-state property.

## Reservoir computing

**Reduction:** fixed recurrent/dynamical feature state + learned readout coefficient state. No independent domain.

## Linear/neural state-space model

**Reduction:** recurrent predictive state with structured transition; finite Hankel rank supplies the exact linear minimal state theorem.

## Selective SSM

**Reduction:** recurrent state + input-conditioned transition/update operator.

## Transformer

**Reduction:** coefficient/token transformations + content-dependent routing + positional distinction + residual composition. It is not a new computability domain; zero-prior challenge is predicting the dynamic-routing property and its lifecycle frontier.

## Sparse/local attention

**Reduction:** dynamic/fixed routing with a sparsity/locality constraint; exact dependency-union/edge-cost laws give the structural phase.

## MoE

**Reduction:** coefficient modules + conditional specialization/routing. Mode-rank law derives sharing pressure; full MoE selection additionally needs optimization/communication effects.

## Hypernetwork

**Reduction:** conditional program/coefficient map whose output is another module's parameters. It is a parameter-generating conditional realization, not a primitive carrier.

---

# 8. Adaptation/continual reductions

## Full fine-tuning

**Reduction:** global update of coefficient state.

## Low-rank adaptation

**Reduction:** coefficient update constrained to low-rank residual family. Exact finite-rank information laws provide the structural criterion.

## Adapter/local module

**Reduction:** parameter expansion/local block addition when desired correction lies outside the old retention-safe image. Continual-update theorems derive this pressure.

## Replay

**Reduction:** global/shared update while reintroducing old evidence so old constraints are jointly optimized.

## EWC/regularization-style retention

**Reduction:** shared update + penalty on old-sensitive directions; linearized `A_old` geometry is the base case.

## Progressive/expanding network

**Reduction:** morphogenesis/parameter expansion to create new retention-safe degrees of freedom.

## Meta-learning / fast adaptation

**Reduction:** persistent cross-task base state + low-burden task residual/update. EM-3 derives information saving from true task sharing.

## MAML-like method

**Reduction:** one particular differentiable realization of meta-state as an initialization/update geometry. Novelty is not at the carrier level.

## NAS

**Reduction:** morphogenesis/architecture variable + search/frontier over realizations.

---

# 9. Generative reductions

## Autoregressive model

**Reduction:** conditional sequence-law state from chain factorization.

## VAE-like latent model

**Reduction:** latent quotient + conditional generator + approximate probabilistic posterior/inference.

## Mixture model

**Reduction:** probabilistic belief with explicit component quotient.

## Normalizing flow

**Reduction:** coefficient/program state representing invertible transport; support-type no-go already registered.

## Score model / diffusion

**Reduction:** score-field coefficient state + dynamical/noising/sampling process. Diffusion is a particular development/serving realization of score-based density information.

## Flow matching

**Reduction:** time-indexed vector field/dynamical transport state.

## GAN

**Reduction:** generator coefficient/program state + learned discriminator measurement/verifier game. EG-3/EG-4 give idealized distribution-matching semantics.

## Energy-based model

**Reduction:** unnormalized probabilistic compatibility/energy state; normalization/sampling cost determines lifecycle niche.

## Masked/denoising generator

**Reduction:** family of conditional reconstruction laws indexed by observed/masked subset; fundamentally a conditional predictor trained under corruption distribution.

---

# 10. Control/RL reductions

## Bandit

**Reduction:** uncertain action-value belief + exploration/intervention choice. Exploration collision theorem proves informative action necessity.

## Value iteration / Q-learning-like state

**Reduction:** compiled value/action-value state for repeated Markov decision obligations; Bellman fixed-point structure supplies semantics.

## Policy gradient

**Reduction:** direct parameterized policy state + score-function stochastic development operator.

## Actor-critic

**Reduction:** direct policy + separate value/baseline state, justified when critic cost is repaid by variance/sample reduction.

## Model-free control

**Reduction:** compiled policy/value state.

## Model-based control/world-model agent

**Reduction:** reusable predictive dynamics state + search/planning.

## Dyna/hybrid

**Reduction:** reusable model + generated planning/training experience + compiled policy/value state. Lifecycle crossover selects proportions.

---

# 11. Tool/agent reductions

## Tool router

**Reduction:** typed conditional routing over external operators.

## Multi-step tool agent

**Reduction:** typed composition path + search/planning over tool graph.

## Generator+verifier

**Reduction:** proposal/search + exact or probabilistic admission/authority gate.

## Planner+executor

**Reduction:** search/planning state + compiled/typed action execution.

## Memory+model composites

**Reduction:** multiple sufficient-state factors joined by explicit composition/authority contracts. Developmental complementarity, not new domain status, is the key variable.

---

# 12. Collective/evolutionary reductions

## Distributed/federated inference or learning

**Reduction:** partitioned sufficient state + communication/aggregation/update operator. Communication lower bounds determine when distribution is unavoidable/expensive.

## Multi-agent/consensus/swarm

**Reduction:** distributed population state + communication/local dynamics. Domain-level novelty requires failure of matched distributed-program reduction; current finite classical forms do not pass that bar.

## Genetic algorithm / evolution strategy

**Reduction:** population state + stochastic variation + selection/search.

## QD/MAP-Elites-like archive

**Reduction:** population/search + explicit multi-niche archive/coverage objective. QD-1 derives retention value; descriptor collision theorem states validity requirement.

## Population-based training

**Reduction:** population search + within-individual developmental update.

---

# 13. Physical/unconventional reductions

## Spiking neural system

At finite precision/finite event description, this is neural coefficient state + event-driven dynamical execution. It may have substrate/energy/latency advantages but is not automatically a new computability/resource domain.

## HDC/VSA

Reduced by `GMI_CANDIDATE_DOMAIN_REDUCTION_THEOREMS_V2.md` to ordinary vector/array program asymptotically under matched primitives.

## Cellular automaton / neural cellular automaton

Reduced to distributed local program/dynamical kingdom under matched topology/communication.

## Physical reservoir

**Reduction at semantic level:** dynamical state + readout. Physical substrate can still shift energy/latency/precision frontier and must be metered end-to-end.

## Ising/annealing

**Reduction at semantic level:** energy landscape + relaxation/search. Local-minimum traps prove limits; physical parallelism/energy may change substrate frontier.

## Reaction network

**Reduction at semantic level:** dynamical/physical state with reaction operators. Distinct domain status requires end-to-end physical lifecycle separation from a matched simulator/alternative.

## Quantum computation

Not reduced here to ordinary classical H3/H4. It remains the calibration case for genuinely nonclassical state/evolution; useful intelligence advantage is task- and I/O-dependent and not implied by quantum syntax alone.

---

# 14. Consequence for the zero-prior programme

The target is **not** to reproduce every historical source-code pattern from first principles.

A known family passes structural zero-prior derivation if GMI predicts its implementation-invariant mechanism/property vector or proves it is a bounded composition/special case of already-derived vectors.

This sharply reduces the irreducible closure problem. Most historical families are combinations of a smaller set of atoms:

```text
coefficient/basis state
explicit exemplar/memory state
probabilistic belief
symbolic/program state
recurrent/dynamical state
search/frontier
routing/composition
verification/authority
population/distributed state
morphogenesis/development
```

plus measurable structural coordinates such as symmetry, rank, residual complexity, dependency geometry, uncertainty and reuse.

---

# 15. What still cannot be reduced away

The remaining blocking science is mainly quantitative:

```text
which hidden structural coordinates actually hold in a new ecology?
can the development process reach the efficient representation?
how well will it generalize?
what are the real lifecycle prices/crossovers?
can neutral search recover the predicted property without family macros?
```

Those are the K3-K6 gates; adding more family names does not close them.
