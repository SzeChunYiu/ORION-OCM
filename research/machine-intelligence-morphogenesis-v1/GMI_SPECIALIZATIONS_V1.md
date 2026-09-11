# GMI Specializations v1 — known forms as realizations of one developmental object

Status: **formal mapping / parent-preserving derivation**. These mappings do not claim that GMI invented the underlying architectures.

Canonical morphology:

\[
M=(F,\Theta,K,U,\Gamma,\kappa,\rho_M).
\]

The purpose of this file is to demonstrate that the same abstract slots can describe materially different machine-intelligence forms without changing definitions.

---

# 1. Static decision/search agent

Take:

```text
F      fixed state representation / model
Theta  fixed parameters/memory
K      policy/search/planning kernel
U      identity
Gamma  identity
kappa  maps internal state/actions to obligation semantics
rho    execution/search resources
```

This is the no-development special case of GMI.

AIXI/UAI-style ideal agents can be viewed at this layer: the focus is optimal action/prediction under a specified environment model/prior rather than morphology development.

Therefore GMI does not require learning. Development is an additional capability.

---

# 2. Neural / differentiable learner

Let a feedforward network have graph `F` and parameters

\[
\Theta=\{W_l,b_l\}_{l=1}^L.
\]

Execution is

\[
h_{l+1}=\sigma_l(W_l h_l+b_l),
\qquad
K(x)=f_\Theta(x).
\]

A gradient learner specializes `U` to

\[
\Theta_{t+1}
=\Theta_t-\eta_t\,\widehat{\nabla}_\Theta\mathcal L_t(\Theta_t).
\]

`Gamma` may be identity, or may include architecture search, growth, pruning, module addition or neuroevolution.

Resource semantics may include:

```text
parameter bytes
activation memory
training examples
forward FLOPs
backward FLOPs
optimizer state
communication/all-reduce
inference FLOPs/latency
retraining/update cost
```

### Developmental state interpretation

The future-distinguishable developmental state need not be individual neurons. It may be represented by the entire relevant parameter/optimizer/history state, or a quotient thereof relative to the obligation.

### Why neural networks are one morphology, not the foundation

Neural systems are particularly effective where their factorization/update geometry creates useful smooth/shared representations, dense credit assignment and strong training→inference amortization. GMI treats those as morphology-specific properties, not axioms of intelligence.

### Meta-learning

MAML/learned optimizers/meta-RL instantiate a higher-level `U` whose parameters are trained so that future within-task updates are efficient. They are direct K2-like parents under their respective task assumptions.

---

# 3. Symbolic production / cognitive architecture

Let

```text
F      typed predicates, rule index, working-state organization
Theta  production rules, facts, preferences, agenda/activation state
K      match -> propose -> select -> apply / search cycle
U      chunking, rule induction, revision, utility update
Gamma  vocabulary/operator/state-representation restructuring
```

A production `r` can be represented schematically as

\[
r:(condition(z)\Rightarrow action/update(z)).
\]

Execution is discrete and often sparse rather than distributed/differentiable.

Resource semantics include:

```text
rule matching work
index lookup
agenda conflict resolution
search depth/branching
rule-base storage
revision dependency work
verification
```

Soar is a strong parent for this specialization.

### Developmental-state mapping

Two working/rule states are equivalent only when no future allowed observations/teachings/actions produce different protected traces/resources. Thus GMI state minimality is independent of whether the representation is symbolic.

---

# 4. Bayesian / probabilistic morphology

Let a model family have structure `F`, latent variables `z`, parameters `theta` and belief/posterior state

\[
\Theta_t=P_t(z,\theta\mid h_t).
\]

Execution/cognition `K` may perform prediction, inference, sampling, expected-utility planning or experiment choice.

A simple Bayesian update specializes `U` to

\[
P_{t+1}(z,\theta)
\propto
P(e_t\mid z,\theta)P_t(z,\theta).
\]

`Gamma` may perform model-structure search, factor addition/deletion, latent-structure learning or probabilistic-program synthesis.

Resource semantics include:

```text
samples
likelihood evaluations
message passing
normalization / partition approximation
posterior storage
experiment/observation cost
```

### Developmental state

For prediction-only obligations, computational-mechanics causal states / predictive-state representations are related minimal abstractions. For decision/development obligations, the sufficient state may need more than a posterior predictive statistic if future learning/resource behavior differs.

---

# 5. Programmatic / synthesis / library-learning morphology

Let

```text
F      grammar + typed program/library/call graph
Theta  current library, priors/search weights, partial solutions
K      program enumeration/synthesis/execution
U      abstraction mining, library admission, search-prior update
Gamma  grammar/operator/library structural change
```

For prefix-coded search, a candidate program `p` may receive mass/work allocation proportional to

\[
2^{-L(p)}.
\]

Adding a reusable abstraction can shorten future descriptions and therefore alter proposal/search geometry.

OOPS, DreamCoder, Stitch and related program-learning systems are strong parents.

Resources:

```text
enumerated candidates
execution cost
checker/verifier calls
library construction
lookup/indexing
storage
maintenance/invalidation
```

### OCM #323 connection

The existing OCM traversal-capital evidence is naturally represented here: learned/selected reusable fragments and controller state alter future proposal order before fresh target success. That is K1 evidence at the registered authored grammar, not proof of a universal GMI law.

---

# 6. Search / evolutionary morphology

Let `Theta` be a population/archive and `K` a proposal/variation/selection kernel.

```text
F      genome/program/network encoding + archive organization
Theta  population/archive/fitness/evidence state
K      mutation/recombination/proposal + selection
U      population/archive update
Gamma  mutation-kernel/search-operator/encoding evolution
```

This covers ordinary evolutionary algorithms, quality-diversity, NEAT-like topology evolution and parts of PowerPlay.

Useful descendant mass can be written

\[
Ev(M;\mathcal U)
=P_{x'\sim K(\cdot|x)}[x'\text{ is useful/admissible under future ecology }\mathcal U].
\]

This is morphology-specific developmental geometry.

---

# 7. Reservoir / dynamical morphology

A high-dimensional dynamical substrate provides state transformations while only a cheap readout may be trained.

```text
F      recurrent dynamical network / physical reservoir
Theta  reservoir state + readout parameters
K      dynamical evolution + readout
U      usually readout learning; possibly reservoir adaptation
Gamma  topology/physical reconfiguration if allowed
```

This specialization is useful because it demonstrates that strong computation can arise with very different credit-assignment/update structure from conventional deep gradient training.

---

# 8. Vector-symbolic / hyperdimensional morphology

```text
F      high-dimensional vector spaces + binding/bundling algebra
Theta  concept/item memories / learned projections
K      algebraic vector operations + associative retrieval
U      memory/prototype/projection updates
Gamma  symbol/vocabulary/encoding restructuring
```

This is a distinct factorization of representational state that can support distributed representations and explicit algebraic composition.

---

# 9. Hybrid morphology

A hybrid is not merely “two modules exist.” It is a coupled morphology

\[
M_H=(M_1,M_2,\ldots,I),
\]

with explicit interfaces `I`, coordination/control, cross-module costs and potentially joint development.

Examples:

```text
neural perception + symbolic proof
LLM proposer + Lean verifier
neural retrieval + program search
probabilistic world model + planner
OCM controller + donor LLM/CAS/Lean/Python
```

A hybrid counts as a distinct developmental morphology only if its coupled developmental/resource behavior is not reducible at acceptable cost to a registered parent realization.

---

# 10. OCM-like governed explicit morphology

Map current OCM approximately as:

```text
F
  persistent warranted field / KnowledgeSpace
  dependency/provenance organization
  explicit cognitive assets / libraries

Theta
  facts, methods, applicability/control state
  failure memory
  self-model / lifecycle / authority metadata

K
  retrieval
  search
  composition
  controller / executive
  donor/tool invocation

U
  externally verified admission
  revision / revocation
  failure learning
  applicability/value update
  consolidation/retirement

Gamma
  governed proposal of representation/operator/control changes
  eventual self-improvement / morphology change

kappa
  Check/Authority/Meter/Commit constitution + domain contracts

rho
  search slots / compute / checker calls / acquisition / validation /
  storage / maintenance / revision / donor cost
```

OCM's distinctive engineering emphasis is explicit warrant/provenance/governance/resource lineage. Whether that yields a general intelligence advantage is empirical.

---

# 11. Same abstract question across all forms

For every specialization the theory asks the same questions:

```text
1. What histories/states are future-distinguishable for the registered obligation?
2. How is that developmental state factorized/represented?
3. What proposal/action kernel does the morphology induce?
4. How does experience change the state/kernel/factorization?
5. What complete resources are consumed to reach verified outcomes?
6. Which previous experience changes future verified burden?
7. Does experience change only answers (K0), cognition generation (K1),
   acquisition of new cognition (K2), or the improvement process itself (K3)?
8. Over what ecology family is the effect valid?
```

If these questions cannot be asked without changing definitions for one architecture family, GMI-v1 is not general enough and must be revised.