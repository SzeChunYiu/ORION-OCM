# General Machine Intelligence Theory v1 (GMI-v1)

Status: **formal synthesis / working theory**, subordinate to #233 (HST), #377 and #373. Parent theorems are adopted where they already solve a layer.

## 0. Central thesis

A general theory of machine intelligence should not identify intelligence with one implementation family. It should explain neural, symbolic, Bayesian, programmatic, evolutionary and OCM-like systems as different realizations of a common abstract developmental object, while preserving the differences in how those realizations learn, search, revise and consume resources.

GMI-v1 proposes:

> **Machine intelligence is the capacity of a resource-bounded adaptive system, from a declared developmental situation and under a declared development protocol, to reach externally admissible verified outcomes across a registered ecology family and to transform its own future cognition-generation process from experience. Different intelligence morphologies are different computational factorizations / inductive biases / update geometries realizing task-relative sufficient developmental states.**

The key hierarchy is:

```text
future cognitive obligation + development protocol
        ↓
semantic developmental sufficient state
        ↓
computational morphology / factorization
        ↓
resource-labelled execution + learning + morphogenesis
        ↓
verified capability/resource developmental frontier
```

This is a synthesis theory. It may legitimately use parent mathematics at every layer.

---

# 1. Cognitive obligation and development protocol

Every intelligence statement is relative to

\[
\mathcal O=(\mathfrak E,\mathcal A,\mathcal Y,V,C,\rho,H,D,J),
\]

where:

- `\mathfrak E` — registered ecology/task family or distribution;
- `A` — legal machine actions/computations/tool calls;
- `Y` — externally visible outcome/evidence space;
- `V` — external verifier/evidence semantics;
- `C` — external constitution: evaluator identity, protected information, authority/adoption rules;
- `rho` — raw resource-metering coordinates;
- `H` — registered horizon/stopping regime;
- `D` — development protocol: initialization, supplied pretrained state, legal information/updates/tools/human input/reset/morphology-change rules;
- `J` — registered external intervention/probe/teaching class used for future distinguishability.

There is no representation-independent scalar intelligence without choosing at least an ecology/evaluation/resource/development contract.

## 1.1 Development protocol is part of the evaluated system

`D` must declare at least:

```text
initial state / supplied pretrained capital
legal training/development streams
availability/timing of labels/answers
preinstalled vs acquired tools/donors
machine-proposed vs externally imposed updates
human intervention and its meter
morphology-change permissions
reset/continuation semantics
maintenance/revalidation obligations
```

A human engineer installing a solution is not free machine intelligence. A pretrained model may be evaluated as a deployed system, but its supplied capital is part of `d,D` and must be controlled or charged when acquisition claims are made.

## 1.2 Verification is external to internal optimization

`V,C` remain outside the learner's internal objective:

```text
low loss != truth
high reward != verified evidence
high confidence != admissibility
```

This allows the same theory to cover formal proof, code execution/tests, retrieval/provenance, empirical evidence and explicit abstention/refusal.

---

# 2. Developmental situations

External history alone need not determine the future of a learning system.

Let

\[
h_t=(o_0,a_0,e_0,r_0,\ldots,o_t)
\]

be registered interaction/development history and `chi_t` the current machine configuration relevant to future protected behavior/development.

Define the **developmental situation**

\[
d_t=(\chi_t,h_t,\xi_t),
\]

where `xi_t` contains current registered public/experimental context that can affect protected futures.

Identical histories may leave different optimizer state, posterior, recurrent state, replay memory, library, rule base, random state or topology, so `chi_t` is necessary in the theory-level situation.

Hidden environment variables unavailable to the machine are not free machine information. They are integrated over the ecology/environment law conditional on legal observations unless the task contract legally exposes them.

---

# 3. Semantic developmental sufficient state

The primary representation-independent state should preserve **cognitive/developmental semantics**, not implementation cost.

Let

\[
(\Omega^{sem}_{\mathcal O},\mathcal F^{sem}_{\mathcal O})
\]

be the registered future semantic trace space. It may include:

```text
external outputs/actions
external verifier/evidence/admissibility receipts
future responses to registered teaching/probes
registered retention/plasticity/generalization observables
authority/abstention/refusal outcomes
```

It does **not** automatically include private weight/topology/rewrite traces or raw implementation resource receipts.

For fixed `O,D,J`, define

\[
d\sim^{sem}_{\mathcal O,D,J} d'
\]

iff every `j in J` induces the same probability law over protected future semantic traces:

\[
P(\Omega^{sem}_{\mathcal O}\mid d,j,D)
=
P(\Omega^{sem}_{\mathcal O}\mid d',j,D).
\]

The **semantic developmental sufficient state** is

\[
z^{sem}=[d]_{\sim^{sem}_{\mathcal O,D,J}}.
\]

This is the theory's strongest representation-independent primitive **state distinction**.

It is not a physical cognitive atom and need not be computable.

Parent instances include:

- deterministic automata/transducer minimization;
- predictive-state representations;
- computational-mechanics causal states/epsilon-machines;
- bisimulation/state abstraction.

## 3.1 Minimality

A semantic distinction is necessary iff merging two situations changes at least one registered future semantic distribution under the allowed intervention/development semantics.

The meaningful minimal object is therefore:

```text
minimal sufficient developmental state relative to (O,D,J)
```

not a universal smallest neuron/rule/operator.

## 3.2 Approximation

Exact equality gives a true equivalence relation. For stochastic/continuous systems use a registered probability pseudometric or parent bisimulation/predictive-state construction.

Naive finite-epsilon closeness is generally not transitive at the same epsilon, so it must not be treated as an exact quotient without additional abstraction/error theory.

---

# 4. Morphology as a resource-labelled realization

The same semantic developmental process may have multiple computational realizations.

Define a morphology

\[
M=(F,\Theta,K,U,\Gamma,\kappa,\rho_M),
\]

where:

- `F` — factorization/topology/program/graph organization;
- `Theta` — mutable parameters, rules, memory, beliefs/configuration;
- `K` — execution/cognition/proposal/action kernel;
- `U` — within-morphology experience-driven update law;
- `Gamma` — structural/morphogenetic law changing `F`, `K`, `U` or their family;
- `kappa` — semantics/compiler map connecting realization states to `z_sem`/task semantics;
- `rho_M` — implementation resource semantics.

Schematically a realization executes resource-labelled semantic transitions:

\[
K_M:(z,o,g)\to\mathcal D(z',y,e,\mathbf r).
\]

Two morphologies may therefore be semantically equivalent yet have radically different:

```text
description size
compute
memory
communication
learning/update work
maintenance/revision
hardware efficiency
```

This separation is essential: those differences are the reason morphology matters.

## 4.1 Current resource availability vs spent resources

If remaining budget/deadline/memory changes future legal actions, that **resource state** belongs in the current situation/context `xi`.

The resources consumed by a realization are **transition receipts** used in burden/frontier comparison.

## 4.2 Resource-sensitive morphology equivalence

Morphology equivalence is stronger than semantic-state equivalence.

A registered bounded developmental compiler relation may require preservation of:

```text
semantic future traces
learning/development responses
verification/authority semantics
resource inflation bounds
```

Thus semantic equivalence does not imply morphology/resource equivalence.

---

# 5. Three timescales

## 5.1 Execution / cognition

For fixed morphology:

\[
(a_t,y_t,c_t,z'_{t})\sim K_{M_t}(\cdot\mid z_t,o_t,g_t).
\]

This includes inference, proof/program search, retrieval, rule firing, planning and tool use.

## 5.2 Within-form development

\[
M_{t+1}=U(M_t,e_t).
\]

Examples include SGD/Adam, Bayesian conditioning, rule induction, chunking, library learning, memory consolidation and OCM admission/revision.

## 5.3 Morphogenesis

\[
M'\sim\Gamma(\cdot\mid M,E,R,H_{dev}).
\]

Examples include NAS, neuroevolution, program synthesis, model-structure learning, growth/pruning and architecture repair.

When experience changes `Gamma` itself, the process enters meta-morphogenesis / K3 / strong-RSI territory.

---

# 6. External admissibility and verified developmental burden

A universal scalar verifier threshold is not assumed.

For task `tau`, define an externally registered admissibility contract

\[
A_\tau(y,e;V,C)\in\{0,1\}
\]

or a declared partially ordered evidence/capability contract with an admissible region fixed before protected outcome access.

Define first-admissible stopping time

\[
T_A=\inf\{t:A_\tau(y_t,e_t;V,C)=1\}.
\]

For morphology `M`, situation `d`, protocol `D`:

\[
\mathbf B_M(\tau\mid d,D)
=E\left[\sum_{t=0}^{T_A}\rho(t)\mid M,d,D,\tau\right].
\]

Raw coordinates may include:

```text
information/labels/demonstrations
candidate generation/search
execution/inference
verification/checker calls
failed/rejected work
learning/update
memory/storage
communication
maintenance/revision
human intervention
CPU/GPU/wall/energy/IO
```

No scalar is canonical. Scalar cost requires a prospectively fixed price/utility mapping.

Failed/censored tasks are retained; conditional-on-success cost may never be reported without success probability.

---

# 7. Developmental feasible set, frontier and intelligence profile

For ecology `E`, morphology `M`, developmental situation `d` and protocol `D`, define semantic/theory reachable capability-resource set

\[
\mathcal A_M(E\mid d,D)
=\{(Q,\mathbf B): (Q,\mathbf B)\text{ reachable under }M,D,E\}.
\]

Its Pareto developmental frontier is

\[
\mathcal F_M(E\mid d,D)
=Pareto(\mathcal A_M(E\mid d,D)).
\]

The **intelligence profile** is

\[
\mathcal I_{M,d,D}:E\mapsto\mathcal F_M(E\mid d,D).
\]

It records what the deployed developmental system can reach and what it must spend.

## 7.1 Semantic vs certified frontier

For rich systems the complete semantic frontier may be uncomputable.

Distinguish:

```text
semantic frontier        theory-level reachable Pareto set
certified inner frontier externally verified/proved/observed points
outer/inner bounds        theorem/statistical bounds
```

Experiments establish certified points/bounds, not universal frontier enumeration.

## 7.2 Starting capital matters

The primary comparison object is `(M,d,D)`, not architecture `M` alone.

Architecture/family claims must match starting capital/protocols, charge acquisition, or explicitly say they compare deployed systems rather than innate architecture-only intelligence.

---

# 8. Generality

For ecology family `\mathfrak E`, define deployed-system dominance

\[
(M_1,d_1,D_1)\succeq_{\mathfrak E}(M_2,d_2,D_2)
\]

when the first frontier weakly dominates the second on every registered ecology.

This relation is a **preorder on deployed systems**, because distinct systems can have identical intelligence profiles.

Define profile equivalence by mutual dominance. Dominance induces a partial order on profile-equivalence classes under the registered frontier semantics.

## 8.1 Distributional scalarization

If ecology distribution `mu` and utility `u(Q,B)` are prospectively declared,

\[
G_{\mu,u}(M,d,D)
=E_{E\sim\mu}
\left[
\sup_{(Q,\mathbf B)\in\mathcal F_M(E\mid d,D)}u(Q,\mathbf B)
\right].
\]

Different `mu,u,d,D` can reverse rankings.

Universal-Intelligence/AIXI-style measures are strong parent orientations under their chosen environment/reward/complexity semantics; GMI does not replace them.

---

# 9. Developmental capital hierarchy

Let RESET be a matched counterfactual lacking the relevant inherited developmental state while retaining the same declared external tools/evaluator/protocol information.

## K0 — solution capital

A directly reusable answer/proof/program/object-specific solution is retained.

## K1 — cognition/search capital

Inherited state creates K1 on fresh targets when:

1. protected target solution is absent from relevant history;
2. before target success, inherited state changes proposal/search/action distribution or representation/control;
3. this causally lowers future verified burden against matched controls.

A measurable mediator is

\[
\Delta I(\tau)=\log_2\frac{rank_{RESET}(m^*)}{rank_H(m^*)}.
\]

#323 currently supports K1/C2 at its authored grammar scope.

## K2 — developmental capital

Inherited state creates K2 only if it lowers burden of acquiring **new K1**:

\[
E[B^{acq}_{H}(K1_{new})]
<
E[B^{acq}_{RESET}(K1_{new})].
\]

#323's retained-capital C3 test ended `NOT_ESTABLISHED` at the current grammar (registered bar met on 2/9 fresh seeds).

## K3 — improvement / morphogenesis capital

Inherited state changes `Gamma/U` such that discovering or constructing future verified frontier improvements becomes cheaper/more reliable on fresh ecology families under fixed external governance.

Capital labels require causal counterfactual evidence; they are not assigned by inspection.

---

# 10. Adopted parent theorem modules

Parent ownership is foundational.

## P-UAI — general agent/performance
Universal Artificial Intelligence / Universal Intelligence.

## P-STATE — minimal/predictive state
Automata minimization, predictive-state representations, computational mechanics, bisimulation/state abstraction.

## P-INFO — information/resource tradeoff
Information Bottleneck, rate-distortion, information-theoretic bounded rationality.

## P-FACT — factorization
Factored MDPs, DBNs, graphical models, structured programs/software.

## P-SEARCH — universal/incremental search
Levin/Solomonoff/Hutter, OOPS/PowerPlay, program synthesis/library learning.

## P-META — learning-to-learn
Baxter, PAC-Bayes lifelong/meta-learning, MAML, learned optimizers and related theory.

## P-MORPH — morphology generation
AutoML/NAS/neuroevolution, modularly varying goals, facilitated variation, connection-cost modularity/hierarchy, QD/open-ended search.

## P-META-COMP — computational allocation
Algorithm selection, rational metareasoning, stochastic-shortest-path/control, drift analysis.

The assumption map specifies when each result may be imported.

---

# 11. Core consequences

## GMI-T1 — no representation-independent implementation atom
Computation alone does not determine a unique unit boundary. Irreducible implementation units require extra locality/physics/resource/causal assumptions.

## GMI-T2 — task-relative minimal semantic developmental state is well posed at finite deterministic scope
Quotient complete developmental situations by equality of registered future semantic traces under allowed interventions; the minimal deterministic representation is unique up to isomorphism under the parent theorem.

## GMI-T3 — factorization can matter exponentially without changing expressivity
A global sufficient state may grow exponentially while a factored realization remains compact/local. Track B has an exact `3^n` construction.

## GMI-T4 — lifecycle morphology phase boundary
For fixed scalarized build/per-use costs:

\[
C_i=A_i+Hc_i(E),
\]

with exact crossover from equality of the two cost lines.

## GMI-T5 — ecology-aligned factorization can lower future developmental burden
Repeated reusable structure can favor matching factorizations after build/coordination costs. Strongly parent-owned.

## GMI-T6 — inherited history need not help
Without relatedness/transfer assumptions, inherited state can hurt via maintenance/interference/routing/acquisition costs.

## GMI-T7 — no universal exact burden predictor for unrestricted Turing-complete systems
Predictive theorems must restrict the class or become probabilistic/empirical.

## GMI-T8 — generality is conditional
No morphology is expected to dominate unrestricted ecologies/resources; use profiles/frontiers or declared scalar measures.

---

# 12. Known forms are specializations

### Neural / differentiable

```text
F layer/module graph
Theta weights + optimizer/recurrent state
K forward/model cognition
U gradient/plastic/meta update
Gamma NAS/evolution/growth/pruning
```

### Symbolic / production

```text
F predicates/rules/index/workspace
Theta facts/rules/preferences
K match/fire/unify/search
U induction/chunking/revision
Gamma vocabulary/operator restructuring
```

### Probabilistic / generative

```text
F factor graph/probabilistic program
Theta posterior/latent/model state
K inference/sampling/planning
U conditioning/parameter learning
Gamma model-structure learning
```

### Programmatic / library-learning

```text
F grammar/program/library graph
Theta library/search prior/partials
K enumeration/synthesis/execution
U abstraction/library/search-prior update
Gamma grammar/operator growth
```

### OCM-like governed explicit

```text
F warranted field/assets/provenance dependencies
Theta facts/methods/applicability/control/self-model
K retrieval/search/composition/tool/executive
U verified admission/revision/failure learning/consolidation
Gamma governed representation/operator/control change
```

No specialization is assumed fundamental.

---

# 13. What makes GMI general?

## G1 — realization breadth
Materially different forms fit the same definitions without architecture-specific semantic escape hatches.

## G2 — invariant definitions
Admissibility, semantic developmental state, resource burden, frontiers, K0-K3 and generality retain the same meanings.

## G3 — parent consistency
Established parent results appear as valid special cases/modules with their assumptions intact.

## G4 — predictive cross-paradigm content
At least one quantitative pre-outcome prediction transfers across materially different forms beyond the product of family-native parent predictors.

G1-G3 establish a coherent synthesis theory at scope. G4 is required for a new general scientific law.

---

# 14. Current evidence

Supported now:

```text
no unique representation-independent implementation atom established
task-relative finite developmental minimization is well posed
factorized realizations can be exponentially more compact/local than flat state tables
ecology/resource morphology phases exist in exact systems and parent literature
#323 provides C2/K1 pre-solution search-geometry evidence at one authored grammar
```

Negative/locked:

```text
#323 K2/C3 retained-capital acquisition NOT_ESTABLISHED at current grammar
no cross-paradigm predictive developmental law yet
no unique basis
no theory-predicted unknown morphology
no meta-morphogenesis / RSI improvement slope
```

---

# 15. Scientific programme

### A — mathematical coherence
Finish obligation/situation/semantic-equivalence semantics, parent assumption maps, finite proofs and approximate-state imports.

### B — realization maps
Complete family-scale mappings and bounded resource/compiler receipts for neural, symbolic, probabilistic, programmatic and OCM-like systems.

### C — developmental measurement
Measure K1/K2/K3 with matched causal controls and complete ledgers.

### D — cross-paradigm prediction
Predict held-out developmental burden/frontier from pre-outcome structure across at least two materially different forms against family-native predictors.

### E — real cognitive ecologies
Lean math -> execution-verified code/tools -> language-mediated mixed tasks -> science, with unchanged GMI definitions.

### F — morphology discovery / RSI
Only after known-family prediction works: predict a parent-frontier hole, search blindly, reduce against parents, then test whether `Gamma` itself develops.

---

# 16. Current theory status

```text
GMI_V1_COHERENT_SYNTHESIS_UNDER_ACTIVE_HOSTILE_REVIEW
PARENT_THEOREMS_ARE_FOUNDATIONAL_MODULES
SEMANTIC_DEVELOPMENTAL_STATE_SEPARATED_FROM_RESOURCE_REALIZATION
REPRESENTATION_INDEPENDENT_IMPLEMENTATION_ATOM_NOT_REQUIRED
MORPHOLOGY_IS_RESOURCE_BOUNDED_REALIZATION / FACTORIZATION
INTELLIGENCE_IS_VERIFIED_DEVELOPMENTAL_FRONTIER / PROFILE
GENERALITY_IS_ECOLOGY_AND_PROTOCOL_RELATIVE_PREORDER
K0_K1_K2_K3_DEVELOPMENTAL_CAPITAL_DEFINED
NEW_CROSS_PARADIGM_PREDICTIVE_LAW_NOT_YET_ESTABLISHED
```

GMI-v1 is intended to remain useful even if most individual mathematics comes from parent fields. The theory becomes scientifically stronger as it survives reductions, hostiles and real math/code/language/science validation.