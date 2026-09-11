# GMI Machine-Learning Phenomena Atlas v1

Status: **EXPLANATORY-CLOSURE MAP / RESEARCH PROGRAMME — NOT A CLAIM THAT ALL ML IS SOLVED**

Status date: 2026-09-12.

Refs:

- `GMI_THEORY_V1.md`
- `GMI_CROSS_PARADIGM_REALIZATION_NORMAL_FORM_V1.md`
- `GMI_SEMANTIC_QUOTIENT_REALIZATION_THEOREM_V1.md`
- `GMI_CAUSAL_MECHANISM_PHASE_THEORY_V1.md`
- `GMI_NEURAL_MACHINE_INTELLIGENCE_DERIVATION_V1.md`
- `GMI_NEURAL_PREDICTION_TO_INTELLIGENCE_THEOREMS_V1.md`
- `GMI_NEURAL_EFFECTIVENESS_REGIME_V1.md`
- `GMI_PREDICTIVE_RESIDUAL_QUOTIENT_THEORY_V1.md`

Purpose:

> Push GMI toward explanatory coverage of machine learning as a whole while refusing the vacuous claim that a broad notation is itself an explanation.

Every ML phenomenon should have a typed home, a causal/mechanistic hypothesis, an evidence status and a falsifying experiment.

---

# 1. Explanatory closure contract

At the registered scope, every learning system is described by:

\[
(\mathcal O,D,J,P,M,H_{dev})
\]

with realization

\[
M=(F,\Theta,K,U,\Gamma,\kappa,\rho_M).
\]

Here:

```text
O       external cognitive/semantic obligation
D       development protocol / supplied information / initialization
J       interventions, probes and teaching class
P       hardware, prices, budgets and other exogenous realization context
F       factorization/topology/architecture
Theta   mutable state/parameters/memory/beliefs
K       execution/inference/proposal kernel
U       within-form update law
Gamma   morphology/structure-changing law
kappa   semantic interpretation/compiler relation
rho_M   resource semantics
```

An observed ML phenomenon must be classified as at least one of:

```text
S  semantic/obligation structure
R  representational/realization structure
O  optimization/development response
G  generalization/statistical response
M  memory/retention/history response
I  inference/search/test-time response
X  morphogenesis/architecture-selection response
P  physical/resource/context response
V  verification/authority response
```

This typing is **coverage**, not explanation.

A GMI explanation is accepted only if it also provides:

1. a pre-outcome variable or mechanism;
2. a directional prediction under intervention;
3. a matched negative twin or collision;
4. a burden/resource accounting rule;
5. a falsifier;
6. a claim status.

---

# 2. Status vocabulary

Use exactly these levels in the atlas.

```text
FORMAL-GMI       proved in the current finite/exact GMI scope
PARENT-THEOREM   rigorous parent mathematics imported under named assumptions
EMPIRICAL-LAW    repeatable empirical phenomenon; GMI supplies a causal placement/prediction
PROGRAMME        prospective explanation with a frozen experiment, not yet established
OPEN             no adequate predictive explanation yet
```

A phenomenon can have multiple statuses at different levels. For example, gradient descent has rigorous convergence/implicit-bias theorems in restricted settings while practical deep-network optimization remains partly empirical.

---

# 3. Representation and capacity

| Phenomenon | GMI placement | Explanatory statement | Status | Primary falsifier |
|---|---|---|---|---|
| universal approximation | `F,Theta,K` capacity | neural family can approximate broad maps; capacity alone does not imply learnability/generalization | PARENT-THEOREM | adequate target map outside stated approximation assumptions |
| depth separation | factorization `F` | compositional target structure can make deep realization exponentially/strongly more efficient than shallow realization | PARENT-THEOREM + PROGRAMME | depth advantage persists after compositionality is destroyed and resource matching is exact |
| representation learning | `kappa`, internal coordinates | development can choose realization coordinates that preserve target distinctions while compressing nuisance variation | EMPIRICAL-LAW / PROGRAMME | learned coordinates fail invariant/remint tests while claimed advantage persists |
| embeddings | `Theta,kappa` | continuous codes are implementation states whose utility comes from preserving task-relevant quotient neighborhoods/relations | EMPIRICAL-LAW | geometry has no predictive relation to transfer/retrieval under matched controls |
| feature learning | evolution of `kappa/F/Theta` | finite networks can change effective representation during training rather than remain at a fixed kernel | EMPIRICAL-LAW | feature movement does not predict gains outside lazy/kernel controls |
| kernel/lazy regime | fixed effective `kappa` / update geometry | sufficiently wide/small-movement networks can behave like kernel learning under stated limits | PARENT-THEOREM | claimed NTK-limit setting exhibits incompatible function dynamics |
| equivariance | constrained `F,K` | known transformation symmetries reduce redundant distinctions and sample burden | PARENT-THEOREM + EMPIRICAL-LAW | symmetry-matched architecture gives no advantage when symmetry is real, after capacity matching |
| invariance | `kappa` quotient compression | nuisance transformations should be merged only when obligation is invariant to them | FORMAL-GMI principle | merging changes protected future consequence |
| convolution | shared local factorization | translation/locality priors reduce description/sample burden when ecology has corresponding locality/symmetry | EMPIRICAL-LAW | advantage survives randomized spatial structure with matched compute |
| graph neural networks | relational factorization | permutation/edge-local computation is favored when obligations respect graph structure | EMPIRICAL-LAW | graph prior remains advantageous after relational structure is reminted away |
| recurrent/state-space models | stateful `K,Theta` | sequential sufficient state can compress history when future depends on bounded/structured latent state | PARENT-THEOREM + EMPIRICAL-LAW | no relation between temporal-state demand and recurrent/state-space advantage |
| attention | dynamic routing in `K` | content-dependent composition is favored when relevant dependency graph varies by input | EMPIRICAL-LAW / PROGRAMME | fixed-routing model matches burden/frontier after dependency variability intervention |
| sparse attention | sparse routing/resource response | sparse dependency geometry can reduce long-context cost if omitted edges are semantically unnecessary | EMPIRICAL-LAW | sparsification cost does not track true dependency density |
| mixture of experts | A7 heterogeneity / conditional routing | multimodal demand can favor conditional activation of parameter subsets, trading routing/communication for specialization | EMPIRICAL-LAW | expert specialization fails to track demand modes under matched parameter/FLOP controls |
| modular networks | A1/A6 factorization | separable query/update dependency can favor module boundaries | PROGRAMME | local/global dependency interventions do not change modular advantage |
| external memory | `Theta` separated by timescale/authority | high-volume or rapidly changing target distinctions can be cheaper in mutable memory than weights | EMPIRICAL-LAW / PRQ PROGRAMME | changing residual burden does not alter memory-vs-parametric frontier |

---

# 4. Optimization and credit assignment

| Phenomenon | GMI placement | Explanatory statement | Status | Primary falsifier |
|---|---|---|---|---|
| backpropagation | update law `U` | reverse-mode differentiation supplies parameter-wide local derivatives at cost comparable in order to graph execution, creating cheap dense credit when objective is differentiable | PARENT-THEOREM | gradient-access price changes but neural frontier position does not respond where gradient credit is claimed causal |
| SGD | stochastic `U` | noisy mini-batch estimates trade update cost for variance and can impose optimizer-dependent selection bias | PARENT-THEOREM + EMPIRICAL-LAW | noise intervention has no predicted effect after update budget matching |
| Adam/adaptive methods | preconditioned `U` | coordinate-wise adaptation changes update geometry and hence reachable solutions per unit burden | PARENT-THEOREM + EMPIRICAL-LAW | benefits survive reminting that removes anisotropic geometry under matched tuning |
| initialization | initial `Z_0` in `D` | starting state changes accessible basin, symmetry breaking, signal propagation and implicit prior | EMPIRICAL-LAW | matched initial function/state changes produce no development response difference where theory predicts it |
| normalization | `F/K/U` conditioning | normalization changes forward and gradient geometry, often increasing stable learning range | EMPIRICAL-LAW | conditioning measures do not mediate training stability under interventions |
| residual connections | execution/update geometry | identity-like paths reduce destructive transformation burden and improve gradient/signal transport in deep compositions | EMPIRICAL-LAW | depth-dependent optimization benefit remains when skip path is functionally but not geometrically reproduced |
| learning-rate schedules | time-dependent `U` | step scale controls exploration/convergence and implicit selection under finite horizon | PARENT-THEOREM + EMPIRICAL-LAW | endpoint/frontier invariant to schedule under regimes claimed schedule-sensitive |
| batch size | `U` noise/resource tradeoff | changes gradient noise, parallel efficiency and number of updates per data/compute budget | EMPIRICAL-LAW | no frontier shift after price/noise decomposition |
| overparameterization | `F,Theta` development geometry | redundant degrees may make low-loss solutions easier to reach even though representational minimum is smaller | PARENT-THEOREM in restricted regimes + EMPIRICAL-LAW | optimization benefit fails to change when redundancy is altered at fixed represented function class |
| implicit bias | trajectory-dependent `U` | optimizer selects among many interpolating solutions; training objective alone does not determine realized predictor | PARENT-THEOREM in restricted regimes + EMPIRICAL-LAW | same loss/data/update rule yields no systematic solution preference |
| lottery-ticket/pruning phenomena | redundant realization | large systems may contain or develop sparse subrealizations; finding them is a search/morphogenesis cost | EMPIRICAL-LAW | sparse subnetwork advantage survives when search cost is fully charged and no redundancy mechanism remains |
| curriculum learning | time ordering in `D/U` | path-dependent development means evidence order can change attainable state and burden | EMPIRICAL-LAW | history-order twins have identical response in claimed path-dependent regime |
| optimization plateaus | `U` geometry | local curvature/symmetry/credit weakness can make progress per resource small | EMPIRICAL-LAW | measured development geometry does not correlate with plateau under intervention |
| sharp/flat minima | local response descriptor | geometry may correlate with perturbation robustness/generalization but is parameterization-sensitive | PROGRAMME/OPEN | claim fails reparameterization-invariance tests |

---

# 5. Generalization, interpolation and statistical behavior

| Phenomenon | GMI placement | Explanatory statement | Status | Primary falsifier |
|---|---|---|---|---|
| classical bias-variance tradeoff | finite statistical response | candidate restriction vs estimation variance under data/noise assumptions | PARENT-THEOREM | outside parent assumptions only, no universal claim |
| interpolation | development endpoint | zero training error is compatible with different protected-risk outcomes because solution selection and target structure matter | EMPIRICAL-LAW | none; generalization claim must specify selector/data regime |
| benign overfitting | `U` implicit selection + data geometry | interpolating solutions can generalize when fitted nuisance directions carry controlled test burden | PARENT-THEOREM in model classes + EMPIRICAL-LAW | matched spectral/noise interventions violate predicted risk direction |
| double descent | capacity/development/statistics interaction | risk can peak near interpolation threshold and improve again as realization redundancy changes solution geometry | EMPIRICAL-LAW + parent models | no peak/shift response when interpolation threshold is moved independently |
| grokking | finite-horizon trajectory | memorizing solution can precede later lower-complexity/generalizing realization under continued optimization/regularization | EMPIRICAL-LAW / PROGRAMME | late transition does not move with data size, regularization or complexity competition as predicted |
| explicit regularization | objective/update constraint | price on norms/complexity/dropout/etc. changes selected realization and protected risk | PARENT-THEOREM + EMPIRICAL-LAW | regularizer has benefit without altering any measured selector/robustness variable |
| data augmentation | development protocol `D` | injects known invariances/equivariances, reducing sample burden if transformations preserve obligation semantics | PARENT-THEOREM principle + EMPIRICAL-LAW | augmentation remains beneficial when transformation violates target semantics |
| early stopping | stopping rule in `D` | limits movement/fit and acts as trajectory-dependent regularization under finite data/noise | PARENT-THEOREM in models + EMPIRICAL-LAW | stopping has no selector effect where claimed |
| ensembles | portfolio realization | multiple partially independent errors can reduce predictive risk at extra serve/memory cost | PARENT-THEOREM + EMPIRICAL-LAW | gains persist with perfectly correlated errors under equal aggregation |
| calibration | `kappa` from scores to probabilities/evidence | predictive ranking and calibrated uncertainty are distinct obligations | EMPIRICAL-LAW | calibration intervention changes neither decision/evidence behavior nor protected loss |
| uncertainty estimation | response distribution | protected decisions can require uncertainty distinctions beyond point prediction | PROGRAMME | uncertainty state adds no value when abstention/exploration obligation is varied |
| distribution shift | mismatch `E_train != E_protected` | generalization depends on invariances/mechanisms shared across environments, not IID fit alone | PARENT-THEOREM + EMPIRICAL-LAW | invariant mechanism predictors fail held-environment tests systematically vs spurious predictors |
| OOD detection | obligation-specific quotient | detecting “outside support/domain” is an additional semantic obligation, not implied by accuracy | EMPIRICAL-LAW | target OOD classes factor through ordinary predictive state yet extra state remains necessary |
| adversarial examples | local robustness obligation | high standard accuracy does not imply invariance to registered perturbation class | PARENT-THEOREM/EMPIRICAL | robust risk fails to respond to adversarially relevant geometry under exact controls |

---

# 6. Self-supervision, transfer and foundation models

| Phenomenon | GMI placement | Explanatory statement | Status | Primary falsifier |
|---|---|---|---|---|
| next-token prediction | predictive quotient learning | exact continuation prediction preserves every distinction that changes future sequence law | FORMAL-GMI + parent probability | two histories with different continuation laws map to same exact predictor state |
| masked prediction | partial-observation predictive state | learning hidden parts pressures representation to preserve structure useful for reconstructing them | EMPIRICAL-LAW | transfer unrelated to target/predictive quotient overlap |
| contrastive learning | representation objective | positive/negative construction defines which distinctions are preserved/merged | PARENT-THEOREM in restricted setups + EMPIRICAL | changing augmentation equivalence has no effect on learned transfer structure |
| multimodal pretraining | side-information/anchor enrichment | additional modalities can break observational aliases and align latent distinctions | EMPIRICAL-LAW / PROGRAMME | alias-breaking intervention adds no target information/transfer benefit |
| transfer learning | reuse horizon | pretrained state is developmental capital; advantage depends on quotient overlap and acquisition/reuse economics | FORMAL-GMI zero-residual criterion + EMPIRICAL | transfer does not track overlap after size/data controls |
| fine-tuning | target-conditioned `U` | modifies reusable state toward target quotient at risk of interference | EMPIRICAL-LAW | update locality/retention interventions do not affect tradeoff |
| parameter-efficient tuning | localized `U` | low-dimensional target residual may be encoded with fewer changed degrees than full retraining | PRQ PROGRAMME | required update rank/size does not grow with controlled residual complexity |
| adapters/LoRA | factorized residual update | freeze broad substrate while learning target-specific residual transformation | EMPIRICAL-LAW / PRQ PROGRAMME | residual complexity intervention does not change adapter sufficiency |
| instruction tuning | development protocol | supervised instruction distribution modifies mapping from latent capability to requested action/format | EMPIRICAL-LAW | capability/evaluation behavior not separable from underlying knowledge under probes |
| preference optimization / RLHF / DPO-like methods | external preference feedback in `D,U` | changes policy selection under human/model preference signal; does not by itself establish truth/verification | EMPIRICAL-LAW | preference improvement automatically implies external factual admissibility without verifier channel |
| catastrophic forgetting during fine-tuning | stability/plasticity response | shared mutable state causes new updates to alter old protected competence | EMPIRICAL-LAW | forgetting fails to track overlap/update geometry/retention mechanisms |

---

# 7. In-context learning and fast adaptation

| Phenomenon | GMI placement | Explanatory statement | Status | Primary falsifier |
|---|---|---|---|---|
| in-context learning | fast state in `K/Z`, no persistent `Theta` update required | execution can construct a task-conditioned predictor/algorithm in activations | PARENT construction + EMPIRICAL-LAW | activation-state probes show no task-dependent computation beyond retrieval in claimed algorithmic regime |
| induction heads / pattern copying | specialized dynamic routing | repeated token/pattern structure can induce reusable copying/search circuits | EMPIRICAL-LAW | targeted circuit ablation has no causal effect in registered setting |
| meta-learning | developmental law over task family | slower training shapes a fast adaptation procedure for new tasks | PARENT-THEOREM in models + EMPIRICAL | fast-adaptation advantage survives task-family remint with no shared structure |
| MAML-like adaptation | learned initialization/update geometry | `D/U` chosen to minimize post-update target burden | EMPIRICAL-LAW | adaptation gradient horizon not causally related to benefit |
| prompt learning | external fast control state | prompt supplies legal context that selects/constructs behavior without changing persistent parameters | EMPIRICAL-LAW | behavior unaffected by prompt information under matched token budget |
| test-time training | online `U` during inference | protected distribution signal can justify temporary state change when adaptation gain exceeds update/interference cost | PROGRAMME | no regime boundary with shift strength/reuse/retention |

---

# 8. Retrieval, memory, provenance and editing

| Phenomenon | GMI placement | Explanatory statement | Status | Primary falsifier |
|---|---|---|---|---|
| retrieval-augmented generation | predictive core + external residual memory | mutable/provenance-sensitive facts can be cheaper and more identifiable outside parametric weights | EMPIRICAL-LAW + PRQ PROGRAMME | retrieval advantage does not scale with residual freshness/provenance demand |
| kNN/memory-based learning | direct episode state | low compilation burden but potentially high query/storage burden; favored under short reuse or highly local novelty | PARENT/EMPIRICAL | frontier fails to move with reuse/query-volume intervention |
| episodic memory | retained history state | needed when future obligation distinguishes histories not compressed by current predictive state | FORMAL-GMI principle | legal histories with different future consequences safely merge |
| semantic memory | compressed quotient-like state | repeated experience can be compiled into reusable sufficient distinctions | PROGRAMME | compression fails to preserve registered consequences |
| model editing | local update | desired when small semantic residual changes without broad retraining; collateral damage measures dependency geometry | EMPIRICAL-LAW / PROGRAMME | edit locality unrelated to measured dependency cones |
| machine unlearning | developmental/history obligation | exact removal may require dependency/lineage information; indistinguishable-from-retrain criteria define semantic target | PARENT + PROGRAMME | claimed unlearning succeeds without retaining/deriving any required dependency distinction under exact hostile |
| provenance | authority residual | content-equivalent states may differ legally by source/evidence; prediction alone need not preserve this | FORMAL-GMI PRQ hostile | provenance obligations factor through predictive quotient but residual remains required |
| historical/as-of queries | lineage residual/A5 | old versions are required only if future obligation queries them | FORMAL-GMI | drift alone predicts persistence after lineage demand removed |

---

# 9. Continual learning and plasticity

| Phenomenon | GMI placement | Explanatory statement | Status | Primary falsifier |
|---|---|---|---|---|
| catastrophic forgetting | shared mutable realization | updates for new competence overwrite distinctions needed by old obligations | EMPIRICAL-LAW | forgetting independent of overlap/update geometry under interventions |
| loss of plasticity | history-conditioned response `R_M` | prior optimization can reduce future learning response even with current performance fixed | EMPIRICAL-LAW | history twins with same present behavior have identical future acquisition across regimes |
| replay | retained training evidence | reintroduces gradients/information for protected old distinctions at memory/compute cost | EMPIRICAL-LAW | benefit unrelated to protected-retention demand |
| EWC/parameter protection | update constraint | penalizes movement along directions estimated important to old competence | EMPIRICAL-LAW | importance alignment does not predict retention |
| dynamic expansion | `Gamma` | adding factors can reduce interference when existing state cannot absorb new distinctions cheaply | PROGRAMME | expansion advantage fails to track interference/residual complexity |
| consolidation | timescale separation | frequently reused stable distinctions migrate toward cheap serving state while volatile details remain mutable | PROGRAMME | volatility/reuse interventions do not change preferred storage timescale |
| continual pretraining | repeated broad `U` | updates predictive substrate as ecology drifts; should be separated from residual/authority updates | EMPIRICAL-LAW | broad retraining remains optimal when change is provably sparse residual-only and costs are charged |

---

# 10. Generative modeling

| Phenomenon | GMI placement | Explanatory statement | Status | Primary falsifier |
|---|---|---|---|---|
| autoregressive generation | sequential predictive `K` | factorizes joint distribution into conditional continuation predictions | PARENT-THEOREM | probability chain factorization violated |
| diffusion / score models | generative `K,U` via denoising/score field | learn reverse/noise-conditioned dynamics; alternative factorization of distribution modeling burden | PARENT-THEOREM + EMPIRICAL | claimed score/reverse process fails its registered distributional objective |
| variational autoencoders | latent `kappa` + variational inference | trade reconstruction against regularized latent coding under model assumptions | PARENT-THEOREM | ELBO/latent interpretation outside assumptions |
| GANs | adversarial development game | generator improves using learned discriminator feedback rather than explicit likelihood | PARENT-THEOREM + EMPIRICAL | discriminator feedback carries no information about generator error in claimed regime |
| normalizing flows | invertible realization | exact likelihood via invertible map trades architectural constraints for tractable density | PARENT-THEOREM | invertibility/Jacobian contract violated |
| mode collapse | development/game failure | objective/optimization can map many target modes to fewer generated modes despite local training progress | EMPIRICAL-LAW | collapse unrelated to game/coverage feedback under interventions |

---

# 11. Reinforcement learning, planning and agency

| Phenomenon | GMI placement | Explanatory statement | Status | Primary falsifier |
|---|---|---|---|---|
| value learning | predictive/control sufficient state | compress future reward/control consequences under policy/environment assumptions | PARENT-THEOREM | state merges situations with distinct protected control consequences |
| policy gradients | stochastic credit `U` | estimate effect of actions/parameters on expected return, usually high variance | PARENT-THEOREM | estimator not unbiased/consistent under stated assumptions |
| model-based RL | learned transition/predictive state + search | pays model cost to reuse imagined rollouts/planning | PARENT/EMPIRICAL | advantage does not track planning reuse/model accuracy |
| model-free RL | compiled policy/value | trades model flexibility/explanation for direct execution efficiency | PARENT/EMPIRICAL | no reuse/serving advantage where model construction is charged |
| exploration | information-acquisition action | action has epistemic value when reducing uncertainty can improve future protected decisions | PARENT-THEOREM | information-gain intervention has no future-decision value under exact setup |
| world models | predictive developmental state | compact state supports counterfactual planning only to extent learned dynamics preserve intervention-relevant distinctions | EMPIRICAL-LAW / PRQ | observationally equivalent worlds with different actions are not separated but planning remains exact |
| planning/search | test-time `K` burden | trades inference compute for reduced compiled knowledge/model size or improved solution quality | PARENT/EMPIRICAL | capability does not vary with search budget where search is claimed causal |
| verification-guided search | `K` + external `V` | cheap candidate generation can be paired with stronger verifier when false candidates are rejectable | PROGRAMME | verifier strength/cost does not shift generator-search frontier |

---

# 12. Compression and serving

| Phenomenon | GMI placement | Explanatory statement | Status | Primary falsifier |
|---|---|---|---|---|
| knowledge distillation | compiler from rich teacher state to smaller serving state | serving can discard distinctions not needed by target obligation but must retain required quotient distinctions | FORMAL-GMI principle + EMPIRICAL | student aliases required protected distinctions while claimed exact |
| pruning | morphology compression `Gamma` | remove parameters/factors whose absence does not change protected frontier enough to justify burden | EMPIRICAL-LAW | no burden/capability tradeoff after full search cost charged |
| quantization | resource/precision realization | lower precision is valid until numeric aliasing changes protected semantic consequence | PARENT + EMPIRICAL | semantic error unaffected by crossing measured precision threshold |
| caching | derived serving state | pays memory/invalidations to reduce repeated compute | PARENT systems principle | reuse/invalidation intervention has no effect on caching frontier |
| speculative decoding | proposal + verification | cheap model proposes; stronger model verifies, useful when acceptance high and verifier can cheaply check | PARENT/EMPIRICAL | speed benefit independent of acceptance/verifier-cost variables |
| serving compilation | A2 authority/derived separation | rich developmental state can compile into cheaper inference state when lost distinctions remain recoverable elsewhere if needed | FORMAL-GMI side-information theorem | lossy compiler supports all protected development with no side information |

---

# 13. Scaling, thresholds and apparent emergence

| Phenomenon | GMI placement | Explanatory statement | Status | Primary falsifier |
|---|---|---|---|---|
| neural scaling laws | empirical response surface over data/model/compute | smooth resource increases often reduce predictive loss over bounded regimes; coefficients are family/ecology/context dependent | EMPIRICAL-LAW | claimed universal exponent fails held families/scales |
| compute-optimal scaling | resource-price frontier | model size and data amount should be co-allocated to minimize loss at fixed compute, not scaled independently | EMPIRICAL-LAW | optimum does not shift with data/model/compute prices |
| capability thresholds | quotient/evaluation threshold | continuous loss improvement can cross a discrete admissibility boundary and look sudden | FORMAL-GMI observation + EMPIRICAL | underlying continuous score truly discontinuous under metric-continuity controls |
| emergent abilities | measurement + possible mechanism transition | some apparent emergence can be metric-induced; genuine emergence requires latent/order-parameter evidence beyond thresholded score | EMPIRICAL-LAW / PROGRAMME | discontinuity survives continuous metrics, dense scale sweep and mechanism controls |
| saturation | unresolved-information/resource limit | scaling gains must flatten when target-relevant unresolved structure, usable data, optimization access or evaluator sensitivity saturates | PROGRAMME | unlimited gains continue after all claimed bottlenecks are experimentally saturated |
| phase transitions | mechanism/frontier order parameter | reserve term for size-scaling/nonanalytic or defensibly critical behavior, not a finite winner switch | GMI methodological constraint | finite crossover mislabeled as critical evidence |

---

# 14. Robustness, causality and intervention

| Phenomenon | GMI placement | Explanatory statement | Status | Primary falsifier |
|---|---|---|---|---|
| causal representation | target quotient under interventions | observational prediction is sufficient only if intervention-relevant distinctions refine predictive state; otherwise residual/interventional information is required | FORMAL-GMI PRQ + parent causal theory | exact intervention behavior recovered from provably aliased observational state with no extra information |
| invariant prediction | cross-environment semantic structure | mechanisms stable across environments can support transfer better than spurious correlations | PARENT-THEOREM | invariance assumptions violated or no held-environment advantage |
| domain adaptation | changed ecology + limited target data | update burden depends on which quotient/mechanism factors changed | EMPIRICAL-LAW / PROGRAMME | adaptation cost unrelated to measured changed factors |
| adversarial training | robustness obligation added to `O` | changes target quotient by requiring equivalence across allowed perturbations | PARENT/EMPIRICAL | robust behavior achieved while merging states that obligation distinguishes |
| certified robustness | verifier/certificate | formal local guarantees require certificate semantics, not empirical accuracy alone | PARENT-THEOREM | certificate unsound at stated scope |

---

# 15. Architecture search and morphogenesis

| Phenomenon | GMI placement | Explanatory statement | Status | Primary falsifier |
|---|---|---|---|---|
| NAS | `Gamma` search over `F` | architecture is a developmental output; search cost and prior must be charged | EMPIRICAL-LAW / GMI accounting | claimed architecture advantage vanishes when search burden is included |
| neuroevolution | stochastic `Gamma` | uses population/selection to explore structures/parameters where gradients may be unavailable | PARENT/EMPIRICAL | advantage unrelated to feedback differentiability/search geometry |
| growth/pruning | online `Gamma` | structure changes when marginal capability/resource value justifies migration cost | PROGRAMME | no response to demand/price intervention |
| conditional computation | `K/F` routing | spends compute selectively on relevant factors; favored under sparse heterogeneous demand | EMPIRICAL-LAW | no advantage response to sparsity/heterogeneity |
| learned routing | adaptive A6/A7 | routing itself is developed and carries search/load-balancing burden | EMPIRICAL-LAW | routing quality not causal after expert matching |
| architecture plasticity | history-dependent `Gamma` | machine changes how it learns/represents rather than only parameters | PROGRAMME | structural change gives no frontier gain under ecology shift |
| meta-morphogenesis | updates to `Gamma` | experience changes the morphology-search law itself | OPEN / E6 | no replicated multi-generation advantage after search cost/control |

---

# 16. Distributed, federated and multi-agent learning

| Phenomenon | GMI placement | Explanatory statement | Status | Primary falsifier |
|---|---|---|---|---|
| data parallelism | physical realization `P,rho` | same update semantics spread over workers; useful if communication/synchronization price is favorable | PARENT systems | speedup independent of communication/straggler costs |
| model parallelism | factorized `F` across devices | required/favored when state exceeds local substrate or parallel compute offsets communication | PARENT systems | frontier unaffected by memory/communication repricing |
| federated learning | distributed authority/data constraint | raw data locality/privacy changes legal information flow and update aggregation | PARENT/EMPIRICAL | centralized-equivalent information assumed when legally unavailable |
| decentralized learning | distributed `U` | consensus/coordination burden enters `rho`; topology affects attainable synchronization | PARENT-THEOREM | convergence claims ignore topology/communication assumptions |
| ensembles/committees | multi-realization portfolio | diversity can reduce correlated errors, support uncertainty or specialization at added burden | PARENT/EMPIRICAL | no dependence on diversity/error correlation |
| multi-agent specialization | heterogeneous A7 | separate agents can specialize when task factors and communication geometry favor decomposition | PROGRAMME | specialization advantage survives dense coupling/communication-price hostiles |

---

# 17. Data quality, labels and feedback

| Phenomenon | GMI placement | Explanatory statement | Status | Primary falsifier |
|---|---|---|---|---|
| label noise | feedback channel `gamma_F` | lowers information/alignment of update signal and can change optimal capacity/regularization | PARENT/EMPIRICAL | no response to controlled noise at matched sample count |
| weak supervision | noisy/indirect feedback | trades label cost for lower signal quality; multiple sources can be combined under assumptions | PARENT/EMPIRICAL | source accuracies/dependencies ignored but claims remain exact |
| active learning | information acquisition in `D` | choose examples whose labels most reduce target uncertainty per acquisition cost | PARENT-THEOREM | no gain where queried information value is provably higher |
| synthetic data | generated development evidence | useful only insofar as generator preserves/adds target-relevant information and diversity; correlated errors can recycle bias | EMPIRICAL-LAW | synthetic gain independent of novelty/fidelity under matched tokens |
| data curation | development distribution | changes which distinctions receive learning pressure and how often | EMPIRICAL-LAW | target behavior invariant to causal curation shifts |
| data contamination | violation of protected split | can turn generalization evidence into memorization/retrieval evidence | GMI methodological constraint | leakage present yet protected-transfer claim unchanged |

---

# 18. Interpretability and mechanistic analysis

| Phenomenon | GMI placement | Explanatory statement | Status | Primary falsifier |
|---|---|---|---|---|
| probes | measurement of `Z/kappa` | decodability does not establish causal use; interventions are needed | PARENT methodological | probe-only evidence treated as causal |
| feature attribution | local response explanation | attribution method is a measurement operator with invariance/faithfulness obligations | PARENT/EMPIRICAL | attribution changes under function-preserving reparameterization where invariance claimed |
| mechanistic circuits | subrealization in `F/K` | causal ablation/patching can identify computation contributing to protected output | EMPIRICAL-LAW | circuit label survives causal-null interventions |
| concept bottlenecks | explicit intermediate quotient hypothesis | interpretable concepts help only if they preserve required target distinctions and do not hide extra channels | EMPIRICAL/PROGRAMME | hidden bypass carries claimed concept information |
| explanation/provenance output | separate obligation | truthful explanation is not implied by predictive accuracy; must be externally checked | GMI principle | explanation accepted from self-report without verifier/evidence |

---

# 19. Safety/alignment-adjacent learning phenomena at theory level

This atlas does not attempt a complete safety theory, but the following machine-learning distinctions are structurally important.

| Phenomenon | GMI placement | Explanatory statement | Status |
|---|---|---|---|
| reward misspecification | `O/V` vs internal objective | optimized proxy can diverge from external admissibility | GMI principle + parent decision theory |
| reward hacking | `K/U` exploiting proxy | high internal score is not proof of protected success | GMI principle |
| abstention/selective prediction | authority/admissibility action | when uncertainty/verification cost is high, refusal can be frontier-optimal | PARENT/EMPIRICAL |
| scalable oversight | verifier resource semantics | verification mechanism has its own cost/error scaling and can become bottleneck | PROGRAMME |
| corrigible update/admission | A4 authority separation | candidate changes should not become authoritative before registered acceptance when rejectability matters | FORMAL-GMI mechanism principle |

---

# 20. The missing quantitative layer

The atlas intentionally reveals what GMI does **not** yet derive from first principles.

The dominant remaining quantitative unknowns are response laws such as:

\[
\epsilon_{opt}(F,U,D,P,H),
\]

\[
\epsilon_{gen}(F,U,D,\mathfrak E),
\]

\[
\Lambda_M(\lambda_R,H_{dev}),
\]

\[
C_{search}(\Gamma,\mathcal G,P),
\]

and real-world estimators for semantic/predictive/residual quotient structure.

A complete GMI programme does not hide these behind architecture names. It treats them as measurable response surfaces with uncertainty and asks which portions admit derivation, parent-theorem reduction or empirical law.

---

# 21. Cross-phenomenon unifications predicted by GMI

The atlas suggests several nontrivial unifications.

## U1 — LoRA/adapters, retrieval and model editing are residual-state strategies

They differ physically, but each can be favorable when broad reusable state is mostly adequate and target change is low-dimensional/local relative to it.

Prediction: their relative advantage should track residual complexity, update frequency, query reuse, provenance and locality—not merely model family.

## U2 — MoE, modular networks and multi-agent specialization are conditional factorization strategies

Prediction: their advantage should track heterogeneity + sparse conditional demand minus routing/communication burden.

## U3 — continual learning, model editing and unlearning share update-geometry pressure

Prediction: dependency cones and protected retention should jointly predict collateral-change burden.

## U4 — distillation, caching and serving models are compilation strategies

Prediction: serving state can be more compressed than developmental/authoritative state exactly when discarded distinctions are not needed at serve time or remain recoverable elsewhere.

## U5 — in-context learning and meta-learning are timescale factorizations

Prediction: reusable slow state should encode an adaptation procedure when task-family regularity makes repeated fast adaptation cheaper than persistent retraining.

## U6 — RAG, causal memory and provenance ledgers are predictive-residual augmentations

Prediction: their necessity begins where target quotient distinctions fail to factor through ordinary predictive state.

## U7 — apparent emergence and frontier crossover must be disentangled

Prediction: many sharp benchmark jumps disappear under continuous metrics; genuine morphology/mechanism transitions should survive metric changes and show internal/resource order-parameter evidence.

---

# 22. Coverage rule for future ML concepts

When a new ML concept appears, add it to this atlas only after recording:

```text
name
registered phenomenon
GMI layer(s)
pre-outcome cause candidate
nearest parent theory
intervention
negative twin
resource meter
protected endpoint
status
kill condition
experiment ID
```

No concept is allowed to live only as prose.

If it cannot be mapped without smuggling the outcome into its explanatory variable, record

```text
UNMAPPED_GMI_PHENOMENON__THEORY_GAP
```

and add it to the gap ledger.

---

# 23. Claim ceiling

This atlas supports the claim:

> GMI now has a typed explanatory location and falsification route for a broad cross-section of modern machine-learning phenomena, connecting representation, optimization, generalization, memory, inference, verification, morphogenesis and resource economics.

It does **not** support:

```text
ALL_ML_NUMERICS_DERIVED_FROM_FIRST_PRINCIPLES
ALL_DEEP_LEARNING_MYSTERIES_SOLVED
EVERY_REAL_WORLD_SEMANTIC_QUOTIENT_IDENTIFIED
ONE_UNIVERSAL_SCALAR_INTELLIGENCE_LAW
```

The research objective is stronger and more useful than those slogans:

> continuously shrink `PROGRAMME` and `OPEN` cells into `FORMAL-GMI`, `PARENT-THEOREM` or replicated `EMPIRICAL-LAW` cells, while preserving explicit falsifiers and resource accounting.