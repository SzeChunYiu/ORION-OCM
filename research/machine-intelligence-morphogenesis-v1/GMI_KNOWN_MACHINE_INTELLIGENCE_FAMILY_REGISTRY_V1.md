# GMI Known Machine-Intelligence Family Registry v1

Status: **REGISTERED ZERO-PRIOR CLOSURE SCOPE / LIVING BUT VERSIONED**

Status date: 2026-09-12.

Purpose:

> Freeze a broad set of historically known machine-intelligence families that GMI must be able to derive, reduce or explicitly classify before strong unknown-species discovery claims are credible.

This is not a claim that human knowledge is complete. It defines a registered closure scope that can be expanded by successor versions.

Derivation levels:

```text
K0 post-hoc home
K1 structural direction
K2 formal property derivation
K3 quantitative response law in at least a registered base regime
K4 neutral rediscovery
K5 held-family prediction
K6 real-regime replication
```

---

# 1. Coefficient/statistical function families

| Family | Zero-prior derivation basis | Current level |
|---|---|---:|
| linear regression / least squares | low-dimensional stable linear sufficient law; finite sufficient statistics | K2/K3 base |
| ridge / regularized linear model | coefficient law + priced norm/variance control | K1/K2 parent |
| logistic regression / GLM | low-dimensional sufficient predictors + exponential-family/link semantics | K1/K2 parent |
| linear discriminant family | class-conditional low-order sufficient statistics | K1/K2 parent |
| polynomial/basis regression | reusable finite basis expansion cheaper than exemplar table | K2 base |
| spline/local basis model | local smoothness + piecewise basis sharing | K1 |
| kernel regression / SVM-like kernel machine | reusable similarity geometry + representer/basis expansion | K1/K2 parent |
| Gaussian process | function uncertainty + kernel covariance prior + posterior update | K1/K2 parent |
| PCA / low-rank factor model | covariance energy concentrated in low-dimensional subspace | K1/K2 parent |
| matrix factorization | low-rank relational residual/state | K2/K3 finite-rank base |
| ICA / source-separation family | independent latent component structure | K1 |

Primary gaps: model/basis/kernel geometry selection, noisy approximate effective dimension, real lifecycle crossover.

---

# 2. Exemplar, memory and density families

| Family | Derivation basis | Level |
|---|---|---:|
| exact key-value table | arbitrary independent distinctions; exact local updates | K2/K3 |
| k-nearest-neighbor / case memory | metric locality + cheap writes + weak global compression | K1/K2 |
| prototype / nearest-centroid | cluster compression of exemplar distinctions | K1 |
| kernel density estimate | local smooth density from stored samples | K1 |
| associative/content-addressable memory | retrieval by distributed similarity cue | K1/K2 parent |
| external factual/retrieval memory | stable core + volatile/provenance residual | K2/K3 |
| RAG-like predictor+memory | predictive quotient + residual retrieval/authority | K2/K3 |

Primary gaps: metric/locality estimator, retrieval noise/cost, provenance value, protected residual prediction.

---

# 3. Partition and ensemble families

| Family | Derivation basis | Level |
|---|---|---:|
| decision tree | sparse recursive partition rules / discontinuous conditional structure | K2 |
| random forest / bagged trees | error diversity + variance reduction under aggregation | K1/K2 |
| gradient boosting | accessible additive residual correction | K2 |
| generic ensemble / voting | correlation-dependent error/variance reduction | K2/K3 base |
| stacking / learned aggregation | heterogeneous predictors + learnable combination | K1 |

Primary gaps: split discovery, weak-learner accessibility, pre-outcome error-correlation/diversity estimator.

---

# 4. Probabilistic belief and latent-state families

| Family | Derivation basis | Level |
|---|---|---:|
| Naive Bayes | explicit uncertainty + conditional independence factorization | K1/K2 parent |
| Bayesian network | sparse conditional independence + evidence updates | K1/K2 parent |
| Markov random/factor graph | local probabilistic factors + message/inference structure | K1/K2 parent |
| HMM | hidden Markov predictive state + belief update | K2 parent |
| Kalman filter / linear Gaussian state estimator | finite-dimensional Gaussian belief closure | K2/K3 parent |
| particle filter | belief state not closed in finite parametric family; sample approximation | K1 |
| Bayesian nonparametric/process family | uncertainty over flexible/infinite-dimensional function state | K1 |
| probabilistic program | symbolic program + explicit stochastic belief semantics | K1/K2 parent |

Primary gaps: zero-prior structure discovery, approximation-family selection, inference-cost prediction.

---

# 5. Symbolic, constraint and program families

| Family | Derivation basis | Level |
|---|---|---:|
| production/expert rules | compact exact reusable discrete laws | K1/K2 |
| finite-state automaton | future-response quotient | K2/K3 |
| logic/Datalog-like system | compositional exact relations + closure | K1/K2 parent |
| SAT/CSP | exact discrete compatibility constraints | K1/K2 parent |
| SMT/constraint programming | typed exact constraints over richer theories | K1/K2 parent |
| theorem prover / proof checker | exact derivation + verifier semantics | K1/K2 |
| program synthesis | target behavior + search over compositional programs | K1/K2 |
| weighted automaton / linear predictive state | finite Hankel rank | K2/K3 parent |

Primary gaps: rule/program compressibility estimator, synthesis/search accessibility, real verification costs.

---

# 6. Search and planning families

| Family | Derivation basis | Level |
|---|---|---:|
| exhaustive/enumerative search | query-specific solution not worth precompiling | K2 |
| breadth/depth search | frontier organization under graph/tree topology | K1/K2 |
| A*/best-first | admissible/informative heuristic reduces frontier burden | K1/K2 |
| beam search | bounded frontier approximation under serving constraint | K1 |
| branch-and-bound | exact bound permits subtree elimination | K1/K2 |
| minimax/alpha-beta | adversarial game tree + value bounds | K1/K2 parent |
| MCTS | stochastic/adaptive allocation of tree evaluations | K1/K2 |
| dynamic programming | overlapping subproblems + reusable value state | K1/K2 parent |
| classical planner | symbolic action/state transition + search | K1/K2 |
| MPC/trajectory optimization | short-horizon dynamics + receding replanning | K1/K2 |
| verifier-gated proposal search | proposal diversity + sound admission + high false-adoption loss | K2/K3 |

Primary gaps: heuristic/proposal information value, correlation, approximate bound quality, learned search allocation.

---

# 7. Neural coefficient families

| Family | Derivation basis | Level |
|---|---|---:|
| perceptron/linear neural unit | coefficient map + threshold/nonlinearity | K1/K2 |
| MLP | reusable nonlinear compositional map | K1/K2 representation; reachability open |
| residual MLP/network | identity-preserving compositional update / gradient pathway | K1/K2 mechanism |
| CNN | translation/local symmetry -> shared local operators | K2/K3 linear symmetry base |
| equivariant neural family | registered group symmetry -> group-shared operator space | K2/K3 linear base |
| GNN/message passing | graph locality + permutation-respecting shared aggregation | K2/K3 communication base |
| RNN | compact future-relevant recurrent state | K2 |
| LSTM/GRU-like gated recurrence | selective retention/overwrite under varying relevance | K2 |
| reservoir computing | fixed nonlinear dynamical basis + learned readout | K1/K2 parent |
| neural state-space model | compact recursively updated predictive state | K2 parent |
| selective SSM | input-dependent state update/selectivity | K1/K2 |
| Transformer | variable content-dependent dependency graph + parallel shared transforms | K2/K3 routing base |
| local/sparse attention | sparse dependency geometry + routing burden | K2/K3 |
| Mixture of Experts | high mode heterogeneity + conditional computation + cheap routing | K2/K3 linear mode base |
| hypernetwork | parameter-generating map reused across tasks/conditions | K1 |

Primary gaps: nonlinear reachability, overparameterized generalization, effective dependency geometry, mode interference/router law.

---

# 8. Neural adaptation / continual-development families

| Family | Derivation basis | Level |
|---|---|---:|
| full fine-tuning | broad residual/update not cheaply localized | K1/K2 |
| low-rank adaptation | low effective residual rank | K2/K3 finite-rank base |
| adapters/local modules | retention-safe local/new degrees of freedom | K2/K3 linearized base |
| replay | shared update conflicts with retention; old data revisited | K1/K2 |
| regularization/EWC-like | penalize motion in old-sensitive directions | K1/K2 |
| parameter expansion | no exact correction in old-task safe subspace | K2/K3 linearized |
| external-memory update | volatile local distinctions cheaper outside parameters | K2/K3 |
| continual architecture growth/pruning | persistent regime shift + morphology-switch amortization | K1/K2 |
| meta-learning / fast adaptation | repeated related tasks justify learning an update prior | K1 |
| MAML-like gradient meta-learning | reusable initialization/update geometry | K1 |
| NAS/architecture search | morphology itself is search variable | K1/K2 |

Primary gaps: nonlinear safe-update geometry, task-family transfer law, meta-development burden.

---

# 9. Generative families

| Family | Derivation basis | Level |
|---|---|---:|
| autoregressive model | chain-rule conditionals over ordered variables | K2/K3 structural |
| latent-variable / VAE-like | low-dimensional/discrete latent quotient + conditional generator | K1/K2 |
| mixture model | multimodal component quotient | K2 base |
| normalizing flow | invertible transport + tractable change of variables | K2 structural |
| score model | smooth positive density determined by score field | K2 structural |
| diffusion model | score/noising representation + iterative reverse dynamics | K1/K2 structural |
| flow matching / continuous transport | learned velocity field transports base to target | K1/K2 parent |
| GAN/adversarial generator | sample generator selected by discriminator divergence game | K1 |
| energy-based generative model | density/compatibility represented by energy up to normalization | K1/K2 parent |
| masked/denoising generator | conditional reconstruction from corrupted partial state | K1 |

Primary gap: prospective complexity/learnability/lifecycle selector among exact/approximate factorizations.

---

# 10. Control and reinforcement-learning families

| Family | Derivation basis | Level |
|---|---|---:|
| multi-armed bandit | action-value uncertainty + exploration/exploitation | K1/K2 parent |
| tabular value iteration | Markov state + Bellman fixed point | K1/K2 parent |
| Q-learning | model-free Bellman target + repeated transitions | K1/K2 parent |
| policy gradient | differentiable policy objective + sampled return signal | K1 |
| actor-critic | separate policy + value/control variate state | K1 |
| model-free policy/value | high reuse favors compiled action/value map | K2/K3 lifecycle base |
| model-based RL | reusable dynamics + counterfactual planning | K2/K3 lifecycle base |
| world-model agent | compressed predictive dynamics + planner/policy | K1/K2 |
| Dyna/hybrid | model-generated planning/training plus compiled policy | K2 lifecycle prediction |
| MPC | model + repeated finite-horizon online optimization | K1/K2 |

Primary gaps: exploration value, model bias, partial observability, learned model/policy development costs.

---

# 11. Tool, retrieval, verifier and agent composition families

| Family | Derivation basis | Level |
|---|---|---:|
| typed tool router | obligation-specific legal cost minimization | K2/K3 |
| multi-step tool composition | no direct semantic edge; shortest legal typed path | K2/K3 |
| calculator/code/proof tool augmentation | narrow exact component lowers composite critical burden | K2 |
| retrieval-augmented agent | volatile/provenance residual + retrieval | K2/K3 |
| generator + verifier | cheap fallible proposal + costly false adoption + sound checker | K2/K3 |
| planner + executor | query-specific decomposition/control | K1/K2 |
| memory + planner + model composites | complementary sufficient-state factors | K1/K2 |

Primary gaps: semantic type discovery, uncertain tool effects, correlated failures, multi-step error propagation.

---

# 12. Collective and distributed families

| Family | Derivation basis | Level |
|---|---|---:|
| distributed inference | partitioned information + communication reconstruction | K1/K2 |
| federated learning | distributed private data + aggregate update | K1 |
| multi-agent coordination | no single node contains sufficient state | K1/K2 |
| consensus/voting | redundant/distributed estimates + aggregation | K1/K2 |
| market/auction allocation | distributed private utilities/resources + price mechanism | K1 |
| swarm/local collective | local rules + population-level outcome | K1/K2 |

Primary gaps: communication sufficiency, strategic incentives, distributed learning/credit assignment.

---

# 13. Evolutionary/open-ended families

| Family | Derivation basis | Level |
|---|---|---:|
| genetic algorithm | variation + selection over explicit population | K1/K2 |
| evolution strategies | stochastic parameter search + fitness signal | K1 |
| quality-diversity archive | multiple niches/descriptor diversity is part of objective | K1/K2 |
| open-ended coevolution | evolving agents and/or ecologies alter search distribution | K1 |
| population-based training | population search plus within-life learning | K1 |

Primary gaps: search/operator selection law, diversity-value prediction, open-ended stability.

---

# 14. Physical/unconventional computation families

| Family | Derivation basis | Level |
|---|---|---:|
| spiking/event neural system | neural coefficients + event/dynamical execution | K1/K2; likely kingdom |
| hyperdimensional/vector-symbolic | high-dimensional algebra + superposition/noise law | K2; reduced asymptotically to array program |
| cellular/neural cellular automaton | local dynamical field + shared rule | K2; distributed-program reduction |
| physical reservoir | physical dynamics as fixed feature/state evolution | K1/K2; substrate-sensitive |
| Ising/annealing/energy relaxation | energy landscape + relaxation/search | K2; local-minimum ceiling known |
| analog/photonic compute | physical field transforms with energy/latency/precision trade | K1; substrate-sensitive |
| molecular/reaction-network compute | reaction kinetics as state/update | K1; strong dynamical parent |
| quantum computation/quantum ML | nonclassical state/evolution/measurement | K1/K2 calibration; complexity advantage task-dependent |

Primary gaps: end-to-end I/O, precision, energy, error correction and matched classical parent accounting.

---

# 15. Registry-wide closure rule

For each registered family, GMI must eventually provide:

```text
semantic sufficient-state derivation
information/state lower bound
constructive realization upper bound
natural complexity coordinate
lifecycle response law
negative twin
strongest alternative/parent comparison
pre-outcome measurable descriptors
neutral rediscovery
held-family prediction
```

A family may be reduced to another family/kingdom rather than independently derived if a bounded semantics-preserving reduction is proved.

---

# 16. Current registry verdict

Broad structural homes exist for essentially all entries above, but **zero-prior derivation closure does not**.

The major common blockers are:

```text
nonlinear optimization reachability
generalization/transfer prediction
real effective complexity estimation
search/router/tool learnability
partial-observability predictive state
exploration/model bias
generative factorization selection
continual/meta-development transfer
physical end-to-end lifecycle accounting
neutral rediscovery at broad grammar scale
```

The registry therefore prevents an early `all known species derived` claim.

Desired registered terminal:

`KNOWN_FAMILY_REGISTRY_ZERO_PRIOR_GREEN_V1`

only after every row is derived/reduced and required K4/K5 tests are green.
