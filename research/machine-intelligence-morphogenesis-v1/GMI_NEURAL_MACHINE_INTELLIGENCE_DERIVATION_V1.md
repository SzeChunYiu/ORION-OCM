# GMI Neural Machine-Intelligence Derivation v1

Status: **FORMAL SYNTHESIS / CONDITIONAL DERIVATION — NOT A CLAIM THAT DEEP LEARNING IS FULLY SOLVED**

Refs: `GMI_THEORY_V1.md`, `GMI_SEMANTIC_QUOTIENT_REALIZATION_THEOREM_V1.md`, `GMI_CROSS_PARADIGM_REALIZATION_NORMAL_FORM_V1.md`, `GMI_REALIZATION_DEMAND_SIGNATURE_V1.md`, `GMI_MECHANISM_NECESSITY_THEOREMS_V1.md`, `GMI_PREDICTIVE_SUFFICIENCY_NO_GO_V1.md`.

## 0. Question this document closes

GMI already says that neural, symbolic, probabilistic, programmatic and OCM-like systems may realize the same obligation-relative semantic developmental state in different ways.

That is not yet enough to answer:

1. **Why can a neural network count as machine intelligence at all?**
2. **Why can gradient-trained deep neural networks be unusually effective on many real tasks?**
3. **Why can predictive/self-supervised training produce capabilities far beyond literal next-step prediction?**
4. **Where does the neural explanation fail?**

This document supplies the missing neural specialization.

The result is not the claim that one theorem explains every empirical phenomenon in modern deep learning. That would be false. The result is a closed causal accounting chain:

```text
registered cognitive obligation
    -> semantic distinctions that must be preserved
    -> neural representability of the required transition/policy
    -> learnability under a declared update rule and data protocol
    -> transfer/generalization to protected situations
    -> execution and adaptation burden under resource prices
    -> intelligence adequacy or a named failure mode
```

Every neural-intelligence claim must pass every arrow. Universal approximation alone closes only one arrow.

---

# 1. Machine intelligence remains obligation-relative

Use the registered GMI obligation

\[
\mathcal O=(\mathfrak E,\mathcal A,\mathcal Y,V,C,\rho,H,D,J).
\]

Let

\[
S_{\mathcal O}
\]

be its semantic developmental quotient. A machine is not intelligent because it contains neurons, weights, attention, a loss function, or a large parameter count.

A machine is an adequate realization at a declared tolerance/resource level only if its protected future behavior and development preserve the distinctions demanded by `S_O` and satisfy the external admissibility/resource contract.

For approximate stochastic scope, define a protected semantic risk

\[
R_{\mathcal O}(M)
=
\mathbb E_{d,j\sim \mathcal P_{\mathcal O}}
[\ell_{\mathcal O}(\operatorname{Trace}_M(d,j),
                  \operatorname{Trace}_{\mathcal O}(d,j))],
\]

where:

- `P_O` is the prospectively registered protected distribution or weighted family over developmental situations and interventions;
- `ell_O` is the externally registered semantic loss/pseudometric;
- hard verifier/constitution violations are represented separately and may not be averaged away.

Call a realization `(epsilon, delta, B)`-adequate when, under the frozen protocol:

```text
protected semantic risk <= epsilon
hard protected violation probability <= delta
registered lifetime burden <= B
```

or the corresponding registered Pareto/admissibility relation when burden is vector-valued.

This is an operational machine-intelligence criterion. It is morphology-neutral.

---

# 2. Neural realization normal form

A fixed-architecture neural learner is a specialization of the GMI realization normal form

\[
\mathfrak N
=(Z,\kappa,Q,U,\Gamma,\rho_N)
\]

with, for example,

```text
Z       = weights theta
          + optimizer state
          + recurrent/activation state when persistent
          + replay/memory state
          + declared caches or external learned memory

kappa   = semantic interpretation into S_O

Q       = neural forward/predictive/policy/proposal kernel

U       = SGD / Adam / gradient-based or meta-learned update

Gamma   = architecture/topology/representation change
          or identity for fixed architecture

rho_N   = training + inference + memory + communication
          + accelerator + data + maintenance + verification burden
```

Important typing rules:

1. **Weights are realization state, not semantic state.** Different weights may implement the same protected semantics.
2. **Optimizer state is cognitive/developmental state when future learning is protected.** Two identical forward functions can be developmentally different.
3. **Prompt/context state is execution state.** In-context adaptation without weight change belongs primarily in `Q/Z`, not automatically in `U`.
4. **KV caches, retrieval stores and tools are not free.** If they carry distinctions used by future cognition they belong in `Z` or the declared external tool contract and in resource accounting.
5. **Pretraining is developmental capital.** It may be supplied by the protocol, but it cannot disappear from acquisition claims.

---

# 3. NMI-1 — neural intelligence admissibility theorem

## 3.1 Decomposition

For a neural family `N_A` with architecture/parameterization `A`, learning procedure `U`, and protocol `D`, define four prospectively measurable errors:

### Representation error

\[
\epsilon_{repr}
=
\inf_{\theta\in\Theta_A}
R_{\mathcal O}(N_{A,\theta}).
\]

This asks whether the architecture family contains a semantically adequate realization.

### Optimization/development error

Let `theta_hat = U(D)` be the state reached by the declared development process. Define

\[
\epsilon_{opt}
=
R^{proxy}(N_{A,\hat\theta})
-
\inf_{\theta\in\Theta_A}R^{proxy}(N_{A,\theta}),
\]

for the prospectively fixed training/development proxy objective.

### Proxy-to-protected generalization error

\[
\epsilon_{gen}
=
R_{\mathcal O}(N_{A,\hat\theta})
-
R^{proxy}(N_{A,\hat\theta}),
\]

with the sign replaced by an absolute or upper-confidence difference when needed.

This term includes sample, distribution, domain, task and intervention transfer at the declared scope.

### Interface / semantic compilation error

`epsilon_int` accounts for mismatch introduced between the learned numeric outputs and the registered semantic/action/verifier interface: decoding, calibration, tool/API compilation, thresholding, execution, or approximation of a required discrete semantics.

For developmental obligations add an explicit state/update term

\[
\epsilon_{dyn}
\]

measuring mismatch of future learning/update traces, not merely current prediction.

## 3.2 Statement

If the registered risk admits the corresponding additive/upper-bound decomposition, then the developed neural realization obeys

\[
R_{\mathcal O}(N_{A,\hat\theta})
\le
\epsilon_{repr}
+
\epsilon_{opt}
+
\epsilon_{gen}
+
\epsilon_{int}
+
\epsilon_{dyn}.
\]

For hard failure events with probabilities `delta_i`, a union bound gives

\[
\delta_{total}\le\sum_i\delta_i.
\]

If the resulting semantic and hard-failure bounds satisfy the registered admissibility threshold and

\[
\rho_N\le B,
\]

then the neural system is an adequate machine-intelligence realization at that declared scope.

## 3.3 Why this matters

This theorem is intentionally simple. Its value is that it blocks a common invalid inference:

```text
universal approximation
=> intelligence.
```

The valid chain is:

```text
representable
AND reachable by the actual development process
AND generalizes to protected futures
AND compiles to the required semantics
AND preserves protected developmental behavior
AND fits the resource/admissibility contract
=> adequate neural realization.
```

A failure at any term is a named scientific failure rather than a philosophical dispute about whether neural networks are "really" intelligent.

---

# 4. NMI-2 — neural representability is not the mysterious part

Classical universal-approximation results show that sufficiently wide feed-forward networks can approximate broad classes of functions on finite-dimensional compact domains. Modern sequence architectures have analogous universality results under their own assumptions; idealized recurrent/attention architectures can also simulate general computation.

Within GMI this means:

> For many finite/compact/approximable obligation scopes, there is no representation-theoretic prohibition on a neural `Q` implementing the required semantic input-output or state-transition map.

This supplies a **possibility theorem**, not a learnability theorem.

Parent results include:

- Cybenko (1989), Hornik/Stinchcombe/White (1989), Hornik (1991): universal approximation;
- Barron (1993): dimension-favorable approximation rates for a structured function class;
- Yun et al. (2020): Transformer universal approximation of sequence-to-sequence functions under stated compactness/positional assumptions;
- Perez, Marinkovic & Barcelo (2019): idealized Turing-completeness results for modern neural architectures.

GMI claims no novelty for those parent results.

## 4.1 Exactness qualification

Universal approximation does not imply exact finite-precision realization of arbitrary symbolic semantics.

If `O` requires exact arithmetic, exact proof, provenance, historical branching, certified deletion, or other discrete hard invariants, the neural realization must either:

```text
implement them exactly,
compose with an exact external mechanism,
or fail the obligation.
```

Approximate numerical similarity cannot silently replace a hard semantic contract.

---

# 5. NMI-3 — semantic quotient lower bound applies to neural state too

From the GMI semantic quotient theorem, every exact realization must preserve all distinctions in `S_O`.

Therefore a neural realization cannot gain intelligence by merely compressing two obligation-distinguishable developmental situations into the same effective future state.

For a finite exact quotient,

\[
|Z_{reachable}^{distinguishable}|\ge |S_{\mathcal O}|.
\]

Under an explicit robust-precision model this induces the corresponding information lower bound.

Continuous hidden state does not evade the theorem by writing infinitely many distinctions into a real number unless the declared precision/noise/resource model actually permits those distinctions to be reliably stored, updated and read.

This blocks the vacuous argument:

```text
"one real-valued neuron can encode everything"
```

from being treated as a physical machine-intelligence explanation.

---

# 6. NMI-4 — predictive-state transfer theorem

This is the main bridge from self-supervised prediction to broader intelligence.

## 6.1 Predictive quotient

Let `h` be a legal observed history in a training ecology. Define predictive equivalence

\[
h\sim_{pred}h'
\]

iff the conditional law of every registered future observation continuation is identical:

\[
P(O_{t:}\mid h)=P(O_{t:}\mid h').
\]

Let

\[
S_{pred}=H/\sim_{pred}
\]

be the predictive-state quotient.

This is the same mathematical family as causal-state / predictive-state constructions. It is not neural-specific.

## 6.2 Intelligence quotient

The target obligation induces its own future semantic equivalence

\[
h\sim_{\mathcal O}h'.
\]

## 6.3 Transfer statement

If predictive equivalence is **finer than or equal to** the target semantic equivalence,

\[
h\sim_{pred}h'\Rightarrow h\sim_{\mathcal O}h',
\]

then the target semantic quotient factors through the predictive quotient:

\[
q_{\mathcal O}
=
g\circ q_{pred}
\]

for a well-defined map `g` on reachable predictive states.

Therefore any internal representation sufficient for exact `S_pred` is also sufficient, in principle, to recover the obligation-relevant semantic state `S_O`.

### Interpretation

If the distinctions needed for the target task all change observable future statistics in the pretraining stream, then sufficiently complete prediction **forces the learner to retain enough information to support the task** even when the target task was not explicitly labeled during pretraining.

This is a rigorous reason predictive/self-supervised learning can create broadly reusable representations.

## 6.4 Converse no-go

If there exist `h,h'` such that

\[
h\sim_{pred}h'
\quad\text{but}\quad
h\not\sim_{\mathcal O}h',
\]

then a prediction-only learner is not forced by the predictive objective to preserve the distinction required by `O`.

Examples can include observationally aliased states that differ only under:

```text
intervention / action
counterfactual consequence
provenance / authority
historical lineage
hidden safety constraint
future teaching response
```

unless those distinctions affect the registered predictive stream.

Terminal:

```text
PREDICTIVE_QUOTIENT_TOO_COARSE_FOR_TARGET_INTELLIGENCE
```

This explains both the power and the limit of next-token pretraining without anthropomorphism.

---

# 7. NMI-5 — why next-token prediction can encode much more than the next token

For a sequence distribution with conditionals

\[
P(x_{t+1}\mid x_{\le t}),
\]

exact knowledge of the conditional next-token law for every reachable history determines the full future sequence law by the chain rule:

\[
P(x_{t+1:t+k}\mid x_{\le t})
=
\prod_{i=1}^{k}
P(x_{t+i}\mid x_{\le t+i-1}).
\]

Thus an exact all-history next-token predictor is an exact predictor of arbitrary finite continuations.

If language/text observations are generated by latent variables describing entities, events, goals, syntax, discourse, social conventions, code, mathematics, and world regularities, then any latent distinction that materially changes future-token distributions belongs to the predictive quotient and cannot be discarded by an exact minimal predictor.

This yields a precise GMI explanation of broad latent feature learning:

```text
world/semantic latent distinction
    -> changes future data distribution
    -> belongs to predictive quotient
    -> predictive sufficiency must preserve it
    -> learned representation can expose it to downstream decoders/policies.
```

But three qualifications are mandatory:

1. finite data/context/training only approximate this ideal;
2. the model may preserve a useful distinction in an inaccessible or fragile encoding;
3. observational prediction does not force distinctions that matter only under unseen interventions or constitutions.

Therefore:

```text
next-token prediction can be a powerful developmental protocol
!=
next-token prediction is sufficient for every intelligence obligation.
```

---

# 8. NMI-6 — depth can reduce realization burden when the target is compositional

Universal approximation alone gives no reason to prefer deep networks over shallow networks.

The relevant GMI question is morphology burden.

Suppose the protected map has a hierarchical composition

\[
f=f_L\circ f_{L-1}\circ\cdots\circ f_1
\]

or a tree/DAG of low-arity constituent maps. A deep architecture whose factorization mirrors that composition can reuse intermediate representations and may require dramatically fewer units/parameters than a shallow unstructured realization.

Parent depth-separation results establish explicit function families for which depth provides exponential representational savings (e.g. Telgarsky 2016; Eldan & Shamir 2016), and compositional-function analyses give settings where deep networks avoid otherwise severe dimension dependence (Mhaskar, Liao & Poggio 2017; related work).

GMI interpretation:

> Depth is valuable when it matches the dependency/composition geometry of the obligation. It is not intrinsically intelligent.

Hostile:

```text
same target family
same semantic tolerance
matched optimizer/data/hardware
no representational or lifecycle advantage from depth
```

narrows or kills a depth-specific morphology claim.

---

# 9. NMI-7 — representation learning changes the coordinate system of the problem

A fixed raw representation can make a simple semantic distinction expensive.

A learned hidden map

\[
r_\theta:X\to H
\]

is useful when it transforms the task into a lower-burden problem, for example when:

```text
relevant factors become more linearly/simple separable;
nuisance variation is quotiented out;
shared factors are reused across many outputs/tasks;
local neighborhoods better align with semantic similarity;
conditional prediction/control becomes lower-description-cost.
```

The relevant GMI quantity is not whether hidden units "look semantic" to a human. It is whether the learned representation reduces protected realization burden while preserving required semantic distinctions.

One operational test is a representation burden gap:

\[
\Delta B_{repr}
=
B(best\ downstream\ realization\ on\ raw\ X)
-
B(best\ matched\ realization\ on\ r_\theta(X)).
\]

A positive protected gap under matched information access is evidence that learning the representation created reusable computational structure.

Parent representation-learning work (e.g. Bengio, Courville & Vincent 2013; LeCun, Bengio & Hinton 2015) motivates this mechanism, but GMI requires the protected burden comparison rather than an architectural label.

---

# 10. NMI-8 — reverse-mode credit assignment makes huge parameterizations trainable at all

A scalar differentiable objective

\[
L(\theta)
\]

may depend on millions or billions of parameters through a computational graph.

Naively estimating one derivative at a time would make local parameter credit scale with parameter count times forward-evaluation cost.

Reverse-mode automatic differentiation/backpropagation computes the whole gradient with time of the same asymptotic order as evaluation of the graph, at the cost of storing/recomputing intermediate state.

This is a major realization advantage:

```text
one global scalar/vector training signal
+ compositional differentiable graph
-> simultaneous local credit information for a huge parameter state.
```

The neural system therefore gets an unusually cheap developmental update channel when the obligation can be represented by a differentiable surrogate whose gradients are informative.

Parent: reverse-mode automatic differentiation; Rumelhart, Hinton & Williams (1986); modern AD surveys such as Baydin et al. (2018).

GMI qualification:

> Cheap gradients are useful only when the proxy gradient is aligned with protected semantic improvement.

If the differentiable objective is misspecified, backpropagation efficiently optimizes the wrong thing.

Terminal:

```text
CHEAP_CREDIT__MISALIGNED_SEMANTIC_OBJECTIVE
```

---

# 11. NMI-9 — overparameterization separates search convenience from semantic complexity

Modern networks frequently contain many more parameters than a naive minimum description would suggest.

This is not paradoxical in GMI because:

```text
semantic minimality
!=
optimization-geometric minimality
!=
resource-optimal realization.
```

Additional implementation degrees of freedom may make an adequate function easier for gradient methods to reach even when many parameter states implement equivalent or near-equivalent functions.

There are rigorous parent results showing global/fast convergence of gradient methods in specific sufficiently overparameterized network regimes. Those results do not prove that all practical deep networks operate in the same regime.

GMI therefore treats overparameterization as a candidate **development/search-geometry mechanism**, not as the source of intelligence.

Required measurements include:

```text
optimization success probability/time;
protected test risk;
parameter/function-space redundancy;
robustness to initialization;
resource burden;
comparison with matched smaller or differently parameterized realizations.
```

---

# 12. NMI-10 — generalization is an ecology-alignment claim, not a parameter-count miracle

A high-capacity network can memorize arbitrary labels. This directly proves that expressive capacity alone does not explain generalization.

The developed predictor is selected jointly by:

```text
architecture
parameterization
initialization
optimizer
loss
training schedule
regularization/noise
training distribution
pretraining history
```

Call this complete development algorithm `A_dev`. It induces an effective preference over functions even when the nominal architecture can represent far more functions.

GMI therefore defines neural generalization relative to a registered environment family as:

\[
G_{\mathcal O}(A_{dev})
=
R_{protected}(A_{dev})-R_{development}(A_{dev}).
\]

A neural family is "good" when its effective development bias aligns with stable structure in the ecology.

Possible parent mechanisms include:

```text
margin/norm bias;
implicit bias of gradient methods;
stability;
feature learning;
smooth/manifold structure;
symmetry/equivariance;
benign interpolation in high-dimensional regimes;
pretraining-induced priors.
```

No one of these is elevated to a universal neural-generalization theorem.

The correct universal statement is weaker and falsifiable:

> Generalization requires alignment between the learner's effective inductive/developmental bias and invariances/regularities that remain valid on protected futures.

Random-label and distribution-remint hostiles directly test that alignment.

---

# 13. NMI-11 — neural learning is especially strong when supervision is dense and reusable

A neural objective can often turn enormous raw datasets into dense training signals:

```text
classification: one or several targets per example;
autoregressive modeling: a target at almost every sequence position;
masked modeling: many reconstruction targets;
contrastive learning: many relational comparisons;
control/RL: repeated temporal prediction/value/policy signals.
```

When those signals correlate with protected semantics, a large fraction of the available data stream can contribute gradient information to shared parameters.

This creates a developmental economy very different from systems that require a human-authored rule, proof step, symbolic decomposition or architecture edit for each new distinction.

The advantage is conditional on information quality. Dense wrong or weakly related supervision can create dense wrong credit.

---

# 14. NMI-12 — amortized cognition theorem

One of the strongest reasons learned neural networks can be effective is that they move computation from repeated online search/inference into an expensive developmental phase whose result is reused.

Let:

```text
C_train^N      neural training/development cost
C_build^A      alternative construction cost
c_query^N      neural per-query serving cost
c_query^A      alternative per-query reasoning/search cost
N_use          number of reuse queries before invalidation/retraining
```

Ignoring common costs, neural realization has lower lifecycle burden whenever

\[
C_{train}^{N}+N_{use}c_{query}^{N}
<
C_{build}^{A}+N_{use}c_{query}^{A}.
\]

If

\[
c_{query}^{A}>c_{query}^{N},
\]

then neural amortization wins after

\[
N_{use}
>
\frac{C_{train}^{N}-C_{build}^{A}}
     {c_{query}^{A}-c_{query}^{N}}.
\]

Maintenance, update, memory, communication and verification terms can be added to the same lifecycle inequality.

This is a concrete GMI derivation of a familiar neural advantage:

> Train an expensive distributed approximator once, then answer a huge number of related queries with a small fixed computation graph instead of re-solving each query from scratch.

Parent analogues include amortized inference and recognition models in probabilistic inference.

This mechanism predicts a negative twin:

```text
very few future uses
+ high training cost
+ rapidly invalidating world
=> neural pretraining advantage can disappear.
```

---

# 15. NMI-13 — hardware co-design is part of the explanation

Modern neural networks are dominated by regular tensor operations that map well to massively parallel accelerators.

Under the typed GMI theory, this is **not** an obligation coordinate. It belongs in exogenous context/resource prices `P`, including quantities such as:

```text
price/latency/energy of matrix multiply;
memory bandwidth;
parallelism;
interconnect cost;
precision support;
compiler/kernel quality.
```

A morphology can become frontier-optimal because the substrate makes its primitive operations cheap.

Therefore "neural networks are intrinsically computationally optimal" is too strong.

The correct claim is:

> Under contemporary accelerator/resource prices, dense differentiable tensor programs often have unusually favorable execution and training economics.

A hardware-price reversal is a legitimate hostile intervention.

---

# 16. NMI-14 — why Transformers are a particularly strong neural morphology

Transformers combine several useful mechanisms in one realization:

1. **shared learned representation:** token/features are mapped into a common continuous workspace;
2. **content-dependent routing:** attention lets each position condition computation on other positions selected by learned similarity/content;
3. **depth/composition:** repeated attention + nonlinear blocks build hierarchical transformations;
4. **parameter sharing across positions/examples:** the same rules are reused broadly;
5. **parallelizable training:** unlike strictly sequential recurrence, many training computations can be batched/parallelized;
6. **dense predictive supervision:** autoregressive or masked objectives reuse raw sequence data at many positions;
7. **amortization:** expensive training is converted into fast repeated forward passes;
8. **context state:** prompts and activations provide a temporary task-specific state without changing long-term weights.

Universal-approximation results for Transformers show that this family has broad representational capacity. The practical advantage comes from the **combination** of representability, routable composition, scalable credit assignment, data reuse and favorable hardware—not from attention alone.

A Transformer may still fail obligations demanding:

```text
exact persistent lineage;
strong local unlearning;
certified provenance;
stable continual update;
formal proof exactness;
causal distinctions absent from observational data;
strict bounded worst-case behavior.
```

Those requirements can select hybrid or non-neural morphologies.

---

# 17. NMI-15 — neural success regime in typed GMI coordinates

Using the typed obligation signature

\[
\Xi_{obl}^{(1)}
=(\sigma,\Delta_Q,\Delta_U,\gamma_F,\nu,\chi_V,
  \rho_{use},\lambda_R,\beta_{lin}),
\]

plus exogenous context `P`, the canonical neural-friendly regime is **not** "high intelligence". It is a specific demand/resource profile.

A broad learned neural realization is favored when, approximately:

```text
sigma          high semantic/input complexity but with reusable statistical structure
Delta_Q        many related high-dimensional queries share latent factors
Delta_U        large batch/global development is acceptable, at least during major training
Gamma_F        abundant feedback/prediction signal can be converted to informative gradients
rho_use        very high reuse before major invalidation
chi_V          approximate/statistical verification is meaningful, or exact checks can be composed externally
lambda_R       retention requirements are compatible with the update scheme or replay/modularity is added
beta_lin       historical branch persistence is not the dominant requirement, unless external versioning is added
P              tensor operations and parallel training are cheap relative to alternatives
```

Neural dominance should weaken as the obligation moves toward:

```text
few-shot exact symbolic transformation with no reusable statistics;
strict proof/provenance authority;
frequent local updates with strict no-interference constraints;
high lineage/as-of query demand;
non-differentiable sparse feedback with weak proxy alignment;
very low reuse before invalidation;
substrates that make dense tensor compute expensive.
```

This is a morphology prediction, not an architecture slogan.

---

# 18. NMI-16 — complete neural-effectiveness burden equation

For comparison against an alternative realization `A`, define registered lifetime burden

\[
B^{N}_{life}
=
B_{data}
+B_{train}
+B_{search}
+B_{serve}
+B_{update}
+B_{memory}
+B_{comm}
+B_{verify}
+B_{failure}
+B_{maintenance}.
\]

Neural networks are "so good" in a scientifically meaningful GMI sense exactly when they reach a protected semantic/admissibility region with lower burden/frontier tradeoff than matched alternatives.

Their recurring sources of advantage are then decomposed as:

```text
A. representational adequacy              broad nonlinear function class
B. compositional efficiency               depth / reuse of intermediate structure
C. representation learning                coordinates learned from data
D. cheap global credit assignment         reverse-mode differentiation
E. favorable search geometry              sometimes helped by overparameterization
F. development bias / generalization       optimizer+architecture+data alignment
G. parameter sharing / symmetry            reuse across locations/tokens/examples
H. amortized cognition                     expensive learning -> cheap repeated serving
I. dense self-supervision                  large raw streams create many learning signals
J. dynamic context routing                 attention / recurrent state / activation state
K. substrate economics                     accelerators make primitives cheap
L. scale headroom                          more data/model/compute can resolve additional structure
```

No single item is sufficient. The conjunction explains the empirical dominance regime.

---

# 19. Scaling laws fit GMI as response curves, not magic laws

Empirically, many neural systems show smooth power-law-like improvement in loss with more model size, data or compute across broad ranges.

GMI represents this as a morphology response surface, for example

\[
R_N(C,D,P)
\approx
R_\infty+aC^{-\alpha}+bD^{-\beta}+\cdots
\]

inside a registered regime.

Recent parent theory connects some scaling regimes to variance-limited and resolution-limited behavior and to smooth data-manifold assumptions. These are useful mechanisms, not universal laws of intelligence.

The GMI interpretation is:

> Scaling remains productive while additional resources buy finer approximation/estimation of obligation-relevant structure faster than they increase lifecycle burden.

A plateau, distribution shift, verifier mismatch, data exhaustion, or objective mismatch can end the regime.

Thus empirical scaling supports a **resource-response law for a morphology in an ecology**, not an unlimited intelligence theorem.

---

# 20. Neural capability is not neural epistemic authority

A neural network may generate an answer, proof sketch, diagnosis, program, factual statement or action with high probability/confidence.

GMI keeps external `V,C` separate:

```text
neural probability != truth
neural logit != authority
neural fluency != evidence
neural self-critique != external verification
```

Neural systems can be machine-intelligent realizations while still requiring exact checkers, retrieval/provenance, execution sandboxes, theorem provers, databases, humans, or other mechanisms for protected authority.

This is not a weakness of the definition. It is what allows neural intelligence to be integrated with stronger hybrid morphologies.

---

# 21. Canonical falsifiers

Any serious neural explanation must survive the following hostiles.

## F1 — random-label hostile

Keep architecture/optimizer/resource scale but destroy reusable input-output structure.

Prediction:

```text
training fit can remain high;
protected generalization advantage collapses.
```

Kills "capacity alone explains generalization."

## F2 — predictive-collision hostile

Construct histories identical in observational future distribution but different under protected interventions/provenance/lineage.

Prediction:

```text
prediction-only representation need not preserve target distinction.
```

Tests NMI-4.

## F3 — reuse hostile

Reduce `rho_use` while keeping training cost high.

Prediction:

```text
amortized neural advantage shrinks or reverses.
```

## F4 — gradient-alignment hostile

Hold data and architecture fixed but use a differentiable proxy weakly aligned with protected semantics.

Prediction:

```text
optimization becomes efficient while semantic adequacy worsens.
```

## F5 — composition hostile

Compare deep and shallow/matched alternative families on targets with and without hierarchical compositional structure.

Prediction:

```text
depth-specific burden advantage appears only where structural match exists.
```

## F6 — hardware-price hostile

Reprice dense tensor operations, memory, communication and symbolic/search primitives.

Prediction:

```text
frontier membership may change without any semantic change.
```

## F7 — lineage/continual-update hostile

Increase local revision, historical persistence and strict retention requirements.

Prediction:

```text
plain monolithic neural realization loses frontier position unless augmented by replay, modularity, versioning or external memory.
```

## F8 — implementation-equivalence hostile

Realize the same protected function with neural, kernel, compiled table, symbolic or hybrid mechanisms under matched information and hardware accounting.

Prediction:

```text
GMI credits the lower-burden realization, not the neural label.
```

---

# 22. What is now derived, and what is not

## Derived at theory level

GMI can now explain, without neural exceptionalism:

1. **why neural networks can be machine intelligence:** they can instantiate the same semantic developmental realization contract as any other morphology;
2. **why expressivity is enough for possibility but not success:** adequacy decomposes into representation, optimization, generalization, semantic compilation, developmental and resource terms;
3. **why predictive pretraining can create broad latent competence:** predictive sufficiency must preserve every latent distinction that changes future data, and target intelligence transfers when its quotient factors through that predictive state;
4. **why prediction can still miss important intelligence:** observationally aliased intervention/provenance/lineage distinctions are not forced into the representation;
5. **why depth helps:** under matching compositional structure it can reduce representation burden dramatically;
6. **why backprop helps:** reverse-mode credit makes huge differentiable parameter states updateable at roughly forward-pass asymptotic cost;
7. **why overparameterization can help:** redundant realization coordinates can improve search geometry without changing semantic-state minimality;
8. **why generalization is possible:** development induces an effective function bias that can align with stable ecology structure, while random-label capacity proves this is not automatic;
9. **why pretraining pays:** it amortizes expensive development over enormous reuse;
10. **why modern Transformers are especially competitive:** broad sequence expressivity + shared representation + content routing + dense supervision + parallel training + hardware alignment;
11. **why scale can keep helping:** additional resources can progressively resolve reusable structure, producing morphology-specific scaling curves;
12. **why neural networks are not universally best:** exactness, lineage, local revision, provenance, sparse feedback or different substrate prices can select other/hybrid morphologies.

## Not derived as universal facts

GMI does **not** currently claim a closed-form universal predictor for:

```text
which practical SGD run converges to which basin;
exact generalization error of arbitrary deep networks;
all emergent capabilities at a given parameter count;
the exact scaling exponent for every dataset/architecture;
feature identifiability inside arbitrary trained networks;
robust OOD/causal transfer from observational training alone;
catastrophic-forgetting-free continual learning;
consciousness or subjective experience.
```

These remain empirical/theoretical subproblems.

The important closure is that none is now an untyped mystery: each has a defined place in the GMI causal chain and a corresponding measurement/falsification interface.

---

# 23. Scientific completion criterion

For GMI, a "complete explanation of why neural networks can be effective machine intelligence" means:

```text
no explanatory jump from architecture label to intelligence;
no appeal to capacity where learnability is required;
no appeal to train loss where protected transfer is required;
no appeal to prediction where intervention semantics are required;
no appeal to parameter count where effective development bias is required;
no appeal to FLOPs without substrate prices;
no appeal to current behavior when future learning is protected;
no unexplained omission of training/data/search/verification burden.
```

By this criterion the neural explanation is structurally complete at v1: every required causal category has a typed variable, theorem/conditional, burden term, or named open empirical response.

It is **not** scientifically legitimate to rename unresolved quantitative deep-learning questions as solved. Those questions are registered as response laws to be measured or further theorized rather than hidden inside the word "neural".

---

# 24. Parent-literature subtraction

This document synthesizes rather than reclaims the following parent ideas:

- universal approximation: Cybenko; Hornik/Stinchcombe/White; Hornik;
- approximation rates: Barron;
- depth separation/compositional efficiency: Telgarsky; Eldan & Shamir; Mhaskar/Liao/Poggio and related work;
- representation learning: Bengio/Courville/Vincent; LeCun/Bengio/Hinton;
- backpropagation / reverse-mode AD: Rumelhart/Hinton/Williams; automatic-differentiation literature;
- implicit bias / modern generalization: Soudry et al.; norm/margin/stability/PAC-Bayes/benign-overfitting literatures;
- overparameterized optimization: Du et al.; Allen-Zhu/Li/Song and related work;
- predictive-state representations / causal states: Littman/Sutton/Singh; Singh/James/Rudary; computational mechanics;
- amortized inference: stochastic-inverse / recognition-model / variational-inference literature;
- Transformers: Vaswani et al.; Yun et al.; modern sequence-architecture theory;
- neural scaling: Kaplan et al.; Hoffmann et al.; Bahri et al. and related work.

The GMI contribution claimed here is the **typed integration and falsifiable derivation chain** linking these mechanisms to obligation-relative semantic developmental sufficiency and lifecycle morphology selection.
